"""
File Upload Widget for Mini Email CRM
Provides drag-and-drop functionality and file browser dialog for CSV contact files
"""

import os
import csv
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QDragEnterEvent, QDropEvent

from ui.styles.stylesheet import (
    BUTTON_STYLE, SUBTITLE_STYLE, CARD_STYLE, SUCCESS_GREEN, ERROR_RED,
    DARK_GREY, LIGHT_GREY, BORDER_GREY, FONT_SIZE_SMALL
)

# Import theme system
from ui.base.themed_widgets import ThemeAwareMixin


class FileUploadWidget(QWidget, ThemeAwareMixin):
    """
    Custom widget for file upload with drag-and-drop support
    Specifically designed for CSV contact file uploads
    """
    
    # Signals
    file_selected = pyqtSignal(str)  # Emitted when a valid file is selected
    validation_error = pyqtSignal(str)  # Emitted when validation fails
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__init_theme_awareness__()  # Initialize theme awareness
        self.selected_file_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        
        # Create drag-and-drop zone
        self.drop_zone = self.create_drop_zone()
        layout.addWidget(self.drop_zone)
        
        # File browser button
        self.browse_button = QPushButton("Browse for CSV File")
        self.browse_button.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_button)
        
        # Selected file display
        self.file_info_label = QLabel("No file selected")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        # Theme styling will be applied in apply_theme_customizations()
        layout.addWidget(self.file_info_label)
        
        # Validation feedback
        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setWordWrap(True)
        layout.addWidget(self.feedback_label)
        
        self.setLayout(layout)
        
        # Apply initial theme
        self.apply_theme_customizations()
        
    def apply_theme_customizations(self):
        """Apply theme-aware styling to all UI elements"""
        theme = self.get_current_theme()
        
        # Update file info label (no file selected state)
        if hasattr(self, 'file_info_label') and self.file_info_label.text() == "No file selected":
            self.file_info_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme['text_placeholder']};
                    font-style: italic;
                }}
            """)
        
        # Update feedback label
        if hasattr(self, 'feedback_label'):
            self.feedback_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme['text_primary']};
                }}
            """)
        
        # Update browse button
        if hasattr(self, 'browse_button'):
            self.browse_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme['primary']};
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {theme['primary_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {theme['primary_pressed']};
                }}
            """)
        
    def create_drop_zone(self):
        """Create the drag-and-drop zone"""
        drop_frame = QFrame()
        drop_frame.setFixedHeight(150)
        drop_frame.setFrameStyle(QFrame.Box)
        drop_frame.setLineWidth(2)
        drop_frame.setAcceptDrops(True)
        
        # Use theme-aware colors for drop zone
        theme = self.get_current_theme()
        drop_frame.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {theme['border']};
                border-radius: 10px;
                background-color: {theme['surface_container']};
            }}
            QFrame:hover {{
                border-color: {theme['primary']};
                background-color: {theme['hover_overlay']};
            }}
        """)
        
        # Add content to drop zone
        layout = QVBoxLayout()
        
        # Icon/Emoji (using text for simplicity)
        icon_label = QLabel("📁")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; border: none; background: transparent;")
        layout.addWidget(icon_label)
        
        # Instruction text
        instruction_label = QLabel("Drag and drop CSV file here")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setStyleSheet(f"font-size: 14px; color: {theme['text_primary']}; border: none; background: transparent;")
        layout.addWidget(instruction_label)
        
        # Supported formats
        format_label = QLabel("Supported: .csv files with email and firstname columns (lastname optional)")
        format_label.setAlignment(Qt.AlignCenter)
        format_label.setStyleSheet(f"font-size: {FONT_SIZE_SMALL}; color: {theme['text_tertiary']}; border: none; background: transparent;")
        layout.addWidget(format_label)
        
        drop_frame.setLayout(layout)
        
        # Enable drag-and-drop events
        drop_frame.dragEnterEvent = self.drag_enter_event
        drop_frame.dragMoveEvent = self.drag_move_event
        drop_frame.dropEvent = self.drop_event
        
        return drop_frame
        
    def browse_file(self):
        """Open file browser dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV Contact File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.process_file(file_path)
            
    def drag_enter_event(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            # Check if it's a single file with .csv extension
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].toString().lower().endswith('.csv'):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()
            
    def drag_move_event(self, event):
        """Handle drag move event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def drop_event(self, event: QDropEvent):
        """Handle drop event"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1:
                file_path = urls[0].toLocalFile()
                self.process_file(file_path)
                event.acceptProposedAction()
            else:
                self.show_validation_error("Please drop only one file at a time.")
                event.ignore()
        else:
            event.ignore()
            
    def process_file(self, file_path):
        """Process the selected file"""
        try:
            # Basic file checks
            if not os.path.exists(file_path):
                self.show_validation_error("File does not exist.")
                return
                
            if not file_path.lower().endswith('.csv'):
                self.show_validation_error("Please select a CSV file.")
                return
                
            # Validate CSV structure
            if self.validate_csv_file(file_path):
                self.selected_file_path = file_path
                self.show_file_selected(file_path)
                self.file_selected.emit(file_path)
            
        except Exception as e:
            self.show_validation_error(f"Error processing file: {str(e)}")
            
    def validate_csv_file(self, file_path):
        """Validate CSV file structure"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                # Check if file is empty
                if os.path.getsize(file_path) == 0:
                    self.show_validation_error("The CSV file is empty.")
                    return False
                
                # Read first few lines to check structure
                reader = csv.reader(file)
                headers = next(reader, None)
                
                if not headers:
                    self.show_validation_error("The CSV file has no headers.")
                    return False
                
                # Check for required columns (case-insensitive)
                headers_lower = [h.lower().strip() for h in headers]
                required_columns = ['email', 'firstname']
                missing_columns = []
                
                for col in required_columns:
                    if col not in headers_lower:
                        missing_columns.append(col)
                
                if missing_columns:
                    self.show_validation_error(
                        f"Missing required columns: {', '.join(missing_columns)}. "
                        f"Found columns: {', '.join(headers)}"
                    )
                    return False
                
                # Check if there's at least one data row
                try:
                    first_row = next(reader, None)
                    if not first_row:
                        self.show_validation_error("The CSV file has no data rows.")
                        return False
                except:
                    pass  # It's okay if we can't read the first row
                
                # If we get here, basic structure is valid
                # Now get actual valid contact count using CSV handler
                try:
                    from core.csv_handler import CSVHandler
                    csv_handler = CSVHandler()
                    result = csv_handler.process_csv_file(file_path)
                    
                    if result and result.get('success', False):
                        valid_contacts = len(result.get('contacts', []))
                        total_rows = result.get('total_rows', 0)
                        
                        if valid_contacts == total_rows:
                            self.show_validation_success(f"Valid CSV file with {valid_contacts} contacts found.")
                        else:
                            # Some contacts were skipped
                            skipped = total_rows - valid_contacts
                            self.show_validation_success(f"Valid CSV file with {valid_contacts} valid contacts found ({skipped} skipped due to missing emails or first names).")
                    else:
                        # Fallback to basic row count if CSV processing fails
                        file.seek(0)  # Reset file pointer
                        row_count = sum(1 for _ in reader) - 1  # Subtract header row
                        self.show_validation_success(f"Valid CSV file with ~{row_count} contacts found.")
                        
                except Exception as csv_error:
                    # Fallback to basic validation if CSV handler fails
                    file.seek(0)  # Reset file pointer
                    row_count = sum(1 for _ in reader) - 1  # Subtract header row
                    self.show_validation_success(f"Valid CSV file with ~{row_count} contacts found.")
                
                return True
                
        except UnicodeDecodeError:
            self.show_validation_error("Unable to read file. Please ensure it's a valid CSV file with UTF-8 encoding.")
            return False
        except Exception as e:
            self.show_validation_error(f"Error validating CSV file: {str(e)}")
            return False
            
    def show_file_selected(self, file_path):
        """Update UI to show selected file"""
        filename = os.path.basename(file_path)
        self.file_info_label.setText(f"Selected: {filename}")
        
        # Use theme-aware colors for selected file display
        theme = self.get_current_theme()
        self.file_info_label.setStyleSheet(f"""
            QLabel {{
                color: {theme['text_primary']};
                font-weight: bold;
            }}
        """)
        
        # Update drop zone style to indicate success
        self.drop_zone.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {theme['success']};
                border-radius: 10px;
                background-color: {theme['surface_container']};
            }}
        """)
        
    def show_validation_success(self, message):
        """Show validation success message"""
        self.feedback_label.setText(f"✅ {message}")
        
        # Use theme-aware colors for success display
        theme = self.get_current_theme()
        self.feedback_label.setStyleSheet(f"""
            QLabel {{
                color: {theme['success']};
                font-weight: bold;
            }}
        """)
        
    def show_validation_error(self, message):
        """Show validation error message"""
        self.feedback_label.setText(f"❌ {message}")
        
        # Use theme-aware colors for error display
        theme = self.get_current_theme()
        self.feedback_label.setStyleSheet(f"""
            QLabel {{
                color: {theme['error']};
                font-weight: bold;
            }}
        """)
        
        self.validation_error.emit(message)
        
        # Reset drop zone style
        self.drop_zone.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {theme['error']};
                border-radius: 10px;
                background-color: {theme['surface_container']};
            }}
        """)
        
    def clear_selection(self):
        """Clear the current file selection"""
        self.selected_file_path = None
        self.file_info_label.setText("No file selected")
        
        # Use theme-aware colors for cleared state
        theme = self.get_current_theme()
        self.file_info_label.setStyleSheet(f"""
            QLabel {{
                color: {theme['text_placeholder']};
                font-style: italic;
            }}
        """)
        
        self.feedback_label.setText("")
        
        # Reset drop zone to default style
        self.drop_zone.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {theme['border']};
                border-radius: 10px;
                background-color: {theme['surface_container']};
            }}
            QFrame:hover {{
                border-color: {theme['primary']};
                background-color: {theme['hover_overlay']};
            }}
        """)
        
    def get_selected_file(self):
        """Get the currently selected file path"""
        return self.selected_file_path
        
    def set_enabled(self, enabled):
        """Enable or disable the widget"""
        super().setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.drop_zone.setAcceptDrops(enabled)


# Example usage and testing
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = FileUploadWidget()
    widget.setWindowTitle("File Upload Widget Test")
    widget.resize(400, 300)
    
    # Connect signals for testing
    widget.file_selected.connect(lambda path: print(f"File selected: {path}"))
    widget.validation_error.connect(lambda error: print(f"Validation error: {error}"))
    
    widget.show()
    sys.exit(app.exec_())
