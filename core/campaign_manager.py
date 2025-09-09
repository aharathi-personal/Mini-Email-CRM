"""
Campaign Manager for Mini Email CRM
Coordinates CSV processing, templating, email sending with progress tracking
"""

import logging
import threading
import time
from typing import List, Dict, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from models.campaign import Campaign, CampaignStatus, EmailResult, EmailStatus
from models.contact import Contact
from models.email_template import EmailTemplate
from core.csv_handler import CSVHandler
from core.template_engine import TemplateEngine, PersonalizationResult
from core.email_service import EmailService, EmailResult as ServiceEmailResult
from config.settings import EMAIL_SETTINGS, SMTP_SETTINGS


class CampaignManagerStatus(Enum):
    """Campaign Manager operational status"""
    IDLE = "idle"
    PROCESSING = "processing"  
    SENDING = "sending"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class CampaignProgress:
    """Progress tracking information"""
    total_emails: int = 0
    processed_emails: int = 0  
    sent_emails: int = 0
    failed_emails: int = 0
    current_email: str = ""
    progress_percentage: float = 0.0
    success_rate: float = 0.0
    emails_per_minute: float = 0.0
    estimated_time_remaining: float = 0.0  # in seconds
    last_updated: datetime = field(default_factory=datetime.now)


class CampaignManager:
    """
    Campaign Manager coordinates the entire email campaign process
    
    Features:
    - CSV file processing and validation
    - Email template personalization
    - Bulk email sending with progress tracking
    - Pause/resume functionality
    - Success/failure tracking and reporting
    - Thread-safe operations for UI integration
    """
    
    def __init__(self, progress_callback: Optional[Callable[[CampaignProgress], None]] = None):
        """
        Initialize Campaign Manager
        
        Args:
            progress_callback: Optional callback function for progress updates
        """
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.csv_handler = CSVHandler()
        self.template_engine = TemplateEngine()
        self.email_service = EmailService()
        
        # Current campaign
        self.current_campaign: Optional[Campaign] = None
        
        # Manager state
        self.status = CampaignManagerStatus.IDLE
        self.progress = CampaignProgress()
        self.progress_callback = progress_callback
        
        # Thread control
        self._sending_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        
        # Timing tracking
        self._start_time: Optional[datetime] = None
        self._pause_start_time: Optional[datetime] = None
        self._total_pause_duration: float = 0.0
        
        # Lock for thread safety
        self._lock = threading.Lock()
    
    # === Campaign Lifecycle ===
    
    def create_campaign(self, name: str, **kwargs) -> Campaign:
        """Create a new campaign"""
        with self._lock:
            if self.current_campaign and self.status != CampaignManagerStatus.IDLE:
                raise ValueError("Cannot create new campaign while another is active")
            
            self.current_campaign = Campaign(name=name, **kwargs)
            self.logger.info(f"Created new campaign: {name}")
            return self.current_campaign
    
    def load_contacts_from_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Load contacts from CSV file
        
        Returns:
            Processing results with contacts and statistics
        """
        if not self.current_campaign:
            raise ValueError("No active campaign")
        
        with self._lock:
            self.status = CampaignManagerStatus.PROCESSING
            
        try:
            self.logger.info(f"Loading contacts from CSV: {file_path}")
            
            # Process CSV file
            result = self.csv_handler.process_csv_file(file_path)
            
            if result['success']:
                # Add contacts to campaign
                self.current_campaign.add_contacts(result['contacts'])
                self.current_campaign.source_file = file_path
                self.current_campaign.file_size = result['file_info'].get('file_size', 0)
                
                self.logger.info(f"Loaded {len(result['contacts'])} contacts successfully")
            else:
                self.logger.error(f"Failed to load contacts: {', '.join(result['errors'])}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error loading contacts: {str(e)}"
            self.logger.error(error_msg)
            result = {
                'success': False,
                'contacts': [],
                'errors': [error_msg],
                'warnings': [],
                'statistics': {}
            }
            return result
        
        finally:
            with self._lock:
                self.status = CampaignManagerStatus.IDLE
    
    def set_email_template(self, subject: str, body: str) -> bool:
        """
        Set email template for campaign
        
        Returns:
            True if template is valid and set successfully
        """
        if not self.current_campaign:
            raise ValueError("No active campaign")
        
        try:
            template = EmailTemplate(
                name=f"{self.current_campaign.name} Template",
                subject=subject,
                body=body
            )
            
            # Validate template
            validation_result = self.template_engine.validate_template(template)
            if not validation_result.is_valid:
                self.logger.error(f"Template validation failed: {', '.join(validation_result.errors)}")
                return False
            
            self.current_campaign.set_email_template(template)
            self.logger.info("Email template set successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting email template: {str(e)}")
            return False
    
    def validate_campaign_ready(self) -> Tuple[bool, List[str]]:
        """
        Validate that campaign is ready for sending
        
        Returns:
            Tuple of (is_ready, error_messages)
        """
        if not self.current_campaign:
            return False, ["No active campaign"]
        
        errors = []
        
        # Check contacts
        if not self.current_campaign.contacts:
            errors.append("No contacts loaded")
        
        # Check template
        if not self.current_campaign.email_template:
            errors.append("No email template set")
        
        # Check SMTP settings
        smtp_errors = self.email_service.validate_smtp_settings()
        errors.extend(smtp_errors)
        
        # Test SMTP connection
        try:
            connection_success, connection_error = self.email_service.test_connection()
            if not connection_success:
                errors.append(f"SMTP connection failed: {connection_error}")
        except Exception as e:
            errors.append(f"SMTP connection test error: {str(e)}")
        
        return len(errors) == 0, errors
    
    # === Email Sending Operations ===
    
    def start_sending(self) -> bool:
        """
        Start sending emails in background thread
        
        Returns:
            True if sending started successfully
        """
        if not self.current_campaign:
            raise ValueError("No active campaign")
        
        # Validate campaign is ready
        is_ready, errors = self.validate_campaign_ready()
        if not is_ready:
            self.logger.error(f"Campaign not ready: {', '.join(errors)}")
            return False
        
        with self._lock:
            if self.status != CampaignManagerStatus.IDLE:
                self.logger.warning("Cannot start sending - manager is busy")
                return False
            
            # Initialize progress tracking
            self._initialize_progress()
            
            # Mark campaign as ready and start sending
            self.current_campaign.mark_ready_for_sending()
            self.current_campaign.start_sending()
            
            # Start sending thread
            self._stop_event.clear()
            self._pause_event.clear()
            self._sending_thread = threading.Thread(target=self._send_emails_worker, daemon=True)
            self._sending_thread.start()
            
            self.status = CampaignManagerStatus.SENDING
            self._start_time = datetime.now()
            self._total_pause_duration = 0.0
            
            self.logger.info("Email sending started")
            return True
    
    def pause_sending(self) -> bool:
        """
        Pause email sending
        
        Returns:
            True if paused successfully
        """
        with self._lock:
            if self.status != CampaignManagerStatus.SENDING:
                return False
            
            self._pause_event.set()
            self.status = CampaignManagerStatus.PAUSED
            self._pause_start_time = datetime.now()
            
            if self.current_campaign:
                self.current_campaign.pause_sending()
            
            self.logger.info("Email sending paused")
            return True
    
    def resume_sending(self) -> bool:
        """
        Resume paused email sending
        
        Returns:
            True if resumed successfully
        """
        with self._lock:
            if self.status != CampaignManagerStatus.PAUSED:
                return False
            
            self._pause_event.clear()
            self.status = CampaignManagerStatus.SENDING
            
            # Track pause duration
            if self._pause_start_time:
                self._total_pause_duration += (datetime.now() - self._pause_start_time).total_seconds()
                self._pause_start_time = None
            
            if self.current_campaign:
                self.current_campaign.resume_sending()
            
            self.logger.info("Email sending resumed")
            return True
    
    def stop_sending(self) -> bool:
        """
        Stop email sending completely
        
        Returns:
            True if stopped successfully
        """
        with self._lock:
            if self.status not in [CampaignManagerStatus.SENDING, CampaignManagerStatus.PAUSED]:
                return False
            
            self.status = CampaignManagerStatus.STOPPING
            self._stop_event.set()
            self._pause_event.clear()
        
        # Wait for sending thread to finish
        if self._sending_thread and self._sending_thread.is_alive():
            self._sending_thread.join(timeout=5.0)
        
        with self._lock:
            self.status = CampaignManagerStatus.IDLE
            
            if self.current_campaign:
                self.current_campaign.cancel_sending()
            
            self.logger.info("Email sending stopped")
            return True
    
    def _initialize_progress(self):
        """Initialize progress tracking"""
        total_contacts = len(self.current_campaign.contacts) if self.current_campaign else 0
        self.progress = CampaignProgress(
            total_emails=total_contacts,
            processed_emails=0,
            sent_emails=0,
            failed_emails=0,
            current_email="",
            progress_percentage=0.0,
            success_rate=0.0,
            emails_per_minute=0.0,
            estimated_time_remaining=0.0
        )
    
    def _update_progress(self, contact_email: str = ""):
        """Update progress tracking and call callback"""
        if not self.current_campaign:
            return
        
        with self._lock:
            self.progress.processed_emails = self.current_campaign.get_sent_count() + self.current_campaign.get_failed_count()
            self.progress.sent_emails = self.current_campaign.get_sent_count()
            self.progress.failed_emails = self.current_campaign.get_failed_count()
            self.progress.current_email = contact_email
            
            # Calculate percentages
            if self.progress.total_emails > 0:
                self.progress.progress_percentage = (self.progress.processed_emails / self.progress.total_emails) * 100
            
            if self.progress.processed_emails > 0:
                self.progress.success_rate = (self.progress.sent_emails / self.progress.processed_emails) * 100
            
            # Calculate rate and ETA
            self._calculate_timing_metrics()
            
            self.progress.last_updated = datetime.now()
        
        # Call progress callback if provided
        if self.progress_callback:
            try:
                self.progress_callback(self.progress)
            except Exception as e:
                self.logger.error(f"Error in progress callback: {str(e)}")
    
    def _calculate_timing_metrics(self):
        """Calculate timing metrics for progress tracking"""
        if not self._start_time or self.progress.processed_emails == 0:
            return
        
        # Calculate effective elapsed time (excluding pauses)
        elapsed_time = (datetime.now() - self._start_time).total_seconds() - self._total_pause_duration
        if self._pause_start_time:
            elapsed_time -= (datetime.now() - self._pause_start_time).total_seconds()
        
        if elapsed_time > 0:
            # Emails per minute
            self.progress.emails_per_minute = (self.progress.processed_emails / elapsed_time) * 60
            
            # Estimated time remaining
            remaining_emails = self.progress.total_emails - self.progress.processed_emails
            if self.progress.emails_per_minute > 0:
                self.progress.estimated_time_remaining = (remaining_emails / self.progress.emails_per_minute) * 60
    
    def _send_emails_worker(self):
        """Worker thread function for sending emails"""
        try:
            self.logger.info("Email sending worker started")
            
            # Get campaign data
            contacts = self.current_campaign.contacts
            template = self.current_campaign.email_template
            
            # Process each contact
            for i, contact in enumerate(contacts):
                # Check for stop signal
                if self._stop_event.is_set():
                    self.logger.info("Email sending stopped by user")
                    break
                
                # Check for pause signal
                if self._pause_event.is_set():
                    self.logger.info("Email sending paused")
                    while self._pause_event.is_set() and not self._stop_event.is_set():
                        time.sleep(0.1)  # Wait for resume or stop
                    
                    if self._stop_event.is_set():
                        self.logger.info("Email sending stopped during pause")
                        break
                
                try:
                    # Personalize template for contact
                    personalization_result = self.template_engine.personalize_template(template, contact)
                    
                    if not personalization_result.success:
                        # Mark as failed due to personalization error
                        self.current_campaign.mark_email_failed(
                            contact.email,
                            f"Personalization failed: {', '.join(personalization_result.errors)}"
                        )
                        self.logger.error(f"Personalization failed for {contact.email}")
                    else:
                        # Send email
                        self._update_progress(contact.email)
                        
                        email_result = self.email_service.send_single_email(
                            contact=contact,
                            subject=personalization_result.subject,
                            body=personalization_result.body
                        )
                        
                        # Update campaign with result
                        if email_result.status.name == "SENT":
                            self.current_campaign.mark_email_sent(contact.email, email_result.sent_at)
                            self.logger.info(f"Email sent successfully to {contact.email}")
                        else:
                            self.current_campaign.mark_email_failed(contact.email, email_result.error_message)
                            self.logger.warning(f"Email failed for {contact.email}: {email_result.error_message}")
                
                except Exception as e:
                    error_msg = f"Error processing {contact.email}: {str(e)}"
                    self.logger.error(error_msg)
                    self.current_campaign.mark_email_failed(contact.email, error_msg)
                
                # Update progress
                self._update_progress()
                
                # Add delay between emails (if not paused/stopped)
                if not self._pause_event.is_set() and not self._stop_event.is_set():
                    delay = self.current_campaign.send_delay
                    time.sleep(delay)
            
            # Mark campaign as completed
            if not self._stop_event.is_set():
                self.current_campaign.complete_sending()
                self.logger.info("Email sending completed")
            
        except Exception as e:
            self.logger.error(f"Error in email sending worker: {str(e)}")
            with self._lock:
                self.status = CampaignManagerStatus.ERROR
                if self.current_campaign:
                    self.current_campaign.status = CampaignStatus.ERROR
        
        finally:
            # Final progress update
            self._update_progress()
            
            with self._lock:
                if self.status not in [CampaignManagerStatus.STOPPING, CampaignManagerStatus.ERROR]:
                    self.status = CampaignManagerStatus.IDLE
    
    # === Campaign Information ===
    
    def get_campaign_status(self) -> Dict[str, Any]:
        """Get current campaign status and statistics"""
        if not self.current_campaign:
            return {'active': False}
        
        return {
            'active': True,
            'campaign': self.current_campaign.to_dict(),
            'manager_status': self.status.value,
            'progress': {
                'total_emails': self.progress.total_emails,
                'processed_emails': self.progress.processed_emails,
                'sent_emails': self.progress.sent_emails,
                'failed_emails': self.progress.failed_emails,
                'current_email': self.progress.current_email,
                'progress_percentage': self.progress.progress_percentage,
                'success_rate': self.progress.success_rate,
                'emails_per_minute': self.progress.emails_per_minute,
                'estimated_time_remaining': self.progress.estimated_time_remaining,
                'last_updated': self.progress.last_updated.isoformat()
            }
        }
    
    def get_detailed_results(self) -> Dict[str, Any]:
        """Get detailed campaign results for reporting"""
        if not self.current_campaign:
            return {}
        
        # Separate successful and failed emails
        successful_emails = []
        failed_emails = []
        
        for result in self.current_campaign.email_results:
            if result.is_successful():
                successful_emails.append({
                    'email': result.contact.email,
                    'name': result.contact.get_full_name(),
                    'sent_at': result.sent_at.isoformat() if result.sent_at else None
                })
            elif result.is_failed():
                failed_emails.append({
                    'email': result.contact.email,
                    'name': result.contact.get_full_name(),
                    'error': result.error_message,
                    'retry_count': result.retry_count
                })
        
        return {
            'campaign_summary': self.current_campaign.get_summary(),
            'successful_emails': successful_emails,
            'failed_emails': failed_emails,
            'statistics': {
                'total_contacts': len(self.current_campaign.contacts),
                'emails_sent': len(successful_emails),
                'emails_failed': len(failed_emails),
                'success_rate': self.progress.success_rate,
                'average_rate': self.progress.emails_per_minute,
                'total_duration': self.current_campaign.get_campaign_duration()
            }
        }
    
    def reset_campaign(self):
        """Reset campaign manager to idle state"""
        # Stop any running operations
        if self.status in [CampaignManagerStatus.SENDING, CampaignManagerStatus.PAUSED]:
            self.stop_sending()
        
        with self._lock:
            self.current_campaign = None
            self.status = CampaignManagerStatus.IDLE
            self.progress = CampaignProgress()
            self._start_time = None
            self._pause_start_time = None
            self._total_pause_duration = 0.0
        
        self.logger.info("Campaign manager reset")
    
    # === Utility Methods ===
    
    def is_busy(self) -> bool:
        """Check if campaign manager is currently busy"""
        return self.status != CampaignManagerStatus.IDLE
    
    def can_start_sending(self) -> bool:
        """Check if campaign can start sending"""
        if not self.current_campaign or self.status != CampaignManagerStatus.IDLE:
            return False
        
        is_ready, _ = self.validate_campaign_ready()
        return is_ready
    
    def can_pause(self) -> bool:
        """Check if sending can be paused"""
        return self.status == CampaignManagerStatus.SENDING
    
    def can_resume(self) -> bool:
        """Check if sending can be resumed"""
        return self.status == CampaignManagerStatus.PAUSED
    
    def can_stop(self) -> bool:
        """Check if sending can be stopped"""
        return self.status in [CampaignManagerStatus.SENDING, CampaignManagerStatus.PAUSED]
    
    def __del__(self):
        """Cleanup when manager is destroyed"""
        try:
            if self.status in [CampaignManagerStatus.SENDING, CampaignManagerStatus.PAUSED]:
                self.stop_sending()
        except:
            pass


# === Factory Functions ===

def create_campaign_manager(progress_callback: Optional[Callable[[CampaignProgress], None]] = None) -> CampaignManager:
    """
    Factory function to create a properly configured campaign manager
    
    Args:
        progress_callback: Optional callback for progress updates
        
    Returns:
        Configured CampaignManager instance
    """
    return CampaignManager(progress_callback=progress_callback)


def create_simple_campaign(name: str, csv_file: str, subject: str, body: str) -> Tuple[Campaign, List[str]]:
    """
    Convenience function to create a simple campaign with basic validation
    
    Args:
        name: Campaign name
        csv_file: Path to CSV file with contacts
        subject: Email subject
        body: Email body
        
    Returns:
        Tuple of (Campaign object, error_messages)
    """
    errors = []
    
    try:
        # Create manager
        manager = CampaignManager()
        
        # Create campaign
        campaign = manager.create_campaign(name)
        
        # Load contacts
        csv_result = manager.load_contacts_from_csv(csv_file)
        if not csv_result['success']:
            errors.extend(csv_result['errors'])
            return campaign, errors
        
        # Set template
        if not manager.set_email_template(subject, body):
            errors.append("Failed to set email template")
            return campaign, errors
        
        # Validate ready for sending
        is_ready, validation_errors = manager.validate_campaign_ready()
        if not is_ready:
            errors.extend(validation_errors)
        
        return campaign, errors
        
    except Exception as e:
        errors.append(f"Error creating campaign: {str(e)}")
        return None, errors