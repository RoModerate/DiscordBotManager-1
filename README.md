# Spiritual Battlegrounds Discord Bot

A comprehensive Discord bot built for the Spiritual Battlegrounds server with advanced features including dynamic stats tracking, custom Bloxlink verification, ticket system, and moderation suite.

## Features

### Dynamic Voice Channel Stats
- Automatically updates voice channel names with real-time statistics
- All Members count (total members including bots)
- Members Only count (excluding bots)
- Bot count
- Goal tracker with intelligent milestone progression

### Custom Bloxlink Verification
- Clean UI with gray Verify and blue Can't Verify buttons
- Integration with Bloxlink API for Roblox account linking
- Automatic Verified role assignment
- Support channel redirection for verification issues
- Welcome DM for new members

### Professional Ticket System
- One-click ticket creation with Open Ticket button
- Private ticket channels with staff access
- Auto-logging to dedicated log channel
- Inactivity timeout management
- Clean closure process

### Comprehensive Moderation Suite
- Warning system with automatic escalation (8-tier punishment structure)
- Mute, kick, and ban commands
- Message clearing (bulk delete)
- Permission-based access control for Romoderate team
- DM notifications for warnings
- Persistent warning tracking

### Utility Commands
- Server statistics dashboard
- Ping check
- Server information
- Help command with complete command list

## Setup

### Requirements
- Python 3.11+
- Discord Bot Token
- Bloxlink API Key (included in config)

### Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your Discord bot token
   - Set your Guild ID
   - Configure role IDs (Verified, Romoderate)
   - Set ticket log channel ID

4. Run the bot:
```bash
python main.py
```

### Environment Variables

```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
BLOXLINK_API_KEY=454b00db-82ce-4c2e-b5ae-3f3a27b02e72

GUILD_ID=your_guild_id_here

ALL_MEMBERS_CHANNEL=1418915825716559884
MEMBERS_ONLY_CHANNEL=1418915829478723715
BOTS_CHANNEL=1423891609795428372
GOAL_CHANNEL=1423891664035905596

SUPPORT_CHANNEL_ID=1389999965979283608
TICKET_LOG_CHANNEL_ID=your_ticket_log_channel_id_here

VERIFIED_ROLE_ID=your_verified_role_id_here
ROMODERATE_ROLE_ID=your_romoderate_role_id_here

TICKET_INACTIVITY_TIMEOUT=1800
```

### Bot Permissions

The bot requires the following permissions:
- Manage Roles
- Manage Channels
- Read Messages/View Channels
- Send Messages
- Manage Messages
- Kick Members
- Ban Members
- Moderate Members (for timeout)

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to Bot section and create a bot
4. Enable these Privileged Gateway Intents:
   - Server Members Intent
   - Message Content Intent
5. Copy the bot token to your `.env` file
6. Generate invite link with required permissions and add bot to your server

## Commands

### Verification Commands
- `!setupverify [channel]` - Set up verification panel

### Ticket Commands
- `!ticketpanel [channel]` - Set up ticket panel
- `!closeticket` - Close current ticket

### Moderation Commands
- `!warn <member> [reason]` - Warn a member (automatic escalation)
- `!warnings [member]` - Check warning count
- `!clearwarnings <member>` - Clear all warnings
- `!mute <member> <duration> [reason]` - Mute a member (5m, 1h, 1d, 1w)
- `!unmute <member>` - Unmute a member
- `!kick <member> [reason]` - Kick a member
- `!ban <member> [reason]` - Ban a member
- `!unban <user_id> [reason]` - Unban a user
- `!clear <amount>` - Delete messages (1-100)

### Utility Commands
- `!stats` - View server statistics
- `!updatestats` - Force update voice channel stats
- `!ping` - Check bot latency
- `!serverinfo` - View server information
- `!help` - Show help message

## Warning System

The bot implements an 8-tier automatic escalation system:

1. Warning 1: Verbal reminder
2. Warning 2: 3-minute mute
3. Warning 3: 15-minute mute
4. Warning 4: 1-hour mute
5. Warning 5: 5-hour mute
6. Warning 6: 1-day mute
7. Warning 7: 1-week mute
8. Warning 8: Permanent ban

## Deployment

### Pella.app Hosting

This bot is optimized for Pella.app hosting with:
- Automatic reconnection on disconnect
- Proper error handling
- Clean startup and shutdown
- Low resource usage

To deploy on Pella.app:
1. Push your code to a Git repository
2. Connect the repository to Pella.app
3. Set environment variables in Pella.app dashboard
4. Deploy and start the bot

## Support

For issues or questions, open a ticket in your Discord server or contact the development team.

## License

This bot is built for the Spiritual Battlegrounds Discord server.
# DiscordBotManager-1
