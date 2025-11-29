import discord
from discord.ext import commands, tasks
from discord import app_commands
from database import Database
from datetime import datetime, timedelta

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.voice_sessions = {}
        self.track_voice_time.start()
    
    def cog_unload(self):
        self.track_voice_time.cancel()
    
    @commands.hybrid_command(name='join', description='Make the bot join your voice channel')
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command.")
            return
        
        channel = ctx.author.voice.channel
        
        if ctx.voice_client:
            if ctx.voice_client.channel == channel:
                await ctx.send("I'm already in your voice channel!")
                return
            else:
                await ctx.voice_client.move_to(channel)
                await ctx.send(f"Moved to {channel.mention}")
        else:
            await channel.connect()
            await ctx.send(f"Joined {channel.mention}")
    
    @commands.hybrid_command(name='leave', description='Make the bot leave the voice channel')
    @commands.has_permissions(moderate_members=True)
    async def leave(self, ctx):
        if ctx.voice_client:
            channel = ctx.voice_client.channel
            await ctx.voice_client.disconnect()
            await ctx.send(f"Left {channel.mention}")
        else:
            await ctx.send("I'm not in a voice channel.")
    
    async def award_voice_xp(self, member, guild_id, xp_amount):
        """Award voice XP and handle level-ups with milestone rewards"""
        leveled_up, new_level = self.db.add_xp(guild_id, member.id, xp_amount)
        
        if leveled_up:
            leveling_cog = self.bot.get_cog('Leveling')
            if leveling_cog and hasattr(leveling_cog, 'level_channel_id'):
                guild = self.bot.get_guild(guild_id)
                if guild:
                    level_channel = guild.get_channel(leveling_cog.level_channel_id)
                    if level_channel:
                        try:
                            await level_channel.send(
                                f"{member.mention} is now **Level {new_level}**! 🎉 (Voice Activity)"
                            )
                        except:
                            pass
                    
                    if new_level in leveling_cog.milestone_roles:
                        await leveling_cog.grant_milestone_role(guild, member, new_level)
                    
                    if new_level == 5:
                        reward_coins = 500
                        if self.db.get_config('economy_enabled'):
                            self.db.add_balance(guild_id, member.id, reward_coins)
                            try:
                                await member.send(f"🎉 You reached Level 5! You earned **{reward_coins}** Spirit Coins!")
                            except:
                                pass
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        
        if not before.channel and after.channel:
            self.voice_sessions[member.id] = {
                'channel_id': after.channel.id,
                'joined_at': datetime.utcnow(),
                'guild_id': after.channel.guild.id
            }
        
        elif before.channel and not after.channel:
            if member.id in self.voice_sessions:
                session = self.voice_sessions[member.id]
                joined_at = session['joined_at']
                duration = (datetime.utcnow() - joined_at).total_seconds() / 60
                
                if duration >= 5:
                    self.db.add_voice_time(session['guild_id'], member.id, int(duration))
                    
                    xp_reward = int(duration / 5) * 10
                    if xp_reward > 0:
                        await self.award_voice_xp(member, session['guild_id'], xp_reward)
                
                del self.voice_sessions[member.id]
        
        elif before.channel and after.channel and before.channel != after.channel:
            if member.id in self.voice_sessions:
                session = self.voice_sessions[member.id]
                joined_at = session['joined_at']
                duration = (datetime.utcnow() - joined_at).total_seconds() / 60
                
                if duration >= 5:
                    self.db.add_voice_time(session['guild_id'], member.id, int(duration))
                
                self.voice_sessions[member.id] = {
                    'channel_id': after.channel.id,
                    'joined_at': datetime.utcnow(),
                    'guild_id': after.channel.guild.id
                }
    
    @tasks.loop(minutes=5)
    async def track_voice_time(self):
        for member_id, session in list(self.voice_sessions.items()):
            joined_at = session['joined_at']
            duration = (datetime.utcnow() - joined_at).total_seconds() / 60
            
            if duration >= 5:
                self.db.add_voice_time(session['guild_id'], member_id, 5)
                
                xp_reward = 10
                guild = self.bot.get_guild(session['guild_id'])
                if guild:
                    member = guild.get_member(member_id)
                    if member:
                        await self.award_voice_xp(member, session['guild_id'], xp_reward)
                
                session['joined_at'] = datetime.utcnow()
    
    @track_voice_time.before_loop
    async def before_track_voice_time(self):
        await self.bot.wait_until_ready()
    
    # DISABLED - /voiceleaderboard command
    # @commands.hybrid_command(name='voiceleaderboard', description='Show the voice activity leaderboard')
    async def voice_leaderboard_disabled(self, ctx):
        voice_data = self.db.data.get('voice_activity', {})
        
        guild_voice = {}
        for key, data in voice_data.items():
            if key.startswith(f"{ctx.guild.id}:"):
                user_id = int(key.split(':')[1])
                guild_voice[user_id] = data.get('total_minutes', 0)
        
        if not guild_voice:
            await ctx.send("No voice activity recorded yet!", ephemeral=True)
            return
        
        sorted_users = sorted(guild_voice.items(), key=lambda x: x[1], reverse=True)[:10]
        
        embed = discord.Embed(
            title="🎙️ Voice Activity Leaderboard",
            description="Top 10 members by voice chat time",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        
        leaderboard_text = ""
        for idx, (user_id, minutes) in enumerate(sorted_users, 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            hours = minutes // 60
            mins = minutes % 60
            leaderboard_text += f"{medal} <@{user_id}> - **{hours}h {mins}m**\n"
        
        embed.add_field(name="Leaderboard", value=leaderboard_text, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Voice(bot))
