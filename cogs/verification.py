import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import aiohttp
from database import Database

class VerificationView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(VerifyButton())
        self.add_item(HelpButton())

class VerifyButton(Button):
    def __init__(self):
        super().__init__(
            label="Verify",
            style=discord.ButtonStyle.gray,
            custom_id="verify_button"
        )

    async def callback(self, interaction: discord.Interaction):
        db = Database()
        verified_role_id = db.get_config('verified_role') or 1423669554441355284
        
        verified_role = interaction.guild.get_role(verified_role_id)
        if not verified_role:
            await interaction.response.send_message("❌ Verified role not found. Contact an administrator.", ephemeral=True)
            return

        if verified_role in interaction.user.roles:
            await interaction.response.send_message("✅ You are already verified.", ephemeral=True)
            return
        
        modal = RobloxVerificationModal()
        await interaction.response.send_modal(modal)

class RobloxVerificationModal(Modal):
    def __init__(self):
        super().__init__(title="Roblox Verification")
        
        self.roblox_username = TextInput(
            label="Enter your Roblox Username",
            placeholder="YourRobloxUsername",
            required=True,
            max_length=50
        )
        self.add_item(self.roblox_username)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        db = Database()
        username = self.roblox_username.value.strip()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://users.roblox.com/v1/usernames/users",
                    json={"usernames": [username]}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('data') and len(data['data']) > 0:
                            roblox_id = data['data'][0]['id']
                            roblox_name = data['data'][0]['name']
                            
                            async with session.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={roblox_id}&size=150x150&format=Png") as avatar_resp:
                                avatar_url = None
                                if avatar_resp.status == 200:
                                    avatar_data = await avatar_resp.json()
                                    if avatar_data.get('data'):
                                        avatar_url = avatar_data['data'][0]['imageUrl']
                            
                            db.set_verification_data(interaction.user.id, roblox_id, roblox_name)
                            
                            verified_role_id = db.get_config('verified_role') or 1423669554441355284
                            verified_role = interaction.guild.get_role(verified_role_id)
                            
                            if verified_role:
                                await interaction.user.add_roles(verified_role, reason="User verified with Roblox")
                            
                            try:
                                dm_embed = discord.Embed(
                                    title="Verification Complete",
                                    description=f"> **Verification Complete.** You have successfully verified in **{interaction.guild.name}**",
                                    color=discord.Color.green(),
                                    timestamp=discord.utils.utcnow()
                                )
                                
                                if avatar_url:
                                    dm_embed.set_thumbnail(url=avatar_url)
                                
                                dm_embed.add_field(
                                    name="Roblox Account",
                                    value=f"**Username:** {roblox_name}\n**Profile:** [View Profile](https://www.roblox.com/users/{roblox_id}/profile)",
                                    inline=False
                                )
                                
                                await interaction.user.send(embed=dm_embed)
                            except:
                                pass
                            
                            log_channel_id = db.get_config('log_channel') or 1411710143598690404
                            log_channel = interaction.guild.get_channel(log_channel_id)
                            if log_channel:
                                log_embed = discord.Embed(
                                    title="User Verified",
                                    description=f"> {interaction.user.mention} has been verified",
                                    color=discord.Color.green(),
                                    timestamp=discord.utils.utcnow()
                                )
                                log_embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
                                log_embed.add_field(name="Roblox", value=f"[{roblox_name}](https://www.roblox.com/users/{roblox_id}/profile)", inline=True)
                                
                                if avatar_url:
                                    log_embed.set_thumbnail(url=avatar_url)
                                else:
                                    log_embed.set_thumbnail(url=interaction.user.display_avatar.url)
                                
                                await log_channel.send(embed=log_embed)
                            
                            await interaction.followup.send(f"✅ Successfully verified as **{roblox_name}**!", ephemeral=True)
                        else:
                            await interaction.followup.send("❌ Roblox username not found. Please check your username and try again.", ephemeral=True)
                    else:
                        await interaction.followup.send("❌ Failed to verify with Roblox. Please try again later.", ephemeral=True)
        except Exception as e:
            print(f"Verification error: {e}")
            await interaction.followup.send("❌ An error occurred during verification. Please contact an administrator.", ephemeral=True)

class HelpButton(Button):
    def __init__(self):
        super().__init__(
            label="Need Help?",
            style=discord.ButtonStyle.primary,
            custom_id="help_button"
        )

    async def callback(self, interaction: discord.Interaction):
        db = Database()
        help_channel_id = db.get_config('help_channel') or 1389999965979283608
        await interaction.response.send_message(
            f"For assistance, please visit <#{help_channel_id}>",
            ephemeral=True
        )

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.hybrid_command(name='setupverify', description='Setup the verification panel')
    @commands.has_permissions(administrator=True)
    async def setupverify(self, ctx):
        """Setup verification panel"""
        embed = discord.Embed(
            title="Verification",
            description="Click the **Verify** button below to verify yourself in the server.",
            color=0x5865F2
        )
        
        view = VerificationView()
        await ctx.send(embed=embed, view=view)
        try:
            await ctx.message.delete()
        except:
            pass

async def setup(bot):
    await bot.add_cog(Verification(bot))
