import discord
from discord.ext import commands, tasks
import asyncio
import sys
from config import Config

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.presences = True

def get_prefix(bot, message):
    return commands.when_mentioned_or('.', '!')(bot, message)

class SpiritualBattlegroundsBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.config = Config
        self.cooldowns = {}
        self.target_voice_channel_id = 1394796103941095475
        self.presence_watchdog_running = False
    
    async def on_voice_state_update(self, member, before, after):
        if member == self.user:
            if before.channel and not after.channel:
                guild = None
                if self.config.GUILD_ID:
                    guild = self.get_guild(self.config.GUILD_ID)
                elif len(self.guilds) > 0:
                    guild = self.guilds[0]
                
                if guild:
                    voice_channel = guild.get_channel(self.target_voice_channel_id)
                    if voice_channel:
                        await asyncio.sleep(2)
                        try:
                            await asyncio.wait_for(
                                voice_channel.connect(timeout=30.0),
                                timeout=35.0
                            )
                            print(f"Reconnected to voice channel: {voice_channel.name}")
                        except asyncio.TimeoutError:
                            print(f"Failed to reconnect to voice channel (timeout)")
                        except Exception as e:
                            print(f"Failed to reconnect to voice channel: {e}")
    
    async def setup_hook(self):
        print("Loading cogs...")
        cogs = [
            'cogs.stats',
            'cogs.verification',
            'cogs.tickets_new',
            'cogs.moderation',
            'cogs.utils',
            'cogs.leveling',
            'cogs.counting',
            'cogs.welcome',
            'cogs.afk',
            'cogs.ai_chat',
            'cogs.voice',
            'cogs.config_new',
            'cogs.suggestions_bugs',
            'cogs.utilities',
            'cogs.staff_tools',
            'cogs.automod',
            'cogs.modlogs'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"Loaded {cog}")
            except Exception as e:
                print(f"Failed to load {cog}: {e}")
        
        print("All cogs loaded successfully")
        
        print("Registering persistent views...")
        from cogs.verification import VerificationView
        from cogs.tickets_new import TicketPanelView, TicketControlView, TicketClaimedView
        
        self.add_view(VerificationView())
        self.add_view(TicketPanelView())
        self.add_view(TicketControlView())
        self.add_view(TicketClaimedView())
        print("✓ Persistent views registered")
        
        try:
            synced = await self.tree.sync()
            print(f"✅ Slash commands loaded. ({len(synced)} commands synced)")
        except Exception as e:
            print(f"❌ Failed to sync slash commands: {e}")
    
    async def set_streaming_presence(self):
        """Set the bot's streaming presence"""
        try:
            await self.change_presence(
                status=discord.Status.online,
                activity=discord.Activity(
                    type=discord.ActivityType.streaming,
                    name="Spiritual Battleground",
                    url="https://twitch.tv/spiritualbattlegrounds"
                )
            )
        except Exception as e:
            print(f"Error setting presence: {e}")
    
    @tasks.loop(minutes=5)
    async def presence_watchdog(self):
        """Watchdog task to ensure bot stays streaming"""
        await self.set_streaming_presence()
    
    @presence_watchdog.before_loop
    async def before_presence_watchdog(self):
        await self.wait_until_ready()
    
    async def on_ready(self):
        print("="*50)
        print(f"✅ Bot is online and connected.")
        print(f"   Logged in as: {self.user} (ID: {self.user.id})")
        print(f"   Connected to {len(self.guilds)} guild(s)")
        print(f"✅ Prefix commands loaded.")
        print("="*50)
        
        await self.set_streaming_presence()
        
        if not self.presence_watchdog_running:
            self.presence_watchdog.start()
            self.presence_watchdog_running = True
            print("✅ Presence watchdog started - bot will stay streaming")
        
        guild = None
        if self.config.GUILD_ID:
            guild = self.get_guild(self.config.GUILD_ID)
        elif len(self.guilds) > 0:
            guild = self.guilds[0]
        
        if guild:
            try:
                print(f"Primary Guild: {guild.name} ({guild.id})")
                print(f"Members: {guild.member_count}")
                
                try:
                    print(f"Attempting to join voice channel ID: {self.target_voice_channel_id}")
                    voice_channel = guild.get_channel(self.target_voice_channel_id)
                    
                    if voice_channel:
                        print(f"Found channel: {voice_channel.name} (Type: {type(voice_channel).__name__})")
                        if isinstance(voice_channel, discord.VoiceChannel):
                            if not guild.voice_client:
                                # Try connecting with retry logic
                                max_retries = 3
                                retry_delay = 5
                                
                                for attempt in range(max_retries):
                                    try:
                                        print(f"Connection attempt {attempt + 1}/{max_retries}...")
                                        vc = await asyncio.wait_for(
                                            voice_channel.connect(timeout=30.0),
                                            timeout=35.0
                                        )
                                        print(f"✅ Joined Voice Channel {voice_channel.id}")
                                        break
                                    except asyncio.TimeoutError:
                                        if attempt < max_retries - 1:
                                            print(f"Connection attempt {attempt + 1} timed out, retrying in {retry_delay} seconds...")
                                            await asyncio.sleep(retry_delay)
                                        else:
                                            print(f"⚠ Failed to connect to voice channel after {max_retries} attempts (timeout)")
                                            print("Voice connection is optional - bot will continue without it")
                                    except Exception as connect_error:
                                        print(f"Connection attempt {attempt + 1} failed: {connect_error}")
                                        if attempt == max_retries - 1:
                                            print("⚠ Voice connection failed - bot will continue without it")
                                        else:
                                            await asyncio.sleep(retry_delay)
                            else:
                                print(f"Already connected to a voice channel")
                        else:
                            print(f"Channel {self.target_voice_channel_id} is not a voice channel (it's a {type(voice_channel).__name__})")
                    else:
                        print(f"❌ Voice channel with ID {self.target_voice_channel_id} not found in guild")
                        print(f"Available voice channels:")
                        for vc in guild.voice_channels:
                            print(f"  - {vc.name} (ID: {vc.id})")
                except discord.errors.ClientException as ce:
                    print(f"Client error connecting to voice: {ce}")
                    print("⚠ Voice connection failed - bot will continue without it")
                except Exception as voice_error:
                    print(f"Error connecting to voice channel: {voice_error}")
                    print(f"Error type: {type(voice_error).__name__}")
                    print("⚠ Voice connection failed - bot will continue without it")
            except Exception as e:
                print(f"Error fetching guild info: {e}")
        else:
            print("No guild found to connect to")

async def main():
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please set up your .env file with the required variables.")
        sys.exit(1)
    
    bot = SpiritualBattlegroundsBot()
    
    try:
        async with bot:
            await bot.start(Config.DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        print("Invalid bot token. Please check your DISCORD_BOT_TOKEN in .env")
    except Exception as e:
        print(f"Error starting bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
