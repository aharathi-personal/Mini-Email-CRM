"""
Enhanced Compose Screen for Mini Email CRM
Task 16: Enhanced Compose Screen (Screen 2)
Two-column layout with settings vs email body, attachment integration,
contact count display, attachment summary, and validation feedback
With enhanced text visibility and theme-aware styling
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
from ui.base.themed_widgets import ThemedWidget
from ui.styles.stylesheet import (
    BUTTON_STYLE, SUCCESS_BUTTON_STYLE, ERROR_BUTTON_STYLE,
    INPUT_STYLE, CARD_STYLE, TITLE_STYLE, SUBTITLE_STYLE
)


class ComposeScreen(ThemedWidget):
    """
    Enhanced Compose Email Screen - Step 2 of 4
    Task 16: Two-column layout with attachment integration and enhanced features
    With enhanced text visibility and theme-aware styling
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
        
        # Store references to themed components for updating
        self.themed_labels = []
        self.themed_buttons = []
        
        # Auto-populate from email with SMTP username for security
        self._auto_populate_from_email()
        
        # Initialize UI
        self.setup_ui()
        self.setup_validation()
    
    def _auto_populate_from_email(self):
        """Auto-populate the from email field with SMTP username for security"""
        try:
            from config.settings import SMTP_SETTINGS
            smtp_username = SMTP_SETTINGS.get('username', '').strip()
            if smtp_username:
                # We'll set this after UI is created in setup_ui
                self._smtp_username = smtp_username
            else:
                self._smtp_username = None
        except Exception as e:
            # If there's any error loading SMTP settings, don't auto-populate
            self._smtp_username = None
            print(f"Warning: Could not load SMTP username for auto-population: {e}")
    
    def apply_theme_customizations(self):
        """Apply theme-specific customizations for enhanced text visibility"""
        if not self.theme_manager:
            return
        
        # Update all themed labels with optimal visibility
        for label_info in self.themed_labels:
            label, label_type = label_info
            if hasattr(label, 'isVisible') and label.isVisible():
                self._apply_label_theme(label, label_type)
        
        # Update all themed buttons
        for button_info in self.themed_buttons:
            button, button_type = button_info
            if hasattr(button, 'isVisible') and button.isVisible():
                self._apply_button_theme(button, button_type)
        
        # Update specific components with enhanced styling
        self._update_step_indicator()
        self._update_status_labels()
        self._update_input_fields()
        self._update_validation_feedback()
        self._update_preview_area()
        self._update_attachment_indicators()
        
    def _update_step_indicator(self):
        """Update step indicator with enhanced visibility"""
        if hasattr(self, 'step_label') and self.text_helper:
            style = self.text_helper.get_label_style('title')
            self.step_label.setStyleSheet(f"QLabel {{ {style} }}")
    
    def _update_status_labels(self):
        """Update status labels with theme-aware colors"""
        if not self.theme_manager:
            return
        
        theme = self.theme_manager.get_current_theme()
        
        # Update attachment summary label
        if hasattr(self, 'attachment_summary_label'):
            text_color = self.get_optimal_text_color(theme['attachment_bg'])
            self.attachment_summary_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    font-size: 10px;
                    font-weight: bold;
                    padding: 4px 8px;
                    background-color: {theme['attachment_bg']};
                    border: 1px solid {theme['primary']};
                    border-radius: 4px;
                    margin-right: 8px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                }}
            """)
        
        # Update contact status label
        if hasattr(self, 'status_label'):
            style = self.text_helper.get_label_style('status')
            self.status_label.setStyleSheet(f"QLabel {{ {style} }}")
    
    def _update_input_fields(self):
        """Update input fields with enhanced visibility"""
        if not self.theme_manager:
            return
        
        theme = self.theme_manager.get_current_theme()
        text_color = self.get_optimal_text_color(theme['surface'])
        
        # Enhanced input field styling
        input_style = f"""
            QLineEdit {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {text_color};
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                selection-background-color: {theme['selection']};
            }}
            QLineEdit:focus {{
                border: 2px solid {theme['border_focus']};
                background-color: {theme['surface_container']};
                padding: 7px 11px;
            }}
            QLineEdit:disabled {{
                background-color: {theme['disabled_background']};
                color: {theme['text_disabled']};
                border-color: {theme['disabled']};
            }}
        """
        
        # Apply to input fields
        for attr_name in ['from_email_input', 'subject_input']:
            if hasattr(self, attr_name):
                getattr(self, attr_name).setStyleSheet(input_style)
                
    def _update_validation_feedback(self):
        """Update validation feedback styling with theme colors"""
        if hasattr(self, 'validation_message') and self.theme_manager:
            theme = self.theme_manager.get_current_theme()
            self.validation_message.setStyleSheet(f"""
                QLabel {{
                    color: {theme['error']};
                    font-size: 11px;
                    background-color: {theme['error']}22;
                    border: 1px solid {theme['error']};
                    border-radius: 4px;
                    padding: 8px;
                    margin: 4px 0px;
                }}
            """)
            
    def _update_preview_area(self):
        """Update preview area styling with theme colors"""
        if not self.theme_manager:
            return
        
        theme = self.theme_manager.get_current_theme()
        
        # Update preview container
        if hasattr(self, 'preview_container'):
            self.preview_container.setStyleSheet(f"""
                QGroupBox {{
                    font-weight: bold;
                    border: 1px solid {theme['border']};
                    border-radius: 4px;
                    margin-top: 8px;
                    padding-top: 12px;
                    background-color: {theme['surface']};
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: {theme['text_secondary']};
                    background-color: {theme['surface']};
                }}
            """)
        
        # Update preview text area
        if hasattr(self, 'preview_text'):
            self.preview_text.setStyleSheet(f"""
                QTextEdit {{
                    border: 1px solid {theme['border']};
                    border-radius: 4px;
                    background-color: {theme['surface']};
                    font-size: 11px;
                    color: {theme['text_primary']};
                }}
            """)
            
    def _update_attachment_indicators(self):
        """Update attachment indicators styling with theme colors"""
        if hasattr(self, 'attachment_indicators') and self.theme_manager:
            theme = self.theme_manager.get_current_theme()
            self.attachment_indicators.setStyleSheet(f"""
                QLabel {{
                    color: {theme['text_secondary']};
                    font-size: 10px;
                    padding: 4px 8px;
                    background-color: {theme.get('surface_elevated', theme['surface'])};
                    border-radius: 3px;
                }}
            """)
        
    def setup_validation(self):
        """Set up validation timer and connections"""
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_attachments_delayed)
        
    def setup_ui(self):
        """Set up the compose screen UI based on Screen 2 design"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # Main content area with better proportions
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left side - From settings and Personalization help (more space)
        left_panel = self.create_left_panel()
        left_panel.setMinimumWidth(320)  # Ensure minimum width for labels
        left_panel.setMaximumWidth(400)   # Limit maximum width
        content_layout.addWidget(left_panel, 1)
        
        # Right side - Email body (less relative space but still flexible)
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
        
        # Step indicator with enhanced visibility
        step_label = self.create_themed_label("Step 2 of 4: Compose Email", "title")
        self.step_label = step_label
        layout.addWidget(step_label)
        
        # Store for theme updates
        self.themed_labels.append((step_label, "title"))
        
        # Spacer
        layout.addStretch()
        
        # Attachment summary (when attachments exist) with enhanced visibility
        self.attachment_summary_label = self.create_themed_label("", "status")
        self.attachment_summary_label.setVisible(False)
        layout.addWidget(self.attachment_summary_label)
        
        # Store for theme updates
        self.themed_labels.append((self.attachment_summary_label, "status"))
        
        # Contact count status with enhanced visibility
        self.status_label = self.create_themed_label("Ready to send to 0 contacts", "status")
        layout.addWidget(self.status_label)
        
        # Store for theme updates
        self.themed_labels.append((self.status_label, "status"))
        
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
        """Create the compact From settings section with consistent card design"""
        group = QGroupBox("From settings")
        # Use dynamic theme colors
        theme_colors = self.theme_manager.get_theme()
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: {theme_colors['surface']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {theme_colors['text_primary']};
                background-color: {theme_colors['surface']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 20)
        layout.setSpacing(15)
        
        # From Email field with better sizing
        from_email_label = QLabel("From Email")
        from_email_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                color: {theme_colors['text_primary']};
                font-size: 12px;
                margin-bottom: 5px;
            }}
        """)
        from_email_label.setWordWrap(True)
        from_email_label.setMinimumHeight(25)
        layout.addWidget(from_email_label)
        
        self.from_email_input = QLineEdit()
        self.from_email_input.setPlaceholderText("your-email@example.com")
        self.from_email_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                background-color: {theme_colors['surface']};
                color: {theme_colors['text_primary']};
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border-color: {theme_colors['primary']};
                outline: none;
            }}
            QLineEdit::placeholder {{
                color: {theme_colors['text_placeholder']};
            }}
        """)
        
        # Auto-populate with SMTP username if available
        if hasattr(self, '_smtp_username') and self._smtp_username:
            self.from_email_input.setText(self._smtp_username)
            self.from_email_input.setToolTip(f"Auto-populated from SMTP credentials: {self._smtp_username}")
        
        layout.addWidget(self.from_email_input)
        
        # Spacer between fields
        layout.addSpacing(10)
        
        # Email subject field with better sizing
        subject_label = QLabel("Email subject")
        subject_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                color: {theme_colors['text_primary']};
                font-size: 12px;
                margin-bottom: 5px;
            }}
        """)
        subject_label.setWordWrap(True)
        subject_label.setMinimumHeight(25)
        layout.addWidget(subject_label)
        
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter your email subject...")
        self.subject_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                background-color: {theme_colors['surface']};
                color: {theme_colors['text_primary']};
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border-color: {theme_colors['primary']};
                outline: none;
            }}
            QLineEdit::placeholder {{
                color: {theme_colors['text_placeholder']};
            }}
        """)
        layout.addWidget(self.subject_input)
        
        # Add some bottom spacing
        layout.addSpacing(15)
        
        group.setLayout(layout)
        return group
        
    def create_personalization_help(self):
        """Create the expanded personalization help section with consistent card design"""
        group = QGroupBox("Personalization help")
        theme_colors = self.theme_manager.get_theme()
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: {theme_colors['surface']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {theme_colors['text_primary']};
                background-color: {theme_colors['surface']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 20)
        layout.setSpacing(12)
        
        # Available placeholders label with better styling
        placeholders_label = QLabel("Available placeholders:")
        placeholders_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                color: {theme_colors['text_primary']};
                font-size: 12px;
                margin-bottom: 5px;
            }}
        """)
        layout.addWidget(placeholders_label)
        
        # Create expanded placeholder list
        self.placeholder_list = QListWidget()
        self.placeholder_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                background-color: {theme_colors['surface']};
                selection-background-color: {theme_colors['primary']};
                selection-color: {theme_colors['text_on_primary']};
                font-family: monospace;
                font-size: 11px;
                min-height: 120px;
                max-height: 120px;
                color: {theme_colors['text_primary']};
            }}
            QListWidget::item {{
                padding: 8px 10px;
                border-bottom: 1px solid {theme_colors['border']};
                color: {theme_colors['text_primary']};
            }}
            QListWidget::item:hover {{
                background-color: {theme_colors['hover_overlay']};
            }}
            QListWidget::item:selected {{
                background-color: {theme_colors['primary']};
                color: {theme_colors['text_on_primary']};
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
        self._apply_button_theme(insert_btn, "primary")
        layout.addWidget(insert_btn)
        
        # Add some bottom spacing
        layout.addSpacing(15)
        
        group.setLayout(layout)
        return group
        
    def create_email_body_section(self):
        """Create the enhanced email body section with EmailEditor and attachment feedback"""
        # Main container as a card
        group = QGroupBox("Email body")
        theme_colors = self.theme_manager.get_theme()
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {theme_colors['border']};
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: {theme_colors['surface']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {theme_colors['text_primary']};
                background-color: {theme_colors['surface']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 20)
        layout.setSpacing(12)
        
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
        
        group.setLayout(layout)
        return group
        
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
        # Theme styling will be applied in apply_theme_customizations()
        
        layout.addWidget(self.validation_message)
        feedback_area.setLayout(layout)
        
        return feedback_area
        
    def create_preview_area(self):
        """Create collapsible email preview area with attachment indicators"""
        self.preview_container = QGroupBox("Email Preview")
        # Theme styling will be applied in apply_theme_customizations()
        
        self.preview_container.setCheckable(True)
        self.preview_container.setChecked(False)  # Collapsed by default
        self.preview_container.setMaximumHeight(200)
        
        # Connect checkbox toggle to preview updates
        self.preview_container.toggled.connect(self.on_preview_toggled)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)
        
        # Preview text area (read-only)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(120)
        # Theme styling will be applied in apply_theme_customizations()
        self.preview_text.setPlaceholderText("Email preview will appear here...")
        layout.addWidget(self.preview_text)
        
        # Attachment indicators
        self.attachment_indicators = QLabel("📎 No attachments")
        # Theme styling will be applied in apply_theme_customizations()
        layout.addWidget(self.attachment_indicators)
        
        self.preview_container.setLayout(layout)
        return self.preview_container
        
    def create_navigation(self):
        """Create the navigation buttons"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Back button with enhanced theming
        back_btn = self.create_themed_button("Back", "secondary")
        back_btn.clicked.connect(self.on_back_clicked)
        
        # Store for theme updates
        self.themed_buttons.append((back_btn, "secondary"))
        layout.addWidget(back_btn)
        
        # Spacer
        layout.addStretch()
        
        # Preview Emails button (primary) with enhanced theming
        self.preview_btn = self.create_themed_button("Preview Emails", "primary")
        self.preview_btn.clicked.connect(self.on_preview_clicked)
        self.preview_btn.setEnabled(False)  # Disabled until content is ready
        
        # Store for theme updates
        self.themed_buttons.append((self.preview_btn, "primary"))
        layout.addWidget(self.preview_btn)
        
        # Exit button with enhanced theming
        exit_btn = self.create_themed_button("Exit", "error")
        exit_btn.clicked.connect(self.on_exit_clicked)
        
        # Store for theme updates
        self.themed_buttons.append((exit_btn, "error"))
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
        # Only update preview if checkbox is checked
        if hasattr(self, 'preview_container') and self.preview_container.isChecked():
            self.update_preview()
        email_data = self.get_email_data()
        self.email_content_changed.emit(email_data)
        
    def on_character_count_changed(self, current, max_count):
        """Handle character count changes"""
        # Only update preview if checkbox is checked
        if hasattr(self, 'preview_container') and self.preview_container.isChecked():
            self.update_preview()
        
    def on_placeholder_inserted(self, placeholder):
        """Handle placeholder insertion"""
        # Only update preview if checkbox is checked
        if hasattr(self, 'preview_container') and self.preview_container.isChecked():
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
        # Get current theme for dynamic styling
        theme = self.get_current_theme()
        
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
                    color: {theme['primary']};
                    font-size: 10px;
                    font-weight: bold;
                    padding: 4px 8px;
                    background-color: {theme['primary']}22;
                    border-radius: 3px;
                }}
            """)
        else:
            self.attachment_indicators.setText("📎 No attachments")
            self.attachment_indicators.setStyleSheet(f"""
                QLabel {{
                    color: {theme['text_secondary']};
                    font-size: 10px;
                    padding: 4px 8px;
                    background-color: {theme.get('surface_elevated', theme['surface'])};
                    border-radius: 3px;
                }}
            """)
            
    def update_preview(self):
        """Update email preview with current content - only if preview is enabled"""
        # Only update preview if the checkbox is checked
        if not hasattr(self, 'preview_container') or not self.preview_container.isChecked():
            return
            
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
        
    def on_preview_toggled(self, checked):
        """Handle preview checkbox toggle"""
        if checked:
            # When checkbox is checked, update the preview immediately
            self.update_preview()
        else:
            # When unchecked, clear the preview
            self.preview_text.clear()
        
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
        # Get current theme for styling
        theme = self.get_current_theme()
        
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
                    background-color: {theme['warning']};
                    color: white;
                    border: 2px solid {theme['warning']};
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 100px;
                    min-height: 36px;
                }}
                QPushButton:disabled {{
                    background-color: {theme['button_secondary']};
                    color: {theme['text_disabled']};
                    border-color: {theme['border']};
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
            
        # Critical security check: Ensure from email matches SMTP credentials
        from config.settings import SMTP_SETTINGS
        smtp_username = SMTP_SETTINGS.get('username', '').strip()
        
        if smtp_username and email_data['from_email'].strip() != smtp_username:
            QMessageBox.critical(
                self, 
                "Email Authorization Error", 
                f"The 'From Email' address ({email_data['from_email']}) does not match your SMTP credentials.\n\n"
                f"For security reasons, you can only send emails from the email address configured in your SMTP settings: {smtp_username}\n\n"
                f"Please update the 'From Email' field to match your authenticated email address."
            )
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
    
    def set_contact_data(self, upload_data):
        """Set contact data from upload screen"""
        if 'contact_count' in upload_data:
            self.set_contact_count(upload_data['contact_count'])
        
        # Store the upload data for later use
        self.upload_data = upload_data
        
        # Update UI to reflect data received
        if hasattr(self, 'status_label') and self.contact_count > 0:
            self.status_label.setText(f"Ready to send to {self.contact_count} contacts")
        
        # Trigger validation to enable Preview button if conditions are met
        self.validate_form()
        
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
        # Only update preview if checkbox is checked
        if hasattr(self, 'preview_container') and self.preview_container.isChecked():
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


# For development: run screen without test data
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    print("📧 ComposeScreen - Enhanced Compose Screen for Mini Email CRM")
    print("🚀 Starting clean compose screen (no test data)")
    print("💡 For full testing with sample data, run: python demos/demo_enhanced_compose_screen.py")
    print("📝 For automated tests, run: python tests/test_compose_screen.py")
    print()
    
    app = QApplication(sys.argv)
    
    # Create clean screen
    screen = ComposeScreen()
    screen.setWindowTitle("Step 2 - Compose")
    screen.resize(1200, 800)
    
    # Connect basic signals
    screen.exit_clicked.connect(app.quit)
    
    # Show instructions
    print("📖 Instructions:")
    print("• This is the clean compose screen without test data")
    print("• Use the demo file to see it with sample data")
    print("• You can type in the fields to test the UI")
    print("• The screen shows the complete layout and styling")
    
    screen.show()
    sys.exit(app.exec_())
