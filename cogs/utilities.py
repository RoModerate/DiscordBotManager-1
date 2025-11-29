import discord
from discord.ext import commands, tasks
from database import Database
from datetime import datetime, timedelta
import asyncio

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.status_rotation.start()
        self.check_reminders.start()
        self.current_status_index = 0
    
    def cog_unload(self):
        self.status_rotation.cancel()
        self.check_reminders.cancel()
    
    @tasks.loop(minutes=5)
    async def status_rotation(self):
        if not self.bot.guilds:
            return
        
        guild = self.bot.guilds[0]
        member_count = guild.member_count
        
        open_tickets = sum(1 for t in self.db.data.get('tickets', {}).values() if t.get('status') == 'open')
        
        statuses = [
            discord.Activity(type=discord.ActivityType.playing, name="Spiritual Battlegrounds"),
            discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} members"),
            discord.Activity(type=discord.ActivityType.listening, name="/help"),
            discord.Activity(type=discord.ActivityType.watching, name=f"{open_tickets} tickets"),
            discord.Activity(type=discord.ActivityType.playing, name="Type /help for commands")
        ]
        
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=statuses[self.current_status_index % len(statuses)]
        )
        
        self.current_status_index += 1
    
    @status_rotation.before_loop
    async def before_status_rotation(self):
        await self.bot.wait_until_ready()
    
    @tasks.loop(minutes=1)
    async def check_reminders(self):
        pending_reminders = self.db.get_pending_reminders()
        
        for reminder in pending_reminders:
            user = self.bot.get_user(reminder['user_id'])
            if user:
                embed = discord.Embed(
                    title="⏰ Reminder",
                    description=reminder['message'],
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                
                try:
                    await user.send(embed=embed)
                except:
                    channel = self.bot.get_channel(reminder['channel_id'])
                    if channel:
                        await channel.send(f"{user.mention}", embed=embed)
            
            self.db.complete_reminder(reminder['id'])
    
    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        
        self.db.add_deleted_message({
            'channel_id': message.channel.id,
            'author_id': message.author.id,
            'author_name': str(message.author),
            'content': message.content,
            'deleted_at': datetime.utcnow().isoformat(),
            'attachments': [a.url for a in message.attachments]
        })
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        
        if before.content == after.content:
            return
        
        self.db.add_edited_message({
            'channel_id': before.channel.id,
            'author_id': before.author.id,
            'author_name': str(before.author),
            'old_content': before.content,
            'new_content': after.content,
            'edited_at': datetime.utcnow().isoformat()
        })
    
    @commands.hybrid_command(name='say', description='Make the bot say something')
    @commands.has_permissions(moderate_members=True)
    async def say(self, ctx, channel: discord.TextChannel, *, message: str):
        if '@everyone' in message or '@here' in message:
            await ctx.send("❌ Cannot use @everyone or @here", ephemeral=True)
            return
        
        for role in ctx.guild.roles:
            if f'<@&{role.id}>' in message:
                await ctx.send("❌ Cannot mention roles", ephemeral=True)
                return
        
        if len(message) > 1000:
            await ctx.send("❌ Message too long (max 1000 characters)", ephemeral=True)
            return
        
        case_id = self.db.add_mod_case(
            guild_id=ctx.guild.id,
            user_id=ctx.author.id,
            moderator_id=ctx.author.id,
            action='say_command',
            reason=f'Used say command in {channel.mention}: {message[:100]}'
        )
        
        await channel.send(message)
        
        embed = discord.Embed(
            title="✅ Message Sent",
            description=f"Message sent to {channel.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="Case ID", value=f"`{case_id}`", inline=True)
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='snipe', description='Show the last deleted message')
    @commands.has_permissions(moderate_members=True)
    async def snipe(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        
        deleted_messages = self.db.get_deleted_messages(channel.id, limit=1)
        
        if not deleted_messages:
            await ctx.send(f"No recently deleted messages in {channel.mention}", ephemeral=True)
            return
        
        msg = deleted_messages[0]
        deleted_time = datetime.fromisoformat(msg['deleted_at'])
        time_ago = (datetime.utcnow() - deleted_time).total_seconds()
        
        if time_ago > 300:
            await ctx.send("Last deleted message is too old (>5 minutes)", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔍 Deleted Message",
            description=msg['content'] or "*No content*",
            color=discord.Color.red(),
            timestamp=deleted_time
        )
        
        embed.set_author(name=msg['author_name'])
        embed.set_footer(text=f"In #{channel.name}")
        
        if msg.get('attachments'):
            embed.add_field(name="Attachments", value='\n'.join(msg['attachments']), inline=False)
        
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='editsnipe', description='Show the last edited message')
    @commands.has_permissions(moderate_members=True)
    async def editsnipe(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        
        edited_messages = self.db.get_edited_messages(channel.id, limit=1)
        
        if not edited_messages:
            await ctx.send(f"No recently edited messages in {channel.mention}", ephemeral=True)
            return
        
        msg = edited_messages[0]
        edited_time = datetime.fromisoformat(msg['edited_at'])
        time_ago = (datetime.utcnow() - edited_time).total_seconds()
        
        if time_ago > 300:
            await ctx.send("Last edited message is too old (>5 minutes)", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📝 Edited Message",
            color=discord.Color.orange(),
            timestamp=edited_time
        )
        
        embed.set_author(name=msg['author_name'])
        embed.add_field(name="Before", value=msg['old_content'][:1024] or "*No content*", inline=False)
        embed.add_field(name="After", value=msg['new_content'][:1024] or "*No content*", inline=False)
        embed.set_footer(text=f"In #{channel.name}")
        
        await ctx.send(embed=embed, ephemeral=True)
    
    # DISABLED - /serverinfo command
    # @commands.hybrid_command(name='serverinfo', description='Show server information')
    async def serverinfo_disabled(self, ctx):
        pass
    
    # DISABLED - /userinfo command
    # @commands.hybrid_command(name='userinfo', description='Show user information')
    async def userinfo_disabled(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(
            title=f"👤 {member.display_name}",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="Username", value=str(member), inline=True)
        embed.add_field(name="Nickname", value=member.nick or "None", inline=True)
        embed.add_field(name="ID", value=f"`{member.id}`", inline=True)
        
        embed.add_field(name="Account Created", value=member.created_at.strftime("%b %d, %Y"), inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%b %d, %Y") if member.joined_at else "Unknown", inline=True)
        
        roles = [role.mention for role in member.roles[1:][:10]]
        embed.add_field(name=f"Roles [{len(member.roles) - 1}]", value=' '.join(roles) if roles else "None", inline=False)
        
        user_level_data = self.db.get_user_level(ctx.guild.id, member.id)
        embed.add_field(name="Level", value=f"**{user_level_data.get('level', 1)}**", inline=True)
        embed.add_field(name="XP", value=f"**{user_level_data.get('xp', 0)}**", inline=True)
        
        verification_data = self.db.get_verification_data(member.id)
        if verification_data:
            embed.add_field(name="Roblox", value=verification_data['roblox_username'], inline=True)
        
        voice_time = self.db.get_voice_time(ctx.guild.id, member.id)
        if voice_time > 0:
            hours = voice_time // 60
            minutes = voice_time % 60
            embed.add_field(name="Voice Time", value=f"{hours}h {minutes}m", inline=True)
        
        embed.set_footer(text=f"User ID: {member.id}")
        
        await ctx.send(embed=embed)
    
    # DISABLED - /avatar command
    # @commands.hybrid_command(name='avatar', description='Show a user\'s avatar')
    async def avatar_disabled(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(
            title=f"🖼️ {member.display_name}'s Avatar",
            color=discord.Color.blue()
        )
        
        embed.set_image(url=member.display_avatar.url)
        embed.add_field(name="Download", value=f"[Click here]({member.display_avatar.url})", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='remind', description='Set a reminder')
    async def remind(self, ctx, time: str, *, message: str):
        time_units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400
        }
        
        try:
            amount = int(time[:-1])
            unit = time[-1].lower()
            
            if unit not in time_units:
                await ctx.send("❌ Invalid time unit. Use s (seconds), m (minutes), h (hours), or d (days)", ephemeral=True)
                return
            
            seconds = amount * time_units[unit]
            
            if seconds > 604800:
                await ctx.send("❌ Reminder time cannot exceed 7 days", ephemeral=True)
                return
            
            remind_at = datetime.utcnow() + timedelta(seconds=seconds)
            reminder_id = self.db.add_reminder(ctx.author.id, ctx.channel.id, message, remind_at)
            
            embed = discord.Embed(
                title="✅ Reminder Set",
                description=f"I'll remind you in **{time}** about:\n{message}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Reminder ID: {reminder_id}")
            
            await ctx.send(embed=embed, ephemeral=True)
        except (ValueError, IndexError):
            await ctx.send("❌ Invalid time format. Examples: 30s, 5m, 2h, 1d", ephemeral=True)
    
    # DISABLED - /dm command
    # @commands.hybrid_command(name='dm', description='Send a DM to a user through the bot')
    # @commands.has_permissions(moderate_members=True)
    async def dm_disabled(self, ctx, member: discord.Member, *, message: str):
        if len(message) > 2000:
            await ctx.send("❌ Message too long (max 2000 characters)", ephemeral=True)
            return
        
        try:
            embed = discord.Embed(
                title=f"📬 Message from {ctx.guild.name}",
                description=message,
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"Sent by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            
            await member.send(embed=embed)
            
            case_id = self.db.add_mod_case(
                guild_id=ctx.guild.id,
                user_id=member.id,
                moderator_id=ctx.author.id,
                action='dm_command',
                reason=f'Sent DM to {member}: {message[:100]}'
            )
            
            success_embed = discord.Embed(
                title="✅ DM Sent",
                description=f"Successfully sent DM to {member.mention}",
                color=discord.Color.green()
            )
            success_embed.add_field(name="Message Preview", value=message[:200], inline=False)
            success_embed.add_field(name="Case ID", value=f"`{case_id}`", inline=True)
            
            await ctx.send(embed=success_embed, ephemeral=True)
            
        except discord.Forbidden:
            await ctx.send(f"❌ Cannot send DM to {member.mention}. They may have DMs disabled.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Failed to send DM: {e}", ephemeral=True)
    

async def setup(bot):
    await bot.add_cog(Utilities(bot))
