"""
Contact data model for Mini Email CRM
Handles contact information with validation and personalization support
"""

import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class Contact:
    """
    Contact data model with validation and personalization support
    
    Core attributes for email personalization:
    - email: Required, validated email address
    - firstname: Required for personalization
    - lastname: Optional, used when available  
    - Additional optional fields for extended functionality
    """
    
    email: str
    firstname: str
    lastname: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate required fields on initialization"""
        self.email = self.email.strip() if self.email else ''
        self.firstname = self.firstname.strip() if self.firstname else ''
        self.lastname = (self.lastname or '').strip()

        if not self.email:
            raise ValueError("Email is required")
        if not self.firstname:
            raise ValueError("First name is required")

        # Validate email format immediately
        if not self.is_valid_email():
            raise ValueError(f"Invalid email format: {self.email}")
    
    def is_valid_email(self) -> bool:
        """
        Validate email format using regex
        Supports standard email formats including unicode and IP addresses
        """
        if not self.email:
            return False
        
        email = self.email.strip()
        
        # Basic structure check: must have @ and non-empty parts
        if '@' not in email or email.count('@') != 1:
            return False
            
        local, domain = email.split('@')
        
        # Local part validation (before @)
        if not local or len(local) > 64:
            return False
            
        # Domain part validation (after @)
        if not domain or len(domain) > 253:
            return False
            
        # Check for IP address domain (e.g., user@192.168.1.1)
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if re.match(ip_pattern, domain):
            # Basic IP validation
            parts = domain.split('.')
            if all(0 <= int(part) <= 255 for part in parts):
                return True
        
        # Regular domain validation (supports unicode)
        # More permissive pattern that allows unicode characters
        domain_pattern = r'^[a-zA-Z0-9\u00a1-\uffff.-]+\.[a-zA-Z\u00a1-\uffff]{2,}$'
        if re.match(domain_pattern, domain):
            return True
            
        return False
    
    def is_valid_phone(self) -> bool:
        """
        Validate phone number format (optional field)
        Supports common phone formats
        """
        if not self.phone:
            return True  # Optional field
        
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', self.phone)
        
        # Must have 10-15 digits (international format support)
        return 10 <= len(digits_only) <= 15
    
    def validate(self) -> List[str]:
        """
        Comprehensive validation returning list of error messages
        Empty list means valid contact
        """
        errors = []
        
        # Required field validation
        if not self.email or not self.email.strip():
            errors.append("Email is required")
        elif not self.is_valid_email():
            errors.append(f"Invalid email format: {self.email}")
        
        if not self.firstname:
            errors.append("First name is required")
        
        # Optional field validation
        if self.phone and not self.is_valid_phone():
            errors.append(f"Invalid phone format: {self.phone}")
        
        return errors
    
    def get_full_name(self) -> str:
        """Get full name in 'FirstName LastName' format"""
        if self.lastname:
            return f"{self.firstname} {self.lastname}"
        return self.firstname
    
    def get_display_name(self) -> str:
        """
        Get display name in format: 'FirstName LastName (email@domain.com)'
        This matches the UI requirement from app features
        """
        return f"{self.get_full_name()} ({self.email})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contact to dictionary for CSV export or API usage"""
        return {
            'email': self.email,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'phone': self.phone,
            'company': self.company,
            'title': self.title,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contact':
        """Create Contact from dictionary (CSV import support)"""
        # Handle case-insensitive column names from CSV
        normalized_data = {}
        for key, value in data.items():
            normalized_key = key.lower().strip()
            # Handle common CSV column variations
            if normalized_key in ['email', 'email_address', 'e_mail']:
                normalized_data['email'] = str(value).strip() if value else ''
            elif normalized_key in ['firstname', 'first_name', 'fname']:
                normalized_data['firstname'] = str(value).strip() if value else ''
            elif normalized_key in ['lastname', 'last_name', 'lname']:
                normalized_data['lastname'] = str(value).strip() if value else ''
            elif normalized_key in ['phone', 'phone_number', 'telephone']:
                normalized_data['phone'] = str(value).strip() if value else None
            elif normalized_key in ['company', 'organization', 'org']:
                normalized_data['company'] = str(value).strip() if value else None
            elif normalized_key in ['title', 'job_title', 'position']:
                normalized_data['title'] = str(value).strip() if value else None
            elif normalized_key in ['notes', 'comments', 'remarks']:
                normalized_data['notes'] = str(value).strip() if value else None
        
        return cls(
            email=normalized_data.get('email', ''),
            firstname=normalized_data.get('firstname', ''),
            lastname=normalized_data.get('lastname', ''),
            phone=normalized_data.get('phone'),
            company=normalized_data.get('company'),
            title=normalized_data.get('title'),
            notes=normalized_data.get('notes')
        )
    
    def get_personalization_data(self) -> Dict[str, str]:
        """
        Get data for email personalization placeholders
        Returns dict with keys matching template placeholders: {firstname}, {lastname}, {email}
        """
        return {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'fullname': self.get_full_name(),
            'company': self.company or '',
            'title': self.title or ''
        }
    
    def __str__(self) -> str:
        """String representation for logging and debugging"""
        return f"Contact({self.get_display_name()})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return (f"Contact(email='{self.email}', firstname='{self.firstname}', "
                f"lastname='{self.lastname}')")