import os
from dotenv import load_dotenv

load_dotenv()

def safe_int(value, default=None):
    if not value or not isinstance(value, str):
        return default
    value = value.strip()
    if value.startswith('your_') or value.endswith('_here') or not value.isdigit():
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

class Config:
    DISCORD_BOT_TOKEN = (os.getenv('DISCORD_BOT_TOKEN') or '').strip()
    BLOXLINK_API_KEY = (os.getenv('BLOXLINK_API_KEY') or '').strip()
    
    GUILD_ID = safe_int(os.getenv('GUILD_ID'), None)
    
    ALL_MEMBERS_CHANNEL = safe_int(os.getenv('ALL_MEMBERS_CHANNEL'), 1418915825716559884)
    MEMBERS_ONLY_CHANNEL = safe_int(os.getenv('MEMBERS_ONLY_CHANNEL'), 1418915829478723715)
    BOTS_CHANNEL = safe_int(os.getenv('BOTS_CHANNEL'), 1423891609795428372)
    GOAL_CHANNEL = safe_int(os.getenv('GOAL_CHANNEL'), 1423891664035905596)
    
    SUPPORT_CHANNEL_ID = safe_int(os.getenv('SUPPORT_CHANNEL_ID'), 1389999965979283608)
    TICKET_LOG_CHANNEL_ID = safe_int(os.getenv('TICKET_LOG_CHANNEL_ID'), None)
    
    VERIFIED_ROLE_ID = safe_int(os.getenv('VERIFIED_ROLE_ID'), 1423669554441355284)
    ROMODERATE_ROLE_ID = safe_int(os.getenv('ROMODERATE_ROLE_ID'), None)
    
    TICKET_INACTIVITY_TIMEOUT = safe_int(os.getenv('TICKET_INACTIVITY_TIMEOUT'), 1800)
    
    GOAL_MILESTONES = [800, 1000, 1500, 2000, 2500, 3000, 5000, 10000, 15000, 20000, 25000, 30000, 50000, 75000, 100000]
    
    TICKET_CLAIM_CHANNEL = 1409304816718709006
    STAFF_PING_ID = 1383270362707656774
    VERIFICATION_CHANNEL = 1423669807521202247
    COUNTING_CATEGORY = 1431428103674138634
    WELCOME_CATEGORY = 1409299795318804612
    
    EMBED_COLOR = 0x5865F2

    @classmethod
    def validate(cls):
        # Debug: Print what we're getting
        token = cls.DISCORD_BOT_TOKEN or ""
        print(f"\n🔍 DEBUG: Token length = {len(token)}")
        print(f"🔍 DEBUG: Token starts with = {token[:20] if token else 'EMPTY'}...")
        
        if not cls.DISCORD_BOT_TOKEN or cls.DISCORD_BOT_TOKEN.startswith('your_') or len(cls.DISCORD_BOT_TOKEN) < 50:
            raise ValueError(
                "\n" + "="*60 + "\n"
                "❌ DISCORD_BOT_TOKEN IS EMPTY OR INVALID!\n"
                "="*60 + "\n"
                "The token is either not set or too short.\n\n"
                "📝 IMMEDIATE FIX:\n"
                "1. Click the 🔒 'Secrets' tool in the LEFT sidebar (Tools panel)\n"
                "2. Click 'Edit as JSON' button\n"
                "3. Add your token like this:\n"
                "   {\n"
                '     "DISCORD_BOT_TOKEN": "YOUR_ACTUAL_TOKEN_HERE"\n'
                "   }\n"
                "4. Click 'Save'\n"
                "5. STOP the current run and click Run again\n\n"
                f"Current value length: {len(cls.DISCORD_BOT_TOKEN)} chars (needs 50+)\n"
                "="*60
            )
        if not cls.BLOXLINK_API_KEY or cls.BLOXLINK_API_KEY.startswith('your_'):
            raise ValueError(
                "❌ BLOXLINK_API_KEY is not configured!\n"
                "Please add your Bloxlink API key to Replit Secrets.\n"
                "You can use: 454b00db-82ce-4c2e-b5ae-3f3a27b02e72"
            )
        if not cls.GUILD_ID:
            raise ValueError(
                "❌ GUILD_ID is not configured!\n"
                "Please set your Discord server ID in Replit Secrets or .env file.\n"
                "Your GUILD_ID should be: 1383111706242191534"
            )
        return True
