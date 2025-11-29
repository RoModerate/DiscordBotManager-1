import discord
from discord.ext import commands
from datetime import datetime
from database import Database

class ModLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    def get_mod_log_channel(self, guild):
        channel_id = self.db.get_config('mod_log_channel')
        if channel_id:
            return guild.get_channel(channel_id)
        return None
    
    async def log_action(self, guild, embed):
        log_channel = self.get_mod_log_channel(guild)
        if log_channel:
            try:
                await log_channel.send(embed=embed)
            except:
                pass
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.log_ban_action(guild, user)
    
    async def log_ban_action(self, guild, user):
        embed = discord.Embed(
            title="🔨 Member Banned",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="User", value=f"{user.mention} ({user})", inline=True)
        embed.add_field(name="User ID", value=str(user.id), inline=True)
        
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if entry.target.id == user.id:
                    embed.add_field(name="Moderator", value=entry.user.mention, inline=True)
                    if entry.reason:
                        embed.add_field(name="Reason", value=entry.reason, inline=False)
                    break
        except:
            pass
        
        await self.log_action(guild, embed)
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(
            title="🔓 Member Unbanned",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="User", value=f"{user.mention} ({user})", inline=True)
        embed.add_field(name="User ID", value=str(user.id), inline=True)
        
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
                if entry.target.id == user.id:
                    embed.add_field(name="Moderator", value=entry.user.mention, inline=True)
                    if entry.reason:
                        embed.add_field(name="Reason", value=entry.reason, inline=False)
                    break
        except:
            pass
        
        await self.log_action(guild, embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return
        
        await self.check_kick_action(member)
    
    async def check_kick_action(self, member):
        guild = member.guild
        
        try:
            await discord.utils.sleep_until(datetime.utcnow())
            
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                if entry.target.id == member.id:
                    embed = discord.Embed(
                        title="👢 Member Kicked",
                        color=discord.Color.orange(),
                        timestamp=datetime.utcnow()
                    )
                    
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.add_field(name="User", value=f"{member.mention} ({member})", inline=True)
                    embed.add_field(name="User ID", value=str(member.id), inline=True)
                    embed.add_field(name="Moderator", value=entry.user.mention, inline=True)
                    
                    if entry.reason:
                        embed.add_field(name="Reason", value=entry.reason, inline=False)
                    
                    await self.log_action(guild, embed)
                    break
        except:
            pass
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.bot:
            return
        
        if before.timed_out_until != after.timed_out_until:
            await self.log_timeout_action(before, after)
        
        if before.roles != after.roles:
            await self.log_role_change(before, after)
    
    async def log_timeout_action(self, before, after):
        guild = after.guild
        
        if after.timed_out_until is None:
            embed = discord.Embed(
                title="🔊 Member Unmuted",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
        else:
            embed = discord.Embed(
                title="🔇 Member Muted",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            
            duration = (after.timed_out_until - datetime.utcnow()).total_seconds()
            minutes = int(duration / 60)
            hours = int(minutes / 60)
            days = int(hours / 24)
            
            duration_str = ""
            if days > 0:
                duration_str = f"{days} day(s)"
            elif hours > 0:
                duration_str = f"{hours} hour(s)"
            else:
                duration_str = f"{minutes} minute(s)"
            
            embed.add_field(name="Duration", value=duration_str, inline=True)
        
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.add_field(name="User", value=f"{after.mention} ({after})", inline=True)
        embed.add_field(name="User ID", value=str(after.id), inline=True)
        
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
                if entry.target.id == after.id:
                    embed.add_field(name="Moderator", value=entry.user.mention, inline=True)
                    if entry.reason:
                        embed.add_field(name="Reason", value=entry.reason, inline=False)
                    break
        except:
            pass
        
        await self.log_action(guild, embed)
    
    async def log_role_change(self, before, after):
        guild = after.guild
        
        added_roles = set(after.roles) - set(before.roles)
        removed_roles = set(before.roles) - set(after.roles)
        
        if not added_roles and not removed_roles:
            return
        
        embed = discord.Embed(
            title="🎭 Member Roles Updated",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.add_field(name="User", value=f"{after.mention} ({after})", inline=True)
        embed.add_field(name="User ID", value=str(after.id), inline=True)
        
        if added_roles:
            roles_text = ", ".join([role.mention for role in added_roles])
            embed.add_field(name="✅ Added Roles", value=roles_text, inline=False)
        
        if removed_roles:
            roles_text = ", ".join([role.mention for role in removed_roles])
            embed.add_field(name="❌ Removed Roles", value=roles_text, inline=False)
        
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
                if entry.target.id == after.id:
                    embed.add_field(name="Moderator", value=entry.user.mention, inline=True)
                    break
        except:
            pass
        
        await self.log_action(guild, embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        
        if len(message.content) == 0:
            return
        
        log_channel = self.get_mod_log_channel(message.guild)
        if not log_channel or log_channel.id == message.channel.id:
            return
        
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.dark_gray(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.add_field(name="Author", value=f"{message.author.mention} ({message.author})", inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Message ID", value=str(message.id), inline=True)
        
        if message.content:
            content = message.content[:1000]
            embed.add_field(name="Content", value=content, inline=False)
        
        if message.attachments:
            attachments_text = "\n".join([f"[{att.filename}]({att.url})" for att in message.attachments])
            embed.add_field(name="Attachments", value=attachments_text, inline=False)
        
        await self.log_action(message.guild, embed)
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        if not messages:
            return
        
        guild = messages[0].guild
        channel = messages[0].channel
        
        embed = discord.Embed(
            title="🗑️ Bulk Message Delete",
            description=f"**{len(messages)}** messages deleted in {channel.mention}",
            color=discord.Color.dark_gray(),
            timestamp=datetime.utcnow()
        )
        
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.message_bulk_delete):
                embed.add_field(name="Moderator", value=entry.user.mention, inline=True)
                break
        except:
            pass
        
        await self.log_action(guild, embed)
    
    # DISABLED - /setmodlog command
    # @commands.hybrid_command(name='setmodlog', description='Set the moderation log channel')
    # @commands.has_permissions(administrator=True)
    async def set_mod_log_disabled(self, ctx, channel: discord.TextChannel):
        self.db.set_config('mod_log_channel', channel.id)
        
        embed = discord.Embed(
            title="✅ Moderation Log Channel Set",
            description=f"Moderation logs will be sent to {channel.mention}",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
        
        test_embed = discord.Embed(
            title="🛡️ Moderation Logs Active",
            description="All moderation actions will be logged in this channel",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        await channel.send(embed=test_embed)

async def setup(bot):
    await bot.add_cog(ModLogs(bot))
