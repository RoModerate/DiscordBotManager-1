import discord
from discord.ext import commands, tasks
from datetime import datetime
import asyncio

class ServerIndex(commands.Cog):
    """Server indexing system for live data accuracy"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.indexing_lock = asyncio.Lock()
        self._initialize_db()
        self.nightly_resync.start()
    
    def _initialize_db(self):
        """Initialize database structure for server indexing"""
        if 'server_index' not in self.db.data:
            self.db.data['server_index'] = {
                'channels': {},
                'categories': {},
                'roles': {},
                'members': {},
                'pinned_messages': {},
                'last_sync': None
            }
            self.db.save()
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Index server on bot startup"""
        await asyncio.sleep(5)  # Wait for bot to fully initialize
        await self.index_server()
    
    async def index_server(self, guild_id=None):
        """Scan and store complete server structure"""
        async with self.indexing_lock:
            try:
                guild = self.bot.get_guild(int(self.bot.config.get('GUILD_ID', 0))) if not guild_id else self.bot.get_guild(guild_id)
                
                if not guild:
                    print("❌ Could not find guild for indexing")
                    return
                
                print(f"🔍 Starting server indexing for {guild.name}...")
                
                # Index channels and categories
                await self._index_channels(guild)
                
                # Index roles
                await self._index_roles(guild)
                
                # Index members with Bloxlink data
                await self._index_members(guild)
                
                # Index pinned messages
                await self._index_pinned_messages(guild)
                
                # Update last sync time
                self.db.data['server_index']['last_sync'] = datetime.utcnow().isoformat()
                self.db.save()
                
                print(f"✅ Server indexing complete! Indexed {len(self.db.data['server_index']['channels'])} channels, {len(self.db.data['server_index']['roles'])} roles, {len(self.db.data['server_index']['members'])} members")
                
            except Exception as e:
                print(f"❌ Error during server indexing: {e}")
    
    async def _index_channels(self, guild):
        """Index all channels, categories, and their properties"""
        channels_data = {}
        categories_data = {}
        
        for channel in guild.channels:
            if isinstance(channel, discord.CategoryChannel):
                categories_data[str(channel.id)] = {
                    'name': channel.name,
                    'id': channel.id,
                    'position': channel.position,
                    'channels': [c.id for c in channel.channels]
                }
            else:
                channel_info = {
                    'name': channel.name,
                    'id': channel.id,
                    'type': str(channel.type),
                    'category': channel.category.name if channel.category else None,
                    'category_id': channel.category.id if channel.category else None,
                    'position': channel.position
                }
                
                # Add permission overwrites
                if hasattr(channel, 'overwrites'):
                    channel_info['permission_overwrites'] = {
                        str(target.id): {
                            'type': 'role' if isinstance(target, discord.Role) else 'member',
                            'name': target.name,
                            'permissions': [perm for perm, value in overwrite if value is not None]
                        }
                        for target, overwrite in channel.overwrites.items()
                    }
                
                channels_data[str(channel.id)] = channel_info
        
        self.db.data['server_index']['channels'] = channels_data
        self.db.data['server_index']['categories'] = categories_data
    
    async def _index_roles(self, guild):
        """Index all roles and their properties"""
        roles_data = {}
        
        for role in guild.roles:
            roles_data[str(role.id)] = {
                'name': role.name,
                'id': role.id,
                'color': str(role.color),
                'position': role.position,
                'permissions': role.permissions.value,
                'mentionable': role.mentionable,
                'hoist': role.hoist,
                'member_count': len(role.members)
            }
        
        self.db.data['server_index']['roles'] = roles_data
    
    async def _index_members(self, guild):
        """Index all members with Bloxlink usernames if available"""
        members_data = {}
        
        for member in guild.members:
            member_info = {
                'id': member.id,
                'name': member.name,
                'display_name': member.display_name,
                'discriminator': member.discriminator,
                'bot': member.bot,
                'roles': [role.id for role in member.roles if role.id != guild.id],
                'joined_at': member.joined_at.isoformat() if member.joined_at else None,
                'created_at': member.created_at.isoformat(),
                'roblox_username': None
            }
            
            # Try to get Roblox username from verification data
            verification = self.db.get_verification(member.id)
            if verification:
                member_info['roblox_username'] = verification.get('roblox_username')
            
            members_data[str(member.id)] = member_info
        
        self.db.data['server_index']['members'] = members_data
    
    async def _index_pinned_messages(self, guild):
        """Index pinned messages from all channels"""
        pinned_data = {}
        
        for channel in guild.text_channels:
            try:
                pins = await channel.pins()
                if pins:
                    pinned_data[str(channel.id)] = [
                        {
                            'message_id': msg.id,
                            'content': msg.content[:500],  # Limit content length
                            'author': msg.author.name,
                            'created_at': msg.created_at.isoformat()
                        }
                        for msg in pins[:10]  # Limit to 10 most recent pins per channel
                    ]
            except discord.Forbidden:
                pass  # Skip channels we can't access
            except Exception as e:
                print(f"Error indexing pins in {channel.name}: {e}")
        
        self.db.data['server_index']['pinned_messages'] = pinned_data
    
    @tasks.loop(hours=24)
    async def nightly_resync(self):
        """Re-index server every 24 hours"""
        await self.index_server()
    
    @nightly_resync.before_loop
    async def before_nightly_resync(self):
        await self.bot.wait_until_ready()
    
    def get_live_channel_count(self):
        """Get real-time channel count"""
        guild = self.bot.get_guild(int(self.bot.config.get('GUILD_ID', 0)))
        if guild:
            text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
            voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
            return {'text': text_channels, 'voice': voice_channels, 'total': len(guild.channels)}
        return None
    
    def get_live_role_count(self):
        """Get real-time role count"""
        guild = self.bot.get_guild(int(self.bot.config.get('GUILD_ID', 0)))
        return len(guild.roles) if guild else 0
    
    def get_live_member_count(self):
        """Get real-time member count"""
        guild = self.bot.get_guild(int(self.bot.config.get('GUILD_ID', 0)))
        if guild:
            humans = len([m for m in guild.members if not m.bot])
            bots = len([m for m in guild.members if m.bot])
            return {'total': guild.member_count, 'humans': humans, 'bots': bots}
        return None
    
    def find_channel_by_name(self, name):
        """Find channel by name from indexed data"""
        name_lower = name.lower()
        for channel_id, channel_data in self.db.data['server_index']['channels'].items():
            if name_lower in channel_data['name'].lower():
                return channel_data
        return None
    
    def find_role_by_name(self, name):
        """Find role by name from indexed data"""
        name_lower = name.lower()
        for role_id, role_data in self.db.data['server_index']['roles'].items():
            if name_lower in role_data['name'].lower():
                return role_data
        return None
    
    @commands.hybrid_command(name='reindex', description='Force server re-indexing')
    @commands.has_permissions(administrator=True)
    async def reindex(self, ctx):
        """Manually trigger server re-indexing"""
        await ctx.defer(ephemeral=True)
        
        await self.index_server()
        
        embed = discord.Embed(
            title="✅ Server Re-indexed",
            description=f"Successfully re-indexed the server structure.\n\n"
                       f"**Channels:** {len(self.db.data['server_index']['channels'])}\n"
                       f"**Roles:** {len(self.db.data['server_index']['roles'])}\n"
                       f"**Members:** {len(self.db.data['server_index']['members'])}\n"
                       f"**Last Sync:** {self.db.data['server_index'].get('last_sync', 'Never')}",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='serverinfo', description='Get detailed server information')
    async def serverinfo(self, ctx):
        """Display comprehensive server information from index"""
        channels = self.get_live_channel_count()
        members = self.get_live_member_count()
        roles = self.get_live_role_count()
        
        embed = discord.Embed(
            title=f"📊 Server Information: {ctx.guild.name}",
            description=f"Real-time server statistics and structure",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        if channels:
            embed.add_field(
                name="📝 Channels",
                value=f"**Total:** {channels['total']}\n**Text:** {channels['text']}\n**Voice:** {channels['voice']}",
                inline=True
            )
        
        if members:
            embed.add_field(
                name="👥 Members",
                value=f"**Total:** {members['total']}\n**Humans:** {members['humans']}\n**Bots:** {members['bots']}",
                inline=True
            )
        
        embed.add_field(
            name="🎭 Roles",
            value=f"**Total:** {roles}",
            inline=True
        )
        
        last_sync = self.db.data['server_index'].get('last_sync', 'Never')
        embed.set_footer(text=f"Last indexed: {last_sync}")
        
        await ctx.send(embed=embed)
    
    async def cog_unload(self):
        self.nightly_resync.cancel()

async def setup(bot):
    await bot.add_cog(ServerIndex(bot))
