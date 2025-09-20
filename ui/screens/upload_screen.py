"""
Upload Screen for Mini Email CRM
Screen 1 of the application - handles CSV file upload and validation
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ui.widgets.file_upload import FileUploadWidget

# Import new theme system
from ui.base.themed_widgets import ThemedWidget, apply_button_style

# Import legacy styles for backward compatibility during transition
from ui.styles.stylesheet import (
    TITLE_STYLE, SUBTITLE_STYLE, BUTTON_STYLE, SUCCESS_BUTTON_STYLE
)


class UploadScreen(ThemedWidget):
    """
    First screen of the application for uploading contact CSV files
    Now inherits from ThemedWidget for automatic theme support
    """
    
    # Signals
    file_uploaded = pyqtSignal(str)  # Emitted when a valid file is uploaded
    next_screen = pyqtSignal()  # Emitted when user wants to proceed to next screen
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.uploaded_file_path = None
        self.setup_ui()
    
    def apply_theme_customizations(self):
        """Apply custom theme-specific changes beyond stylesheets"""
        # Update button styles using the theme system
        if hasattr(self, 'back_button'):
            apply_button_style(self.back_button, "primary")
        
        if hasattr(self, 'next_button'):
            apply_button_style(self.next_button, "success")
        
        # Update title and subtitle with theme colors
        theme = self.get_current_theme()
        
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    font-family: Arial, Helvetica, sans-serif;
                    font-size: 18px;
                    font-weight: bold;
                    color: {theme['text_primary']};
                }}
            """)
        
        if hasattr(self, 'subtitle_label'):
            self.subtitle_label.setStyleSheet(f"""
                QLabel {{
                    font-family: Arial, Helvetica, sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    color: {theme['text_secondary']};
                }}
            """)
        
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        
        # Header section
        header_layout = QVBoxLayout()
        
        # Title
        self.title_label = QLabel("Step 1 of 4: Upload Contact List")
        # Theme styling will be applied by apply_theme_customizations()
        self.title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.title_label)
        
        # Subtitle
        self.subtitle_label = QLabel("Upload a CSV file containing your contact list with email, firstname, and lastname columns")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        # Theme styling will be applied by apply_theme_customizations()
        self.subtitle_label.setWordWrap(True)
        header_layout.addWidget(self.subtitle_label)
        
        layout.addLayout(header_layout)
        
        # Add spacing
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # File upload widget
        self.file_upload_widget = FileUploadWidget()
        self.file_upload_widget.file_selected.connect(self.on_file_selected)
        self.file_upload_widget.validation_error.connect(self.on_validation_error)
        layout.addWidget(self.file_upload_widget)
        
        # Add spacing
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        # Back button (for future use)
        self.back_button = QPushButton("← Back")
        self.back_button.setEnabled(False)  # Not used in first screen
        # Theme styling will be applied by apply_theme_customizations()
        nav_layout.addWidget(self.back_button)
        
        # Add spacing
        nav_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Next button
        self.next_button = QPushButton("Next: Review Contacts →")
        self.next_button.setEnabled(False)  # Enabled only when file is uploaded
        # Theme styling will be applied by apply_theme_customizations()
        self.next_button.clicked.connect(self.on_next_clicked)
        nav_layout.addWidget(self.next_button)
        
        layout.addLayout(nav_layout)
        
        self.setLayout(layout)
        
    def on_file_selected(self, file_path):
        """Handle file selection"""
        self.uploaded_file_path = file_path
        self.next_button.setEnabled(True)
        self.file_uploaded.emit(file_path)
        
        # Update next button text with contact count
        try:
            import csv
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                contact_count = sum(1 for _ in reader)
                self.next_button.setText(f"Next: Review {contact_count} Contacts →")
        except:
            self.next_button.setText("Next: Review Contacts →")
            
    def on_validation_error(self, error_message):
        """Handle validation errors"""
        self.uploaded_file_path = None
        self.next_button.setEnabled(False)
        self.next_button.setText("Next: Review Contacts →")
        
    def on_next_clicked(self):
        """Handle next button click"""
        if self.uploaded_file_path:
            self.next_screen.emit()
            
    def get_uploaded_file(self):
        """Get the uploaded file path"""
        return self.uploaded_file_path
        
    def clear_upload(self):
        """Clear the current upload"""
        self.uploaded_file_path = None
        self.next_button.setEnabled(False)
        self.next_button.setText("Next: Review Contacts →")
        self.file_upload_widget.clear_selection()
        
    def set_enabled(self, enabled):
        """Enable or disable the screen"""
        super().setEnabled(enabled)
        self.file_upload_widget.set_enabled(enabled)
        self.next_button.setEnabled(enabled and self.uploaded_file_path is not None)


# Example usage and testing
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    screen = UploadScreen()
    screen.setWindowTitle("Step 1 - Upload CSV")
    screen.resize(600, 500)
    
    # Connect signals for testing
    screen.file_uploaded.connect(lambda path: print(f"File uploaded: {path}"))
    screen.next_screen.connect(lambda: print("Proceeding to next screen"))
    
    screen.show()
    sys.exit(app.exec_())
