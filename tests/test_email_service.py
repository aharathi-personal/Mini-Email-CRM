"""
Simple tests for Email Service Core
Manual testing without pytest to keep it simple
"""

import sys
import os

# Windows consoles default to cp1252, which can't encode the emoji/check
# marks this script prints; reconfigure to UTF-8 so it runs unmodified.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.email_service import EmailService, EmailStatus, validate_email_settings, send_test_email
from models.contact import Contact
from models.email_template import EmailTemplate
from utils.validators import is_valid_email, validate_email_list


def test_email_validation():
    """Test email validation functionality"""
    print("Testing email validation...")
    
    # Test valid emails
    valid_emails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "firstname.lastname@company.org"
    ]
    
    for email in valid_emails:
        result = is_valid_email(email)
        print(f"  {email}: {'✓' if result else '✗'}")
        assert result, f"Expected {email} to be valid"
    
    # Test invalid emails
    invalid_emails = [
        "invalid.email",
        "@domain.com",
        "user@",
        "user name@domain.com",
        ""
    ]
    
    for email in invalid_emails:
        result = is_valid_email(email)
        print(f"  {email}: {'✗' if not result else '✓ (should be invalid!)'}")
        assert not result, f"Expected {email} to be invalid"
    
    print("✓ Email validation tests passed\n")


def test_contact_creation():
    """Test contact creation and validation"""
    print("Testing contact creation...")
    
    # Test valid contact
    try:
        contact = Contact(
            email="john.doe@example.com",
            firstname="John",
            lastname="Doe"
        )
        print(f"  Valid contact created: {contact.get_display_name()}")
        print("✓ Valid contact creation passed")
    except Exception as e:
        print(f"✗ Unexpected error creating valid contact: {e}")
        return False
    
    # Test invalid contact - bad email
    try:
        contact = Contact(
            email="invalid.email",
            firstname="John", 
            lastname="Doe"
        )
        print("✗ Should have failed with invalid email")
        return False
    except ValueError as e:
        print(f"✓ Correctly rejected invalid email: {e}")
    
    # Test invalid contact - missing firstname
    try:
        contact = Contact(
            email="test@example.com",
            firstname="",
            lastname="Doe"
        )
        print("✗ Should have failed with empty firstname")
        return False
    except ValueError as e:
        print(f"✓ Correctly rejected empty firstname: {e}")
    
    print("✓ Contact creation tests passed\n")


def test_email_template():
    """Test email template functionality"""
    print("Testing email template...")
    
    # Create template
    template = EmailTemplate(
        subject="Hello {firstname}!",
        body="Hi {firstname} {lastname},\n\nWelcome to our service!\n\nBest regards,\nThe Team"
    )
    
    # Test placeholder detection
    subject_placeholders = template.get_subject_placeholders()
    body_placeholders = template.get_body_placeholders()
    all_placeholders = template.get_all_placeholders()
    
    print(f"  Subject placeholders: {subject_placeholders}")
    print(f"  Body placeholders: {body_placeholders}")
    print(f"  All placeholders: {all_placeholders}")
    
    assert 'firstname' in subject_placeholders
    assert 'firstname' in body_placeholders and 'lastname' in body_placeholders
    assert len(all_placeholders) == 2
    
    # Test personalization
    contact = Contact(
        email="jane.smith@example.com",
        firstname="Jane",
        lastname="Smith"
    )
    
    personalized = template.personalize_for_contact(contact)
    print(f"  Personalized subject: {personalized['subject']}")
    print(f"  Personalized body preview: {personalized['body'][:50]}...")
    
    assert "Hello Jane!" in personalized['subject']
    assert "Hi Jane Smith" in personalized['body']
    
    print("✓ Email template tests passed\n")


def test_email_service_validation():
    """Test email service configuration validation"""
    print("Testing email service validation...")
    
    # Test settings validation
    is_valid, errors = validate_email_settings()
    print(f"  Settings valid: {is_valid}")
    if errors:
        print(f"  Validation errors: {errors}")
    
    # Create email service
    service = EmailService()
    
    # Test content validation
    content_errors = service.validate_email_content("", "")
    assert len(content_errors) > 0, "Should have errors for empty content"
    print(f"  Content validation correctly found {len(content_errors)} errors")
    
    # Test valid content
    content_errors = service.validate_email_content("Valid Subject", "Valid body content")
    assert len(content_errors) == 0, f"Should have no errors for valid content, got: {content_errors}"
    print("  Valid content passed validation")
    
    print("✓ Email service validation tests passed\n")


def test_connection_status():
    """Test connection status functionality"""
    print("Testing connection status...")
    
    service = EmailService()
    status = service.get_connection_status()
    
    print(f"  Connection status: {status}")
    assert 'connected' in status
    assert 'server' in status
    assert 'port' in status
    
    print("✓ Connection status tests passed\n")


def demo_email_sending():
    """Demo email sending functionality (doesn't actually send)"""
    print("Demo: Email sending workflow...")
    
    # Create test contacts
    contacts = [
        Contact(email="test1@example.com", firstname="Alice", lastname="Johnson"),
        Contact(email="test2@example.com", firstname="Bob", lastname="Wilson"),
    ]
    
    # Create template
    template = EmailTemplate(
        subject="Welcome {firstname}!",
        body="Dear {firstname} {lastname},\n\nThank you for joining us!\n\nBest regards,\nThe Team"
    )
    
    # Create email service
    service = EmailService()
    
    print(f"  Created {len(contacts)} test contacts")
    print(f"  Template has {len(template.get_all_placeholders())} placeholders")
    
    # Show what would be sent (without actually sending)
    for i, contact in enumerate(contacts, 1):
        personalized = template.personalize_for_contact(contact)
        print(f"\n  Email {i} for {contact.get_display_name()}:")
        print(f"    Subject: {personalized['subject']}")
        print(f"    Body preview: {personalized['body'][:80]}...")
    
    print("\n✓ Email sending demo completed\n")


def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("MINI EMAIL CRM - EMAIL SERVICE TESTS")
    print("="*50)
    print()
    
    try:
        test_email_validation()
        test_contact_creation()
        test_email_template()
        test_email_service_validation()
        test_connection_status()
        demo_email_sending()
        
        print("="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("="*50)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
