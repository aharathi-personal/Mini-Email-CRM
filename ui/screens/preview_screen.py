"""
Enhanced Preview Screen for Mini Email CRM
Task 17: Enhanced Preview Screen (Screen 3)
Contact list with search, email preview with headers, attachment validation warnings
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QGroupBox, QSpacerItem, QSizePolicy,
    QMessageBox, QListWidget, QListWidgetItem, QScrollArea,
    QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette

from core.template_engine import TemplateEngine
from models.contact import Contact
from models.attachment import Attachment, AttachmentType
from ui.styles.stylesheet import (
    BUTTON_STYLE, SUCCESS_BUTTON_STYLE, ERROR_BUTTON_STYLE,
    INPUT_STYLE, CARD_STYLE, TITLE_STYLE, SUBTITLE_STYLE, BODY_STYLE,
    PRIMARY_BLUE, SUCCESS_GREEN, ERROR_RED, LIGHT_GREY, BORDER_GREY,
    WARNING_ORANGE, DARK_GREY
)


class PreviewScreen(QWidget):
    """
    Enhanced Preview Screen - Step 3 of 4
    Task 17: Contact list and email preview with search and attachment validation
    """
    
    # Navigation signals
    previous_clicked = pyqtSignal()
    send_all_clicked = pyqtSignal(dict)  # Passes final email data
    exit_clicked = pyqtSignal()
    
    # Contact selection signal
    contact_selected = pyqtSignal(Contact)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Data storage
        self.contacts = []
        self.filtered_contacts = []
        self.current_contact_index = 0
        self.email_data = {}
        self.attachments = []
        self.attachment_errors = []
        
        # Template engine for personalization
        self.template_engine = TemplateEngine()
        
        # Search timer for delayed filtering
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.apply_contact_filter)
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Set up the preview screen UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # Main content area - split layout
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setChildrenCollapsible(False)
        
        # Left panel - Contact list with search
        left_panel = self.create_contact_list_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Email preview
        right_panel = self.create_email_preview_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions (1:2 ratio)
        content_splitter.setSizes([300, 600])
        content_splitter.setStretchFactor(0, 1)
        content_splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(content_splitter)
        
        # Navigation buttons
        nav_layout = self.create_navigation()
        main_layout.addLayout(nav_layout)
        
        self.setLayout(main_layout)
        
    def create_header(self):
        """Create the header with step indicator and status"""
        layout = QHBoxLayout()
        
        # Step indicator
        step_label = QLabel("Step 3 of 4: Preview Emails")
        step_label.setStyleSheet(TITLE_STYLE)
        layout.addWidget(step_label)
        
        # Spacer
        layout.addStretch()
        
        # Contact status (will be updated dynamically)
        self.contact_status_label = QLabel("0 contacts ready")
        self.contact_status_label.setStyleSheet(SUBTITLE_STYLE)
        layout.addWidget(self.contact_status_label)
        
        return layout
        
    def create_contact_list_panel(self):
        """Create the left panel with contact list and search"""
        panel = QGroupBox("Contacts")
        panel.setStyleSheet(CARD_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Search section
        search_layout = self.create_search_section()
        layout.addLayout(search_layout)
        
        # Contact count
        self.contact_count_label = QLabel("0 contacts")
        self.contact_count_label.setStyleSheet(SUBTITLE_STYLE)
        layout.addWidget(self.contact_count_label)
        
        # Contact list
        self.contact_list = QListWidget()
        self.contact_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {BORDER_GREY};
                border-radius: 4px;
                background-color: white;
                selection-background-color: {PRIMARY_BLUE};
                selection-color: white;
                font-size: 11px;
                min-height: 300px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid #F0F0F0;
                color: {DARK_GREY};
            }}
            QListWidget::item:hover {{
                background-color: #E3F2FD;
            }}
            QListWidget::item:selected {{
                background-color: {PRIMARY_BLUE};
                color: white;
            }}
        """)
        
        # Connect contact selection
        self.contact_list.currentRowChanged.connect(self.on_contact_selected)
        
        layout.addWidget(self.contact_list)
        
        # Navigation within contacts
        nav_layout = self.create_contact_navigation()
        layout.addLayout(nav_layout)
        
        panel.setLayout(layout)
        return panel
        
    def create_search_section(self):
        """Create the search functionality"""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Search label
        search_label = QLabel("Search contacts:")
        search_label.setStyleSheet(SUBTITLE_STYLE)
        layout.addWidget(search_label)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or email...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self.search_input)
        
        return layout
        
    def create_contact_navigation(self):
        """Create navigation buttons within contact list"""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        # Previous contact
        self.prev_contact_btn = QPushButton("◀ Previous")
        self.prev_contact_btn.clicked.connect(self.select_previous_contact)
        self.prev_contact_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {LIGHT_GREY};
                color: {DARK_GREY};
                border: 1px solid {BORDER_GREY};
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: #EEEEEE;
            }}
            QPushButton:disabled {{
                color: #999999;
                background-color: #F9F9F9;
            }}
        """)
        layout.addWidget(self.prev_contact_btn)
        
        # Contact position indicator
        self.position_label = QLabel("1 of 0")
        self.position_label.setStyleSheet(f"""
            QLabel {{
                color: {DARK_GREY};
                font-size: 10px;
                padding: 6px;
                text-align: center;
            }}
        """)
        layout.addWidget(self.position_label)
        
        # Next contact
        self.next_contact_btn = QPushButton("Next ▶")
        self.next_contact_btn.clicked.connect(self.select_next_contact)
        self.next_contact_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {LIGHT_GREY};
                color: {DARK_GREY};
                border: 1px solid {BORDER_GREY};
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: #EEEEEE;
            }}
            QPushButton:disabled {{
                color: #999999;
                background-color: #F9F9F9;
            }}
        """)
        layout.addWidget(self.next_contact_btn)
        
        return layout
        
    def create_email_preview_panel(self):
        """Create the right panel with email preview"""
        panel = QGroupBox("Email Preview")
        panel.setStyleSheet(CARD_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Email headers section
        headers_section = self.create_email_headers_section()
        layout.addWidget(headers_section)
        
        # Email content preview
        content_section = self.create_email_content_section()
        layout.addWidget(content_section)
        
        # Attachment list section
        attachments_section = self.create_attachments_section()
        layout.addWidget(attachments_section)
        
        # Validation warnings section
        warnings_section = self.create_validation_warnings_section()
        layout.addWidget(warnings_section)
        
        panel.setLayout(layout)
        return panel
        
    def create_email_headers_section(self):
        """Create the email headers display"""
        section = QFrame()
        section.setFrameStyle(QFrame.Box)
        section.setStyleSheet(f"""
            QFrame {{
                background-color: #FAFAFA;
                border: 1px solid {BORDER_GREY};
                border-radius: 4px;
                padding: 12px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # To field
        self.to_label = QLabel("To: (No contact selected)")
        self.to_label.setStyleSheet(f"""
            QLabel {{
                font-family: monospace;
                font-size: 11px;
                color: {DARK_GREY};
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.to_label)
        
        # From field
        self.from_label = QLabel("From: (Not set)")
        self.from_label.setStyleSheet(f"""
            QLabel {{
                font-family: monospace;
                font-size: 11px;
                color: {DARK_GREY};
            }}
        """)
        layout.addWidget(self.from_label)
        
        # Subject field
        self.subject_label = QLabel("Subject: (Not set)")
        self.subject_label.setStyleSheet(f"""
            QLabel {{
                font-family: monospace;
                font-size: 11px;
                color: {DARK_GREY};
            }}
        """)
        layout.addWidget(self.subject_label)
        
        section.setLayout(layout)
        return section
        
    def create_email_content_section(self):
        """Create the email content preview"""
        section = QGroupBox("Email Content")
        section.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {BORDER_GREY};
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {DARK_GREY};
                background-color: white;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)
        
        # Content preview area
        self.content_preview = QTextEdit()
        self.content_preview.setReadOnly(True)
        self.content_preview.setMinimumHeight(200)
        self.content_preview.setMaximumHeight(300)
        self.content_preview.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {BORDER_GREY};
                border-radius: 4px;
                background-color: white;
                font-size: 11px;
                color: {DARK_GREY};
                padding: 8px;
            }}
        """)
        self.content_preview.setPlaceholderText("Email content will appear here when a contact is selected...")
        layout.addWidget(self.content_preview)
        
        section.setLayout(layout)
        return section
        
    def create_attachments_section(self):
        """Create the attachments display section"""
        section = QGroupBox("Attachments")
        section.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {BORDER_GREY};
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: #E3F2FD;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {DARK_GREY};
                background-color: #E3F2FD;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)
        
        # Attachment summary
        self.attachment_summary = QLabel("📎 No attachments")
        self.attachment_summary.setStyleSheet(f"""
            QLabel {{
                color: {DARK_GREY};
                font-size: 11px;
                font-weight: bold;
                padding: 8px;
                background-color: white;
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.attachment_summary)
        
        # Attachment list
        self.attachment_list = QListWidget()
        self.attachment_list.setMaximumHeight(120)
        self.attachment_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {BORDER_GREY};
                border-radius: 4px;
                background-color: white;
                font-size: 10px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
                color: {DARK_GREY};
            }}
        """)
        layout.addWidget(self.attachment_list)
        
        section.setLayout(layout)
        return section
        
    def create_validation_warnings_section(self):
        """Create the validation warnings section"""
        self.warnings_section = QFrame()
        self.warnings_section.setFrameStyle(QFrame.NoFrame)
        self.warnings_section.setVisible(False)  # Hidden by default
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Warning message
        self.warning_message = QLabel()
        self.warning_message.setWordWrap(True)
        self.warning_message.setStyleSheet(f"""
            QLabel {{
                color: {ERROR_RED};
                font-size: 11px;
                background-color: #FFEBEE;
                border: 1px solid {ERROR_RED};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        layout.addWidget(self.warning_message)
        
        self.warnings_section.setLayout(layout)
        return self.warnings_section
        
    def create_navigation(self):
        """Create the navigation buttons"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Previous button
        previous_btn = QPushButton("Previous")
        previous_btn.clicked.connect(self.on_previous_clicked)
        previous_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {LIGHT_GREY};
                color: {DARK_GREY};
                border: 2px solid {BORDER_GREY};
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: #EEEEEE;
                border-color: #CCCCCC;
            }}
            QPushButton:pressed {{
                background-color: #E0E0E0;
            }}
        """)
        layout.addWidget(previous_btn)
        
        # Spacer
        layout.addStretch()
        
        # Send All button (primary)
        self.send_all_btn = QPushButton("Send All Emails")
        self.send_all_btn.clicked.connect(self.on_send_all_clicked)
        self.send_all_btn.setStyleSheet(SUCCESS_BUTTON_STYLE)
        self.send_all_btn.setEnabled(False)  # Disabled until data is loaded
        layout.addWidget(self.send_all_btn)
        
        # Exit button
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.on_exit_clicked)
        exit_btn.setStyleSheet(ERROR_BUTTON_STYLE)
        layout.addWidget(exit_btn)
        
        return layout
        
    def connect_signals(self):
        """Connect internal signals"""
        pass
        
    # Event handlers
    def on_previous_clicked(self):
        """Handle previous button click"""
        self.previous_clicked.emit()
        
    def on_send_all_clicked(self):
        """Handle send all button click"""
        if self.validate_all_data():
            final_data = self.get_final_email_data()
            self.send_all_clicked.emit(final_data)
        
    def on_exit_clicked(self):
        """Handle exit button click with confirmation"""
        reply = QMessageBox.question(
            self,
            "Exit Preview",
            "Are you sure you want to exit? You will lose the current email campaign.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.exit_clicked.emit()
            
    def on_search_text_changed(self, text):
        """Handle search text changes with delay"""
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms delay
        
    def on_contact_selected(self, row):
        """Handle contact selection from list"""
        if 0 <= row < len(self.filtered_contacts):
            self.current_contact_index = row
            contact = self.filtered_contacts[row]
            self.update_email_preview(contact)
            self.update_contact_navigation()
            self.contact_selected.emit(contact)
            
    # Contact navigation methods
    def select_previous_contact(self):
        """Select the previous contact in the filtered list"""
        if self.current_contact_index > 0:
            self.current_contact_index -= 1
            self.contact_list.setCurrentRow(self.current_contact_index)
            
    def select_next_contact(self):
        """Select the next contact in the filtered list"""
        if self.current_contact_index < len(self.filtered_contacts) - 1:
            self.current_contact_index += 1
            self.contact_list.setCurrentRow(self.current_contact_index)
            
    def update_contact_navigation(self):
        """Update contact navigation button states and position indicator"""
        contact_count = len(self.filtered_contacts)
        
        # Update navigation buttons
        self.prev_contact_btn.setEnabled(self.current_contact_index > 0)
        self.next_contact_btn.setEnabled(self.current_contact_index < contact_count - 1)
        
        # Update position indicator
        if contact_count > 0:
            self.position_label.setText(f"{self.current_contact_index + 1} of {contact_count}")
        else:
            self.position_label.setText("0 of 0")
            
    # Search and filtering methods
    def apply_contact_filter(self):
        """Apply search filter to contacts"""
        search_text = self.search_input.text().strip().lower()
        
        if not search_text:
            self.filtered_contacts = self.contacts.copy()
        else:
            self.filtered_contacts = [
                contact for contact in self.contacts
                if (search_text in contact.get_full_name().lower() or 
                    search_text in contact.email.lower())
            ]
        
        self.update_contact_list()
        
        # Reset selection to first contact if available
        if self.filtered_contacts:
            self.current_contact_index = 0
            self.contact_list.setCurrentRow(0)
        else:
            self.current_contact_index = 0
            self.clear_email_preview()
            
    def update_contact_list(self):
        """Update the contact list widget"""
        self.contact_list.clear()
        
        for contact in self.filtered_contacts:
            item = QListWidgetItem(contact.get_display_name())
            item.setData(Qt.UserRole, contact)
            self.contact_list.addItem(item)
        
        # Update contact count
        total_count = len(self.contacts)
        filtered_count = len(self.filtered_contacts)
        
        if filtered_count == total_count:
            self.contact_count_label.setText(f"{total_count} contacts")
        else:
            self.contact_count_label.setText(f"{filtered_count} of {total_count} contacts")
            
        self.update_contact_navigation()
        
    # Email preview methods
    def update_email_preview(self, contact):
        """Update email preview for selected contact"""
        if not contact or not self.email_data:
            self.clear_email_preview()
            return
            
        # Update headers
        self.to_label.setText(f"To: {contact.get_display_name()}")
        self.from_label.setText(f"From: {self.email_data.get('from_email', '(Not set)')}")
        
        # Process subject with personalization
        subject = self.email_data.get('subject', '(Not set)')
        if subject != '(Not set)':
            personalized_subject = self.template_engine.replace_placeholders(
                subject, contact.get_personalization_data()
            )
            self.subject_label.setText(f"Subject: {personalized_subject}")
        else:
            self.subject_label.setText("Subject: (Not set)")
            
        # Process email content with personalization
        content = self.email_data.get('content_plain', '')
        if content:
            personalized_content = self.template_engine.replace_placeholders(
                content, contact.get_personalization_data()
            )
            self.content_preview.setPlainText(personalized_content)
        else:
            self.content_preview.setPlainText("(No email content)")
            
    def clear_email_preview(self):
        """Clear the email preview"""
        self.to_label.setText("To: (No contact selected)")
        self.from_label.setText("From: (Not set)")
        self.subject_label.setText("Subject: (Not set)")
        self.content_preview.setPlaceholderText("Email content will appear here when a contact is selected...")
        self.content_preview.clear()
        
    # Attachment methods
    def update_attachments_display(self):
        """Update the attachments display"""
        self.attachment_list.clear()
        
        if not self.attachments:
            self.attachment_summary.setText("📎 No attachments")
            self.attachment_summary.setStyleSheet(f"""
                QLabel {{
                    color: {DARK_GREY};
                    font-size: 11px;
                    font-weight: bold;
                    padding: 8px;
                    background-color: white;
                    border-radius: 4px;
                }}
            """)
            return
            
        # Update summary
        total_size = sum(att.get('file_size', 0) for att in self.attachments)
        count = len(self.attachments)
        
        if total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        else:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
            
        self.attachment_summary.setText(f"📎 {count} file{'s' if count != 1 else ''} ({size_str})")
        self.attachment_summary.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY_BLUE};
                font-size: 11px;
                font-weight: bold;
                padding: 8px;
                background-color: white;
                border-radius: 4px;
            }}
        """)
        
        # Add attachments to list
        for attachment in self.attachments:
            filename = attachment.get('filename', 'Unknown file')
            file_size = attachment.get('file_size_formatted', 'Unknown size')
            att_type = attachment.get('attachment_type', 'other')
            
            # Choose icon based on type
            if att_type == 'pdf':
                icon = "📄"
            elif att_type == 'image':
                icon = "🖼️"
            elif att_type == 'document':
                icon = "📃"
            else:
                icon = "📎"
                
            item_text = f"{icon} {filename} ({file_size})"
            item = QListWidgetItem(item_text)
            self.attachment_list.addItem(item)
            
    # Validation methods
    def update_validation_warnings(self):
        """Update validation warnings display"""
        if self.attachment_errors:
            warning_text = "⚠️ Attachment Issues:\n• " + "\n• ".join(self.attachment_errors)
            self.warning_message.setText(warning_text)
            self.warnings_section.setVisible(True)
        else:
            self.warnings_section.setVisible(False)
            
    def validate_all_data(self):
        """Validate all data before sending"""
        if not self.contacts:
            QMessageBox.warning(self, "No Contacts", "No contacts available to send emails to.")
            return False
            
        if not self.email_data:
            QMessageBox.warning(self, "No Email Data", "No email data available.")
            return False
            
        if self.attachment_errors:
            reply = QMessageBox.question(
                self,
                "Attachment Issues",
                f"There are attachment validation issues:\n\n" + 
                "\n".join(self.attachment_errors) + 
                "\n\nDo you want to continue sending anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return False
                
        return True
        
    # Public interface methods
    def set_contacts(self, contacts):
        """Set the contact list"""
        self.contacts = contacts
        self.filtered_contacts = contacts.copy()
        self.update_contact_list()
        
        # Update status
        count = len(contacts)
        self.contact_status_label.setText(f"{count} contact{'s' if count != 1 else ''} ready")
        
        # Select first contact if available
        if contacts:
            self.current_contact_index = 0
            self.contact_list.setCurrentRow(0)
            
        # Enable send button if we have contacts and email data
        self.send_all_btn.setEnabled(bool(contacts and self.email_data))
        
    def set_email_data(self, email_data):
        """Set the email data"""
        self.email_data = email_data
        
        # Extract attachments if present
        self.attachments = email_data.get('attachments', [])
        self.attachment_errors = email_data.get('attachment_errors', [])
        
        # Update displays
        self.update_attachments_display()
        self.update_validation_warnings()
        
        # Update email preview for current contact
        if self.filtered_contacts and self.current_contact_index < len(self.filtered_contacts):
            current_contact = self.filtered_contacts[self.current_contact_index]
            self.update_email_preview(current_contact)
            
        # Enable send button if we have contacts and email data
        self.send_all_btn.setEnabled(bool(self.contacts and email_data))
        
    def get_final_email_data(self):
        """Get final email data for sending"""
        return {
            'email_data': self.email_data,
            'contacts': self.contacts,
            'total_emails': len(self.contacts),
            'attachments': self.attachments,
            'attachment_errors': self.attachment_errors,
            'has_validation_issues': bool(self.attachment_errors)
        }
        
    def clear_data(self):
        """Clear all data"""
        self.contacts = []
        self.filtered_contacts = []
        self.email_data = {}
        self.attachments = []
        self.attachment_errors = []
        self.current_contact_index = 0
        
        # Clear UI
        self.search_input.clear()
        self.contact_list.clear()
        self.clear_email_preview()
        self.update_attachments_display()
        self.update_validation_warnings()
        self.update_contact_navigation()
        
        # Update status
        self.contact_status_label.setText("0 contacts ready")
        self.contact_count_label.setText("0 contacts")
        self.send_all_btn.setEnabled(False)
        
    def get_selected_contact(self):
        """Get currently selected contact"""
        if (self.filtered_contacts and 
            0 <= self.current_contact_index < len(self.filtered_contacts)):
            return self.filtered_contacts[self.current_contact_index]
        return None


# For development: run screen without test data
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    print("📋 PreviewScreen - Enhanced Preview Screen for Mini Email CRM")
    print("🚀 Starting clean preview screen (no test data)")
    print("💡 For full testing with sample data, run: python demos/demo_preview_screen.py")
    print("📝 For automated tests, run: python tests/test_preview_screen.py")
    print()
    
    app = QApplication(sys.argv)
    
    # Create clean screen
    screen = PreviewScreen()
    screen.setWindowTitle("Step 3 - Preview")
    screen.resize(1200, 800)
    
    # Connect basic signals
    screen.exit_clicked.connect(app.quit)
    
    # Show instructions
    print("📖 Instructions:")
    print("• This is the clean preview screen without test data")
    print("• Use the demo file to see it with sample contacts and emails")
    print("• The screen shows the UI layout and styling")
    print("• All functionality is implemented but needs data to be useful")
    
    screen.show()
    sys.exit(app.exec_())