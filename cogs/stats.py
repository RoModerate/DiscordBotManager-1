import discord
from discord.ext import commands, tasks
from config import Config

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_stats.start()
    
    def cog_unload(self):
        self.update_stats.cancel()
    
    @tasks.loop(minutes=5)
    async def update_stats(self):
        await self.bot.wait_until_ready()
        
        guild = None
        if Config.GUILD_ID:
            guild = self.bot.get_guild(Config.GUILD_ID)
        
        if not guild:
            guilds = self.bot.guilds
            if guilds:
                guild = guilds[0]
        
        if not guild:
            print("No guild found for stats update")
            return
        
        try:
            members = [m for m in guild.members if not m.bot]
            bots = [m for m in guild.members if m.bot]
            total_members = len(guild.members)
            
            all_members_channel = guild.get_channel(Config.ALL_MEMBERS_CHANNEL)
            if all_members_channel:
                await all_members_channel.edit(name=f"All Members: {total_members}")
            
            members_only_channel = guild.get_channel(Config.MEMBERS_ONLY_CHANNEL)
            if members_only_channel:
                await members_only_channel.edit(name=f"Members: {len(members)}")
            
            bots_channel = guild.get_channel(Config.BOTS_CHANNEL)
            if bots_channel:
                await bots_channel.edit(name=f"Bots: {len(bots)}")
            
            current_goal = self.get_next_goal(total_members)
            goal_channel = guild.get_channel(Config.GOAL_CHANNEL)
            if goal_channel:
                await goal_channel.edit(name=f"Goal: {current_goal}")
            
            print(f"Stats updated - Total: {total_members}, Members: {len(members)}, Bots: {len(bots)}, Goal: {current_goal}")
        
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def get_next_goal(self, current_count):
        for milestone in Config.GOAL_MILESTONES:
            if current_count < milestone:
                return milestone
        
        next_milestone = ((current_count // 10000) + 1) * 10000
        return next_milestone
    
    # DISABLED - /updatestats command
    # @commands.hybrid_command(name='updatestats', description='Force update voice channel statistics')
    # @commands.has_permissions(administrator=True)
    async def force_update_stats_disabled(self, ctx):
        await self.update_stats()
        
        embed = discord.Embed(
            title="Stats Updated",
            description="Voice channel statistics have been refreshed",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, delete_after=5)
        await ctx.message.delete(delay=5)

async def setup(bot):
    await bot.add_cog(Stats(bot))
