# Environment Variables Setup Guide
## Spiritual Battlegrounds Discord Bot

This guide will help you set up all the required environment variables (secrets) for your Discord bot.

---

## 🔐 Required Secrets (Must Have)

### 1. **DISCORD_BOT_TOKEN** 
**What it is:** Your bot's authentication token  
**Where to get it:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Go to "Bot" section
4. Click "Reset Token" and copy it
5. **Keep this secret!** Never share it publicly

**Current Status:** ⚠️ Needs to be set

---

### 2. **HUGGINGFACE_API_KEY**
**What it is:** API key for AI chat functionality  
**Where to get it:**
1. Go to [Hugging Face](https://huggingface.co)
2. Sign up for an account
3. Go to [Settings > Access Tokens](https://huggingface.co/settings/tokens)
4. Create a new access token (read permission is sufficient)
5. Copy the key

**Current Status:** ⚠️ Needs to be set

---

### 3. **BLOXLINK_API_KEY**
**What it is:** API key for Roblox username verification  
**Current Status:** ✅ Already set in your .env

---

## 📋 Required Channel IDs (Must Configure)

To get Channel IDs in Discord:
1. Enable Developer Mode: Settings → Advanced → Developer Mode (ON)
2. Right-click any channel → Copy ID

### Ticket System Channels
- **TICKET_SUPPORT_CATEGORY** - Category for Support tickets
- **TICKET_CC_CATEGORY** - Category for Request CC tickets
- **TICKET_REPORT_CATEGORY** - Category for Report Member tickets
- **TICKET_APPEAL_CATEGORY** - Category for Warning Appeal tickets
- **TICKET_TRANSCRIPT_CHANNEL** - Where closed ticket transcripts are posted
- **TICKET_LOG_CHANNEL_ID** - General ticket activity logs

### Staff & Moderation Channels
- **SHIFT_LOG_CHANNEL** - Where shift start/end logs are posted (ID: 1436895129615995060 ✅)
- **PROMOTION_CHANNEL** - Promotion announcements (ID: 1436895147206901810 ✅)
- **INFRACTION_CHANNEL** - Warning/infraction logs (ID: 1436895168367169637 ✅)
- **MODLOG_CHANNEL** - Moderation action logs
- **AUDIT_LOG_CHANNEL** - Full audit trail of all bot actions
- **BUG_REPORT_CHANNEL** - User bug reports

### Other Channels
- **WELCOME_CHANNEL** - Where welcome messages are sent
- **VERIFICATION_CHANNEL** - Already set ✅
- **Stats Channels** - Already set ✅

---

## 👥 Required Role IDs (Must Configure)

To get Role IDs in Discord:
1. Right-click the role in Server Settings → Roles
2. Copy ID

### Essential Roles
- **ROMODERATE_ROLE_ID** - Main moderation team role (full access to mod commands)
- **STAFF_PING_ROLE_ID** - Role pinged when new tickets are created (Already set ✅)
- **COMMUNITY_MANAGER_ROLE_ID** - High-level role for promotions/force warns
- **ADMIN_ROLE_ID** - Admin role for sensitive commands
- **VERIFIED_ROLE_ID** - Role given after Bloxlink verification ✅
- **AFK_MUTED_ROLE_ID** - (Optional) Role assigned when users go AFK

---

## 🌐 Web Dashboard Setup (Optional)

If you want to build a web dashboard:

### **DISCORD_CLIENT_ID & DISCORD_CLIENT_SECRET**
**Where to get:**
1. [Discord Developer Portal](https://discord.com/developers/applications)
2. Your application → OAuth2 section
3. Copy Client ID and Client Secret
4. Add redirect URL: `https://your-replit-url.repl.co/callback`

### **WEB_SECRET_KEY**
Generate a random secret key for session security:
```python
import secrets
print(secrets.token_hex(32))
```

---

## 📦 Database Configuration

### **DATABASE_URL**
**Status:** ✅ **Already configured!** 
PostgreSQL database has been created and `DATABASE_URL` is automatically set by Replit.

**Current Database:** PostgreSQL (Production-ready)  
**Alternative:** SQLite is used as fallback for development

---

## 🚀 Quick Setup Checklist

Use this checklist to track your progress:

- [ ] Set **DISCORD_BOT_TOKEN**
- [ ] Set **HUGGINGFACE_API_KEY**
- [ ] Create all ticket category channels and set their IDs
- [ ] Set **TICKET_TRANSCRIPT_CHANNEL**
- [ ] Set **MODLOG_CHANNEL** and **AUDIT_LOG_CHANNEL**
- [ ] Set **BUG_REPORT_CHANNEL**
- [ ] Set **WELCOME_CHANNEL**
- [ ] Set **ROMODERATE_ROLE_ID**
- [ ] Set **COMMUNITY_MANAGER_ROLE_ID**
- [ ] Set **ADMIN_ROLE_ID**
- [ ] (Optional) Set **AFK_MUTED_ROLE_ID**
- [ ] (Optional) Configure web dashboard OAuth

---

## 📝 How to Add Environment Variables in Replit

### Method 1: Using Replit Secrets (Recommended)
1. Click the "Secrets" tool (🔒) in the left sidebar
2. Click "Edit as JSON" or add individually
3. Add each variable with its value
4. The bot will automatically read from secrets

### Method 2: Direct .env File Editing
1. Open the `.env` file in your Replit workspace
2. Replace `your_*_here` with actual values
3. Save the file

**Note:** Secrets tool is more secure and recommended for sensitive data!

---

## 🔍 Finding Your Discord Server/Guild ID

**GUILD_ID** is already set to: `1383111706242191534` ✅

To verify or change:
1. Right-click your server icon
2. Click "Copy ID"
3. Update GUILD_ID in your environment

---

## ⚙️ Current Configuration Status

✅ **Configured:**
- Guild ID
- Bloxlink API Key
- Stats Channels (All Members, Members Only, Bots, Goal)
- Verification Channel
- Shift Log Channel
- Promotion Channel
- Infraction Channel
- Staff Ping Role
- Verified Role
- Counting & Welcome Categories
- PostgreSQL Database

⚠️ **Needs Configuration:**
- Discord Bot Token
- Hugging Face API Key
- Ticket Categories (4 categories)
- Ticket Transcript Channel
- ModLog & Audit Log Channels
- Bug Report Channel
- Welcome Channel
- Romoderate Role
- Community Manager Role
- Admin Role

---

## 🆘 Need Help?

If you're stuck on any step:
1. Check that Developer Mode is enabled in Discord
2. Verify you have permission to access the channels/roles
3. Make sure you're copying the ID, not the name
4. IDs are long numbers (e.g., 1436895129615995060)

---

## 📚 Additional Resources

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Hugging Face](https://huggingface.co)
- [Discord.py Documentation](https://discordpy.readthedocs.io)
- [Bloxlink API](https://blox.link/developers)

---

**Last Updated:** November 2025  
**Bot Version:** Spiritual Battlegrounds v2.0
