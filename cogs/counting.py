import discord
from discord.ext import commands
from database import Database
from datetime import datetime, timedelta

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counting_channel_id = 1431428103674138634
        self.cooldown_seconds = 5
        self.max_mistakes = 5
        self.lockout_duration = 3600
        self.celebration_number = 5000
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.channel.id != self.counting_channel_id:
            return
        
        db = Database()
        
        lockout_data = db.get_counting_lockout(message.author.id)
        if lockout_data:
            lockout_until = datetime.fromisoformat(lockout_data['lockout_until'])
            if datetime.utcnow() < lockout_until:
                await message.delete()
                remaining = (lockout_until - datetime.utcnow()).total_seconds()
                remaining_minutes = int(remaining / 60)
                try:
                    await message.author.send(f"🔒 You are locked from counting for {remaining_minutes} more minutes due to {self.max_mistakes} mistakes.")
                except:
                    pass
                return
            else:
                db.clear_counting_lockout(message.author.id)
        
        cooldown_data = db.get_counting_cooldown(message.author.id)
        if cooldown_data:
            cooldown_until = datetime.fromisoformat(cooldown_data['cooldown_until'])
            if datetime.utcnow() < cooldown_until:
                await message.delete()
                remaining_seconds = int((cooldown_until - datetime.utcnow()).total_seconds())
                try:
                    await message.channel.send(
                        f"{message.author.mention} ⏱️ Please wait **{remaining_seconds}** seconds before typing again.",
                        delete_after=3
                    )
                except:
                    pass
                return
        
        content = message.content.strip()
        if not content.isdigit():
            await message.delete()
            try:
                await message.channel.send(
                    f"{message.author.mention} ❌ Numbers only!",
                    delete_after=3
                )
            except:
                pass
            return
        
        number = int(content)
        
        counting_state = db.get_counting_state(message.guild.id)
        last_number = counting_state.get('last_number', 0)
        last_user_id = counting_state.get('last_user_id')
        
        if last_user_id == message.author.id:
            await message.delete()
            mistakes = db.increment_counting_mistakes(message.author.id)
            
            remaining_mistakes = self.max_mistakes - mistakes
            
            try:
                await message.channel.send(
                    f"{message.author.mention} ❌ You cannot count twice in a row! **{remaining_mistakes}** mistakes remaining before lockout.",
                    delete_after=5
                )
            except:
                pass
            
            if mistakes >= self.max_mistakes:
                lockout_until = datetime.utcnow() + timedelta(seconds=self.lockout_duration)
                db.set_counting_lockout(message.author.id, lockout_until.isoformat())
                db.reset_counting_mistakes(message.author.id)
                try:
                    await message.author.send("🔒 You have been locked from counting for **1 hour** due to 5 mistakes. Take a break!")
                except:
                    pass
            
            return
        
        expected = last_number + 1
        
        if number != expected:
            await message.delete()
            mistakes = db.increment_counting_mistakes(message.author.id)
            
            remaining_mistakes = self.max_mistakes - mistakes
            
            try:
                await message.channel.send(
                    f"{message.author.mention} ❌ Wrong number! Expected **{expected}**. **{remaining_mistakes}** mistakes remaining.",
                    delete_after=5
                )
            except:
                pass
            
            if mistakes >= self.max_mistakes:
                lockout_until = datetime.utcnow() + timedelta(seconds=self.lockout_duration)
                db.set_counting_lockout(message.author.id, lockout_until.isoformat())
                db.reset_counting_mistakes(message.author.id)
                try:
                    await message.author.send("🔒 You have been locked from counting for **1 hour** due to 5 mistakes. Take a break!")
                except:
                    pass
            
            return
        
        await message.add_reaction("✅")
        
        db.update_counting_state(message.guild.id, number, message.author.id)
        db.increment_count_contribution(message.author.id)
        
        cooldown_until = datetime.utcnow() + timedelta(seconds=self.cooldown_seconds)
        db.set_counting_cooldown(message.author.id, cooldown_until.isoformat())
        
        if number == self.celebration_number:
            await self.celebrate_milestone(message.channel, db)
            db.update_counting_state(message.guild.id, 0, None)
            db.reset_counting_contributions()
    
    async def celebrate_milestone(self, channel, db):
        leaderboard = db.get_counting_leaderboard(limit=10)
        
        embed = discord.Embed(
            title="🎉 CONGRATULATIONS! 🎉",
            description=f"The server has reached **{self.celebration_number}**!",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        
        if leaderboard:
            top_3_text = ""
            for idx, (user_id, count) in enumerate(leaderboard[:3], 1):
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉"
                top_3_text += f"{medal} <@{user_id}> - **{count}** counts\n"
            
            embed.add_field(name="🏆 Top Contributors", value=top_3_text, inline=False)
            
            all_contributors_text = ""
            for idx, (user_id, count) in enumerate(leaderboard[3:], 4):
                all_contributors_text += f"{idx}. <@{user_id}> - **{count}** counts\n"
            
            if all_contributors_text:
                embed.add_field(name="Other Top Contributors", value=all_contributors_text, inline=False)
        
        embed.set_footer(text="Starting over from 1... Good luck!")
        
        await channel.send(embed=embed)
        
        await channel.send(f"🎯 Let's start counting again! Next number: **1**")
    
    @commands.hybrid_command(name='resetmistakes', description='Reset a user\'s counting mistakes (Moderator+)')
    @commands.has_permissions(moderate_members=True)
    async def reset_mistakes_cmd(self, ctx, member: discord.Member):
        db = Database()
        db.reset_counting_mistakes(member.id)
        db.clear_counting_lockout(member.id)
        
        embed = discord.Embed(
            title="✅ Mistakes Reset",
            description=f"Reset counting mistakes and lockout for {member.mention}",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed, ephemeral=True)

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.value = None
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.defer()
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.defer()

async def setup(bot):
    await bot.add_cog(Counting(bot))
