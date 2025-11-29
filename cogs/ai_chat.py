
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os
from database import Database

class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        
        if not self.db.get_config('ai_model'):
            self.db.set_config('ai_model', 'meta-llama/Llama-3.2-3B-Instruct:fastest')

    async def get_server_context(self, guild) -> str:
        """Build server context with accurate data from server indexing"""
        if not guild:
            return ""
        
        # Get server index cog for accurate live data
        server_index = self.bot.get_cog('ServerIndex')
        
        if server_index:
            channels = server_index.get_live_channel_count()
            members = server_index.get_live_member_count()
            roles = server_index.get_live_role_count()
            
            context = f"\n\nACCURATE Server Information:\n"
            context += f"- Server Name: {guild.name}\n"
            if members:
                context += f"- Total Members: {members['total']}\n"
                context += f"- Human Members: {members['humans']}\n"
                context += f"- Bot Members: {members['bots']}\n"
            if channels:
                context += f"- Total Channels: {channels['total']}\n"
                context += f"- Text Channels: {channels['text']}\n"
                context += f"- Voice Channels: {channels['voice']}\n"
            if roles:
                context += f"- Total Roles: {roles}\n"
        else:
            # Fallback to basic guild data
            context = f"\n\nServer Information:\n"
            context += f"- Server Name: {guild.name}\n"
            context += f"- Total Members: {guild.member_count}\n"
            context += f"- Total Channels: {len(guild.channels)}\n"
            context += f"- Text Channels: {len(guild.text_channels)}\n"
            context += f"- Voice Channels: {len(guild.voice_channels)}\n"
            context += f"- Total Roles: {len(guild.roles)}\n"
        
        return context
    
    def sanitize_mentions(self, text: str) -> str:
        """Remove @everyone and @here mentions from text to prevent abuse"""
        # Replace @everyone and @here with safe alternatives
        text = text.replace('@everyone', '@ everyone')
        text = text.replace('@here', '@ here')
        # Also handle variations
        text = text.replace('@Everyone', '@ Everyone')
        text = text.replace('@EVERYONE', '@ EVERYONE')
        text = text.replace('@Here', '@ Here')
        text = text.replace('@HERE', '@ HERE')
        return text
    
    async def get_ai_response(self, prompt: str, user_name: str = "User", guild=None, channel_id: int = None) -> str:
        """Get AI response from Hugging Face API with server-wide memory context"""
        if not self.api_key:
            return "❌ Hugging Face API key not configured. Please add HUGGINGFACE_API_KEY to your secrets."

        model = self.db.get_config('ai_model') or 'meta-llama/Llama-3.2-3B-Instruct:fastest'

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Get all taught responses for context
        all_teaches = self.db.get_all_teaches()
        knowledge_base = ""
        if all_teaches:
            knowledge_base = "\n\nKnowledge Base:\n"
            for teach_id, teach_info in list(all_teaches.items())[:10]:  # Limit to 10 most recent
                knowledge_base += f"- When users ask about '{teach_info['trigger']}': {teach_info['response']}\n"
        
        # Get accurate server context
        server_context = await self.get_server_context(guild) if guild else ""
        
        # Get recent server memory for context
        memory_context = ""
        if guild:
            recent_messages = self.db.get_ai_memory(limit=50, channel_id=channel_id)
            if recent_messages:
                memory_context = "\n\nRecent Server Context (past conversations):\n"
                for msg in recent_messages[-20:]:  # Last 20 messages
                    memory_context += f"- {msg['username']}: {msg['content'][:100]}\n"
        
        system_prompt = f"""You are a professional Discord bot assistant for Spiritual Battlegrounds server.

CRITICAL RULES:
- NEVER repeat the user's question in your response
- NEVER start responses with variations of the question
- Get straight to the answer - be direct and concise
- ONLY respond when directly asked a question or mentioned
- Provide accurate, professional responses based on the knowledge base and recent conversations
- Use the server information, knowledge base, and conversation history to answer questions accurately
- NO embeds, NO unnecessary chatter
- NEVER include @everyone or @here in your responses{knowledge_base}{server_context}{memory_context}

EXAMPLE:
Wrong: "What is Spiritual Battlegrounds? Spiritual Battlegrounds is..."
Correct: "Spiritual Battlegrounds is a Roblox Battlegrounds game based on the anime 'Dan Da Dan'..."

When asked about server statistics, use the exact numbers provided above."""

        # Use OpenAI-compatible format for Hugging Face router
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        ai_response = data['choices'][0]['message']['content']
                        # Sanitize the response to prevent @everyone/@here pings
                        return self.sanitize_mentions(ai_response)
                    else:
                        error_text = await response.text()
                        print(f"Hugging Face API error: {response.status} - {error_text}")
                        return f"❌ API Error: {response.status}"
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return f"❌ Error: {str(e)}"

    @commands.hybrid_command(name='ask', description='Ask the AI a question')
    async def ask(self, ctx, *, question: str):
        """Ask the AI a question"""
        ai_enabled = self.db.get_config('ai_enabled')
        if not ai_enabled:
            await ctx.send("❌ AI chat is currently disabled. Use `/aisetup` to enable it.", ephemeral=True)
            return

        await ctx.defer()

        response = await self.get_ai_response(question, ctx.author.name, ctx.guild)
        
        embed = discord.Embed(
            title="🤖 AI Response",
            description=response,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Asked by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # LOG ALL MESSAGES TO AI MEMORY (server-wide learning)
        if message.guild and message.content:
            self.db.add_ai_memory_message(
                user_id=message.author.id,
                username=message.author.name,
                channel_id=message.channel.id,
                content=message.content,
                guild_id=message.guild.id
            )

        ai_enabled = self.db.get_config('ai_enabled')
        if not ai_enabled:
            return
        
        # Blacklist channels where AI should not respond
        AI_BLACKLIST_CHANNELS = [
            1409307931622768762,  # General
            1426711816024756314,  # International
            1421903738636865556,  # Media
            1409308015827353720,  # Creation
            1409308088300998707,  # Question
            1409308197809819668,  # Bot command
            1431428103674138634   # Counting to 1000
        ]
        
        # Skip AI responses in blacklisted channels
        if message.channel.id in AI_BLACKLIST_CHANNELS:
            return
        
        # Check if message is in an allowed ticket category
        ALLOWED_TICKET_CATEGORIES = [
            1436498409153626213,  # Support
            1436498445216256031,  # Request CC
            1436498528544227428   # Warning Appeal
        ]
        
        is_in_allowed_ticket_category = False
        if message.channel.category_id in ALLOWED_TICKET_CATEGORIES:
            is_in_allowed_ticket_category = True
        
        # Check if AI operations are enabled (STOP/START control)
        ai_ops_enabled = self.db.get_ai_ops_status()

        # Clean message content for comparison
        content_clean = message.content.strip().lower()
        
        # IGNORE messages that are ONLY punctuation (like ??, .., ???, etc.)
        if content_clean and all(c in '?!.,;:-' for c in content_clean):
            return
        
        # Remove bot mention if present for trigger matching
        bot_mention = f'<@{self.bot.user.id}>'
        bot_mention_nick = f'<@!{self.bot.user.id}>'
        content_for_teach = content_clean.replace(bot_mention.lower(), '').replace(bot_mention_nick.lower(), '').strip()
        
        # IGNORE if content is empty after removing bot mention
        if not content_for_teach:
            return
        
        # Remove common punctuation for better matching
        content_normalized = content_for_teach.replace('?', '').replace('!', '').replace('.', '').replace(',', '').strip()
        
        # IGNORE if content becomes empty after normalization (only had punctuation)
        if not content_normalized:
            return
        
        all_teaches = self.db.get_all_teaches()
        
        if all_teaches:
            def normalize_text(text):
                """Normalize text for better matching"""
                text = text.lower().strip()
                text = text.replace('?', '').replace('!', '').replace('.', '').replace(',', '')
                text = text.replace("'", '').replace('"', '').replace('-', ' ')
                text = ' '.join(text.split())
                return text
            
            def get_similarity(s1, s2):
                """Calculate similarity ratio between two strings"""
                if not s1 or not s2:
                    return 0.0
                shorter = min(len(s1), len(s2))
                longer = max(len(s1), len(s2))
                return shorter / longer
            
            content_norm = normalize_text(content_for_teach)
            
            for teach_id, teach_data in all_teaches.items():
                trigger = teach_data.get('trigger', '')
                trigger_norm = normalize_text(trigger)
                
                if content_norm == trigger_norm:
                    response = teach_data['response'].replace('<user>', message.author.mention)
                    response = self.sanitize_mentions(response)
                    await message.reply(response, mention_author=False)
                    return
                
                if len(trigger_norm) >= 8 and len(content_norm) >= 8:
                    similarity = get_similarity(trigger_norm, content_norm)
                    if similarity >= 0.85:
                        if trigger_norm in content_norm or content_norm in trigger_norm:
                            response = teach_data['response'].replace('<user>', message.author.mention)
                            response = self.sanitize_mentions(response)
                            await message.reply(response, mention_author=False)
                            return
        
        # PRIORITY 2: Handle bot mentions with AI responses (if AI ops enabled)
        has_bot_mention = self.bot.user.mentioned_in(message) and not message.mention_everyone
        
        # If mentioned but no taught response matched, use AI to respond (if enabled)
        # ALLOW mentions in ticket categories even if AI ops is disabled elsewhere
        should_respond_to_mention = has_bot_mention and (ai_ops_enabled or is_in_allowed_ticket_category)
        
        if should_respond_to_mention:
            # If content is empty after removing mention, use a default prompt
            prompt = content_for_teach if content_for_teach else "Hello, how can I help you?"
            async with message.channel.typing():
                response = await self.get_ai_response(prompt, message.author.name, message.guild, message.channel.id)
                await message.reply(response, mention_author=False)

    # DISABLED - /aisetup command
    # @commands.hybrid_command(name='aisetup', description='Enable or disable AI chat')
    # @commands.has_permissions(administrator=True)
    async def aisetup_disabled(self, ctx):
        """Toggle AI chat on/off"""
        current = self.db.get_config('ai_enabled')
        new_state = not current
        self.db.set_config('ai_enabled', new_state)

        status = "✅ enabled" if new_state else "❌ disabled"
        
        embed = discord.Embed(
            title="AI Chat Configuration",
            description=f"AI chat has been {status}",
            color=discord.Color.green() if new_state else discord.Color.red()
        )
        
        if new_state and not self.api_key:
            embed.add_field(
                name="⚠️ Warning",
                value="Hugging Face API key not found. Please add HUGGINGFACE_API_KEY to your secrets.",
                inline=False
            )

        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name='teach', description='Teach the bot a custom response or action')
    @commands.has_permissions(administrator=True)
    async def teach(self, ctx, trigger: str, *, response: str):
        """Teach the bot a custom trigger-response pair or action
        
        Examples:
        !teach what is spiritual battlegrounds? Spiritual Battlegrounds is a Roblox game based on DanDaDan
        !teach start my shift Shift started for <user>
        
        Use <user> as a placeholder for the user's mention
        """
        from datetime import datetime
        
        # Remove bot mentions from trigger if present
        trigger_clean = trigger.replace(f'<@{self.bot.user.id}>', '').replace(f'<@!{self.bot.user.id}>', '').strip()
        
        action_type = 'response'
        if '→' in response or 'automatically' in response.lower():
            action_type = 'action'
        
        teach_id = self.db.add_teach_advanced(trigger_clean, response, ctx.author.id, action_type)
        
        timestamp = datetime.now().strftime('%I:%M %p')
        
        embed = discord.Embed(
            title="✅ Bot Trained Successfully",
            description=f"> **Trigger:** `{trigger_clean}`\n> **Response:** {response[:100]}{'...' if len(response) > 100 else ''}",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 How it works",
            value=f"When users ask `{trigger_clean}` (exact match), I will respond with the taught response.",
            inline=False
        )
        
        if '<user>' in response:
            embed.add_field(
                name="💡 Tip",
                value="The `<user>` placeholder will be replaced with the user's mention.",
                inline=False
            )
        
        embed.set_footer(text=f"Bot trained successfully at {timestamp}")
        
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name='unteach', aliases=['forget'], description='Remove a taught response')
    @commands.has_permissions(administrator=True)
    async def unteach(self, ctx, *, identifier: str):
        """Remove a taught response by trigger name or ID
        
        Examples:
        !unteach what is spiritual battlegrounds
        !unteach 5
        """
        from datetime import datetime
        
        # Try to remove by ID first
        success = self.db.remove_teach(identifier)
        
        # If that didn't work, try removing by trigger name
        if not success:
            success = self.db.remove_teach_by_trigger(identifier)
        
        timestamp = datetime.now().strftime('%I:%M %p')
        
        if success:
            embed = discord.Embed(
                title="✅ Response Removed",
                description=f"The taught response for `{identifier}` has been removed.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Response removed at {timestamp}")
        else:
            embed = discord.Embed(
                title="❌ Not Found",
                description=f"No taught response found for `{identifier}`.\nUse `!teaches` to see all taught responses.",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='stop', description='Stop AI autonomous operations')
    @commands.has_permissions(administrator=True)
    async def stop_ai(self, ctx):
        """Stop AI autonomous operations (ticket handling, etc.)"""
        self.db.set_ai_ops_status(False)
        
        embed = discord.Embed(
            title="⏹️ AI Operations Stopped",
            description="AI autonomous operations have been stopped. The bot will no longer:\n• Handle tickets autonomously\n• Respond to mentions (except taught triggers)\n\nUse `/start` to resume AI operations.",
            color=discord.Color.red()
        )
        
        await ctx.send(embed=embed)
    
    # DISABLED - /start command
    # @commands.hybrid_command(name='start', description='Start AI autonomous operations')
    # @commands.has_permissions(administrator=True)
    async def start_ai_disabled(self, ctx):
        """Start AI autonomous operations (ticket handling, etc.)"""
        self.db.set_ai_ops_status(True)
        
        embed = discord.Embed(
            title="▶️ AI Operations Started",
            description="AI autonomous operations have been resumed. The bot will now:\n• Handle tickets autonomously in configured categories\n• Respond to mentions with AI\n• Use server-wide memory for context\n\nUse `/stop` to pause AI operations.",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
    
    # DISABLED - /commands command
    # @commands.hybrid_command(name='commands', description='Show all available commands')
    async def commands_list_disabled(self, ctx):
        """Display all available bot commands"""
        embed = discord.Embed(
            title="📚 Bot Commands",
            description="Here are all available commands for Spiritual Battlegrounds Bot:",
            color=discord.Color.blue()
        )
        
        # Moderation Commands
        moderation = """
        `!warn [@user] [reason]` - Warn a user
        `!mute [@user] [duration] [reason]` - Mute a user
        `!unmute [@user]` - Unmute a user
        `!kick [@user] [reason]` - Kick a user
        `!ban [@user] [reason]` - Ban a user
        `!purge [amount]` - Delete messages
        """
        embed.add_field(name="⚖️ Moderation", value=moderation, inline=False)
        
        # Shift & Staff Management
        staff = """
        `!shift start [duration]` - Start your shift
        `!shift end` - End your shift
        `!promotion [@user] [rank]` - Promote staff
        `!infraction [@user] [reason]` - Log infraction
        """
        embed.add_field(name="👮 Staff Management", value=staff, inline=False)
        
        # Ticket System
        tickets = """
        `!ticketpanel` - Create ticket panel
        `STOP` - Stop AI in ticket
        `START` - Resume AI in ticket
        """
        embed.add_field(name="🎫 Tickets", value=tickets, inline=False)
        
        # AI Commands
        ai = """
        `!ask [question]` - Ask the AI
        `!teach [trigger] [response]` - Teach AI
        `!forget [teach_id]` - Remove taught response
        `!teaches` - List all taught responses
        """
        embed.add_field(name="🤖 AI System", value=ai, inline=False)
        
        # Utility Commands
        utility = """
        `!userinfo [@user]` - User information
        `!avatar [@user]` - Show avatar
        `!remind [time] [message]` - Set reminder
        `!afk [reason]` - Set AFK status
        """
        embed.add_field(name="🔧 Utility", value=utility, inline=False)
        
        # Configuration
        config = """
        `!config` - Server configuration (Owner only)
        `!aisetup` - Toggle AI chat
        `!verify` - Get verified role
        `!commands` - Show this message
        """
        embed.add_field(name="⚙️ Configuration", value=config, inline=False)
        
        embed.set_footer(text="Use . or / prefix for commands | Type !commands anytime")
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='teaches', description='List all taught responses')
    @commands.has_permissions(administrator=True)
    async def teaches(self, ctx, page: int = 1):
        """List all taught responses with pagination"""
        all_teaches = self.db.get_all_teaches()
        
        if not all_teaches:
            await ctx.send("No taught responses found.", ephemeral=True)
            return
        
        teaches_list = list(all_teaches.items())
        per_page = 10
        total_pages = (len(teaches_list) + per_page - 1) // per_page
        page = max(1, min(page, total_pages))
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_teaches = teaches_list[start_idx:end_idx]

        embed = discord.Embed(
            title="📚 Taught Responses",
            description=f"Total: {len(teaches_list)} | Page {page}/{total_pages}",
            color=discord.Color.blue()
        )

        for teach_id, teach_data in page_teaches:
            trigger = teach_data.get('trigger', 'Unknown')[:50]
            response = teach_data.get('response', '')[:80]
            embed.add_field(
                name=f"ID: {teach_id} | `{trigger}`",
                value=f"{response}{'...' if len(teach_data.get('response', '')) > 80 else ''}",
                inline=False
            )
        
        embed.set_footer(text=f"Use !teaches [page] to view more | !unteach [id or trigger] to remove")

        await ctx.send(embed=embed, ephemeral=True)

    # DISABLED - /aiinfo command
    # @commands.hybrid_command(name='aiinfo', description='Show current AI configuration')
    # @commands.has_permissions(administrator=True)
    async def aiinfo_disabled(self, ctx):
        """Show current AI configuration"""
        ai_enabled = self.db.get_config('ai_enabled')
        ai_model = self.db.get_config('ai_model') or 'meta-llama/llama-3.2-3b-instruct'
        
        embed = discord.Embed(
            title="🤖 AI Configuration",
            color=discord.Color.blue()
        )
        embed.add_field(name="Status", value="✅ Enabled" if ai_enabled else "❌ Disabled", inline=True)
        embed.add_field(name="Model", value=f"`{ai_model}`", inline=True)
        embed.add_field(name="API Key", value="✅ Configured" if self.api_key else "❌ Missing", inline=True)
        
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name='exportteaches', description='Export all taught responses as JSON')
    @commands.has_permissions(administrator=True)
    async def export_teaches(self, ctx):
        """Export all taught responses to a JSON file"""
        import json
        from datetime import datetime
        
        all_teaches = self.db.get_all_teaches()
        
        if not all_teaches:
            await ctx.send("❌ No taught responses to export.", ephemeral=True)
            return
        
        # Create export data
        export_data = {
            'export_date': datetime.utcnow().isoformat(),
            'total_teaches': len(all_teaches),
            'teaches': all_teaches
        }
        
        # Create JSON file
        filename = f"teaches_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        # Send file
        embed = discord.Embed(
            title="✅ Taught Responses Exported",
            description=f"Exported {len(all_teaches)} taught responses",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed, file=discord.File(filename), ephemeral=True)
        
        # Clean up file
        import os
        os.remove(filename)

async def setup(bot):
    await bot.add_cog(AIChat(bot))
