"""
Template Engine for Mini Email CRM
Handles email template personalization with placeholder replacement and validation
"""

import re
import logging
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from models.contact import Contact
from models.email_template import EmailTemplate


@dataclass
class TemplateValidationResult:
    """Result of template validation with detailed error information"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    missing_placeholders: Set[str]
    unsupported_placeholders: Set[str]


@dataclass 
class PersonalizationResult:
    """Result of personalizing a template for a contact"""
    subject: str
    body: str
    contact_email: str
    success: bool
    errors: List[str]
    warnings: List[str]
    missing_data: Set[str]


class TemplateEngine:
    """
    Email template personalization engine
    
    Features:
    - Placeholder replacement ({firstname}, {lastname}, {email}, etc.)
    - Validation for missing placeholders and contact data
    - Graceful handling of missing contact information
    - Support for batch processing
    - Detailed error reporting and logging
    """
    
    # Core placeholders that should always be available
    CORE_PLACEHOLDERS = {'firstname', 'lastname', 'email'}
    
    # Extended placeholders for additional personalization
    EXTENDED_PLACEHOLDERS = {'fullname', 'company', 'title', 'phone'}
    
    # All supported placeholders
    SUPPORTED_PLACEHOLDERS = CORE_PLACEHOLDERS.union(EXTENDED_PLACEHOLDERS)
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize template engine with optional logger"""
        self.logger = logger or logging.getLogger(__name__)
        
    def extract_placeholders(self, text: str) -> Set[str]:
        """
        Extract all placeholders from text in {placeholder} format
        
        Args:
            text: Text containing placeholders
            
        Returns:
            Set of placeholder names (without braces)
        """
        if not text:
            return set()
        
        # Find all {placeholder} patterns (case-insensitive)
        # Updated pattern to avoid nested braces
        placeholder_pattern = r'\{([^{}]+)\}'
        matches = re.findall(placeholder_pattern, text, re.IGNORECASE)
        
        # Normalize to lowercase and strip whitespace
        return {match.lower().strip() for match in matches if match.strip()}
    
    def validate_template(self, template: EmailTemplate) -> TemplateValidationResult:
        """
        Validate email template for placeholder usage and structure
        
        Args:
            template: EmailTemplate object to validate
            
        Returns:
            TemplateValidationResult with validation details
        """
        errors = []
        warnings = []
        
        # Basic template validation
        if not template.subject or not template.subject.strip():
            errors.append("Email subject cannot be empty")
        
        if not template.body or not template.body.strip():
            errors.append("Email body cannot be empty")
        
        # Extract placeholders from both subject and body
        subject_placeholders = self.extract_placeholders(template.subject)
        body_placeholders = self.extract_placeholders(template.body)
        all_placeholders = subject_placeholders.union(body_placeholders)
        
        # Check for unsupported placeholders
        unsupported_placeholders = all_placeholders - self.SUPPORTED_PLACEHOLDERS
        for placeholder in unsupported_placeholders:
            errors.append(f"Unsupported placeholder: {{{placeholder}}}")
        
        # Check for missing core placeholders (warnings only)
        missing_core = self.CORE_PLACEHOLDERS - all_placeholders
        if missing_core:
            warnings.append(f"Consider adding core placeholders for better personalization: {', '.join(f'{{{p}}}' for p in missing_core)}")
        
        # Check for malformed placeholders
        malformed_pattern = r'\{[^}]*$|\{.*?\{.*?\}'  # Unclosed or nested braces
        if re.search(malformed_pattern, template.subject + template.body):
            warnings.append("Possible malformed placeholders detected - check for unclosed or nested braces")
        
        is_valid = len(errors) == 0
        
        return TemplateValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            missing_placeholders=set(),  # Will be filled during personalization
            unsupported_placeholders=unsupported_placeholders
        )
    
    def validate_contact_data(self, contact: Contact, required_placeholders: Set[str]) -> Tuple[Dict[str, str], Set[str]]:
        """
        Validate and prepare contact data for personalization
        
        Args:
            contact: Contact object to validate
            required_placeholders: Set of placeholders needed for template
            
        Returns:
            Tuple of (contact_data_dict, missing_data_set)
        """
        # Get base personalization data from contact
        contact_data = contact.get_personalization_data()
        
        # Add computed fields if not already present
        if 'fullname' not in contact_data:
            contact_data['fullname'] = contact.get_full_name()
        
        # Ensure all values are strings and handle None values gracefully
        processed_data = {}
        missing_data = set()
        
        for placeholder in required_placeholders:
            if placeholder in self.SUPPORTED_PLACEHOLDERS:
                value = contact_data.get(placeholder, '')
                
                # Handle None or empty values
                if value is None or (isinstance(value, str) and not value.strip()):
                    if placeholder in self.CORE_PLACEHOLDERS:
                        # Core placeholders are required
                        missing_data.add(placeholder)
                        processed_data[placeholder] = f"[{placeholder.upper()}_MISSING]"
                    else:
                        # Extended placeholders can be empty
                        processed_data[placeholder] = ""
                else:
                    processed_data[placeholder] = str(value).strip()
            else:
                # Unsupported placeholder
                missing_data.add(placeholder)
                processed_data[placeholder] = f"[{placeholder.upper()}_UNSUPPORTED]"
        
        return processed_data, missing_data
    
    def replace_placeholders(self, text: str, contact_data: Dict[str, str]) -> str:
        """
        Replace placeholders in text with contact data
        
        Args:
            text: Text containing placeholders
            contact_data: Dictionary mapping placeholder names to values
            
        Returns:
            Text with placeholders replaced
        """
        if not text or not contact_data:
            return text
        
        result = text
        placeholders_in_text = self.extract_placeholders(text)
        
        # Replace each placeholder (case-insensitive)
        for placeholder in placeholders_in_text:
            pattern = re.compile(f'\\{{{re.escape(placeholder)}\\}}', re.IGNORECASE)
            replacement = contact_data.get(placeholder, f"[{placeholder.upper()}_NOT_FOUND]")
            result = pattern.sub(replacement, result)
        
        return result
    
    def personalize_template(self, template: EmailTemplate, contact: Contact) -> PersonalizationResult:
        """
        Personalize an email template for a specific contact
        
        Args:
            template: EmailTemplate to personalize
            contact: Contact to personalize for
            
        Returns:
            PersonalizationResult with personalized content and status
        """
        errors = []
        warnings = []
        
        try:
            # Validate template first
            template_validation = self.validate_template(template)
            if not template_validation.is_valid:
                return PersonalizationResult(
                    subject="",
                    body="",
                    contact_email=contact.email,
                    success=False,
                    errors=template_validation.errors,
                    warnings=template_validation.warnings,
                    missing_data=set()
                )
            
            # Get all placeholders used in template
            all_placeholders = self.extract_placeholders(template.subject + " " + template.body)
            
            # Validate and prepare contact data
            contact_data, missing_data = self.validate_contact_data(contact, all_placeholders)
            
            # Generate warnings for missing core data
            core_missing = missing_data.intersection(self.CORE_PLACEHOLDERS)
            if core_missing:
                warnings.append(f"Missing core contact data: {', '.join(core_missing)}")
            
            # Personalize subject and body
            personalized_subject = self.replace_placeholders(template.subject, contact_data)
            personalized_body = self.replace_placeholders(template.body, contact_data)
            
            # Check for any remaining unreplaced placeholders
            remaining_subject = self.extract_placeholders(personalized_subject)
            remaining_body = self.extract_placeholders(personalized_body)
            remaining_placeholders = remaining_subject.union(remaining_body)
            
            if remaining_placeholders:
                warnings.append(f"Some placeholders could not be replaced: {', '.join(f'{{{p}}}' for p in remaining_placeholders)}")
            
            success = len(errors) == 0
            
            self.logger.info(f"Personalized template for {contact.email} - Success: {success}")
            
            return PersonalizationResult(
                subject=personalized_subject,
                body=personalized_body,
                contact_email=contact.email,
                success=success,
                errors=errors,
                warnings=warnings,
                missing_data=missing_data
            )
            
        except Exception as e:
            error_msg = f"Error personalizing template for {contact.email}: {str(e)}"
            self.logger.error(error_msg)
            errors.append(error_msg)
            
            return PersonalizationResult(
                subject="",
                body="",
                contact_email=contact.email,
                success=False,
                errors=errors,
                warnings=warnings,
                missing_data=set()
            )
    
    def batch_personalize(self, template: EmailTemplate, contacts: List[Contact]) -> List[PersonalizationResult]:
        """
        Personalize template for multiple contacts
        
        Args:
            template: EmailTemplate to personalize
            contacts: List of Contact objects
            
        Returns:
            List of PersonalizationResult objects
        """
        results = []
        
        self.logger.info(f"Starting batch personalization for {len(contacts)} contacts")
        
        # Validate template once
        template_validation = self.validate_template(template)
        if not template_validation.is_valid:
            # Return error result for all contacts
            error_result = PersonalizationResult(
                subject="",
                body="",
                contact_email="",
                success=False,
                errors=template_validation.errors,
                warnings=template_validation.warnings,
                missing_data=set()
            )
            return [error_result for _ in contacts]
        
        # Process each contact
        for i, contact in enumerate(contacts):
            try:
                result = self.personalize_template(template, contact)
                results.append(result)
                
                # Log progress for large batches
                if (i + 1) % 100 == 0 or (i + 1) == len(contacts):
                    self.logger.info(f"Processed {i + 1}/{len(contacts)} contacts")
                    
            except Exception as e:
                self.logger.error(f"Error processing contact {contact.email}: {str(e)}")
                error_result = PersonalizationResult(
                    subject="",
                    body="",
                    contact_email=contact.email,
                    success=False,
                    errors=[f"Processing error: {str(e)}"],
                    warnings=[],
                    missing_data=set()
                )
                results.append(error_result)
        
        # Log summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        self.logger.info(f"Batch personalization complete: {successful} successful, {failed} failed")
        
        return results
    
    def preview_template(self, template: EmailTemplate, sample_data: Optional[Dict[str, str]] = None) -> PersonalizationResult:
        """
        Generate a preview of the template with sample data
        
        Args:
            template: EmailTemplate to preview
            sample_data: Optional custom sample data, uses default if None
            
        Returns:
            PersonalizationResult with preview content
        """
        if sample_data is None:
            sample_data = {
                'firstname': 'John',
                'lastname': 'Doe',
                'email': 'john.doe@example.com',
                'fullname': 'John Doe',
                'company': 'Acme Corp',
                'title': 'Marketing Manager',
                'phone': '+1-555-123-4567'
            }
        
        # Create a sample contact for preview
        try:
            sample_contact = Contact(
                email=sample_data.get('email', 'preview@example.com'),
                firstname=sample_data.get('firstname', 'John'),
                lastname=sample_data.get('lastname', 'Doe'),
                company=sample_data.get('company'),
                title=sample_data.get('title'),
                phone=sample_data.get('phone')
            )
            
            return self.personalize_template(template, sample_contact)
            
        except Exception as e:
            self.logger.error(f"Error generating template preview: {str(e)}")
            return PersonalizationResult(
                subject="",
                body="",
                contact_email="preview@example.com",
                success=False,
                errors=[f"Preview error: {str(e)}"],
                warnings=[],
                missing_data=set()
            )
    
    def get_template_statistics(self, template: EmailTemplate) -> Dict[str, Any]:
        """
        Get statistics about template placeholder usage
        
        Args:
            template: EmailTemplate to analyze
            
        Returns:
            Dictionary with template statistics
        """
        subject_placeholders = self.extract_placeholders(template.subject)
        body_placeholders = self.extract_placeholders(template.body)
        all_placeholders = subject_placeholders.union(body_placeholders)
        
        return {
            'total_placeholders': len(all_placeholders),
            'subject_placeholders': len(subject_placeholders),
            'body_placeholders': len(body_placeholders),
            'core_placeholders_used': len(all_placeholders.intersection(self.CORE_PLACEHOLDERS)),
            'extended_placeholders_used': len(all_placeholders.intersection(self.EXTENDED_PLACEHOLDERS)),
            'unsupported_placeholders': len(all_placeholders - self.SUPPORTED_PLACEHOLDERS),
            'placeholder_list': sorted(list(all_placeholders)),
            'character_count': {
                'subject': len(template.subject),
                'body': len(template.body),
                'total': len(template.subject) + len(template.body)
            }
        }
