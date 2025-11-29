# Complete Environment Variables Reference

This document lists **ALL** environment variables used by the Spiritual Battlegrounds Discord Bot.

## 🎯 Quick Reference Table

| Variable Name | Type | Required | Default | Description |
|--------------|------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | Secret | ✅ Yes | - | Discord bot authentication token |
| `BLOXLINK_API_KEY` | Secret | ✅ Yes | - | Bloxlink API for Roblox verification |
| `GUILD_ID` | ID | ✅ Yes | - | Your Discord server ID |
| `DATABASE_URL` | Connection | ✅ Yes | sqlite:///bot.db | PostgreSQL connection string |
| `HUGGINGFACE_API_KEY` | Secret | ⚠️ Recommended | - | AI chat provider API key |

---

## 📊 Stats Channels (Auto-updating voice channels)

| Variable | Required | Your Value | Description |
|----------|----------|------------|-------------|
| `ALL_MEMBERS_CHANNEL` | Yes | 1418915825716559884 | Shows total server members |
| `MEMBERS_ONLY_CHANNEL` | Yes | 1418915829478723715 | Shows human members only |
| `BOTS_CHANNEL` | Yes | 1423891609795428372 | Shows bot count |
| `GOAL_CHANNEL` | Yes | 1423891664035905596 | Shows progress to member goal |

---

## 🎫 Ticket System Configuration

| Variable | Required | Your Value | Description |
|----------|----------|------------|-------------|
| `SUPPORT_CHANNEL_ID` | Yes | 1389999965979283608 | Main support/ticket panel channel |
| `TICKET_CLAIM_CHANNEL` | Yes | 1409304816718709006 | Category for claimed tickets |
| `TICKET_SUPPORT_CATEGORY` | ⚠️ Yes | *Not Set* | Category ID for Support tickets |
| `TICKET_CC_CATEGORY` | ⚠️ Yes | *Not Set* | Category ID for Request CC tickets |
| `TICKET_REPORT_CATEGORY` | ⚠️ Yes | *Not Set* | Category ID for Report Member tickets |
| `TICKET_APPEAL_CATEGORY` | ⚠️ Yes | *Not Set* | Category ID for Warning Appeal tickets |
| `TICKET_TRANSCRIPT_CHANNEL` | ⚠️ Yes | *Not Set* | Where ticket transcripts are posted |
| `TICKET_LOG_CHANNEL_ID` | Yes | *Not Set* | General ticket activity logs |
| `TICKET_INACTIVITY_TIMEOUT` | No | 1800 | Seconds before flagging inactive ticket |

---

## 👮 Staff & Moderation Channels

| Variable | Required | Your Value | Description |
|----------|----------|------------|-------------|
| `SHIFT_LOG_CHANNEL` | Yes | 1436895129615995060 | Staff shift start/end logs |
| `PROMOTION_CHANNEL` | Yes | 1436895147206901810 | Staff promotion announcements |
| `INFRACTION_CHANNEL` | Yes | 1436895168367169637 | Warning & infraction logs |
| `MODLOG_CHANNEL` | ⚠️ Yes | *Not Set* | Moderation actions log |
| `AUDIT_LOG_CHANNEL` | ⚠️ Yes | *Not Set* | Complete audit trail |
| `BUG_REPORT_CHANNEL` | ⚠️ Yes | *Not Set* | User bug reports |

---

## 👋 Welcome & Verification

| Variable | Required | Your Value | Description |
|----------|----------|------------|-------------|
| `WELCOME_CHANNEL` | ⚠️ Yes | *Not Set* | Where welcome messages are sent |
| `WELCOME_CATEGORY` | Yes | 1409299795318804612 | Welcome section category |
| `VERIFICATION_CHANNEL` | Yes | 1423669807521202247 | Bloxlink verification panel |

---

## 🎮 Other Features

| Variable | Required | Your Value | Description |
|----------|----------|------------|-------------|
| `COUNTING_CATEGORY` | Yes | 1431428103674138634 | Counting game category |

---

## 👥 Role Configuration

| Variable | Required | Your Value | Description |
|----------|----------|------------|-------------|
| `VERIFIED_ROLE_ID` | Yes | 1423669554441355284 | Role given after verification |
| `STAFF_PING_ROLE_ID` | Yes | 1383270362707656774 | Role pinged for new tickets |
| `ROMODERATE_ROLE_ID` | ⚠️ Yes | *Not Set* | Main moderation team role |
| `COMMUNITY_MANAGER_ROLE_ID` | Recommended | *Not Set* | High-level staff role |
| `ADMIN_ROLE_ID` | Recommended | *Not Set* | Administrator role |
| `AFK_MUTED_ROLE_ID` | Optional | *Not Set* | Role for AFK users (optional) |

---

## 🤖 AI Configuration

| Variable | Required | Your Value | Description |
|----------|----------|------------|-------------|
| `HUGGINGFACE_API_KEY` | Recommended | ✅ Set | Hugging Face API for AI chat |

---

## 🌐 Web Dashboard (Optional)

| Variable | Required | Your Value | Description |
|----------|----------|------------|-------------|
| `WEB_SECRET_KEY` | For Dashboard | *Not Set* | Session encryption key |
| `DISCORD_CLIENT_ID` | For OAuth | *Not Set* | Discord OAuth2 Client ID |
| `DISCORD_CLIENT_SECRET` | For OAuth | *Not Set* | Discord OAuth2 Secret |
| `DASHBOARD_URL` | For OAuth | - | Your Replit URL |
| `WEB_PORT` | No | 5000 | Dashboard port |

---

## ⚙️ Bot Behavior

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COMMAND_PREFIX` | No | `.` | Bot command prefix |
| `EMBED_COLOR` | No | 0x5865F2 | Default embed color (hex) |
| `DEBUG_MODE` | No | false | Enable debug logging |

---

## 📝 Priority Setup Order

### **Phase 1: Critical (Bot Won't Start Without These)**
1. ✅ `DISCORD_BOT_TOKEN`
2. ✅ `BLOXLINK_API_KEY`
3. ✅ `GUILD_ID`
4. ✅ `DATABASE_URL` (Auto-configured)

### **Phase 2: Core Features**
5. `HUGGINGFACE_API_KEY`
6. `ROMODERATE_ROLE_ID`
7. `WELCOME_CHANNEL`
8. `TICKET_TRANSCRIPT_CHANNEL`

### **Phase 3: Ticket System**
9. `TICKET_SUPPORT_CATEGORY`
10. `TICKET_CC_CATEGORY`
11. `TICKET_REPORT_CATEGORY`
12. `TICKET_APPEAL_CATEGORY`

### **Phase 4: Moderation & Logging**
13. `MODLOG_CHANNEL`
14. `AUDIT_LOG_CHANNEL`
15. `BUG_REPORT_CHANNEL`

### **Phase 5: Advanced Roles**
16. `COMMUNITY_MANAGER_ROLE_ID`
17. `ADMIN_ROLE_ID`
18. `AFK_MUTED_ROLE_ID` (optional)

### **Phase 6: Web Dashboard (Optional)**
19. `DISCORD_CLIENT_ID`
20. `DISCORD_CLIENT_SECRET`
21. `WEB_SECRET_KEY`

---

## 📋 Copy-Paste Template for .env

```env
# CRITICAL - Bot won't start without these
DISCORD_BOT_TOKEN=
BLOXLINK_API_KEY=454b00db-82ce-4c2e-b5ae-3f3a27b02e72
GUILD_ID=1383111706242191534

# AI Provider
HUGGINGFACE_API_KEY=

# Roles - MUST SET
ROMODERATE_ROLE_ID=
VERIFIED_ROLE_ID=1423669554441355284
STAFF_PING_ROLE_ID=1383270362707656774

# Roles - RECOMMENDED
COMMUNITY_MANAGER_ROLE_ID=
ADMIN_ROLE_ID=

# Ticket Categories - MUST CREATE AND SET
TICKET_SUPPORT_CATEGORY=
TICKET_CC_CATEGORY=
TICKET_REPORT_CATEGORY=
TICKET_APPEAL_CATEGORY=
TICKET_TRANSCRIPT_CHANNEL=

# Moderation Channels - MUST SET
MODLOG_CHANNEL=
AUDIT_LOG_CHANNEL=
BUG_REPORT_CHANNEL=
WELCOME_CHANNEL=

# Already Configured ✅
SHIFT_LOG_CHANNEL=1436895129615995060
PROMOTION_CHANNEL=1436895147206901810
INFRACTION_CHANNEL=1436895168367169637
```

---

## 🎯 Summary

- **Total Variables:** 45+
- **Required for Startup:** 4
- **Already Configured:** 16
- **Need Configuration:** 11-15 (depending on features)
- **Optional:** 8-10

---

**Use this as your complete reference for setting up the bot!**
