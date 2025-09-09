"""
Compose Screen for Mini Email CRM
Step 2 of 4: Compose Email
Integrates the EmailEditor widget with from settings and navigation
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QGroupBox, QSpacerItem, QSizePolicy,
    QMessageBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ui.widgets.email_editor import EmailEditor


class ComposeScreen(QWidget):
    """
    Compose email screen - Step 2 of 4
    Matches Screen 2 design with EmailEditor integration
    """
    
    # Navigation signals
    back_clicked = pyqtSignal()
    preview_clicked = pyqtSignal(dict)  # Passes email data
    exit_clicked = pyqtSignal()
    
    # Content signals
    email_content_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.contact_count = 0
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
        """Create the header with step indicator and contact count"""
        layout = QHBoxLayout()
        
        # Step indicator
        step_label = QLabel("Step 2 of 4: Compose Email")
        step_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
            }
        """)
        layout.addWidget(step_label)
        
        # Spacer
        layout.addStretch()
        
        # Contact count status
        self.status_label = QLabel("Ready to send to 0 contacts")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
                background-color: #F5F5F5;
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid #DDDDDD;
            }
        """)
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
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #333333;
                border: 1px solid #DDDDDD;
                border-radius: 6px;
                margin: 3px 0;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 20)
        layout.setSpacing(15)
        
        # From Email field
        from_email_label = QLabel("From Email")
        from_email_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 11px;
                color: #333333;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(from_email_label)
        
        self.from_email_input = QLineEdit()
        self.from_email_input.setPlaceholderText("your-email@example.com")
        self.from_email_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 10px 12px;
                font-size: 12px;
                background-color: white;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        layout.addWidget(self.from_email_input)
        
        # Spacer between fields
        layout.addSpacing(10)
        
        # Email subject field
        subject_label = QLabel("Email subject")
        subject_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 11px;
                color: #333333;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(subject_label)
        
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter your email subject...")
        self.subject_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 10px 12px;
                font-size: 12px;
                background-color: white;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        layout.addWidget(self.subject_input)
        
        # Add some bottom spacing
        layout.addSpacing(15)
        
        group.setLayout(layout)
        return group
        
    def create_personalization_help(self):
        """Create the expanded personalization help section"""
        group = QGroupBox("Personalization help")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #333333;
                border: 1px solid #DDDDDD;
                border-radius: 6px;
                margin: 3px 0;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 20)
        layout.setSpacing(12)
        
        # Available placeholders label
        placeholders_label = QLabel("Available placeholders:")
        placeholders_label.setStyleSheet("""
            QLabel {
                font-weight: normal; 
                color: #333333; 
                margin: 5px 0;
                font-size: 11px;
            }
        """)
        layout.addWidget(placeholders_label)
        
        # Create expanded placeholder list
        self.placeholder_list = QListWidget()
        self.placeholder_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #2196F3;
                selection-color: white;
                font-family: monospace;
                font-size: 11px;
                min-height: 120px;
                max-height: 120px;
            }
            QListWidget::item {
                padding: 8px 10px;
                border-bottom: 1px solid #F0F0F0;
                color: #333333;
            }
            QListWidget::item:hover {
                background-color: #E3F2FD;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
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
        insert_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        layout.addWidget(insert_btn)
        
        # Add some bottom spacing
        layout.addSpacing(15)
        
        group.setLayout(layout)
        return group
        
    def create_email_body_section(self):
        """Create the email body section with just the EmailEditor"""
        # Create the EmailEditor widget
        self.email_editor = EmailEditor(max_characters=5000)
        
        # Connect EmailEditor signals
        self.email_editor.text_changed.connect(self.on_email_content_changed)
        self.email_editor.character_count_changed.connect(self.on_character_count_changed)
        self.email_editor.placeholder_inserted.connect(self.on_placeholder_inserted)
        
        return self.email_editor
        
    def create_navigation(self):
        """Create the navigation buttons"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Back button
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.on_back_clicked)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #333333;
                border: 2px solid #DDDDDD;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #EEEEEE;
                border-color: #CCCCCC;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        layout.addWidget(back_btn)
        
        # Spacer
        layout.addStretch()
        
        # Preview Emails button (primary)
        self.preview_btn = QPushButton("Preview Emails")
        self.preview_btn.clicked.connect(self.on_preview_clicked)
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        self.preview_btn.setEnabled(False)  # Disabled until content is ready
        layout.addWidget(self.preview_btn)
        
        # Exit button
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.on_exit_clicked)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #333333;
                border: 2px solid #DDDDDD;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #EEEEEE;
                border-color: #CCCCCC;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)
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
        email_data = self.get_email_data()
        self.email_content_changed.emit(email_data)
        
    def on_character_count_changed(self, current, max_count):
        """Handle character count changes"""
        # Could add additional handling here if needed
        pass
        
    def on_placeholder_inserted(self, placeholder):
        """Handle placeholder insertion"""
        # Could log or track placeholder usage
        pass
        
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
        """Validate the form and enable/disable preview button"""
        from_email = self.from_email_input.text().strip()
        subject = self.subject_input.text().strip()
        email_content = self.email_editor.get_plain_text().strip()
        
        # Basic validation
        has_from_email = bool(from_email and '@' in from_email)
        has_subject = bool(subject)
        has_content = bool(email_content)
        has_contacts = self.contact_count > 0
        
        # Enable preview button only if all required fields are filled
        is_valid = has_from_email and has_subject and has_content and has_contacts
        self.preview_btn.setEnabled(is_valid)
        
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
        """Get all email data as a dictionary"""
        return {
            'from_email': self.from_email_input.text().strip(),
            'subject': self.subject_input.text().strip(),
            'content_html': self.email_editor.get_html_content(),
            'content_plain': self.email_editor.get_plain_text(),
            'character_count': len(self.email_editor.get_plain_text()),
            'placeholders_used': self.get_placeholders_in_content()
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
        """Clear all form fields"""
        self.from_email_input.clear()
        self.subject_input.clear()
        self.email_editor.clear_content()
        
    def load_email_template(self, template_data):
        """Load an email template"""
        if 'subject' in template_data:
            self.set_subject(template_data['subject'])
        if 'content' in template_data:
            self.set_email_content(template_data['content'], template_data.get('is_html', False))
            
    def get_form_data(self):
        """Get all form data for external use"""
        return self.get_email_data()
        
    def set_enabled(self, enabled):
        """Enable or disable the entire form"""
        super().setEnabled(enabled)
        self.from_email_input.setEnabled(enabled)
        self.subject_input.setEnabled(enabled)
        self.email_editor.set_enabled(enabled)
