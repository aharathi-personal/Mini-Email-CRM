"""
Enhanced Preview Screen for Mini Email CRM
Task 17: Enhanced Preview Screen (Screen 3)
Contact list with search, email preview with headers, attachment validation warnings

Prompt: Can you scan the entire codebase and summarize the color scheme and UI design being using for dark mode and light mode.

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

# Import new theme system
from ui.base.themed_widgets import ThemedWidget, get_current_theme_colors, apply_button_style

# Import legacy styles for backward compatibility during transition
from ui.styles.stylesheet import (
    BUTTON_STYLE, SUCCESS_BUTTON_STYLE, ERROR_BUTTON_STYLE,
    INPUT_STYLE, CARD_STYLE, TITLE_STYLE, SUBTITLE_STYLE, BODY_STYLE,
    PRIMARY_BLUE, SUCCESS_GREEN, ERROR_RED, LIGHT_GREY, BORDER_GREY,
    WARNING_ORANGE, DARK_GREY
)


class PreviewScreen(ThemedWidget):
    """
    Enhanced Preview Screen - Step 3 of 4
    Task 17: Contact list and email preview with search and attachment validation
    Now inherits from ThemedWidget for automatic theme support
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
    
    def get_widget_stylesheet(self) -> str:
        """Override to provide custom stylesheet for preview screen"""
        # Use the full dynamic stylesheet
        return self.stylesheet_generator.generate_stylesheet()
    
    def apply_theme_customizations(self):
        """Apply custom theme-specific changes beyond stylesheets"""
        theme = self.get_current_theme()
        
        # Update button styles using the theme system
        if hasattr(self, 'previous_button'):
            apply_button_style(self.previous_button, "primary")
        
        if hasattr(self, 'send_all_button'):
            apply_button_style(self.send_all_button, "success")
        
        if hasattr(self, 'exit_button'):
            apply_button_style(self.exit_button, "error")
        
        # Update contact navigation buttons
        if hasattr(self, 'prev_contact_btn'):
            self._update_navigation_button_style(self.prev_contact_btn)
        
        if hasattr(self, 'next_contact_btn'):
            self._update_navigation_button_style(self.next_contact_btn)
    
    def _update_navigation_button_style(self, button):
        """Update navigation button style with current theme"""
        theme = self.get_current_theme()
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['surface_container']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                padding: 8px 14px;
                border-radius: 6px;
                font-size: 11px;
                font-family: Arial, Helvetica, sans-serif;
                font-weight: 500;
                min-width: 70px;
            }}
            QPushButton:hover {{
                background-color: {theme['hover_overlay']};
                border-color: {theme['primary']};
            }}
            QPushButton:disabled {{
                color: {theme['text_disabled']};
                background-color: {theme['disabled_background']};
                border-color: {theme['disabled']};
            }}
        """)
        
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
        """Create the enhanced header with step indicator and contact status - matching compose screen"""
        layout = QHBoxLayout()
        
        # Step indicator
        step_label = QLabel("Step 3 of 4: Preview Emails")
        step_label.setStyleSheet(TITLE_STYLE)
        layout.addWidget(step_label)
        
        # Spacer
        layout.addStretch()
        
        # Contact status (enhanced styling to match compose screen)
        self.contact_status_label = QLabel("0 contacts ready")
        self.contact_status_label.setStyleSheet(SUBTITLE_STYLE)
        layout.addWidget(self.contact_status_label)
        
        return layout
        
    def create_contact_list_panel(self):
        """Create the left panel with contact list and search - matching compose screen styling"""
        panel = QGroupBox("Contacts")
        panel.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 13px;
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 16px;
                background-color: white;
                color: {DARK_GREY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: {DARK_GREY};
                background-color: white;
                font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(12)
        
        # Search section
        search_layout = self.create_search_section()
        layout.addLayout(search_layout)
        
        # Contact count (enhanced styling)
        self.contact_count_label = QLabel("0 contacts")
        self.contact_count_label.setStyleSheet(f"""
            QLabel {{
                font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
                font-size: 12px;
                font-weight: 500;
                color: #5F6368;
                margin-bottom: 4px;
            }}
        """)
        layout.addWidget(self.contact_count_label)
        
        # Contact list (enhanced styling matching compose screen aesthetics)
        self.contact_list = QListWidget()
        self.contact_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                background-color: white;
                selection-background-color: {PRIMARY_BLUE};
                selection-color: white;
                font-size: 12px;
                font-family: 'SF Pro Text', 'Segoe UI', 'Arial', sans-serif;
                min-height: 300px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px 16px;
                border-bottom: 1px solid #F0F2F5;
                color: {DARK_GREY};
                margin: 0px;
            }}
            QListWidget::item:last {{
                border-bottom: none;
            }}
            QListWidget::item:hover {{
                background-color: #F8F9FA;
            }}
            QListWidget::item:selected {{
                background-color: {PRIMARY_BLUE};
                color: white;
                border-bottom: 1px solid {PRIMARY_BLUE};
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
        """Create the search functionality - enhanced styling matching compose screen"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Search label (enhanced styling)
        search_label = QLabel("Search contacts:")
        search_label.setStyleSheet(f"""
            QLabel {{
                font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
                font-size: 13px;
                font-weight: 600;
                color: {DARK_GREY};
                margin-bottom: 2px;
            }}
        """)
        layout.addWidget(search_label)
        
        # Search input (enhanced styling)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or email...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 12px;
                font-family: 'SF Pro Text', 'Segoe UI', 'Arial', sans-serif;
                background-color: white;
                color: {DARK_GREY};
                selection-background-color: {PRIMARY_BLUE};
            }}
            QLineEdit:focus {{
                border-color: {PRIMARY_BLUE};
                background-color: #FAFBFC;
            }}
            QLineEdit::placeholder {{
                color: #9AA0A6;
            }}
        """)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self.search_input)
        
        return layout
        
    def create_contact_navigation(self):
        """Create navigation buttons within contact list"""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        # Previous contact (enhanced styling)
        self.prev_contact_btn = QPushButton("◀ Previous")
        self.prev_contact_btn.clicked.connect(self.select_previous_contact)
        self.prev_contact_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #F8F9FA;
                color: {DARK_GREY};
                border: 1px solid {BORDER_GREY};
                padding: 8px 14px;
                border-radius: 6px;
                font-size: 11px;
                font-family: 'SF Pro Text', 'Segoe UI', 'Arial', sans-serif;
                font-weight: 500;
                min-width: 70px;
            }}
            QPushButton:hover {{
                background-color: #EEEEEE;
                border-color: #CCCCCC;
            }}
            QPushButton:disabled {{
                color: #9AA0A6;
                background-color: #F5F6F7;
                border-color: #E8E9EA;
            }}
        """)
        layout.addWidget(self.prev_contact_btn)
        
        # Contact position indicator (enhanced styling)
        self.position_label = QLabel("1 of 0")
        self.position_label.setStyleSheet(f"""
            QLabel {{
                color: #5F6368;
                font-size: 11px;
                font-family: 'SF Pro Text', 'Segoe UI', 'Arial', sans-serif;
                font-weight: 500;
                padding: 8px 12px;
                text-align: center;
                background-color: #F8F9FA;
                border-radius: 6px;
                min-width: 50px;
            }}
        """)
        layout.addWidget(self.position_label)
        
        # Next contact (enhanced styling)
        self.next_contact_btn = QPushButton("Next ▶")
        self.next_contact_btn.clicked.connect(self.select_next_contact)
        self.next_contact_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #F8F9FA;
                color: {DARK_GREY};
                border: 1px solid {BORDER_GREY};
                padding: 8px 14px;
                border-radius: 6px;
                font-size: 11px;
                font-family: 'SF Pro Text', 'Segoe UI', 'Arial', sans-serif;
                font-weight: 500;
                min-width: 70px;
            }}
            QPushButton:hover {{
                background-color: #EEEEEE;
                border-color: #CCCCCC;
            }}
            QPushButton:disabled {{
                color: #9AA0A6;
                background-color: #F5F6F7;
                border-color: #E8E9EA;
            }}
        """)
        layout.addWidget(self.next_contact_btn)
        
        return layout
        
    def create_email_preview_panel(self):
        """Create the right panel with email preview - matching compose screen styling"""
        panel = QGroupBox("Email Preview")
        panel.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 13px;
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 16px;
                background-color: white;
                color: {DARK_GREY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: {DARK_GREY};
                background-color: white;
                font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 16)
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
        """Create the email headers display - enhanced styling to match compose screen"""
        section = QFrame()
        section.setFrameStyle(QFrame.NoFrame)
        section.setStyleSheet(f"""
            QFrame {{
                background-color: #F8F9FA;
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                padding: 16px;
                margin-bottom: 8px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # To field (enhanced styling)
        self.to_label = QLabel("To: (No contact selected)")
        self.to_label.setStyleSheet(f"""
            QLabel {{
                font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
                font-size: 12px;
                color: {DARK_GREY};
                font-weight: 600;
                padding: 2px 0px;
            }}
        """)
        layout.addWidget(self.to_label)
        
        # From field
        self.from_label = QLabel("From: (Not set)")
        self.from_label.setStyleSheet(f"""
            QLabel {{
                font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
                font-size: 12px;
                color: #5F6368;
                padding: 2px 0px;
            }}
        """)
        layout.addWidget(self.from_label)
        
        # Subject field
        self.subject_label = QLabel("Subject: (Not set)")
        self.subject_label.setStyleSheet(f"""
            QLabel {{
                font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
                font-size: 12px;
                color: #5F6368;
                padding: 2px 0px;
            }}
        """)
        layout.addWidget(self.subject_label)
        
        section.setLayout(layout)
        return section
        
    def create_email_content_section(self):
        """Create the email content preview - matching attachments widget container pattern"""
        section = QGroupBox("Email Content")
        section.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 13px;
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 16px;
                background-color: white;
                color: {DARK_GREY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: {DARK_GREY};
                background-color: white;
                font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(12)
        
        # Create scrollable container for content preview (like attachments widget)
        content_scroll_area = QScrollArea()
        content_scroll_area.setWidgetResizable(True)
        content_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_scroll_area.setFrameStyle(QFrame.NoFrame)
        content_scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: #F0F2F5;
                border: 1px solid #E1E3E1;
                border-radius: 8px;
                margin: 4px;
            }}
            QScrollBar:vertical {{
                background-color: #F8F9FA;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #DADCE0;
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #BBBDBF;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        content_widget.setStyleSheet("QWidget { background-color: transparent; }")
        
        content_widget_layout = QVBoxLayout()
        content_widget_layout.setContentsMargins(16, 16, 16, 16)
        content_widget_layout.setSpacing(0)
        
        # Content preview area (properly contained and scrollable)
        self.content_preview = QTextEdit()
        self.content_preview.setReadOnly(True)
        self.content_preview.setMinimumHeight(120)
        # Remove maximum height to allow flexible sizing
        self.content_preview.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
                font-family: 'SF Pro Text', 'Segoe UI', 'Arial', sans-serif;
                color: {DARK_GREY};
                padding: 12px;
                line-height: 1.4;
            }}
            QTextEdit:focus {{
                border-color: {PRIMARY_BLUE};
                background-color: white;
            }}
        """)
        self.content_preview.setPlaceholderText("Email content will appear here when a contact is selected...")
        
        content_widget_layout.addWidget(self.content_preview)
        content_widget.setLayout(content_widget_layout)
        content_scroll_area.setWidget(content_widget)
        layout.addWidget(content_scroll_area)
        
        section.setLayout(layout)
        return section
        
    def create_attachments_section(self):
        """Create the attachments display section - enhanced styling matching compose screen"""
        section = QGroupBox("Attachments")
        section.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 13px;
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 16px;
                background-color: #F8F9FA;
                color: {DARK_GREY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: {DARK_GREY};
                background-color: #F8F9FA;
                font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(12)
        
        # Attachment summary (enhanced styling)
        self.attachment_summary = QLabel("📎 No attachments")
        self.attachment_summary.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY_BLUE};
                font-size: 12px;
                font-weight: 600;
                font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
                padding: 10px 12px;
                background-color: #E3F2FD;
                border: 1px solid {PRIMARY_BLUE};
                border-radius: 6px;
                margin-bottom: 4px;
            }}
        """)
        layout.addWidget(self.attachment_summary)
        
        # Attachment list (enhanced styling)
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
        """Create the navigation buttons - matching compose screen styling"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Previous button (matching compose screen Back button styling)
        previous_btn = QPushButton("Previous")
        previous_btn.clicked.connect(self.on_previous_clicked)
        previous_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {LIGHT_GREY};
                color: #333333;
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
        
        # Send All button (primary - using BUTTON_STYLE like compose screen Preview button)
        self.send_all_btn = QPushButton("Send All Emails")
        self.send_all_btn.clicked.connect(self.on_send_all_clicked)
        self.send_all_btn.setStyleSheet(BUTTON_STYLE)
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
        total_size = 0
        for att in self.attachments:
            if isinstance(att, dict):
                total_size += att.get('file_size', 0)
            else:
                # Handle Attachment object
                total_size += getattr(att, 'file_size', 0)
                
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
            if isinstance(attachment, dict):
                filename = attachment.get('filename', 'Unknown file')
                file_size = attachment.get('file_size_formatted', 'Unknown size')
                att_type = attachment.get('attachment_type', 'other')
            else:
                # Handle Attachment object
                filename = getattr(attachment, 'filename', 'Unknown file')
                file_size = getattr(attachment, 'get_file_size_formatted', lambda: 'Unknown size')()
                att_type = getattr(attachment, 'attachment_type', 'other')
                if hasattr(att_type, 'value'):
                    att_type = att_type.value
            
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
    def set_campaign_data(self, campaign_data):
        """Set complete campaign data from previous screens"""
        print(f"🔍 Preview Screen - Received campaign data: {list(campaign_data.keys())}")
        
        # Extract and set email data
        email_data = {}
        if 'from_email' in campaign_data:
            email_data['from_email'] = campaign_data['from_email']
        if 'subject' in campaign_data:
            email_data['subject'] = campaign_data['subject']
        if 'content_plain' in campaign_data:
            email_data['content_plain'] = campaign_data['content_plain']
        if 'content_html' in campaign_data:
            email_data['content_html'] = campaign_data['content_html']
        if 'attachments' in campaign_data:
            email_data['attachments'] = campaign_data['attachments']
        
        self.set_email_data(email_data)
        
        # Load contacts from CSV file if available
        if 'file_path' in campaign_data or 'uploaded_file' in campaign_data:
            file_path = campaign_data.get('file_path') or campaign_data.get('uploaded_file')
            if file_path and os.path.exists(file_path):
                contacts = self.load_contacts_from_csv(file_path)
                self.set_contacts(contacts)
                print(f"✅ Loaded {len(contacts)} contacts from {file_path}")
            else:
                print(f"❌ Contact file not found: {file_path}")
        
        # Store complete campaign data
        self.campaign_data = campaign_data
        
        # Update preview if we have contacts
        if self.contacts:
            self.update_email_preview(self.contacts[0])
    
    def load_contacts_from_csv(self, file_path):
        """Load contacts from CSV file using CSV handler for proper validation"""
        contacts = []
        try:
            # Import CSV handler
            from core.csv_handler import CSVHandler
            
            # Process CSV file with proper validation
            csv_handler = CSVHandler()
            result = csv_handler.process_csv_file(file_path)
            
            if result and result.get('success', False):
                contacts = result.get('contacts', [])
                
                # Log processing results
                total_rows = result.get('total_rows', 0)
                valid_contacts = len(contacts)
                print(f"📊 CSV Processing Results:")
                print(f"   - Total rows processed: {total_rows}")
                print(f"   - Valid contacts created: {valid_contacts}")
                print(f"   - Invalid/skipped rows: {total_rows - valid_contacts}")
                
                if result.get('warnings'):
                    print(f"   - Warnings: {result['warnings']}")
                if result.get('errors'):
                    print(f"   - Errors: {result['errors']}")
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'Failed to process CSV file'
                print(f"❌ CSV processing failed: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error loading contacts: {e}")
            
        return contacts
    
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
        
        # Extract attachments - handle both list and dict formats
        attachments_data = email_data.get('attachments', [])
        if isinstance(attachments_data, dict):
            # Handle AttachmentManager.to_dict() format: {'attachments': [...], 'summary': '...'}
            self.attachments = attachments_data.get('attachments', [])
        elif isinstance(attachments_data, list):
            # Handle direct list of attachments
            self.attachments = attachments_data
        else:
            self.attachments = []
            
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
        """Get final email data for sending - flattened format for Progress screen"""
        # Convert Contact objects to dictionaries for Progress screen compatibility
        contacts_dict = []
        for contact in self.contacts:
            if hasattr(contact, 'to_dict'):
                # Contact object - convert to dict
                contacts_dict.append(contact.to_dict())
            else:
                # Already a dict - use as is
                contacts_dict.append(contact)
        
        # Flatten the data structure to match Progress screen expectations
        final_data = {
            # Direct campaign data that Progress screen expects
            'contacts': contacts_dict,  # Progress screen expects dicts, not Contact objects
            'attachments': self.attachments,
            'attachment_errors': self.attachment_errors,
            'total_emails': len(self.contacts),
            'has_validation_issues': bool(self.attachment_errors),
            
            # Email template data (flatten email_data)
            'from_email': self.email_data.get('from_email', ''),
            'subject': self.email_data.get('subject', ''),
            'content_html': self.email_data.get('content_html', ''),
            'content_plain': self.email_data.get('content_plain', ''),
            
            # Additional campaign metadata
            'campaign_ready': True,
            'preview_completed': True,
        }
        
        # Include complete campaign data if available from previous screens
        if hasattr(self, 'campaign_data') and self.campaign_data:
            # Merge with existing campaign data, but override with current values
            merged_data = self.campaign_data.copy()
            merged_data.update(final_data)
            return merged_data
        
        return final_data
        
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