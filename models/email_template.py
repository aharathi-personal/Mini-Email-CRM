"""
Email Template data model for Mini Email CRM
Handles email templates with placeholder personalization system
"""

import re
from enum import Enum
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime

from .attachment import AttachmentManager


class TemplateType(Enum):
    """Template types for different use cases"""
    MARKETING = "marketing"
    ANNOUNCEMENT = "announcement"
    NEWSLETTER = "newsletter"
    FOLLOW_UP = "follow_up"
    CUSTOM = "custom"


@dataclass
class EmailTemplate:
    """
    Email template with placeholder personalization system and attachment support
    
    Supports placeholders: {firstname}, {lastname}, {email}, {fullname}, {company}, {title}
    Both subject and body support personalization
    Includes attachment management for email campaigns
    """
    
    subject: str
    body: str
    template_type: TemplateType = TemplateType.CUSTOM
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    attachments: AttachmentManager = field(default_factory=AttachmentManager)
    
    # Supported placeholders for validation and replacement
    SUPPORTED_PLACEHOLDERS = {
        'firstname', 'lastname', 'email', 'fullname', 'company', 'title'
    }
    
    def __post_init__(self):
        """Validate template on initialization"""
        if not self.subject or not self.subject.strip():
            raise ValueError("Subject is required")
        if not self.body or not self.body.strip():
            raise ValueError("Email body is required")
        
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def get_placeholders(self, text: str) -> Set[str]:
        """
        Extract all placeholders from text in {placeholder} format
        Returns set of placeholder names (without braces)
        """
        if not text:
            return set()
        
        # Find all {placeholder} patterns
        placeholder_pattern = r'\{([^}]+)\}'
        matches = re.findall(placeholder_pattern, text)
        return {match.lower().strip() for match in matches}
    
    def get_subject_placeholders(self) -> Set[str]:
        """Get all placeholders used in subject line"""
        return self.get_placeholders(self.subject)
    
    def get_body_placeholders(self) -> Set[str]:
        """Get all placeholders used in email body"""
        return self.get_placeholders(self.body)
    
    def get_all_placeholders(self) -> Set[str]:
        """Get all placeholders used in both subject and body"""
        return self.get_subject_placeholders().union(self.get_body_placeholders())
    
    # === Attachment Management ===
    
    def add_attachment(self, filepath: str) -> List[str]:
        """
        Add attachment from file path
        
        Args:
            filepath: Path to the file to attach
            
        Returns:
            List of validation errors, empty if successful
        """
        return self.attachments.add_attachment_from_file(filepath)
    
    def remove_attachment(self, filename: str) -> bool:
        """
        Remove attachment by filename
        
        Args:
            filename: Name of the file to remove
            
        Returns:
            True if removed, False if not found
        """
        return self.attachments.remove_attachment(filename)
    
    def get_attachments(self):
        """Get list of all attachments"""
        return self.attachments.get_attachments()
    
    def get_attachment_count(self) -> int:
        """Get number of attachments"""
        return self.attachments.get_attachment_count()
    
    def get_attachment_summary(self) -> Dict:
        """Get attachment summary for display"""
        return self.attachments.get_summary()
    
    def has_attachments(self) -> bool:
        """Check if template has any attachments"""
        return self.attachments.get_attachment_count() > 0
    
    def clear_attachments(self) -> None:
        """Remove all attachments"""
        self.attachments.clear_attachments()
    
    def validate_attachments(self) -> List[str]:
        """
        Validate all attachments
        
        Returns:
            List of attachment validation errors
        """
        return self.attachments.validate_all()
    
    def validate_placeholders(self) -> List[str]:
        """
        Validate that all placeholders are supported
        Returns list of error messages for unsupported placeholders
        """
        errors = []
        all_placeholders = self.get_all_placeholders()
        
        for placeholder in all_placeholders:
            if placeholder not in self.SUPPORTED_PLACEHOLDERS:
                errors.append(f"Unsupported placeholder: {{{placeholder}}}")
        
        return errors
    
    def validate(self) -> List[str]:
        """
        Comprehensive template validation including attachments
        Returns list of error messages, empty list means valid
        """
        errors = []
        
        # Required field validation
        if not self.subject or not self.subject.strip():
            errors.append("Subject is required")
        
        if not self.body or not self.body.strip():
            errors.append("Email body is required")
        
        # Placeholder validation
        placeholder_errors = self.validate_placeholders()
        errors.extend(placeholder_errors)
        
        # Length validation (reasonable limits for email)
        if len(self.subject) > 200:
            errors.append("Subject line too long (maximum 200 characters)")
        
        if len(self.body) > 50000:  # ~50KB limit
            errors.append("Email body too long (maximum 50,000 characters)")
        
        # Attachment validation
        attachment_errors = self.validate_attachments()
        errors.extend(attachment_errors)
        
        return errors
    
    def personalize_text(self, text: str, contact_data: Dict[str, str]) -> str:
        """
        Replace placeholders in text with contact data
        
        Args:
            text: Text containing {placeholder} patterns
            contact_data: Dict with placeholder names as keys
        
        Returns:
            Text with placeholders replaced with actual data
        """
        if not text or not contact_data:
            return text
        
        personalized_text = text
        
        # Replace each placeholder with corresponding contact data
        for placeholder in self.get_placeholders(text):
            placeholder_pattern = f"{{{placeholder}}}"
            replacement_value = contact_data.get(placeholder, f"{{{placeholder}}}")  # Keep original if not found
            personalized_text = personalized_text.replace(placeholder_pattern, replacement_value)
        
        return personalized_text
    
    def personalize_subject(self, contact_data: Dict[str, str]) -> str:
        """Personalize subject line with contact data"""
        return self.personalize_text(self.subject, contact_data)
    
    def personalize_body(self, contact_data: Dict[str, str]) -> str:
        """Personalize email body with contact data"""
        return self.personalize_text(self.body, contact_data)
    
    def personalize_for_contact(self, contact) -> Dict[str, str]:
        """
        Create fully personalized email for a specific contact
        
        Args:
            contact: Contact object with personalization data
            
        Returns:
            Dict with 'subject' and 'body' keys containing personalized content
        """
        contact_data = contact.get_personalization_data()
        
        return {
            'subject': self.personalize_subject(contact_data),
            'body': self.personalize_body(contact_data)
        }
    
    def preview_with_sample_data(self) -> Dict[str, str]:
        """
        Generate preview with sample contact data
        Useful for template testing and UI preview
        """
        sample_data = {
            'firstname': 'John',
            'lastname': 'Doe', 
            'email': 'john.doe@example.com',
            'fullname': 'John Doe',
            'company': 'Acme Corp',
            'title': 'Marketing Manager'
        }
        
        return {
            'subject': self.personalize_subject(sample_data),
            'body': self.personalize_body(sample_data)
        }
    
    def get_character_count(self) -> Dict[str, int]:
        """Get character counts for UI display"""
        return {
            'subject': len(self.subject),
            'body': len(self.body),
            'total': len(self.subject) + len(self.body)
        }
    
    def to_dict(self) -> Dict:
        """Convert template to dictionary for storage/export"""
        return {
            'name': self.name,
            'subject': self.subject,
            'body': self.body,
            'template_type': self.template_type.value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'placeholders': list(self.get_all_placeholders()),
            'attachments': self.attachments.to_dict(),
            'attachment_summary': self.get_attachment_summary()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EmailTemplate':
        """Create EmailTemplate from dictionary"""
        template_type = TemplateType(data.get('template_type', 'custom'))
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        # Create template
        template = cls(
            subject=data['subject'],
            body=data['body'],
            template_type=template_type,
            name=data.get('name'),
            description=data.get('description'),
            created_at=created_at
        )
        
        # Load attachments if present
        if 'attachments' in data:
            template.attachments = AttachmentManager.from_dict(data['attachments'])
        
        return template
    
    def copy(self) -> 'EmailTemplate':
        """Create a copy of the template including attachments"""
        copied_template = EmailTemplate(
            subject=self.subject,
            body=self.body,
            template_type=self.template_type,
            name=f"{self.name} (Copy)" if self.name else None,
            description=self.description,
            created_at=datetime.now()
        )
        
        # Copy attachments
        for attachment in self.get_attachments():
            copied_template.attachments.attachments.append(attachment)
        
        return copied_template
    
    def __str__(self) -> str:
        """String representation for logging"""
        name = self.name or "Untitled Template"
        return f"EmailTemplate({name}, {len(self.get_all_placeholders())} placeholders)"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return (f"EmailTemplate(subject='{self.subject[:50]}...', "
                f"template_type={self.template_type})")