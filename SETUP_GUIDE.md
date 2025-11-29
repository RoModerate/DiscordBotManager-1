# Spiritual Battlegrounds Bot - Complete Setup Guide

## Current Status

Your bot is now running and connected to Discord successfully.

Bot Name: Spiritual Battlegrounds#3445
Bot ID: 1436208461112148060

## Important Next Steps

To fully activate all bot features, you need to configure the following:

### 1. Invite the Bot to Your Server

The bot is currently not in any server. Use this link format to invite it:

```
https://discord.com/api/oauth2/authorize?client_id=1436208461112148060&permissions=8&scope=bot
```

Or create a custom invite link with specific permissions:
- Go to Discord Developer Portal
- Select your application
- Go to OAuth2 > URL Generator
- Select scopes: `bot`
- Select permissions: Administrator (or specific permissions as needed)
- Copy and use the generated URL

### 2. Required Environment Variables to Configure

After adding the bot to your server, set these environment variables in Replit Secrets:

#### Guild Configuration
```
GUILD_ID=your_server_id_here
```
How to find: Right-click your server icon > Copy Server ID (Developer Mode must be enabled)

#### Role IDs
```
VERIFIED_ROLE_ID=your_verified_role_id_here
ROMODERATE_ROLE_ID=your_romoderate_role_id_here
```
How to find: Server Settings > Roles > Right-click role > Copy Role ID

#### Channel IDs for Logging
```
TICKET_LOG_CHANNEL_ID=your_ticket_log_channel_id_here
```
How to find: Right-click channel > Copy Channel ID

### 3. Voice Channel Stats (Already Configured)

The following voice channels are already set in the configuration:
- All Members Channel: 1418915825716559884
- Members Only Channel: 1418915829478723715
- Bots Channel: 1423891609795428372
- Goal Channel: 1423891664035905596

These will automatically update every 5 minutes once the bot is in your server.

### 4. Setup Commands to Run

Once the bot is in your server, run these commands to set up the features:

#### Verification Panel
```
!setupverify #verification-channel
```
This creates the verification panel with gray Verify and blue Can't Verify buttons.

#### Ticket Panel
```
!ticketpanel #support
```
This creates the ticket panel in your support channel.

### 5. Bot Permissions Required

Ensure the bot has these permissions in your server:
- Administrator (recommended for full functionality)

Or specific permissions:
- Manage Roles
- Manage Channels
- Read Messages/View Channels
- Send Messages
- Manage Messages
- Kick Members
- Ban Members
- Moderate Members (for timeout/mute)
- Manage Webhooks

### 6. Testing the Bot

After configuration, test these features:

#### Stats System
- Voice channels should update automatically every 5 minutes
- Use `!updatestats` to force an immediate update

#### Verification
- Click the Verify button in the verification panel
- The bot will check Bloxlink API for your linked Roblox account

#### Tickets
- Click Open Ticket button
- A private ticket channel will be created
- Use Close Ticket button or `!closeticket` command to close

#### Moderation
- `!warn @user test warning` - Test warning system
- `!warnings @user` - Check warning count
- `!mute @user 5m test` - Test mute (5 minutes)
- `!help` - View all commands

### 7. Romoderate Team Setup

Members with the Romoderate role will have access to all moderation commands. Make sure to:
1. Create or identify the Romoderate role in your server
2. Copy its ID and set it in ROMODERATE_ROLE_ID
3. Assign this role to your moderators
4. Restart the bot for changes to take effect

### 8. Common Issues and Solutions

#### Bot not responding to commands
- Check that bot has Read/Send Messages permissions
- Verify the bot is online (green status)
- Check console logs for errors

#### Stats channels not updating
- Verify GUILD_ID is set correctly
- Check that channel IDs are correct
- Ensure bot has Manage Channels permission

#### Verification not working
- Confirm Bloxlink API key is correct (already configured)
- Ensure users have linked their Roblox account via Bloxlink
- Check that VERIFIED_ROLE_ID is set

#### Tickets not creating
- Verify bot has Manage Channels permission
- Check that it can read/send in the support channel category
- Ensure ROMODERATE_ROLE_ID is set if you want staff access

### 9. Production Deployment on Pella.app

The bot is optimized for Pella.app hosting:
1. All environment variables are managed through Replit Secrets
2. Automatic reconnection on disconnect is built-in
3. Error handling prevents crashes
4. Low resource usage design

No additional configuration needed for Pella.app deployment.

### 10. Advanced Configuration

#### Goal Milestones
The bot automatically sets the next goal based on current member count. Default milestones:
800, 1000, 1500, 2000, 2500, 3000, 5000, 10000, 15000, 20000, 25000, 30000, 50000, 75000, 100000

To customize, edit the `GOAL_MILESTONES` list in `config.py`.

#### Ticket Inactivity Timeout
Default: 30 minutes (1800 seconds)
To change, set TICKET_INACTIVITY_TIMEOUT in Replit Secrets.

#### Bloxlink API Key
Already configured: 454b00db-82ce-4c2e-b5ae-3f3a27b02e72
If you need to change it, update BLOXLINK_API_KEY in Replit Secrets.

## Support

If you encounter any issues:
1. Check the console logs in the Replit output
2. Verify all environment variables are set correctly
3. Ensure the bot has proper permissions
4. Test commands in a test channel first

## Quick Start Checklist

- [ ] Invite bot to server using OAuth2 URL
- [ ] Set GUILD_ID in Replit Secrets
- [ ] Set VERIFIED_ROLE_ID in Replit Secrets
- [ ] Set ROMODERATE_ROLE_ID in Replit Secrets
- [ ] Set TICKET_LOG_CHANNEL_ID in Replit Secrets
- [ ] Run `!setupverify #verification-channel`
- [ ] Run `!ticketpanel #support`
- [ ] Test verification system
- [ ] Test ticket system
- [ ] Test moderation commands
- [ ] Verify voice channel stats are updating

Once completed, your Spiritual Battlegrounds Discord bot will be fully operational!
