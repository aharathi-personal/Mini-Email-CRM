"""
Enhanced Progress Widget for Phase 8 Task 24
Features: Better visual indicators, step-by-step progress, estimated time, cancel support
"""

import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QProgressBar, QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QPalette, QMovie, QPixmap, QPainter, QColor

from ui.styles.stylesheet import (
    BUTTON_STYLE, SUBTITLE_STYLE, CARD_STYLE, SUCCESS_GREEN, ERROR_RED,
    DARK_GREY, LIGHT_GREY, BORDER_GREY, FONT_SIZE_SMALL, PRIMARY_BLUE,
    WARNING_ORANGE
)


class AnimatedProgressBar(QProgressBar):
    """Custom progress bar with smooth animations and color transitions"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
        
    def setup_style(self):
        """Set up animated progress bar styling"""
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {BORDER_GREY};
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: white;
                height: 24px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {PRIMARY_BLUE}, stop:0.5 #42a5f5, stop:1 {PRIMARY_BLUE});
                border-radius: 6px;
                margin: 1px;
            }}
            QProgressBar::chunk:disabled {{
                background: {BORDER_GREY};
            }}
        """)


class ProgressStepWidget(QWidget):
    """Individual step indicator widget"""
    
    def __init__(self, step_number, title, description="", parent=None):
        super().__init__(parent)
        self.step_number = step_number
        self.title = title
        self.description = description
        self.state = "pending"  # pending, active, completed, error
        self.setup_ui()
        
    def setup_ui(self):
        """Set up step indicator UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(12)
        
        # Step circle
        self.step_circle = QLabel(str(self.step_number))
        self.step_circle.setFixedSize(32, 32)
        self.step_circle.setAlignment(Qt.AlignCenter)
        self.update_circle_style()
        layout.addWidget(self.step_circle)
        
        # Step content
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                font-weight: bold;
                color: {DARK_GREY};
            }}
        """)
        content_layout.addWidget(self.title_label)
        
        # Description
        if self.description:
            self.desc_label = QLabel(self.description)
            self.desc_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 10px;
                    color: #888;
                }}
            """)
            self.desc_label.setWordWrap(True)
            content_layout.addWidget(self.desc_label)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def update_circle_style(self):
        """Update circle styling based on state"""
        if self.state == "pending":
            bg_color = LIGHT_GREY
            text_color = "#888"
            border_color = BORDER_GREY
        elif self.state == "active":
            bg_color = PRIMARY_BLUE
            text_color = "white"
            border_color = PRIMARY_BLUE
        elif self.state == "completed":
            bg_color = SUCCESS_GREEN
            text_color = "white"
            border_color = SUCCESS_GREEN
            self.step_circle.setText("✓")
        elif self.state == "error":
            bg_color = ERROR_RED
            text_color = "white"
            border_color = ERROR_RED
            self.step_circle.setText("✗")
        
        self.step_circle.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 16px;
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        
    def set_state(self, state):
        """Update step state"""
        self.state = state
        self.update_circle_style()
        
        # Update title color
        if state == "completed":
            color = SUCCESS_GREEN
        elif state == "error":
            color = ERROR_RED
        elif state == "active":
            color = PRIMARY_BLUE
        else:
            color = DARK_GREY
            
        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                font-weight: bold;
                color: {color};
            }}
        """)


class EnhancedProgressWidget(QWidget):
    """
    Enhanced progress widget with:
    - Step-by-step progress indicators
    - Estimated time remaining
    - Cancellation support
    - Better error handling
    - Visual feedback
    """
    
    # Signals
    cancel_requested = pyqtSignal()
    step_completed = pyqtSignal(int, str)  # step_number, step_name
    progress_finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, steps=None, show_cancel=True, parent=None):
        super().__init__(parent)
        self.steps = steps or []
        self.show_cancel = show_cancel
        self.current_step = 0
        self.start_time = None
        self.step_start_time = None
        self.is_cancelled = False
        self.is_finished = False
        
        # Timer for updating elapsed time
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_display)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the enhanced progress UI"""
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Header
        header_layout = QVBoxLayout()
        
        self.main_title = QLabel("Processing...")
        self.main_title.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {DARK_GREY};
                margin-bottom: 4px;
            }}
        """)
        header_layout.addWidget(self.main_title)
        
        self.subtitle = QLabel("Please wait while we process your request")
        self.subtitle.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                color: #666;
                margin-bottom: 8px;
            }}
        """)
        header_layout.addWidget(self.subtitle)
        
        layout.addLayout(header_layout)
        
        # Main progress bar
        self.main_progress = AnimatedProgressBar()
        self.main_progress.setRange(0, 100)
        self.main_progress.setValue(0)
        layout.addWidget(self.main_progress)
        
        # Progress info
        info_layout = QHBoxLayout()
        
        self.progress_label = QLabel("0%")
        self.progress_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                color: {DARK_GREY};
                font-weight: bold;
            }}
        """)
        info_layout.addWidget(self.progress_label)
        
        info_layout.addStretch()
        
        self.time_label = QLabel("Starting...")
        self.time_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                color: #888;
            }}
        """)
        info_layout.addWidget(self.time_label)
        
        layout.addLayout(info_layout)
        
        # Step indicators (if steps provided)
        if self.steps:
            layout.addWidget(self.create_steps_widget())
        
        # Current step description
        self.step_description = QLabel("")
        self.step_description.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                color: {PRIMARY_BLUE};
                font-style: italic;
                margin: 8px 0;
            }}
        """)
        self.step_description.setWordWrap(True)
        layout.addWidget(self.step_description)
        
        # Cancel button (if enabled)
        if self.show_cancel:
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {WARNING_ORANGE};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: #e68a00;
                }}
                QPushButton:disabled {{
                    background-color: {BORDER_GREY};
                    color: #999;
                }}
            """)
            self.cancel_button.clicked.connect(self.request_cancel)
            button_layout.addWidget(self.cancel_button)
            
            layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def create_steps_widget(self):
        """Create step-by-step progress indicators"""
        steps_frame = QFrame()
        steps_frame.setFrameStyle(QFrame.Box)
        steps_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                background-color: white;
                padding: 12px;
            }}
        """)
        
        steps_layout = QVBoxLayout()
        steps_layout.setSpacing(8)
        
        # Steps title
        steps_title = QLabel("Progress Steps")
        steps_title.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                font-weight: bold;
                color: {DARK_GREY};
                margin-bottom: 8px;
            }}
        """)
        steps_layout.addWidget(steps_title)
        
        # Individual step widgets
        self.step_widgets = []
        for i, step in enumerate(self.steps, 1):
            if isinstance(step, dict):
                step_widget = ProgressStepWidget(
                    i, step['title'], step.get('description', '')
                )
            else:
                step_widget = ProgressStepWidget(i, step)
            
            self.step_widgets.append(step_widget)
            steps_layout.addWidget(step_widget)
        
        steps_frame.setLayout(steps_layout)
        return steps_frame
        
    def start_progress(self, title="Processing...", subtitle="Please wait..."):
        """Start the progress operation"""
        self.main_title.setText(title)
        self.subtitle.setText(subtitle)
        self.start_time = time.time()
        self.step_start_time = time.time()
        self.is_cancelled = False
        self.is_finished = False
        self.current_step = 0
        
        # Reset all steps to pending
        for step_widget in getattr(self, 'step_widgets', []):
            step_widget.set_state("pending")
        
        # Start timer
        self.timer.start(1000)  # Update every second
        
        # Set first step as active if steps exist
        if self.step_widgets:
            self.step_widgets[0].set_state("active")
        
        self.update_progress(0, "Starting...")
        
    def update_progress(self, percentage, description=""):
        """Update progress percentage and description"""
        if self.is_cancelled or self.is_finished:
            return
            
        self.main_progress.setValue(min(100, max(0, percentage)))
        self.progress_label.setText(f"{percentage}%")
        
        if description:
            self.step_description.setText(description)
    
    def complete_step(self, step_number, description=""):
        """Mark a step as completed"""
        if self.is_cancelled or self.is_finished:
            return
            
        if hasattr(self, 'step_widgets') and step_number <= len(self.step_widgets):
            # Mark current step as completed
            self.step_widgets[step_number - 1].set_state("completed")
            
            # Mark next step as active if it exists
            if step_number < len(self.step_widgets):
                self.step_widgets[step_number].set_state("active")
        
        self.current_step = step_number
        self.step_start_time = time.time()
        
        if description:
            self.step_description.setText(description)
        
        self.step_completed.emit(step_number, description)
        
    def error_step(self, step_number, error_message):
        """Mark a step as error"""
        if hasattr(self, 'step_widgets') and step_number <= len(self.step_widgets):
            self.step_widgets[step_number - 1].set_state("error")
        
        self.show_error(error_message)
        
    def finish_progress(self, success=True, message=""):
        """Complete the progress operation"""
        self.is_finished = True
        self.timer.stop()
        
        if success:
            self.main_progress.setValue(100)
            self.progress_label.setText("100%")
            self.step_description.setText(message or "Completed successfully!")
            self.step_description.setStyleSheet(f"""
                QLabel {{
                    font-size: {FONT_SIZE_SMALL};
                    color: {SUCCESS_GREEN};
                    font-weight: bold;
                    margin: 8px 0;
                }}
            """)
            
            # Mark all remaining steps as completed
            for step_widget in getattr(self, 'step_widgets', []):
                if step_widget.state not in ["completed", "error"]:
                    step_widget.set_state("completed")
                    
        else:
            self.show_error(message or "Operation failed")
        
        # Disable cancel button
        if hasattr(self, 'cancel_button'):
            self.cancel_button.setEnabled(False)
            
        self.progress_finished.emit(success, message)
        
    def show_error(self, error_message):
        """Show error state"""
        self.main_title.setText("Error")
        self.main_title.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {ERROR_RED};
                margin-bottom: 4px;
            }}
        """)
        
        self.step_description.setText(error_message)
        self.step_description.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                color: {ERROR_RED};
                font-weight: bold;
                margin: 8px 0;
            }}
        """)
        
        # Update progress bar to error state
        self.main_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {ERROR_RED};
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: white;
                height: 24px;
            }}
            QProgressBar::chunk {{
                background-color: {ERROR_RED};
                border-radius: 6px;
                margin: 1px;
            }}
        """)
    
    def request_cancel(self):
        """Handle cancel request"""
        self.is_cancelled = True
        self.timer.stop()
        
        self.main_title.setText("Cancelling...")
        self.step_description.setText("Cancelling operation...")
        
        if hasattr(self, 'cancel_button'):
            self.cancel_button.setEnabled(False)
            self.cancel_button.setText("Cancelling...")
        
        self.cancel_requested.emit()
        
    def update_time_display(self):
        """Update elapsed time display"""
        if not self.start_time or self.is_finished:
            return
            
        elapsed = time.time() - self.start_time
        
        if elapsed < 60:
            time_text = f"Elapsed: {elapsed:.0f}s"
        else:
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            time_text = f"Elapsed: {minutes}m {seconds}s"
        
        # Add estimated time remaining if we have progress
        progress = self.main_progress.value()
        if progress > 10:  # Only estimate after 10% progress
            estimated_total = elapsed * 100 / progress
            remaining = estimated_total - elapsed
            
            if remaining > 0:
                if remaining < 60:
                    time_text += f" (≈{remaining:.0f}s remaining)"
                else:
                    rem_minutes = int(remaining // 60)
                    rem_seconds = int(remaining % 60)
                    time_text += f" (≈{rem_minutes}m {rem_seconds}s remaining)"
        
        self.time_label.setText(time_text)
        
    def set_steps(self, steps):
        """Update the steps list"""
        self.steps = steps
        # This would require recreating the steps widget
        # For simplicity, this is best set during initialization
        
    def get_current_step(self):
        """Get current step number"""
        return self.current_step
        
    def is_operation_cancelled(self):
        """Check if operation was cancelled"""
        return self.is_cancelled