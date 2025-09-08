#!/usr/bin/env python3
"""
Manual Test Script for Template Engine
Demonstrates template engine functionality with real examples
"""

import sys
import os
import logging

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from models.contact import Contact
from models.email_template import EmailTemplate, TemplateType
from core.template_engine import TemplateEngine
from core.csv_handler import CSVHandler


def setup_logging():
    """Set up logging for demonstrations"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_basic_personalization():
    """Test basic template personalization"""
    print("\n" + "="*60)
    print("TEST 1: Basic Template Personalization")
    print("="*60)
    
    # Create template engine
    engine = TemplateEngine()
    
    # Create a sample contact
    contact = Contact(
        email='john.doe@example.com',
        firstname='John',
        lastname='Doe',
        company='Acme Corp',
        title='Marketing Manager'
    )
    
    # Create a sample email template
    template = EmailTemplate(
        subject='Welcome to our service, {firstname}!',
        body='''Dear {firstname} {lastname},

Thank you for joining our service! We're excited to have you aboard.

Your account details:
- Name: {fullname}
- Email: {email}
- Company: {company}
- Title: {title}

If you have any questions, please don't hesitate to reach out.

Best regards,
The Team''',
        name='Welcome Email',
        template_type=TemplateType.MARKETING
    )
    
    # Personalize the template
    result = engine.personalize_template(template, contact)
    
    print(f"Personalization Success: {result.success}")
    print(f"Contact Email: {result.contact_email}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
    print(f"Missing Data: {result.missing_data}")
    
    print("\nPersonalized Subject:")
    print(f"'{result.subject}'")
    
    print("\nPersonalized Body:")
    print(result.body)


def test_template_validation():
    """Test template validation functionality"""
    print("\n" + "="*60)
    print("TEST 2: Template Validation")
    print("="*60)
    
    engine = TemplateEngine()
    
    # Test 1: Valid template
    print("\n--- Valid Template ---")
    valid_template = EmailTemplate(
        subject='Hello {firstname}!',
        body='Dear {firstname} {lastname}, welcome to {company}!'
    )
    
    validation_result = engine.validate_template(valid_template)
    print(f"Is Valid: {validation_result.is_valid}")
    print(f"Errors: {validation_result.errors}")
    print(f"Warnings: {validation_result.warnings}")
    
    # Test 2: Template with unsupported placeholders
    print("\n--- Template with Unsupported Placeholders ---")
    invalid_template = EmailTemplate(
        subject='Order {orderid} for {firstname}',
        body='Your order {orderid} with {invalidfield} is ready!'
    )
    
    validation_result = engine.validate_template(invalid_template)
    print(f"Is Valid: {validation_result.is_valid}")
    print(f"Errors: {validation_result.errors}")
    print(f"Warnings: {validation_result.warnings}")
    
    # Test 3: Template without personalization
    print("\n--- Template without Personalization ---")
    generic_template = EmailTemplate(
        subject='Monthly Newsletter',
        body='Here is our monthly newsletter with updates for everyone.'
    )
    
    validation_result = engine.validate_template(generic_template)
    print(f"Is Valid: {validation_result.is_valid}")
    print(f"Errors: {validation_result.errors}")
    print(f"Warnings: {validation_result.warnings}")


def test_missing_data_handling():
    """Test handling of missing contact data"""
    print("\n" + "="*60)
    print("TEST 3: Missing Contact Data Handling")
    print("="*60)
    
    engine = TemplateEngine()
    
    # Create contact with missing data by bypassing validation
    incomplete_contact = Contact.__new__(Contact)
    incomplete_contact.email = 'incomplete@example.com'
    incomplete_contact.firstname = 'John'
    incomplete_contact.lastname = ''  # Missing lastname
    incomplete_contact.phone = None
    incomplete_contact.company = None  # No company
    incomplete_contact.title = None
    incomplete_contact.notes = None
    
    template = EmailTemplate(
        subject='Hello {firstname} {lastname}!',
        body='''Dear {fullname},

Thank you for your interest from {company}.

We look forward to working with you!

Best regards,
{company} Team'''
    )
    
    # Personalize with incomplete data
    result = engine.personalize_template(template, incomplete_contact)
    
    print(f"Personalization Success: {result.success}")
    print(f"Warnings: {result.warnings}")
    print(f"Missing Data: {result.missing_data}")
    
    print("\nPersonalized Subject:")
    print(f"'{result.subject}'")
    
    print("\nPersonalized Body:")
    print(result.body)


def test_batch_personalization():
    """Test batch personalization with multiple contacts"""
    print("\n" + "="*60)
    print("TEST 4: Batch Personalization")
    print("="*60)
    
    engine = TemplateEngine()
    
    # Create contact with missing data by bypassing validation
    incomplete_contact = Contact.__new__(Contact)
    incomplete_contact.email = 'alice@example.com'
    incomplete_contact.firstname = 'Alice'
    incomplete_contact.lastname = 'Brown'
    incomplete_contact.phone = None
    incomplete_contact.company = None  # No company
    incomplete_contact.title = None
    incomplete_contact.notes = None
    
    # Create multiple contacts
    contacts = [
        Contact('john@example.com', 'John', 'Doe', company='Acme Corp'),
        Contact('jane@example.com', 'Jane', 'Smith', company='Tech Solutions'),
        Contact('bob@example.com', 'Bob', 'Wilson', company='Marketing Inc'),
        incomplete_contact,  # No company
    ]
    
    template = EmailTemplate(
        subject='Update from {company}',
        body='''Hi {firstname},

We have some exciting updates to share with you!

As a valued {company} customer, you'll be the first to know.

Best regards,
{firstname} from {company}'''
    )
    
    # Batch personalization
    results = engine.batch_personalize(template, contacts)
    
    print(f"Total Contacts: {len(contacts)}")
    print(f"Total Results: {len(results)}")
    
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    print("\nResults Summary:")
    for i, result in enumerate(results):
        contact = contacts[i]
        print(f"  {contact.email}: Success={result.success}, Warnings={len(result.warnings)}")
        if result.warnings:
            print(f"    Warnings: {result.warnings}")


def test_template_preview():
    """Test template preview functionality"""
    print("\n" + "="*60)
    print("TEST 5: Template Preview")
    print("="*60)
    
    engine = TemplateEngine()
    
    template = EmailTemplate(
        subject='Special offer for {firstname}!',
        body='''Dear {fullname},

We have a special offer just for you at {company}!

As our valued customer, you get 20% off your next purchase.

Use code: SAVE20

Best regards,
{title} Team'''
    )
    
    # Preview with default sample data
    print("--- Default Preview ---")
    preview_result = engine.preview_template(template)
    
    print(f"Preview Success: {preview_result.success}")
    print(f"Subject: '{preview_result.subject}'")
    print("Body:")
    print(preview_result.body)
    
    # Preview with custom sample data
    print("\n--- Custom Preview ---")
    custom_data = {
        'firstname': 'Sarah',
        'lastname': 'Johnson',
        'email': 'sarah@customcorp.com',
        'fullname': 'Sarah Johnson',
        'company': 'Custom Corp',
        'title': 'Sales'
    }
    
    custom_preview = engine.preview_template(template, custom_data)
    print(f"Subject: '{custom_preview.subject}'")
    print("Body:")
    print(custom_preview.body)


def test_template_statistics():
    """Test template statistics functionality"""
    print("\n" + "="*60)
    print("TEST 6: Template Statistics")
    print("="*60)
    
    engine = TemplateEngine()
    
    # Create a comprehensive template
    template = EmailTemplate(
        subject='Hello {firstname} from {company}!',
        body='''Dear {fullname},

Thank you for contacting {company}. We received your inquiry.

Your information:
- Name: {firstname} {lastname}
- Email: {email}
- Company: {company}
- Title: {title}
- Phone: {phone}

We'll get back to you soon, {firstname}!

Best regards,
{company} Support Team'''
    )
    
    # Get statistics
    stats = engine.get_template_statistics(template)
    
    print("Template Statistics:")
    print(f"  Total Placeholders: {stats['total_placeholders']}")
    print(f"  Subject Placeholders: {stats['subject_placeholders']}")
    print(f"  Body Placeholders: {stats['body_placeholders']}")
    print(f"  Core Placeholders Used: {stats['core_placeholders_used']}")
    print(f"  Extended Placeholders Used: {stats['extended_placeholders_used']}")
    print(f"  Unsupported Placeholders: {stats['unsupported_placeholders']}")
    
    print(f"  Placeholder List: {', '.join(f'{{{p}}}' for p in stats['placeholder_list'])}")
    
    print("Character Counts:")
    print(f"  Subject: {stats['character_count']['subject']} chars")
    print(f"  Body: {stats['character_count']['body']} chars")
    print(f"  Total: {stats['character_count']['total']} chars")


def test_csv_integration():
    """Test integration with CSV handler for real data"""
    print("\n" + "="*60)
    print("TEST 7: CSV Integration")
    print("="*60)
    
    engine = TemplateEngine()
    
    # Check if sample CSV exists
    csv_file = 'sample_contacts.csv'
    if not os.path.exists(csv_file):
        print(f"Sample CSV file '{csv_file}' not found. Skipping CSV integration test.")
        return
    
    try:
        # Load contacts from CSV
        csv_handler = CSVHandler()
        contacts, errors = csv_handler.import_contacts(csv_file)
        
        print(f"Loaded {len(contacts)} contacts from CSV")
        if errors:
            print(f"CSV Import Errors: {errors}")
        
        if not contacts:
            print("No valid contacts found in CSV")
            return
        
        # Create template for CSV contacts
        template = EmailTemplate(
            subject='Personalized message for {firstname}',
            body='''Dear {firstname} {lastname},

We hope this message finds you well at {company}.

As a {title}, you might be interested in our latest offerings.

Feel free to contact us at any time.

Best regards,
Our Team

P.S. We have your email as {email} - please let us know if this needs updating.'''
        )
        
        # Batch process first 3 contacts
        test_contacts = contacts[:3] if len(contacts) >= 3 else contacts
        results = engine.batch_personalize(template, test_contacts)
        
        print(f"\nProcessed {len(results)} contacts:")
        for i, result in enumerate(results):
            contact = test_contacts[i]
            print(f"\n--- Contact {i+1}: {contact.email} ---")
            print(f"Success: {result.success}")
            if result.warnings:
                print(f"Warnings: {result.warnings}")
            print(f"Subject: '{result.subject}'")
            print("Body preview (first 200 chars):")
            print(result.body[:200] + "..." if len(result.body) > 200 else result.body)
    
    except Exception as e:
        print(f"Error in CSV integration test: {str(e)}")


def main():
    """Run all manual tests"""
    setup_logging()
    
    print("Template Engine Manual Test Suite")
    print("="*60)
    
    try:
        test_basic_personalization()
        test_template_validation()
        test_missing_data_handling()
        test_batch_personalization()
        test_template_preview()
        test_template_statistics()
        test_csv_integration()
        
        print("\n" + "="*60)
        print("All tests completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
