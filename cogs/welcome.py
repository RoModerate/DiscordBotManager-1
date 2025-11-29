import discord
from discord.ext import commands
from database import Database

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.welcome_channel_id = 1409299795318804612

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            welcome_channel = member.guild.get_channel(self.welcome_channel_id)
            if welcome_channel:
                await welcome_channel.send(
                    f"Welcome {member.mention} to **{member.guild.name}**!"
                )
        except Exception as e:
            print(f"Welcome error: {e}")

async def setup(bot):
    await bot.add_cog(Welcome(bot))