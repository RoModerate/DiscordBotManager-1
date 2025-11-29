import discord
from discord.ext import commands
from database import Database
from datetime import datetime

class SuggestionsBugs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        suggestion_channel_id = self.db.get_config('suggestion_channel')
        bug_channel_id = self.db.get_config('bug_channel')
        
        if message.channel.id == suggestion_channel_id:
            await self.handle_suggestion(message)
        elif message.channel.id == bug_channel_id:
            await self.handle_bug_report(message)
    
    async def handle_suggestion(self, message):
        if len(message.content) < 10:
            await message.delete()
            try:
                await message.author.send("❌ Your suggestion was too short. Please provide more detail (at least 10 characters).")
            except:
                pass
            return
        
        last_hour_suggestions = [
            s for s in self.db.data.get('suggestions', {}).values()
            if s['user_id'] == message.author.id and 
            (datetime.utcnow() - datetime.fromisoformat(s['timestamp'])).total_seconds() < 3600
        ]
        
        for old_suggestion in last_hour_suggestions:
            if old_suggestion['content'].lower() == message.content.lower():
                await message.delete()
                try:
                    await message.author.send("❌ You already submitted this suggestion recently. Please wait before submitting duplicates.")
                except:
                    pass
                return
        
        suggestion_id = self.db.add_suggestion(
            user_id=message.author.id,
            content=message.content,
            channel_id=message.channel.id,
            message_id=message.id
        )
        
        self.db.increment_contribution(message.author.id, 'suggestions')
        
        await message.add_reaction('👍')
        await message.add_reaction('👎')
        
        try:
            await message.author.send(f"✅ Your suggestion has been recorded with ID: **{suggestion_id}**")
        except:
            pass
    
    async def handle_bug_report(self, message):
        if len(message.content) < 15:
            await message.delete()
            try:
                await message.author.send("❌ Your bug report was too short. Please provide detailed information (at least 15 characters).")
            except:
                pass
            return
        
        bug_id = self.db.add_bug_report(
            user_id=message.author.id,
            content=message.content,
            channel_id=message.channel.id,
            message_id=message.id
        )
        
        self.db.increment_contribution(message.author.id, 'bugs')
        
        embed = discord.Embed(
            title="🐛 Bug Report Received",
            description=message.content,
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
        embed.add_field(name="Report ID", value=f"`{bug_id}`", inline=True)
        embed.add_field(name="Status", value="Pending Review", inline=True)
        embed.set_footer(text=f"Reporter ID: {message.author.id}")
        
        await message.reply(embed=embed, mention_author=False)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        
        suggestion_channel_id = self.db.get_config('suggestion_channel')
        if payload.channel_id != suggestion_channel_id:
            return
        
        if str(payload.emoji) != '👍':
            return
        
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return
        
        try:
            message = await channel.fetch_message(payload.message_id)
        except:
            return
        
        thumbs_up_count = 0
        for reaction in message.reactions:
            if str(reaction.emoji) == '👍':
                thumbs_up_count = reaction.count
                break
        
        threshold = self.db.get_config('suggestion_forward_threshold') or 10
        
        if thumbs_up_count >= threshold:
            for suggestion_id, suggestion_data in self.db.data.get('suggestions', {}).items():
                if suggestion_data['message_id'] == message.id and not suggestion_data.get('forwarded'):
                    await self.forward_suggestion(message, suggestion_id, thumbs_up_count)
                    self.db.mark_suggestion_forwarded(suggestion_id)
                    break
    
    async def forward_suggestion(self, original_message, suggestion_id, reaction_count):
        forward_channel_id = self.db.get_config('suggestion_forward_channel')
        if not forward_channel_id:
            return
        
        forward_channel = self.bot.get_channel(forward_channel_id)
        if not forward_channel:
            return
        
        embed = discord.Embed(
            title="📝 Popular Suggestion",
            description=original_message.content,
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_author(
            name=str(original_message.author),
            icon_url=original_message.author.display_avatar.url
        )
        
        embed.add_field(name="👍 Reactions", value=str(reaction_count), inline=True)
        embed.add_field(name="Suggestion ID", value=f"`{suggestion_id}`", inline=True)
        embed.add_field(name="Original Message", value=f"[Jump to Message]({original_message.jump_url})", inline=False)
        
        embed.set_footer(text=f"Submitted by {original_message.author}")
        
        await forward_channel.send(embed=embed)
        
        await original_message.add_reaction('✅')
        
        try:
            await original_message.author.send(f"🎉 Your suggestion ({suggestion_id}) has been forwarded to the staff team for review!")
        except:
            pass

async def setup(bot):
    await bot.add_cog(SuggestionsBugs(bot))
