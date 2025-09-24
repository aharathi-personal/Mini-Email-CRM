"""
Enhanced Progress Screen for Mini Email CRM
Task 18: Enhanced Progress Screen (Screen 4)
Campaign timestamp, step indicator, progress bar, success/failure counters,
real-time sending log with attachment info, and pause/cancel/exit controls
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGroupBox, QTextEdit, QProgressBar, QSplitter,
    QScrollArea, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QTextCursor

from ui.styles.stylesheet import (
    BUTTON_STYLE, SUCCESS_BUTTON_STYLE, ERROR_BUTTON_STYLE,
    CARD_STYLE, TITLE_STYLE, SUBTITLE_STYLE, BODY_STYLE,
    SUCCESS_BADGE_STYLE, ERROR_BADGE_STYLE, FONT_SIZE_SMALL,
    SURFACE, SURFACE_ELEVATED, SURFACE_CONTAINER, TEXT_SECONDARY, PRIMARY_HOVER, SUCCESS_HOVER
)

# Import ThemedWidget for theme support
from ui.base.themed_widgets import ThemedWidget

# Import EmailService for actual email sending
from core.email_service import EmailService

# Import theme manager for dynamic styling  
from core.theme_manager import ThemeManager


class ProgressScreen(ThemedWidget):
    """
    Enhanced Progress Screen - Step 4 of 4
    Task 18: Email sending progress with real-time updates and attachment info
    """
    
    # Navigation signals
    exit_clicked = pyqtSignal()
    campaign_completed = pyqtSignal(dict)  # Passes completion statistics
    
    # Progress control signals
    pause_requested = pyqtSignal()
    cancel_requested = pyqtSignal()
    
    # Progress update signals
    progress_updated = pyqtSignal(int)      # Current progress count
    email_sent = pyqtSignal(str, bool)      # Email address, success status
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize theme manager using singleton instance
        self.theme_manager = ThemeManager.instance()
        if self.theme_manager is None:
            # Fallback: create a new instance if singleton failed
            self.theme_manager = ThemeManager()
        
        # Campaign data
        self.campaign_data = {}
        self.contacts = []
        self.attachments = []
        self.campaign_start_time = None
        
        # Email service for actual sending
        self.email_service = EmailService()
        
        # Progress tracking
        self.total_emails = 0
        self.current_progress = 0
        self.success_count = 0
        theme = self.get_current_theme()

        # Build the UI now so widgets (like progress_bar) exist before any
        # simulation or campaign start. This prevents AttributeError when
        # start_simulation/start_campaign is invoked immediately after
        # constructing the screen (as happens in some demos/tests).
        self.setup_ui()

        # Initialize runtime state and timers
        # Timer callback will be connected dynamically in start_campaign depending on
        # whether this is a real campaign or a demo simulation.
        self.simulation_timer = QTimer(self)
        # Timer callback is not connected here; start_campaign decides which handler to use.
        self.simulation_active = False
        self.progress_animation = None
        self.failed_emails = []
        self.current_email = ""
        self.estimated_time = ""
        self.is_paused = False
        self.is_cancelled = False
        self.is_completed = False

        # Update navigation buttons (if present) with proper styles now that
        # widgets are available
        if hasattr(self, 'prev_contact_btn'):
            self._update_navigation_button_style(self.prev_contact_btn)
        if hasattr(self, 'next_contact_btn'):
            self._update_navigation_button_style(self.next_contact_btn)

        # Update all themed buttons
        if hasattr(self, 'themed_buttons'):
            for button_info in self.themed_buttons:
                button, button_type = button_info
                if hasattr(button, 'isVisible') and button.isVisible():
                    self._apply_button_theme(button, button_type)

        # Apply theme-aware styles to the newly created widgets
        self._apply_theme_to_hardcoded_elements()
    
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
        
    def _apply_theme_to_hardcoded_elements(self):
        """Apply theme-aware colors to all hardcoded elements in the UI"""
        theme = self.get_current_theme()
        
        # Update progress label
        if hasattr(self, 'progress_label'):
            self.progress_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    font-weight: bold;
                    color: {theme['text_primary']};
                    text-align: center;
                    background-color: transparent;
                    border: none;
                }}
            """)
        
        # Update percentage label
        if hasattr(self, 'percentage_label'):
            self.percentage_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 12px;
                    color: {theme['text_primary']};
                    text-align: center;
                    font-weight: bold;
                }}
            """)
        
        # Update status section
        if hasattr(self, 'status_section'):
            self.status_section.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme['surface_container']};
                    border: 1px solid {theme['border']};
                    border-radius: 6px;
                    padding: 12px;
                }}
            """)
        
        # Update current email label
        if hasattr(self, 'current_email_label'):
            self.current_email_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 13px;
                    color: {theme['text_primary']};
                    font-weight: 500;
                    text-align: center;
                    background-color: transparent;
                    border: none;
                }}
            """)
        
        # Update time remaining label
        if hasattr(self, 'time_remaining_label'):
            self.time_remaining_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 11px;
                    color: {theme['text_secondary']};
                    text-align: center;
                }}
            """)
        
        # Update counters section frames
        if hasattr(self, 'success_frame'):
            self.success_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme['surface_container']};
                    border: 1px solid {theme['border']};
                    border-radius: 6px;
                    padding: 12px;
                }}
            """)
        
        if hasattr(self, 'failed_frame'):
            self.failed_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme['surface_container']};
                    border: 1px solid {theme['border']};
                    border-radius: 6px;
                    padding: 12px;
                }}
            """)
        
        # Update success badge text
        if hasattr(self, 'success_badge'):
            self.success_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {theme['success']};
                    color: white;
                    border-radius: 12px;
                    padding: 4px 8px;
                    font-size: 12px;
                    font-weight: bold;
                    min-width: 20px;
                    text-align: center;
                }}
            """)
        
        # Update failed badge text
        if hasattr(self, 'failed_badge'):
            self.failed_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {theme['error']};
                    color: white;
                    border-radius: 12px;
                    padding: 4px 8px;
                    font-size: 12px;
                    font-weight: bold;
                    min-width: 20px;
                    text-align: center;
                }}
            """)
        
        # Update success text
        if hasattr(self, 'success_text'):
            self.success_text.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    font-weight: 500;
                    color: {theme['text_primary']};
                }}
            """)
        
        # Update failed text
        if hasattr(self, 'failed_text'):
            self.failed_text.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    font-weight: 500;
                    color: {theme['text_primary']};
                }}
            """)
        
        # Update log section
        if hasattr(self, 'log_section'):
            self.log_section.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme['surface']};
                    border: 1px solid {theme['border']};
                    border-radius: 6px;
                    padding: 5px;
                }}
            """)
        
        # Update log area
        if hasattr(self, 'log_area'):
            self.log_area.setStyleSheet(f"""
                QTextEdit {{
                    border: none;
                    background-color: {theme['surface_elevated']};
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 10px;
                    color: {theme['text_primary']};
                    border-radius: 4px;
                    padding: 8px;
                }}
            """)
        
        # Update campaign status label (dynamic based on state)
        if hasattr(self, 'campaign_status_label'):
            # This will be updated dynamically in other methods, but set a default theme-aware style
            self.campaign_status_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme['primary']};
                    font-size: 14px;
                    font-weight: bold;
                    padding: 6px 12px;
                    background-color: {theme['surface_container']};
                    border-radius: 4px;
                    border: 1px solid {theme['primary']};
                }}
            """)
        
        # Update attachment info label
        if hasattr(self, 'attachment_info_label'):
            self.attachment_info_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme['text_primary']};
                    font-size: 12px;
                    font-weight: 500;
                    padding: 4px 8px;
                    background-color: {theme['surface_container']};
                    border-radius: 4px;
                }}
            """)
        
        # Update processed label
        if hasattr(self, 'processed_label'):
            self.processed_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 10px;
                    color: {theme['text_primary']};
                    font-weight: bold;
                    padding: 4px 8px;
                    background-color: {theme['surface_elevated']};
                    border-radius: 3px;
                }}
            """)
        
        # Update attachment failures label
        if hasattr(self, 'attachment_failures_label'):
            self.attachment_failures_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 10px;
                    color: {theme['warning']};
                    font-weight: bold;
                    padding: 4px 8px;
                    background-color: {theme['surface_elevated']};
                    border-radius: 3px;
                }}
            """)
        
        # Update auto-scroll button (dynamic based on state)
        if hasattr(self, 'auto_scroll_btn'):
            # This will be updated dynamically in toggle_auto_scroll, but set a default
            self.auto_scroll_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme['success']};
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 9px;
                    font-weight: bold;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {SUCCESS_HOVER};
                }}
            """)
        
        # Update clear log button
        if hasattr(self, 'clear_log_btn'):
            self.clear_log_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme['surface_elevated']};
                    color: {theme['text_primary']};
                    border: 1px solid {theme['border']};
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 9px;
                    min-width: 60px;
                }}
                QPushButton:hover {{
                    background-color: {theme['surface_hover']};
                }}
            """)
    
    def setup_ui(self):
        """Set up the progress screen UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section with campaign info and step indicator
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # Main content area - split layout
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setChildrenCollapsible(False)
        
        # Left panel - Progress display and controls
        left_panel = self.create_progress_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Sending log and attachment info
        right_panel = self.create_log_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions (3:2 ratio)
        content_splitter.setSizes([480, 320])
        content_splitter.setStretchFactor(0, 3)
        content_splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(content_splitter)
        
        # Control buttons
        controls_layout = self.create_controls()
        main_layout.addLayout(controls_layout)
        
        self.setLayout(main_layout)
        
    def create_header(self):
        """Create the header section with campaign info and status"""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        # Step indicator
        step_layout = QHBoxLayout()
        
        step_label = self.create_themed_label("Step 4 of 4: Sending Emails", "title")
        step_layout.addWidget(step_label)
        
        step_layout.addStretch()
        
        # Campaign status
        self.campaign_status_label = QLabel("Campaign Ready")
        # Theme styling will be applied in apply_theme_customizations()
        step_layout.addWidget(self.campaign_status_label)
        
        header_layout.addLayout(step_layout)
        
        # Campaign timestamp
        timestamp_layout = QHBoxLayout()
        
        self.campaign_timestamp_label = QLabel("Campaign not started")
        self.campaign_timestamp_label.setStyleSheet(SUBTITLE_STYLE)
        timestamp_layout.addWidget(self.campaign_timestamp_label)
        
        timestamp_layout.addStretch()
        
        # Attachment info summary
        self.attachment_info_label = QLabel("No attachments")
        # Theme styling will be applied in apply_theme_customizations()
        timestamp_layout.addWidget(self.attachment_info_label)
        
        header_layout.addLayout(timestamp_layout)
        
        return header_layout
        
    def create_progress_panel(self):
        """Create the left panel with progress display"""
        panel = QGroupBox("Email Sending Progress")
        panel.setStyleSheet(CARD_STYLE)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Progress section
        progress_section = self.create_progress_section()
        layout.addWidget(progress_section)

        # Current status section
        status_section = self.create_status_section()
        layout.addWidget(status_section)

        # Counters section
        counters_section = self.create_counters_section()
        layout.addWidget(counters_section)

        # Remove attachment progress section - keeping only 1 progress bar

        panel.setLayout(layout)
        return panel
        
    def create_progress_section(self):
        """Create the main progress bar section"""
        section = QFrame()
        # Theme styling will be applied in apply_theme_customizations()
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Progress label
        self.progress_label = QLabel("Preparing to send emails")
        theme = self.get_current_theme()
        # Make the main progress label larger and ensure strong contrast.
        # Use a transparent background by default; a subtle translucent
        # backing will be applied in _apply_theme_to_hardcoded_elements if
        # the computed contrast is low for the current theme.
        self.progress_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: 700;
                color: {theme['text_primary']};
                background-color: transparent;
                margin-bottom: 8px;
                padding: 4px 8px;
                border-radius: 4px;
            }}
        """)
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        # Hide the built-in QProgressBar text to avoid overlapping/duplicate
        # percentage text. We show percentage explicitly in `self.percentage_label`.
        try:
            self.progress_bar.setTextVisible(False)
        except Exception:
            # Some PyQt versions may not have setTextVisible; ignore if absent
            pass
        
        # Get theme colors for dynamic styling - single clean progress bar design
        # Previous styling created visual appearance of two progress bars due to:
        # 1. Thick border creating outer "bar" appearance  
        # 2. Background color visible around filled chunk creating inner "bar" appearance
        # This styling creates a single, unified progress bar appearance
        theme_colors = self.theme_manager.get_theme()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {theme_colors['border']};
                border-radius: 6px;
                background-color: {theme_colors['surface']};
                text-align: center;
                font-weight: bold;
                font-size: {FONT_SIZE_SMALL};
                color: {theme_colors['text_primary']};
                height: 24px;
            }}
            QProgressBar::chunk {{
                background-color: {theme_colors['primary']};
                border-radius: 4px;
                margin: 0px;
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        # Progress percentage
        self.percentage_label = QLabel("0%")
        theme = self.get_current_theme()
        self.percentage_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {theme['text_primary']};
                text-align: center;
                font-weight: bold;
            }}
        """)
        self.percentage_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.percentage_label)
        
        section.setLayout(layout)
        return section
        
    def create_status_section(self):
        """Create the current status section"""
        # Theme styling will be applied in apply_theme_customizations()
        
        # Use a minimal, non-card status area so it doesn't look like a second
        # progress bar. Keep it visually light and text-focused.
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                padding: 6px 0px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(4)
        
        # Current email
        self.current_email_label = QLabel("Ready to start sending")
        theme = self.get_current_theme()
        self.current_email_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                color: {theme['text_primary']};
                font-weight: 500;
                text-align: center;
                background-color: transparent;
                border: none;
            }}
        """)
        self.current_email_label.setAlignment(Qt.AlignCenter)
        self.current_email_label.setWordWrap(True)
        layout.addWidget(self.current_email_label)
        
        # Time remaining
        self.time_remaining_label = QLabel("")
        theme = self.get_current_theme()
        self.time_remaining_label.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: {theme['text_secondary']};
                text-align: center;
            }}
        """)
        self.time_remaining_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_remaining_label)
        
        section.setLayout(layout)
        return section
        
    def create_counters_section(self):
        """Create the success/failed counters section"""
        # Theme styling will be applied in apply_theme_customizations()
        
        section = QFrame()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Success counter
        success_frame = QFrame()
        theme = self.get_current_theme()
        success_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['surface_container']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        
        success_layout = QHBoxLayout()
        success_layout.setSpacing(10)
        
        # Success badge
        self.success_badge = QLabel("0")
        self.success_badge.setStyleSheet(SUCCESS_BADGE_STYLE)
        self.success_badge.setAlignment(Qt.AlignCenter)
        success_layout.addWidget(self.success_badge)
        
        success_text = QLabel("Success")
        theme = self.get_current_theme()
        success_text.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {theme['text_primary']};
            }}
        """)
        success_layout.addWidget(success_text)
        
        success_frame.setLayout(success_layout)
        layout.addWidget(success_frame)
        
        # Failed counter
        failed_frame = QFrame()
        theme = self.get_current_theme()
        failed_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['surface_container']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        
        failed_layout = QHBoxLayout()
        failed_layout.setSpacing(10)
        
        # Failed badge
        self.failed_badge = QLabel("0")
        self.failed_badge.setStyleSheet(ERROR_BADGE_STYLE)
        self.failed_badge.setAlignment(Qt.AlignCenter)
        failed_layout.addWidget(self.failed_badge)
        
        failed_text = QLabel("Failed")
        theme = self.get_current_theme()
        failed_text.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {theme['text_primary']};
            }}
        """)
        failed_layout.addWidget(failed_text)
        
        failed_frame.setLayout(failed_layout)
        layout.addWidget(failed_frame)
        
        section.setLayout(layout)
        return section
        
    def create_attachment_progress_section(self):
        """Create attachment processing progress section"""
        # Theme styling will be applied in apply_theme_customizations()
        
        self.attachment_progress_section = QFrame()
        self.attachment_progress_section.setVisible(False)  # Hidden by default
        
        theme = self.get_current_theme()
        self.attachment_progress_section.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['surface_container']};
                border: 1px solid {theme['primary']};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Attachment progress label
        self.attachment_progress_label = QLabel("Processing attachments...")
        theme = self.get_current_theme()
        self.attachment_progress_label.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: {theme['primary']};
                font-weight: bold;
                text-align: center;
            }}
        """)
        self.attachment_progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.attachment_progress_label)
        
        # Attachment errors counter
        self.attachment_errors_label = QLabel("")
        theme = self.get_current_theme()
        self.attachment_errors_label.setStyleSheet(f"""
            QLabel {{
                font-size: 10px;
                color: {theme['error']};
                text-align: center;
            }}
        """)
        self.attachment_errors_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.attachment_errors_label)
        
        self.attachment_progress_section.setLayout(layout)
        return self.attachment_progress_section
        
    def create_log_panel(self):
        """Create the right panel with sending log"""
        panel = QGroupBox("Sending Log")
        panel.setStyleSheet(CARD_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Log statistics
        stats_layout = self.create_log_statistics()
        layout.addLayout(stats_layout)
        
        # Log area
        log_section = self.create_log_section()
        layout.addWidget(log_section)
        
        # Log controls
        log_controls = self.create_log_controls()
        layout.addLayout(log_controls)
        
        panel.setLayout(layout)
        return panel
        
    def create_log_statistics(self):
        """Create log statistics display"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # Total processed
        self.processed_label = QLabel("Processed: 0")
        self.processed_label.setStyleSheet(f"""
            QLabel {{
                font-size: 10px;
                color: {theme['text_primary']};
                font-weight: bold;
                padding: 4px 8px;
                background-color: {theme['surface_elevated']};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.processed_label)
        
        layout.addStretch()
        
        # Attachment failures
        self.attachment_failures_label = QLabel("Attachment issues: 0")
        self.attachment_failures_label.setStyleSheet(f"""
            QLabel {{
                font-size: 10px;
                color: {theme['warning']};
                font-weight: bold;
                padding: 4px 8px;
                background-color: {theme['surface_elevated']};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.attachment_failures_label)
        
        return layout
        
    def create_log_section(self):
        """Create the scrollable log section"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        section = QFrame()
        theme = self.get_current_theme()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Log area
        self.log_area = QTextEdit()
        self.log_area.setStyleSheet(f"""
            QTextEdit {{
                border: none;
                background-color: {theme['surface_elevated']};
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 10px;
                color: {theme['text_primary']};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(300)
        self.log_area.setMaximumHeight(400)
        
        layout.addWidget(self.log_area)
        section.setLayout(layout)
        return section
        
    def create_log_controls(self):
        """Create log control buttons"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        # Auto-scroll toggle
        self.auto_scroll_enabled = True
        self.auto_scroll_btn = QPushButton("Auto-scroll: ON")
        self.auto_scroll_btn.clicked.connect(self.toggle_auto_scroll)
        self.auto_scroll_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['success']};
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 9px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {theme['success_hover']};
            }}
        """)
        layout.addWidget(self.auto_scroll_btn)
        
        layout.addStretch()
        
        # Clear log button
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.clear_log)
        clear_log_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['surface_elevated']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 9px;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: {theme['surface_hover']};
            }}
        """)
        layout.addWidget(clear_log_btn)
        
        return layout
        
    def create_controls(self):
        """Create control buttons section"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Pause/Resume button
        self.pause_button = QPushButton("Pause Sending")
        self.pause_button.clicked.connect(self.on_pause_clicked)
        theme = self.get_current_theme()
        self.pause_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['warning']};
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {theme['warning_hover']};
            }}
            QPushButton:pressed {{
                background-color: {theme['warning_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {theme['disabled']};
                color: {theme['text_disabled']};
            }}
        """)
        layout.addWidget(self.pause_button)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel Remaining")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.cancel_button.setStyleSheet(ERROR_BUTTON_STYLE)
        layout.addWidget(self.cancel_button)
        
        layout.addStretch()
        
        # Exit button
        self.exit_button = self.create_themed_button("Exit", "error")
        self.exit_button.clicked.connect(self.on_exit_clicked)
        
        # Store for theme updates
        if not hasattr(self, 'themed_buttons'):
            self.themed_buttons = []
        self.themed_buttons.append((self.exit_button, "error"))
        layout.addWidget(self.exit_button)
        
        return layout
        
    def connect_signals(self):
        """Connect internal signals"""
        pass
        
    # Event handlers
    def on_pause_clicked(self):
        """Handle pause/resume button click"""
        if self.is_paused:
            self.resume_sending()
        else:
            self.pause_sending()
        self.pause_requested.emit()
        
    def on_cancel_clicked(self):
        """Handle cancel button click"""
        if not self.is_completed:
            reply = QMessageBox.question(
                self,
                "Cancel Sending",
                "Are you sure you want to cancel the remaining emails?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.cancel_sending()
                self.cancel_requested.emit()
        
    def on_exit_clicked(self):
        """Handle exit button click"""
        if not self.is_completed and (self.current_progress > 0):
            reply = QMessageBox.question(
                self,
                "Exit Campaign",
                "Campaign is still in progress. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.exit_clicked.emit()
        else:
            self.exit_clicked.emit()
            
    # Progress control methods
    def pause_sending(self):
        """Pause the sending process"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        self.is_paused = True
        self.pause_button.setText("Resume Sending")
        self.pause_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['success']};
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {theme['success_hover']};
            }}
        """)
        
        self.campaign_status_label.setText("Campaign Paused")
        self.campaign_status_label.setStyleSheet(f"""
            QLabel {{
                color: {theme['warning']};
                font-size: 14px;
                font-weight: bold;
                padding: 6px 12px;
                background-color: {theme['surface_container']};
                border-radius: 4px;
                border: 1px solid {theme['warning']};
            }}
        """)
        
        self.update_status_display()
        self.log_warning("Sending paused by user")
        
        # Pause simulation if active
        if self.simulation_active:
            self.simulation_timer.stop()
        
    def resume_sending(self):
        """Resume the sending process"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        self.is_paused = False
        self.pause_button.setText("Pause Sending")
        self.pause_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['warning']};
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {theme['warning_hover']};
            }}
        """)
        
        self.campaign_status_label.setText("Campaign Active")
        self.campaign_status_label.setStyleSheet(f"""
            QLabel {{
                color: {theme['success']};
                font-size: 14px;
                font-weight: bold;
                padding: 6px 12px;
                background-color: {theme['surface_container']};
                border-radius: 4px;
                border: 1px solid {theme['success']};
            }}
        """)
        
        self.update_status_display()
        self.log_info("Sending resumed")
        
        # Resume simulation if active
        if self.simulation_active and not self.is_cancelled:
            self.simulation_timer.start(800)
        
    def cancel_sending(self):
        """Cancel the remaining sends"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        self.is_cancelled = True
        self.pause_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        
        self.campaign_status_label.setText("Campaign Cancelled")
        self.campaign_status_label.setStyleSheet(f"""
            QLabel {{
                color: {theme['error']};
                font-size: 14px;
                font-weight: bold;
                padding: 6px 12px;
                background-color: {theme['surface_container']};
                border-radius: 4px;
                border: 1px solid {theme['error']};
            }}
        """)
        
        self.update_status_display()
        self.log_warning(f"Campaign cancelled - {self.total_emails - self.current_progress} emails remaining")
        
        # Stop simulation if active
        if self.simulation_active:
            self.simulation_timer.stop()
            self.simulation_active = False
        
    # Progress update methods
    def start_campaign(self, campaign_data):
        """Start the email campaign with provided data"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        self.campaign_data = campaign_data
        self.contacts = campaign_data.get('contacts', [])
        self.attachments = campaign_data.get('attachments', [])
        
        self.total_emails = len(self.contacts)
        self.current_progress = 0
        self.success_count = 0
        self.failed_count = 0
        self.attachment_failures = 0
        
        self.is_paused = False
        self.is_cancelled = False
        self.is_completed = False
        
        self.campaign_start_time = datetime.now()
        
        # Initialize progress bar
        self.progress_bar.setMaximum(self.total_emails)
        self.progress_bar.setValue(0)
        
        # Update displays
        self.update_campaign_info()
        self.update_progress_display()
        
        # Set active status
        self.campaign_status_label.setText("Campaign Active")
        self.campaign_status_label.setStyleSheet(f"""
            QLabel {{
                color: {theme['success']};
                font-size: 14px;
                font-weight: bold;
                padding: 6px 12px;
                background-color: {theme['surface_container']};
                border-radius: 4px;
                border: 1px solid {theme['success']};
            }}
        """)
        
        # Log campaign start
        self.log_info(f"Campaign started - sending to {self.total_emails} recipients")
        if self.attachments:
            total_size = sum(att.get('file_size', 0) for att in self.attachments)
            size_str = self.format_file_size(total_size)
            self.log_info(f"Attachments: {len(self.attachments)} files ({size_str})")
        
        # Start the email sending process
        self.log_info("Starting email sending timer...")

        # Decide whether to run the real sending loop or the demo simulation.
        # PreviewScreen/other callers set 'campaign_ready' and 'preview_completed'
        # when this is a real campaign coming from the preview flow.
        use_real_send = bool(campaign_data.get('campaign_ready') or campaign_data.get('preview_completed'))

        # Reconnect timer callback safely
        try:
            self.simulation_timer.timeout.disconnect()
        except Exception:
            # No prior connection
            pass

        if use_real_send:
            self.simulation_timer.timeout.connect(self.send_next_email)
        else:
            self.simulation_timer.timeout.connect(self.simulate_next_email)

        if not self.simulation_active:
            self.simulation_active = True
            self.simulation_timer.start(1000)  # Start sending emails with 1 second interval
        
    def update_progress(self, current, current_email="", time_remaining="", attachment_info=""):
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
            
            # Log attachment processing if provided
            if attachment_info:
                self.log_attachment_info(attachment_info)
            
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
        # Progress text and percentage
        if self.total_emails > 0:
            percentage = int((self.current_progress / self.total_emails) * 100)
            self.progress_label.setText(f"Sending {self.current_progress} of {self.total_emails} emails")
            self.percentage_label.setText(f"{percentage}%")

            # Ensure progress label has good contrast in dark mode
            theme = self.get_current_theme()
            self.progress_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    font-weight: bold;
                    color: {theme['text_primary']};
                    text-align: center;
                    background-color: transparent;
                    border: none;
                }}
            """)

        # Current status
        self.update_status_display()

        # Update counters
        self.update_counters()

        # Update log statistics
        self.update_log_statistics()
        
    def update_status_display(self):
        """Update current status display"""
        if self.is_paused:
            self.current_email_label.setText("Sending paused")
            self.time_remaining_label.setText("")
        elif self.is_cancelled:
            self.current_email_label.setText("Sending cancelled")
            self.time_remaining_label.setText("")
        elif self.current_progress >= self.total_emails:
            self.current_email_label.setText("All emails sent!")
            self.time_remaining_label.setText("")
        elif self.current_email:
            self.current_email_label.setText(f"Currently sending to: {self.current_email}")
            if self.estimated_time:
                self.time_remaining_label.setText(f"Estimated time remaining: {self.estimated_time}")
        else:
            self.current_email_label.setText("Ready to start sending")
            self.time_remaining_label.setText("")
            
    def update_counters(self):
        """Update success/failed counters"""
        self.success_badge.setText(str(self.success_count))
        self.failed_badge.setText(str(self.failed_count))
        
    def update_log_statistics(self):
        """Update log statistics"""
        total_processed = self.success_count + self.failed_count
        self.processed_label.setText(f"Processed: {total_processed}")
        
        if self.attachment_failures > 0:
            self.attachment_failures_label.setText(f"Attachment issues: {self.attachment_failures}")
            self.attachment_failures_label.setVisible(True)
        else:
            self.attachment_failures_label.setVisible(False)
            
    def update_campaign_info(self):
        """Update campaign information display"""
        if self.campaign_start_time:
            formatted_time = self.campaign_start_time.strftime("%B %d, %Y at %I:%M %p")
            self.campaign_timestamp_label.setText(f"Campaign started: {formatted_time}")
        
        # Update attachment info
        if self.attachments:
            total_size = sum(att.get('file_size', 0) for att in self.attachments)
            size_str = self.format_file_size(total_size)
            self.attachment_info_label.setText(f"📎 {len(self.attachments)} attachments ({size_str})")
        else:
            self.attachment_info_label.setText("No attachments")
            
    # Logging methods
    def log_success(self, email, attachment_info=""):
        """Log a successful email send"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        self.success_count += 1
        self.log_entry(f"✅ Sent to {email}", theme['success'])
        
        if attachment_info:
            self.log_entry(f"   📎 {attachment_info}", theme['text_secondary'])
        
        self.update_counters()
        self.email_sent.emit(email, True)
        
    def log_failure(self, email, reason, is_attachment_issue=False):
        """Log a failed email send"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        self.failed_count += 1
        
        # Add email to failed emails list for CSV export
        self.failed_emails.append(email)
        
        if is_attachment_issue:
            self.attachment_failures += 1
            self.log_entry(f"❌ Failed to send to {email} - {reason}", theme['error'])
            self.log_entry(f"   📎 Attachment processing error", theme['warning'])
        else:
            self.log_entry(f"❌ Failed to send to {email} - {reason}", theme['error'])
        
        self.update_counters()
        self.email_sent.emit(email, False)
        
    def log_attachment_info(self, info):
        """Log attachment-specific information"""
        # Get current theme for styling
        theme = self.get_current_theme()
        self.log_entry(f"📎 {info}", theme['primary'])
        
    def log_info(self, message):
        """Log an info message"""
        # Get current theme for styling
        theme = self.get_current_theme()
        self.log_entry(f"ℹ️ {message}", theme['primary'])
        
    def log_warning(self, message):
        """Log a warning message"""
        # Get current theme for styling
        theme = self.get_current_theme()
        self.log_entry(f"⚠️ {message}", theme['warning'])
        
    def log_entry(self, message, color=None):
        """Add an entry to the log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Resolve default color from theme when not provided
        if color is None:
            theme = self.get_current_theme()
            color = theme.get('text_primary', '#333333')
        html_message = f'<span style="color: {color};">[{timestamp}] {message}</span>'
        
        # Add to log
        self.log_area.append(html_message)
        
        # Auto-scroll to bottom if enabled
        if self.auto_scroll_enabled:
            cursor = self.log_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.log_area.setTextCursor(cursor)
            
    # Log control methods
    def toggle_auto_scroll(self):
        """Toggle auto-scroll functionality"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        self.auto_scroll_enabled = not self.auto_scroll_enabled
        
        if self.auto_scroll_enabled:
            self.auto_scroll_btn.setText("Auto-scroll: ON")
            self.auto_scroll_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme['success']};
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 9px;
                    font-weight: bold;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {theme['success_hover']};
                }}
            """)
        else:
            self.auto_scroll_btn.setText("Auto-scroll: OFF")
            self.auto_scroll_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme['surface_elevated']};
                    color: {theme['text_primary']};
                    border: 1px solid {theme['border']};
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 9px;
                    font-weight: bold;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {theme['surface_hover']};
                }}
            """)
            
    def clear_log(self):
        """Clear the log area"""
        self.log_area.clear()
        
    # Campaign completion methods
    def complete_campaign(self):
        """Mark campaign as complete"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        self.is_completed = True
        self.current_progress = self.total_emails
        self.progress_bar.setValue(self.total_emails)
        
        # Update status
        self.campaign_status_label.setText("Campaign Completed")
        self.campaign_status_label.setStyleSheet(f"""
            QLabel {{
                color: {theme['success']};
                font-size: 14px;
                font-weight: bold;
                padding: 6px 12px;
                background-color: {theme['surface_container']};
                border-radius: 4px;
                border: 1px solid {theme['success']};
            }}
        """)
        
        # Disable control buttons
        self.pause_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        
        self.update_progress_display()
        
        # Summary log
        duration = ""
        if self.campaign_start_time:
            elapsed = datetime.now() - self.campaign_start_time
            minutes = int(elapsed.total_seconds() / 60)
            seconds = int(elapsed.total_seconds() % 60)
            duration = f" in {minutes}m {seconds}s"
            
        self.log_info(f"Campaign completed{duration}! Total: {self.success_count + self.failed_count}, Success: {self.success_count}, Failed: {self.failed_count}")
        
        if self.attachment_failures > 0:
            self.log_warning(f"Attachment issues encountered: {self.attachment_failures}")
        
        # Emit completion signal
        completion_stats = {
            'total_emails': self.total_emails,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'attachment_failures': self.attachment_failures,
            'duration': duration,
            'start_time': self.campaign_start_time,
            'end_time': datetime.now(),
            # Include campaign data for CSV export
            'contacts': self.contacts,
            'attachments': self.attachments,
            'campaign_data': self.campaign_data,
            'failed_emails': self.failed_emails
        }
        
        self.campaign_completed.emit(completion_stats)
        
        # Stop simulation if active
        if self.simulation_active:
            self.simulation_timer.stop()
            self.simulation_active = False
        
    # Utility methods
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
            
    # Simulation methods (for demo purposes)
    def start_simulation(self, demo_emails=None, demo_attachments=None):
        """Start simulation for demo purposes"""
        if demo_emails is None:
            demo_emails = [f"user{i}@example.com" for i in range(1, 101)]
            
        # Create mock campaign data
        campaign_data = {
            'contacts': [{'email': email} for email in demo_emails],
            'attachments': demo_attachments or [],
            'email_data': {
                'subject': 'Demo Email Campaign',
                'content_plain': 'This is a demo email campaign.'
            }
        }
        
        self.start_campaign(campaign_data)
        
        # Start simulation timer
        self.simulation_active = True
        self.simulation_timer.start(800)  # Send every 800ms
        
    def send_next_email(self):
        """Send the next email using EmailService"""
        print(f"🔄 send_next_email called - Progress: {self.current_progress}/{self.total_emails}")
        
        if (self.is_paused or self.is_cancelled or 
            self.current_progress >= self.total_emails):
            print(f"⚠️ Stopping: paused={self.is_paused}, cancelled={self.is_cancelled}, progress={self.current_progress}/{self.total_emails}")
            return
            
        contact = self.contacts[self.current_progress]
        email = contact.get('email', f"demo{self.current_progress}@example.com")
        
        # Calculate time remaining
        remaining = self.total_emails - self.current_progress - 1
        if remaining > 75:
            time_remaining = f"{int((remaining * 0.8) / 60)} minutes"
        else:
            time_remaining = f"{int(remaining * 0.8)} seconds"
            
        # Update progress
        self.update_progress(
            self.current_progress + 1,
            email,
            time_remaining
        )
        
        # Prepare email data for sending
        email_data = {
            'from_email': self.campaign_data.get('from_email', ''),
            'subject': self.campaign_data.get('subject', ''),
            'content_html': self.campaign_data.get('content_html', ''),
            'content_plain': self.campaign_data.get('content_plain', ''),
            'to_email': email,
            'to_name': contact.get('firstname', '') + ' ' + contact.get('lastname', ''),
            'attachments': self.attachments
        }
        
        print(f"📝 Email data: subject='{email_data['subject']}', from='{email_data['from_email']}', to='{email}'")
        print(f"📎 Attachments: {len(self.attachments)} files")
        print(f"🔍 Attachment data: {self.attachments}")
        print(f"🔧 Attachment types: {[type(att) for att in self.attachments]}")
        
        # Actually send the email
        try:
            print(f"📧 Sending email to {email}")
            
            # Test connection first
            print("🔐 Testing SMTP connection...")
            connection_success, connection_error = self.email_service.test_connection()
            if not connection_success:
                print(f"❌ SMTP connection failed: {connection_error}")
                self.log_failure(email, f"SMTP connection failed: {connection_error}", False)
                return
            print("✅ SMTP connection successful")
            
            # Create a Contact object from the dict
            from models.contact import Contact
            print(f"🔍 Contact dict: {contact}")
            
            try:
                contact_obj = Contact.from_dict(contact)
                print(f"✅ Contact object created: {contact_obj}")
                print(f"🔧 Contact type: {type(contact_obj)}")
            except Exception as e:
                print(f"❌ Failed to create Contact object: {e}")
                self.log_failure(email, f"Contact creation failed: {e}", False)
                return
            
            # Personalize email content before sending
            raw_subject = self.campaign_data.get('subject', '')
            raw_body = self.campaign_data.get('content_html', '')
            
            # Get personalization data from contact
            personalization_data = contact_obj.get_personalization_data()
            print(f"📝 Personalization data: {personalization_data}")
            
            # Replace placeholders in subject and body
            personalized_subject = raw_subject
            personalized_body = raw_body
            
            for placeholder, value in personalization_data.items():
                placeholder_pattern = "{" + placeholder + "}"
                personalized_subject = personalized_subject.replace(placeholder_pattern, value)
                personalized_body = personalized_body.replace(placeholder_pattern, value)
            
            print(f"📧 Original body: {raw_body[:100]}...")
            print(f"🎯 Personalized body: {personalized_body[:100]}...")
            
            # Convert attachment dicts to Attachment objects
            attachment_objects = []
            if self.attachments:
                print(f"🔧 Converting {len(self.attachments)} attachment dicts to Attachment objects")
                from models.attachment import Attachment
                
                for att_dict in self.attachments:
                    try:
                        # Use filepath from the dict to create Attachment object
                        filepath = att_dict.get('filepath', '')
                        if filepath and os.path.exists(filepath):
                            attachment_obj = Attachment.from_file_path(filepath)
                            attachment_objects.append(attachment_obj)
                            print(f"✅ Converted attachment: {attachment_obj.filename}")
                        else:
                            print(f"❌ Invalid filepath for attachment: {att_dict.get('filename', 'unknown')}")
                    except Exception as e:
                        print(f"❌ Failed to convert attachment {att_dict.get('filename', 'unknown')}: {e}")
                
                print(f"📎 Successfully converted {len(attachment_objects)} attachments")
            
            # Send the email using the correct method with personalized content
            result = self.email_service.send_single_email(
                contact=contact_obj,
                subject=personalized_subject,  # Use personalized content
                body=personalized_body,        # Use personalized content
                sender_email=self.campaign_data.get('from_email', ''),
                is_html=True,
                attachments=attachment_objects  # Use converted Attachment objects
            )
            
            print(f"📬 Email result: {result.status}, attempts: {result.attempts}")
            
            # Log result based on EmailResult status
            if result.status.value == "sent":
                attachment_info = f"Sent with {len(self.attachments)} attachments" if self.attachments else ""
                self.log_success(email, attachment_info)
            else:
                error_msg = result.error_message or "Unknown error"
                self.log_failure(email, error_msg, False)
                print(f"❌ Email failed: {error_msg}")
                
        except Exception as e:
            # Handle sending errors
            error_msg = str(e)
            print(f"💥 Exception sending email: {error_msg}")
            is_attachment_issue = "attachment" in error_msg.lower()
            self.log_failure(email, error_msg, is_attachment_issue)
            
        # Check if campaign is complete
        if self.current_progress >= self.total_emails:
            self.simulation_timer.stop()
            self.simulation_active = False
            self.complete_campaign()

    def simulate_next_email(self):
        """Simulate sending the next email (for demo)"""
        if (self.is_paused or self.is_cancelled or 
            self.current_progress >= self.total_emails):
            return
            
        contact = self.contacts[self.current_progress]
        email = contact.get('email', f"demo{self.current_progress}@example.com")
        
        # Calculate time remaining
        remaining = self.total_emails - self.current_progress - 1
        if remaining > 75:
            time_remaining = f"{int((remaining * 0.8) / 60)} minutes"
        else:
            time_remaining = f"{int(remaining * 0.8)} seconds"
            
        # Update progress
        self.update_progress(
            self.current_progress + 1,
            email,
            time_remaining
        )
        
        # Simulate success/failure (90% success rate)
        import random
        
        # Simulate attachment processing for some emails
        attachment_info = ""
        if self.attachments and random.random() < 0.3:  # 30% chance of attachment processing info
            attachment_info = f"Processed {len(self.attachments)} attachments"
            
        if random.random() < 0.9:  # 90% success rate
            self.log_success(email, attachment_info)
        else:
            # Simulate different types of failures
            failure_reasons = [
                "Invalid email address",
                "Mailbox full",
                "Server timeout",
                "Attachment too large"
            ]
            reason = random.choice(failure_reasons)
            is_attachment_issue = "Attachment" in reason
            self.log_failure(email, reason, is_attachment_issue)
            
        # Check if campaign is complete
        if self.current_progress >= self.total_emails:
            self.simulation_timer.stop()
            self.simulation_active = False
            self.complete_campaign()
            
    # Public interface methods
    def set_campaign_data(self, campaign_data):
        """Set campaign data for sending"""
        self.campaign_data = campaign_data
        self.contacts = campaign_data.get('contacts', [])
        self.attachments = campaign_data.get('attachments', [])
        self.total_emails = len(self.contacts)
        
        # Update displays
        self.update_campaign_info()
        
    def get_progress_status(self):
        """Get current progress status"""
        return {
            'total_emails': self.total_emails,
            'current_progress': self.current_progress,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'attachment_failures': self.attachment_failures,
            'is_paused': self.is_paused,
            'is_cancelled': self.is_cancelled,
            'is_completed': self.is_completed
        }
        
    def reset_progress(self):
        """Reset all progress tracking"""
        # Get current theme for styling
        theme = self.get_current_theme()
        
        self.campaign_data = {}
        self.contacts = []
        self.attachments = []
        self.campaign_start_time = None
        
        self.total_emails = 0
        self.current_progress = 0
        self.success_count = 0
        self.failed_count = 0
        self.attachment_failures = 0
        self.failed_emails = []  # Reset failed emails list
        
        self.is_paused = False
        self.is_cancelled = False
        self.is_completed = False
        self.current_email = ""
        self.estimated_time = ""
        
        # Reset UI
        self.progress_bar.setValue(0)
        self.progress_label.setText("Preparing to send emails")
        self.percentage_label.setText("0%")
        self.current_email_label.setText("Ready to start sending")
        self.time_remaining_label.setText("")
        self.campaign_timestamp_label.setText("Campaign not started")
        self.attachment_info_label.setText("No attachments")
        self.log_area.clear()
        
        # Reset buttons
        self.pause_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.pause_button.setText("Pause Sending")
        
        # Reset status
        self.campaign_status_label.setText("Campaign Ready")
        self.campaign_status_label.setStyleSheet(f"""
            QLabel {{
                color: {theme['primary']};
                font-size: 14px;
                font-weight: bold;
                padding: 6px 12px;
                background-color: {theme['surface_container']};
                border-radius: 4px;
                border: 1px solid {theme['primary']};
            }}
        """)
        
        # Update all displays
        self.update_counters()
        self.update_log_statistics()
        
        # Stop simulation if active
        if self.simulation_active:
            self.simulation_timer.stop()
            self.simulation_active = False


# For development: run screen without test data
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    print("📊 ProgressScreen - Enhanced Progress Screen for Mini Email CRM")
    print("🚀 Starting clean progress screen (no test data)")
    print("💡 For full testing with sample data, run: python demos/demo_progress_screen.py")
    print("📝 For automated tests, run: python tests/test_progress_screen.py")
    print()
    
    app = QApplication(sys.argv)
    
    # Create clean screen
    screen = ProgressScreen()
    screen.setWindowTitle("Step 4 - Progress")
    screen.resize(1200, 800)
    
    # Connect basic signals
    screen.exit_clicked.connect(app.quit)
    
    # Show instructions
    print("📖 Instructions:")
    print("• This is the clean progress screen without test data")
    print("• Use the demo file to see it with sample campaign simulation")
    print("• The screen shows the UI layout and styling")
    print("• All functionality is implemented but needs data to be useful")
    
    screen.show()
    sys.exit(app.exec_())