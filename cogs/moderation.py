import discord
from discord.ext import commands
from datetime import timedelta
import json
import os
from config import Config

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings_file = 'warnings.json'
        self.warnings = self.load_warnings()
    
    def load_warnings(self):
        if os.path.exists(self.warnings_file):
            with open(self.warnings_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_warnings(self):
        with open(self.warnings_file, 'w') as f:
            json.dump(self.warnings, f, indent=4)
    
    def get_user_warnings(self, guild_id, user_id):
        guild_key = str(guild_id)
        user_key = str(user_id)
        return self.warnings.get(guild_key, {}).get(user_key, 0)
    
    def add_warning(self, guild_id, user_id):
        guild_key = str(guild_id)
        user_key = str(user_id)
        
        if guild_key not in self.warnings:
            self.warnings[guild_key] = {}
        
        if user_key not in self.warnings[guild_key]:
            self.warnings[guild_key][user_key] = 0
        
        self.warnings[guild_key][user_key] += 1
        self.save_warnings()
        return self.warnings[guild_key][user_key]
    
    def is_romoderate(self, member):
        if member.guild_permissions.administrator:
            return True
        if Config.ROMODERATE_ROLE_ID:
            return any(role.id == Config.ROMODERATE_ROLE_ID for role in member.roles)
        return False
    
    @commands.hybrid_command(name='warn', description='Warn a member')
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if not self.is_romoderate(ctx.author):
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to use this command",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if member.bot:
            embed = discord.Embed(
                title="Error",
                description="You cannot warn bots",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        warning_count = self.add_warning(ctx.guild.id, member.id)
        
        mute_duration = None
        if warning_count == 2:
            mute_duration = timedelta(minutes=3)
        elif warning_count == 3:
            mute_duration = timedelta(minutes=15)
        elif warning_count == 4:
            mute_duration = timedelta(hours=1)
        elif warning_count == 5:
            mute_duration = timedelta(hours=5)
        elif warning_count == 6:
            mute_duration = timedelta(days=1)
        elif warning_count == 7:
            mute_duration = timedelta(weeks=1)
        elif warning_count >= 8:
            try:
                await member.ban(reason=f"Warning #{warning_count}: {reason}")
                embed = discord.Embed(
                    title="Member Banned",
                    description=f"{member.mention} has been permanently banned\n\n> Warning: {warning_count}/8\n> Reason: {reason}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
            except Exception as e:
                embed = discord.Embed(
                    title="Error",
                    description=f"Failed to ban member: {e}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
        
        if mute_duration:
            try:
                await member.timeout(mute_duration, reason=f"Warning #{warning_count}: {reason}")
                embed = discord.Embed(
                    title="Member Warned and Muted",
                    description=f"{member.mention} has been warned and muted\n\n> Warning: {warning_count}/8\n> Duration: {self.format_duration(mute_duration)}\n> Reason: {reason}",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(
                    title="Error",
                    description=f"Failed to mute member: {e}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Member Warned",
                description=f"{member.mention} has been warned\n\n> Warning: {warning_count}/8\n> Reason: {reason}",
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title=f"Warning in {ctx.guild.name}",
                description=f"You have been warned by a staff member\n\n> Warning: {warning_count}/8\n> Reason: {reason}",
                color=discord.Color.orange()
            )
            await member.send(embed=dm_embed)
        except:
            pass
    
    def format_duration(self, delta):
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        parts = []
        if days:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        return ', '.join(parts) if parts else "0 minutes"
    
    @commands.hybrid_command(name='warnings', description='Check warnings for a member')
    async def check_warnings(self, ctx, member: discord.Member = None):
        if not self.is_romoderate(ctx.author) and member != ctx.author:
            embed = discord.Embed(
                title="Permission Denied",
                description="You can only check your own warnings",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        target = member or ctx.author
        warning_count = self.get_user_warnings(ctx.guild.id, target.id)
        
        embed = discord.Embed(
            title="Warning Status",
            description=f"{target.mention} has {warning_count}/8 warnings",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='clearwarnings', description='Clear all warnings for a member')
    @commands.has_permissions(moderate_members=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        if not self.is_romoderate(ctx.author):
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to use this command",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        guild_key = str(ctx.guild.id)
        user_key = str(member.id)
        
        if guild_key in self.warnings and user_key in self.warnings[guild_key]:
            del self.warnings[guild_key][user_key]
            self.save_warnings()
        
        embed = discord.Embed(
            title="Warnings Cleared",
            description=f"All warnings have been cleared for {member.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='mute', description='Mute a member for a specified duration')
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
        if not self.is_romoderate(ctx.author):
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to use this command",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        try:
            time_delta = self.parse_duration(duration)
            await member.timeout(time_delta, reason=reason)
            
            embed = discord.Embed(
                title="Member Muted",
                description=f"{member.mention} has been muted\n\n> Duration: {self.format_duration(time_delta)}\n> Reason: {reason}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        except ValueError as e:
            embed = discord.Embed(
                title="Error",
                description=str(e),
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to mute member: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    def parse_duration(self, duration_str):
        duration_str = duration_str.lower()
        
        if duration_str.endswith('m'):
            minutes = int(duration_str[:-1])
            return timedelta(minutes=minutes)
        elif duration_str.endswith('h'):
            hours = int(duration_str[:-1])
            return timedelta(hours=hours)
        elif duration_str.endswith('d'):
            days = int(duration_str[:-1])
            return timedelta(days=days)
        elif duration_str.endswith('w'):
            weeks = int(duration_str[:-1])
            return timedelta(weeks=weeks)
        else:
            raise ValueError("Invalid duration format. Use: 5m, 1h, 1d, 1w")
    
    @commands.hybrid_command(name='unmute', description='Unmute a member')
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        if not self.is_romoderate(ctx.author):
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to use this command",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.timeout(None)
            embed = discord.Embed(
                title="Member Unmuted",
                description=f"{member.mention} has been unmuted",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to unmute member: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='kick', description='Kick a member from the server')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if not self.is_romoderate(ctx.author):
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to use this command",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="Member Kicked",
                description=f"{member.mention} has been kicked\n\n> Reason: {reason}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to kick member: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='ban', description='Ban a member from the server')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if not self.is_romoderate(ctx.author):
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to use this command",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="Member Banned",
                description=f"{member.mention} has been banned\n\n> Reason: {reason}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to ban member: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='unban', description='Unban a user from the server')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str = "No reason provided"):
        if not self.is_romoderate(ctx.author):
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to use this command",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            embed = discord.Embed(
                title="Member Unbanned",
                description=f"{user.mention} has been unbanned\n\n> Reason: {reason}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to unban user: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    # DISABLED - /clear command
    # @commands.hybrid_command(name='clear', description='Clear a specified number of messages')
    # @commands.has_permissions(manage_messages=True)
    async def clear_disabled(self, ctx, amount: int):
        if not self.is_romoderate(ctx.author):
            embed = discord.Embed(
                title="Permission Denied",
                description="You do not have permission to use this command",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if amount < 1 or amount > 100:
            embed = discord.Embed(
                title="Error",
                description="Amount must be between 1 and 100",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
            embed = discord.Embed(
                title="Messages Cleared",
                description=f"Deleted {len(deleted) - 1} message(s)",
                color=discord.Color.green()
            )
            msg = await ctx.send(embed=embed)
            await msg.delete(delay=5)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to clear messages: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    # DISABLED - /purge command
    # @commands.hybrid_command(name='purge', description='Advanced message purge with filters')
    # @commands.has_permissions(manage_messages=True)
    async def purge_disabled(self, ctx, amount: int, filter_type: str = None, *, filter_value: str = None):
        if not self.is_romoderate(ctx.author):
            await ctx.send("❌ You don't have permission to use this command", ephemeral=True)
            return
        
        if amount < 1 or amount > 500:
            await ctx.send("❌ Amount must be between 1 and 500", ephemeral=True)
            return
        
        def check_filter(message):
            if filter_type == 'user' and filter_value:
                return str(message.author.id) == filter_value or message.author.mention == filter_value
            elif filter_type == 'bot':
                return message.author.bot
            elif filter_type == 'embeds':
                return len(message.embeds) > 0
            elif filter_type == 'links':
                return 'http://' in message.content or 'https://' in message.content
            elif filter_type == 'attachments':
                return len(message.attachments) > 0
            elif filter_type == 'contains' and filter_value:
                return filter_value.lower() in message.content.lower()
            return True
        
        try:
            await ctx.defer(ephemeral=True)
            deleted = await ctx.channel.purge(limit=amount, check=check_filter)
            
            filter_desc = f"**Filter**: {filter_type}" if filter_type else "**Filter**: None"
            if filter_value:
                filter_desc += f" ({filter_value})"
            
            await ctx.send(f"✅ Deleted **{len(deleted)}** message(s)\n{filter_desc}", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Failed to purge messages: {e}", ephemeral=True)
    
    @commands.hybrid_command(name='lock', description='Lock a channel to prevent members from sending messages')
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None, *, reason: str = "No reason provided"):
        if not self.is_romoderate(ctx.author):
            await ctx.send("❌ You don't have permission to use this command", ephemeral=True)
            return
        
        channel = channel or ctx.channel
        
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False, reason=reason)
            
            embed = discord.Embed(
                title="🔒 Channel Locked",
                description=f"{channel.mention} has been locked",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Locked by {ctx.author}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to lock channel: {e}", ephemeral=True)
    
    @commands.hybrid_command(name='unlock', description='Unlock a channel to allow members to send messages')
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None, *, reason: str = "No reason provided"):
        if not self.is_romoderate(ctx.author):
            await ctx.send("❌ You don't have permission to use this command", ephemeral=True)
            return
        
        channel = channel or ctx.channel
        
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=None, reason=reason)
            
            embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description=f"{channel.mention} has been unlocked",
                color=discord.Color.green()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Unlocked by {ctx.author}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to unlock channel: {e}", ephemeral=True)
    
    # DISABLED - /slowmode command
    # @commands.hybrid_command(name='slowmode', description='Set channel slowmode delay')
    # @commands.has_permissions(manage_channels=True)
    async def slowmode_disabled(self, ctx, seconds: int, channel: discord.TextChannel = None):
        if not self.is_romoderate(ctx.author):
            await ctx.send("❌ You don't have permission to use this command", ephemeral=True)
            return
        
        channel = channel or ctx.channel
        
        if seconds < 0 or seconds > 21600:
            await ctx.send("❌ Slowmode must be between 0 and 21600 seconds (6 hours)", ephemeral=True)
            return
        
        try:
            await channel.edit(slowmode_delay=seconds)
            
            if seconds == 0:
                await ctx.send(f"✅ Slowmode disabled for {channel.mention}")
            else:
                embed = discord.Embed(
                    title="⏱️ Slowmode Updated",
                    description=f"Slowmode set to **{seconds}** seconds for {channel.mention}",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to set slowmode: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
