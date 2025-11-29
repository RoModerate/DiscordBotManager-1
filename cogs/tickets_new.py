import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Select, Button, Modal, TextInput
from datetime import datetime, timedelta
from database import Database
import io
import asyncio
import aiohttp
from ticket_ai_config import TicketAIConfig
from cogs.tickets_ai_enhanced import TicketAIManager

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Support Ticket",
                description="Get help with general issues",
                value="support"
            ),
            discord.SelectOption(
                label="Request CC",
                description="Content Creator application",
                value="cc"
            ),
            discord.SelectOption(
                label="Report a Member",
                description="Report a player for rule violations",
                value="report"
            ),
            discord.SelectOption(
                label="Warning Appeal",
                description="Appeal a warning or punishment",
                value="appeal"
            )
        ]
        super().__init__(
            placeholder="Select a ticket type...",
            options=options,
            custom_id="ticket_select_menu"
        )
    
    async def callback(self, interaction: discord.Interaction):
        db = Database()
        ticket_categories = db.get_config('ticket_categories') or {}
        
        ticket_type = self.values[0]
        category_map = {
            'support': ('Support Ticket', ticket_categories.get('support', 1436498409153626213)),
            'cc': ('Request CC!', ticket_categories.get('cc', 1436498445216256031)),
            'report': ('Report a Member!', ticket_categories.get('report', 1436498495153635512)),
            'appeal': ('Warning Appeal', ticket_categories.get('appeal', 1436498528544227428))
        }
        
        ticket_label, category_id = category_map[ticket_type]
        
        existing_key = f"{interaction.guild.id}:{interaction.user.id}:{ticket_type}"
        if db.data.get('open_tickets', {}).get(existing_key):
            await interaction.response.send_message(
                f"You already have an open {ticket_label} ticket.",
                ephemeral=True
            )
            return
        
        modal = TicketReasonModal(ticket_type, ticket_label, category_id, interaction.user.id)
        await interaction.response.send_modal(modal)

class TicketPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketReasonModal(Modal):
    def __init__(self, ticket_type: str, ticket_label: str, category_id: int, user_id: int):
        super().__init__(title=f"Reason for {ticket_label}")
        self.ticket_type = ticket_type
        self.ticket_label = ticket_label
        self.category_id = category_id
        self.user_id = user_id

        self.reason_input = TextInput(
            label="Describe your issue in detail",
            style=discord.TextStyle.paragraph,
            placeholder="Please provide details about your ticket...",
            required=True,
            max_length=1000
        )
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db = Database()

        existing_key = f"{interaction.guild.id}:{self.user_id}:{self.ticket_type}"
        
        if db.data.get('open_tickets', {}).get(existing_key):
            await interaction.followup.send(
                f"You already have an open {self.ticket_label} ticket.",
                ephemeral=True
            )
            return

        # Use emoji naming format from AI config
        ticket_config = TicketAIConfig.TICKET_TYPES.get(self.ticket_type)
        if ticket_config:
            username = interaction.user.name.lower().replace(" ", "-").replace("_", "-")
            channel_name = ticket_config['name_format'].format(username=username)[:100]
        else:
            channel_name = f"ticket-{interaction.user.name}".lower().replace(" ", "-").replace("_", "-")[:100]

        staff_role_id = db.get_config('staff_ping_role')
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        if staff_role_id:
            staff_role = interaction.guild.get_role(staff_role_id)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        try:
            category = interaction.guild.get_channel(self.category_id)
            if not category or not isinstance(category, discord.CategoryChannel):
                await interaction.followup.send(
                    "Ticket category not configured properly. Please contact an administrator.",
                    ephemeral=True
                )
                return

            ticket_channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                topic=f"Ticket by {interaction.user.name} | Status: UNCLAIMED"
            )

            # Save ticket data BEFORE sending embed
            ticket_data = {
                'ticket_id': ticket_channel.id,
                'type': self.ticket_type,
                'label': self.ticket_label,
                'creator': interaction.user.id,
                'created_at': datetime.utcnow().isoformat(),
                'claimed_by': None,
                'claimed_at': None,
                'status': 'unclaimed',
                'reason': self.reason_input.value,
                'embed_message_id': None,
                'ai_active': db.get_ai_ops_status(),
                'messages': []
            }
            db.save_ticket_data(ticket_channel.id, ticket_data)

            if 'open_tickets' not in db.data:
                db.data['open_tickets'] = {}
            db.data['open_tickets'][existing_key] = ticket_channel.id
            db.save()

            embed = discord.Embed(
                title=f"{self.ticket_label}",
                description=f"**Opened by:** {interaction.user.mention}\n**Status:** Unclaimed\n\n**Reason:**\n```\n{self.reason_input.value}\n```",
                color=0x5865F2,
                timestamp=datetime.utcnow()
            )
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text=f"Ticket ID: {ticket_channel.id}")

            view = TicketControlView()
            
            bot_id = 1436208461112148060
            ping_message = f"{interaction.user.mention} <@{bot_id}>"
            await ticket_channel.send(ping_message, delete_after=1)
            
            ticket_message = await ticket_channel.send(embed=embed, view=view)

            # Update ticket data with message ID
            ticket_data['embed_message_id'] = ticket_message.id
            db.save_ticket_data(ticket_channel.id, ticket_data)

            await interaction.followup.send(
                f"Your ticket has been created: {ticket_channel.mention}",
                ephemeral=True
            )
            
            # Trigger AI auto-claim and greeting ONLY for allowed categories
            allowed_categories = [1436498409153626213, 1436498445216256031, 1436498528544227428]
            cog = interaction.client.get_cog('Tickets')
            if cog and db.get_ai_ops_status() and self.category_id in allowed_categories:
                await cog.ai_autoclaim_and_greet(ticket_channel, ticket_data)

        except Exception as e:
            print(f"Error creating ticket: {e}")
            await interaction.followup.send(
                "Failed to create ticket. Please contact an administrator.",
                ephemeral=True
            )
    
    async def get_roblox_info(self, discord_id):
        try:
            db = Database()
            verification_data = db.get_verification_data(discord_id)
            if verification_data and 'roblox_id' in verification_data:
                roblox_id = verification_data['roblox_id']
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://users.roblox.com/v1/users/{roblox_id}") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            username = data.get('name', 'Unknown')
                            
                            async with session.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={roblox_id}&size=150x150&format=Png") as avatar_resp:
                                if avatar_resp.status == 200:
                                    avatar_data = await avatar_resp.json()
                                    avatar_url = avatar_data['data'][0]['imageUrl'] if avatar_data.get('data') else None
                                    return {
                                        'username': username,
                                        'roblox_id': roblox_id,
                                        'avatar_url': avatar_url
                                    }
        except:
            pass
        return None

class TicketControlView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ClaimButton())
        self.add_item(CloseButton())

class ClaimButton(Button):
    def __init__(self):
        super().__init__(
            label="Claim",
            style=discord.ButtonStyle.gray,
            custom_id="claim_ticket_button"
        )
    
    async def callback(self, interaction: discord.Interaction):
        db = Database()
        ticket_data = db.get_ticket_data(interaction.channel.id)
        
        if not ticket_data:
            ticket_data = {
                'ticket_id': interaction.channel.id,
                'type': 'unknown',
                'label': 'Ticket',
                'creator': None,
                'created_at': datetime.utcnow().isoformat(),
                'claimed_by': None,
                'claimed_at': None,
                'status': 'unclaimed',
                'reason': 'N/A',
                'embed_message_id': None,
                'ai_active': False,
                'messages': []
            }
            
            for member in interaction.channel.members:
                if not member.bot and member != interaction.guild.me:
                    ticket_data['creator'] = member.id
                    break
            
            db.save_ticket_data(interaction.channel.id, ticket_data)
        
        if ticket_data['claimed_by']:
            claimer = interaction.guild.get_member(ticket_data['claimed_by'])
            claimer_name = claimer.mention if claimer else f"<@{ticket_data['claimed_by']}>"
            await interaction.response.send_message(
                f"This ticket is already claimed by {claimer_name}",
                ephemeral=True
            )
            return
        
        ticket_data['claimed_by'] = interaction.user.id
        ticket_data['claimed_at'] = datetime.utcnow().isoformat()
        ticket_data['status'] = 'claimed'
        db.save_ticket_data(interaction.channel.id, ticket_data)
        
        await interaction.channel.edit(
            topic=f"Ticket claimed by {interaction.user.name}"
        )
        
        await interaction.response.send_message(
            f"This ticket has been claimed by {interaction.user.mention}",
            view=TicketClaimedView()
        )

class CloseButton(Button):
    def __init__(self):
        super().__init__(
            label="Close",
            style=discord.ButtonStyle.red,
            custom_id="close_ticket_button"
        )
    
    async def callback(self, interaction: discord.Interaction):
        modal = CloseReasonModal()
        await interaction.response.send_modal(modal)

class TicketClaimedView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(UnclaimButton())
        self.add_item(CloseButton())

class UnclaimButton(Button):
    def __init__(self):
        super().__init__(
            label="Unclaim",
            style=discord.ButtonStyle.gray,
            custom_id="unclaim_ticket_button"
        )
    
    async def callback(self, interaction: discord.Interaction):
        db = Database()
        ticket_data = db.get_ticket_data(interaction.channel.id)
        
        if not ticket_data:
            ticket_data = {
                'ticket_id': interaction.channel.id,
                'type': 'unknown',
                'label': 'Ticket',
                'creator': None,
                'created_at': datetime.utcnow().isoformat(),
                'claimed_by': None,
                'claimed_at': None,
                'status': 'unclaimed',
                'reason': 'N/A',
                'embed_message_id': None,
                'ai_active': False,
                'messages': []
            }
            
            for member in interaction.channel.members:
                if not member.bot and member != interaction.guild.me:
                    ticket_data['creator'] = member.id
                    break
        
        ticket_data['claimed_by'] = None
        ticket_data['claimed_at'] = None
        ticket_data['status'] = 'unclaimed'
        db.save_ticket_data(interaction.channel.id, ticket_data)
        
        await interaction.channel.edit(
            topic=f"Ticket - Status: UNCLAIMED"
        )
        
        await interaction.response.send_message(
            f"{interaction.user.mention} unclaimed this ticket.",
            view=TicketControlView()
        )

class CloseReasonModal(Modal):
    def __init__(self):
        super().__init__(title="Close Ticket")
        
        self.reason_input = TextInput(
            label="Reason for closing",
            style=discord.TextStyle.paragraph,
            placeholder="Why are you closing this ticket?",
            required=True,
            max_length=500
        )
        self.add_item(self.reason_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        db = Database()
        ticket_data = db.get_ticket_data(interaction.channel.id)
        
        if not ticket_data:
            ticket_data = {
                'ticket_id': interaction.channel.id,
                'type': 'unknown',
                'label': 'Ticket',
                'creator': None,
                'created_at': datetime.utcnow().isoformat(),
                'claimed_by': None,
                'claimed_at': None,
                'status': 'unclaimed',
                'reason': 'N/A',
                'embed_message_id': None,
                'ai_active': False,
                'messages': []
            }
            
            for member in interaction.channel.members:
                if not member.bot and member != interaction.guild.me:
                    ticket_data['creator'] = member.id
                    break
            
            db.save_ticket_data(interaction.channel.id, ticket_data)
        
        creator_id = ticket_data.get('creator')
        creator = interaction.guild.get_member(creator_id)
        
        await interaction.followup.send(f"Ticket closed by {interaction.user.mention}\nReason: {self.reason_input.value}")
        
        await asyncio.sleep(2)
        
        transcript = await self.generate_transcript(interaction.channel, ticket_data, self.reason_input.value, interaction.user)
        
        transcript_channel_id = db.get_config('transcript_channel')
        if transcript_channel_id:
            transcript_channel = interaction.guild.get_channel(transcript_channel_id)
            if transcript_channel:
                transcript_embed = discord.Embed(
                    title=f"Ticket Transcript - {interaction.channel.name}",
                    description=f"> **Type:** {ticket_data.get('label', 'Unknown')}\n> **Creator:** <@{creator_id}>\n> **Closed by:** {interaction.user.mention}",
                    color=0x2F3136,
                    timestamp=datetime.utcnow()
                )
                transcript_embed.add_field(name="Close Reason", value=self.reason_input.value, inline=False)
                transcript_embed.set_footer(text=f"Ticket ID: {interaction.channel.id}")
                
                transcript_file = discord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{interaction.channel.id}.txt"
                )
                
                await transcript_channel.send(embed=transcript_embed, file=transcript_file)
        
        existing_key = f"{interaction.guild.id}:{creator_id}:{ticket_data.get('type')}"
        if existing_key in db.data.get('open_tickets', {}):
            del db.data['open_tickets'][existing_key]
            db.save()
        
        await interaction.channel.delete(reason=f"Ticket closed by {interaction.user.name}")
    
    async def generate_transcript(self, channel, ticket_data, close_reason, closer):
        transcript_lines = []
        transcript_lines.append(f"Ticket Transcript - {channel.name}")
        transcript_lines.append(f"Ticket ID: {channel.id}")
        transcript_lines.append(f"Type: {ticket_data.get('label', 'Unknown')}")
        transcript_lines.append(f"Creator: {ticket_data.get('creator')}")
        transcript_lines.append(f"Created: {ticket_data.get('created_at', 'Unknown')}")
        transcript_lines.append(f"Closed by: {closer.name} ({closer.id})")
        transcript_lines.append(f"Close Reason: {close_reason}")
        transcript_lines.append("=" * 80)
        transcript_lines.append("")
        
        try:
            async for message in channel.history(limit=500, oldest_first=True):
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                transcript_lines.append(f"[{timestamp}] {message.author.name}: {message.content}")
                
                if message.embeds:
                    for embed in message.embeds:
                        transcript_lines.append(f"  [Embed: {embed.title or 'No title'}]")
                
                if message.attachments:
                    for attachment in message.attachments:
                        transcript_lines.append(f"  [Attachment: {attachment.filename} - {attachment.url}]")
        except:
            transcript_lines.append("[Error fetching message history]")
        
        return "\n".join(transcript_lines)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.ai_manager = TicketAIManager(self.db)
        self.check_inactive_tickets.start()
    
    async def cog_unload(self):
        self.check_inactive_tickets.cancel()
    
    @tasks.loop(hours=1)
    async def check_inactive_tickets(self):
        """Check for inactive tickets and auto-close them after 24h"""
        try:
            now = datetime.utcnow()
            
            if 'tickets' not in self.db.data or not isinstance(self.db.data['tickets'], dict):
                return
            
            # Iterate over the tickets dictionary (key=channel_id, value=ticket_data)
            for channel_id_str, ticket_data in list(self.db.data['tickets'].items()):
                if ticket_data.get('status') == 'closed':
                    continue
                
                try:
                    channel_id = int(channel_id_str)
                except ValueError:
                    continue
                
                messages = ticket_data.get('messages', [])
                
                last_message_time = None
                if messages:
                    try:
                        last_msg = messages[-1]
                        last_message_time = datetime.fromisoformat(last_msg.get('timestamp', ''))
                    except:
                        pass
                
                if not last_message_time:
                    created_at = ticket_data.get('created_at')
                    if created_at:
                        try:
                            last_message_time = datetime.fromisoformat(created_at)
                        except:
                            continue
                    else:
                        continue
                
                time_since_last_message = now - last_message_time
                
                if time_since_last_message >= timedelta(hours=24):
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        try:
                            await channel.send(
                                "⚠️ This ticket has been inactive for 24 hours and will now be automatically closed.\n"
                                "If you need further assistance, please open a new ticket."
                            )
                            
                            await asyncio.sleep(5)
                            
                            # Update ticket status in the database
                            ticket_data['status'] = 'closed'
                            ticket_data['closed_at'] = now.isoformat()
                            ticket_data['closed_by'] = self.bot.user.id
                            ticket_data['close_reason'] = 'Auto-closed due to inactivity (24h no reply)'
                            self.db.save_ticket_data(channel_id, ticket_data)
                            
                            # Remove from open_tickets
                            open_ticket_key = f"{channel.guild.id}:{ticket_data.get('creator')}:{ticket_data.get('type')}"
                            if open_ticket_key in self.db.data.get('open_tickets', {}):
                                del self.db.data['open_tickets'][open_ticket_key]
                                self.db.save()
                            
                            # Save transcript before deleting channel
                            closer_user = self.bot.user
                            transcript = await self.generate_transcript(channel, ticket_data, 'Auto-closed due to inactivity', closer_user)
                            
                            # Send transcript to logs channel
                            logs_channel_id = self.db.get_config('ticket_logs_channel') or TicketAIConfig.CHANNELS.get('ticket_logs')
                            if logs_channel_id:
                                logs_channel = self.bot.get_channel(logs_channel_id)
                                if logs_channel:
                                    transcript_file = discord.File(
                                        fp=io.BytesIO(transcript.encode('utf-8')),
                                        filename=f"ticket-{channel_id}-transcript.txt"
                                    )
                                    await logs_channel.send(
                                        f"Ticket auto-closed: {channel.name} (Inactive for 24h)",
                                        file=transcript_file
                                    )
                            
                            await channel.delete(reason="Auto-closed due to inactivity")
                            
                        except Exception as e:
                            print(f"Error auto-closing ticket {channel_id}: {e}")
        except Exception as e:
            print(f"Error in check_inactive_tickets task: {e}")
            import traceback
            traceback.print_exc()
    
    @check_inactive_tickets.before_loop
    async def before_check_inactive_tickets(self):
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Thin adapter - delegates to AI manager with role-ping enforcement"""
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        # Check if message is in a ticket channel
        ticket_data = self.db.get_ticket_data(message.channel.id)
        if not ticket_data:
            return
        
        # CRITICAL: AI must ONLY respond in these 3 specific categories
        # Support: 1436498409153626213, Request CC: 1436498445216256031, Warning Appeal: 1436498528544227428
        allowed_categories = [1436498409153626213, 1436498445216256031, 1436498528544227428]
        if message.channel.category_id not in allowed_categories:
            # AI must ignore messages in any other category (including Report Player)
            return
        
        # Check global AI ops status
        if not self.db.get_ai_ops_status():
            return
        
        # Check if ticket has AI enabled
        if not ticket_data.get('ai_active', True):
            return
        
        # CRITICAL: Check for unauthorized role pings
        # Messages with @everyone, @here, or role pings are IGNORED unless from Ticket Manager or Appeal Manager
        user_role_ids = [role.id for role in message.author.roles]
        ticket_manager_id = TicketAIConfig.ROLES['ticket_manager']
        appeal_manager_id = TicketAIConfig.ROLES['appeal_manager']
        
        has_authorized_role = ticket_manager_id in user_role_ids or appeal_manager_id in user_role_ids
        
        # Check if message contains pings
        has_everyone_ping = message.mention_everyone
        has_role_ping = len(message.role_mentions) > 0
        
        # If message has pings but user is not authorized, ignore it
        if (has_everyone_ping or has_role_ping) and not has_authorized_role:
            # AI must not respond to unauthorized pings
            return
        
        # Delegate to comprehensive AI processor
        try:
            should_save, response = await self.ai_manager.process_ticket_message(
                message, ticket_data, message.channel
            )
            
            if response:
                # Check if AI wants to close the ticket
                if response == 'CLOSE_TICKET_NOW':
                    # Send "Alright!" message first
                    await message.channel.send("Alright!")
                    await asyncio.sleep(2)
                    # Close the ticket
                    await self.ai_manager.close_ticket(self.bot, message.channel, ticket_data, self.bot.user, "User requested closure via AI")
                else:
                    # Ping user and bot ID when responding to ticket messages
                    creator_id = ticket_data.get('creator')
                    bot_id = 1436208461112148060
                    ping_message = f"<@{creator_id}> <@{bot_id}> {response}"
                    await message.channel.send(ping_message)
        except Exception as e:
            print(f"Error processing ticket message: {e}")
            import traceback
            traceback.print_exc()
    
    async def ai_autoclaim_and_greet(self, channel, ticket_data):
        """Auto-claim ticket and send initial AI greeting"""
        try:
            # Auto-claim the ticket
            await self.ai_manager.claim_ticket(self.bot, channel, ticket_data)
            
            # Send initial AI greeting
            await self.ai_manager.send_initial_greeting(channel, ticket_data)
        except Exception as e:
            print(f"Error in AI auto-claim and greet: {e}")
            import traceback
            traceback.print_exc()
    
    async def send_initial_ai_greeting(self, channel, ticket_data):
        """Send initial AI greeting when ticket is created"""
        import os
        import aiohttp
        
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            return
        
        ai_model = self.db.get_config('ai_model') or 'meta-llama/Llama-3.2-3B-Instruct:fastest'
        ticket_reason = ticket_data.get('reason', 'No reason provided')
        ticket_type = ticket_data.get('type', 'support')
        
        # Generate context-specific greeting based on ticket type
        type_context = {
            'support': 'I\'m here to help you with your support request.',
            'cc': 'I\'m here to help you with your content creator application.',
            'appeal': 'I\'m here to help you with your warning appeal.'
        }
        
        greeting_context = type_context.get(ticket_type, 'I\'m here to help you.')
        
        system_prompt = f"""You are a helpful AI support assistant for Spiritual Battlegrounds.
{greeting_context}

The user's reason for opening this ticket: {ticket_reason}

Your task:
1. Acknowledge their specific reason
2. Show you understand what they need
3. Ask how you can help them resolve this
4. Be friendly, professional, and direct
5. Keep response short (2-3 sentences max)

Respond naturally in plain text only."""
        
        try:
            api_endpoint = "https://router.huggingface.co/v1/chat/completions"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_endpoint,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": ai_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"I need: {ticket_reason}"}
                        ],
                        "max_tokens": 300,
                        "temperature": 0.6
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        ai_response = data['choices'][0]['message']['content']
                        
                        if 'messages' not in ticket_data:
                            ticket_data['messages'] = []
                        
                        ticket_data['messages'].append({
                            'role': 'assistant',
                            'content': ai_response,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        self.db.save_ticket_data(channel.id, ticket_data)
                        
                        # Ping both user and bot ID in ticket response
                        creator_id = ticket_data.get('creator')
                        bot_id = 1436208461112148060
                        ping_message = f"<@{creator_id}> <@{bot_id}> {ai_response}"
                        await channel.send(ping_message)
        except Exception as e:
            print(f"Initial AI greeting error: {e}")
    
    async def send_ai_response(self, channel, ticket_data):
        import os
        import aiohttp
        
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            return
        
        ai_model = self.db.get_config('ai_model') or 'meta-llama/Llama-3.2-3B-Instruct:fastest'
        
        ticket_type = ticket_data.get('type', 'support')
        ticket_label = ticket_data.get('label', 'Support Ticket')
        ticket_reason = ticket_data.get('reason', 'No reason provided')
        
        if ticket_type == 'support':
            system_prompt = f"""You are a helpful support assistant for Spiritual Battlegrounds Discord server.

Ticket Type: Support Ticket
Initial Reason: {ticket_reason}

Your role:
- Greet the user warmly
- Ask what specific issue they're facing
- Help them resolve their problem step by step
- Be professional, friendly, and clear
- When the issue is resolved, suggest closing the ticket

Important: Respond naturally in plain text, NOT in embeds. Keep responses short and helpful."""
        
        elif ticket_type == 'cc':
            system_prompt = f"""You are a helpful support assistant for Spiritual Battlegrounds Discord server.

Ticket Type: Request CC (Content Creator)
Initial Reason: {ticket_reason}

Your role:
- Greet the user
- Ask for their custom command idea
- Ask about the format they want for the command
- Ask about the purpose and use case
- Gather all necessary details professionally
- Be friendly and encouraging

Important: Respond naturally in plain text, NOT in embeds. Keep responses short and helpful."""
        
        elif ticket_type == 'report':
            system_prompt = f"""You are a helpful support assistant for Spiritual Battlegrounds Discord server.

Ticket Type: Report a Member
Initial Reason: {ticket_reason}

Your role:
- Greet the user
- Ask for evidence (screenshots, videos, etc.)
- Ask for the player's username
- Ask for a detailed description of what happened
- Be professional and thorough in collecting information
- Ensure all details are gathered before staff review

Important: Respond naturally in plain text, NOT in embeds. Keep responses short and helpful."""
        
        elif ticket_type == 'appeal':
            system_prompt = f"""You are a helpful support assistant for Spiritual Battlegrounds Discord server.

Ticket Type: Warning Appeal
Initial Reason: {ticket_reason}

Your role:
- Greet the user
- Ask which warning they're appealing
- Ask why they believe it should be removed
- Ask for any proof or evidence supporting their appeal
- Be understanding but maintain professionalism
- Gather all information for staff review

Important: Respond naturally in plain text, NOT in embeds. Keep responses short and helpful."""
        
        else:
            system_prompt = f"""You are a helpful support assistant for Spiritual Battlegrounds Discord server.

Ticket Type: {ticket_label}
Initial Reason: {ticket_reason}

Your role:
- Help users with their ticket issues
- Be professional and friendly
- Provide clear, concise answers
- Gather necessary information

Important: Respond naturally in plain text, NOT in embeds. Keep responses short and helpful."""
        
        # Build message history for OpenAI-compatible format
        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in ticket_data.get('messages', [])[-10:]:
            messages.append({
                "role": msg.get('role', 'user'),
                "content": msg.get('content', '')
            })
        
        try:
            api_endpoint = "https://router.huggingface.co/v1/chat/completions"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_endpoint,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": ai_model,
                        "messages": messages,
                        "max_tokens": 500,
                        "temperature": 0.7
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        ai_response = data['choices'][0]['message']['content']
                        
                        ticket_data['messages'].append({
                            'role': 'assistant',
                            'content': ai_response,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        self.db.save_ticket_data(channel.id, ticket_data)
                        
                        # Ping both user and bot ID in ticket response
                        creator_id = ticket_data.get('creator')
                        bot_id = 1436208461112148060
                        ping_message = f"<@{creator_id}> <@{bot_id}> {ai_response}"
                        await channel.send(ping_message)
        except Exception as e:
            print(f"AI response error: {e}")

    @commands.hybrid_command(name='summarize', description='Get a summary of the current ticket')
    async def summarize(self, ctx):
        """Get a summary of the current ticket (Ticket Manager and Appeal Manager only)"""
        from ticket_ai_config import TicketAIConfig
        
        ticket_manager_id = TicketAIConfig.ROLES['ticket_manager']
        appeal_manager_id = TicketAIConfig.ROLES['appeal_manager']
        
        user_role_ids = [role.id for role in ctx.author.roles]
        
        if ticket_manager_id not in user_role_ids and appeal_manager_id not in user_role_ids:
            await ctx.send("❌ You must be a Ticket Manager or Appeal Manager to use this command.", ephemeral=True)
            return
        
        ticket_data = self.db.get_ticket_data(ctx.channel.id)
        if not ticket_data:
            await ctx.send("❌ This command can only be used in ticket channels.", ephemeral=True)
            return
        
        ticket_type = ticket_data.get('type', 'Unknown')
        ticket_label = ticket_data.get('label', 'Ticket')
        creator_id = ticket_data.get('creator')
        creator_mention = f"<@{creator_id}>" if creator_id else "Unknown"
        reason = ticket_data.get('reason', 'No reason provided')
        created_at = ticket_data.get('created_at', 'Unknown')
        claimed_by = ticket_data.get('claimed_by')
        claimed_mention = f"<@{claimed_by}>" if claimed_by else "Unclaimed"
        status = ticket_data.get('status', 'Open')
        messages = ticket_data.get('messages', [])
        
        from datetime import datetime
        try:
            created_date = datetime.fromisoformat(created_at).strftime('%Y-%m-%d %H:%M UTC')
        except:
            created_date = created_at
        
        embed = discord.Embed(
            title=f"📋 Ticket Summary - {ticket_label}",
            color=0x5865F2,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Ticket Type", value=ticket_type.capitalize(), inline=True)
        embed.add_field(name="Status", value=status.capitalize(), inline=True)
        embed.add_field(name="Created", value=created_date, inline=True)
        embed.add_field(name="Creator", value=creator_mention, inline=True)
        embed.add_field(name="Claimed By", value=claimed_mention, inline=True)
        embed.add_field(name="Message Count", value=str(len(messages)), inline=True)
        embed.add_field(name="Initial Reason", value=reason[:1024] if len(reason) > 1024 else reason, inline=False)
        
        conversation_summary = ""
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        ai_messages = [msg for msg in messages if msg.get('role') == 'assistant']
        
        if messages:
            conversation_summary = f"**User messages:** {len(user_messages)}\n**AI responses:** {len(ai_messages)}\n\n"
            
            recent_messages = messages[-5:]
            conversation_summary += "**Recent conversation:**\n"
            for msg in recent_messages:
                role = "User" if msg.get('role') == 'user' else "AI"
                content = msg.get('content', '')
                if len(content) > 150:
                    content = content[:150] + "..."
                conversation_summary += f"• **{role}:** {content}\n"
        else:
            conversation_summary = "No messages yet."
        
        if len(conversation_summary) > 1024:
            conversation_summary = conversation_summary[:1020] + "..."
        
        embed.add_field(name="Conversation Overview", value=conversation_summary, inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='ticketpanel', description='Setup the ticket panel')
    @commands.has_permissions(administrator=True)
    async def ticketpanel(self, ctx):
        """Set up the ticket panel with select menu"""
        embed = discord.Embed(color=0x5865F2)

        embed.description = (
            "```Notice```\n"
            "> • If this is your first time using our ticket system, please read the ticket guide below.\n"
            "> • These guides will help you understand the process, and following them will significantly speed up the handling of your ticket.\n\n"
            "```Allowed Tickets```\n"
            "> • User Reports\n"
            "> • Staff Reports\n"
            "> • Bug Reports\n"
            "> • Warning Appeals\n"
            "> • Content Creator Requests\n"
            "> • Other Server-Related Inquiry\n\n"
            "```Disallowed Tickets```\n"
            "> • General Game Questions\n"
            "> • Suggestions\n"
            "> • Role Requests (Staff, Tester, Helper, etc.)"
        )

        view = TicketPanelView()
        await ctx.send(embed=embed, view=view)
        try:
            await ctx.message.delete()
        except:
            pass

async def setup(bot):
    await bot.add_cog(Tickets(bot))
