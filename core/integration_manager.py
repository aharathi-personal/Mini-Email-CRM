"""
Integration Manager for Mini Email CRM
Task 22: Enhanced Integration & Flow Implementation

This module provides the central integration manager that handles data flow,
validation, screen transitions, and attachment management across all screens.
"""

import os
import shutil
import tempfile
import csv
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from models.contact import Contact
from models.attachment import Attachment, AttachmentManager
from models.email_template import EmailTemplate
from models.campaign import Campaign
from core.email_service import EmailService
from core.csv_handler import CSVHandler

# Set up logging
import logging
logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of validation checks with detailed feedback"""
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.info = []
    
    def add_error(self, message: str):
        """Add validation error"""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Add validation warning"""
        self.warnings.append(message)
    
    def add_info(self, message: str):
        """Add validation info"""
        self.info.append(message)
    
    def get_all_messages(self) -> List[str]:
        """Get all validation messages"""
        messages = []
        if self.errors:
            messages.extend([f"ERROR: {msg}" for msg in self.errors])
        if self.warnings:
            messages.extend([f"WARNING: {msg}" for msg in self.warnings])
        if self.info:
            messages.extend([f"INFO: {msg}" for msg in self.info])
        return messages


class IntegrationManager:
    """
    Central manager for data flow, validation, and screen transitions
    Task 22: Provides enhanced integration between all screens with attachment support
    """
    
    def __init__(self):
        self.campaign_data = {}
        self.temp_dir = None
        self.cleanup_handlers = []
        
        # Initialize core components
        self.csv_handler = CSVHandler()
        self.email_service = EmailService()
        
        # Track validation state
        self.last_validation = None
        self.validation_cache = {}
        
        logger.info("Integration Manager initialized")
    
    def initialize_temp_directory(self) -> str:
        """Initialize temporary directory for attachments"""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix="mini_crm_")
            logger.info(f"Temporary directory created: {self.temp_dir}")
        return self.temp_dir
    
    def cleanup_temp_directory(self):
        """Clean up temporary directory and attachments"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Temporary directory cleaned up: {self.temp_dir}")
                self.temp_dir = None
            except Exception as e:
                logger.error(f"Failed to cleanup temp directory: {e}")
    
    def register_cleanup_handler(self, handler):
        """Register cleanup handler for campaign completion/cancellation"""
        self.cleanup_handlers.append(handler)
    
    def execute_cleanup_handlers(self):
        """Execute all registered cleanup handlers"""
        for handler in self.cleanup_handlers:
            try:
                handler()
            except Exception as e:
                logger.error(f"Cleanup handler error: {e}")
    
    # ========== Upload Screen Integration ==========
    
    def validate_upload_data(self, file_path: str) -> ValidationResult:
        """Validate uploaded contact file"""
        result = ValidationResult()
        
        if not file_path:
            result.add_error("No file selected")
            return result
        
        if not os.path.exists(file_path):
            result.add_error(f"File not found: {file_path}")
            return result
        
        # Validate file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            result.add_error("File is empty")
            return result
        
        if file_size > 50 * 1024 * 1024:  # 50MB limit for CSV files
            result.add_error(f"File too large: {file_size / (1024*1024):.1f}MB (max 50MB)")
            return result
        
        # Validate CSV format
        try:
            contacts = self.csv_handler.read_contacts(file_path)
            if not contacts:
                result.add_error("No valid contacts found in file")
                return result
            
            # Check for required columns
            if not any(hasattr(contact, 'email') and contact.email for contact in contacts):
                result.add_error("No valid email addresses found")
                return result
            
            result.add_info(f"Found {len(contacts)} contacts")
            
            # Check for duplicates
            emails = [c.email for c in contacts if hasattr(c, 'email') and c.email]
            unique_emails = set(emails)
            if len(emails) != len(unique_emails):
                duplicates = len(emails) - len(unique_emails)
                result.add_warning(f"{duplicates} duplicate email addresses found")
            
        except Exception as e:
            result.add_error(f"Failed to read CSV file: {str(e)}")
        
        return result
    
    def process_upload_transition(self, file_path: str) -> Dict[str, Any]:
        """Process transition from upload to compose screen"""
        logger.info(f"Processing upload transition for: {file_path}")
        
        # Validate the upload data
        validation = self.validate_upload_data(file_path)
        if not validation.is_valid:
            raise ValueError(f"Upload validation failed: {'; '.join(validation.errors)}")
        
        # Read contacts
        contacts = self.csv_handler.read_contacts(file_path)
        
        # Store upload data
        upload_data = {
            'uploaded_file': file_path,
            'file_path': file_path,
            'contacts': contacts,
            'contact_count': len(contacts),
            'upload_timestamp': datetime.now(),
            'validation_messages': validation.get_all_messages()
        }
        
        self.campaign_data.update(upload_data)
        logger.info(f"Upload processed: {len(contacts)} contacts loaded")
        
        return upload_data
    
    # ========== Compose Screen Integration ==========
    
    def validate_compose_data(self, email_data: Dict[str, Any]) -> ValidationResult:
        """Validate compose screen data including attachments"""
        result = ValidationResult()
        
        # Validate email fields
        if not email_data.get('from_email'):
            result.add_error("From email is required")
        elif not self._is_valid_email(email_data['from_email']):
            result.add_error("From email format is invalid")
        
        if not email_data.get('subject'):
            result.add_error("Subject is required")
        elif len(email_data['subject'].strip()) < 3:
            result.add_warning("Subject is very short")
        
        if not email_data.get('content'):
            result.add_error("Email content is required")
        elif len(email_data['content'].strip()) < 10:
            result.add_warning("Email content is very short")
        
        # Validate attachments if present
        attachments = email_data.get('attachments', [])
        if attachments:
            attachment_result = self.validate_attachments(attachments)
            if not attachment_result.is_valid:
                result.errors.extend(attachment_result.errors)
                result.is_valid = False
            result.warnings.extend(attachment_result.warnings)
            result.info.extend(attachment_result.info)
        
        # Check for contacts
        if not self.campaign_data.get('contacts'):
            result.add_error("No contacts loaded. Please upload contacts first.")
        
        return result
    
    def validate_attachments(self, attachments: List[Attachment]) -> ValidationResult:
        """Comprehensive attachment validation"""
        result = ValidationResult()
        
        if not attachments:
            return result  # No attachments is valid
        
        total_size = 0
        file_names = set()
        
        for attachment in attachments:
            # Individual file validation
            file_validation = attachment.validate()
            if file_validation:
                result.errors.extend([f"{attachment.filename}: {err}" for err in file_validation])
                result.is_valid = False
            
            # Check for duplicate names
            if attachment.filename in file_names:
                result.add_error(f"Duplicate attachment name: {attachment.filename}")
            file_names.add(attachment.filename)
            
            # Check file existence and corruption
            if os.path.exists(attachment.filepath):
                try:
                    # Try to read a small portion to check for corruption
                    with open(attachment.filepath, 'rb') as f:
                        f.read(1024)  # Read first 1KB
                    total_size += attachment.file_size
                except Exception as e:
                    result.add_error(f"File appears corrupted: {attachment.filename}")
            else:
                result.add_error(f"File not found: {attachment.filepath}")
        
        # Total size validation
        if total_size > Attachment.MAX_TOTAL_SIZE:
            total_mb = total_size / (1024 * 1024)
            max_mb = Attachment.MAX_TOTAL_SIZE / (1024 * 1024)
            result.add_error(f"Total attachment size ({total_mb:.1f}MB) exceeds limit ({max_mb}MB)")
        
        if attachments:
            result.add_info(f"{len(attachments)} attachments, {total_size / (1024*1024):.1f}MB total")
        
        return result
    
    def process_compose_transition(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process transition from compose to preview screen"""
        logger.info("Processing compose transition")
        
        # Validate compose data
        validation = self.validate_compose_data(email_data)
        if not validation.is_valid:
            raise ValueError(f"Compose validation failed: {'; '.join(validation.errors)}")
        
        # Process attachments - copy to temp directory for campaign
        processed_attachments = []
        if email_data.get('attachments'):
            temp_dir = self.initialize_temp_directory()
            
            for attachment in email_data['attachments']:
                try:
                    # Copy file to temp directory
                    temp_path = os.path.join(temp_dir, attachment.filename)
                    shutil.copy2(attachment.filepath, temp_path)
                    
                    # Create new attachment with temp path
                    temp_attachment = Attachment.from_file_path(temp_path)
                    processed_attachments.append(temp_attachment)
                    
                except Exception as e:
                    logger.error(f"Failed to process attachment {attachment.filename}: {e}")
                    raise ValueError(f"Failed to process attachment: {attachment.filename}")
        
        # Update campaign data
        compose_data = {
            'from_email': email_data['from_email'],
            'subject': email_data['subject'],
            'content': email_data['content'],
            'attachments': processed_attachments,
            'compose_timestamp': datetime.now(),
            'validation_messages': validation.get_all_messages()
        }
        
        self.campaign_data.update(compose_data)
        logger.info(f"Compose processed: {len(processed_attachments)} attachments")
        
        return compose_data
    
    # ========== Preview Screen Integration ==========
    
    def validate_preview_data(self) -> ValidationResult:
        """Validate data for preview screen"""
        result = ValidationResult()
        
        # Check required data is present
        if not self.campaign_data.get('contacts'):
            result.add_error("No contacts available")
        
        if not self.campaign_data.get('from_email'):
            result.add_error("From email not set")
        
        if not self.campaign_data.get('subject'):
            result.add_error("Subject not set")
        
        if not self.campaign_data.get('content'):
            result.add_error("Email content not set")
        
        # Check email service connectivity
        try:
            if not self.email_service.test_connection():
                result.add_warning("Email service connection test failed")
        except Exception as e:
            result.add_warning(f"Cannot test email service: {e}")
        
        # Validate personalization
        content = self.campaign_data.get('content', '')
        contacts = self.campaign_data.get('contacts', [])
        
        if contacts and content:
            # Check if personalization placeholders exist and are valid
            import re
            placeholders = re.findall(r'\{\{(\w+)\}\}', content)
            if placeholders:
                # Check if all placeholders can be filled
                sample_contact = contacts[0]
                for placeholder in placeholders:
                    if not hasattr(sample_contact, placeholder):
                        result.add_warning(f"Placeholder '{{{{ {placeholder} }}}}' may not be filled for all contacts")
        
        return result
    
    def process_preview_transition(self) -> Dict[str, Any]:
        """Process transition from preview to progress screen"""
        logger.info("Processing preview transition")
        
        # Validate preview data
        validation = self.validate_preview_data()
        if not validation.is_valid:
            raise ValueError(f"Preview validation failed: {'; '.join(validation.errors)}")
        
        # Create email template
        template = EmailTemplate(
            subject=self.campaign_data['subject'],
            content=self.campaign_data['content'],
            from_email=self.campaign_data['from_email']
        )
        
        # Add attachments to template
        if self.campaign_data.get('attachments'):
            for attachment in self.campaign_data['attachments']:
                template.attachments.add_attachment(attachment)
        
        # Create campaign
        campaign = Campaign(
            name=f"Campaign {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            template=template,
            contacts=self.campaign_data['contacts']
        )
        
        # Update campaign data
        preview_data = {
            'campaign': campaign,
            'template': template,
            'preview_timestamp': datetime.now(),
            'validation_messages': validation.get_all_messages()
        }
        
        self.campaign_data.update(preview_data)
        logger.info("Preview processed: Campaign created")
        
        return preview_data
    
    # ========== Progress Screen Integration ==========
    
    def process_campaign_execution(self, progress_callback=None) -> Dict[str, Any]:
        """Execute campaign with progress tracking"""
        logger.info("Starting campaign execution")
        
        campaign = self.campaign_data.get('campaign')
        if not campaign:
            raise ValueError("No campaign available for execution")
        
        # Initialize progress tracking
        results = {
            'total_emails': len(campaign.contacts),
            'sent_count': 0,
            'failed_count': 0,
            'success_emails': [],
            'failed_emails': [],
            'start_time': datetime.now(),
            'end_time': None,
            'errors': []
        }
        
        # Send emails with progress tracking
        for i, contact in enumerate(campaign.contacts):
            try:
                # Update progress
                if progress_callback:
                    progress_callback(i + 1, contact.email, results)
                
                # Send email
                success = self.email_service.send_campaign_email(campaign, contact)
                
                if success:
                    results['sent_count'] += 1
                    results['success_emails'].append(contact.email)
                else:
                    results['failed_count'] += 1
                    results['failed_emails'].append(contact.email)
                    
            except Exception as e:
                logger.error(f"Failed to send email to {contact.email}: {e}")
                results['failed_count'] += 1
                results['failed_emails'].append(contact.email)
                results['errors'].append(f"{contact.email}: {str(e)}")
        
        results['end_time'] = datetime.now()
        results['duration'] = results['end_time'] - results['start_time']
        
        # Update campaign data
        self.campaign_data.update(results)
        logger.info(f"Campaign completed: {results['sent_count']} sent, {results['failed_count']} failed")
        
        return results
    
    # ========== Complete Screen Integration ==========
    
    def process_campaign_completion(self) -> Dict[str, Any]:
        """Process campaign completion and cleanup"""
        logger.info("Processing campaign completion")
        
        completion_data = {
            'completion_timestamp': datetime.now(),
            'final_results': {
                'total_emails': self.campaign_data.get('total_emails', 0),
                'sent_count': self.campaign_data.get('sent_count', 0),
                'failed_count': self.campaign_data.get('failed_count', 0),
                'success_rate': 0
            }
        }
        
        # Calculate success rate
        total = completion_data['final_results']['total_emails']
        sent = completion_data['final_results']['sent_count']
        if total > 0:
            completion_data['final_results']['success_rate'] = (sent / total) * 100
        
        # Execute cleanup
        self.execute_cleanup_handlers()
        self.cleanup_temp_directory()
        
        # Update campaign data
        self.campaign_data.update(completion_data)
        logger.info("Campaign completion processed")
        
        return completion_data
    
    # ========== Utility Methods ==========
    
    def reset_campaign(self):
        """Reset campaign data for new campaign"""
        logger.info("Resetting campaign data")
        
        # Execute cleanup
        self.execute_cleanup_handlers()
        self.cleanup_temp_directory()
        
        # Clear data
        self.campaign_data.clear()
        self.validation_cache.clear()
        self.cleanup_handlers.clear()
        
        logger.info("Campaign data reset completed")
    
    def get_campaign_data(self) -> Dict[str, Any]:
        """Get current campaign data"""
        return self.campaign_data.copy()
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """Get campaign summary for display"""
        summary = {
            'has_contacts': bool(self.campaign_data.get('contacts')),
            'contact_count': len(self.campaign_data.get('contacts', [])),
            'has_email_data': all([
                self.campaign_data.get('from_email'),
                self.campaign_data.get('subject'),
                self.campaign_data.get('content')
            ]),
            'has_attachments': bool(self.campaign_data.get('attachments')),
            'attachment_count': len(self.campaign_data.get('attachments', [])),
            'is_ready_for_sending': False
        }
        
        # Check if ready for sending
        summary['is_ready_for_sending'] = (
            summary['has_contacts'] and
            summary['has_email_data'] and
            summary['contact_count'] > 0
        )
        
        return summary
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def handle_error_recovery(self, error: Exception, context: str) -> Dict[str, Any]:
        """Handle error recovery with context"""
        logger.error(f"Error in {context}: {error}")
        
        recovery_info = {
            'error': str(error),
            'context': context,
            'timestamp': datetime.now(),
            'recovery_suggestions': []
        }
        
        # Add context-specific recovery suggestions
        if "attachment" in str(error).lower():
            recovery_info['recovery_suggestions'].extend([
                "Check file permissions and accessibility",
                "Verify file is not corrupted",
                "Ensure file size is within limits",
                "Try removing and re-adding the attachment"
            ])
        
        if "email" in str(error).lower():
            recovery_info['recovery_suggestions'].extend([
                "Check internet connection",
                "Verify email server settings",
                "Ensure from email address is valid",
                "Try reducing attachment size"
            ])
        
        if "contacts" in str(error).lower():
            recovery_info['recovery_suggestions'].extend([
                "Check CSV file format",
                "Ensure required columns are present",
                "Verify email addresses are valid",
                "Try re-uploading the contact file"
            ])
        
        return recovery_info