#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*60)
print("🔍 ENVIRONMENT VARIABLES CHECK")
print("="*60 + "\n")

critical_vars = {
    'DISCORD_BOT_TOKEN': 'Discord Bot Token',
    'BLOXLINK_API_KEY': 'Bloxlink API Key',
    'GUILD_ID': 'Discord Server/Guild ID',
}

important_vars = {
    'HUGGINGFACE_API_KEY': 'AI Chat API Key (Hugging Face)',
    'ROMODERATE_ROLE_ID': 'Moderation Team Role',
    'TICKET_TRANSCRIPT_CHANNEL': 'Ticket Transcripts Channel',
    'MODLOG_CHANNEL': 'Moderation Log Channel',
    'AUDIT_LOG_CHANNEL': 'Audit Log Channel',
    'BUG_REPORT_CHANNEL': 'Bug Reports Channel',
    'WELCOME_CHANNEL': 'Welcome Messages Channel',
}

optional_vars = {
    'COMMUNITY_MANAGER_ROLE_ID': 'Community Manager Role',
    'ADMIN_ROLE_ID': 'Admin Role',
    'AFK_MUTED_ROLE_ID': 'AFK Muted Role',
}

def check_var(var_name, description):
    value = os.getenv(var_name)
    if not value:
        return '❌', 'Not Set', value
    elif value.startswith('your_') or value.endswith('_here'):
        return '⚠️', 'Placeholder', value
    else:
        masked = value[:10] + '...' if len(value) > 10 else value
        return '✅', 'Configured', masked

print("🔴 CRITICAL (Required for bot to start):")
print("-" * 60)
critical_ok = True
for var, desc in critical_vars.items():
    status, state, value = check_var(var, desc)
    print(f"{status} {desc:30} [{state}]")
    if status != '✅':
        critical_ok = False

print("\n🟡 IMPORTANT (Core features won't work without these):")
print("-" * 60)
for var, desc in important_vars.items():
    status, state, value = check_var(var, desc)
    print(f"{status} {desc:30} [{state}]")

print("\n🟢 OPTIONAL (Enhanced features):")
print("-" * 60)
for var, desc in optional_vars.items():
    status, state, value = check_var(var, desc)
    print(f"{status} {desc:30} [{state}]")

print("\n" + "="*60)
if critical_ok:
    print("✅ All critical variables are configured!")
    print("   Your bot should be able to start.")
else:
    print("⚠️  Some critical variables need configuration.")
    print("   Please update your .env file before starting the bot.")
print("="*60 + "\n")

print("📝 Need help? Check these files:")
print("   - ENVIRONMENT_SETUP_GUIDE.md (step-by-step setup)")
print("   - ENV_VARIABLES_REFERENCE.md (complete reference)")
print("\n")
