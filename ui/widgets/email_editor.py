"""
Email Editor Widget for Mini Email CRM
Provides rich text editing with formatting toolbar and personalization helpers
Based on Screen 2 design - Gmail-like compose interface
Enhanced with attachment functionality
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QFileDialog, QFrame, QListWidget, QListWidgetItem, QScrollArea, QSizePolicy,
    QMessageBox, QSpacerItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QUrl, QTimer
from PyQt5.QtGui import QFont, QPixmap, QDropEvent, QDragEnterEvent, QTextCursor

# Import themed dialogs
from ui.error_dialogs import ThemedMessageBox, ErrorDialogManager

# Import theme-aware styling system
from core.theme_manager import ThemeManager
from ui.styles.dynamic_stylesheet import DynamicStylesheetGenerator
from utils.text_visibility import ThemedTextHelper
from models.attachment import Attachment, AttachmentManager, AttachmentType


class EmailEditor(QWidget):
    """
    Email editor widget with formatting toolbar and personalization panel
    Follows UI Design Guidelines and Screen 2 layout
    """
    
    # Signals
    text_changed = pyqtSignal(str)  # Emitted when text content changes
    character_count_changed = pyqtSignal(int, int)  # Current count, max count
    placeholder_inserted = pyqtSignal(str)  # Emitted when placeholder is inserted
    attachment_added = pyqtSignal(str)  # Emitted when attachment is added (filename)
    attachment_removed = pyqtSignal(str)  # Emitted when attachment is removed (filename)
    attachments_changed = pyqtSignal(int, str)  # Count and total size
    
    def __init__(self, parent=None, max_characters=5000):
        super().__init__(parent)
        self.max_characters = max_characters
        self.attachment_manager = AttachmentManager()
        
        # Initialize theme system
        self.theme_manager = ThemeManager()
        self.stylesheet_generator = DynamicStylesheetGenerator(self.theme_manager)
        self.text_helper = ThemedTextHelper(self.theme_manager)
        
        self.available_placeholders = [
            '{firstname}',
            '{lastname}',
            '{email}'
        ]
        self.setup_ui()
        self.connect_signals()
        self.setup_drag_drop()
    
    def get_theme_colors(self):
        """Get current theme colors for styling"""
        current_theme = self.theme_manager.get_theme()
        return {
            'background': current_theme['background'],
            'surface': current_theme['surface'],
            'primary': current_theme['primary'],
            'text_primary': current_theme['text_primary'],
            'text_secondary': current_theme['text_secondary'],
            'border': current_theme['border'],
            'success': current_theme['success'],
            'error': current_theme['error'],
            'warning': current_theme['warning'],
            'surface_elevated': current_theme.get('surface_elevated', current_theme['surface'])
        }
    
    def get_theme_aware_style(self, style_type):
        """Get theme-aware styles for different UI elements"""
        colors = self.get_theme_colors()
        
        if style_type == 'subtitle':
            return f"""
                color: {colors['text_primary']};
                font-weight: 600;
                font-size: 14px;
                margin: 4px 0px;
            """
        elif style_type == 'toolbar':
            return f"""
                QFrame {{
                    background-color: {colors['surface_elevated']};
                    border: 1px solid {colors['border']};
                    border-radius: 6px;
                    padding: 4px;
                }}
            """
        elif style_type == 'input':
            # Use the text helper's method instead of direct optimal color call
            text_style = self.text_helper.get_text_style('body', 'primary', 'surface')
            return f"""
                QTextEdit {{
                    background-color: {colors['surface']};
                    {text_style}
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 14px;
                    line-height: 1.4;
                }}
                QTextEdit:focus {{
                    border-color: {colors['primary']};
                }}
            """
        return ""
        
    def setup_ui(self):
        """Set up the user interface - just the email editor section"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        # Email body label
        body_label = QLabel("Email body")
        body_label.setStyleSheet(self.get_theme_aware_style('subtitle'))
        main_layout.addWidget(body_label)
        
        # Create formatting toolbar
        self.toolbar = self.create_formatting_toolbar()
        main_layout.addWidget(self.toolbar)
        
        # Create text editor
        self.text_editor = self.create_text_editor()
        main_layout.addWidget(self.text_editor)
        
        # Character count display
        self.char_count_label = self.create_character_counter()
        main_layout.addWidget(self.char_count_label)
        
        # Create attachment section
        self.attachment_section = self.create_attachment_section()
        main_layout.addWidget(self.attachment_section)
        
        self.setLayout(main_layout)
        
    def create_formatting_toolbar(self):
        """Create the formatting toolbar with B, I, U, and attachment buttons"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Box)
        toolbar.setLineWidth(1)
        toolbar.setStyleSheet(self.get_theme_aware_style('toolbar'))
        
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)
        
        # Bold button
        self.bold_btn = self.create_toolbar_button("B", "Bold", self.toggle_bold)
        self.bold_btn.setStyleSheet(self.get_toolbar_button_style() + "font-weight: bold;")
        self.bold_btn.setCheckable(True)
        layout.addWidget(self.bold_btn)
        
        # Italic button
        self.italic_btn = self.create_toolbar_button("I", "Italic", self.toggle_italic)
        self.italic_btn.setStyleSheet(self.get_toolbar_button_style() + "font-style: italic;")
        self.italic_btn.setCheckable(True)
        layout.addWidget(self.italic_btn)
        
        # Underline button
        self.underline_btn = self.create_toolbar_button("U", "Underline", self.toggle_underline)
        self.underline_btn.setStyleSheet(self.get_toolbar_button_style() + "text-decoration: underline;")
        self.underline_btn.setCheckable(True)
        layout.addWidget(self.underline_btn)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        colors = self.get_theme_colors()
        separator.setStyleSheet(f"color: {colors['border']}; margin: 2px;")
        layout.addWidget(separator)
        
        # Attachment button - use the same theme-aware styling as other toolbar buttons
        self.attachment_btn = self.create_toolbar_button("📎", "Attach files", self.open_file_dialog)
        self.attachment_btn.setStyleSheet(self.get_toolbar_button_style())
        layout.addWidget(self.attachment_btn)
        
        # Add spacer to push buttons to the left
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        toolbar.setLayout(layout)
        return toolbar
        
    def get_toolbar_button_style(self):
        """Get consistent toolbar button styling following UI Guidelines"""
        colors = self.get_theme_colors()
        button_bg = colors['surface']
        # Use the text helper's proper method
        text_style = self.text_helper.get_text_style('button', 'primary', 'surface')
        
        return f"""
            QPushButton {{
                min-width: 28px;
                min-height: 28px;
                border: 1px solid {colors['border']};
                border-radius: 3px;
                background-color: {button_bg};
                {text_style}
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {colors['primary']}33;
                border-color: {colors['primary']};
            }}
            QPushButton:pressed {{
                background-color: {colors['primary']};
                color: {colors['surface']};
            }}
            QPushButton:checked {{
                background-color: {colors['primary']};
                color: {colors['surface']};
                border-color: {colors['primary']};
            }}
        """
        
    def create_toolbar_button(self, text, tooltip, callback):
        """Create a toolbar button with consistent styling"""
        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        button.setFont(QFont("Arial", 11))
        return button
        
    def create_text_editor(self):
        """Create the main text editing area"""
        editor = QTextEdit()
        editor.setMinimumHeight(200)
        editor.setMaximumHeight(350)
        editor.setStyleSheet(self.get_theme_aware_style('input'))
        
        # Set placeholder text (as seen in Screen 2)
        editor.setPlaceholderText("Dear {firstname},\n\nI hope this email finds you well.")
        
        # Set default font
        font = QFont("Arial", 14)
        editor.setFont(font)
        
        return editor
        
    def create_character_counter(self):
        """Create the character count display (27/5000 format from Screen 2)"""
        counter = QLabel("0/5000")
        counter.setAlignment(Qt.AlignRight)
        colors = self.get_theme_colors()
        counter.setStyleSheet(f"""
            QLabel {{
                color: {colors['text_secondary']};
                font-size: 12px;
                padding: 4px;
                background-color: transparent;
            }}
        """)
        return counter
        
    def connect_signals(self):
        """Connect internal signals"""
        self.text_editor.textChanged.connect(self.on_text_changed)
        self.text_editor.cursorPositionChanged.connect(self.update_format_buttons)
        
        # Timer for debounced text change events
        self.text_change_timer = QTimer()
        self.text_change_timer.setSingleShot(True)
        self.text_change_timer.timeout.connect(self.emit_text_changed)
        
    def toggle_bold(self):
        """Toggle bold formatting"""
        cursor = self.text_editor.textCursor()
        format = cursor.charFormat()
        
        if format.fontWeight() == QFont.Bold:
            format.setFontWeight(QFont.Normal)
        else:
            format.setFontWeight(QFont.Bold)
            
        cursor.setCharFormat(format)
        self.text_editor.setTextCursor(cursor)
        self.text_editor.setFocus()
        self.update_format_buttons()
        
    def toggle_italic(self):
        """Toggle italic formatting"""
        cursor = self.text_editor.textCursor()
        format = cursor.charFormat()
        
        format.setFontItalic(not format.fontItalic())
        
        cursor.setCharFormat(format)
        self.text_editor.setTextCursor(cursor)
        self.text_editor.setFocus()
        self.update_format_buttons()
        
    def toggle_underline(self):
        """Toggle underline formatting"""
        cursor = self.text_editor.textCursor()
        format = cursor.charFormat()
        
        format.setFontUnderline(not format.fontUnderline())
        
        cursor.setCharFormat(format)
        self.text_editor.setTextCursor(cursor)
        self.text_editor.setFocus()
        self.update_format_buttons()

        
    def update_format_buttons(self):
        """Update toolbar buttons based on current cursor position"""
        cursor = self.text_editor.textCursor()
        format = cursor.charFormat()
        
        # Update button states without triggering signals
        self.bold_btn.setChecked(format.fontWeight() == QFont.Bold)
        self.italic_btn.setChecked(format.fontItalic())
        self.underline_btn.setChecked(format.fontUnderline())
        
    def on_text_changed(self):
        """Handle text change events and update character count"""
        text = self.text_editor.toPlainText()
        char_count = len(text)  # Character count excludes attachment data per requirements
        
        # Update counter display (format from Screen 2)
        self.char_count_label.setText(f"{char_count}/{self.max_characters}")
        
        # Change color based on character limit (following UI Guidelines)
        colors = self.get_theme_colors()
        if char_count > self.max_characters:
            self.char_count_label.setStyleSheet(f"color: {colors['error']}; font-weight: bold;")  # Error red
        elif char_count > self.max_characters * 0.9:  # 90% of limit
            self.char_count_label.setStyleSheet(f"color: {colors['warning']}; font-weight: bold;")  # Warning orange
        else:
            self.char_count_label.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: normal;")
            
        # Emit character count signal
        self.character_count_changed.emit(char_count, self.max_characters)
        
        # Debounce text change signal
        self.text_change_timer.start(300)  # 300ms delay
        
    def create_attachment_section(self):
        """Create the attachment section below the email body - Gmail style with scrolling"""
        section = QFrame()
        section.setFrameStyle(QFrame.NoFrame)
        section.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin-top: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Create a scrollable area for attachments to prevent UI overflow
        self.attachment_scroll = QScrollArea()
        self.attachment_scroll.setWidgetResizable(True)
        self.attachment_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.attachment_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.attachment_scroll.setMaximumHeight(120)  # Limit height to ~4 attachment items
        self.attachment_scroll.setMinimumHeight(0)    # Allow shrinking when no attachments
        self.attachment_scroll.setVisible(False)      # Hidden by default
        self.attachment_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
            QScrollBar:vertical {
                background-color: #F8F9FA;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #DADCE0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #BBBDBF;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Container widget for attachment items
        self.attachment_container = QWidget()
        self.attachment_layout = QVBoxLayout()
        self.attachment_layout.setContentsMargins(0, 0, 0, 0)
        self.attachment_layout.setSpacing(4)
        self.attachment_layout.addStretch()  # Push items to top
        
        self.attachment_container.setLayout(self.attachment_layout)
        self.attachment_scroll.setWidget(self.attachment_container)
        layout.addWidget(self.attachment_scroll)
        
        section.setLayout(layout)
        self.update_attachment_display()
        return section
        
    def setup_drag_drop(self):
        """Set up drag and drop functionality"""
        self.setAcceptDrops(True)
        self.attachment_section.setAcceptDrops(True)
        if hasattr(self, 'attachment_scroll'):
            self.attachment_scroll.setAcceptDrops(True)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # Simple visual feedback - highlight the scroll area or container
            if hasattr(self, 'attachment_scroll') and self.attachment_scroll.isVisible():
                self.attachment_scroll.setStyleSheet("""
                    QScrollArea {
                        background-color: #F0F8FF;
                        border: 1px dashed #2196F3;
                        border-radius: 4px;
                    }
                """ + self.attachment_scroll.styleSheet().split('QScrollArea {')[0] if 'QScrollArea {' in self.attachment_scroll.styleSheet() else "")
            else:
                self.attachment_container.setStyleSheet("""
                    QWidget {
                        background-color: #F0F8FF;
                        border: 1px dashed #2196F3;
                        border-radius: 4px;
                    }
                """)
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        # Reset to normal style
        if hasattr(self, 'attachment_scroll'):
            # Reset scroll area style to original
            self.attachment_scroll.setStyleSheet("""
                QScrollArea {
                    background-color: transparent;
                    border: none;
                    margin: 0px;
                    padding: 0px;
                }
                QScrollBar:vertical {
                    background-color: #F8F9FA;
                    width: 8px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background-color: #DADCE0;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #BBBDBF;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
        self.attachment_container.setStyleSheet("")
        
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        # Reset style
        self.dragLeaveEvent(event)
        
        urls = event.mimeData().urls()
        for url in urls:
            if url.isLocalFile():
                file_path = url.toLocalFile()
                errors = self.add_attachment_from_file(file_path)
                if errors:
                    self.show_attachment_errors(errors, file_path)
                    
        event.acceptProposedAction()
        
    def open_file_dialog(self):
        """Open file dialog to select attachments"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(
            "All Supported Files (*.pdf *.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp *.doc *.docx *.txt *.rtf *.odt *.xlsx *.xls *.ppt *.pptx);;"
            "PDF Files (*.pdf);;"
            "Image Files (*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp);;"
            "Document Files (*.doc *.docx *.txt *.rtf *.odt *.xlsx *.xls *.ppt *.pptx);;"
            "All Files (*)"
        )
        
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            for file_path in file_paths:
                errors = self.add_attachment_from_file(file_path)
                if errors:
                    self.show_attachment_errors(errors, file_path)
                    
    def add_attachment_from_file(self, file_path: str) -> list:
        """Add attachment from file path"""
        errors = self.attachment_manager.add_attachment_from_file(file_path)
        if not errors:
            # Successfully added
            filename = os.path.basename(file_path)
            self.update_attachment_display()
            self.attachment_added.emit(filename)
            self.emit_attachment_changes()
        return errors
        
    def remove_attachment(self, filename: str):
        """Remove attachment by filename"""
        if self.attachment_manager.remove_attachment(filename):
            self.update_attachment_display()
            self.attachment_removed.emit(filename)
            self.emit_attachment_changes()
            
    def emit_attachment_changes(self):
        """Emit attachment count and size changes"""
        count = self.attachment_manager.get_attachment_count()
        total_size = self.attachment_manager.get_total_size_formatted()
        self.attachments_changed.emit(count, total_size)
        
    def update_attachment_display(self):
        """Update the attachment display area - Gmail style with scrolling"""
        # Clear existing items (except the stretch)
        while self.attachment_layout.count() > 1:  # Keep the stretch at the end
            child = self.attachment_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Add attachment items
        attachments = self.attachment_manager.get_attachments()
        
        # Show/hide scroll area based on whether we have attachments
        if attachments:
            self.attachment_scroll.setVisible(True)
            # Calculate dynamic height based on attachment count (max 4 items visible)
            item_height = 32  # Approximate height of each attachment item
            max_visible_items = 4
            needed_height = min(len(attachments) * item_height, max_visible_items * item_height)
            self.attachment_scroll.setMaximumHeight(max(needed_height, 50))  # Minimum 50px
            
            for attachment in attachments:
                item_widget = self.create_attachment_item(attachment)
                # Insert before the stretch
                self.attachment_layout.insertWidget(self.attachment_layout.count() - 1, item_widget)
        else:
            self.attachment_scroll.setVisible(False)
            
    def create_attachment_item(self, attachment: Attachment):
        """Create a simple attachment item - Gmail style (no icon, compact)"""
        item_frame = QFrame()
        item_frame.setFrameStyle(QFrame.NoFrame)
        item_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #F8F9FA;
                border: 1px solid #E1E3E1;
                border-radius: 4px;
                padding: 4px;
                margin: 1px 0px;
            }}
            QFrame:hover {{
                background-color: #F1F3F4;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(6)
        
        # File name (clean, simple, no icon)
        filename = attachment.filename
        if len(filename) > 40:
            filename = filename[:37] + "..."
            
        filename_label = QLabel(filename)
        filename_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: #3C4043;
                font-weight: normal;
            }}
        """)
        filename_label.setToolTip(attachment.filename)
        layout.addWidget(filename_label)
        
        layout.addStretch()
        
        # Simple file size
        size_label = QLabel(attachment.get_file_size_formatted())
        size_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #5F6368;
                margin-right: 4px;
            }
        """)
        layout.addWidget(size_label)
        
        # Simple remove button (like Gmail's X)
        remove_btn = QPushButton("×")
        remove_btn.setToolTip(f"Remove {attachment.filename}")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #5F6368;
                border: none;
                border-radius: 8px;
                min-width: 16px;
                max-width: 16px;
                min-height: 16px;
                max-height: 16px;
                font-size: 14px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #F1F3F4;
                color: #EA4335;
            }
            QPushButton:pressed {
                background-color: #E8EAED;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_attachment(attachment.filename))
        layout.addWidget(remove_btn)
        
        item_frame.setLayout(layout)
        return item_frame
        
    def show_attachment_errors(self, errors: list, file_path: str):
        """Show attachment error dialog"""
        filename = os.path.basename(file_path)
        error_msg = f"Failed to attach '{filename}':\n\n" + "\n".join(errors)
        
        msg_box = ThemedMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Attachment Error")
        msg_box.setText(error_msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
    def emit_text_changed(self):
        """Emit the text changed signal"""
        text = self.text_editor.toHtml()
        self.text_changed.emit(text)
        
    def insert_placeholder(self, item):
        """Insert a placeholder at cursor position"""
        placeholder = item.text()
        cursor = self.text_editor.textCursor()
        cursor.insertText(placeholder)
        self.text_editor.setFocus()
        self.placeholder_inserted.emit(placeholder)
        
    def insert_selected_placeholder(self):
        """Insert the currently selected placeholder"""
        current_item = self.placeholder_list.currentItem()
        if current_item:
            self.insert_placeholder(current_item)
        
    # Public API methods
    def get_html_content(self):
        """Get the HTML content of the editor"""
        return self.text_editor.toHtml()
        
    def get_plain_text(self):
        """Get the plain text content of the editor"""
        return self.text_editor.toPlainText()
        
    def set_content(self, content, is_html=False):
        """Set the content of the editor"""
        if is_html:
            self.text_editor.setHtml(content)
        else:
            self.text_editor.setPlainText(content)
            
    def clear_content(self):
        """Clear the editor content"""
        self.text_editor.clear()
        
    def set_placeholder_text(self, text):
        """Set the placeholder text"""
        self.text_editor.setPlaceholderText(text)
                    
    def set_max_characters(self, max_chars):
        """Set the maximum character limit"""
        self.max_characters = max_chars
        self.on_text_changed()  # Update counter display
        
    def is_at_character_limit(self):
        """Check if the content is at or over the character limit"""
        return len(self.text_editor.toPlainText()) >= self.max_characters
        
    def set_enabled(self, enabled):
        """Enable or disable the widget"""
        super().setEnabled(enabled)
        self.text_editor.setEnabled(enabled)
        self.toolbar.setEnabled(enabled)
        
    # Attachment API methods
    def get_attachments(self):
        """Get all attachments"""
        return self.attachment_manager.get_attachments()
        
    def get_attachment_count(self):
        """Get number of attachments"""
        return self.attachment_manager.get_attachment_count()
        
    def get_total_attachment_size(self):
        """Get total size of attachments in bytes"""
        return self.attachment_manager.get_total_size()
        
    def get_attachment_summary(self):
        """Get attachment summary dictionary"""
        return self.attachment_manager.get_summary()
        
    def clear_attachments(self):
        """Clear all attachments"""
        self.attachment_manager.clear_attachments()
        self.update_attachment_display()
        self.emit_attachment_changes()
        
    def has_attachments(self):
        """Check if there are any attachments"""
        return self.attachment_manager.get_attachment_count() > 0
        
    def validate_attachments(self):
        """Validate all attachments and return errors"""
        return self.attachment_manager.validate_all()
        
    def get_attachment_data(self):
        """Get attachment data for email sending"""
        return self.attachment_manager.to_dict()
