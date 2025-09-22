"""
Enhanced File Upload Widget with improved UX for Phase 8 Task 24
Features: Loading indicators, improved error messages, tooltips, drag-drop feedback
"""

import os
import csv
import time
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QFrame, QMessageBox, QProgressBar, QToolTip,
    QApplication, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSignal as Signal
from PyQt5.QtGui import (
    QFont, QPalette, QDragEnterEvent, QDropEvent, QMovie, 
    QPixmap, QPainter, QColor, QBrush
)

from ui.styles.stylesheet import (
    BUTTON_STYLE, SUBTITLE_STYLE, CARD_STYLE, SUCCESS_GREEN, ERROR_RED,
    DARK_GREY, LIGHT_GREY, BORDER_GREY, FONT_SIZE_SMALL, PRIMARY_BLUE,
    WARNING_ORANGE
)
from core.csv_handler import CSVHandler


class FileValidationThread(QThread):
    """Background thread for file validation to prevent UI blocking"""
    validation_complete = Signal(dict)
    progress_update = Signal(int)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.csv_handler = CSVHandler()
    
    def run(self):
        """Run validation in background thread"""
        try:
            # Step 1: File validation (25%)
            self.progress_update.emit(25)
            file_result = self.csv_handler.validate_file(self.file_path)
            
            if not file_result['valid']:
                self.validation_complete.emit({
                    'success': False,
                    'errors': file_result['errors'],
                    'step': 'file_validation'
                })
                return
            
            # Step 2: Structure validation (50%)
            self.progress_update.emit(50)
            structure_result = self.csv_handler.validate_csv_structure(self.file_path)
            
            if not structure_result['valid']:
                self.validation_complete.emit({
                    'success': False,
                    'errors': structure_result['errors'],
                    'step': 'structure_validation',
                    'details': structure_result
                })
                return
            
            # Step 3: Sample data preview (75%)
            self.progress_update.emit(75)
            sample_result = self.csv_handler.get_sample_data(self.file_path, 3)
            
            # Step 4: Complete (100%)
            self.progress_update.emit(100)
            
            self.validation_complete.emit({
                'success': True,
                'file_info': file_result,
                'structure': structure_result,
                'sample': sample_result,
                'step': 'complete'
            })
            
        except Exception as e:
            self.validation_complete.emit({
                'success': False,
                'errors': [f"Validation error: {str(e)}"],
                'step': 'exception'
            })


class EnhancedFileUploadWidget(QWidget):
    """
    Enhanced file upload widget with improved UX features:
    - Loading indicators during validation
    - Better error messages with suggestions
    - Tooltips and help text
    - Visual drag-drop feedback
    - Responsive design
    """
    
    # Signals
    file_selected = pyqtSignal(str, dict)  # filepath, validation_result
    validation_started = pyqtSignal(str)  # filepath
    validation_progress = pyqtSignal(int)  # progress percentage
    validation_error = pyqtSignal(str, list)  # error_type, error_messages
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file_path = None
        self.validation_thread = None
        self.drag_active = False
        self.setup_ui()
        self.setup_tooltips()
        
    def setup_ui(self):
        """Set up the enhanced user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Header with help text
        header_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Upload Contact List")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {DARK_GREY};
                margin-bottom: 4px;
            }}
        """)
        header_layout.addWidget(title_label)
        
        # Help text
        help_label = QLabel("Select a CSV file containing email addresses and contact information")
        help_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                color: #666;
                margin-bottom: 8px;
            }}
        """)
        help_label.setWordWrap(True)
        header_layout.addWidget(help_label)
        
        layout.addLayout(header_layout)
        
        # Enhanced drag-and-drop zone
        self.drop_zone = self.create_enhanced_drop_zone()
        layout.addWidget(self.drop_zone)
        
        # Action buttons layout
        button_layout = QHBoxLayout()
        
        # File browser button
        self.browse_button = QPushButton("Browse Files")
        self.browse_button.setStyleSheet(f"""
            QPushButton {{
                {BUTTON_STYLE}
                min-width: 120px;
                padding: 8px 16px;
            }}
        """)
        self.browse_button.clicked.connect(self.browse_file)
        button_layout.addWidget(self.browse_button)
        
        # Clear button (initially hidden)
        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet(f"""
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
        """)
        self.clear_button.clicked.connect(self.clear_selection)
        self.clear_button.hide()
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {BORDER_GREY};
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {PRIMARY_BLUE};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Selected file display
        self.file_info_widget = self.create_file_info_widget()
        layout.addWidget(self.file_info_widget)
        
        # Enhanced feedback area
        self.feedback_widget = self.create_feedback_widget()
        layout.addWidget(self.feedback_widget)
        
        self.setLayout(layout)
        
    def create_enhanced_drop_zone(self):
        """Create enhanced drag-and-drop zone with better visual feedback"""
        drop_frame = QFrame()
        drop_frame.setFixedHeight(180)
        drop_frame.setAcceptDrops(True)
        drop_frame.setObjectName("dropZone")
        
        # Install event filter for drag/drop events
        drop_frame.dragEnterEvent = self.dragEnterEvent
        drop_frame.dragLeaveEvent = self.dragLeaveEvent
        drop_frame.dropEvent = self.dropEvent
        
        self.update_drop_zone_style(drop_frame, False, False)
        
        # Content layout
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setSpacing(8)
        
        # Large file icon
        icon_label = QLabel("📂")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                border: none;
                background: transparent;
                margin: 8px;
            }
        """)
        content_layout.addWidget(icon_label)
        
        # Main instruction
        main_instruction = QLabel("Drop CSV file here")
        main_instruction.setAlignment(Qt.AlignCenter)
        main_instruction.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {DARK_GREY};
                border: none;
                background: transparent;
                margin: 4px;
            }}
        """)
        content_layout.addWidget(main_instruction)
        
        # Secondary instruction
        sub_instruction = QLabel("or click Browse Files to select")
        sub_instruction.setAlignment(Qt.AlignCenter)
        sub_instruction.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                color: #888;
                border: none;
                background: transparent;
                margin: 2px;
            }}
        """)
        content_layout.addWidget(sub_instruction)
        
        # Requirements text
        requirements = QLabel("Supports: CSV files with email, firstname, lastname columns")
        requirements.setAlignment(Qt.AlignCenter)
        requirements.setStyleSheet(f"""
            QLabel {{
                font-size: 10px;
                color: #999;
                border: none;
                background: transparent;
                margin: 4px;
            }}
        """)
        requirements.setWordWrap(True)
        content_layout.addWidget(requirements)
        
        drop_frame.setLayout(content_layout)
        return drop_frame
    
    def update_drop_zone_style(self, drop_zone, is_hover, is_drag_active, is_error=False):
        """Update drop zone styling based on state"""
        if is_error:
            border_color = ERROR_RED
            bg_color = "#ffebee"
        elif is_drag_active:
            border_color = PRIMARY_BLUE
            bg_color = "#e3f2fd"
        elif is_hover:
            border_color = "#888"
            bg_color = "#f8f9fa"
        else:
            border_color = BORDER_GREY
            bg_color = LIGHT_GREY
        
        border_style = "solid" if is_drag_active else "dashed"
        
        drop_zone.setStyleSheet(f"""
            QFrame#dropZone {{
                border: 2px {border_style} {border_color};
                border-radius: 8px;
                background-color: {bg_color};
                margin: 4px;
            }}
        """)
    
    def create_file_info_widget(self):
        """Create widget to display selected file information"""
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Box)
        info_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                background-color: white;
                padding: 8px;
                margin: 2px;
            }}
        """)
        info_frame.hide()  # Initially hidden
        
        layout = QVBoxLayout()
        layout.setSpacing(4)
        
        # File name and size
        self.file_name_label = QLabel()
        self.file_name_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                color: {DARK_GREY};
                font-size: {FONT_SIZE_SMALL};
            }}
        """)
        layout.addWidget(self.file_name_label)
        
        # File details (size, type, etc.)
        self.file_details_label = QLabel()
        self.file_details_label.setStyleSheet(f"""
            QLabel {{
                color: #666;
                font-size: 10px;
            }}
        """)
        layout.addWidget(self.file_details_label)
        
        # Preview info
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY_BLUE};
                font-size: 10px;
                font-style: italic;
            }}
        """)
        layout.addWidget(self.preview_label)
        
        info_frame.setLayout(layout)
        return info_frame
    
    def create_feedback_widget(self):
        """Create enhanced feedback widget for errors and warnings"""
        feedback_frame = QFrame()
        feedback_frame.setFrameStyle(QFrame.NoFrame)
        feedback_frame.hide()  # Initially hidden
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Status icon and message
        self.feedback_icon = QLabel()
        self.feedback_icon.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.feedback_icon)
        
        self.feedback_message = QLabel()
        self.feedback_message.setWordWrap(True)
        self.feedback_message.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.feedback_message)
        
        # Additional details (for errors)
        self.feedback_details = QLabel()
        self.feedback_details.setWordWrap(True)
        self.feedback_details.setStyleSheet("font-size: 10px; color: #666;")
        layout.addWidget(self.feedback_details)
        
        feedback_frame.setLayout(layout)
        return feedback_frame
    
    def setup_tooltips(self):
        """Set up helpful tooltips for UI elements"""
        self.browse_button.setToolTip(
            "Browse and select a CSV file from your computer.\n"
            "Supported formats: .csv files with contact information."
        )
        
        self.drop_zone.setToolTip(
            "Drag and drop a CSV file here for quick upload.\n"
            "Required columns: email, firstname, lastname\n"
            "Optional columns: company, phone, title"
        )
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events with visual feedback"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].toLocalFile().endswith('.csv'):
                event.acceptProposedAction()
                self.drag_active = True
                self.update_drop_zone_style(self.drop_zone, False, True)
                return
        
        # Invalid file or multiple files
        event.ignore()
        self.update_drop_zone_style(self.drop_zone, False, False, True)
        
        # Show temporary tooltip
        QToolTip.showText(
            event.pos(),
            "Only single CSV files are supported",
            self
        )
    
    def dragLeaveEvent(self, event):
        """Handle drag leave events"""
        self.drag_active = False
        self.update_drop_zone_style(self.drop_zone, False, False)
    
    def dropEvent(self, event: QDropEvent):
        """Handle file drops with validation"""
        self.drag_active = False
        self.update_drop_zone_style(self.drop_zone, False, False)
        
        urls = event.mimeData().urls()
        if urls and len(urls) == 1:
            file_path = urls[0].toLocalFile()
            if file_path.endswith('.csv'):
                self.handle_file_selection(file_path)
                event.acceptProposedAction()
            else:
                self.show_error("Invalid file type", 
                              ["Please select a CSV file (.csv extension)"])
        else:
            self.show_error("Invalid selection", 
                          ["Please drop only one CSV file at a time"])
    
    def browse_file(self):
        """Open file browser dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV Contact File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.handle_file_selection(file_path)
    
    def handle_file_selection(self, file_path):
        """Handle file selection and start validation"""
        self.selected_file_path = file_path
        self.clear_feedback()
        
        # Show file info immediately
        self.show_file_info(file_path)
        
        # Start validation
        self.start_validation(file_path)
    
    def show_file_info(self, file_path):
        """Display basic file information"""
        file_path_obj = Path(file_path)
        file_size = file_path_obj.stat().st_size
        
        # File name
        self.file_name_label.setText(f"📄 {file_path_obj.name}")
        
        # File details
        size_mb = file_size / (1024 * 1024)
        if size_mb < 1:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{size_mb:.1f} MB"
        
        self.file_details_label.setText(f"Size: {size_str} • Type: CSV")
        
        # Show the widget
        self.file_info_widget.show()
        self.clear_button.show()
    
    def start_validation(self, file_path):
        """Start file validation in background thread"""
        self.validation_started.emit(file_path)
        
        # Show progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        # Update preview
        self.preview_label.setText("Validating file...")
        
        # Start validation thread
        self.validation_thread = FileValidationThread(file_path)
        self.validation_thread.progress_update.connect(self.update_progress)
        self.validation_thread.validation_complete.connect(self.handle_validation_result)
        self.validation_thread.start()
    
    def update_progress(self, progress):
        """Update validation progress"""
        self.progress_bar.setValue(progress)
        self.validation_progress.emit(progress)
        
        # Update status text based on progress
        if progress <= 25:
            status = "Checking file..."
        elif progress <= 50:
            status = "Analyzing structure..."
        elif progress <= 75:
            status = "Previewing data..."
        else:
            status = "Finalizing..."
        
        self.preview_label.setText(status)
    
    def handle_validation_result(self, result):
        """Handle validation completion"""
        self.progress_bar.hide()
        
        if result['success']:
            self.show_success(result)
            self.file_selected.emit(self.selected_file_path, result)
        else:
            self.show_error(f"Validation failed at {result['step']}", result['errors'])
            self.validation_error.emit(result['step'], result['errors'])
    
    def show_success(self, result):
        """Display success feedback"""
        self.feedback_widget.show()
        
        # Success icon
        self.feedback_icon.setText("✅")
        self.feedback_icon.setStyleSheet(f"color: {SUCCESS_GREEN}; font-size: 16px;")
        
        # Success message
        structure = result.get('structure', {})
        row_count = structure.get('row_count', 0)
        columns = structure.get('columns', [])
        
        self.feedback_message.setText(f"File validated successfully!")
        self.feedback_message.setStyleSheet(f"color: {SUCCESS_GREEN}; font-weight: bold;")
        
        # Details
        details = f"Found {row_count} rows with columns: {', '.join(columns[:3])}{'...' if len(columns) > 3 else ''}"
        self.feedback_details.setText(details)
        self.feedback_details.setStyleSheet("color: #666; font-size: 10px;")
        
        # Update preview
        self.preview_label.setText(f"Ready to import {row_count} contacts")
        self.preview_label.setStyleSheet(f"color: {SUCCESS_GREEN}; font-weight: bold;")
    
    def show_error(self, error_type, errors):
        """Display error feedback with helpful suggestions"""
        self.feedback_widget.show()
        
        # Error icon
        self.feedback_icon.setText("❌")
        self.feedback_icon.setStyleSheet(f"color: {ERROR_RED}; font-size: 16px;")
        
        # Error message
        self.feedback_message.setText(f"{error_type}")
        self.feedback_message.setStyleSheet(f"color: {ERROR_RED}; font-weight: bold;")
        
        # Error details with suggestions
        error_text = "\\n".join(errors)
        suggestions = self.get_error_suggestions(errors)
        if suggestions:
            error_text += f"\\n\\nSuggestions:\\n{suggestions}"
        
        self.feedback_details.setText(error_text)
        self.feedback_details.setStyleSheet(f"color: {ERROR_RED}; font-size: 10px;")
        
        # Update preview
        self.preview_label.setText("❌ File validation failed")
        self.preview_label.setStyleSheet(f"color: {ERROR_RED};")
    
    def get_error_suggestions(self, errors):
        """Generate helpful suggestions based on error types"""
        suggestions = []
        
        error_text = " ".join(errors).lower()
        
        if "required columns not found" in error_text:
            suggestions.append("• Ensure your CSV has columns named 'email', 'firstname', and 'lastname'")
            suggestions.append("• Check that the first row contains column headers")
        
        if "file too large" in error_text:
            suggestions.append("• Try splitting the file into smaller chunks")
            suggestions.append("• Remove unnecessary columns to reduce file size")
        
        if "invalid email format" in error_text:
            suggestions.append("• Check that email addresses are properly formatted (user@domain.com)")
            suggestions.append("• Remove any rows with incomplete email addresses")
        
        if "file not found" in error_text:
            suggestions.append("• Make sure the file exists and you have permission to read it")
            suggestions.append("• Try copying the file to a different location")
        
        return "\\n".join(suggestions)
    
    def clear_feedback(self):
        """Clear all feedback displays"""
        self.feedback_widget.hide()
        self.preview_label.setText("")
        self.progress_bar.hide()
    
    def clear_selection(self):
        """Clear the current file selection"""
        self.selected_file_path = None
        self.file_info_widget.hide()
        self.clear_button.hide()
        self.clear_feedback()
        self.update_drop_zone_style(self.drop_zone, False, False)
    
    def get_selected_file(self):
        """Get the currently selected file path"""
        return self.selected_file_path
    
    def set_enabled(self, enabled):
        """Enable or disable the widget"""
        super().setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.drop_zone.setAcceptDrops(enabled)
        
        if not enabled:
            self.update_drop_zone_style(self.drop_zone, False, False)