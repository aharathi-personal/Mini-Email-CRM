"""
Progress Display Widget for Mini Email CRM
Provides animated progress bar with real-time status updates for email sending
Based on Screen 4 design - Sending Emails
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, 
    QScrollArea, QTextEdit, QPushButton, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPalette, QTextCursor
from datetime import datetime


class ProgressDisplayWidget(QWidget):
    """
    Progress display widget with animated progress bar and real-time status updates
    Shows email sending progress with success/failure counters and detailed log
    """
    
    # Signals
    pause_requested = pyqtSignal()       # Emitted when pause is requested
    cancel_requested = pyqtSignal()      # Emitted when cancel is requested
    exit_requested = pyqtSignal()        # Emitted when exit is requested
    progress_updated = pyqtSignal(int)   # Emitted when progress changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.total_emails = 0
        self.current_progress = 0
        self.success_count = 0
        self.failed_count = 0
        self.is_paused = False
        self.is_cancelled = False
        self.current_email = ""
        self.estimated_time = ""
        
        # Animation
        self.progress_animation = None
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Set up the progress display UI based on Screen 4 design"""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        
        # Header section
        header_layout = self.create_header_section()
        layout.addLayout(header_layout)
        
        # Progress section
        progress_section = self.create_progress_section()
        layout.addWidget(progress_section)
        
        # Status section
        status_section = self.create_status_section()
        layout.addWidget(status_section)
        
        # Counters section
        counters_section = self.create_counters_section()
        layout.addWidget(counters_section)
        
        # Log section
        log_section = self.create_log_section()
        layout.addWidget(log_section)
        
        # Control buttons
        buttons_section = self.create_buttons_section()
        layout.addWidget(buttons_section)
        
        self.setLayout(layout)
        
    def create_header_section(self):
        """Create the header section with title and timestamp"""
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Title
        self.title_label = QLabel("Step 4 of 4: Sending Emails")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(self.title_label)
        
        # Timestamp
        self.timestamp_label = QLabel()
        self.update_timestamp()
        self.timestamp_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(self.timestamp_label)
        
        return layout
        
    def create_progress_section(self):
        """Create the progress bar section"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Progress text
        self.progress_label = QLabel("Preparing to send emails...")
        self.progress_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                text-align: center;
            }
        """)
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                background-color: #F5F5F5;
                text-align: center;
                font-weight: bold;
                font-size: 12px;
                color: #333333;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 6px;
                margin: 1px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        section.setLayout(layout)
        return section
        
    def create_status_section(self):
        """Create the current status section"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Current email
        self.current_email_label = QLabel("Ready to start sending...")
        self.current_email_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333333;
                font-weight: 500;
            }
        """)
        self.current_email_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.current_email_label)
        
        # Estimated time
        self.time_remaining_label = QLabel("")
        self.time_remaining_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
            }
        """)
        self.time_remaining_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_remaining_label)
        
        section.setLayout(layout)
        return section
        
    def create_counters_section(self):
        """Create the success/failed counters section"""
        section = QFrame()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Success counter
        success_frame = QFrame()
        success_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        success_layout = QHBoxLayout()
        success_layout.setSpacing(10)
        
        # Success badge
        self.success_badge = QLabel("0")
        self.success_badge.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
                min-width: 30px;
                max-width: 50px;
                min-height: 30px;
                max-height: 30px;
                text-align: center;
            }
        """)
        self.success_badge.setAlignment(Qt.AlignCenter)
        success_layout.addWidget(self.success_badge)
        
        success_text = QLabel("Success")
        success_text.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 500;
                color: #333333;
            }
        """)
        success_layout.addWidget(success_text)
        
        success_frame.setLayout(success_layout)
        layout.addWidget(success_frame)
        
        # Failed counter
        failed_frame = QFrame()
        failed_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        failed_layout = QHBoxLayout()
        failed_layout.setSpacing(10)
        
        # Failed badge
        self.failed_badge = QLabel("0")
        self.failed_badge.setStyleSheet("""
            QLabel {
                background-color: #F44336;
                color: white;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
                min-width: 30px;
                max-width: 50px;
                min-height: 30px;
                max-height: 30px;
                text-align: center;
            }
        """)
        self.failed_badge.setAlignment(Qt.AlignCenter)
        failed_layout.addWidget(self.failed_badge)
        
        failed_text = QLabel("Failed")
        failed_text.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 500;
                color: #333333;
            }
        """)
        failed_layout.addWidget(failed_text)
        
        failed_frame.setLayout(failed_layout)
        layout.addWidget(failed_frame)
        
        section.setLayout(layout)
        return section
        
    def create_log_section(self):
        """Create the scrollable log section"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Log area
        self.log_area = QTextEdit()
        self.log_area.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: #FAFAFA;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                color: #333333;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(200)
        self.log_area.setMaximumHeight(300)
        
        layout.addWidget(self.log_area)
        section.setLayout(layout)
        return section
        
    def create_buttons_section(self):
        """Create the control buttons section"""
        section = QFrame()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        # Pause/Resume button
        self.pause_button = QPushButton("Pause Sending")
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        layout.addWidget(self.pause_button)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel Remaining")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        layout.addWidget(self.cancel_button)
        
        layout.addStretch()
        
        # Exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
        """)
        layout.addWidget(self.exit_button)
        
        section.setLayout(layout)
        return section
        
    def connect_signals(self):
        """Connect internal signals"""
        self.pause_button.clicked.connect(self.on_pause_clicked)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.exit_button.clicked.connect(self.on_exit_clicked)
        
    def on_pause_clicked(self):
        """Handle pause button click"""
        if self.is_paused:
            self.resume_sending()
        else:
            self.pause_sending()
        self.pause_requested.emit()
        
    def on_cancel_clicked(self):
        """Handle cancel button click"""
        self.cancel_sending()
        self.cancel_requested.emit()
        
    def on_exit_clicked(self):
        """Handle exit button click"""
        self.exit_requested.emit()
        
    def update_timestamp(self):
        """Update the timestamp display"""
        current_time = datetime.now()
        formatted_time = current_time.strftime("%B %d, %Y %I:%M %p")
        self.timestamp_label.setText(formatted_time)
        
    # Public API methods
    def start_progress(self, total_emails):
        """Start the progress tracking"""
        self.total_emails = total_emails
        self.current_progress = 0
        self.success_count = 0
        self.failed_count = 0
        self.is_paused = False
        self.is_cancelled = False
        
        self.progress_bar.setMaximum(total_emails)
        self.progress_bar.setValue(0)
        self.update_progress_display()
        self.log_info(f"Starting email campaign to {total_emails} recipients...")
        self.update_timestamp()
        
    def update_progress(self, current, current_email="", time_remaining=""):
        """Update the progress display"""
        if current > self.current_progress:
            self.current_progress = current
            self.current_email = current_email
            self.estimated_time = time_remaining
            
            # Animate progress bar
            self.animate_progress_to(current)
            
            # Update displays
            self.update_progress_display()
            self.progress_updated.emit(current)
            
    def animate_progress_to(self, target_value):
        """Animate progress bar to target value"""
        if self.progress_animation:
            self.progress_animation.stop()
            
        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(500)  # 500ms animation
        self.progress_animation.setStartValue(self.progress_bar.value())
        self.progress_animation.setEndValue(target_value)
        self.progress_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.progress_animation.start()
        
    def update_progress_display(self):
        """Update all progress-related displays"""
        # Progress text
        if self.total_emails > 0:
            percentage = int((self.current_progress / self.total_emails) * 100)
            self.progress_label.setText(f"Sending {self.current_progress} of {self.total_emails} emails... ({percentage}%)")
        
        # Current status
        if self.current_email and not self.is_paused and not self.is_cancelled:
            self.current_email_label.setText(f"Currently sending to: {self.current_email}")
        elif self.is_paused:
            self.current_email_label.setText("Sending paused")
        elif self.is_cancelled:
            self.current_email_label.setText("Sending cancelled")
        elif self.current_progress >= self.total_emails:
            self.current_email_label.setText("All emails sent!")
            
        # Time remaining
        if self.estimated_time and not self.is_paused and not self.is_cancelled:
            self.time_remaining_label.setText(f"Estimated time remaining: {self.estimated_time}")
        else:
            self.time_remaining_label.setText("")
            
        # Update counters
        self.update_counters()
        
    def update_counters(self):
        """Update success/failed counters"""
        self.success_badge.setText(str(self.success_count))
        self.failed_badge.setText(str(self.failed_count))
        
    def log_success(self, email):
        """Log a successful email send"""
        self.success_count += 1
        self.log_entry(f"✅ Sent to {email}", "#4CAF50")
        self.update_counters()
        
    def log_failure(self, email, reason):
        """Log a failed email send"""
        self.failed_count += 1
        self.log_entry(f"❌ Failed to send to {email} - {reason}", "#F44336")
        self.update_counters()
        
    def log_info(self, message):
        """Log an info message"""
        self.log_entry(f"ℹ️ {message}", "#2196F3")
        
    def log_warning(self, message):
        """Log a warning message"""
        self.log_entry(f"⚠️ {message}", "#FF9800")
        
    def log_entry(self, message, color="#333333"):
        """Add an entry to the log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        html_message = f'<span style="color: {color};">[{timestamp}] {message}</span>'
        
        # Add to log
        self.log_area.append(html_message)
        
        # Auto-scroll to bottom
        cursor = self.log_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_area.setTextCursor(cursor)
        
    def pause_sending(self):
        """Pause the sending process"""
        self.is_paused = True
        self.pause_button.setText("Resume Sending")
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        self.update_progress_display()
        self.log_warning("Sending paused by user")
        
    def resume_sending(self):
        """Resume the sending process"""
        self.is_paused = False
        self.pause_button.setText("Pause Sending")
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.update_progress_display()
        self.log_info("Sending resumed")
        
    def cancel_sending(self):
        """Cancel the remaining sends"""
        self.is_cancelled = True
        self.pause_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.update_progress_display()
        self.log_warning("Remaining emails cancelled by user")
        
    def complete_sending(self):
        """Mark sending as complete"""
        self.current_progress = self.total_emails
        self.progress_bar.setValue(self.total_emails)
        self.pause_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.update_progress_display()
        
        # Summary log
        total_sent = self.success_count + self.failed_count
        self.log_info(f"Email campaign completed! Total: {total_sent}, Success: {self.success_count}, Failed: {self.failed_count}")
        
    def reset_progress(self):
        """Reset all progress tracking"""
        self.total_emails = 0
        self.current_progress = 0
        self.success_count = 0
        self.failed_count = 0
        self.is_paused = False
        self.is_cancelled = False
        self.current_email = ""
        self.estimated_time = ""
        
        self.progress_bar.setValue(0)
        self.progress_label.setText("Ready to send emails...")
        self.current_email_label.setText("No emails in queue")
        self.time_remaining_label.setText("")
        self.log_area.clear()
        
        # Reset buttons
        self.pause_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.pause_button.setText("Pause Sending")
        self.update_counters()
        
    # Getter methods for integration
    def get_progress(self):
        """Get current progress"""
        return self.current_progress
        
    def get_total_emails(self):
        """Get total emails count"""
        return self.total_emails
        
    def get_success_count(self):
        """Get success count"""
        return self.success_count
        
    def get_failed_count(self):
        """Get failed count"""
        return self.failed_count
        
    def is_sending_paused(self):
        """Check if sending is paused"""
        return self.is_paused
        
    def is_sending_cancelled(self):
        """Check if sending is cancelled"""
        return self.is_cancelled
        
    def is_sending_complete(self):
        """Check if sending is complete"""
        return self.current_progress >= self.total_emails and self.total_emails > 0
        
    def get_log_text(self):
        """Get the full log text"""
        return self.log_area.toPlainText()
        
    def clear_log(self):
        """Clear the log area"""
        self.log_area.clear()
