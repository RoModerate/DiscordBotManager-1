# Spiritual Battlegrounds Discord Bot

## Overview

The Spiritual Battlegrounds Discord Bot is a comprehensive, production-ready bot designed to enhance server management and user engagement. Its core purpose is to provide dynamic member statistics, a robust custom Bloxlink verification, an advanced ticket system, leveling/XP tracking, an interactive counting game, an AFK system, AI chat integration, voice channel control, and a full suite of moderation tools. The bot is optimized for Pella.app hosting and features dual command prefix support (. and /). Key ambitions include a clean, professional user interface and reliable, feature-rich functionality to foster an active and well-managed Discord community.

## User Preferences

### Design Requirements
- Clean, professional UI
- Discord markdown formatting
- Focus on functionality and reliability
- Button-based interactions (no dropdown menus for tickets)
- Plain text welcome messages (no embeds)
- English-only counting channel
- Complete transcript generation with all message data

### Command Design
- Dual prefix support: . and /
- Case-insensitive command names
- Ephemeral responses for error messages
- Permission-based access control
- Cooldown system to prevent spam

### Permission Model
- Romoderate team has full access to all moderation features
- Owner-only access for /config command
- Permission checks on all commands
- Role-based access control

## System Architecture

### Project Structure
The bot follows a modular design with a `cogs` directory for organizing features.
```
/
├── main.py                 # Main bot entry point with hybrid command support
├── config.py              # Configuration management
├── database.py            # Persistent data storage
├── cogs/                  # Modular feature cogs
│   ├── stats.py          # Dynamic voice channel stats
│   ├── verification.py   # Bloxlink verification system
│   ├── tickets_new.py    # Advanced ticket system
│   ├── moderation.py     # Moderation commands
│   ├── utils.py          # Utility commands
│   ├── leveling.py       # XP/Level system
│   ├── counting.py       # Counting game
│   ├── welcome.py        # Plain text welcome messages
│   ├── afk.py            # AFK system
│   ├── ai_chat.py        # AI chat integration
│   ├── voice.py          # Voice channel join/leave functionality
│   └── config_new.py     # Interactive paged configuration UI
├── web_control.py        # Web dashboard backend (Flask)
├── templates/
│   ├── base.html         # Base template with DanDaDan styling
│   ├── home.html         # Dashboard home page
│   ├── bot_control.html  # Bot and AI operations control
│   ├── ai_memory.html    # Server-wide message memory viewer
│   └── tickets.html      # Autonomous ticket system overview
├── bot_data.json         # Persistent database file
├── database.json         # Main database file
├── .env.example          # Environment variable template
├── README.md             # Project documentation
└── SETUP_GUIDE.md        # Complete setup instructions
```

### Key Features and Implementations

#### Dual Prefix & Hybrid Commands
- Supports both `.` and `/` prefixes for all commands.
- Commands are case-insensitive.
- Hybrid commands automatically generate both prefix and slash versions, handled by `send_response()` for proper ephemeral messaging.

#### Advanced Autonomous Ticket System
- **UI**: Utilizes a 4-button UI for ticket creation (Support, Report Player, Warning Appeal, Request CC).
- **AI Autonomous Handling**: AI agent handles tickets in 3 categories (Support, Request CC, Warning Appeal) with initial greeting and continuous intelligent responses using server context.
- **Active Categories**: AI only responds in Support (1436498409153626213), Request CC (1436498445216256031), and Warning Appeal (1436498528544227428). Report Player tickets are manual-only.
- **Category-Specific Prompts**: Each ticket type has specialized AI behavior tailored to the ticket category.
- **Auto-Claim on Creation**: When ticket is created in allowed categories, AI automatically claims it, pings ticket manager role (1383270362707656774), and updates channel name with green emoji indicator.
- **Channel Naming**: Claimed tickets are renamed to `《🟢》・username-[category]` where category is "support", "request", or "warning-appeal".
- **Workflow**: Modals for reason input, Claim/Unclaim functionality with `🔴`/`🟢` indicators in channel names.
- **AI Control**: Staff can type STOP/START in tickets to pause/resume AI, global control via /start and /stop commands.
- **AI Channel Restrictions**: AI enforces strict channel restrictions - only responds in 3 allowed ticket categories, ignores messages with @everyone/@here/role pings unless from Ticket Manager or Appeal Manager, prevents response in general chat/logs/bot command channels.
- **Ticket Summary Command**: `!summarize` command for Ticket Manager and Appeal Manager roles provides comprehensive ticket overview including type, status, creator, claimed by, message count, conversation history, and initial reason.
- **Auto-Close Inactive Tickets**: Hourly background task automatically closes tickets with no reply for 24 hours, sends notification before closing, generates and logs full transcript, properly updates database records.
- **AI Ticket Closing**: AI can close tickets when user requests with explicit phrases (e.g., "close this ticket", "i'm done here"). AI responds with "Alright!" before generating transcript and closing channel.
- **AI Human Escalation**: When users request human support, AI pings ticket manager role and stops autonomous responses until staff types START.
- **Teaching Integration**: AI uses taught knowledge base (cached for 5 minutes, limited to 10 items, rewrites in own words) when responding to tickets for consistent, accurate answers.
- **Transcripts**: Full transcript generation on close, including content, attachments, embeds, and system messages, saved to category-specific log channels.
- **Notifications**: Ticket manager role (1383270362707656774) is pinged automatically when tickets are created in allowed categories.

#### AFK System
- Commands: `/afk`, `.afk`, `/unafk`, `.unafk` with optional reasons and duration parsing (e.g., 30m, 2h).
- Features optional muted role assignment and auto-notification when AFK users are mentioned.
- AFK states are database-persistent.

#### AI Chat & Autonomous AI System (Updated November 2025)
- **Bot Status**: Set to "Do Not Disturb" with name "Spiritual Battleground" (singular).
- **Natural Conversations**: AI responds naturally to all mentions without "not taught yet" guard.
- **Server-Wide Memory**: All user messages logged to build contextual knowledge for intelligent responses.
- **Teaching System**: Exact-match trigger detection (no partial/first-word triggering).
- **Commands**: `!teach [trigger] [response]` and `!unteach [trigger/ID]` with timestamp confirmations.
- **AI Enhancement**: LLM configured to never repeat user questions, provide direct answers only.
- **Persistence**: All taught responses and conversation history stored permanently in database.

#### Interactive Configuration System
- Owner-only access with a paged UI (Previous/Next/Reload/Submit buttons).
- Configurable settings include Verification, Welcome, Tickets, Staff Roles, AFK, and Stats Channels.
- Features real-time ID validation and full database persistence for all settings.

#### Other Core Features
- **Counting Game**: English-only, sequence counting with mistake tracking and cooldowns.
- **Welcome System**: Simple plain text welcome messages for new members, configurable channel.
- **Dynamic Voice Channel Stats**: Auto-updates every 5 minutes, tracking members, bots, and goal progress.
- **Leveling & XP System**: Automatic XP gain with cooldown, level-up announcements, and persistent storage.
- **Bloxlink Verification**: Button-based UI, integration with Bloxlink API for role assignment.
- **Moderation Suite**: Comprehensive commands for warn, mute, kick, ban, and message purging with an 8-tier warning system.

#### Professional Web Dashboard - DanDaDan Theme (New November 2025)
- **DanDaDan Aesthetic**: Purple/pink gradient theme matching combatwarriors.gg style with dark background and glassmorphism effects.
- **Multi-Page Design**: Home, Bot Control, AI Memory, and Ticket Operations pages with smooth routing.
- **Bot Controls**: Start, stop, and restart bot directly from web interface.
- **AI Operations Control**: Global STOP/START toggles for autonomous AI (chat and tickets) via POST /ai/start and /ai/stop endpoints.
- **AI Memory Dashboard**: View server-wide message logs and statistics (total messages, recent activity).
- **Ticket Operations**: Overview of 4 autonomous ticket categories and AI handling workflow.
- **Live Updates**: Auto-refreshing status every 5 seconds with real-time indicators.
- **Accessibility**: Runs on port 5000, accessible via Replit webview.

### Technology Stack
- Python 3.11
- discord.py 2.6.4
- aiohttp 3.13.2
- python-dotenv 1.2.1
- pynacl (for voice support)
- Flask + Flask-CORS (for web dashboard)
- psutil (for bot process management)

## Recent Updates (November 2025)

### Ticket System & AI Enhancements (November 29, 2025)
- **Ticket Pings**: Bot now pings both the ticket creator and bot user ID (1436208461112148060) when a ticket is opened and in all AI responses
- **Reason Acknowledgment**: AI reads and acknowledges the ticket opening reason from embeds in initial greetings and all subsequent responses
- **Context Persistence**: AI maintains ticket context (type, reason, label) throughout the conversation for more relevant responses
- **Punctuation Filtering**: Bot ignores punctuation-only messages (e.g., `??`, `..`, `!!!`) to prevent false triggers
- **Streaming Presence Watchdog**: Bot maintains streaming status via a 5-minute watchdog task that resets presence
- **Teaching Improvements**: Improved trigger matching with better normalization (handles punctuation, quotes, hyphens) and safer fuzzy matching for longer triggers
- **Teaches Command**: Enabled paginated `!teaches` command to list all taught responses with 10 items per page
- **AI Safety**: All AI responses are sanitized to prevent @everyone/@here pings

### AI Provider Migration to Hugging Face (November 2025)
- **API Switch**: Migrated from OpenRouter to Hugging Face Inference API for all AI functionality.
- **Model**: Using `meta-llama/Llama-3.2-3B-Instruct` via Hugging Face's free inference API.
- **Integration Points**: Updated both AI chat (`cogs/ai_chat.py`) and autonomous ticket handling (`cogs/tickets_new.py`).
- **Environment Variable**: Changed from `OPENROUTER_API_KEY` to `HUGGINGFACE_API_KEY`.
- **Documentation**: All setup guides, environment references, and config checks updated to reflect Hugging Face.

### Autonomous AI Agent System (November 2025)
1. **Natural AI Conversations**: Removed "not taught yet" guard - AI responds naturally to all mentions and questions.
2. **Server-Wide Memory System**: All user messages logged to database for contextual AI learning (ai_memory.messages).
3. **Autonomous Ticket Handling**: AI agent handles tickets in 4 categories with intelligent initial greetings and continuous responses.
4. **Category-Specific AI**: Support, Report Player, Warning Appeal, and Request CC each have specialized prompts and behavior.
5. **Global STOP/START Control**: 
   - Discord commands: /start and /stop (hybrid commands in ai_chat.py)
   - Ticket-level: Type STOP/START in any ticket channel
   - Web dashboard: AI Operations control buttons with POST /ai/start and /ai/stop endpoints
6. **Bot Configuration**: Status set to "Do Not Disturb", name changed to "Spiritual Battleground" (singular).

### DanDaDan Multi-Page Web Dashboard (November 2025)
- **Aesthetic**: Full DanDaDan anime theme with purple/pink gradients, dark background, glassmorphism effects.
- **Pages**: Home (overview), Bot Control (start/stop/AI ops), AI Memory (message logs/stats), Ticket Operations (category overview).
- **Flask Routing**: Multi-page support with base template for consistent styling across all pages.
- **API Integration**: Dashboard fully integrated with backend - controls bot processes and AI operations.
- **Production Ready**: All features tested and architect-approved for deployment.

## External Dependencies

- **Discord API**: Core platform for bot interaction.
- **Bloxlink API**: Used for custom Roblox verification.
- **Hugging Face API**: Provides LLM access for AI chat integration using Llama 3.2 3B Instruct model.
- **`database.json`**: Main database storing all bot data including taught responses.
- **Environment Variables**: For sensitive credentials like `DISCORD_BOT_TOKEN`, `BLOXLINK_API_KEY`, `HUGGINGFACE_API_KEY`, and `GUILD_ID`.