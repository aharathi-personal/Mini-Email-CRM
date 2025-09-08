"""
Campaign data model for Mini Email CRM
Manages email campaign state and coordination across screens
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .contact import Contact
from .email_template import EmailTemplate


class CampaignStatus(Enum):
    """Campaign status tracking for UI state management"""
    DRAFT = "draft"                    # Initial state
    CONTACTS_LOADED = "contacts_loaded"   # CSV uploaded and validated
    TEMPLATE_READY = "template_ready"     # Email composed
    READY_TO_SEND = "ready_to_send"      # Previewed and approved
    SENDING = "sending"                   # Currently sending emails  
    PAUSED = "paused"                     # Sending paused by user
    COMPLETED = "completed"               # All emails processed
    CANCELLED = "cancelled"               # Cancelled by user
    ERROR = "error"                       # Fatal error occurred


class EmailStatus(Enum):
    """Individual email sending status"""
    PENDING = "pending"
    SENDING = "sending" 
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class EmailResult:
    """Individual email sending result"""
    contact: Contact
    status: EmailStatus
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def is_successful(self) -> bool:
        """Check if email was sent successfully"""
        return self.status == EmailStatus.SENT
    
    def is_failed(self) -> bool:
        """Check if email failed permanently"""
        return self.status == EmailStatus.FAILED


@dataclass  
class Campaign:
    """
    Campaign model for coordinating the entire email sending process
    Manages state across all 4 screens: Upload → Compose → Preview → Progress
    """
    
    # Required identification
    name: str
    campaign_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    # Campaign data
    contacts: List[Contact] = field(default_factory=list)
    email_template: Optional[EmailTemplate] = None
    
    # State management
    status: CampaignStatus = CampaignStatus.DRAFT
    current_screen: str = "upload"  # upload, compose, preview, progress, complete
    
    # Progress tracking
    email_results: List[EmailResult] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    
    # Settings
    send_delay: float = 2.0  # Seconds between emails
    max_retries: int = 3
    batch_size: int = 50
    
    # File information
    source_file: Optional[str] = None
    file_size: Optional[int] = None
    
    def __post_init__(self):
        """Initialize campaign after creation"""
        if not self.name or not self.name.strip():
            raise ValueError("Campaign name is required")
    
    # === Contact Management ===
    
    def add_contacts(self, contacts: List[Contact]) -> None:
        """Add contacts to campaign with validation"""
        if not contacts:
            raise ValueError("No contacts provided")
        
        # Validate all contacts before adding
        for contact in contacts:
            validation_errors = contact.validate()
            if validation_errors:
                raise ValueError(f"Invalid contact {contact.email}: {', '.join(validation_errors)}")
        
        self.contacts = contacts
        self.status = CampaignStatus.CONTACTS_LOADED
        self._initialize_email_results()
    
    def _initialize_email_results(self) -> None:
        """Initialize email results for all contacts"""
        self.email_results = [
            EmailResult(contact=contact, status=EmailStatus.PENDING)
            for contact in self.contacts
        ]
    
    def get_contact_count(self) -> int:
        """Get total number of contacts"""
        return len(self.contacts)
    
    def get_valid_contacts(self) -> List[Contact]:
        """Get all valid contacts (with successful validation)"""
        return [contact for contact in self.contacts if not contact.validate()]
    
    def get_invalid_contacts(self) -> List[Contact]:
        """Get contacts with validation errors"""
        return [contact for contact in self.contacts if contact.validate()]
    
    # === Template Management ===
    
    def set_email_template(self, template: EmailTemplate) -> None:
        """Set email template with validation"""
        if not template:
            raise ValueError("Email template is required")
        
        validation_errors = template.validate()
        if validation_errors:
            raise ValueError(f"Invalid template: {', '.join(validation_errors)}")
        
        self.email_template = template
        self.status = CampaignStatus.TEMPLATE_READY
    
    def is_ready_to_send(self) -> bool:
        """Check if campaign is ready for sending"""
        return (
            len(self.contacts) > 0 and
            self.email_template is not None and
            self.status in [CampaignStatus.TEMPLATE_READY, CampaignStatus.READY_TO_SEND]
        )
    
    def mark_ready_for_sending(self) -> None:
        """Mark campaign as ready after preview approval"""
        if not self.is_ready_to_send():
            raise ValueError("Campaign is not ready for sending")
        self.status = CampaignStatus.READY_TO_SEND
    
    # === Progress Tracking ===
    
    def start_sending(self) -> None:
        """Mark campaign as started"""
        if not self.is_ready_to_send():
            raise ValueError("Campaign is not ready for sending")
        
        self.status = CampaignStatus.SENDING
        self.started_at = datetime.now()
    
    def pause_sending(self) -> None:
        """Pause the sending process"""
        if self.status != CampaignStatus.SENDING:
            raise ValueError("Can only pause a campaign that is currently sending")
        
        self.status = CampaignStatus.PAUSED
        self.paused_at = datetime.now()
    
    def resume_sending(self) -> None:
        """Resume paused sending"""
        if self.status != CampaignStatus.PAUSED:
            raise ValueError("Can only resume a paused campaign")
        
        self.status = CampaignStatus.SENDING
        self.paused_at = None
    
    def complete_sending(self) -> None:
        """Mark campaign as completed"""
        self.status = CampaignStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def cancel_sending(self) -> None:
        """Cancel the sending process"""
        self.status = CampaignStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def mark_email_sent(self, contact_email: str, sent_at: Optional[datetime] = None) -> None:
        """Mark an email as successfully sent"""
        result = self.get_email_result_by_email(contact_email)
        if result:
            result.status = EmailStatus.SENT
            result.sent_at = sent_at or datetime.now()
    
    def mark_email_failed(self, contact_email: str, error_message: str) -> None:
        """Mark an email as failed"""
        result = self.get_email_result_by_email(contact_email)
        if result:
            result.status = EmailStatus.FAILED
            result.error_message = error_message
    
    def mark_email_retrying(self, contact_email: str) -> None:
        """Mark an email for retry"""
        result = self.get_email_result_by_email(contact_email)
        if result and result.retry_count < self.max_retries:
            result.status = EmailStatus.RETRYING
            result.retry_count += 1
    
    def get_email_result_by_email(self, email: str) -> Optional[EmailResult]:
        """Get email result by contact email address"""
        for result in self.email_results:
            if result.contact.email == email:
                return result
        return None
    
    # === Statistics ===
    
    def get_sent_count(self) -> int:
        """Get number of successfully sent emails"""
        return len([r for r in self.email_results if r.status == EmailStatus.SENT])
    
    def get_failed_count(self) -> int:
        """Get number of failed emails"""
        return len([r for r in self.email_results if r.status == EmailStatus.FAILED])
    
    def get_pending_count(self) -> int:
        """Get number of pending emails"""
        return len([r for r in self.email_results if r.status == EmailStatus.PENDING])
    
    def get_progress_percentage(self) -> float:
        """Get sending progress as percentage (0-100)"""
        if not self.email_results:
            return 0.0
        
        completed = self.get_sent_count() + self.get_failed_count()
        return (completed / len(self.email_results)) * 100
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage"""
        total_processed = self.get_sent_count() + self.get_failed_count()
        if total_processed == 0:
            return 0.0
        
        return (self.get_sent_count() / total_processed) * 100
    
    def get_campaign_duration(self) -> Optional[float]:
        """Get campaign duration in seconds"""
        if not self.started_at:
            return None
        
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    # === Screen Navigation ===
    
    def can_proceed_to_screen(self, screen: str) -> bool:
        """Check if campaign can proceed to specified screen"""
        screen_requirements = {
            "upload": True,  # Always can go back to upload
            "compose": len(self.contacts) > 0,
            "preview": len(self.contacts) > 0 and self.email_template is not None,
            "progress": self.is_ready_to_send(),
            "complete": self.status in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]
        }
        
        return screen_requirements.get(screen, False)
    
    def set_current_screen(self, screen: str) -> None:
        """Set current screen with validation"""
        if not self.can_proceed_to_screen(screen):
            raise ValueError(f"Cannot proceed to {screen} screen in current state")
        
        self.current_screen = screen
    
    # === Data Export/Import ===
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert campaign to dictionary for storage"""
        return {
            'campaign_id': self.campaign_id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'current_screen': self.current_screen,
            'contact_count': len(self.contacts),
            'template': self.email_template.to_dict() if self.email_template else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'source_file': self.source_file,
            'statistics': {
                'sent_count': self.get_sent_count(),
                'failed_count': self.get_failed_count(),
                'success_rate': self.get_success_rate(),
                'progress_percentage': self.get_progress_percentage()
            }
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get campaign summary for completion screen"""
        return {
            'name': self.name,
            'total_contacts': len(self.contacts),
            'emails_sent': self.get_sent_count(),
            'emails_failed': self.get_failed_count(),
            'success_rate': self.get_success_rate(),
            'duration': self.get_campaign_duration(),
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }
    
    def __str__(self) -> str:
        """String representation for logging"""
        return f"Campaign({self.name}, {self.status.value}, {len(self.contacts)} contacts)"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return (f"Campaign(id={self.campaign_id[:8]}, name='{self.name}', "
                f"status={self.status}, contacts={len(self.contacts)})")