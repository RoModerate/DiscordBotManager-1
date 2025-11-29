import discord
from discord.ext import commands
from database import Database
from datetime import datetime, timedelta

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.level_channel_id = 1409304816718709006

        self.milestone_roles = {
            5: {'name': 'Active Member', 'id': None},
            10: {'name': 'Regular', 'id': None},
            25: {'name': 'Veteran', 'id': None},
            50: {'name': 'Legend', 'id': None}
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if not message.guild:
            return

        excluded_channels = self.db.get_config('excluded_xp_channels') or []
        if message.channel.id in excluded_channels:
            return

        counting_channel = self.db.get_config('counting_channel')
        if message.channel.id == counting_channel:
            return

        user_data = self.db.get_user_level(message.guild.id, message.author.id)

        last_message = user_data.get('last_message')
        if last_message:
            last_time = datetime.fromisoformat(last_message)
            if datetime.utcnow() - last_time < timedelta(seconds=60):
                return

        user_data['last_message'] = datetime.utcnow().isoformat()

        xp_gain = 15

        verified_role_id = self.db.get_config('verified_role')
        if verified_role_id:
            member_role_ids = [role.id for role in message.author.roles]
            if verified_role_id in member_role_ids:
                xp_gain += 5

        if len(set([m.id for m in message.channel.members if not m.bot])) >= 3:
            xp_gain += 10

        leveled_up, new_level = self.db.add_xp(message.guild.id, message.author.id, xp_gain)

        if leveled_up:
            level_channel = message.guild.get_channel(self.level_channel_id)
            if level_channel:
                try:
                    await level_channel.send(
                        f"{message.author.mention} is now **Level {new_level}**! 🎉"
                    )
                except:
                    pass

            if new_level in self.milestone_roles:
                await self.grant_milestone_role(message.guild, message.author, new_level)

            if new_level == 5:
                reward_coins = 500
                if self.db.get_config('economy_enabled'):
                    self.db.add_balance(message.guild.id, message.author.id, reward_coins)
                    try:
                        await message.author.send(f"🎉 You reached Level 5! You earned **{reward_coins}** Spirit Coins!")
                    except:
                        pass

        self.db.track_daily_message(message.guild.id)

    async def grant_milestone_role(self, guild, member, level):
        milestone_info = self.milestone_roles.get(level)
        if not milestone_info:
            return

        role = discord.utils.get(guild.roles, name=milestone_info['name'])

        if role:
            try:
                await member.add_roles(role, reason=f"Reached level {level}")
            except:
                pass

    # DISABLED - /serverinfo command
    # @commands.hybrid_command(name='serverinfo', description='Get server information')
    async def server_info_disabled(self, ctx):
        pass # Command disabled

    # DISABLED - /setmodlog command
    # @commands.hybrid_command(name='setmodlog', description='Set the mod log channel')
    # @commands.has_permissions(manage_channels=True)
    async def set_modlog_disabled(self, ctx, channel: discord.TextChannel):
        pass # Command disabled

    # DISABLED - /resetmistakes command
    # @commands.hybrid_command(name='resetmistakes', description='Reset mistakes for a user')
    # @commands.has_permissions(administrator=True)
    async def reset_mistakes_disabled(self, ctx, member: discord.Member):
        pass # Command disabled

    # DISABLED - /slowmode command
    # @commands.hybrid_command(name='slowmode', description='Set the slowmode for a channel')
    # @commands.has_permissions(manage_channels=True)
    async def slow_mode_disabled(self, ctx, seconds: int):
        pass # Command disabled

    # DISABLED - /automodstats command
    # @commands.hybrid_command(name='automodstats', description='View automod statistics')
    async def automod_stats_disabled(self, ctx):
        pass # Command disabled


    # DISABLED - /rank command
    # @commands.hybrid_command(name='rank', description='Check your or another user\'s rank and XP')
    async def rank_disabled(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_data = self.db.get_user_level(ctx.guild.id, member.id)
        level = user_data.get('level', 1)
        xp = user_data.get('xp', 0)
        xp_needed = self.db.get_xp_for_level(level)

        all_users = {}
        for key, data in self.db.data.get('levels', {}).items():
            if key.startswith(f"{ctx.guild.id}:"):
                user_id = int(key.split(':')[1])
                total_xp = (data['level'] - 1) * 1000 + data['xp']
                all_users[user_id] = total_xp

        sorted_users = sorted(all_users.items(), key=lambda x: x[1], reverse=True)
        rank = next((i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == member.id), 0)

        embed = discord.Embed(
            title=f"📊 Rank for {member.display_name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(name="XP", value=f"**{xp}** / {xp_needed}", inline=True)
        embed.add_field(name="Rank", value=f"**#{rank}**", inline=True)

        progress = int((xp / xp_needed) * 20)
        progress_bar = f"[{'█' * progress}{'░' * (20 - progress)}] {int((xp / xp_needed) * 100)}%"
        embed.add_field(name="Progress", value=f"`{progress_bar}`", inline=False)

        if self.db.get_config('economy_enabled'):
            balance = self.db.get_balance(ctx.guild.id, member.id)
            embed.add_field(name="Spirit Coins", value=f"**{balance}** SC", inline=True)

        await ctx.send(embed=embed)

    # DISABLED - /leaderboard command
    # @commands.hybrid_command(name='leaderboard', description='Show the top 10 server levels')
    async def leaderboard_disabled(self, ctx):
        all_users = {}
        for key, data in self.db.data.get('levels', {}).items():
            if key.startswith(f"{ctx.guild.id}:"):
                user_id = int(key.split(':')[1])
                total_xp = (data['level'] - 1) * 1000 + data.get('xp', 0)
                all_users[user_id] = {
                    'level': data.get('level', 1),
                    'xp': data.get('xp', 0),
                    'total_xp': total_xp
                }

        sorted_users = sorted(all_users.items(), key=lambda x: x[1]['total_xp'], reverse=True)[:10]

        if not sorted_users:
            await ctx.send("No users have earned XP yet!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🏆 Level Leaderboard",
            description="Top 10 members by level and XP",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )

        leaderboard_text = ""
        for idx, (user_id, user_info) in enumerate(sorted_users, 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            leaderboard_text += f"{medal} <@{user_id}> - **Level {user_info['level']}** ({user_info['xp']} XP)\n"

        embed.add_field(name="Leaderboard", value=leaderboard_text, inline=False)

        await ctx.send(embed=embed)

    # DISABLED - /setxp command
    # @commands.hybrid_command(name='setxp', description='Set a user\'s XP (Admin only)')
    # @commands.has_permissions(administrator=True)
    async def set_xp_disabled(self, ctx, member: discord.Member, amount: int):
        user_data = self.db.get_user_level(ctx.guild.id, member.id)
        old_level = user_data.get('level', 1)

        user_data['xp'] = amount
        self.db.save()

        xp_needed = self.db.get_xp_for_level(old_level)
        while user_data['xp'] >= xp_needed:
            user_data['level'] += 1
            user_data['xp'] -= xp_needed
            xp_needed = self.db.get_xp_for_level(user_data['level'])

        self.db.save()

        embed = discord.Embed(
            title="✅ XP Updated",
            description=f"Set {member.mention}'s XP to **{amount}**",
            color=discord.Color.green()
        )

        await ctx.send(embed=embed, ephemeral=True)

    # DISABLED - /resetlevel command
    # @commands.hybrid_command(name='resetlevel', description='Reset a user\'s level (Admin only)')
    # @commands.has_permissions(administrator=True)
    async def reset_level_disabled(self, ctx, member: discord.Member):
        user_data = self.db.get_user_level(ctx.guild.id, member.id)
        user_data['level'] = 1
        user_data['xp'] = 0
        self.db.save()

        embed = discord.Embed(
            title="✅ Level Reset",
            description=f"Reset {member.mention}'s level to 1",
            color=discord.Color.green()
        )

        await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Leveling(bot))