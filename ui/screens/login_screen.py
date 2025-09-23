"""
Login Screen for Mini Email CRM
Screen 0 of the application - handles SMTP credential input and validation
"""

import os
import sys
import re
from typing import Dict, Any
import socket

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QProgressBar, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QIcon

from ui.base.themed_widgets import ThemedWidget
from core.email_service import EmailService


class SMTPCredentialValidator(QThread):
    """
    Background thread for SMTP credential validation
    """
    validation_complete = pyqtSignal(bool, str)  # success, error_message

    def __init__(self, smtp_username: str, smtp_password: str):
        super().__init__()
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password

    def run(self):
        """Validate SMTP credentials in background thread"""
        try:
            # Create email service with provided credentials
            smtp_settings = {
                'server': 'smtp.gmail.com',  # Default to Gmail, could be made configurable later
                'port': 587,
                'username': self.smtp_username,
                'password': self.smtp_password,
                'use_tls': True
            }

            email_service = EmailService(smtp_settings=smtp_settings)

            # Test connection
            success, error_message = email_service.test_connection()

            if success:
                self.validation_complete.emit(True, "")
            else:
                self.validation_complete.emit(False, error_message or "SMTP connection failed. Please check your credentials.")

        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            self.validation_complete.emit(False, error_msg)


class LoginScreen(ThemedWidget):
    """
    Login screen for SMTP credential input and validation
    First screen of the application - validates SMTP credentials before proceeding
    """

    # Signals
    login_successful = pyqtSignal(dict)  # Emitted with validated credentials
    exit_requested = pyqtSignal()  # Emitted when user wants to exit

    def __init__(self, parent=None):
        super().__init__(parent)

        # UI state
        self.is_validating = False
        self.validation_thread = None

        # Credential storage (temporary, not persisted)
        self.validated_credentials = None

        self.setup_ui()

    def apply_theme_customizations(self):
        """Apply custom theme-specific changes"""
        theme = self.get_current_theme()

        # Update input field styling
        input_style = f"""
            QLineEdit {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 12px 16px;
                color: {theme['text_primary']};
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                selection-background-color: {theme['selection']};
            }}
            QLineEdit:focus {{
                border: 2px solid {theme['primary']};
                background-color: {theme['surface_container']};
                padding: 11px 15px;
            }}
            QLineEdit:disabled {{
                background-color: {theme['disabled_background']};
                color: {theme['text_disabled']};
                border-color: {theme['disabled']};
            }}
        """

        if hasattr(self, 'username_input'):
            self.username_input.setStyleSheet(input_style)

        if hasattr(self, 'password_input'):
            self.password_input.setStyleSheet(input_style)

        # Update status message styling
        if hasattr(self, 'status_message'):
            self.status_message.setStyleSheet(f"""
                QLabel {{
                    color: {theme['text_secondary']};
                    font-size: 12px;
                    padding: 8px 0px;
                    background-color: transparent;
                    border-radius: 4px;
                }}
            """)

        # Update progress bar styling
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {theme['border']};
                    border-radius: 4px;
                    text-align: center;
                    background-color: {theme['surface']};
                }}
                QProgressBar::chunk {{
                    background-color: {theme['primary']};
                    border-radius: 2px;
                }}
            """)

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Header section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)

        # Title
        title_label = self.create_themed_label("Welcome to Mini Email CRM", "title")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {self.get_current_theme()['text_primary']};
                margin-bottom: 8px;
            }}
        """)
        header_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = self.create_themed_label(
            "Please enter your SMTP credentials to get started",
            "subtitle"
        )
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {self.get_current_theme()['text_secondary']};
                margin-bottom: 20px;
            }}
        """)
        header_layout.addWidget(subtitle_label)

        layout.addLayout(header_layout)

        # Main content area
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.NoFrame)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)

        # Username field
        username_layout = QVBoxLayout()
        username_layout.setSpacing(8)

        username_label = self.create_themed_label("SMTP Email Address", "default")
        username_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                color: {self.get_current_theme()['text_primary']};
                font-size: 13px;
            }}
        """)
        username_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("your-email@gmail.com")
        self.username_input.setMinimumHeight(45)
        self.username_input.textChanged.connect(self.on_input_changed)
        username_layout.addWidget(self.username_input)

        content_layout.addLayout(username_layout)

        # Password field
        password_layout = QVBoxLayout()
        password_layout.setSpacing(8)

        password_label = self.create_themed_label("SMTP Password", "default")
        password_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                color: {self.get_current_theme()['text_primary']};
                font-size: 13px;
            }}
        """)
        password_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your SMTP password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.textChanged.connect(self.on_input_changed)
        password_layout.addWidget(self.password_input)

        content_layout.addLayout(password_layout)

        # Status message area
        self.status_message = QLabel("")
        self.status_message.setWordWrap(True)
        self.status_message.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.status_message)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(4)
        content_layout.addWidget(self.progress_bar)

        content_frame.setLayout(content_layout)
        layout.addWidget(content_frame)

        # Spacer
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(15)

        # Exit button
        exit_button = self.create_themed_button("Exit", "error")
        exit_button.clicked.connect(self.on_exit_clicked)
        nav_layout.addWidget(exit_button)

        # Spacer
        nav_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Login button
        self.login_button = self.create_themed_button("Connect & Continue", "primary")
        self.login_button.clicked.connect(self.on_login_clicked)
        self.login_button.setEnabled(False)  # Disabled until inputs are valid
        self.login_button.setMinimumWidth(160)
        nav_layout.addWidget(self.login_button)

        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def on_input_changed(self):
        """Handle input field changes"""
        self.clear_status_message()
        self.update_login_button_state()

    def update_login_button_state(self):
        """Update login button enabled state based on input validation"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # Basic validation
        has_username = bool(username)
        has_password = bool(password)

        # Email format validation
        is_valid_email = self.is_valid_email_format(username)

        # Enable button only if all conditions met
        is_enabled = has_username and has_password and is_valid_email and not self.is_validating
        self.login_button.setEnabled(is_enabled)

        # Update button text based on state
        if self.is_validating:
            self.login_button.setText("Connecting...")
        else:
            self.login_button.setText("Connect & Continue")

    def is_valid_email_format(self, email: str) -> bool:
        """Check if email has valid format"""
        if not email:
            return False

        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def on_login_clicked(self):
        """Handle login button click"""
        if self.is_validating:
            return  # Prevent multiple validation attempts

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # Validate inputs
        if not username or not password:
            self.show_status_message("Please enter both email and password.", "error")
            return

        if not self.is_valid_email_format(username):
            self.show_status_message("Please enter a valid email address.", "error")
            return

        # Check for spaces in password (common Gmail issue)
        if ' ' in password:
            self.show_status_message(
                "Warning: SMTP password should not contain spaces.\n"
                "For Gmail, use an App Password instead of your regular password.",
                "warning"
            )
            return

        # Check internet connectivity first
        if not self.check_internet_connectivity():
            self.show_status_message(
                "No internet connection detected.\n"
                "Please check your network connection and try again.",
                "error"
            )
            return

        # Start validation
        self.start_validation(username, password)

    def start_validation(self, username: str, password: str):
        """Start SMTP credential validation"""
        self.is_validating = True
        self.update_login_button_state()

        # Show progress
        self.show_status_message("Testing SMTP connection...", "info")
        self.progress_bar.setVisible(True)

        # Disable inputs during validation
        self.username_input.setEnabled(False)
        self.password_input.setEnabled(False)

        # Start validation thread
        self.validation_thread = SMTPCredentialValidator(username, password)
        self.validation_thread.validation_complete.connect(self.on_validation_complete)
        self.validation_thread.start()

    def on_validation_complete(self, success: bool, error_message: str):
        """Handle validation completion"""
        self.is_validating = False
        self.progress_bar.setVisible(False)

        # Re-enable inputs
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)

        if success:
            # Store validated credentials
            username = self.username_input.text().strip()
            password = self.password_input.text().strip()
            self.validated_credentials = {
                'username': username,
                'password': password
            }

            self.show_status_message("✅ Connection successful! Proceeding...", "success")

            # Small delay before emitting signal
            QTimer.singleShot(1000, self.emit_login_success)
        else:
            self.show_status_message(f"❌ {error_message}", "error")
            self.update_login_button_state()

    def emit_login_success(self):
        """Emit login successful signal with credentials"""
        if self.validated_credentials:
            self.login_successful.emit(self.validated_credentials)

    def show_status_message(self, message: str, message_type: str = "info"):
        """Show status message with appropriate styling"""
        theme = self.get_current_theme()

        color_map = {
            "info": theme['text_secondary'],
            "success": theme['success'],
            "warning": theme['warning'],
            "error": theme['error']
        }

        color = color_map.get(message_type, theme['text_secondary'])

        self.status_message.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                padding: 8px 12px;
                background-color: {color}15;
                border-radius: 4px;
                border: 1px solid {color}30;
            }}
        """)

        self.status_message.setText(message)

    def clear_status_message(self):
        """Clear the status message"""
        self.status_message.setText("")
        self.status_message.setStyleSheet("")

    def on_exit_clicked(self):
        """Handle exit button click"""
        if self.is_validating:
            # Stop validation if in progress
            if self.validation_thread and self.validation_thread.isRunning():
                self.validation_thread.terminate()
            self.is_validating = False

        reply = QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.exit_requested.emit()

    def check_internet_connectivity(self) -> bool:
        """Check if internet connection is available"""
        try:
            # Try to connect to a reliable host (Google DNS)
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def reset_form(self):
        """Reset the form to initial state"""
        self.username_input.clear()
        self.password_input.clear()
        self.clear_status_message()
        self.progress_bar.setVisible(False)
        self.validated_credentials = None
        self.is_validating = False
        self.update_login_button_state()


# Example usage and testing
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    screen = LoginScreen()
    screen.setWindowTitle("Mini Email CRM - Login")
    screen.resize(500, 600)

    # Connect signals for testing
    screen.login_successful.connect(lambda creds: print(f"Login successful: {creds}"))
    screen.exit_requested.connect(app.quit)

    screen.show()
    sys.exit(app.exec_())