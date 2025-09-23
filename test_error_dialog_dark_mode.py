#!/usr/bin/env python3
"""
Test script to verify error dialogs are visible in dark mode
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.error_dialogs import ThemedMessageBox, ErrorDialogManager
from core.theme_manager import ThemeManager

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dark Mode Error Dialog Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.theme_manager.set_auto_detect(True)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Add buttons to test different error types
        critical_btn = QPushButton("Test Critical Error Dialog")
        critical_btn.clicked.connect(self.test_critical_error)
        layout.addWidget(critical_btn)
        
        warning_btn = QPushButton("Test Warning Dialog")
        warning_btn.clicked.connect(self.test_warning)
        layout.addWidget(warning_btn)
        
        info_btn = QPushButton("Test Information Dialog")
        info_btn.clicked.connect(self.test_information)
        layout.addWidget(info_btn)
        
        question_btn = QPushButton("Test Question Dialog")
        question_btn.clicked.connect(self.test_question)
        layout.addWidget(question_btn)
        
        print(f"Current theme: {self.theme_manager.get_current_theme_name()}")
        
    def test_critical_error(self):
        """Test critical error dialog in current theme"""
        ThemedMessageBox.critical(
            self,
            "Critical Error Test",
            "This is a test critical error dialog.\n\n"
            "Can you see this text clearly in dark mode?\n"
            "The dialog should have proper contrast and be readable."
        )
        
    def test_warning(self):
        """Test warning dialog in current theme"""
        ThemedMessageBox.warning(
            self,
            "Warning Test",
            "This is a test warning dialog.\n\n"
            "The text should be clearly visible with proper theming."
        )
        
    def test_information(self):
        """Test information dialog in current theme"""
        ThemedMessageBox.information(
            self,
            "Information Test",
            "This is a test information dialog.\n\n"
            "All text should be properly themed and readable."
        )
        
    def test_question(self):
        """Test question dialog in current theme"""
        from PyQt5.QtWidgets import QMessageBox
        result = ThemedMessageBox.question(
            self,
            "Question Test",
            "This is a test question dialog.\n\n"
            "Can you see the buttons and text clearly?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if result == QMessageBox.Yes:
            ThemedMessageBox.information(self, "Result", "You clicked Yes!")
        else:
            ThemedMessageBox.information(self, "Result", "You clicked No!")

def main():
    app = QApplication(sys.argv)
    
    # Force high DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    window = TestWindow()
    window.show()
    
    print("Test window opened. Click the buttons to test error dialogs in dark mode.")
    print("All dialogs should be clearly visible with proper contrast.")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()