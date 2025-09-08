"""
Validation utilities for Mini Email CRM
Simple validation functions for email addresses and other data
"""

import re
from typing import List, Optional, Tuple


def is_valid_email(email: str) -> bool:
    """
    Validate email format using regex
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Comprehensive email regex pattern
    # Matches standard email formats required for SMTP sending
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))


def validate_email_list(emails: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate a list of email addresses
    
    Args:
        emails: List of email addresses to validate
        
    Returns:
        Tuple of (valid_emails, invalid_emails)
    """
    valid_emails = []
    invalid_emails = []
    
    for email in emails:
        if is_valid_email(email):
            valid_emails.append(email.strip())
        else:
            invalid_emails.append(email)
    
    return valid_emails, invalid_emails


def validate_required_field(value: str, field_name: str) -> Optional[str]:
    """
    Validate that a required field has a value
    
    Args:
        value: Field value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Error message if invalid, None if valid
    """
    if not value or not str(value).strip():
        return f"{field_name} is required"
    return None


def validate_string_length(value: str, field_name: str, max_length: int, min_length: int = 0) -> Optional[str]:
    """
    Validate string length constraints
    
    Args:
        value: String value to validate
        field_name: Name of the field for error messages
        max_length: Maximum allowed length
        min_length: Minimum allowed length
        
    Returns:
        Error message if invalid, None if valid
    """
    if not value:
        if min_length > 0:
            return f"{field_name} must be at least {min_length} characters"
        return None
    
    length = len(str(value))
    
    if length < min_length:
        return f"{field_name} must be at least {min_length} characters"
    
    if length > max_length:
        return f"{field_name} must not exceed {max_length} characters"
    
    return None


def sanitize_email(email: str) -> str:
    """
    Sanitize email address by trimming whitespace and converting to lowercase
    
    Args:
        email: Email address to sanitize
        
    Returns:
        Sanitized email address
    """
    if not email or not isinstance(email, str):
        return ""
    
    return email.strip().lower()


def sanitize_name(name: str) -> str:
    """
    Sanitize name field by trimming whitespace and capitalizing properly
    
    Args:
        name: Name to sanitize
        
    Returns:
        Sanitized name
    """
    if not name or not isinstance(name, str):
        return ""
    
    # Trim whitespace and capitalize first letter of each word
    return " ".join(word.capitalize() for word in name.strip().split() if word)


def validate_csv_headers(headers: List[str], required_headers: List[str]) -> List[str]:
    """
    Validate CSV headers contain required fields
    
    Args:
        headers: List of CSV column headers
        required_headers: List of required header names
        
    Returns:
        List of missing required headers
    """
    # Convert to lowercase for case-insensitive comparison
    headers_lower = [h.lower().strip() for h in headers]
    required_lower = [r.lower() for r in required_headers]
    
    missing_headers = []
    for required in required_lower:
        # Check for exact match or common variations
        variations = {
            'email': ['email', 'email_address', 'e_mail', 'e-mail'],
            'firstname': ['firstname', 'first_name', 'fname', 'first'],
            'lastname': ['lastname', 'last_name', 'lname', 'last']
        }
        
        found = False
        if required in variations:
            for variation in variations[required]:
                if variation in headers_lower:
                    found = True
                    break
        else:
            found = required in headers_lower
        
        if not found:
            missing_headers.append(required)
    
    return missing_headers


def is_valid_phone(phone: str) -> bool:
    """
    Validate phone number format (basic validation)
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if phone format appears valid, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove all non-digit characters for validation
    digits_only = re.sub(r'\D', '', phone)
    
    # Must have 10-15 digits (supports international formats)
    return 10 <= len(digits_only) <= 15


def clean_phone(phone: str) -> str:
    """
    Clean and format phone number
    
    Args:
        phone: Phone number to clean
        
    Returns:
        Cleaned phone number
    """
    if not phone or not isinstance(phone, str):
        return ""
    
    # Remove all non-digit and non-plus characters, keep the plus for international
    cleaned = re.sub(r'[^\d+]', '', phone.strip())
    
    return cleaned


def validate_file_size(file_size: int, max_size_mb: int = 10) -> Optional[str]:
    """
    Validate file size is within limits
    
    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in megabytes
        
    Returns:
        Error message if too large, None if valid
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        return f"File size ({file_size // (1024*1024)}MB) exceeds maximum allowed size ({max_size_mb}MB)"
    
    return None


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> Optional[str]:
    """
    Validate file has an allowed extension
    
    Args:
        filename: Name of the file to validate
        allowed_extensions: List of allowed extensions (e.g., ['.csv', '.xlsx'])
        
    Returns:
        Error message if invalid extension, None if valid
    """
    if not filename or not isinstance(filename, str):
        return "Invalid filename"
    
    # Get file extension
    file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    
    if file_ext not in [ext.lower() for ext in allowed_extensions]:
        return f"Invalid file type. Allowed extensions: {', '.join(allowed_extensions)}"
    
    return None
