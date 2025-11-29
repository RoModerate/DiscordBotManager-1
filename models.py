from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Boolean, Text, DateTime, JSON, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
import os

Base = declarative_base()

class TicketStatus(enum.Enum):
    OPEN = "open"
    CLAIMED = "claimed"
    CLOSED = "closed"

class TicketType(enum.Enum):
    SUPPORT = "support"
    CC = "cc"
    REPORT = "report"
    APPEAL = "appeal"

class AuditAction(enum.Enum):
    # Moderation
    WARN = "warn"
    MUTE = "mute"
    UNMUTE = "unmute"
    KICK = "kick"
    BAN = "ban"
    UNBAN = "unban"
    # Tickets
    TICKET_CREATE = "ticket_create"
    TICKET_CLAIM = "ticket_claim"
    TICKET_UNCLAIM = "ticket_unclaim"
    TICKET_CLOSE = "ticket_close"
    # AI Teach
    TEACH_ADD = "teach_add"
    TEACH_REMOVE = "teach_remove"
    # Role Changes
    ROLE_ADD = "role_add"
    ROLE_REMOVE = "role_remove"
    # Staff
    SHIFT_START = "shift_start"
    SHIFT_END = "shift_end"
    PROMOTION = "promotion"
    INFRACTION = "infraction"
    # Channel
    CHANNEL_CREATE = "channel_create"
    CHANNEL_DELETE = "channel_delete"
    MESSAGE_DELETE = "message_delete"

# Server Index Models
class IndexedChannel(Base):
    __tablename__ = 'indexed_channels'
    
    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    channel_type = Column(String(50))
    category_id = Column(BigInteger)
    category_name = Column(String(100))
    position = Column(Integer)
    permission_overwrites = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IndexedRole(Base):
    __tablename__ = 'indexed_roles'
    
    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(20))
    position = Column(Integer)
    permissions = Column(BigInteger)
    mentionable = Column(Boolean, default=False)
    hoist = Column(Boolean, default=False)
    member_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IndexedMember(Base):
    __tablename__ = 'indexed_members'
    
    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    display_name = Column(String(100))
    discriminator = Column(String(10))
    is_bot = Column(Boolean, default=False)
    roblox_username = Column(String(100))
    roles = Column(JSON)  # List of role IDs
    joined_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PinnedMessage(Base):
    __tablename__ = 'pinned_messages'
    
    id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger, nullable=False, index=True)
    content = Column(Text)
    author_id = Column(BigInteger)
    author_name = Column(String(100))
    created_at = Column(DateTime)
    pinned_at = Column(DateTime, default=datetime.utcnow)

# Teach System Models
class TeachEntry(Base):
    __tablename__ = 'teach_entries'
    
    id = Column(Integer, primary_key=True)
    trigger = Column(String(500), nullable=False, index=True)
    response = Column(Text, nullable=False)
    author_id = Column(BigInteger, nullable=False)
    author_name = Column(String(100))
    guild_id = Column(BigInteger, nullable=False, index=True)
    priority = Column(Integer, default=0)  # Higher = more priority
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def increment_usage(self):
        self.usage_count += 1

# Ticket System Models
class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    channel_id = Column(BigInteger, unique=True, nullable=False)
    creator_id = Column(BigInteger, nullable=False, index=True)
    creator_name = Column(String(100))
    ticket_type = Column(SQLEnum(TicketType), nullable=False)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN)
    claimed_by_id = Column(BigInteger)
    claimed_by_name = Column(String(100))
    claimed_at = Column(DateTime)
    closed_by_id = Column(BigInteger)
    closed_by_name = Column(String(100))
    closed_at = Column(DateTime)
    close_reason = Column(Text)
    initial_reason = Column(Text)
    transcript = Column(Text)
    metadata = Column(JSON)  # Additional ticket-specific data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")

class TicketMessage(Base):
    __tablename__ = 'ticket_messages'
    
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'), nullable=False, index=True)
    message_id = Column(BigInteger, unique=True)
    author_id = Column(BigInteger, nullable=False)
    author_name = Column(String(100))
    content = Column(Text)
    attachments = Column(JSON)  # URLs and filenames
    embeds = Column(JSON)  # Embed data
    is_bot = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ticket = relationship("Ticket", back_populates="messages")

class AIPrompt(Base):
    __tablename__ = 'ai_prompts'
    
    id = Column(Integer, primary_key=True)
    ticket_type = Column(SQLEnum(TicketType), unique=True, nullable=False)
    prompt_template = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Shift System Models
class ShiftSession(Base):
    __tablename__ = 'shift_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(100))
    guild_id = Column(BigInteger, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    expected_duration_minutes = Column(Integer)
    actual_duration_minutes = Column(Integer)
    tickets_handled = Column(Integer, default=0)
    tasks_performed = Column(Text)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Promotion & Infraction Models
class Promotion(Base):
    __tablename__ = 'promotions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(100))
    promoter_id = Column(BigInteger, nullable=False)
    promoter_name = Column(String(100))
    old_role_id = Column(BigInteger)
    old_role_name = Column(String(100))
    new_role_id = Column(BigInteger, nullable=False)
    new_role_name = Column(String(100), nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Infraction(Base):
    __tablename__ = 'infractions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(100))
    issuer_id = Column(BigInteger, nullable=False)
    issuer_name = Column(String(100))
    guild_id = Column(BigInteger, nullable=False)
    reason = Column(Text, nullable=False)
    infraction_type = Column(String(50))  # warning, strike, etc
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Audit Log Model
class AuditEvent(Base):
    __tablename__ = 'audit_events'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    action_type = Column(SQLEnum(AuditAction), nullable=False, index=True)
    actor_id = Column(BigInteger, nullable=False)
    actor_name = Column(String(100))
    target_id = Column(BigInteger)
    target_name = Column(String(100))
    source_system = Column(String(50))  # 'bot', 'web_dashboard', 'discord'
    metadata = Column(JSON)  # Flexible data storage
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# Leveling System
class UserLevel(Base):
    __tablename__ = 'user_levels'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=False)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    last_xp_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Bug Reports
class BugReport(Base):
    __tablename__ = 'bug_reports'
    
    id = Column(Integer, primary_key=True)
    reporter_id = Column(BigInteger, nullable=False, index=True)
    reporter_name = Column(String(100))
    guild_id = Column(BigInteger, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default='medium')
    status = Column(String(20), default='open')
    attachments = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    resolved_by_id = Column(BigInteger)

# Database Engine and Session
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot.db')

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def get_session():
    """Get a new database session"""
    return SessionLocal()
