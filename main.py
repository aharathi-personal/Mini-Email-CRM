#!/usr/bin/env python3
"""
Mini Email CRM Application
Main entry point for the PyQt5 Email Campaign Management System
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    """Main application entry point"""
    # Set up logging
    logger = setup_logger()
    logger.info("Starting Mini Email CRM Application")
    
    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Mini Email CRM")
    app.setOrganizationName("Mini CRM")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    try:
        window = MainWindow()
        window.show()
        logger.info("Main window created and displayed")
        
        # Start the application event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()