import discord
from discord.ext import commands
from discord import app_commands
from database import Database
from datetime import datetime, timedelta
import re

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    def parse_duration(self, duration_str):
        if not duration_str:
            return None
        
        time_regex = re.compile(r'(\d+)([smhd])')
        matches = time_regex.findall(duration_str.lower())
        
        if not matches:
            return None
        
        total_seconds = 0
        for value, unit in matches:
            value = int(value)
            if unit == 's':
                total_seconds += value
            elif unit == 'm':
                total_seconds += value * 60
            elif unit == 'h':
                total_seconds += value * 3600
            elif unit == 'd':
                total_seconds += value * 86400
        
        return timedelta(seconds=total_seconds)
    
    # DISABLED - /afk command
    # @commands.hybrid_command(name='afk', description='Set yourself as AFK')
    # @app_commands.describe(
    #     duration='Duration (e.g., 30m, 2h, 1d)',
    #     reason='Reason for being AFK',
    #     muted='Auto-assign muted role (true/false)'
    # )
    async def afk_disabled(self, ctx, duration: str = None, *, reason: str = "AFK", muted: bool = False):
        until_time = None
        
        if duration:
            delta = self.parse_duration(duration)
            if delta:
                until_time = datetime.utcnow() + delta
        
        self.db.set_afk(ctx.author.id, reason, until_time, muted)
        
        if muted:
            muted_role_id = self.db.get_config('muted_role')
            if muted_role_id:
                muted_role = ctx.guild.get_role(muted_role_id)
                if muted_role:
                    try:
                        await ctx.author.add_roles(muted_role, reason="Auto-muted while AFK")
                    except:
                        pass
        
        if until_time:
            timestamp = int(until_time.timestamp())
            await ctx.send(f"✅ {ctx.author.mention} is now AFK until <t:{timestamp}:R>: {reason}")
        else:
            await ctx.send(f"✅ {ctx.author.mention} is now AFK: {reason}")
    
    # DISABLED - /unafk command
    # @commands.hybrid_command(name='unafk', description='Remove your AFK status')
    async def unafk_disabled(self, ctx):
        afk_data = self.db.get_afk(ctx.author.id)
        
        if not afk_data:
            await ctx.send(f"{ctx.author.mention}, you are not currently AFK.")
            return
        
        if afk_data.get('muted'):
            muted_role_id = self.db.get_config('muted_role')
            if muted_role_id:
                muted_role = ctx.guild.get_role(muted_role_id)
                if muted_role and muted_role in ctx.author.roles:
                    try:
                        await ctx.author.remove_roles(muted_role, reason="Returned from AFK")
                    except:
                        pass
        
        self.db.remove_afk(ctx.author.id)
        await ctx.send(f"✅ Welcome back, {ctx.author.mention}! Your AFK status has been removed.")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        afk_data = self.db.get_afk(message.author.id)
        if afk_data and not message.content.startswith(('.afk', '!afk', '/afk')):
            if afk_data.get('muted'):
                muted_role_id = self.db.get_config('muted_role')
                if muted_role_id:
                    muted_role = message.guild.get_role(muted_role_id)
                    if muted_role and muted_role in message.author.roles:
                        try:
                            await message.author.remove_roles(muted_role, reason="Returned from AFK")
                        except:
                            pass
            
            self.db.remove_afk(message.author.id)
            await message.channel.send(f"✅ Welcome back, {message.author.mention}! Your AFK status has been removed.", delete_after=5)
        
        if message.mentions:
            for mentioned_user in message.mentions:
                if mentioned_user.bot:
                    continue
                
                afk_data = self.db.get_afk(mentioned_user.id)
                if afk_data:
                    reason = afk_data.get('reason', 'AFK')
                    until = afk_data.get('until')
                    
                    if until:
                        until_time = datetime.fromisoformat(until)
                        remaining = until_time - datetime.utcnow()
                        
                        if remaining.total_seconds() > 0:
                            hours = int(remaining.total_seconds() // 3600)
                            minutes = int((remaining.total_seconds() % 3600) // 60)
                            
                            if hours > 0:
                                time_str = f"{hours}h {minutes}m"
                            else:
                                time_str = f"{minutes}m"
                            
                            await message.channel.send(
                                f"{mentioned_user.mention} is currently AFK: {reason} (Returning in {time_str})",
                                delete_after=10
                            )
                        else:
                            await message.channel.send(
                                f"{mentioned_user.mention} is currently AFK: {reason}",
                                delete_after=10
                            )
                    else:
                        await message.channel.send(
                            f"{mentioned_user.mention} is currently AFK: {reason}",
                            delete_after=10
                        )

async def setup(bot):
    await bot.add_cog(AFK(bot))
