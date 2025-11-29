import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from database import Database
from datetime import datetime

class ConfigModal(Modal):
    def __init__(self, config_type: str, db: Database):
        super().__init__(title=f"Configure {config_type}")
        self.config_type = config_type
        self.db = db
        
        if config_type == "Welcome Channel":
            self.channel_id = TextInput(
                label="Welcome Channel ID",
                placeholder="Enter channel ID (e.g., 1234567890)",
                required=False
            )
            self.add_item(self.channel_id)
        
        elif config_type == "Muted Role":
            self.role_id = TextInput(
                label="Muted Role ID",
                placeholder="Enter role ID (e.g., 1234567890)",
                required=False
            )
            self.add_item(self.role_id)
        
        elif config_type == "Staff Ping":
            self.staff_role = TextInput(
                label="Staff Role ID",
                placeholder="Enter staff role ID",
                required=False
            )
            self.staff_user = TextInput(
                label="Staff User ID (optional)",
                placeholder="Enter staff user ID",
                required=False
            )
            self.add_item(self.staff_role)
            self.add_item(self.staff_user)
        
        elif config_type == "AI Settings":
            self.ai_enabled = TextInput(
                label="AI Enabled (true/false)",
                placeholder="true or false",
                max_length=5
            )
            self.ai_endpoint = TextInput(
                label="AI Endpoint URL",
                placeholder="https://api.example.com/v1/chat/completions",
                required=False
            )
            self.add_item(self.ai_enabled)
            self.add_item(self.ai_endpoint)
        
        elif config_type == "Ticket Categories":
            self.support_cat = TextInput(
                label="Support Ticket Category ID",
                placeholder="1436498409153626213",
                required=False
            )
            self.cc_cat = TextInput(
                label="Request CC Category ID",
                placeholder="1436498445216256031",
                required=False
            )
            self.report_cat = TextInput(
                label="Report Player Category ID",
                placeholder="1436498495153635512",
                required=False
            )
            self.appeal_cat = TextInput(
                label="Warning Appeal Category ID",
                placeholder="1436498528544227428",
                required=False
            )
            self.add_item(self.support_cat)
            self.add_item(self.cc_cat)
            self.add_item(self.report_cat)
            self.add_item(self.appeal_cat)
    
    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        errors = []
        
        try:
            if self.config_type == "Welcome Channel":
                if self.channel_id.value:
                    channel_id = int(self.channel_id.value)
                    channel = guild.get_channel(channel_id)
                    if channel:
                        self.db.set_config('welcome_channel', channel_id)
                        await interaction.response.send_message(f"✅ Welcome channel set to {channel.mention}", ephemeral=True)
                    else:
                        errors.append(f"Channel ID {channel_id} not found in this server.")
                else:
                    self.db.set_config('welcome_channel', None)
                    await interaction.response.send_message("✅ Welcome channel cleared.", ephemeral=True)
            
            elif self.config_type == "Muted Role":
                if self.role_id.value:
                    role_id = int(self.role_id.value)
                    role = guild.get_role(role_id)
                    if role:
                        self.db.set_config('muted_role', role_id)
                        await interaction.response.send_message(f"✅ Muted role set to {role.mention}", ephemeral=True)
                    else:
                        errors.append(f"Role ID {role_id} not found in this server.")
                else:
                    self.db.set_config('muted_role', None)
                    await interaction.response.send_message("✅ Muted role cleared.", ephemeral=True)
            
            elif self.config_type == "Staff Ping":
                if self.staff_role.value:
                    role_id = int(self.staff_role.value)
                    role = guild.get_role(role_id)
                    if role:
                        self.db.set_config('staff_ping_role', role_id)
                    else:
                        errors.append(f"Staff role ID {role_id} not found.")
                
                if self.staff_user.value:
                    user_id = int(self.staff_user.value)
                    self.db.set_config('staff_ping_user', user_id)
                
                if not errors:
                    await interaction.response.send_message("✅ Staff ping settings updated.", ephemeral=True)
            
            elif self.config_type == "AI Settings":
                ai_enabled = self.ai_enabled.value.lower() == 'true'
                self.db.set_config('ai_enabled', ai_enabled)
                
                if self.ai_endpoint.value:
                    self.db.set_config('ai_endpoint', self.ai_endpoint.value)
                
                await interaction.response.send_message(f"✅ AI settings updated. AI is now {'enabled' if ai_enabled else 'disabled'}.", ephemeral=True)
            
            elif self.config_type == "Ticket Categories":
                categories = self.db.get_config('ticket_categories') or {}
                
                if self.support_cat.value:
                    cat_id = int(self.support_cat.value)
                    cat = guild.get_channel(cat_id)
                    if cat and isinstance(cat, discord.CategoryChannel):
                        categories['support'] = cat_id
                    else:
                        errors.append(f"Support category {cat_id} not found or not a category.")
                
                if self.cc_cat.value:
                    cat_id = int(self.cc_cat.value)
                    cat = guild.get_channel(cat_id)
                    if cat and isinstance(cat, discord.CategoryChannel):
                        categories['cc'] = cat_id
                    else:
                        errors.append(f"CC category {cat_id} not found or not a category.")
                
                if self.report_cat.value:
                    cat_id = int(self.report_cat.value)
                    cat = guild.get_channel(cat_id)
                    if cat and isinstance(cat, discord.CategoryChannel):
                        categories['report'] = cat_id
                    else:
                        errors.append(f"Report category {cat_id} not found or not a category.")
                
                if self.appeal_cat.value:
                    cat_id = int(self.appeal_cat.value)
                    cat = guild.get_channel(cat_id)
                    if cat and isinstance(cat, discord.CategoryChannel):
                        categories['appeal'] = cat_id
                    else:
                        errors.append(f"Appeal category {cat_id} not found or not a category.")
                
                if not errors:
                    self.db.set_config('ticket_categories', categories)
                    await interaction.response.send_message("✅ Ticket categories updated.", ephemeral=True)
            
            if errors:
                error_msg = "\n".join([f"❌ {err}" for err in errors])
                await interaction.response.send_message(f"**Errors:**\n{error_msg}", ephemeral=True)
        
        except ValueError:
            await interaction.response.send_message("❌ Invalid input. Please enter valid IDs (numbers only).", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class ConfigPage(View):
    def __init__(self, page: int, db: Database):
        super().__init__(timeout=None)
        self.page = page
        self.db = db
        self.total_pages = 3
        
        if page > 1:
            self.add_item(PreviousButton())
        if page < self.total_pages:
            self.add_item(NextButton())
        self.add_item(ReloadButton())
        
        if page == 1:
            self.add_item(WelcomeChannelButton(db))
            self.add_item(MutedRoleButton(db))
        elif page == 2:
            self.add_item(StaffPingButton(db))
            self.add_item(AISettingsButton(db))
        elif page == 3:
            self.add_item(TicketCategoriesButton(db))

class PreviousButton(Button):
    def __init__(self):
        super().__init__(label="Previous", style=discord.ButtonStyle.primary, emoji="◀️")
    
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        new_page = max(1, view.page - 1)
        embed = get_config_embed(new_page, view.db, interaction.guild)
        new_view = ConfigPage(new_page, view.db)
        await interaction.response.edit_message(embed=embed, view=new_view)

class NextButton(Button):
    def __init__(self):
        super().__init__(label="Next", style=discord.ButtonStyle.primary, emoji="▶️")
    
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        new_page = min(view.total_pages, view.page + 1)
        embed = get_config_embed(new_page, view.db, interaction.guild)
        new_view = ConfigPage(new_page, view.db)
        await interaction.response.edit_message(embed=embed, view=new_view)

class ReloadButton(Button):
    def __init__(self):
        super().__init__(label="Reload", style=discord.ButtonStyle.secondary, emoji="🔄")
    
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        embed = get_config_embed(view.page, view.db, interaction.guild)
        await interaction.response.edit_message(embed=embed)

class WelcomeChannelButton(Button):
    def __init__(self, db):
        super().__init__(label="Set Welcome Channel", style=discord.ButtonStyle.success)
        self.db = db
    
    async def callback(self, interaction: discord.Interaction):
        modal = ConfigModal("Welcome Channel", self.db)
        await interaction.response.send_modal(modal)

class MutedRoleButton(Button):
    def __init__(self, db):
        super().__init__(label="Set Muted Role", style=discord.ButtonStyle.success)
        self.db = db
    
    async def callback(self, interaction: discord.Interaction):
        modal = ConfigModal("Muted Role", self.db)
        await interaction.response.send_modal(modal)

class StaffPingButton(Button):
    def __init__(self, db):
        super().__init__(label="Set Staff Ping", style=discord.ButtonStyle.success)
        self.db = db
    
    async def callback(self, interaction: discord.Interaction):
        modal = ConfigModal("Staff Ping", self.db)
        await interaction.response.send_modal(modal)

class AISettingsButton(Button):
    def __init__(self, db):
        super().__init__(label="AI Settings", style=discord.ButtonStyle.success)
        self.db = db
    
    async def callback(self, interaction: discord.Interaction):
        modal = ConfigModal("AI Settings", self.db)
        await interaction.response.send_modal(modal)

class TicketCategoriesButton(Button):
    def __init__(self, db):
        super().__init__(label="Ticket Categories", style=discord.ButtonStyle.success)
        self.db = db
    
    async def callback(self, interaction: discord.Interaction):
        modal = ConfigModal("Ticket Categories", self.db)
        await interaction.response.send_modal(modal)

def get_config_embed(page: int, db: Database, guild):
    embed = discord.Embed(
        title=f"⚙️ Server Configuration - Page {page}/3",
        color=0x5865F2,
        timestamp=datetime.utcnow()
    )
    
    if page == 1:
        welcome_channel_id = db.get_config('welcome_channel')
        welcome_channel = guild.get_channel(welcome_channel_id) if welcome_channel_id else None
        
        muted_role_id = db.get_config('muted_role')
        muted_role = guild.get_role(muted_role_id) if muted_role_id else None
        
        embed.add_field(
            name="👋 Welcome Channel",
            value=welcome_channel.mention if welcome_channel else "Not set",
            inline=False
        )
        embed.add_field(
            name="🔇 Muted Role (for AFK)",
            value=muted_role.mention if muted_role else "Not set",
            inline=False
        )
    
    elif page == 2:
        staff_role_id = db.get_config('staff_ping_role')
        staff_role = guild.get_role(staff_role_id) if staff_role_id else None
        
        staff_user_id = db.get_config('staff_ping_user')
        
        ai_enabled = db.get_config('ai_enabled')
        ai_endpoint = db.get_config('ai_endpoint')
        
        embed.add_field(
            name="👮 Staff Ping Role",
            value=staff_role.mention if staff_role else "Not set",
            inline=False
        )
        embed.add_field(
            name="👤 Staff Ping User",
            value=f"<@{staff_user_id}>" if staff_user_id else "Not set",
            inline=False
        )
        embed.add_field(
            name="🤖 AI Settings",
            value=f"**Enabled:** {ai_enabled}\n**Endpoint:** {ai_endpoint or 'Not set'}",
            inline=False
        )
    
    elif page == 3:
        categories = db.get_config('ticket_categories') or {}
        
        support_cat = guild.get_channel(categories.get('support', 0))
        cc_cat = guild.get_channel(categories.get('cc', 0))
        report_cat = guild.get_channel(categories.get('report', 0))
        appeal_cat = guild.get_channel(categories.get('appeal', 0))
        
        transcript_channel_id = db.get_config('transcript_channel')
        transcript_channel = guild.get_channel(transcript_channel_id) if transcript_channel_id else None
        
        embed.add_field(
            name="🎫 Ticket Categories",
            value=f"**Support:** {support_cat.name if support_cat else 'Not set'}\n"
                  f"**Request CC:** {cc_cat.name if cc_cat else 'Not set'}\n"
                  f"**Report:** {report_cat.name if report_cat else 'Not set'}\n"
                  f"**Appeal:** {appeal_cat.name if appeal_cat else 'Not set'}",
            inline=False
        )
        embed.add_field(
            name="📝 Transcript Channel",
            value=transcript_channel.mention if transcript_channel else "Not set",
            inline=False
        )
    
    embed.set_footer(text="Use the buttons below to configure settings. Only server owners can make changes.")
    return embed

class ConfigNew(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

async def setup(bot):
    await bot.add_cog(ConfigNew(bot))
