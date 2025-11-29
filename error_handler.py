import discord
from discord.ext import commands
import traceback
from datetime import datetime
from database import Database
from typing import Optional

class ErrorHandler:
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
    
    async def log_error(self, error: Exception, context: str = "Unknown", user_id: Optional[int] = None, guild_id: Optional[int] = None):
        error_log_channel_id = self.db.get_config('error_log_channel')
        if not error_log_channel_id:
            return
        
        error_log_channel = self.bot.get_channel(error_log_channel_id)
        if not error_log_channel:
            return
        
        error_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        
        embed = discord.Embed(
            title="❌ Bot Error Occurred",
            description=f"**Context:** {context}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Error Type",
            value=f"`{type(error).__name__}`",
            inline=True
        )
        
        embed.add_field(
            name="Error Message",
            value=f"`{str(error)[:1000]}`",
            inline=False
        )
        
        if user_id:
            embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
        
        if guild_id:
            embed.add_field(name="Guild ID", value=f"`{guild_id}`", inline=True)
        
        if len(error_trace) <= 1024:
            embed.add_field(
                name="Traceback",
                value=f"```python\n{error_trace}\n```",
                inline=False
            )
        else:
            embed.add_field(
                name="Traceback",
                value=f"```python\n{error_trace[:1000]}...\n```",
                inline=False
            )
            embed.set_footer(text="Full traceback truncated")
        
        try:
            await error_log_channel.send(embed=embed)
        except:
            pass
    
    async def send_error_message(self, ctx_or_interaction, error_message: str, ephemeral: bool = True):
        embed = discord.Embed(
            title="❌ Error",
            description=error_message,
            color=discord.Color.red()
        )
        
        if isinstance(ctx_or_interaction, discord.Interaction):
            if ctx_or_interaction.response.is_done():
                await ctx_or_interaction.followup.send(embed=embed, ephemeral=ephemeral)
            else:
                await ctx_or_interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        else:
            await ctx_or_interaction.send(embed=embed)
    
    async def send_success_message(self, ctx_or_interaction, success_message: str, ephemeral: bool = False):
        embed = discord.Embed(
            title="✅ Success",
            description=success_message,
            color=discord.Color.green()
        )
        
        if isinstance(ctx_or_interaction, discord.Interaction):
            if ctx_or_interaction.response.is_done():
                await ctx_or_interaction.followup.send(embed=embed, ephemeral=ephemeral)
            else:
                await ctx_or_interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        else:
            await ctx_or_interaction.send(embed=embed)
    
    async def handle_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            required_perms = ', '.join(error.missing_permissions)
            await self.send_error_message(
                ctx,
                f"You don't have the required permissions: **{required_perms}**"
            )
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await self.send_error_message(
                ctx,
                f"Missing required argument: **{error.param.name}**\nPlease check the command usage."
            )
        
        elif isinstance(error, commands.CommandNotFound):
            pass
        
        elif isinstance(error, commands.CommandOnCooldown):
            await self.send_error_message(
                ctx,
                f"This command is on cooldown. Try again in **{error.retry_after:.1f}** seconds."
            )
        
        elif isinstance(error, commands.BadArgument):
            await self.send_error_message(
                ctx,
                f"Invalid argument provided. Please check your input."
            )
        
        elif isinstance(error, commands.CheckFailure):
            await self.send_error_message(
                ctx,
                "You don't have permission to use this command."
            )
        
        else:
            await self.send_error_message(
                ctx,
                "An unexpected error occurred. The error has been logged."
            )
            
            await self.log_error(
                error,
                context=f"Command: {ctx.command.name if ctx.command else 'Unknown'}",
                user_id=ctx.author.id if ctx.author else None,
                guild_id=ctx.guild.id if ctx.guild else None
            )

async def setup_error_handler(bot):
    error_handler = ErrorHandler(bot)
    
    @bot.event
    async def on_command_error(ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        
        error = getattr(error, 'original', error)
        await error_handler.handle_command_error(ctx, error)
    
    return error_handler
