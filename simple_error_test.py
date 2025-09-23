#!/usr/bin/env python3
"""
Simple Error Dialog Test - Test dark mode error visibility
This will create simple error scenarios to test dialog visibility
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.theme_manager import ThemeManager
from ui.error_dialogs import ThemedMessageBox

def test_error_dialogs():
    """Simple test of themed error dialogs"""
    app = QApplication(sys.argv)
    
    # Set dark mode
    theme_manager = ThemeManager()
    theme_manager.set_auto_detect(False)
    theme_manager.set_theme('dark')
    
    # Create a simple test window
    window = QWidget()
    window.setWindowTitle("Error Dialog Test")
    window.setGeometry(100, 100, 300, 200)
    
    # Apply dark theme to window
    colors = theme_manager.get_theme()
    window.setStyleSheet(f"""
        QWidget {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
        }}
    """)
    
    window.show()
    
    # Test critical error - this should be clearly visible in dark mode
    ThemedMessageBox.critical(
        window,
        "Dark Mode Test",
        "This is a critical error dialog in dark mode.\n\n"
        "Can you see this text clearly?\n"
        "The background should be dark and text should be light."
    )
    
    # Test warning
    ThemedMessageBox.warning(
        window,
        "Dark Mode Warning",
        "This is a warning dialog in dark mode.\n\n"
        "Can you see this text clearly?\n"
        "The background should be dark and text should be light."
    )
    
    # Test information
    ThemedMessageBox.information(
        window,
        "Dark Mode Info",
        "This is an information dialog in dark mode.\n\n"
        "Can you see this text clearly?\n"
        "The background should be dark and text should be light."
    )
    
    print("All error dialogs have been shown.")
    print("If you could see them clearly in dark mode, the fix is working!")
    
    app.exec_()

if __name__ == '__main__':
    test_error_dialogs()