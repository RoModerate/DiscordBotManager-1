import json
import os
from datetime import datetime, timedelta

class Database:
    def __init__(self, filename='database.json'):
        self.filename = filename
        self.data = self.load()
        self.last_save = datetime.utcnow()
        self._initialize_defaults()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return self.default_structure()
        return self.default_structure()

    def default_structure(self):
        return {
            'levels': {},
            'counting': {
                'current': 0,
                'last_user': None,
                'mistakes': {}
            },
            'tickets': {},
            'ticket_transcripts': {},
            'warnings': {},
            'cooldowns': {},
            'afk_states': {},
            'teach_database': {},
            'verifications': {},
            'open_tickets': {},
            'suggestions': {},
            'bug_reports': {},
            'staff_notes': {},
            'events': {},
            'economy': {
                'balances': {},
                'transactions': [],
                'shop_items': {}
            },
            'moderation_cases': {},
            'starboard': {},
            'reminders': {},
            'voice_activity': {},
            'deleted_messages': [],
            'edited_messages': [],
            'giveaways': {},
            'polls': {},
            'user_contributions': {},
            'ai_memory': {
                'messages': [],
                'summaries': {},
                'profiles': {},
                'last_cleanup': None
            },
            'ticket_ai_state': {},
            'analytics': {
                'daily_messages': {},
                'command_usage': {},
                'ticket_stats': {}
            },
            'config': {
                'log_channel': None,
                'ticket_category': None,
                'verification_channel': None,
                'verified_role': None,
                'welcome_message': 'Welcome to the server!',
                'counting_channel': 1409299795318804612,
                'welcome_channel': None,
                'muted_role': None,
                'staff_ping_role': 1383270362707656774,
                'staff_ping_user': 1383270362707656774,
                'transcript_channel': 1420538005936013403,
                'ai_enabled': True,
                'ai_ops_enabled': True,
                'ai_endpoint': 'https://api.sampleapis.com/ai/v1/chat/completions',
                'ai_model': 'meta-llama/Llama-3.2-3B-Instruct:fastest',
                'ai_temperature': 0.7,
                'ai_memory_retention_days': 30,
                'ai_memory_max_messages': 10000,
                'ticket_categories': {
                    'support': 1436498409153626213,
                    'cc': 1436498445216256031,
                    'report': 1436498495153635512,
                    'appeal': 1436498528544227428
                },
                'command_permissions': {},
                'suggestion_channel': 1409310962103877752,
                'suggestion_forward_channel': 1436559543139045437,
                'bug_channel': 1409311252400050196,
                'error_log_channel': None,
                'starboard_channel': None,
                'starboard_threshold': 5,
                'economy_enabled': False,
                'anti_raid_enabled': True,
                'auto_mod_enabled': True,
                'excluded_xp_channels': []
            }
        }

    def _initialize_defaults(self):
        """Initialize default configuration values if not set"""
        defaults = {
            'counting_channel': 1431428103674138634,
            'transcript_channel': 1420538005936013403,
            'level_channel': 1409304816718709006,
            'welcome_channel': 1409299795318804612,
            'verified_role': 1423669554441355284,
            'help_channel': 1389999965979283608,
            'log_channel': 1411710143598690404,
            'ai_enabled': True,
            'ticket_categories': {
                'support': 1436498409153626213,
                'cc': 1436498445216256031,
                'report': 1436498495153635512,
                'appeal': 1436498528544227428
            }
        }

        if 'config' not in self.data:
            self.data['config'] = {}

        for key, value in defaults.items():
            if key not in self.data['config']:
                self.data['config'][key] = value

        self.save()


    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_user_level(self, guild_id, user_id):
        key = f"{guild_id}:{user_id}"
        if key not in self.data['levels']:
            self.data['levels'][key] = {'xp': 0, 'level': 1, 'last_message': None}
        return self.data['levels'][key]

    def add_xp(self, guild_id, user_id, amount):
        key = f"{guild_id}:{user_id}"
        user_data = self.get_user_level(guild_id, user_id)
        user_data['xp'] += amount

        xp_needed = self.get_xp_for_level(user_data['level'])
        if user_data['xp'] >= xp_needed:
            user_data['level'] += 1
            user_data['xp'] = 0
            self.save()
            return True, user_data['level']

        self.save()
        return False, user_data['level']

    def get_xp_for_level(self, level):
        return 5 * (level ** 2) + (50 * level) + 100

    def get_counting_data(self):
        return self.data['counting']

    def update_counting(self, current, last_user):
        self.data['counting']['current'] = current
        self.data['counting']['last_user'] = last_user
        self.save()

    def add_counting_mistake(self, user_id):
        if user_id not in self.data['counting']['mistakes']:
            self.data['counting']['mistakes'][user_id] = {
                'count': 0,
                'locked_until': None
            }
        self.data['counting']['mistakes'][user_id]['count'] += 1
        self.save()
        return self.data['counting']['mistakes'][user_id]['count']

    def lock_user_from_counting(self, user_id, hours=1):
        if user_id not in self.data['counting']['mistakes']:
            self.data['counting']['mistakes'][user_id] = {'count': 0}

        locked_until = (datetime.utcnow() + timedelta(hours=hours)).isoformat()
        self.data['counting']['mistakes'][user_id]['locked_until'] = locked_until
        self.save()

    def is_user_locked(self, user_id):
        if user_id not in self.data['counting']['mistakes']:
            return False

        locked_until = self.data['counting']['mistakes'][user_id].get('locked_until')
        if not locked_until:
            return False

        return datetime.fromisoformat(locked_until) > datetime.utcnow()

    def get_config(self, key):
        if 'config' not in self.data:
            self.data['config'] = {}
        return self.data['config'].get(key)

    def set_config(self, key, value):
        if 'config' not in self.data:
            self.data['config'] = {}
        self.data['config'][key] = value
        self.save()

    def get_all_config(self):
        if 'config' not in self.data:
            self.data['config'] = {}
        return self.data['config']

    def set_afk(self, user_id, reason, until_time, muted=False):
        if 'afk_states' not in self.data:
            self.data['afk_states'] = {}
        self.data['afk_states'][str(user_id)] = {
            'reason': reason,
            'until': until_time.isoformat() if until_time else None,
            'muted': muted,
            'set_at': datetime.utcnow().isoformat()
        }
        self.save()

    def remove_afk(self, user_id):
        if 'afk_states' not in self.data:
            self.data['afk_states'] = {}
        if str(user_id) in self.data['afk_states']:
            del self.data['afk_states'][str(user_id)]
            self.save()
            return True
        return False

    def get_afk(self, user_id):
        if 'afk_states' not in self.data:
            self.data['afk_states'] = {}
        afk_data = self.data['afk_states'].get(str(user_id))
        if afk_data:
            if afk_data.get('until'):
                until_time = datetime.fromisoformat(afk_data['until'])
                if datetime.utcnow() > until_time:
                    self.remove_afk(user_id)
                    return None
        return afk_data

    def add_teach(self, trigger, response, taught_by):
        if 'teach_database' not in self.data:
            self.data['teach_database'] = {}
        
        # Check if trigger already exists and update it
        for tid, teach in self.data['teach_database'].items():
            if teach['trigger'].lower().strip() == trigger.lower().strip():
                self.data['teach_database'][tid]['response'] = response
                self.data['teach_database'][tid]['timestamp'] = datetime.utcnow().isoformat()
                self.save()
                return tid
        
        # Create new teach entry
        teach_id = str(len(self.data['teach_database']) + 1)
        self.data['teach_database'][teach_id] = {
            'trigger': trigger.lower().strip(),
            'response': response,
            'taught_by': taught_by,
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'response'
        }
        self.save()
        return teach_id
    
    def add_teach_advanced(self, trigger, response, taught_by, action_type='response'):
        if 'teach_database' not in self.data:
            self.data['teach_database'] = {}
        teach_id = str(len(self.data['teach_database']) + 1)
        self.data['teach_database'][teach_id] = {
            'trigger': trigger.lower(),
            'response': response,
            'taught_by': taught_by,
            'timestamp': datetime.utcnow().isoformat(),
            'type': action_type
        }
        self.save()
        return teach_id

    def remove_teach(self, teach_id):
        if 'teach_database' not in self.data:
            self.data['teach_database'] = {}
        if str(teach_id) in self.data['teach_database']:
            del self.data['teach_database'][str(teach_id)]
            self.save()
            return True
        return False
    
    def remove_teach_by_trigger(self, trigger):
        if 'teach_database' not in self.data:
            self.data['teach_database'] = {}
        
        trigger_lower = trigger.lower().strip()
        
        for teach_id, teach_data in list(self.data['teach_database'].items()):
            if teach_data['trigger'].lower().strip() == trigger_lower:
                del self.data['teach_database'][teach_id]
                self.save()
                return True
        
        return False

    def get_teach(self, trigger):
        if 'teach_database' not in self.data:
            self.data['teach_database'] = {}
        trigger_lower = trigger.lower()
        
        # First try exact match
        for teach_id, teach_data in self.data['teach_database'].items():
            if teach_data['trigger'].lower() == trigger_lower:
                return teach_data
        
        # Then try partial match (trigger contains the taught trigger)
        for teach_id, teach_data in self.data['teach_database'].items():
            if teach_data['trigger'].lower() in trigger_lower:
                return teach_data
        
        return None

    def get_all_teaches(self):
        if 'teach_database' not in self.data:
            self.data['teach_database'] = {}
        return self.data['teach_database']

    def save_ticket_transcript(self, ticket_id, data):
        if 'ticket_transcripts' not in self.data:
            self.data['ticket_transcripts'] = {}
        self.data['ticket_transcripts'][str(ticket_id)] = data
        self.save()

    def get_ticket_data(self, ticket_id):
        if 'tickets' not in self.data:
            self.data['tickets'] = {}
        return self.data['tickets'].get(str(ticket_id))

    def save_ticket_data(self, ticket_id, data):
        if 'tickets' not in self.data:
            self.data['tickets'] = {}
        self.data['tickets'][str(ticket_id)] = data
        self.save()

    # Counting System
    def get_counting_state(self, guild_id: int):
        if 'counting_state' not in self.data:
            self.data['counting_state'] = {}
        return self.data['counting_state'].get(str(guild_id), {'last_number': 0, 'last_user_id': None})

    def update_counting_state(self, guild_id: int, last_number: int, last_user_id: int):
        if 'counting_state' not in self.data:
            self.data['counting_state'] = {}
        self.data['counting_state'][str(guild_id)] = {
            'last_number': last_number,
            'last_user_id': last_user_id
        }
        self.save()

    def get_counting_mistakes(self, user_id: int):
        if 'counting_mistakes' not in self.data:
            self.data['counting_mistakes'] = {}
        return self.data['counting_mistakes'].get(str(user_id), 0)

    def increment_counting_mistakes(self, user_id: int):
        if 'counting_mistakes' not in self.data:
            self.data['counting_mistakes'] = {}
        current = self.data['counting_mistakes'].get(str(user_id), 0)
        self.data['counting_mistakes'][str(user_id)] = current + 1
        self.save()
        return current + 1

    def reset_counting_mistakes(self, user_id: int):
        if 'counting_mistakes' not in self.data:
            self.data['counting_mistakes'] = {}
        self.data['counting_mistakes'][str(user_id)] = 0
        self.save()

    def get_counting_cooldown(self, user_id: int):
        if 'counting_cooldowns' not in self.data:
            self.data['counting_cooldowns'] = {}
        return self.data['counting_cooldowns'].get(str(user_id))

    def set_counting_cooldown(self, user_id: int, cooldown_until: str):
        if 'counting_cooldowns' not in self.data:
            self.data['counting_cooldowns'] = {}
        self.data['counting_cooldowns'][str(user_id)] = {'cooldown_until': cooldown_until}
        self.save()

    def get_counting_lockout(self, user_id: int):
        if 'counting_lockouts' not in self.data:
            self.data['counting_lockouts'] = {}
        return self.data['counting_lockouts'].get(str(user_id))

    def set_counting_lockout(self, user_id: int, lockout_until: str):
        if 'counting_lockouts' not in self.data:
            self.data['counting_lockouts'] = {}
        self.data['counting_lockouts'][str(user_id)] = {'lockout_until': lockout_until}
        self.save()

    def clear_counting_lockout(self, user_id: int):
        if 'counting_lockouts' not in self.data:
            self.data['counting_lockouts'] = {}
        if str(user_id) in self.data['counting_lockouts']:
            del self.data['counting_lockouts'][str(user_id)]
            self.save()

    # Lock system for preventing race conditions
    def is_locked(self, lock_key: str):
        if 'locks' not in self.data:
            self.data['locks'] = {}
        lock_data = self.data['locks'].get(lock_key)
        if lock_data:
            expires_at = datetime.fromisoformat(lock_data['expires_at'])
            if datetime.utcnow() < expires_at:
                return True
            else:
                del self.data['locks'][lock_key]
                self.save()
        return False

    def set_lock(self, lock_key: str, duration_seconds: int):
        if 'locks' not in self.data:
            self.data['locks'] = {}
        expires_at = datetime.utcnow() + timedelta(seconds=duration_seconds)
        self.data['locks'][lock_key] = {'expires_at': expires_at.isoformat()}
        self.save()

    def release_lock(self, lock_key: str):
        if 'locks' not in self.data:
            self.data['locks'] = {}
        if lock_key in self.data['locks']:
            del self.data['locks'][lock_key]
            self.save()

    def get_open_ticket(self, guild_id: int, user_id: int):
        if 'tickets' not in self.data:
            self.data['tickets'] = []

        for ticket in self.data['tickets']:
            if ticket['guild_id'] == guild_id and ticket['user_id'] == user_id and ticket['status'] == 'open':
                return ticket
        return None

    def create_ticket(self, ticket_data):
        if 'tickets' not in self.data:
            self.data['tickets'] = []

        self.data['tickets'].append(ticket_data)
        self.save()

    def get_ticket_by_channel(self, channel_id: int):
        if 'tickets' not in self.data:
            return None

        for ticket in self.data['tickets']:
            if ticket['channel_id'] == channel_id:
                return ticket
        return None

    def update_ticket(self, channel_id: int, updates: dict):
        if 'tickets' not in self.data:
            return

        for ticket in self.data['tickets']:
            if ticket['channel_id'] == channel_id:
                ticket.update(updates)
                self.save()
                return

    def clear_afk(self, user_id: int):
        if 'afk_states' not in self.data:
            self.data['afk_states'] = {}
        if str(user_id) in self.data['afk_states']:
            del self.data['afk_states'][str(user_id)]
            self.save()
            return True
        return False
    
    def get_verification_data(self, user_id: int):
        if 'verifications' not in self.data:
            self.data['verifications'] = {}
        return self.data['verifications'].get(str(user_id))
    
    def set_verification_data(self, user_id: int, roblox_id: int, roblox_username: str):
        if 'verifications' not in self.data:
            self.data['verifications'] = {}
        self.data['verifications'][str(user_id)] = {
            'roblox_id': roblox_id,
            'roblox_username': roblox_username,
            'verified_at': datetime.utcnow().isoformat()
        }
        self.save()
    
    # Suggestion System
    def add_suggestion(self, user_id: int, content: str, channel_id: int, message_id: int):
        if 'suggestions' not in self.data:
            self.data['suggestions'] = {}
        suggestion_id = f"SUG-{len(self.data['suggestions']) + 1}"
        self.data['suggestions'][suggestion_id] = {
            'user_id': user_id,
            'content': content,
            'channel_id': channel_id,
            'message_id': message_id,
            'forwarded': False,
            'timestamp': datetime.utcnow().isoformat(),
            'reactions': 0
        }
        self.save()
        return suggestion_id
    
    def mark_suggestion_forwarded(self, suggestion_id: str):
        if 'suggestions' not in self.data:
            self.data['suggestions'] = {}
        if suggestion_id in self.data['suggestions']:
            self.data['suggestions'][suggestion_id]['forwarded'] = True
            self.save()
    
    def get_suggestion(self, suggestion_id: str):
        if 'suggestions' not in self.data:
            return None
        return self.data['suggestions'].get(suggestion_id)
    
    # Bug Report System
    def add_bug_report(self, user_id: int, content: str, channel_id: int, message_id: int):
        if 'bug_reports' not in self.data:
            self.data['bug_reports'] = {}
        bug_id = f"BUG-{len(self.data['bug_reports']) + 1}"
        self.data['bug_reports'][bug_id] = {
            'user_id': user_id,
            'content': content,
            'channel_id': channel_id,
            'message_id': message_id,
            'status': 'pending',
            'timestamp': datetime.utcnow().isoformat()
        }
        self.save()
        return bug_id
    
    def update_bug_status(self, bug_id: str, status: str):
        if 'bug_reports' not in self.data:
            self.data['bug_reports'] = {}
        if bug_id in self.data['bug_reports']:
            self.data['bug_reports'][bug_id]['status'] = status
            self.save()
            return True
        return False
    
    def get_bug_report(self, bug_id: str):
        if 'bug_reports' not in self.data:
            return None
        return self.data['bug_reports'].get(bug_id)
    
    def get_all_bug_reports(self):
        if 'bug_reports' not in self.data:
            self.data['bug_reports'] = {}
        return self.data['bug_reports']
    
    # Staff Notes System
    def add_staff_note(self, user_id: int, staff_id: int, note: str):
        if 'staff_notes' not in self.data:
            self.data['staff_notes'] = {}
        user_key = str(user_id)
        if user_key not in self.data['staff_notes']:
            self.data['staff_notes'][user_key] = []
        self.data['staff_notes'][user_key].append({
            'note': note,
            'staff_id': staff_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.save()
    
    def get_staff_notes(self, user_id: int):
        if 'staff_notes' not in self.data:
            self.data['staff_notes'] = {}
        return self.data['staff_notes'].get(str(user_id), [])
    
    # Moderation Cases System
    def add_mod_case(self, guild_id: int, user_id: int, moderator_id: int, action: str, reason: str):
        if 'moderation_cases' not in self.data:
            self.data['moderation_cases'] = {}
        case_id = len(self.data['moderation_cases']) + 1
        self.data['moderation_cases'][str(case_id)] = {
            'guild_id': guild_id,
            'user_id': user_id,
            'moderator_id': moderator_id,
            'action': action,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.save()
        return case_id
    
    def get_mod_case(self, case_id: int):
        if 'moderation_cases' not in self.data:
            return None
        return self.data['moderation_cases'].get(str(case_id))
    
    def edit_mod_case_reason(self, case_id: int, new_reason: str):
        if 'moderation_cases' not in self.data:
            return False
        if str(case_id) in self.data['moderation_cases']:
            self.data['moderation_cases'][str(case_id)]['reason'] = new_reason
            self.save()
            return True
        return False
    
    # Economy System
    def get_balance(self, guild_id: int, user_id: int):
        if 'economy' not in self.data:
            self.data['economy'] = {'balances': {}, 'transactions': [], 'shop_items': {}}
        key = f"{guild_id}:{user_id}"
        return self.data['economy']['balances'].get(key, 0)
    
    def add_balance(self, guild_id: int, user_id: int, amount: int):
        if 'economy' not in self.data:
            self.data['economy'] = {'balances': {}, 'transactions': [], 'shop_items': {}}
        key = f"{guild_id}:{user_id}"
        current = self.data['economy']['balances'].get(key, 0)
        self.data['economy']['balances'][key] = current + amount
        self.data['economy']['transactions'].append({
            'user_id': user_id,
            'guild_id': guild_id,
            'amount': amount,
            'type': 'add',
            'timestamp': datetime.utcnow().isoformat()
        })
        self.save()
        return self.data['economy']['balances'][key]
    
    def remove_balance(self, guild_id: int, user_id: int, amount: int):
        if 'economy' not in self.data:
            self.data['economy'] = {'balances': {}, 'transactions': [], 'shop_items': {}}
        key = f"{guild_id}:{user_id}"
        current = self.data['economy']['balances'].get(key, 0)
        if current < amount:
            return False
        self.data['economy']['balances'][key] = current - amount
        self.data['economy']['transactions'].append({
            'user_id': user_id,
            'guild_id': guild_id,
            'amount': amount,
            'type': 'remove',
            'timestamp': datetime.utcnow().isoformat()
        })
        self.save()
        return True
    
    # Voice Activity Tracking
    def add_voice_time(self, guild_id: int, user_id: int, minutes: int):
        if 'voice_activity' not in self.data:
            self.data['voice_activity'] = {}
        key = f"{guild_id}:{user_id}"
        if key not in self.data['voice_activity']:
            self.data['voice_activity'][key] = {'total_minutes': 0, 'last_joined': None}
        self.data['voice_activity'][key]['total_minutes'] += minutes
        self.save()
    
    def get_voice_time(self, guild_id: int, user_id: int):
        if 'voice_activity' not in self.data:
            return 0
        key = f"{guild_id}:{user_id}"
        return self.data['voice_activity'].get(key, {}).get('total_minutes', 0)
    
    # Deleted/Edited Messages for Snipe
    def add_deleted_message(self, message_data: dict):
        if 'deleted_messages' not in self.data:
            self.data['deleted_messages'] = []
        self.data['deleted_messages'].append(message_data)
        if len(self.data['deleted_messages']) > 100:
            self.data['deleted_messages'] = self.data['deleted_messages'][-100:]
        self.save()
    
    def get_deleted_messages(self, channel_id: int, limit: int = 5):
        if 'deleted_messages' not in self.data:
            return []
        messages = [m for m in self.data['deleted_messages'] if m['channel_id'] == channel_id]
        return messages[-limit:]
    
    def add_edited_message(self, message_data: dict):
        if 'edited_messages' not in self.data:
            self.data['edited_messages'] = []
        self.data['edited_messages'].append(message_data)
        if len(self.data['edited_messages']) > 100:
            self.data['edited_messages'] = self.data['edited_messages'][-100:]
        self.save()
    
    def get_edited_messages(self, channel_id: int, limit: int = 5):
        if 'edited_messages' not in self.data:
            return []
        messages = [m for m in self.data['edited_messages'] if m['channel_id'] == channel_id]
        return messages[-limit:]
    
    # Starboard System
    def add_to_starboard(self, message_id: int, channel_id: int, author_id: int, content: str, star_count: int):
        if 'starboard' not in self.data:
            self.data['starboard'] = {}
        self.data['starboard'][str(message_id)] = {
            'channel_id': channel_id,
            'author_id': author_id,
            'content': content,
            'star_count': star_count,
            'starred_at': datetime.utcnow().isoformat()
        }
        self.save()
    
    def update_starboard_count(self, message_id: int, star_count: int):
        if 'starboard' not in self.data:
            self.data['starboard'] = {}
        if str(message_id) in self.data['starboard']:
            self.data['starboard'][str(message_id)]['star_count'] = star_count
            self.save()
    
    def is_in_starboard(self, message_id: int):
        if 'starboard' not in self.data:
            return False
        return str(message_id) in self.data['starboard']
    
    # Reminder System
    def add_reminder(self, user_id: int, channel_id: int, message: str, remind_at: datetime):
        if 'reminders' not in self.data:
            self.data['reminders'] = {}
        reminder_id = str(len(self.data['reminders']) + 1)
        self.data['reminders'][reminder_id] = {
            'user_id': user_id,
            'channel_id': channel_id,
            'message': message,
            'remind_at': remind_at.isoformat(),
            'created_at': datetime.utcnow().isoformat(),
            'completed': False
        }
        self.save()
        return reminder_id
    
    def get_pending_reminders(self):
        if 'reminders' not in self.data:
            return []
        now = datetime.utcnow()
        pending = []
        for reminder_id, reminder in self.data['reminders'].items():
            if not reminder['completed']:
                remind_at = datetime.fromisoformat(reminder['remind_at'])
                if remind_at <= now:
                    pending.append({'id': reminder_id, **reminder})
        return pending
    
    def complete_reminder(self, reminder_id: str):
        if 'reminders' not in self.data:
            return False
        if reminder_id in self.data['reminders']:
            self.data['reminders'][reminder_id]['completed'] = True
            self.save()
            return True
        return False
    
    # User Contributions Tracking
    def increment_contribution(self, user_id: int, contribution_type: str):
        if 'user_contributions' not in self.data:
            self.data['user_contributions'] = {}
        user_key = str(user_id)
        if user_key not in self.data['user_contributions']:
            self.data['user_contributions'][user_key] = {
                'suggestions': 0,
                'bugs': 0,
                'helpful_messages': 0
            }
        if contribution_type in self.data['user_contributions'][user_key]:
            self.data['user_contributions'][user_key][contribution_type] += 1
        self.save()
    
    def get_contributions(self, user_id: int):
        if 'user_contributions' not in self.data:
            return {'suggestions': 0, 'bugs': 0, 'helpful_messages': 0}
        return self.data['user_contributions'].get(str(user_id), {'suggestions': 0, 'bugs': 0, 'helpful_messages': 0})
    
    def get_top_contributors(self, limit: int = 10):
        if 'user_contributions' not in self.data:
            return []
        sorted_contributors = sorted(
            self.data['user_contributions'].items(),
            key=lambda x: sum(x[1].values()),
            reverse=True
        )
        return sorted_contributors[:limit]
    
    # Analytics System
    def track_command_usage(self, command_name: str):
        if 'analytics' not in self.data:
            self.data['analytics'] = {'command_usage': {}, 'daily_messages': {}, 'ticket_stats': {}}
        if 'command_usage' not in self.data['analytics']:
            self.data['analytics']['command_usage'] = {}
        
        current_count = self.data['analytics']['command_usage'].get(command_name, 0)
        self.data['analytics']['command_usage'][command_name] = current_count + 1
        self.save()
    
    def track_daily_message(self, guild_id: int):
        if 'analytics' not in self.data:
            self.data['analytics'] = {'command_usage': {}, 'daily_messages': {}, 'ticket_stats': {}}
        if 'daily_messages' not in self.data['analytics']:
            self.data['analytics']['daily_messages'] = {}
        
        today = datetime.utcnow().date().isoformat()
        guild_key = str(guild_id)
        
        if guild_key not in self.data['analytics']['daily_messages']:
            self.data['analytics']['daily_messages'][guild_key] = {}
        
        current_count = self.data['analytics']['daily_messages'][guild_key].get(today, 0)
        self.data['analytics']['daily_messages'][guild_key][today] = current_count + 1
        self.save()
    
    # Counting Leaderboard
    def increment_count_contribution(self, user_id: int):
        if 'counting_contributions' not in self.data:
            self.data['counting_contributions'] = {}
        current = self.data['counting_contributions'].get(str(user_id), 0)
        self.data['counting_contributions'][str(user_id)] = current + 1
        self.save()
    
    def get_counting_leaderboard(self, limit: int = 10):
        if 'counting_contributions' not in self.data:
            return []
        sorted_users = sorted(
            self.data['counting_contributions'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_users[:limit]
    
    def reset_counting_contributions(self):
        if 'counting_contributions' not in self.data:
            self.data['counting_contributions'] = {}
        self.data['counting_contributions'] = {}
        self.save()
    
    # Auto-Moderation Logging
    def log_automod_action(self, guild_id: int, user_id: int, action: str, reason: str, duration = None):
        if 'automod_logs' not in self.data:
            self.data['automod_logs'] = []
        
        log_entry = {
            'guild_id': guild_id,
            'user_id': user_id,
            'action': action,
            'reason': reason,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.data['automod_logs'].append(log_entry)
        
        if len(self.data['automod_logs']) > 1000:
            self.data['automod_logs'] = self.data['automod_logs'][-1000:]
        
        self.save()
    
    # AI Memory System
    def add_ai_memory_message(self, user_id: int, username: str, channel_id: int, content: str, guild_id: int):
        if 'ai_memory' not in self.data:
            self.data['ai_memory'] = {'messages': [], 'summaries': {}, 'profiles': {}, 'last_cleanup': None}
        
        message_entry = {
            'user_id': user_id,
            'username': username,
            'channel_id': channel_id,
            'content': content,
            'guild_id': guild_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.data['ai_memory']['messages'].append(message_entry)
        
        max_messages = self.data['config'].get('ai_memory_max_messages', 10000)
        if len(self.data['ai_memory']['messages']) > max_messages:
            self.data['ai_memory']['messages'] = self.data['ai_memory']['messages'][-max_messages:]
        
        self.save()
    
    def get_ai_memory(self, limit: int = 100, user_id: int = None, channel_id: int = None):
        if 'ai_memory' not in self.data:
            return []
        
        messages = self.data['ai_memory']['messages']
        
        if user_id:
            messages = [m for m in messages if m['user_id'] == user_id]
        if channel_id:
            messages = [m for m in messages if m['channel_id'] == channel_id]
        
        return messages[-limit:]
    
    def cleanup_old_ai_memory(self):
        if 'ai_memory' not in self.data:
            return
        
        retention_days = self.data['config'].get('ai_memory_retention_days', 30)
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        self.data['ai_memory']['messages'] = [
            m for m in self.data['ai_memory']['messages']
            if datetime.fromisoformat(m['timestamp']) > cutoff_date
        ]
        
        self.data['ai_memory']['last_cleanup'] = datetime.utcnow().isoformat()
        self.save()
    
    def get_ai_ops_status(self):
        return self.data['config'].get('ai_ops_enabled', True)
    
    def set_ai_ops_status(self, enabled: bool):
        self.data['config']['ai_ops_enabled'] = enabled
        self.save()
    
    # Ticket AI State Management
    def set_ticket_ai_state(self, channel_id: int, state: dict):
        if 'ticket_ai_state' not in self.data:
            self.data['ticket_ai_state'] = {}
        self.data['ticket_ai_state'][str(channel_id)] = state
        self.save()
    
    def get_ticket_ai_state(self, channel_id: int):
        if 'ticket_ai_state' not in self.data:
            return None
        return self.data['ticket_ai_state'].get(str(channel_id))
    
    def remove_ticket_ai_state(self, channel_id: int):
        if 'ticket_ai_state' not in self.data:
            return
        if str(channel_id) in self.data['ticket_ai_state']:
            del self.data['ticket_ai_state'][str(channel_id)]
            self.save()