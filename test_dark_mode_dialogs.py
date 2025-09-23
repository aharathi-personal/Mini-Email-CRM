#!/usr/bin/env python3
"""
Test Dark Mode Error Dialogs
Quick test to verify ThemedMessageBox works correctly in dark mode
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.theme_manager import ThemeManager
from ui.error_dialogs import ThemedMessageBox, ErrorDialogManager

class DarkModeTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dark Mode Dialog Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Force dark mode for testing
        self.theme_manager.set_auto_detect(False)
        self.theme_manager.set_theme('dark')
        
        # Setup UI
        self.setup_ui()
        
        # Apply theme
        self.apply_theme()
        
    def setup_ui(self):
        """Setup the test UI with buttons for different dialog types"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Test buttons
        critical_btn = QPushButton("Test Critical Error")
        critical_btn.clicked.connect(self.test_critical)
        layout.addWidget(critical_btn)
        
        warning_btn = QPushButton("Test Warning")
        warning_btn.clicked.connect(self.test_warning)
        layout.addWidget(warning_btn)
        
        info_btn = QPushButton("Test Information")
        info_btn.clicked.connect(self.test_information)
        layout.addWidget(info_btn)
        
        question_btn = QPushButton("Test Question")
        question_btn.clicked.connect(self.test_question)
        layout.addWidget(question_btn)
        
        error_manager_btn = QPushButton("Test Error Manager")
        error_manager_btn.clicked.connect(self.test_error_manager)
        layout.addWidget(error_manager_btn)
        
    def apply_theme(self):
        """Apply dark theme to main window"""
        colors = self.theme_manager.get_theme()
        style = f"""
            QMainWindow {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
            }}
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: none;
                padding: 10px;
                margin: 5px;
                border-radius: 5px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors['primary_hover']};
            }}
        """
        self.setStyleSheet(style)
        
    def test_critical(self):
        """Test critical error dialog"""
        ThemedMessageBox.critical(
            self,
            "Critical Error Test",
            "This is a test of the critical error dialog in dark mode.\n\n"
            "The text should be clearly visible with proper contrast.\n"
            "Background should be dark, text should be light."
        )
        
    def test_warning(self):
        """Test warning dialog"""
        ThemedMessageBox.warning(
            self,
            "Warning Test",
            "This is a test of the warning dialog in dark mode.\n\n"
            "The text should be clearly visible with proper contrast.\n"
            "Background should be dark, text should be light."
        )
        
    def test_information(self):
        """Test information dialog"""
        ThemedMessageBox.information(
            self,
            "Information Test",
            "This is a test of the information dialog in dark mode.\n\n"
            "The text should be clearly visible with proper contrast.\n"
            "Background should be dark, text should be light."
        )
        
    def test_question(self):
        """Test question dialog"""
        reply = ThemedMessageBox.question(
            self,
            "Question Test",
            "This is a test of the question dialog in dark mode.\n\n"
            "Can you see this text clearly?"
        )
        
        if reply == ThemedMessageBox.Yes:
            ThemedMessageBox.information(self, "Result", "You clicked Yes!")
        else:
            ThemedMessageBox.information(self, "Result", "You clicked No!")
            
    def test_error_manager(self):
        """Test ErrorDialogManager"""
        error_manager = ErrorDialogManager()
        error_manager.show_error(
            "Error Manager Test",
            "This error was shown using ErrorDialogManager.\n"
            "It should also be properly themed for dark mode."
        )

def main():
    app = QApplication(sys.argv)
    
    # Force dark mode detection for testing
    app.setStyle('Fusion')  # Use Fusion style for better dark mode support
    
    window = DarkModeTestWindow()
    window.show()
    
    print("Dark Mode Dialog Test Window Opened")
    print("Click the buttons to test different dialog types")
    print("All dialogs should be clearly visible in dark mode")
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())