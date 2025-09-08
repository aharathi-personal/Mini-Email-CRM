"""
Tests for Template Engine
Comprehensive test suite for email template personalization functionality
"""

import unittest
import logging
from unittest.mock import patch
from models.contact import Contact
from models.email_template import EmailTemplate, TemplateType
from core.template_engine import TemplateEngine, TemplateValidationResult, PersonalizationResult


class TestTemplateEngine(unittest.TestCase):
    """Test suite for TemplateEngine class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = TemplateEngine()
        
        # Sample contact data
        self.sample_contact = Contact(
            email='john.doe@example.com',
            firstname='John',
            lastname='Doe',
            company='Acme Corp',
            title='Manager'
        )
        
        # Sample template
        self.sample_template = EmailTemplate(
            subject='Hello {firstname}!',
            body='Dear {firstname} {lastname},\n\nThank you for joining {company}!\n\nBest regards,\nThe Team',
            name='Welcome Email'
        )
    
    def test_extract_placeholders_basic(self):
        """Test basic placeholder extraction"""
        text = "Hello {firstname} {lastname}!"
        placeholders = self.engine.extract_placeholders(text)
        expected = {'firstname', 'lastname'}
        self.assertEqual(placeholders, expected)
    
    def test_extract_placeholders_case_insensitive(self):
        """Test case-insensitive placeholder extraction"""
        text = "Hello {FirstName} {LASTNAME}!"
        placeholders = self.engine.extract_placeholders(text)
        expected = {'firstname', 'lastname'}
        self.assertEqual(placeholders, expected)
    
    def test_extract_placeholders_empty_text(self):
        """Test placeholder extraction with empty text"""
        placeholders = self.engine.extract_placeholders("")
        self.assertEqual(placeholders, set())
        
        placeholders = self.engine.extract_placeholders(None)
        self.assertEqual(placeholders, set())
    
    def test_extract_placeholders_malformed(self):
        """Test placeholder extraction with malformed braces"""
        text = "Hello {firstname} and {unclosed and {nested {inside}}"
        placeholders = self.engine.extract_placeholders(text)
        # Should only extract properly formed placeholders
        expected = {'firstname', 'inside'}
        self.assertEqual(placeholders, expected)
    
    def test_extract_placeholders_whitespace(self):
        """Test placeholder extraction with whitespace"""
        text = "Hello { firstname } and {  lastname  }!"
        placeholders = self.engine.extract_placeholders(text)
        expected = {'firstname', 'lastname'}
        self.assertEqual(placeholders, expected)
    
    def test_validate_template_valid(self):
        """Test validation of valid template"""
        result = self.engine.validate_template(self.sample_template)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_validate_template_empty_subject(self):
        """Test validation with empty subject"""
        # Create template with bypass of validation to test engine validation
        template = EmailTemplate.__new__(EmailTemplate)
        template.subject = ''
        template.body = 'Hello {firstname}!'
        template.template_type = TemplateType.CUSTOM
        template.name = None
        template.description = None
        template.created_at = None
        
        result = self.engine.validate_template(template)
        self.assertFalse(result.is_valid)
        self.assertIn("Email subject cannot be empty", result.errors)
    
    def test_validate_template_empty_body(self):
        """Test validation with empty body"""
        # Create template with bypass of validation to test engine validation
        template = EmailTemplate.__new__(EmailTemplate)
        template.subject = 'Hello {firstname}!'
        template.body = ''
        template.template_type = TemplateType.CUSTOM
        template.name = None
        template.description = None
        template.created_at = None
        
        result = self.engine.validate_template(template)
        self.assertFalse(result.is_valid)
        self.assertIn("Email body cannot be empty", result.errors)
    
    def test_validate_template_unsupported_placeholders(self):
        """Test validation with unsupported placeholders"""
        template = EmailTemplate(
            subject='Hello {firstname}!',
            body='Your order {orderid} is ready, {invalidplaceholder}!'
        )
        
        result = self.engine.validate_template(template)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("orderid" in error for error in result.errors))
        self.assertTrue(any("invalidplaceholder" in error for error in result.errors))
    
    def test_validate_template_warnings_for_missing_core(self):
        """Test warnings for missing core placeholders"""
        template = EmailTemplate(
            subject='Generic Subject',
            body='Generic body without personalization'
        )
        
        result = self.engine.validate_template(template)
        self.assertTrue(result.is_valid)  # No errors, just warnings
        self.assertTrue(len(result.warnings) > 0)
        self.assertTrue(any("core placeholders" in warning for warning in result.warnings))
    
    def test_validate_contact_data_complete(self):
        """Test contact data validation with complete data"""
        required_placeholders = {'firstname', 'lastname', 'email', 'company'}
        contact_data, missing_data = self.engine.validate_contact_data(
            self.sample_contact, required_placeholders
        )
        
        self.assertEqual(len(missing_data), 0)
        self.assertEqual(contact_data['firstname'], 'John')
        self.assertEqual(contact_data['lastname'], 'Doe')
        self.assertEqual(contact_data['email'], 'john.doe@example.com')
        self.assertEqual(contact_data['company'], 'Acme Corp')
    
    def test_validate_contact_data_missing_core(self):
        """Test contact data validation with missing core data"""
        # Create contact with bypass of validation to test engine validation
        incomplete_contact = Contact.__new__(Contact)
        incomplete_contact.email = 'test@example.com'
        incomplete_contact.firstname = 'John'
        incomplete_contact.lastname = ''  # Missing lastname
        incomplete_contact.phone = None
        incomplete_contact.company = None
        incomplete_contact.title = None
        incomplete_contact.notes = None
        
        required_placeholders = {'firstname', 'lastname', 'email'}
        contact_data, missing_data = self.engine.validate_contact_data(
            incomplete_contact, required_placeholders
        )
        
        self.assertIn('lastname', missing_data)
        self.assertEqual(contact_data['lastname'], '[LASTNAME_MISSING]')
    
    def test_validate_contact_data_missing_extended(self):
        """Test contact data validation with missing extended data"""
        # Create contact without company
        basic_contact = Contact(
            email='test@example.com',
            firstname='John',
            lastname='Doe'
        )
        
        required_placeholders = {'firstname', 'lastname', 'company'}
        contact_data, missing_data = self.engine.validate_contact_data(
            basic_contact, required_placeholders
        )
        
        # Extended placeholders should not be in missing_data but should be empty string
        self.assertEqual(len(missing_data), 0)
        self.assertEqual(contact_data['company'], '')
    
    def test_replace_placeholders_basic(self):
        """Test basic placeholder replacement"""
        text = "Hello {firstname} {lastname}!"
        contact_data = {'firstname': 'John', 'lastname': 'Doe'}
        
        result = self.engine.replace_placeholders(text, contact_data)
        expected = "Hello John Doe!"
        
        self.assertEqual(result, expected)
    
    def test_replace_placeholders_case_insensitive(self):
        """Test case-insensitive placeholder replacement"""
        text = "Hello {FirstName} {LASTNAME}!"
        contact_data = {'firstname': 'John', 'lastname': 'Doe'}
        
        result = self.engine.replace_placeholders(text, contact_data)
        expected = "Hello John Doe!"
        
        self.assertEqual(result, expected)
    
    def test_replace_placeholders_missing_data(self):
        """Test placeholder replacement with missing data"""
        text = "Hello {firstname} {lastname}!"
        contact_data = {'firstname': 'John'}  # Missing lastname
        
        result = self.engine.replace_placeholders(text, contact_data)
        expected = "Hello John [LASTNAME_NOT_FOUND]!"
        
        self.assertEqual(result, expected)
    
    def test_replace_placeholders_empty_text(self):
        """Test placeholder replacement with empty text"""
        result = self.engine.replace_placeholders("", {'firstname': 'John'})
        self.assertEqual(result, "")
        
        result = self.engine.replace_placeholders(None, {'firstname': 'John'})
        self.assertIsNone(result)
    
    def test_personalize_template_success(self):
        """Test successful template personalization"""
        result = self.engine.personalize_template(self.sample_template, self.sample_contact)
        
        self.assertTrue(result.success)
        self.assertEqual(result.contact_email, 'john.doe@example.com')
        self.assertEqual(result.subject, 'Hello John!')
        self.assertIn('Dear John Doe', result.body)
        self.assertIn('joining Acme Corp', result.body)
    
    def test_personalize_template_invalid_template(self):
        """Test personalization with invalid template"""
        # Create invalid template with bypass of validation
        invalid_template = EmailTemplate.__new__(EmailTemplate)
        invalid_template.subject = ''  # Empty subject
        invalid_template.body = 'Hello {firstname}!'
        invalid_template.template_type = TemplateType.CUSTOM
        invalid_template.name = None
        invalid_template.description = None
        invalid_template.created_at = None
        
        result = self.engine.personalize_template(invalid_template, self.sample_contact)
        
        self.assertFalse(result.success)
        self.assertTrue(len(result.errors) > 0)
    
    def test_personalize_template_missing_contact_data(self):
        """Test personalization with missing contact data"""
        # Create contact with bypass of validation for testing
        incomplete_contact = Contact.__new__(Contact)
        incomplete_contact.email = 'test@example.com'
        incomplete_contact.firstname = 'John'
        incomplete_contact.lastname = ''  # Missing lastname
        incomplete_contact.phone = None
        incomplete_contact.company = None
        incomplete_contact.title = None
        incomplete_contact.notes = None
        
        result = self.engine.personalize_template(self.sample_template, incomplete_contact)
        
        # Should still succeed but with warnings
        self.assertTrue(result.success)
        self.assertTrue(len(result.warnings) > 0)
        self.assertIn('lastname', result.missing_data)
    
    def test_batch_personalize_success(self):
        """Test successful batch personalization"""
        contacts = [
            Contact('john@example.com', 'John', 'Doe'),
            Contact('jane@example.com', 'Jane', 'Smith'),
            Contact('bob@example.com', 'Bob', 'Wilson')
        ]
        
        results = self.engine.batch_personalize(self.sample_template, contacts)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r.success for r in results))
        self.assertEqual(results[0].subject, 'Hello John!')
        self.assertEqual(results[1].subject, 'Hello Jane!')
        self.assertEqual(results[2].subject, 'Hello Bob!')
    
    def test_batch_personalize_invalid_template(self):
        """Test batch personalization with invalid template"""
        # Create invalid template with bypass of validation
        invalid_template = EmailTemplate.__new__(EmailTemplate)
        invalid_template.subject = ''  # Empty subject
        invalid_template.body = 'Hello {firstname}!'
        invalid_template.template_type = TemplateType.CUSTOM
        invalid_template.name = None
        invalid_template.description = None
        invalid_template.created_at = None
        
        contacts = [Contact('john@example.com', 'John', 'Doe')]
        results = self.engine.batch_personalize(invalid_template, contacts)
        
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].success)
    
    def test_batch_personalize_mixed_results(self):
        """Test batch personalization with mixed success/failure"""
        # Create contact with bypass of validation for testing
        incomplete_contact = Contact.__new__(Contact)
        incomplete_contact.email = 'invalid@example.com'
        incomplete_contact.firstname = ''  # Missing firstname
        incomplete_contact.lastname = 'Smith'
        incomplete_contact.phone = None
        incomplete_contact.company = None
        incomplete_contact.title = None
        incomplete_contact.notes = None
        
        contacts = [
            Contact('john@example.com', 'John', 'Doe'),
            incomplete_contact,
            Contact('jane@example.com', 'Jane', 'Wilson')
        ]
        
        results = self.engine.batch_personalize(self.sample_template, contacts)
        
        self.assertEqual(len(results), 3)
        # All should succeed but second should have warnings
        self.assertTrue(all(r.success for r in results))
        self.assertTrue(len(results[1].warnings) > 0)
    
    def test_preview_template_default_data(self):
        """Test template preview with default sample data"""
        result = self.engine.preview_template(self.sample_template)
        
        self.assertTrue(result.success)
        self.assertEqual(result.subject, 'Hello John!')
        self.assertIn('Dear John Doe', result.body)
        self.assertIn('joining Acme Corp', result.body)
    
    def test_preview_template_custom_data(self):
        """Test template preview with custom sample data"""
        custom_data = {
            'firstname': 'Alice',
            'lastname': 'Brown',
            'email': 'alice@example.com',
            'company': 'Tech Startup'
        }
        
        result = self.engine.preview_template(self.sample_template, custom_data)
        
        self.assertTrue(result.success)
        self.assertEqual(result.subject, 'Hello Alice!')
        self.assertIn('Dear Alice Brown', result.body)
        self.assertIn('joining Tech Startup', result.body)
    
    def test_get_template_statistics(self):
        """Test template statistics generation"""
        stats = self.engine.get_template_statistics(self.sample_template)
        
        self.assertEqual(stats['total_placeholders'], 3)  # firstname, lastname, company
        self.assertEqual(stats['subject_placeholders'], 1)  # firstname
        self.assertEqual(stats['body_placeholders'], 3)  # firstname, lastname, company
        self.assertEqual(stats['core_placeholders_used'], 2)  # firstname, lastname
        self.assertEqual(stats['extended_placeholders_used'], 1)  # company
        self.assertEqual(stats['unsupported_placeholders'], 0)
        self.assertIn('firstname', stats['placeholder_list'])
        self.assertIn('lastname', stats['placeholder_list'])
        self.assertIn('company', stats['placeholder_list'])
    
    def test_template_with_all_supported_placeholders(self):
        """Test template using all supported placeholders"""
        comprehensive_template = EmailTemplate(
            subject='Hello {firstname}!',
            body='''Dear {fullname},

Thank you for contacting us, {firstname} {lastname}.

Your details:
- Email: {email}
- Company: {company}
- Title: {title}
- Phone: {phone}

Best regards,
The Team'''
        )
        
        result = self.engine.personalize_template(comprehensive_template, self.sample_contact)
        
        self.assertTrue(result.success)
        self.assertIn('John Doe', result.body)  # fullname
        self.assertIn('john.doe@example.com', result.body)  # email
        self.assertIn('Acme Corp', result.body)  # company
        self.assertIn('Manager', result.body)  # title
    
    def test_complex_template_structure(self):
        """Test complex template with multiple placeholder occurrences"""
        complex_template = EmailTemplate(
            subject='{firstname}, your {company} account is ready!',
            body='''Hi {firstname},

Welcome to {company}! Your account has been created.

Account Details:
- Name: {fullname}
- Email: {email}
- Company: {company}
- Position: {title}

{firstname}, please login at your earliest convenience.

Thanks,
{company} Team'''
        )
        
        result = self.engine.personalize_template(complex_template, self.sample_contact)
        
        self.assertTrue(result.success)
        # Check multiple occurrences are replaced
        self.assertEqual(result.body.count('John'), 3)  # firstname appears 3 times (Hi, fullname, please login)
        self.assertEqual(result.body.count('Acme Corp'), 3)  # company appears 3 times


class TestTemplateEngineEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = TemplateEngine()
    
    def test_contact_with_special_characters(self):
        """Test personalization with special characters in contact data"""
        # Create contact with bypass of email validation for testing
        special_contact = Contact.__new__(Contact)
        special_contact.email = 'jose@example.com'  # Use ASCII version
        special_contact.firstname = 'José'
        special_contact.lastname = "O'Connor"
        special_contact.phone = None
        special_contact.company = 'Müller & Co'
        special_contact.title = None
        special_contact.notes = None
        
        template = EmailTemplate(
            subject='Hello {firstname}!',
            body='Dear {firstname} {lastname} from {company}!'
        )
        
        result = self.engine.personalize_template(template, special_contact)
        
        self.assertTrue(result.success)
        self.assertIn('José', result.body)
        self.assertIn("O'Connor", result.body)
        self.assertIn('Müller & Co', result.body)
    
    def test_very_long_template(self):
        """Test with very long template content"""
        long_body = "Hello {firstname}! " * 1000  # Very long template
        
        template = EmailTemplate(
            subject='Hello {firstname}!',
            body=long_body
        )
        
        contact = Contact('test@example.com', 'John', 'Doe')
        result = self.engine.personalize_template(template, contact)
        
        self.assertTrue(result.success)
        self.assertEqual(result.body.count('Hello John!'), 1000)
    
    def test_template_without_placeholders(self):
        """Test template that doesn't use any placeholders"""
        plain_template = EmailTemplate(
            subject='Generic Newsletter',
            body='This is a generic message without personalization.'
        )
        
        contact = Contact('test@example.com', 'John', 'Doe')
        result = self.engine.personalize_template(plain_template, contact)
        
        self.assertTrue(result.success)
        self.assertEqual(result.subject, 'Generic Newsletter')
        self.assertEqual(result.body, 'This is a generic message without personalization.')
    
    @patch('core.template_engine.logging')
    def test_logging_integration(self, mock_logging):
        """Test that logging is properly integrated"""
        engine = TemplateEngine()  # Will create default logger
        
        contact = Contact('test@example.com', 'John', 'Doe')
        template = EmailTemplate(
            subject='Hello {firstname}!',
            body='Dear {firstname}!'
        )
        
        engine.personalize_template(template, contact)
        
        # Logger should be created and used
        self.assertIsNotNone(engine.logger)


if __name__ == '__main__':
    # Set up logging for tests
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    unittest.main()
