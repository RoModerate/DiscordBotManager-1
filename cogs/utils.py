import discord
from discord.ext import commands
from datetime import datetime
from config import Config

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name='help', description='Show all bot commands')
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="Spiritual Battlegrounds Bot",
            description="Complete command list for the server",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        verification_commands = (
            "> **!setupverify** [channel]\n"
            "> Set up verification panel in a channel"
        )
        
        ticket_commands = (
            "> **!ticketpanel** [channel]\n"
            "> Set up ticket panel in a channel\n\n"
            "> **!closeticket**\n"
            "> Close the current ticket"
        )
        
        moderation_commands = (
            "> **!warn** <member> [reason]\n"
            "> Warn a member (automatic escalation)\n\n"
            "> **!warnings** [member]\n"
            "> Check warning count\n\n"
            "> **!clearwarnings** <member>\n"
            "> Clear all warnings for a member\n\n"
            "> **!mute** <member> <duration> [reason]\n"
            "> Mute a member (5m, 1h, 1d, 1w)\n\n"
            "> **!unmute** <member>\n"
            "> Unmute a member\n\n"
            "> **!kick** <member> [reason]\n"
            "> Kick a member from the server\n\n"
            "> **!ban** <member> [reason]\n"
            "> Ban a member from the server\n\n"
            "> **!unban** <user_id> [reason]\n"
            "> Unban a user by their ID\n\n"
            "> **!clear** <amount>\n"
            "> Delete messages (1-100)"
        )
        
        utility_commands = (
            "> **!stats**\n"
            "> View server statistics\n\n"
            "> **!updatestats**\n"
            "> Force update voice channel stats\n\n"
            "> **!ping**\n"
            "> Check bot latency\n\n"
            "> **!serverinfo**\n"
            "> View server information\n\n"
            "> **!help**\n"
            "> Show this help message"
        )
        
        embed.add_field(name="Verification Commands", value=verification_commands, inline=False)
        embed.add_field(name="Ticket Commands", value=ticket_commands, inline=False)
        embed.add_field(name="Moderation Commands", value=moderation_commands, inline=False)
        embed.add_field(name="Utility Commands", value=utility_commands, inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='stats', description='View server statistics')
    async def stats(self, ctx):
        guild = ctx.guild
        
        members = [m for m in guild.members if not m.bot]
        bots = [m for m in guild.members if m.bot]
        online = sum(1 for m in members if m.status != discord.Status.offline)
        
        verified_count = 0
        if Config.VERIFIED_ROLE_ID:
            verified_role = guild.get_role(Config.VERIFIED_ROLE_ID)
            if verified_role:
                verified_count = len(verified_role.members)
        
        embed = discord.Embed(
            title=f"{guild.name} Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Total Members", value=f"> {len(guild.members)}", inline=True)
        embed.add_field(name="Members", value=f"> {len(members)}", inline=True)
        embed.add_field(name="Bots", value=f"> {len(bots)}", inline=True)
        
        embed.add_field(name="Online", value=f"> {online}", inline=True)
        if verified_count > 0:
            embed.add_field(name="Verified", value=f"> {verified_count}", inline=True)
        embed.add_field(name="Channels", value=f"> {len(guild.channels)}", inline=True)
        
        embed.set_footer(text=f"Server ID: {guild.id}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='ping', description='Check bot latency')
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="Pong",
            description=f"> Latency: {latency}ms",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='serverinfo', description='View server information')
    async def serverinfo(self, ctx):
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"{guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Server ID", value=f"> {guild.id}", inline=True)
        embed.add_field(name="Owner", value=f"> {guild.owner.mention}", inline=True)
        embed.add_field(name="Created", value=f"> {guild.created_at.strftime('%Y-%m-%d')}", inline=True)
        
        embed.add_field(name="Members", value=f"> {guild.member_count}", inline=True)
        embed.add_field(name="Roles", value=f"> {len(guild.roles)}", inline=True)
        embed.add_field(name="Channels", value=f"> {len(guild.channels)}", inline=True)
        
        embed.add_field(name="Boost Level", value=f"> {guild.premium_tier}", inline=True)
        embed.add_field(name="Boosts", value=f"> {guild.premium_subscription_count}", inline=True)
        
        if guild.description:
            embed.add_field(name="Description", value=f"> {guild.description}", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utils(bot))
