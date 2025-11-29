from sqlalchemy.orm import Session
from models import (
    TeachEntry, Ticket, TicketMessage, AuditEvent, ShiftSession,
    Promotion, Infraction, BugReport, IndexedChannel, IndexedRole,
    IndexedMember, PinnedMessage, AIPrompt, UserLevel,
    TicketStatus, TicketType, AuditAction
)
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import discord

class AuditLogger:
    """Centralized audit logging service"""
    
    @staticmethod
    def log(db: Session, guild_id: int, action_type: AuditAction,
            actor_id: int, actor_name: str, target_id: Optional[int] = None,
            target_name: Optional[str] = None, source_system: str = 'bot',
            metadata: Optional[Dict] = None, description: Optional[str] = None):
        """Log an audit event"""
        event = AuditEvent(
            guild_id=guild_id,
            action_type=action_type,
            actor_id=actor_id,
            actor_name=actor_name,
            target_id=target_id,
            target_name=target_name,
            source_system=source_system,
            metadata=metadata or {},
            description=description
        )
        db.add(event)
        db.commit()
        return event
    
    @staticmethod
    def get_recent(db: Session, guild_id: int, limit: int = 50,
                   action_type: Optional[AuditAction] = None,
                   user_id: Optional[int] = None):
        """Get recent audit events"""
        query = db.query(AuditEvent).filter(AuditEvent.guild_id == guild_id)
        
        if action_type:
            query = query.filter(AuditEvent.action_type == action_type)
        
        if user_id:
            query = query.filter((AuditEvent.actor_id == user_id) | (AuditEvent.target_id == user_id))
        
        return query.order_by(AuditEvent.created_at.desc()).limit(limit).all()


class TeachService:
    """Service for managing taught AI responses"""
    
    @staticmethod
    def add_teach(db: Session, trigger: str, response: str, author_id: int,
                  author_name: str, guild_id: int, priority: int = 0):
        """Add a new taught response"""
        # Check if trigger already exists
        existing = db.query(TeachEntry).filter(
            TeachEntry.trigger == trigger,
            TeachEntry.guild_id == guild_id,
            TeachEntry.is_active == True
        ).first()
        
        if existing:
            # Update existing
            existing.response = response
            existing.priority = priority
            existing.updated_at = datetime.utcnow()
            db.commit()
            
            # Log audit
            AuditLogger.log(
                db, guild_id, AuditAction.TEACH_ADD,
                author_id, author_name,
                description=f"Updated teach: {trigger}"
            )
            
            return existing, False  # False = not new
        else:
            # Create new
            teach = TeachEntry(
                trigger=trigger,
                response=response,
                author_id=author_id,
                author_name=author_name,
                guild_id=guild_id,
                priority=priority
            )
            db.add(teach)
            db.commit()
            
            # Log audit
            AuditLogger.log(
                db, guild_id, AuditAction.TEACH_ADD,
                author_id, author_name,
                description=f"Added teach: {trigger}"
            )
            
            return teach, True  # True = new
    
    @staticmethod
    def remove_teach(db: Session, teach_id: int, remover_id: int, remover_name: str):
        """Remove a taught response"""
        teach = db.query(TeachEntry).filter(TeachEntry.id == teach_id).first()
        if teach:
            teach.is_active = False
            db.commit()
            
            # Log audit
            AuditLogger.log(
                db, teach.guild_id, AuditAction.TEACH_REMOVE,
                remover_id, remover_name,
                description=f"Removed teach: {teach.trigger}"
            )
            return True
        return False
    
    @staticmethod
    def find_response(db: Session, message: str, guild_id: int) -> Optional[TeachEntry]:
        """Find a taught response matching the message (prioritized)"""
        # Exact match first, ordered by priority
        teaches = db.query(TeachEntry).filter(
            TeachEntry.guild_id == guild_id,
            TeachEntry.is_active == True
        ).order_by(TeachEntry.priority.desc()).all()
        
        message_lower = message.lower().strip()
        
        for teach in teaches:
            if teach.trigger.lower() in message_lower or message_lower in teach.trigger.lower():
                teach.increment_usage()
                db.commit()
                return teach
        
        return None
    
    @staticmethod
    def list_teaches(db: Session, guild_id: int, page: int = 1, per_page: int = 20):
        """List all taught responses with pagination"""
        query = db.query(TeachEntry).filter(
            TeachEntry.guild_id == guild_id,
            TeachEntry.is_active == True
        ).order_by(TeachEntry.usage_count.desc())
        
        total = query.count()
        teaches = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return teaches, total
    
    @staticmethod
    def export_teaches(db: Session, guild_id: int):
        """Export all taught responses"""
        teaches = db.query(TeachEntry).filter(
            TeachEntry.guild_id == guild_id,
            TeachEntry.is_active == True
        ).all()
        
        return [
            {
                'id': t.id,
                'trigger': t.trigger,
                'response': t.response,
                'author': t.author_name,
                'usage_count': t.usage_count,
                'created_at': t.created_at.isoformat()
            }
            for t in teaches
        ]


class TicketService:
    """Service for managing tickets"""
    
    @staticmethod
    def create_ticket(db: Session, guild_id: int, channel_id: int,
                      creator_id: int, creator_name: str, ticket_type: TicketType,
                      initial_reason: str):
        """Create a new ticket"""
        ticket = Ticket(
            guild_id=guild_id,
            channel_id=channel_id,
            creator_id=creator_id,
            creator_name=creator_name,
            ticket_type=ticket_type,
            initial_reason=initial_reason,
            status=TicketStatus.OPEN
        )
        db.add(ticket)
        db.commit()
        
        # Log audit
        AuditLogger.log(
            db, guild_id, AuditAction.TICKET_CREATE,
            creator_id, creator_name,
            target_id=channel_id,
            target_name=f"{ticket_type.value} ticket",
            metadata={'ticket_id': ticket.id, 'reason': initial_reason}
        )
        
        return ticket
    
    @staticmethod
    def has_open_ticket(db: Session, user_id: int, guild_id: int, ticket_type: TicketType = None) -> bool:
        """Check if user has an open ticket"""
        query = db.query(Ticket).filter(
            Ticket.creator_id == user_id,
            Ticket.guild_id == guild_id,
            Ticket.status != TicketStatus.CLOSED
        )
        
        if ticket_type:
            query = query.filter(Ticket.ticket_type == ticket_type)
        
        return query.first() is not None
    
    @staticmethod
    def claim_ticket(db: Session, ticket_id: int, claimer_id: int, claimer_name: str):
        """Claim a ticket"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            ticket.status = TicketStatus.CLAIMED
            ticket.claimed_by_id = claimer_id
            ticket.claimed_by_name = claimer_name
            ticket.claimed_at = datetime.utcnow()
            db.commit()
            
            # Log audit
            AuditLogger.log(
                db, ticket.guild_id, AuditAction.TICKET_CLAIM,
                claimer_id, claimer_name,
                target_id=ticket.creator_id,
                target_name=ticket.creator_name,
                metadata={'ticket_id': ticket.id}
            )
            
            return ticket
        return None
    
    @staticmethod
    def unclaim_ticket(db: Session, ticket_id: int, unclaimer_id: int, unclaimer_name: str):
        """Unclaim a ticket"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            ticket.status = TicketStatus.OPEN
            ticket.claimed_by_id = None
            ticket.claimed_by_name = None
            ticket.claimed_at = None
            db.commit()
            
            # Log audit
            AuditLogger.log(
                db, ticket.guild_id, AuditAction.TICKET_UNCLAIM,
                unclaimer_id, unclaimer_name,
                metadata={'ticket_id': ticket.id}
            )
            
            return ticket
        return None
    
    @staticmethod
    def close_ticket(db: Session, ticket_id: int, closer_id: int, closer_name: str,
                     close_reason: str, transcript: str):
        """Close a ticket"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            ticket.status = TicketStatus.CLOSED
            ticket.closed_by_id = closer_id
            ticket.closed_by_name = closer_name
            ticket.closed_at = datetime.utcnow()
            ticket.close_reason = close_reason
            ticket.transcript = transcript
            db.commit()
            
            # Log audit
            AuditLogger.log(
                db, ticket.guild_id, AuditAction.TICKET_CLOSE,
                closer_id, closer_name,
                target_id=ticket.creator_id,
                target_name=ticket.creator_name,
                metadata={'ticket_id': ticket.id, 'reason': close_reason}
            )
            
            return ticket
        return None
    
    @staticmethod
    def add_message(db: Session, ticket_id: int, message_id: int,
                    author_id: int, author_name: str, content: str,
                    attachments: list = None, embeds: list = None, is_bot: bool = False):
        """Add a message to ticket conversation history"""
        ticket_msg = TicketMessage(
            ticket_id=ticket_id,
            message_id=message_id,
            author_id=author_id,
            author_name=author_name,
            content=content,
            attachments=attachments or [],
            embeds=embeds or [],
            is_bot=is_bot
        )
        db.add(ticket_msg)
        db.commit()
        return ticket_msg
    
    @staticmethod
    def get_conversation_history(db: Session, ticket_id: int, limit: int = 50):
        """Get recent conversation history for a ticket"""
        return db.query(TicketMessage).filter(
            TicketMessage.ticket_id == ticket_id
        ).order_by(TicketMessage.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_ticket_by_channel(db: Session, channel_id: int):
        """Get ticket by channel ID"""
        return db.query(Ticket).filter(Ticket.channel_id == channel_id).first()


class ShiftService:
    """Service for managing staff shifts"""
    
    @staticmethod
    def start_shift(db: Session, user_id: int, username: str, guild_id: int,
                    expected_duration_minutes: Optional[int] = None):
        """Start a new shift"""
        # Check for active shifts
        active = db.query(ShiftSession).filter(
            ShiftSession.user_id == user_id,
            ShiftSession.guild_id == guild_id,
            ShiftSession.is_active == True
        ).first()
        
        if active:
            return None, "You already have an active shift!"
        
        shift = ShiftSession(
            user_id=user_id,
            username=username,
            guild_id=guild_id,
            start_time=datetime.utcnow(),
            expected_duration_minutes=expected_duration_minutes
        )
        db.add(shift)
        db.commit()
        
        # Log audit
        AuditLogger.log(
            db, guild_id, AuditAction.SHIFT_START,
            user_id, username,
            description=f"Started shift (expected: {expected_duration_minutes or 'N/A'} min)"
        )
        
        return shift, None
    
    @staticmethod
    def end_shift(db: Session, user_id: int, username: str, guild_id: int,
                  tickets_handled: int = 0, tasks_performed: str = None, notes: str = None):
        """End the current shift"""
        shift = db.query(ShiftSession).filter(
            ShiftSession.user_id == user_id,
            ShiftSession.guild_id == guild_id,
            ShiftSession.is_active == True
        ).first()
        
        if not shift:
            return None, "You don't have an active shift!"
        
        shift.end_time = datetime.utcnow()
        shift.is_active = False
        shift.tickets_handled = tickets_handled
        shift.tasks_performed = tasks_performed
        shift.notes = notes
        
        # Calculate actual duration
        duration = shift.end_time - shift.start_time
        shift.actual_duration_minutes = int(duration.total_seconds() / 60)
        
        db.commit()
        
        # Log audit
        AuditLogger.log(
            db, guild_id, AuditAction.SHIFT_END,
            user_id, username,
            description=f"Ended shift (duration: {shift.actual_duration_minutes} min)"
        )
        
        return shift, None
    
    @staticmethod
    def get_active_shift(db: Session, user_id: int, guild_id: int):
        """Get user's active shift"""
        return db.query(ShiftSession).filter(
            ShiftSession.user_id == user_id,
            ShiftSession.guild_id == guild_id,
            ShiftSession.is_active == True
        ).first()


class PromotionService:
    """Service for managing promotions"""
    
    @staticmethod
    def record_promotion(db: Session, user_id: int, username: str,
                        promoter_id: int, promoter_name: str,
                        old_role_id: Optional[int], old_role_name: Optional[str],
                        new_role_id: int, new_role_name: str,
                        guild_id: int, notes: Optional[str] = None):
        """Record a promotion"""
        promotion = Promotion(
            user_id=user_id,
            username=username,
            promoter_id=promoter_id,
            promoter_name=promoter_name,
            old_role_id=old_role_id,
            old_role_name=old_role_name,
            new_role_id=new_role_id,
            new_role_name=new_role_name,
            guild_id=guild_id,
            notes=notes
        )
        db.add(promotion)
        db.commit()
        
        # Log audit
        AuditLogger.log(
            db, guild_id, AuditAction.PROMOTION,
            promoter_id, promoter_name,
            target_id=user_id,
            target_name=username,
            metadata={'from_role': old_role_name, 'to_role': new_role_name}
        )
        
        return promotion


class InfractionService:
    """Service for managing infractions"""
    
    @staticmethod
    def record_infraction(db: Session, user_id: int, username: str,
                         issuer_id: int, issuer_name: str,
                         guild_id: int, reason: str, infraction_type: str = 'warning'):
        """Record an infraction"""
        infraction = Infraction(
            user_id=user_id,
            username=username,
            issuer_id=issuer_id,
            issuer_name=issuer_name,
            guild_id=guild_id,
            reason=reason,
            infraction_type=infraction_type
        )
        db.add(infraction)
        db.commit()
        
        # Log audit
        AuditLogger.log(
            db, guild_id, AuditAction.INFRACTION,
            issuer_id, issuer_name,
            target_id=user_id,
            target_name=username,
            metadata={'type': infraction_type, 'reason': reason}
        )
        
        return infraction
    
    @staticmethod
    def get_user_infractions(db: Session, user_id: int, guild_id: int, active_only: bool = True):
        """Get user's infractions"""
        query = db.query(Infraction).filter(
            Infraction.user_id == user_id,
            Infraction.guild_id == guild_id
        )
        
        if active_only:
            query = query.filter(Infraction.is_active == True)
        
        return query.order_by(Infraction.created_at.desc()).all()
    
    @staticmethod
    def get_strike_count(db: Session, user_id: int, guild_id: int):
        """Get user's active strike count"""
        return db.query(Infraction).filter(
            Infraction.user_id == user_id,
            Infraction.guild_id == guild_id,
            Infraction.is_active == True
        ).count()


class BugReportService:
    """Service for managing bug reports"""
    
    @staticmethod
    def submit_bug(db: Session, reporter_id: int, reporter_name: str,
                   guild_id: int, description: str, priority: str = 'medium',
                   attachments: list = None):
        """Submit a bug report"""
        bug = BugReport(
            reporter_id=reporter_id,
            reporter_name=reporter_name,
            guild_id=guild_id,
            description=description,
            priority=priority,
            attachments=attachments or []
        )
        db.add(bug)
        db.commit()
        return bug
    
    @staticmethod
    def get_recent_bugs(db: Session, guild_id: int, limit: int = 20):
        """Get recent bug reports"""
        return db.query(BugReport).filter(
            BugReport.guild_id == guild_id
        ).order_by(BugReport.created_at.desc()).limit(limit).all()
