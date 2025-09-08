"""
Email Service Core for Mini Email CRM
Handles SMTP connections, email sending, retry logic, and validation
"""

import smtplib
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from config.settings import SMTP_SETTINGS, EMAIL_SETTINGS
from models.contact import Contact
from models.email_template import EmailTemplate


class EmailStatus(Enum):
    """Email sending status enumeration"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class EmailResult:
    """Result of email sending operation"""
    contact: Contact
    status: EmailStatus
    error_message: Optional[str] = None
    attempts: int = 0
    sent_at: Optional[datetime] = None


class EmailValidationError(Exception):
    """Custom exception for email validation errors"""
    pass


class SMTPConnectionError(Exception):
    """Custom exception for SMTP connection errors"""
    pass


class EmailService:
    """
    Core email service for sending personalized emails via SMTP
    
    Features:
    - SMTP connection management with TLS support
    - Email validation and sanitization
    - Retry logic for failed sends
    - Batch processing with rate limiting
    - Comprehensive logging and error handling
    """
    
    def __init__(self, smtp_settings: Optional[Dict] = None, email_settings: Optional[Dict] = None):
        """
        Initialize email service with configuration
        
        Args:
            smtp_settings: SMTP configuration (uses default from settings if None)
            email_settings: Email behavior settings (uses default from settings if None)
        """
        self.smtp_settings = smtp_settings or SMTP_SETTINGS
        self.email_settings = email_settings or EMAIL_SETTINGS
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        # Connection state
        self._smtp_connection = None
        self._connection_established = False
        
        # Validation patterns
        self._initialize_validation()
    
    def _initialize_validation(self):
        """Initialize email validation patterns and settings"""
        # These will be used for additional validation beyond Contact model
        self.max_subject_length = 200
        self.max_body_length = 50000
        
    def validate_smtp_settings(self) -> List[str]:
        """
        Validate SMTP configuration settings
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not self.smtp_settings.get('server'):
            errors.append("SMTP server is required")
        
        if not self.smtp_settings.get('port'):
            errors.append("SMTP port is required")
        elif not isinstance(self.smtp_settings['port'], int) or self.smtp_settings['port'] <= 0:
            errors.append("SMTP port must be a positive integer")
        
        if not self.smtp_settings.get('username'):
            errors.append("SMTP username is required")
        
        if not self.smtp_settings.get('password'):
            errors.append("SMTP password is required")
        
        return errors
    
    def validate_email_content(self, subject: str, body: str) -> List[str]:
        """
        Validate email content
        
        Args:
            subject: Email subject line
            body: Email body content
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not subject or not subject.strip():
            errors.append("Email subject is required")
        elif len(subject) > self.max_subject_length:
            errors.append(f"Subject too long (max {self.max_subject_length} characters)")
        
        if not body or not body.strip():
            errors.append("Email body is required")
        elif len(body) > self.max_body_length:
            errors.append(f"Body too long (max {self.max_body_length} characters)")
        
        return errors
    
    def establish_connection(self) -> bool:
        """
        Establish SMTP connection with error handling
        
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            SMTPConnectionError: If connection cannot be established
        """
        try:
            # Validate settings first
            validation_errors = self.validate_smtp_settings()
            if validation_errors:
                raise SMTPConnectionError(f"Invalid SMTP settings: {', '.join(validation_errors)}")
            
            self.logger.info(f"Connecting to SMTP server: {self.smtp_settings['server']}:{self.smtp_settings['port']}")
            
            # Create SMTP connection
            self._smtp_connection = smtplib.SMTP(
                self.smtp_settings['server'], 
                self.smtp_settings['port'],
                timeout=self.email_settings.get('timeout', 30)
            )
            
            # Enable debug logging in debug mode
            if self.logger.level <= logging.DEBUG:
                self._smtp_connection.set_debuglevel(1)
            
            # Start TLS if enabled
            if self.smtp_settings.get('use_tls', True):
                self.logger.debug("Starting TLS encryption")
                self._smtp_connection.starttls()
            
            # Login with credentials
            self.logger.debug("Authenticating with SMTP server")
            self._smtp_connection.login(
                self.smtp_settings['username'],
                self.smtp_settings['password']
            )
            
            self._connection_established = True
            self.logger.info("SMTP connection established successfully")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed: {str(e)}"
            self.logger.error(error_msg)
            raise SMTPConnectionError(error_msg)
        
        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"SMTP server disconnected: {str(e)}"
            self.logger.error(error_msg)
            raise SMTPConnectionError(error_msg)
        
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            self.logger.error(error_msg)
            raise SMTPConnectionError(error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected connection error: {str(e)}"
            self.logger.error(error_msg)
            raise SMTPConnectionError(error_msg)
    
    def close_connection(self):
        """Close SMTP connection safely"""
        try:
            if self._smtp_connection and self._connection_established:
                self._smtp_connection.quit()
                self.logger.info("SMTP connection closed")
        except Exception as e:
            self.logger.warning(f"Error closing SMTP connection: {str(e)}")
        finally:
            self._smtp_connection = None
            self._connection_established = False
    
    def create_email_message(self, 
                           sender_email: str,
                           recipient_email: str, 
                           subject: str, 
                           body: str,
                           is_html: bool = False) -> MIMEMultipart:
        """
        Create email message with proper headers
        
        Args:
            sender_email: Sender's email address
            recipient_email: Recipient's email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML format
            
        Returns:
            Configured MIMEMultipart message
        """
        # Create message container
        message = MIMEMultipart('alternative')
        
        # Set headers
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = subject
        
        # Add body
        if is_html:
            body_part = MIMEText(body, 'html')
        else:
            body_part = MIMEText(body, 'plain')
        
        message.attach(body_part)
        
        return message
    
    def send_single_email(self, 
                         contact: Contact,
                         subject: str,
                         body: str,
                         sender_email: Optional[str] = None,
                         is_html: bool = False) -> EmailResult:
        """
        Send a single email with retry logic
        
        Args:
            contact: Contact to send email to
            subject: Email subject
            body: Email body
            sender_email: Sender email (uses SMTP username if None)
            is_html: Whether body is HTML format
            
        Returns:
            EmailResult with sending status
        """
        # Use SMTP username as sender if not provided
        if not sender_email:
            sender_email = self.smtp_settings['username']
        
        # Validate contact
        contact_errors = contact.validate()
        if contact_errors:
            return EmailResult(
                contact=contact,
                status=EmailStatus.FAILED,
                error_message=f"Contact validation failed: {', '.join(contact_errors)}"
            )
        
        # Validate email content
        content_errors = self.validate_email_content(subject, body)
        if content_errors:
            return EmailResult(
                contact=contact,
                status=EmailStatus.FAILED,
                error_message=f"Content validation failed: {', '.join(content_errors)}"
            )
        
        max_retries = self.email_settings.get('max_retries', 3)
        
        for attempt in range(max_retries + 1):  # +1 for initial attempt
            try:
                # Ensure connection is established
                if not self._connection_established:
                    self.establish_connection()
                
                # Create email message
                message = self.create_email_message(
                    sender_email=sender_email,
                    recipient_email=contact.email,
                    subject=subject,
                    body=body,
                    is_html=is_html
                )
                
                # Send email
                self.logger.info(f"Sending email to {contact.email} (attempt {attempt + 1})")
                self._smtp_connection.send_message(message)
                
                # Success
                self.logger.info(f"Email sent successfully to {contact.email}")
                return EmailResult(
                    contact=contact,
                    status=EmailStatus.SENT,
                    attempts=attempt + 1,
                    sent_at=datetime.now()
                )
                
            except smtplib.SMTPRecipientsRefused as e:
                error_msg = f"Recipient refused: {str(e)}"
                self.logger.warning(f"Failed to send to {contact.email}: {error_msg}")
                
                # Don't retry for recipient refused errors
                return EmailResult(
                    contact=contact,
                    status=EmailStatus.FAILED,
                    error_message=error_msg,
                    attempts=attempt + 1
                )
            
            except smtplib.SMTPServerDisconnected as e:
                error_msg = f"Server disconnected: {str(e)}"
                self.logger.warning(f"Connection lost while sending to {contact.email}: {error_msg}")
                
                # Reset connection for retry
                self._connection_established = False
                self._smtp_connection = None
                
                if attempt < max_retries:
                    self.logger.info(f"Retrying email to {contact.email} (attempt {attempt + 2})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return EmailResult(
                        contact=contact,
                        status=EmailStatus.FAILED,
                        error_message=error_msg,
                        attempts=attempt + 1
                    )
            
            except (smtplib.SMTPException, Exception) as e:
                error_msg = f"Send error: {str(e)}"
                self.logger.warning(f"Failed to send to {contact.email}: {error_msg}")
                
                if attempt < max_retries:
                    self.logger.info(f"Retrying email to {contact.email} (attempt {attempt + 2})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return EmailResult(
                        contact=contact,
                        status=EmailStatus.FAILED,
                        error_message=error_msg,
                        attempts=attempt + 1
                    )
        
        # This should not be reached, but just in case
        return EmailResult(
            contact=contact,
            status=EmailStatus.FAILED,
            error_message="Maximum retries exceeded",
            attempts=max_retries + 1
        )
    
    def send_bulk_emails(self, 
                        contacts: List[Contact],
                        template: EmailTemplate,
                        sender_email: Optional[str] = None,
                        progress_callback: Optional[callable] = None) -> List[EmailResult]:
        """
        Send emails to multiple contacts with rate limiting and progress tracking
        
        Args:
            contacts: List of contacts to send emails to
            template: Email template for personalization
            sender_email: Sender email (uses SMTP username if None)
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of EmailResult objects
        """
        results = []
        batch_size = self.email_settings.get('batch_size', 50)
        delay_between_batches = self.email_settings.get('delay_between_batches', 2)
        
        self.logger.info(f"Starting bulk email send to {len(contacts)} contacts")
        
        try:
            # Establish connection once for the entire batch
            self.establish_connection()
            
            for i, contact in enumerate(contacts):
                try:
                    # Personalize email for this contact
                    personalized = template.personalize_for_contact(contact)
                    
                    # Send email
                    result = self.send_single_email(
                        contact=contact,
                        subject=personalized['subject'],
                        body=personalized['body'],
                        sender_email=sender_email,
                        is_html=False  # Plain text for simplicity
                    )
                    
                    results.append(result)
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback(i + 1, len(contacts), result)
                    
                    # Batch delay
                    if (i + 1) % batch_size == 0 and i + 1 < len(contacts):
                        self.logger.info(f"Processed batch of {batch_size}, waiting {delay_between_batches}s")
                        time.sleep(delay_between_batches)
                
                except Exception as e:
                    error_msg = f"Unexpected error processing {contact.email}: {str(e)}"
                    self.logger.error(error_msg)
                    
                    results.append(EmailResult(
                        contact=contact,
                        status=EmailStatus.FAILED,
                        error_message=error_msg,
                        attempts=1
                    ))
            
        except Exception as e:
            self.logger.error(f"Bulk email operation failed: {str(e)}")
            raise
        
        finally:
            self.close_connection()
        
        # Log summary
        sent_count = sum(1 for r in results if r.status == EmailStatus.SENT)
        failed_count = sum(1 for r in results if r.status == EmailStatus.FAILED)
        
        self.logger.info(f"Bulk email completed: {sent_count} sent, {failed_count} failed")
        
        return results
    
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Test SMTP connection without sending emails
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            self.establish_connection()
            self.close_connection()
            return True, None
        
        except SMTPConnectionError as e:
            return False, str(e)
        
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current connection status information
        
        Returns:
            Dictionary with connection status details
        """
        return {
            'connected': self._connection_established,
            'server': self.smtp_settings.get('server', 'Not configured'),
            'port': self.smtp_settings.get('port', 'Not configured'),
            'username': self.smtp_settings.get('username', 'Not configured'),
            'use_tls': self.smtp_settings.get('use_tls', True)
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.establish_connection()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_connection()


# Convenience functions for simple usage
def send_test_email(recipient_email: str, 
                   subject: str = "Test Email", 
                   body: str = "This is a test email from Mini Email CRM.") -> bool:
    """
    Send a simple test email
    
    Args:
        recipient_email: Email address to send test to
        subject: Test email subject
        body: Test email body
        
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Create a dummy contact for testing
        test_contact = Contact(
            email=recipient_email,
            firstname="Test",
            lastname="User"
        )
        
        service = EmailService()
        result = service.send_single_email(test_contact, subject, body)
        service.close_connection()
        
        return result.status == EmailStatus.SENT
        
    except Exception as e:
        logging.error(f"Test email failed: {str(e)}")
        return False


def validate_email_settings() -> Tuple[bool, List[str]]:
    """
    Validate current email configuration
    
    Returns:
        Tuple of (is_valid: bool, error_messages: List[str])
    """
    try:
        service = EmailService()
        errors = service.validate_smtp_settings()
        return len(errors) == 0, errors
        
    except Exception as e:
        return False, [f"Configuration error: {str(e)}"]
