# Spiritual Battlegrounds Discord Bot - Enhanced Specification

## Core Philosophy
The bot must be stable, user-friendly, professional, and feature-rich. All systems must work flawlessly with no duplicate messages, proper error handling, and intuitive UX.

---

## 1. AI Assistant System

### Core Requirements
- **Built-in, free to use, and always active**
- **Direct text responses** - No unnecessary embeds
- **Context-aware and intelligent**

### AI Capabilities

#### Response System
- Respond to users' queries directly in text
- Use natural language processing for better understanding
- Provide accurate information only
- Suggest staff involvement when issues are beyond AI scope

#### Teaching System (`/teach` and `!teach`)
- **Access**: Administrator permission required
- **Functionality**: Users can train the bot with custom responses
- **Persistence**: Training is stored permanently in database
- **Scope**: Server-wide learned responses
- **Syntax**: 
  - Simple response: `!teach trigger response text here`
  - Action/rule: `!teach report @Bot if a user wants to report a player, it must be done in #support`
- **Context types**:
  - Direct responses (greetings, FAQs)
  - Rule enforcement (channel usage, report procedures)
  - Automated actions (ticket claiming, role assignments)

#### Context Retention
- **User Data Memory**:
  - Roblox usernames (pulled from verification)
  - Discord IDs and roles
  - User level and activity status
  - Previous ticket history
  - Last 10 messages in current conversation
- **Server Structure Memory**:
  - All categories and channels
  - Role hierarchy
  - Server rules and guidelines
  - Frequently asked questions
- **Memory Duration**: 
  - Active conversation: Session-based (until conversation ends)
  - Taught responses: Permanent
  - User verification data: Permanent
  - General context: Reset every 24 hours for performance

#### Ticket Integration
- **AI Activation**: Automatically active in new tickets
- **STOP/START Commands**:
  - `STOP` - Pause AI assistance
  - `START` - Resume AI assistance
  - Must respond with confirmation messages
- **Smart Suggestions**:
  - Analyze ticket type and provide relevant help
  - Collect necessary information before staff involvement
  - Suggest closing ticket when issue appears resolved
  - Escalate to staff when AI cannot help
- **Conversation History**: Maintain full ticket conversation for context

#### Fallback Handling
- **API Timeout**: "I'm experiencing delays. Please wait a moment or type STOP to talk to staff directly."
- **API Failure**: "AI is temporarily unavailable. A staff member will assist you shortly."
- **Rate Limiting**: Queue responses, max 1 response per 3 seconds per ticket
- **Error Logging**: Log all AI errors for admin review

---

## 2. Suggestion & Bug Report System

### Suggestion Channel (1409310962103877752)
- **Auto-Analysis**: AI reviews suggestion for usefulness
- **Forwarding**: Useful suggestions → Channel 1436559543139045437
- **Format**: 
  ```
  📝 New Suggestion from @Username
  [User's Profile Picture]
  
  Suggestion: [content here]
  
  Submitted: [timestamp]
  ```
- **Reactions**: Add ✅ reaction to original when forwarded
- **Spam Filter**: Block repeat suggestions (same user, same content within 1 hour)
- **Threshold**: Suggestions with 10+ 👍 reactions auto-forward

### Bug Report Channel (1409311252400050196)
- **Format**:
  ```
  🐛 Bug Report from @Username
  
  Description: [content]
  
  Status: Pending Review
  Report ID: #BUG-[number]
  ```
- **Logging**: Store in database with status tracking
- **Admin Commands**:
  - `/bugstatus <ID> <status>` - Mark as fixed/investigating/wontfix
  - `/buglog` - View all bug reports
- **User Notification**: DM user when bug status changes

### Activity Analysis
- **Tracking**:
  - Count suggestions per user (weekly/monthly leaderboard)
  - Track bug reports per user
  - Award "Contributor" role after 5 accepted suggestions
- **Reports**:
  - `/contributorleaderboard` - Show top contributors
  - `/mycontributions` - Show user's personal stats

---

## 3. Counting System

### Channel: 1431428103674138634

### Rules
- Count from 1 → 5000
- Maximum 5 mistakes per user
- 5-second cooldown between messages
- Cannot count twice in a row
- Numbers only (no text, emojis, or formatting)

### Enforcement
- **Wrong Number**: Delete message, record mistake, show remaining mistakes
- **Too Fast**: Delete message, show "Please wait [X] seconds before typing"
- **Duplicate User**: Delete message, record mistake
- **5 Mistakes Reached**: 1-hour lockout with DM notification

### Reset & Leaderboard
- **Auto-Reset**: When 5000 is reached, celebrate and reset to 1
- **Celebration Message**: 
  ```
  🎉 Congratulations! The server has reached 5000!
  Top Contributors:
  1. @User1 - 847 counts
  2. @User2 - 621 counts
  3. @User3 - 503 counts
  
  Starting over from 1...
  ```
- **Manual Reset**: `/countreset` (Server Manager only)
- **Leaderboard**: `/countleaderboard` - Show top 10 counters

### Mistake Management
- **View Mistakes**: `/countmistakes [@user]` - Check mistake count
- **Reset Mistakes**: `/resetmistakes @user` (Moderator+)
- **Mistake History**: Log all mistakes with timestamps

---

## 4. Level-Up System

### XP & Leveling
- **XP Per Message**: 15 XP
- **Cooldown**: 60 seconds between XP gains
- **Formula**: 
  - Level 2: 100 XP
  - Level 3: 200 XP
  - Level 4: 300 XP
  - Pattern: Level N requires (N-1) × 100 XP
- **Bonus XP**:
  - Verified users: +5 XP per message
  - Messages in active discussions (3+ participants): +10 XP
  - Voice chat activity: 10 XP per 5 minutes

### Announcements
- **Channel**: 1409304816718709006
- **Format**: Plain text only (no embeds)
- **Message**: `@Username is now Level [number]! 🎉`
- **Milestone Rewards**:
  - Level 5: "Active Member" role
  - Level 10: "Regular" role + custom color
  - Level 25: "Veteran" role + special perms
  - Level 50: "Legend" role + exclusive channel access

### Excluded Channels
- Counting channel (prevents abuse)
- Bot commands channel
- Spam channel
- AFK channel

### Commands
- `/rank [@user]` - Check level, XP, and rank
- `/leaderboard` - Top 10 server levels
- `/setxp @user <amount>` (Admin only)
- `/resetlevel @user` (Admin only)

---

## 5. Command System

### Universal Commands
All commands must support both prefix (`.` or `!`) and slash (`/`) versions with identical functionality.

### Core Commands

#### .say / /say
- **Function**: Bot repeats the message
- **Access**: Junior Moderator+
- **Filters**:
  - Block @everyone and @here pings
  - Block role mentions
  - Filter profanity/slurs (delete and warn sender)
  - Max 1000 characters
- **Logging**: Log who used command, what they said, and where
- **Syntax**: `.say <channel> <message>` or `/say channel:<#channel> message:<text>`

#### .afk / /afk
- **Function**: Set AFK status with optional reason
- **Access**: Everyone
- **Features**:
  - Display "[AFK]" tag in mention responses
  - Auto-remove AFK when user sends next message
  - Show AFK reason when mentioned
  - Track AFK duration
- **Syntax**: `.afk [reason]` or `/afk reason:[optional]`

#### /unafk
- **Function**: Manually remove AFK status
- **Access**: Everyone

#### /giveaway
- **Access**: Junior Admin+
- **Parameters**:
  - Duration (minutes/hours/days)
  - Prize description
  - Winner count (1-10)
  - Required role (optional)
  - Minimum level (optional)
  - Channel to announce
- **Functionality**:
  - React with 🎉 to enter
  - Auto-select random winners when time expires
  - DM winners and announce in channel
  - Reroll option if winner doesn't respond within 24 hours
- **Syntax**: `/giveaway duration:1h prize:Nitro winners:1 channel:#giveaways`

#### /poll
- **Access**: Moderator+
- **Parameters**:
  - Question
  - Options (2-10)
  - Duration
  - Allow multiple votes (yes/no)
- **Features**:
  - Auto-add number reactions (1️⃣, 2️⃣, etc.)
  - Live result tracking
  - Announce results when closed
- **Syntax**: `/poll question:"Best feature?" options:"AI, Tickets, Levels" duration:1h`

---

## 6. Configuration System

### /config and .config
- **Access**: Owner/Server Manager only
- **Interface**: Button-based navigation
  - ✅ Next
  - ◀️ Previous
  - 🔄 Reload
  - 📤 Submit

### Configuration Sections

#### 1. Command Permissions
- Assign which roles can use which commands
- Toggle command availability per channel
- Set custom cooldowns per command

#### 2. Ticket Categories
- Create/edit/delete ticket categories
- Set category-specific AI behavior
- Assign staff roles per category
- Custom opening messages per category

#### 3. Verification Settings
- Toggle auto-role on verification
- Set verified role ID
- Configure Bloxlink integration
- Age/account age requirements

#### 4. AI Settings
- Enable/disable AI per channel
- Set AI response style (formal/casual)
- Configure teaching permissions
- AI rate limiting settings

#### 5. Moderation Settings
- Auto-mod rules (spam, links, caps)
- Warning thresholds and actions
- Mute/ban duration defaults
- Log channel configuration

#### 6. Leveling Settings
- XP rates and cooldowns
- Level-up announcement channel
- Milestone roles and rewards
- Excluded channels

#### 7. AFK System
- Enable/disable AFK tracking
- AFK timeout (auto-remove after X hours inactive)
- AFK announcement channel

### Error Handling
- **Invalid Input**: "❌ Invalid configuration. Please check your settings."
- **Missing Permissions**: "❌ This role does not have permission to access this setting."
- **Save Confirmation**: "✅ Configuration saved successfully!"

---

## 7. Role-Based Permissions

### Permission Hierarchy

| Role | ID | Permissions |
|------|---|-------------|
| Trial Moderator | 1383270277147787294 | Warn, Timeout |
| Junior Moderator | 1409873374288674816 | Kick + Trial Mod |
| Moderator | 1383175157186564286 | Clear/Purge + Junior Mod |
| Appeals Manager | 1423157373295525979 | Appeal Review, Appeal Commands |
| Senior Admin | 1383145641491828746 | Junior Admin perms |
| Junior Admin | 1409874361615388746 | All utilities, giveaways |
| Administrator | 1388254732543590492 | All moderation/utilities |
| Head of Staff | 1409874452866400346 | Same as Admin |
| Community Manager | 1411739899639496704 | Almost all commands (no server settings) |
| Server Manager | 1383270529430978590 | Everything including config |

### Permission Enforcement
- Commands check role hierarchy before executing
- Show specific error: "❌ This command requires [Role Name] or higher."
- Log permission violations for audit

---

## 8. Voice Channel Features

### Voice Commands

#### /join
- **Function**: Bot joins your current voice channel
- **Access**: Everyone
- **Uses**: Future music/soundboard features

#### /leave
- **Function**: Bot leaves voice channel
- **Access**: Moderator+ or voice channel owner

### Voice Activity Tracking
- Track time spent in voice channels
- Award voice XP (10 XP per 5 minutes)
- Exclude AFK channel from tracking
- Show voice leaderboard: `/voiceleaderboard`

### Auto-Join Features
- Join when 5+ members are in a channel (for events)
- Auto-announce events in voice channels
- Text-to-speech announcements (toggle-able)

---

## 9. Advanced Moderation Features

### Moderation Commands

#### /warn <user> <reason>
- **Access**: Trial Moderator+
- **Function**: Issue warning to user
- **Escalation**:
  - 3 warnings = 1-hour timeout
  - 5 warnings = 24-hour timeout
  - 7 warnings = kick
  - 10 warnings = ban
- **Logging**: All warnings logged with moderator, reason, timestamp

#### /warnings <user>
- **Access**: Trial Moderator+
- **Function**: View all warnings for a user

#### /clearwarnings <user>
- **Access**: Administrator+
- **Function**: Clear all warnings for a user

#### /timeout <user> <duration> <reason>
- **Access**: Trial Moderator+
- **Duration Options**: 60s, 5m, 10m, 1h, 1d, 1w
- **Logging**: Log timeout with details

#### /kick <user> <reason>
- **Access**: Junior Moderator+
- **Confirmation**: Require button confirmation
- **Logging**: Full audit log

#### /ban <user> <reason> [delete_days]
- **Access**: Moderator+
- **Confirmation**: Require button confirmation
- **Options**: Delete messages from last 0-7 days
- **Logging**: Full audit log with unban instructions

#### /unban <user_id> <reason>
- **Access**: Moderator+
- **Logging**: Log unban action

#### /purge <amount> [user] [contains]
- **Access**: Moderator+
- **Function**: Bulk delete messages
- **Filters**:
  - Amount (1-100)
  - Specific user's messages
  - Messages containing text
  - Bots only
  - Embeds only
  - Links only
- **Confirmation**: Show preview, require confirmation
- **Logging**: Log what was purged and by whom

#### /lock [channel] <reason>
- **Access**: Moderator+
- **Function**: Lock channel (remove send message permission)
- **Notification**: "🔒 This channel has been locked. Reason: [reason]"

#### /unlock [channel]
- **Access**: Moderator+
- **Function**: Unlock channel
- **Notification**: "🔓 This channel has been unlocked."

#### /slowmode <seconds> [channel]
- **Access**: Moderator+
- **Options**: 0s (off), 5s, 10s, 30s, 1m, 5m, 15m, 1h, 6h
- **Notification**: "⏱️ Slowmode set to [duration]"

### Auto-Moderation

#### Spam Detection
- **Triggers**:
  - 5+ messages in 5 seconds
  - 10+ identical messages
  - Mass emoji spam (20+ emojis)
- **Action**: Auto-timeout 5 minutes, warn user

#### Link Filtering
- **Settings**:
  - Whitelist trusted domains
  - Block discord invite links (except permitted channels)
  - Block IP grabbers and malicious sites
- **Action**: Delete message, warn user

#### Caps Lock Filter
- **Trigger**: 70%+ capital letters in messages over 10 characters
- **Action**: Delete message, friendly reminder

#### Mass Mention Protection
- **Trigger**: 5+ mentions in one message
- **Action**: Delete message, timeout 10 minutes

#### Profanity Filter
- **Settings**: Configurable word list
- **Action**: Delete message, issue warning
- **Bypass**: Messages from Moderator+ ignore filter

### Moderation Logging
- **Log Channel**: Configurable in /config
- **Logged Actions**:
  - All warns, timeouts, kicks, bans
  - Message edits and deletions (with content)
  - Role changes
  - Channel lockdowns
  - Auto-mod actions
  - Join/leave events
- **Format**: Clean embeds with all relevant info

---

## 10. Ticket System Enhancements

### Ticket Panel (`/ticketpanel`)
- **Access**: Administrator+
- **Function**: Send professional embed with ticket creation buttons
- **Categories**:
  - 🎫 General Support
  - 📝 Player Report
  - 🐛 Bug Report
  - 💡 Suggestion
  - ⚖️ Appeal (Ban/Warn)
  - ❓ Other
- **Embed Design**:
  ```
  🎫 Need Help? Create a Ticket!
  
  Click the button below to create a support ticket.
  Our staff team will assist you as soon as possible.
  
  Please select the appropriate category for faster support.
  ```

### Ticket Categories

Each category has custom behavior:

#### General Support
- **AI Behavior**: Answer common questions, guide to FAQs
- **Auto-Assign**: Available support staff
- **Initial Message**: "Welcome! Please describe your issue and our team will assist you."

#### Player Report
- **AI Behavior**: Collect evidence (username, offense, screenshots)
- **Required Info**: 
  - Player's Roblox username
  - Type of offense
  - Evidence (screenshots/videos)
- **Auto-Assign**: Moderators
- **Initial Message**: "Please provide the reported player's username, what they did, and any evidence."

#### Bug Report
- **AI Behavior**: Gather reproduction steps
- **Required Info**:
  - What happened
  - Expected behavior
  - Steps to reproduce
- **Auto-Assign**: Developers/Admins
- **Initial Message**: "Please describe the bug, what you expected to happen, and steps to reproduce it."

#### Appeal
- **AI Behavior**: Collect appeal details, remain neutral
- **Required Info**:
  - Punishment type (ban/warn/timeout)
  - Reason for punishment
  - Why it should be appealed
  - Evidence
- **Auto-Assign**: Appeals Manager
- **Initial Message**: "Please explain what punishment you're appealing, why you were punished, and why you believe it should be removed."

### Ticket Commands

#### User Commands
- `STOP` - Pause AI (already specified)
- `START` - Resume AI (already specified)
- `/close [reason]` - Close your ticket

#### Staff Commands
- `/claim` - Claim ticket for yourself
- `/unclaim` - Unclaim ticket
- `/adduser @user` - Add user to ticket
- `/removeuser @user` - Remove user from ticket
- `/rename <new-name>` - Rename ticket channel
- `/transcript` - Generate and save full conversation log
- `/forceclose <ticket>` - Close any ticket (Admin only)

### Ticket Features
- **Claim System**: Staff can claim tickets (shows "Claimed by @Staff")
- **Transcripts**: Auto-saved when closed, uploaded to log channel
- **Inactivity**: Close tickets after 48 hours of no response (with warning at 24h)
- **Ratings**: After close, DM user to rate experience (1-5 stars)
- **Analytics**: Track response times, resolution rates, staff performance

---

## 11. Welcome & Verification System

### Welcome Messages
- **Channel**: Configurable
- **Format**: 
  ```
  Welcome to Spiritual Battlegrounds, @Username! 👋
  
  Please verify your Roblox account to gain access to the server.
  Click the "Verify" button below to get started!
  
  Member #[count]
  ```
- **Auto-Delete**: Remove welcome after user verifies

### Verification Process
1. User clicks "Verify" button
2. Bloxlink verification modal appears
3. User links Roblox account
4. Auto-assign role: 1423669554441355284
5. Welcome to verified channels message
6. Log verification in audit channel

### Verification Features
- **Auto-Nickname**: Set nickname to Roblox username
- **Group Rank Sync**: Sync roles based on Roblox group rank
- **Re-verification**: `/reverify` updates Roblox data
- **Unverified Kick**: Auto-kick unverified users after 7 days (toggle-able)

---

## 12. Additional Quality-of-Life Features

### Server Information

#### /serverinfo
- Total members, bots, online count
- Server creation date, boost level
- Role count, channel count
- Server owner and staff count

#### /userinfo [@user]
- Join date, account creation date
- Roles, nickname
- Level, XP, rank
- Voice time, message count
- Verification status and Roblox username

#### /avatar [@user]
- Display user's avatar in high quality
- Include server-specific avatar if different

#### /roleinfo <role>
- Member count with this role
- Role permissions
- Role creation date, color

### Utility Commands

#### /ping
- Show bot latency
- API response time
- Database response time

#### /help [command]
- List all available commands for user's role
- Detailed help for specific command
- Category-based navigation

#### /rules
- Display server rules
- Require reaction to accept rules (for new members)
- Track who has accepted rules

#### /announce <channel> <message>
- **Access**: Community Manager+
- **Function**: Send professional announcement
- **Features**: Optional @everyone ping, embed formatting

#### /embed
- **Access**: Junior Admin+
- **Function**: Interactive embed builder
- **Features**: Title, description, color, fields, image, thumbnail, footer

#### /remind <time> <message>
- **Access**: Everyone
- **Function**: Bot reminds you after specified time
- **Examples**: `/remind 1h Check giveaway` → DM after 1 hour

#### /snipe [channel]
- **Access**: Moderator+
- **Function**: Show last deleted message
- **Limit**: Last 5 deleted messages, max 5 minutes old

#### /editsnipe [channel]
- **Access**: Moderator+
- **Function**: Show message before edit
- **Format**: Display old → new content

### Fun Commands

#### /coinflip
- Flip a coin (Heads/Tails)

#### /roll <max>
- Roll dice (1 to max)
- Default max: 100

#### /8ball <question>
- Magic 8-ball responses

#### /rps <choice>
- Rock, Paper, Scissors vs bot

### Starboard
- **Channel**: Configurable (e.g., #starboard)
- **Threshold**: 5 ⭐ reactions
- **Function**: Showcase best messages
- **Format**: Display original message with star count and link

---

## 13. Economy System (Optional Advanced Feature)

### Currency
- **Name**: Spirit Coins (SC)
- **Earn By**:
  - Daily reward: 100 SC (`/daily`)
  - Voice chat: 50 SC per hour
  - Leveling up: 500 SC per level
  - Winning giveaways
  - Staff rewards for helpfulness

### Shop
- **Custom Roles**: 5,000 SC (custom color, name)
- **Profile Backgrounds**: 2,000 SC
- **Nickname Changes**: 1,000 SC (bypass cooldown)
- **Channel Access**: 10,000 SC (VIP channels for 30 days)

### Commands
- `/balance [@user]` - Check SC balance
- `/pay @user <amount>` - Transfer SC
- `/shop` - View purchasable items
- `/buy <item>` - Purchase item
- `/leaderboard economy` - Richest users

---

## 14. Staff Utility Features

### Activity Tracking
- **Command**: `/staffactivity [period]`
- **Function**: Show staff performance metrics
  - Messages sent
  - Tickets handled
  - Moderation actions taken
  - Response time average
  - Online time
- **Periods**: Today, Week, Month, All Time

### Staff Notes
- **Command**: `/note @user <note>`
- **Access**: Trial Moderator+
- **Function**: Add internal notes about users
- **View**: `/notes @user` (staff only)
- **Use Case**: Track behavior patterns, context for future actions

### Case System
- **Auto-Assign**: Each mod action gets a unique case number
- **Command**: `/case <number>`
- **Function**: View full details of past moderation action
- **Modify**: `/editcase <number> <new_reason>` (action author or Admin)

### Staff Announcements
- **Channel**: Staff-only channel (configurable)
- **Command**: `/staffannounce <message>`
- **Access**: Administrator+
- **Function**: Ping all staff with important updates

---

## 15. Performance & Reliability

### Technical Requirements

#### No Duplicates
- Implement message cooldowns per command
- Use interaction IDs to prevent double-processing
- Database locks for concurrent operations

#### Error Handling
- Try-catch all async operations
- Graceful degradation (if AI fails, show error but don't crash)
- Auto-retry failed API calls (max 3 attempts)
- Log all errors to error channel (staff-only)

#### Database
- Auto-save every 5 minutes
- Backup database daily to separate file
- Database corruption detection and recovery
- Transaction-based operations for data integrity

#### Rate Limiting
- Respect Discord API limits
- Queue messages to avoid 429 errors
- User command cooldowns (1-5 seconds depending on command)

#### Memory Management
- Clear old cache data (messages older than 24 hours)
- Limit stored deleted messages (max 100)
- Prune old tickets from database (archive after 30 days)

### Professional Appearance
- Consistent embed colors (success: green, error: red, info: blue)
- Clean button layouts (max 5 buttons per row)
- Clear loading indicators ("Processing...")
- Professional language in all messages
- Proper capitalization and punctuation

---

## 16. Security Features

### Anti-Raid Protection
- **Mass Join Detection**: 10+ joins in 10 seconds
- **Action**: Enable verification captcha, notify staff
- **Auto-Kick**: Kick accounts younger than 1 day during raid

### Anti-Nuke Protection
- **Protect Against**:
  - Mass channel deletion
  - Mass role deletion
  - Mass ban
- **Action**: Remove permissions, alert owner, create audit log

### Permission Safety
- **Bot Permission Check**: Verify bot has required permissions before executing
- **Hierarchy Check**: Ensure bot role is above target role
- **Owner Protection**: Cannot moderate server owner

### API Key Security
- All keys stored in environment variables
- Never log or display API keys
- Rotate keys if exposed (with warning system)

---

## 17. Multi-Language Support (Future Enhancement)

### Supported Languages
- English (default)
- Spanish
- Portuguese
- French

### Implementation
- User preference: `/language <lang>`
- Store per-user language preference
- Translate all bot responses
- Keep commands in English (universal)

---

## 18. Event System

### Event Commands

#### /event create
- **Access**: Community Manager+
- **Parameters**: Name, description, date/time, channel, role ping
- **Function**: Schedule server event with reminder
- **Reminder**: Ping 1 hour before, 15 minutes before

#### /event list
- Show upcoming events

#### /event join <event>
- RSVP to event (add to attendee list)

#### /event cancel <event>
- **Access**: Event creator or Admin
- **Function**: Cancel event and notify attendees

---

## 19. Analytics Dashboard (Advanced)

### /analytics
- **Access**: Administrator+
- **Metrics**:
  - Daily/weekly/monthly active users
  - Message count trends
  - Most active channels
  - Most active members
  - Command usage statistics
  - Ticket volume and resolution time
  - Verification rate
  - Member growth rate
- **Export**: Generate CSV report

---

## 20. Status & Presence

### Bot Status Rotation
Rotate status every 5 minutes:
- "Playing Spiritual Battlegrounds"
- "Watching over [member count] members"
- "Listening to /help"
- "Managing [open ticket count] tickets"
- "Type /help for commands"

### Activity Type
- Rotate between Playing, Watching, Listening
- Show online status (green dot)
- Custom status for special events

---

## Final Notes

### Testing Requirements
- Test every command before deployment
- Verify all permissions work correctly
- Stress test with high message volume
- Test error scenarios (API failures, missing permissions)
- User acceptance testing with real users

### Documentation
- Create `/guide` command with beginner tutorial
- Maintain changelog for updates
- In-bot command documentation (`/help`)
- Staff handbook with moderation guidelines

### Maintenance
- Weekly database cleanup
- Monthly permission audit
- Update dependencies regularly
- Monitor error logs daily
- Backup database before major updates

---

**All systems must be stable, reliable, and professional. No bugs from previous implementations. Focus on polish, user experience, and clear Discord formatting.**
