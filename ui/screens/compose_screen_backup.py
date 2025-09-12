"""
Enhanced Compose Screen for Mini Email CRM
Task 16: Enhanced Compose Screen (Screen 2)
Two-column layout with settings vs email body, attachment integration,
contact count display, attachment summary, and validation feedback
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QGroupBox, QSpacerItem, QSizePolicy,
    QMessageBox, QListWidget, QListWidgetItem, QScrollArea,
    QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette

from ui.widgets.email_editor import EmailEditor
from ui.styles.stylesheet import (
    BUTTON_STYLE, SUCCESS_BUTTON_STYLE, ERROR_BUTTON_STYLE,
    INPUT_STYLE, CARD_STYLE, HEADER_STYLE, BODY_STYLE, SMALL_TEXT_STYLE,
    PRIMARY_BLUE, SUCCESS_GREEN, ERROR_RED, WARNING_ORANGE,
    WHITE, LIGHT_GREY, BORDER_GREY, TEXT_DARK, NEUTRAL_GREY,
    ATTACHMENT_BG, ATTACHMENT_BORDER, ATTACHMENT_HOVER,
    ERROR_TEXT_STYLE, SUCCESS_TEXT_STYLE, WARNING_TEXT_STYLE,
    SPACING_MEDIUM, SPACING_LARGE, BORDER_RADIUS_CARDS
)


class ComposeScreen(QWidget):
    """
    Enhanced Compose Email Screen - Step 2 of 4
    Task 16: Two-column layout with attachment integration and enhanced features
    """
    
    # Navigation signals
    back_clicked = pyqtSignal()
    preview_clicked = pyqtSignal(dict)  # Passes email data with attachments
    exit_clicked = pyqtSignal()
    
    # Content signals
    email_content_changed = pyqtSignal(dict)
    attachment_validation_changed = pyqtSignal(bool)  # True if all attachments valid
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.contact_count = 0
        self.attachment_errors = []
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_attachments_delayed)
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Set up the compose screen UI based on Screen 2 design"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # Left side - From settings and Personalization help (stacked)
        left_panel = self.create_left_panel()
        content_layout.addWidget(left_panel, 1)
        
        # Right side - Email body (EmailEditor only)
        email_body_section = self.create_email_body_section()
        content_layout.addWidget(email_body_section, 2)
        
        main_layout.addLayout(content_layout)
        
        # Navigation buttons (below everything)
        nav_layout = self.create_navigation()
        main_layout.addLayout(nav_layout)
        
        self.setLayout(main_layout)
        
    def create_header(self):
        """Create the enhanced header with step indicator, contact count, and attachment summary"""
        layout = QHBoxLayout()
        
        # Step indicator
        step_label = QLabel("Step 2 of 4: Compose Email")
        step_label.setStyleSheet(HEADER_STYLE)
        layout.addWidget(step_label)
        
        # Spacer
        layout.addStretch()
        
        # Attachment summary (when attachments exist)
        self.attachment_summary_label = QLabel("")
        self.attachment_summary_label.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY_BLUE};
                font-size: 10px;
                font-weight: bold;
                padding: 4px 8px;
                background-color: #E3F2FD;
                border: 1px solid {PRIMARY_BLUE};
                border-radius: 4px;
                margin-right: 8px;
            }}
        """)
        self.attachment_summary_label.setVisible(False)
        layout.addWidget(self.attachment_summary_label)
        
        # Contact count status
        self.status_label = QLabel("Ready to send to 0 contacts")
        self.status_label.setStyleSheet(BODY_STYLE)
        layout.addWidget(self.status_label)
        
        return layout
        
    def create_left_panel(self):
        """Create the left panel with From settings and Personalization help stacked"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # From settings (compact)
        from_settings = self.create_from_settings()
        layout.addWidget(from_settings)
        
        # Personalization help (expanded)
        personalization_help = self.create_personalization_help()
        layout.addWidget(personalization_help)
        
        panel.setLayout(layout)
        return panel
        
    def create_from_settings(self):
        """Create the compact From settings section"""
        group = QGroupBox("From settings")
        group.setStyleSheet(CARD_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 20)
        layout.setSpacing(15)
        
        # From Email field
        from_email_label = QLabel("From Email")
        from_email_label.setStyleSheet(BODY_STYLE)
        layout.addWidget(from_email_label)
        
        self.from_email_input = QLineEdit()
        self.from_email_input.setPlaceholderText("your-email@example.com")
        self.from_email_input.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.from_email_input)
        
        # Spacer between fields
        layout.addSpacing(10)
        
        # Email subject field
        subject_label = QLabel("Email subject")
        subject_label.setStyleSheet(BODY_STYLE)
        layout.addWidget(subject_label)
        
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter your email subject...")
        self.subject_input.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.subject_input)
        
        # Add some bottom spacing
        layout.addSpacing(15)
        
        group.setLayout(layout)
        return group
        
    def create_personalization_help(self):
        """Create the expanded personalization help section"""
        group = QGroupBox("Personalization help")
        group.setStyleSheet(CARD_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 20)
        layout.setSpacing(12)
        
        # Available placeholders label
        placeholders_label = QLabel("Available placeholders:")
        placeholders_label.setStyleSheet(BODY_STYLE)
        layout.addWidget(placeholders_label)
        
        # Create expanded placeholder list
        self.placeholder_list = QListWidget()
        self.placeholder_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {NEUTRAL_BORDER};
                border-radius: 4px;
                background-color: rgba(255, 255, 255, 0.05);
                selection-background-color: #2196F3;
                selection-color: white;
                font-family: monospace;
                font-size: 11px;
                min-height: 120px;
                max-height: 120px;
                color: {TEXT_PRIMARY};
            }}
            QListWidget::item {{
                padding: 8px 10px;
                border-bottom: 1px solid rgba(128, 128, 128, 0.15);
                color: {TEXT_PRIMARY};
            }}
            QListWidget::item:hover {{
                background-color: rgba(33, 150, 243, 0.1);
            }}
            QListWidget::item:selected {{
                background-color: {PRIMARY_BLUE};
                color: white;
            }}
        """)
        
        # Add placeholders to list
        for placeholder in ['{firstname}', '{lastname}', '{email}']:
            item = QListWidgetItem(placeholder)
            item.setToolTip(f"Double-click to insert {placeholder}")
            self.placeholder_list.addItem(item)
            
        # Connect double-click to insert placeholder
        self.placeholder_list.itemDoubleClicked.connect(self.insert_placeholder)
        
        layout.addWidget(self.placeholder_list)
        
        # Expanded insert button
        insert_btn = QPushButton("Insert Selected")
        insert_btn.clicked.connect(self.insert_selected_placeholder)
        insert_btn.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(insert_btn)
        
        # Add some bottom spacing
        layout.addSpacing(15)
        
        group.setLayout(layout)
        return group
        
    def create_email_body_section(self):
        """Create the enhanced email body section with EmailEditor and attachment feedback"""
        # Main container for email body
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Create the EmailEditor widget
        self.email_editor = EmailEditor(max_characters=5000)
        layout.addWidget(self.email_editor)
        
        # Attachment validation feedback area
        self.validation_feedback = self.create_validation_feedback_area()
        layout.addWidget(self.validation_feedback)
        
        # Email body preview with attachment indicators
        self.preview_area = self.create_preview_area()
        layout.addWidget(self.preview_area)
        
        # Connect EmailEditor signals
        self.email_editor.text_changed.connect(self.on_email_content_changed)
        self.email_editor.character_count_changed.connect(self.on_character_count_changed)
        self.email_editor.placeholder_inserted.connect(self.on_placeholder_inserted)
        self.email_editor.attachment_added.connect(self.on_attachment_added)
        self.email_editor.attachment_removed.connect(self.on_attachment_removed)
        self.email_editor.attachments_changed.connect(self.on_attachments_changed)
        
        container.setLayout(layout)
        return container
        
    def create_validation_feedback_area(self):
        """Create area for attachment validation feedback"""
        feedback_area = QFrame()
        feedback_area.setFrameStyle(QFrame.NoFrame)
        feedback_area.setStyleSheet("QFrame { background-color: transparent; }")
        feedback_area.setVisible(False)  # Hidden by default
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Validation message label
        self.validation_message = QLabel()
        self.validation_message.setWordWrap(True)
        self.validation_message.setStyleSheet(f"""
            QLabel {{
                color: {ERROR_RED};
                font-size: 11px;
                background-color: rgba(244, 67, 54, 0.08);
                border: 1px solid {ERROR_RED};
                border-radius: 4px;
                padding: 8px;
                margin: 4px 0px;
            }}
        """)
        layout.addWidget(self.validation_message)
        
        feedback_area.setLayout(layout)
        return feedback_area
        
    def create_preview_area(self):
        """Create collapsible email preview area with attachment indicators"""
        preview_container = QGroupBox("Email Preview")
        preview_container.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {NEUTRAL_BORDER};
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: {NEUTRAL_BG_PRIMARY};
                color: {TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {TEXT_PRIMARY};
                background-color: {NEUTRAL_BG_PRIMARY};
            }}
        """)
        preview_container.setCheckable(True)
        preview_container.setChecked(False)  # Collapsed by default
        preview_container.setMaximumHeight(200)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)
        
        # Preview text area (read-only)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(120)
        self.preview_text.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {NEUTRAL_BORDER};
                border-radius: 4px;
                background-color: rgba(255, 255, 255, 0.03);
                font-size: 11px;
                color: {TEXT_PRIMARY};
            }}
        """)
        self.preview_text.setPlaceholderText("Email preview will appear here...")
        layout.addWidget(self.preview_text)
        
        # Attachment indicators
        self.attachment_indicators = QLabel("📎 No attachments")
        self.attachment_indicators.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 10px;
                padding: 4px 8px;
                background-color: {NEUTRAL_BG_SECONDARY};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.attachment_indicators)
        
        preview_container.setLayout(layout)
        return preview_container
        
    def create_navigation(self):
        """Create the navigation buttons"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Back button
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.on_back_clicked)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {NEUTRAL_BG_SECONDARY};
                color: {TEXT_PRIMARY};
                border: 2px solid {NEUTRAL_BORDER};
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: rgba(128, 128, 128, 0.15);
                border-color: rgba(128, 128, 128, 0.3);
            }}
            QPushButton:pressed {{
                background-color: rgba(128, 128, 128, 0.2);
            }}
        """)
        layout.addWidget(back_btn)
        
        # Spacer
        layout.addStretch()
        
        # Preview Emails button (primary)
        self.preview_btn = QPushButton("Preview Emails")
        self.preview_btn.clicked.connect(self.on_preview_clicked)
        self.preview_btn.setStyleSheet(BUTTON_STYLE)
        self.preview_btn.setEnabled(False)  # Disabled until content is ready
        layout.addWidget(self.preview_btn)
        
        # Exit button
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.on_exit_clicked)
        exit_btn.setStyleSheet(ERROR_BUTTON_STYLE)
        layout.addWidget(exit_btn)
        
        return layout
        
    def connect_signals(self):
        """Connect internal signals"""
        # Connect input field changes to validation
        self.from_email_input.textChanged.connect(self.validate_form)
        self.subject_input.textChanged.connect(self.validate_form)
        
    # Event handlers
    def on_back_clicked(self):
        """Handle back button click"""
        self.back_clicked.emit()
        
    def on_preview_clicked(self):
        """Handle preview button click"""
        if self.validate_email_data():
            email_data = self.get_email_data()
            self.preview_clicked.emit(email_data)
        
    def on_exit_clicked(self):
        """Handle exit button click with confirmation"""
        reply = QMessageBox.question(
            self,
            "Exit Compose",
            "Are you sure you want to exit? Any unsaved changes will be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.exit_clicked.emit()
            
    def on_email_content_changed(self, html_content):
        """Handle email content changes from EmailEditor"""
        self.validate_form()
        self.update_preview()
        email_data = self.get_email_data()
        self.email_content_changed.emit(email_data)
        
    def on_character_count_changed(self, current, max_count):
        """Handle character count changes"""
        # Update preview when character count changes
        self.update_preview()
        
    def on_placeholder_inserted(self, placeholder):
        """Handle placeholder insertion"""
        # Update preview when placeholders are inserted
        self.update_preview()
        
    def on_attachment_added(self, filename):
        """Handle attachment added"""
        print(f"📎 Attachment added: {filename}")
        self.update_attachment_summary()
        self.update_attachment_indicators()
        self.validate_form()
        # Trigger validation after a short delay to allow for UI updates
        self.validation_timer.start(500)
        
    def on_attachment_removed(self, filename):
        """Handle attachment removed"""
        print(f"📎 Attachment removed: {filename}")
        self.update_attachment_summary()
        self.update_attachment_indicators()
        self.validate_form()
        self.clear_validation_feedback()
        
    def on_attachments_changed(self, count, total_size):
        """Handle attachment count/size changes"""
        self.update_attachment_summary()
        self.update_attachment_indicators()
        self.validate_form()
        
    def update_attachment_summary(self):
        """Update attachment summary in header"""
        if self.email_editor.has_attachments():
            summary = self.email_editor.get_attachment_summary()
            count = summary['count']
            size = summary['total_size_formatted']
            self.attachment_summary_label.setText(f"📎 {count} file{'s' if count != 1 else ''} ({size})")
            self.attachment_summary_label.setVisible(True)
        else:
            self.attachment_summary_label.setVisible(False)
            
    def update_attachment_indicators(self):
        """Update attachment indicators in preview area"""
        if self.email_editor.has_attachments():
            summary = self.email_editor.get_attachment_summary()
            count = summary['count']
            size = summary['total_size_formatted']
            types = summary['types']
            
            # Create type breakdown
            type_parts = []
            if types['pdf'] > 0:
                type_parts.append(f"{types['pdf']} PDF")
            if types['image'] > 0:
                type_parts.append(f"{types['image']} image{'s' if types['image'] != 1 else ''}")
            if types['document'] > 0:
                type_parts.append(f"{types['document']} document{'s' if types['document'] != 1 else ''}")
            if types['other'] > 0:
                type_parts.append(f"{types['other']} other")
                
            type_text = ", ".join(type_parts) if type_parts else "files"
            self.attachment_indicators.setText(f"📎 {count} attachment{'s' if count != 1 else ''} ({size}) - {type_text}")
            self.attachment_indicators.setStyleSheet(f"""
                QLabel {{
                    color: {PRIMARY_BLUE};
                    font-size: 10px;
                    font-weight: bold;
                    padding: 4px 8px;
                    background-color: #E3F2FD;
                    border-radius: 3px;
                }}
            """)
        else:
            self.attachment_indicators.setText("📎 No attachments")
            self.attachment_indicators.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_SECONDARY};
                    font-size: 10px;
                    padding: 4px 8px;
                    background-color: {NEUTRAL_BG_SECONDARY};
                    border-radius: 3px;
                }}
            """)
            
    def update_preview(self):
        """Update email preview with current content"""
        # Get email content
        from_email = self.from_email_input.text().strip()
        subject = self.subject_input.text().strip()
        content = self.email_editor.get_plain_text().strip()
        
        # Build preview
        preview_lines = []
        if from_email:
            preview_lines.append(f"From: {from_email}")
        if subject:
            preview_lines.append(f"Subject: {subject}")
        if content:
            preview_lines.append(f"\n{content[:200]}{'...' if len(content) > 200 else ''}")
        else:
            preview_lines.append("\n(No email content)")
            
        preview_text = "\n".join(preview_lines)
        self.preview_text.setPlainText(preview_text)
        
    def validate_attachments_delayed(self):
        """Validate attachments with delay to avoid excessive validation"""
        self.attachment_errors = self.email_editor.validate_attachments()
        
        if self.attachment_errors:
            self.show_validation_feedback(self.attachment_errors)
            self.attachment_validation_changed.emit(False)
        else:
            self.clear_validation_feedback()
            self.attachment_validation_changed.emit(True)
            
    def show_validation_feedback(self, errors):
        """Show attachment validation errors"""
        if errors:
            error_text = "Attachment Issues:\n• " + "\n• ".join(errors)
            self.validation_message.setText(error_text)
            self.validation_feedback.setVisible(True)
        else:
            self.clear_validation_feedback()
            
    def clear_validation_feedback(self):
        """Clear validation feedback"""
        self.validation_feedback.setVisible(False)
        self.validation_message.setText("")
        
    def insert_placeholder(self, item):
        """Insert a placeholder from the personalization list"""
        placeholder = item.text()
        cursor = self.email_editor.text_editor.textCursor()
        cursor.insertText(placeholder)
        self.email_editor.text_editor.setFocus()
        
    def insert_selected_placeholder(self):
        """Insert the currently selected placeholder"""
        current_item = self.placeholder_list.currentItem()
        if current_item:
            self.insert_placeholder(current_item)
        
    # Data and validation methods
    def validate_form(self):
        """Enhanced validation including attachments"""
        from_email = self.from_email_input.text().strip()
        subject = self.subject_input.text().strip()
        email_content = self.email_editor.get_plain_text().strip()
        
        # Basic validation
        has_from_email = bool(from_email and '@' in from_email)
        has_subject = bool(subject)
        has_content = bool(email_content)
        has_contacts = self.contact_count > 0
        
        # Attachment validation
        attachments_valid = len(self.attachment_errors) == 0
        
        # Enable preview button only if all validations pass
        is_valid = has_from_email and has_subject and has_content and has_contacts and attachments_valid
        self.preview_btn.setEnabled(is_valid)
        
        # Update button style based on validation state
        if not attachments_valid and self.email_editor.has_attachments():
            self.preview_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {WARNING_ORANGE};
                    color: white;
                    border: 2px solid {WARNING_ORANGE};
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 100px;
                    min-height: 36px;
                }}
                QPushButton:disabled {{
                    background-color: {NEUTRAL_BG_SECONDARY};
                    color: {TEXT_DISABLED};
                    border-color: {NEUTRAL_BORDER};
                }}
            """)
        else:
            self.preview_btn.setStyleSheet(BUTTON_STYLE)
            
        return is_valid
        
    def validate_email_data(self):
        """Validate email data before proceeding"""
        email_data = self.get_email_data()
        
        # Check for empty fields
        if not email_data['from_email']:
            QMessageBox.warning(self, "Missing Information", "Please enter a from email address.")
            self.from_email_input.setFocus()
            return False
            
        if not email_data['subject']:
            QMessageBox.warning(self, "Missing Information", "Please enter an email subject.")
            self.subject_input.setFocus()
            return False
            
        if not email_data['content_plain'].strip():
            QMessageBox.warning(self, "Missing Information", "Please enter email content.")
            self.email_editor.text_editor.setFocus()
            return False
            
        # Basic email validation
        if '@' not in email_data['from_email'] or '.' not in email_data['from_email']:
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid from email address.")
            self.from_email_input.setFocus()
            return False
            
        return True
        
    def get_email_data(self):
        """Get all email data including attachments as a dictionary"""
        return {
            'from_email': self.from_email_input.text().strip(),
            'subject': self.subject_input.text().strip(),
            'content_html': self.email_editor.get_html_content(),
            'content_plain': self.email_editor.get_plain_text(),
            'character_count': len(self.email_editor.get_plain_text()),
            'placeholders_used': self.get_placeholders_in_content(),
            'attachments': self.email_editor.get_attachment_data(),
            'attachment_count': self.email_editor.get_attachment_count(),
            'attachment_summary': self.email_editor.get_attachment_summary(),
            'attachment_errors': self.attachment_errors.copy()
        }
        
    def get_placeholders_in_content(self):
        """Get list of placeholders used in the email content"""
        content = self.email_editor.get_plain_text()
        used_placeholders = []
        
        for placeholder in self.email_editor.available_placeholders:
            if placeholder in content:
                used_placeholders.append(placeholder)
                
        return used_placeholders
        
    # Public interface methods
    def set_contact_count(self, count):
        """Set the number of contacts to send to"""
        self.contact_count = count
        self.status_label.setText(f"Ready to send to {count} contacts")
        self.validate_form()  # Re-validate with new contact count
        
    def set_from_email(self, email):
        """Set the from email address"""
        self.from_email_input.setText(email)
        
    def set_subject(self, subject):
        """Set the email subject"""
        self.subject_input.setText(subject)
        
    def set_email_content(self, content, is_html=False):
        """Set the email content"""
        self.email_editor.set_content(content, is_html)
        
    def clear_form(self):
        """Clear all form fields including attachments"""
        self.from_email_input.clear()
        self.subject_input.clear()
        self.email_editor.clear_content()
        self.email_editor.clear_attachments()
        self.clear_validation_feedback()
        self.update_attachment_summary()
        self.update_attachment_indicators()
        self.update_preview()
        
    def load_email_template(self, template_data):
        """Load an email template"""
        if 'subject' in template_data:
            self.set_subject(template_data['subject'])
        if 'content' in template_data:
            self.set_email_content(template_data['content'], template_data.get('is_html', False))
        # Note: Templates don't include attachments for security reasons
            
    def get_form_data(self):
        """Get all form data for external use including attachments"""
        return self.get_email_data()
        
    def set_enabled(self, enabled):
        """Enable or disable the entire form"""
        super().setEnabled(enabled)
        self.from_email_input.setEnabled(enabled)
        self.subject_input.setEnabled(enabled)
        self.email_editor.set_enabled(enabled)
        
    # New attachment-related public methods
    def get_attachment_summary(self):
        """Get attachment summary for external use"""
        return self.email_editor.get_attachment_summary()
        
    def has_attachments(self):
        """Check if email has attachments"""
        return self.email_editor.has_attachments()
        
    def get_attachments(self):
        """Get all attachments"""
        return self.email_editor.get_attachments()
        
    def validate_all_attachments(self):
        """Validate all attachments and return errors"""
        return self.email_editor.validate_attachments()
        
    def clear_attachments(self):
        """Clear all attachments"""
        self.email_editor.clear_attachments()
        self.clear_validation_feedback()
        self.update_attachment_summary()
        self.update_attachment_indicators()
        
    def get_validation_errors(self):
        """Get current validation errors"""
        return self.attachment_errors.copy()


# Test the enhanced screen directly
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    screen = ComposeScreen()
    screen.setWindowTitle("Enhanced Compose Screen Test - Task 16")
    screen.resize(1200, 800)  # Larger for better layout testing
    
    # Set test data
    screen.set_contact_count(25)
    screen.set_from_email("test@minicrm.com")
    
    # Connect signals for testing
    screen.exit_clicked.connect(screen.close)
    screen.attachment_validation_changed.connect(
        lambda valid: print(f"📎 Attachment validation: {'✅ Valid' if valid else '❌ Invalid'}")
    )
    
    screen.show()
    
    print("✅ Enhanced Compose Screen launched successfully!")
    print("🆕 Task 16 Features:")
    print("✅ Two-column layout (settings vs email body)")
    print("✅ From Email and Subject inputs")
    print("✅ Enhanced email editor with attachments")
    print("✅ Contact count in header")
    print("✅ Attachment summary display")
    print("✅ Attachment file size validation feedback")
    print("✅ Email body preview with attachment indicators")
    print("✅ Back/Preview/Exit buttons")
    print("\n📋 Test Features:")
    print("• Drag and drop files to attach")
    print("• Watch attachment summary in header")
    print("• Check validation feedback for large files")
    print("• Toggle email preview to see attachment indicators")
    print("• Fill form and watch preview button enable")
    
    sys.exit(app.exec_())
