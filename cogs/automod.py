import discord
from discord.ext import commands
from datetime import datetime, timedelta
from collections import defaultdict
from database import Database

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        
        self.message_cache = defaultdict(list)
        self.mention_cache = defaultdict(list)
        
        self.spam_threshold = 5
        self.spam_interval = 5
        self.duplicate_threshold = 3
        self.mention_threshold = 5
        self.caps_threshold = 0.7
        self.caps_min_length = 10
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.author.guild_permissions.manage_messages:
            return
        
        automod_enabled = self.db.get_config('auto_mod_enabled') or False
        if not automod_enabled:
            return
        
        exempt_roles = self.db.get_config('automod_exempt_roles') or []
        if any(role.id in exempt_roles for role in message.author.roles):
            return
        
        current_time = datetime.utcnow()
        
        if await self.check_spam(message, current_time):
            return
        
        if await self.check_mass_mentions(message):
            return
        
        if await self.check_caps(message):
            return
        
        if await self.check_links(message):
            return
    
    async def check_spam(self, message, current_time):
        user_messages = self.message_cache[message.author.id]
        
        user_messages = [msg for msg in user_messages if current_time - msg['time'] < timedelta(seconds=self.spam_interval)]
        
        user_messages.append({
            'time': current_time,
            'content': message.content,
            'channel': message.channel.id
        })
        
        self.message_cache[message.author.id] = user_messages
        
        if len(user_messages) >= self.spam_threshold:
            try:
                await message.delete()
                
                await message.author.timeout(timedelta(minutes=5), reason="Auto-Mod: Spam detected")
                
                embed = discord.Embed(
                    title="🛡️ Auto-Mod Action",
                    description=f"{message.author.mention} was muted for **5 minutes** for spam",
                    color=discord.Color.orange()
                )
                await message.channel.send(embed=embed, delete_after=10)
                
                self.db.log_automod_action(
                    guild_id=message.guild.id,
                    user_id=message.author.id,
                    action='mute',
                    reason='Spam detection',
                    duration=300
                )
                
                self.message_cache[message.author.id] = []
                return True
            except:
                pass
        
        duplicate_count = sum(1 for msg in user_messages if msg['content'] == message.content)
        if duplicate_count >= self.duplicate_threshold:
            try:
                await message.delete()
                
                embed = discord.Embed(
                    description=f"❌ {message.author.mention} Please don't spam duplicate messages",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed, delete_after=5)
                
                self.db.log_automod_action(
                    guild_id=message.guild.id,
                    user_id=message.author.id,
                    action='delete',
                    reason=f'Duplicate spam ({duplicate_count} duplicates)',
                    duration=None
                )
                
                return True
            except:
                pass
        
        return False
    
    async def check_mass_mentions(self, message):
        mention_count = len(message.mentions) + len(message.role_mentions)
        
        if mention_count >= self.mention_threshold:
            try:
                await message.delete()
                
                await message.author.timeout(timedelta(minutes=10), reason="Auto-Mod: Mass mentions")
                
                embed = discord.Embed(
                    title="🛡️ Auto-Mod Action",
                    description=f"{message.author.mention} was muted for **10 minutes** for mass mentions ({mention_count} mentions)",
                    color=discord.Color.orange()
                )
                await message.channel.send(embed=embed, delete_after=10)
                
                self.db.log_automod_action(
                    guild_id=message.guild.id,
                    user_id=message.author.id,
                    action='mute',
                    reason=f'Mass mentions ({mention_count})',
                    duration=600
                )
                
                return True
            except:
                pass
        
        return False
    
    async def check_caps(self, message):
        if len(message.content) < self.caps_min_length:
            return False
        
        caps_count = sum(1 for char in message.content if char.isupper())
        total_letters = sum(1 for char in message.content if char.isalpha())
        
        if total_letters == 0:
            return False
        
        caps_ratio = caps_count / total_letters
        
        if caps_ratio >= self.caps_threshold:
            try:
                await message.delete()
                
                await message.author.timeout(timedelta(minutes=3), reason="Auto-Mod: Excessive caps")
                
                embed = discord.Embed(
                    title="🛡️ Auto-Mod Action",
                    description=f"{message.author.mention} was muted for **3 minutes** for excessive caps ({int(caps_ratio * 100)}% caps)",
                    color=discord.Color.orange()
                )
                await message.channel.send(embed=embed, delete_after=10)
                
                self.db.log_automod_action(
                    guild_id=message.guild.id,
                    user_id=message.author.id,
                    action='mute',
                    reason=f'Excessive caps ({int(caps_ratio * 100)}%)',
                    duration=180
                )
                
                return True
            except:
                pass
        
        return False
    
    async def check_links(self, message):
        link_filter_enabled = self.db.get_config('link_filter_enabled') or False
        if not link_filter_enabled:
            return False
        
        whitelisted_domains = self.db.get_config('whitelisted_domains') or [
            'discord.gg', 'discord.com', 'youtube.com', 'youtu.be',
            'twitch.tv', 'twitter.com', 'x.com', 'roblox.com'
        ]
        
        if 'http://' in message.content or 'https://' in message.content:
            is_whitelisted = any(domain in message.content.lower() for domain in whitelisted_domains)
            
            if not is_whitelisted:
                try:
                    await message.delete()
                    
                    embed = discord.Embed(
                        description=f"❌ {message.author.mention} Unauthorized links are not allowed",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed, delete_after=5)
                    
                    self.db.log_automod_action(
                        guild_id=message.guild.id,
                        user_id=message.author.id,
                        action='delete',
                        reason='Unauthorized link posted',
                        duration=None
                    )
                    
                    return True
                except:
                    pass
        
        return False
    
    # DISABLED - /automod command
    # @commands.hybrid_command(name='automod', description='Toggle auto-moderation on or off')
    # @commands.has_permissions(administrator=True)
    async def toggle_automod_disabled(self, ctx, enabled: bool):
        self.db.set_config('auto_mod_enabled', enabled)
        
        status = "✅ enabled" if enabled else "❌ disabled"
        embed = discord.Embed(
            title="Auto-Moderation Settings",
            description=f"Auto-moderation is now {status}",
            color=discord.Color.green() if enabled else discord.Color.red()
        )
        
        await ctx.send(embed=embed)
    
    # DISABLED - /linkfilter command
    # @commands.hybrid_command(name='linkfilter', description='Toggle link filtering on or off')
    # @commands.has_permissions(administrator=True)
    async def toggle_link_filter_disabled(self, ctx, enabled: bool):
        self.db.set_config('link_filter_enabled', enabled)
        
        status = "✅ enabled" if enabled else "❌ disabled"
        embed = discord.Embed(
            title="Link Filter Settings",
            description=f"Link filtering is now {status}",
            color=discord.Color.green() if enabled else discord.Color.red()
        )
        
        await ctx.send(embed=embed)
    
    # DISABLED - /automodstats command
    # @commands.hybrid_command(name='automodstats', description='View auto-mod statistics')
    # @commands.has_permissions(moderate_members=True)
    async def automod_stats_disabled(self, ctx):
        logs = self.db.data.get('automod_logs', [])
        
        guild_logs = [log for log in logs if log.get('guild_id') == ctx.guild.id]
        
        if not guild_logs:
            await ctx.send("No auto-mod actions recorded yet", ephemeral=True)
            return
        
        recent_logs = guild_logs[-10:]
        
        total_actions = len(guild_logs)
        spam_actions = sum(1 for log in guild_logs if 'spam' in log.get('reason', '').lower())
        mention_actions = sum(1 for log in guild_logs if 'mention' in log.get('reason', '').lower())
        
        embed = discord.Embed(
            title="🛡️ Auto-Mod Statistics",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Total Actions", value=str(total_actions), inline=True)
        embed.add_field(name="Spam Violations", value=str(spam_actions), inline=True)
        embed.add_field(name="Mass Mentions", value=str(mention_actions), inline=True)
        
        recent_text = ""
        for log in recent_logs[-5:]:
            user_id = log.get('user_id')
            reason = log.get('reason', 'Unknown')
            timestamp = log.get('timestamp', 'Unknown')
            recent_text += f"<@{user_id}> - {reason} ({timestamp})\n"
        
        if recent_text:
            embed.add_field(name="Recent Actions", value=recent_text, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
