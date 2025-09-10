"""
Email Editor Widget for Mini Email CRM
Provides rich text editing with formatting toolbar and personalization helpers
Based on Screen 2 design - Gmail-like compose interface
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QLabel, QFrame, QGroupBox, QListWidget, QListWidgetItem,
    QSizePolicy, QSpacerItem, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCharFormat, QTextCursor, QPalette

from ui.styles.stylesheet import (
    BUTTON_STYLE, INPUT_STYLE, CARD_STYLE, SUBTITLE_STYLE,
    PRIMARY_BLUE, SUCCESS_GREEN, ERROR_RED, BORDER_GREY, LIGHT_GREY,
    FONT_SIZE_SMALL, DARK_GREY, WARNING_ORANGE
)


class EmailEditor(QWidget):
    """
    Email editor widget with formatting toolbar and personalization panel
    Follows UI Design Guidelines and Screen 2 layout
    """
    
    # Signals
    text_changed = pyqtSignal(str)  # Emitted when text content changes
    character_count_changed = pyqtSignal(int, int)  # Current count, max count
    placeholder_inserted = pyqtSignal(str)  # Emitted when placeholder is inserted
    
    def __init__(self, parent=None, max_characters=5000):
        super().__init__(parent)
        self.max_characters = max_characters
        self.available_placeholders = [
            '{firstname}',
            '{lastname}',
            '{email}'
        ]
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Set up the user interface - just the email editor section"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        # Email body label
        body_label = QLabel("Email body")
        body_label.setStyleSheet(SUBTITLE_STYLE)
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
        
        self.setLayout(main_layout)
        
    def create_formatting_toolbar(self):
        """Create the formatting toolbar with B, I, U, and alignment buttons"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Box)
        toolbar.setLineWidth(1)
        toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {LIGHT_GREY};
                border: 1px solid {BORDER_GREY};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        
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
        separator.setStyleSheet(f"color: {BORDER_GREY}; margin: 2px;")
        layout.addWidget(separator)
        
        # Add spacer to push buttons to the left
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        toolbar.setLayout(layout)
        return toolbar
        
    def get_toolbar_button_style(self):
        """Get consistent toolbar button styling following UI Guidelines"""
        return f"""
            QPushButton {{
                min-width: 28px;
                min-height: 28px;
                border: 1px solid {BORDER_GREY};
                border-radius: 3px;
                background-color: white;
                color: {DARK_GREY};
                font-size: {FONT_SIZE_SMALL};
            }}
            QPushButton:hover {{
                background-color: #E3F2FD;
                border-color: {PRIMARY_BLUE};
            }}
            QPushButton:pressed {{
                background-color: {PRIMARY_BLUE};
                color: white;
            }}
            QPushButton:checked {{
                background-color: {PRIMARY_BLUE};
                color: white;
                border-color: #1976D2;
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
        editor.setStyleSheet(INPUT_STYLE)
        
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
        counter.setStyleSheet(f"""
            QLabel {{
                color: {DARK_GREY};
                font-size: {FONT_SIZE_SMALL};
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
        char_count = len(text)
        
        # Update counter display (format from Screen 2)
        self.char_count_label.setText(f"{char_count}/{self.max_characters}")
        
        # Change color based on character limit (following UI Guidelines)
        if char_count > self.max_characters:
            self.char_count_label.setStyleSheet(f"color: {ERROR_RED}; font-weight: bold;")  # Error red
        elif char_count > self.max_characters * 0.9:  # 90% of limit
            self.char_count_label.setStyleSheet(f"color: {WARNING_ORANGE}; font-weight: bold;")  # Warning orange
        else:
            self.char_count_label.setStyleSheet(f"color: {DARK_GREY}; font-weight: normal;")
            
        # Emit character count signal
        self.character_count_changed.emit(char_count, self.max_characters)
        
        # Debounce text change signal
        self.text_change_timer.start(300)  # 300ms delay
        
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
