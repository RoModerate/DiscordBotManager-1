import discord
from discord.ext import commands
from database import Database
from datetime import datetime, timedelta
from collections import defaultdict

class StaffTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.message_tracker = defaultdict(int)
        self.mod_action_tracker = defaultdict(int)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        mod_roles = [
            1383270277147787294,
            1409873374288674816,
            1383175157186564286,
            1409874361615388746,
            1388254732543590492,
            1409874452866400346,
            1411739899639496704,
            1383270529430978590
        ]
        
        if any(role.id in mod_roles for role in message.author.roles):
            self.message_tracker[message.author.id] += 1
    
    # DISABLED - /note command
    # @commands.hybrid_command(name='note', description='Add a note about a user (Staff only)')
    # @commands.has_permissions(moderate_members=True)
    async def add_note_disabled(self, ctx, member: discord.Member, *, note: str):
        self.db.add_staff_note(member.id, ctx.author.id, note)
        
        embed = discord.Embed(
            title="✅ Note Added",
            description=f"Note added for {member.mention}",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Note", value=note, inline=False)
        embed.set_footer(text=f"Added by {ctx.author}")
        
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='notes', description='View notes about a user (Staff only)')
    @commands.has_permissions(moderate_members=True)
    async def view_notes(self, ctx, member: discord.Member):
        notes = self.db.get_staff_notes(member.id)
        
        if not notes:
            await ctx.send(f"No notes found for {member.mention}", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📝 Notes for {member.display_name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        for idx, note in enumerate(notes[-10:], 1):
            staff_user = self.bot.get_user(note['staff_id'])
            staff_name = str(staff_user) if staff_user else f"ID: {note['staff_id']}"
            timestamp = datetime.fromisoformat(note['timestamp']).strftime("%b %d, %Y %H:%M")
            
            embed.add_field(
                name=f"Note #{idx} - {staff_name}",
                value=f"{note['note']}\n*{timestamp}*",
                inline=False
            )
        
        if len(notes) > 10:
            embed.set_footer(text=f"Showing last 10 of {len(notes)} notes")
        
        await ctx.send(embed=embed, ephemeral=True)
    
    # DISABLED - /case command
    # @commands.hybrid_command(name='case', description='View details of a moderation case')
    # @commands.has_permissions(moderate_members=True)
    async def view_case_disabled(self, ctx, case_id: int):
        case = self.db.get_mod_case(case_id)
        
        if not case:
            await ctx.send(f"❌ Case #{case_id} not found", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📋 Case #{case_id}",
            color=discord.Color.blue(),
            timestamp=datetime.fromisoformat(case['timestamp'])
        )
        
        user = self.bot.get_user(case['user_id'])
        moderator = self.bot.get_user(case['moderator_id'])
        
        embed.add_field(name="User", value=user.mention if user else f"ID: {case['user_id']}", inline=True)
        embed.add_field(name="Moderator", value=moderator.mention if moderator else f"ID: {case['moderator_id']}", inline=True)
        embed.add_field(name="Action", value=case['action'].title(), inline=True)
        
        embed.add_field(name="Reason", value=case['reason'], inline=False)
        
        embed.set_footer(text=f"Case ID: {case_id}")
        
        await ctx.send(embed=embed, ephemeral=True)
    
    # DISABLED - /editcase command
    # @commands.hybrid_command(name='editcase', description='Edit the reason for a moderation case')
    # @commands.has_permissions(moderate_members=True)
    async def edit_case_disabled(self, ctx, case_id: int, *, new_reason: str):
        case = self.db.get_mod_case(case_id)
        
        if not case:
            await ctx.send(f"❌ Case #{case_id} not found", ephemeral=True)
            return
        
        if case['moderator_id'] != ctx.author.id and not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You can only edit cases you created (unless you're an administrator)", ephemeral=True)
            return
        
        success = self.db.edit_mod_case_reason(case_id, new_reason)
        
        if success:
            embed = discord.Embed(
                title="✅ Case Updated",
                description=f"Case #{case_id} reason has been updated",
                color=discord.Color.green()
            )
            
            embed.add_field(name="New Reason", value=new_reason, inline=False)
            
            await ctx.send(embed=embed, ephemeral=True)
        else:
            await ctx.send(f"❌ Failed to update case #{case_id}", ephemeral=True)
    
    @commands.hybrid_command(name='staffactivity', description='View staff activity metrics')
    @commands.has_permissions(administrator=True)
    async def staff_activity(self, ctx, period: str = "week"):
        if period not in ["today", "week", "month", "all"]:
            await ctx.send("❌ Invalid period. Use: today, week, month, or all", ephemeral=True)
            return
        
        cutoff_time = datetime.utcnow()
        if period == "today":
            cutoff_time -= timedelta(days=1)
        elif period == "week":
            cutoff_time -= timedelta(weeks=1)
        elif period == "month":
            cutoff_time -= timedelta(days=30)
        else:
            cutoff_time = datetime(2020, 1, 1)
        
        all_cases = self.db.data.get('moderation_cases', {})
        
        staff_stats = defaultdict(lambda: {
            'warns': 0,
            'timeouts': 0,
            'kicks': 0,
            'bans': 0,
            'total': 0
        })
        
        for case in all_cases.values():
            case_time = datetime.fromisoformat(case['timestamp'])
            if case_time >= cutoff_time:
                moderator_id = case['moderator_id']
                action = case['action']
                
                staff_stats[moderator_id]['total'] += 1
                
                if 'warn' in action.lower():
                    staff_stats[moderator_id]['warns'] += 1
                elif 'timeout' in action.lower() or 'mute' in action.lower():
                    staff_stats[moderator_id]['timeouts'] += 1
                elif 'kick' in action.lower():
                    staff_stats[moderator_id]['kicks'] += 1
                elif 'ban' in action.lower():
                    staff_stats[moderator_id]['bans'] += 1
        
        if not staff_stats:
            await ctx.send(f"No staff activity found for period: {period}", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📊 Staff Activity - {period.title()}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        sorted_staff = sorted(staff_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
        
        activity_text = ""
        for staff_id, stats in sorted_staff:
            staff_member = self.bot.get_user(staff_id)
            staff_name = str(staff_member) if staff_member else f"ID: {staff_id}"
            
            activity_text += f"**{staff_name}**\n"
            activity_text += f"└ Total: {stats['total']} | Warns: {stats['warns']} | Timeouts: {stats['timeouts']} | Kicks: {stats['kicks']} | Bans: {stats['bans']}\n\n"
        
        embed.description = activity_text if activity_text else "No activity"
        
        embed.set_footer(text=f"Showing top 10 staff members")
        
        await ctx.send(embed=embed, ephemeral=True)
    
    
    # DISABLED - /viewwarnings command
    # @commands.hybrid_command(name='viewwarnings', description='View warnings for a user')
    # @commands.has_permissions(moderate_members=True)
    async def view_warnings_disabled(self, ctx, member: discord.Member):
        from cogs.moderation import Moderation
        
        mod_cog = self.bot.get_cog('Moderation')
        if not mod_cog:
            await ctx.send("❌ Moderation system not loaded", ephemeral=True)
            return
        
        warning_count = mod_cog.get_user_warnings(ctx.guild.id, member.id)
        
        embed = discord.Embed(
            title=f"⚠️ Warnings for {member.display_name}",
            color=discord.Color.orange()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Total Warnings", value=f"**{warning_count}** / 8", inline=True)
        
        if warning_count == 0:
            embed.add_field(name="Status", value="✅ Clean Record", inline=True)
        elif warning_count < 3:
            embed.add_field(name="Status", value="⚠️ Minor Warnings", inline=True)
        elif warning_count < 6:
            embed.add_field(name="Status", value="⚠️ Multiple Warnings", inline=True)
        else:
            embed.add_field(name="Status", value="🚨 Severe - Close to Ban", inline=True)
        
        embed.set_footer(text=f"User ID: {member.id}")
        
        await ctx.send(embed=embed, ephemeral=True)
    
    # DISABLED - /resetwarnings command
    # @commands.hybrid_command(name='resetwarnings', description='Clear all warnings for a user')
    # @commands.has_permissions(administrator=True)
    async def clear_warnings_disabled(self, ctx, member: discord.Member):
        from cogs.moderation import Moderation
        
        mod_cog = self.bot.get_cog('Moderation')
        if not mod_cog:
            await ctx.send("❌ Moderation system not loaded", ephemeral=True)
            return
        
        guild_key = str(ctx.guild.id)
        user_key = str(member.id)
        
        if guild_key in mod_cog.warnings and user_key in mod_cog.warnings[guild_key]:
            mod_cog.warnings[guild_key][user_key] = 0
            mod_cog.save_warnings()
            
            embed = discord.Embed(
                title="✅ Warnings Cleared",
                description=f"All warnings cleared for {member.mention}",
                color=discord.Color.green()
            )
            
            await ctx.send(embed=embed, ephemeral=True)
        else:
            await ctx.send(f"{member.mention} has no warnings to clear", ephemeral=True)
    
    # DISABLED - /shift command
    # @commands.hybrid_command(name='shift', description='Manage your shift (start/end)')
    # @commands.has_permissions(moderate_members=True)
    async def shift_disabled(self, ctx, action: str, duration: str = ""):
        """Start or end a moderation shift
        
        Examples:
        !shift start 2h
        !shift end
        """
        if action.lower() == 'start':
            if not duration:
                await ctx.send("Please provide a duration (e.g., 2h, 30m, 1h30m)", ephemeral=True)
                return
            
            if 'active_shifts' not in self.db.data:
                self.db.data['active_shifts'] = {}
            
            user_key = str(ctx.author.id)
            if user_key in self.db.data['active_shifts']:
                await ctx.send("You already have an active shift. Use `!shift end` first.", ephemeral=True)
                return
            
            start_time = datetime.utcnow()
            self.db.data['active_shifts'][user_key] = {
                'start_time': start_time.isoformat(),
                'duration': duration,
                'user_id': ctx.author.id,
                'username': str(ctx.author)
            }
            self.db.save()
            
            shift_start_channel_id = 1436895113820373144
            shift_start_channel = ctx.guild.get_channel(shift_start_channel_id)
            
            if shift_start_channel:
                embed = discord.Embed(
                    title="🟢 Shift Started",
                    color=discord.Color.green(),
                    timestamp=start_time
                )
                embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                embed.add_field(name="Started", value=start_time.strftime('%I:%M %p'), inline=True)
                embed.add_field(name="Expected Duration", value=duration, inline=True)
                embed.add_field(name="Status", value="🟢 Active", inline=False)
                embed.set_footer(text=f"Moderator ID: {ctx.author.id}")
                await shift_start_channel.send(embed=embed)
            
            await ctx.send(f"✅ Shift started! Duration: {duration}", ephemeral=True)
        
        elif action.lower() == 'end':
            if 'active_shifts' not in self.db.data:
                self.db.data['active_shifts'] = {}
            
            user_key = str(ctx.author.id)
            if user_key not in self.db.data['active_shifts']:
                await ctx.send("You don't have an active shift.", ephemeral=True)
                return
            
            shift_data = self.db.data['active_shifts'][user_key]
            start_time = datetime.fromisoformat(shift_data['start_time'])
            end_time = datetime.utcnow()
            time_elapsed = end_time - start_time
            
            hours = int(time_elapsed.total_seconds() // 3600)
            minutes = int((time_elapsed.total_seconds() % 3600) // 60)
            duration_str = f"{hours} Hours" if hours > 0 else ""
            if minutes > 0:
                duration_str += f" {minutes} Minutes" if duration_str else f"{minutes} Minutes"
            
            shift_end_channel_id = 1436895129615995060
            shift_end_channel = ctx.guild.get_channel(shift_end_channel_id)
            
            if shift_end_channel:
                embed = discord.Embed(
                    title="🔴 Shift Ended",
                    color=discord.Color.red(),
                    timestamp=end_time
                )
                embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
                embed.add_field(name="Started", value=start_time.strftime('%I:%M %p'), inline=True)
                embed.add_field(name="Ended", value=end_time.strftime('%I:%M %p'), inline=True)
                embed.add_field(name="Total Duration", value=duration_str, inline=False)
                embed.add_field(name="Status", value="✅ Completed Successfully", inline=False)
                embed.set_footer(text=f"Moderator ID: {ctx.author.id}")
                await shift_end_channel.send(embed=embed)
            
            del self.db.data['active_shifts'][user_key]
            self.db.save()
            
            await ctx.send(f"✅ Shift ended! Total duration: {duration_str}", ephemeral=True)
        
        else:
            await ctx.send("Invalid action. Use 'start' or 'end'.", ephemeral=True)
    
    @commands.hybrid_command(name='promotion', description='Promote a staff member to a higher rank')
    @commands.has_permissions(manage_roles=True)
    async def promotion(self, ctx, member: discord.Member, *, new_rank: str):
        """Promote a staff member
        
        Example:
        !promotion @User Moderator
        """
        promotion_channel_id = 1436895147206901810
        promotion_channel = ctx.guild.get_channel(promotion_channel_id)
        
        now = datetime.utcnow()
        
        if promotion_channel:
            embed = discord.Embed(
                title="🎉 Staff Promotion",
                description=f"{member.mention} has been promoted!",
                color=discord.Color.gold(),
                timestamp=now
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Member", value=member.mention, inline=True)
            embed.add_field(name="New Rank", value=new_rank, inline=True)
            embed.add_field(name="Promoted By", value=ctx.author.mention, inline=True)
            embed.add_field(name="Date", value=now.strftime('%B %d, %Y'), inline=False)
            embed.set_footer(text=f"Member ID: {member.id}")
            await promotion_channel.send(embed=embed)
        
        await ctx.send(f"✅ Promotion logged for {member.mention} to **{new_rank}**", ephemeral=True)
    
    @commands.hybrid_command(name='infraction', description='Log a staff infraction')
    @commands.has_permissions(manage_roles=True)
    async def infraction(self, ctx, member: discord.Member, *, reason: str):
        """Log a staff infraction
        
        Example:
        !infraction @User Misuse of mod commands
        """
        infraction_channel_id = 1436895168367169637
        infraction_channel = ctx.guild.get_channel(infraction_channel_id)
        
        now = datetime.utcnow()
        
        if infraction_channel:
            embed = discord.Embed(
                title="⚠️ Staff Infraction Logged",
                description=f"Infraction issued to {member.mention}",
                color=discord.Color.orange(),
                timestamp=now
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Staff Member", value=member.mention, inline=True)
            embed.add_field(name="Issued By", value=ctx.author.mention, inline=True)
            embed.add_field(name="Date", value=now.strftime('%B %d, %Y'), inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Member ID: {member.id}")
            await infraction_channel.send(embed=embed)
        
        await ctx.send(f"✅ Infraction logged for {member.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(StaffTools(bot))
