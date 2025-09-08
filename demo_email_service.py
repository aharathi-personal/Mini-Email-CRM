"""
Demo script showing how to use the Email Service
Run this to see the email service in action (without actually sending emails)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.email_service import EmailService, EmailStatus, validate_email_settings
from models.contact import Contact
from models.email_template import EmailTemplate


def demo_email_service():
    """Demonstrate email service functionality"""
    print("="*60)
    print("MINI EMAIL CRM - EMAIL SERVICE DEMO")
    print("="*60)
    
    # 1. Check email settings
    print("\n1. Checking email configuration...")
    is_valid, errors = validate_email_settings()
    if is_valid:
        print("✓ Email settings are valid")
    else:
        print(f"⚠️  Email settings need configuration:")
        for error in errors:
            print(f"   - {error}")
        print("   (This is expected if .env file is not configured)")
    
    # 2. Create sample contacts
    print("\n2. Creating sample contacts...")
    contacts = [
        Contact(
            email="alice@example.com",
            firstname="Alice",
            lastname="Johnson",
            company="Tech Corp"
        ),
        Contact(
            email="bob@example.com", 
            firstname="Bob",
            lastname="Smith",
            company="Design Studio"
        ),
        Contact(
            email="charlie@example.com",
            firstname="Charlie",
            lastname="Brown"
        )
    ]
    
    print(f"✓ Created {len(contacts)} sample contacts:")
    for contact in contacts:
        print(f"   - {contact.get_display_name()}")
    
    # 3. Create email template
    print("\n3. Creating email template...")
    template = EmailTemplate(
        name="Welcome Email",
        subject="Welcome to our service, {firstname}!",
        body="""Dear {firstname} {lastname},

Welcome to Mini Email CRM! We're excited to have you on board.

{company} sounds like a great place to work! We look forward to helping you 
streamline your email marketing campaigns.

Key features you'll love:
• Easy CSV contact imports
• Personalized email templates
• Bulk email sending with retry logic
• Simple, clean interface

If you have any questions, don't hesitate to reach out.

Best regards,
The Mini Email CRM Team

P.S. Your email address ({email}) has been securely stored in our system."""
    )
    
    print(f"✓ Created template: {template.name}")
    print(f"   Subject: {template.subject}")
    print(f"   Placeholders: {', '.join(['{' + p + '}' for p in template.get_all_placeholders()])}")
    
    # 4. Show personalized emails
    print("\n4. Showing personalized email previews...")
    for i, contact in enumerate(contacts, 1):
        print(f"\n--- Email {i} for {contact.get_display_name()} ---")
        
        personalized = template.personalize_for_contact(contact)
        print(f"Subject: {personalized['subject']}")
        print("Body:")
        # Show first few lines of the body
        body_lines = personalized['body'].split('\n')
        for line in body_lines[:6]:  # Show first 6 lines
            print(f"  {line}")
        if len(body_lines) > 6:
            print("  ...")
    
    # 5. Demonstrate email service features
    print(f"\n{'-'*60}")
    print("5. Email Service Features Demonstration")
    print(f"{'-'*60}")
    
    service = EmailService()
    
    # Connection status
    print("\n📡 Connection Status:")
    status = service.get_connection_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Email validation
    print("\n✉️  Email Validation:")
    test_emails = ["valid@example.com", "invalid.email", ""]
    for email in test_emails:
        if email:
            # Create a test contact to validate
            try:
                test_contact = Contact(email=email, firstname="Test", lastname="User")
                validation_errors = test_contact.validate()
                result = "✓ Valid" if not validation_errors else f"✗ Invalid: {validation_errors[0]}"
            except Exception as e:
                result = f"✗ Invalid: {str(e)}"
        else:
            result = "✗ Invalid: Empty email"
        print(f"   {email or '(empty)'}: {result}")
    
    # Content validation
    print("\n📝 Content Validation:")
    test_contents = [
        ("Valid Subject", "Valid body content"),
        ("", "Body without subject"),
        ("Subject", ""),
        ("Very " + "long " * 50 + "subject", "Normal body")  # Long subject
    ]
    
    for subject, body in test_contents:
        errors = service.validate_email_content(subject, body)
        if errors:
            status = f"✗ Invalid: {errors[0]}"
        else:
            status = "✓ Valid"
        
        subject_preview = subject[:30] + "..." if len(subject) > 30 else subject
        body_preview = body[:30] + "..." if len(body) > 30 else body
        print(f"   '{subject_preview}' / '{body_preview}': {status}")
    
    # 6. Simulate bulk email sending
    print(f"\n{'-'*60}")
    print("6. Simulated Bulk Email Sending")
    print(f"{'-'*60}")
    
    print(f"\nWould send {len(contacts)} emails with the following results:")
    for i, contact in enumerate(contacts, 1):
        # Simulate different outcomes
        if i == 1:
            status_msg = "✅ SENT - Delivered successfully"
        elif i == 2:
            status_msg = "🔄 RETRY - Temporary failure, will retry"
        else:
            status_msg = "✅ SENT - Delivered successfully after retry"
        
        print(f"   {contact.get_display_name()}: {status_msg}")
    
    print(f"\nSummary: 3 emails processed, 3 sent successfully, 0 failed permanently")
    
    # 7. Configuration tips
    print(f"\n{'-'*60}")
    print("7. Configuration Tips")
    print(f"{'-'*60}")
    
    print("\nTo actually send emails, configure your .env file:")
    print("   SMTP_SERVER=smtp.gmail.com")
    print("   SMTP_PORT=587") 
    print("   SMTP_USERNAME=your-email@gmail.com")
    print("   SMTP_PASSWORD=your-app-password")
    print("\nFor Gmail, you'll need to:")
    print("   1. Enable 2-factor authentication")
    print("   2. Generate an App Password")
    print("   3. Use the App Password (not your regular password)")
    
    print(f"\n{'='*60}")
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("The email service is ready to use once configured.")
    print(f"{'='*60}")


if __name__ == "__main__":
    demo_email_service()
