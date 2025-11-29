"""
Ticket AI Configuration
Comprehensive configuration for AI-powered ticket system
Based on Spiritual Battlegrounds AI instruction document
"""

class TicketAIConfig:
    # Channel IDs (Reference Map)
    CHANNELS = {
        'verification': 1423669807521202247,
        'rules': 1383266456745017536,
        'welcome': 1409299795318804612,
        'information': 1415330559974183024,
        'faq': 1409301002070397120,
        'announcements': 1409302679510843493,
        'sub_announcements': 1409303086488359013,
        'update_log': 1409303699813171200,
        'game_polls': 1409304343248765149,
        'sneak_peeks': 1409304494503886980,
        'invite_events': 1409304574413508659,
        'boost_channel': 1409304963749773442,
        'links': 1409305489266966658,
        'partnership_rules': 1426708847145521223,
        'content_announcements': 1412775408482521249,
        'content_rules': 1412778118615273604,
        'event_rules': 1412929027202617374,
        'event_announcements': 1417829107554582648,
        'pickups_events': 1409306874817282078,
        'artwork_events': 1409307102173728862,
        'giveaway_events': 1409307003834208286,
        'video_events': 1409307220545634314,
        'dev_events': 1409307679251370044,
        'support_category': 1389999965979283608,
        'suggestions': 1409310962103877752,
        'bug_reports': 1409311252400050196,
        'ticket_logs': 1420538005936013403
    }
    
    # Role IDs
    ROLES = {
        'ticket_manager': 1383270362707656774,
        'appeal_manager': 1423157373295525979,
        'owner_1': 523693281541095424,
        'owner_2': 1327460512858116154
    }
    
    # Ticket Categories
    CATEGORIES = {
        'report': 1436498495153635512,
        'appeal': 1436498528544227428,
        'support': 1436498409153626213,
        'cc': 1436498445216256031  # Content Creator
    }
    
    # Ticket Type Configuration
    TICKET_TYPES = {
        'report': {
            'emoji': '🔴',
            'name_format': '《🔴》・{username}-report-player',
            'category_id': 1436498495153635512,
            'allowed': True,
            'label': 'User Report'
        },
        'appeal': {
            'emoji': '🟡',
            'name_format': '《🟡》・{username}-warning-appeal',
            'category_id': 1436498528544227428,
            'allowed': True,
            'label': 'Warning Appeal'
        },
        'bug': {
            'emoji': '🟠',
            'name_format': '《🟠》・{username}-bug-report',
            'category_id': 1436498409153626213,
            'allowed': True,
            'label': 'Bug Report'
        },
        'cc': {
            'emoji': '🟣',
            'name_format': '《🟣》・{username}-creator-request',
            'category_id': 1436498445216256031,
            'allowed': True,
            'label': 'Content Creator Request'
        },
        'support': {
            'emoji': '🔵',
            'name_format': '《🔵》・{username}-support',
            'category_id': 1436498409153626213,
            'allowed': True,
            'label': 'Other Inquiry'
        }
    }
    
    # Allowed Topics
    ALLOWED_TOPICS = [
        'user reports',
        'staff reports',
        'bug reports',
        'warning appeals',
        'content creator requests',
        'other server-related inquiries'
    ]
    
    # Disallowed Topics
    DISALLOWED_TOPICS = {
        'game_questions': {
            'keywords': ['how to play', 'game help', 'what is', 'how does', 'game question'],
            'redirect': f"Please ask game questions in <#{CHANNELS['faq']}> or <#{CHANNELS['information']}>."
        },
        'suggestions': {
            'keywords': ['suggest', 'suggestion', 'feature request', 'add this'],
            'redirect': f"Please submit suggestions in <#{CHANNELS['suggestions']}>."
        },
        'role_requests': {
            'keywords': ['give me', 'can i have', 'role request', 'staff role', 'tester role', 'helper role', 'moderator'],
            'redirect': "Role requests cannot be processed through tickets. Please contact server administrators directly."
        }
    }
    
    # AI Stop Keywords
    STOP_KEYWORDS = [
        'stop talking',
        'can you stop responding',
        'stop responding',
        'please stop',
        'you can stop',
        'shut up'
    ]
    
    # Human Request Keywords
    HUMAN_REQUEST_KEYWORDS = [
        'i want support from staff',
        "i don't want ai",
        'can i get a real person',
        'i would like support',
        'human support',
        'real person',
        'staff help',
        'actual staff'
    ]
    
    # Disrespect Keywords (for detection)
    DISRESPECT_KEYWORDS = [
        'stupid',
        'dumb',
        'useless',
        'trash',
        'garbage',
        'idiot',
        'fuck',
        'shit',
        'ass',
        'bitch'
    ]
    
    # AI Resume Keywords
    RESUME_KEYWORDS = [
        'you can reply now',
        'ai reply',
        'continue',
        'keep going',
        '@bot'
    ]
    
    # Close Request Keywords (must be explicit to avoid false positives)
    CLOSE_REQUEST_KEYWORDS = [
        'close the ticket',
        'close this ticket',
        'please close the ticket',
        'please close this ticket',
        'you can close the ticket',
        'you can close this ticket',
        'we can close the ticket',
        'we can close this ticket',
        'i\'m done here',
        'im done here',
        'i\'m done with this',
        'im done with this',
        'that\'s all i needed',
        'thats all i needed',
        'that\'s all for now',
        'thats all for now',
        'thanks, close this',
        'thank you, close this',
        'thanks close this',
        'thank you close this'
    ]
    
    # System Messages
    MESSAGES = {
        'welcome': "Hello! I've claimed your ticket and will assist you. Please describe your issue in detail.",
        'creation_failed': "Your ticket could not be created. Please contact an administrator.",
        'human_handoff': "Understood. I'll notify a Ticket Manager to take over.",
        'stopped': "I've stopped responding. Ping me or say 'you can reply now' if you need me again.",
        'disrespect_warning': "Please maintain a respectful tone. Continued disrespectful behavior may result in ticket escalation to staff.",
        'disrespect_escalation': "user is being uncooperative.",
        'another_user_joined': "Another user has joined the conversation. I'll pause my responses unless the ticket creator asks me to continue.",
        'topic_disallowed': "This ticket type is not supported through the ticket system. {redirect}",
        'evidence_request': "To help resolve this issue, please provide:\n• Screenshots (if applicable)\n• User IDs or usernames\n• Detailed description of what happened",
        'cc_redirect': f"For Content Creator requests, you may also DM the server owners:\n• <@{ROLES['owner_1']}>\n• <@{ROLES['owner_2']}>",
        'closing': "This ticket will now be closed. Thank you for contacting support!",
        'neutral_stance': "I remain neutral in this matter. My role is to gather information for staff review."
    }
    
    # AI Behavioral Rules
    BEHAVIOR = {
        'professional': True,
        'no_sarcasm': True,
        'no_trolling': True,
        'concise': True,
        'patient': True,
        'stop_on_command': True,
        'stop_when_others_speak': True,
        'auto_claim': True,
        'max_warnings': 1
    }
    
    @classmethod
    def get_ticket_manager_ping(cls):
        """Get the Ticket Manager role mention"""
        return f"<@&{cls.ROLES['ticket_manager']}>"
    
    @classmethod
    def is_stop_command(cls, message):
        """Check if message contains stop command"""
        msg_lower = message.lower().strip()
        return any(keyword in msg_lower for keyword in cls.STOP_KEYWORDS)
    
    @classmethod
    def is_human_request(cls, message):
        """Check if message requests human support"""
        msg_lower = message.lower().strip()
        return any(keyword in msg_lower for keyword in cls.HUMAN_REQUEST_KEYWORDS)
    
    @classmethod
    def is_disrespectful(cls, message):
        """Check if message contains disrespectful language"""
        msg_lower = message.lower().strip()
        return any(keyword in msg_lower for keyword in cls.DISRESPECT_KEYWORDS)
    
    @classmethod
    def is_resume_command(cls, message):
        """Check if message asks AI to resume"""
        msg_lower = message.lower().strip()
        return any(keyword in msg_lower for keyword in cls.RESUME_KEYWORDS)
    
    @classmethod
    def check_disallowed_topic(cls, message):
        """Check if message contains disallowed topic keywords"""
        msg_lower = message.lower().strip()
        for topic, data in cls.DISALLOWED_TOPICS.items():
            if any(keyword in msg_lower for keyword in data['keywords']):
                return data['redirect']
        return None
    
    @classmethod
    def is_close_request(cls, message):
        """Check if message requests ticket closure"""
        msg_lower = message.lower().strip()
        return any(keyword in msg_lower for keyword in cls.CLOSE_REQUEST_KEYWORDS)
