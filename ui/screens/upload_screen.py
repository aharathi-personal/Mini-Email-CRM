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


class UploadScreen(QWidget):
    """
    First screen of the application for uploading contact CSV files
    """
    
    # Signals
    file_uploaded = pyqtSignal(str)  # Emitted when a valid file is uploaded
    next_screen = pyqtSignal()  # Emitted when user wants to proceed to next screen
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.uploaded_file_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        
        # Header section
        header_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Step 1 of 4: Upload Contact List")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Upload a CSV file containing your contact list with email, firstname, and lastname columns")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 14px; margin-bottom: 20px;")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)
        
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
        self.back_button.setStyleSheet("padding: 10px 20px;")
        nav_layout.addWidget(self.back_button)
        
        # Add spacing
        nav_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Next button
        self.next_button = QPushButton("Next: Review Contacts →")
        self.next_button.setEnabled(False)  # Enabled only when file is uploaded
        self.next_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:enabled:hover {
                background-color: #005f99;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
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
    screen.setWindowTitle("Upload Screen Test")
    screen.resize(600, 500)
    
    # Connect signals for testing
    screen.file_uploaded.connect(lambda path: print(f"File uploaded: {path}"))
    screen.next_screen.connect(lambda: print("Proceeding to next screen"))
    
    screen.show()
    sys.exit(app.exec_())
