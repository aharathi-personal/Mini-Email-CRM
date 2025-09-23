#!/usr/bin/env python3
"""
Mini Email CRM Application
Main entry point for the PyQt5 Email Campaign Management System
Task 21: Enhanced Application Entry Point with comprehensive initialization,
exception handling, and application properties.
"""

import sys
import os
import traceback
import signal
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QStandardPaths
from PyQt5.QtGui import QPixmap, QFont, QPalette, QIcon
from ui.error_dialogs import ThemedMessageBox, ErrorDialogManager, apply_global_messagebox_theme

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import application components
from ui.main_window import MainWindow
from utils.logger import setup_logger


class MiniEmailCRMApplication:
    """
    Main application class for Mini Email CRM
    Task 21: Encapsulates application initialization, configuration, and lifecycle management
    """
    
    def __init__(self):
        """Initialize the application wrapper"""
        self.app = None
        self.main_window = None
        self.logger = None
        self.splash_screen = None
        
    def setup_application_properties(self):
        """Configure Qt application properties and metadata"""
        if not self.app:
            return
            
        # Application identification
        self.app.setApplicationName("Mini Email CRM")
        self.app.setApplicationDisplayName("Mini Email CRM - Campaign Manager")
        self.app.setOrganizationName("Mini CRM Solutions")
        self.app.setOrganizationDomain("minicrm.local")
        self.app.setApplicationVersion("1.0.0")
        
        # Application description and additional metadata
        self.app.setProperty("applicationDescription", 
                           "A comprehensive email campaign management system for small to medium businesses")
        self.app.setProperty("applicationCategory", "Office/Business")
        self.app.setProperty("buildDate", "2025-09-15")
        
        # Set application icon if available
        self.setup_application_icon()
        
        # Configure application style and theme
        self.setup_application_style()
        
        self.logger.info("Application properties configured")
        
    def setup_application_icon(self):
        """Set up application icon from resources"""
        try:
            icon_paths = [
                os.path.join(os.path.dirname(__file__), "resources", "icons", "app_icon.png"),
                os.path.join(os.path.dirname(__file__), "resources", "icons", "crm_icon.png"),
                os.path.join(os.path.dirname(__file__), "ui", "resources", "icons", "app_icon.png")
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        self.app.setWindowIcon(icon)
                        self.logger.info(f"Application icon set from: {icon_path}")
                        return
                        
            # Create a simple default icon if no icon file found
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.blue)
            default_icon = QIcon(pixmap)
            self.app.setWindowIcon(default_icon)
            self.logger.info("Default application icon created")
            
        except Exception as e:
            self.logger.warning(f"Could not set application icon: {e}")
    
    def setup_application_style(self):
        """Configure application-wide styling and theme"""
        try:
            # Initialize theme system first
            from core.theme_manager import ThemeManager
            from ui.styles.dynamic_stylesheet import DynamicStylesheetGenerator
            
            theme_manager = ThemeManager.instance()
            stylesheet_generator = DynamicStylesheetGenerator(theme_manager)
            
            # Set application font
            font = QFont("Arial", 10)
            font.setStyleHint(QFont.SansSerif)
            self.app.setFont(font)
            
            # High DPI scaling is now handled in initialize_application()
            
            # Apply dynamic theme-based stylesheet
            dynamic_stylesheet = stylesheet_generator.generate_stylesheet()
            
            # Test if the stylesheet can be parsed by Qt
            from PyQt5.QtWidgets import QWidget
            test_widget = QWidget()
            test_widget.setStyleSheet(dynamic_stylesheet)
            parsed_stylesheet = test_widget.styleSheet()
            
            if parsed_stylesheet and len(parsed_stylesheet.strip()) > 0:
                # Stylesheet parsed successfully
                self.app.setStyleSheet(dynamic_stylesheet)
                self.logger.info(f"Dynamic theme system initialized. Current theme: {theme_manager.get_current_theme_name()}")
            else:
                # Stylesheet parsing failed, use fallback
                self.logger.warning("Dynamic stylesheet parsing failed, using fallback styling")
                self._setup_fallback_style()
            
            # Apply themed error dialogs
            apply_global_messagebox_theme()
            
        except Exception as e:
            self.logger.warning(f"Could not initialize theme system, falling back to basic styling: {e}")
            # Fallback to basic styling if theme system fails
            self._setup_fallback_style()
    
    def _setup_fallback_style(self):
        """Fallback styling if theme system fails"""
        try:
            style_sheet = """
                QApplication {
                    font-family: Arial, Helvetica, sans-serif;
                    font-size: 10pt;
                }
                
                QMainWindow {
                    background-color: #F5F5F5;
                    color: #333333;
                }
                
                QMessageBox {
                    background-color: white;
                    color: #333333;
                }
                
                QMessageBox QPushButton {
                    min-width: 80px;
                    padding: 6px 12px;
                    border: 1px solid #2196F3;
                    border-radius: 4px;
                    background-color: #2196F3;
                    color: white;
                    font-weight: bold;
                }
                
                QMessageBox QPushButton:hover {
                    background-color: #1976D2;
                }
                
                QMessageBox QPushButton:pressed {
                    background-color: #0D47A1;
                }
            """
            
            self.app.setStyleSheet(style_sheet)
            self.logger.info("Fallback styling applied")
            
        except Exception as e:
            self.logger.warning(f"Could not set fallback style: {e}")
            
        except Exception as e:
            self.logger.warning(f"Could not set application style: {e}")
    
    def setup_splash_screen(self):
        """Create and display application splash screen"""
        try:
            # Create splash screen pixmap
            splash_paths = [
                os.path.join(os.path.dirname(__file__), "resources", "images", "splash.png"),
                os.path.join(os.path.dirname(__file__), "ui", "resources", "images", "splash.png")
            ]
            
            splash_pixmap = None
            for splash_path in splash_paths:
                if os.path.exists(splash_path):
                    splash_pixmap = QPixmap(splash_path)
                    break
            
            # Create default splash if no image found
            if not splash_pixmap or splash_pixmap.isNull():
                splash_pixmap = QPixmap(400, 300)
                splash_pixmap.fill(Qt.white)
                
            # Create splash screen
            self.splash_screen = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
            self.splash_screen.setMask(splash_pixmap.mask())
            
            # Show splash screen
            self.splash_screen.show()
            self.splash_screen.showMessage("Loading Mini Email CRM...", 
                                         Qt.AlignBottom | Qt.AlignCenter, Qt.black)
            
            # Process events to ensure splash is visible
            self.app.processEvents()
            
            self.logger.info("Splash screen displayed")
            
        except Exception as e:
            self.logger.warning(f"Could not create splash screen: {e}")
            self.splash_screen = None
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down gracefully...")
            if self.main_window:
                self.main_window.close()
            else:
                self.app.quit()
        
        # Handle SIGINT (Ctrl+C) and SIGTERM
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        self.logger.info("Signal handlers configured")
    
    def create_directories(self):
        """Create necessary application directories"""
        try:
            # Get application data directory
            app_data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            
            # Create directories
            directories = [
                app_data_dir,
                os.path.join(app_data_dir, "logs"),
                os.path.join(app_data_dir, "exports"),
                os.path.join(app_data_dir, "temp"),
                os.path.join(os.path.dirname(__file__), "logs"),
                os.path.join(os.path.dirname(__file__), "exports"),
                os.path.join(os.path.dirname(__file__), "temp")
            ]
            
            for directory in directories:
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                    self.logger.info(f"Created directory: {directory}")
                    
        except Exception as e:
            self.logger.warning(f"Could not create directories: {e}")
    
    def initialize_application(self):
        """Initialize PyQt5 application with comprehensive configuration"""
        try:
            # Set Qt attributes BEFORE creating QApplication
            # These must be set before QApplication instantiation
            from PyQt5.QtCore import Qt
            self.app = QApplication(sys.argv)
            self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            self.app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            
            # Set up logging first
            self.logger = setup_logger()
            self.logger.info("Starting Mini Email CRM Application - Task 21 Implementation")
            
            # Configure application properties
            self.setup_application_properties()
            
            # Create necessary directories
            self.create_directories()
            
            # Set up signal handlers for graceful shutdown
            self.setup_signal_handlers()
            
            # Display splash screen
            self.setup_splash_screen()
            
            self.logger.info("Application initialization completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize application: {str(e)}"
            print(f"CRITICAL ERROR: {error_msg}")
            if self.logger:
                self.logger.critical(error_msg)
            traceback.print_exc()
            return False
    
    def create_main_window(self):
        """Create and configure the main application window"""
        try:
            # Create main window
            self.main_window = MainWindow()
            
            # Configure main window
            self.main_window.setWindowTitle("Mini Email CRM - Campaign Manager")
            
            # Connect window signals for proper cleanup
            self.main_window.window_closing.connect(self.on_window_closing)
            
            self.logger.info("Main window created successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to create main window: {str(e)}"
            self.logger.error(error_msg)
            
            # Show error dialog to user
            ErrorDialogManager.show_error(
                None, 
                "Startup Error",
                "Failed to initialize the main window. Please check the logs for more details and contact support if the issue persists.",
                str(e)
            )
            return False
    
    def show_main_window(self):
        """Display the main window and hide splash screen"""
        try:
            if not self.main_window:
                return False
                
            # Show main window
            self.main_window.show()
            
            # Bring window to front and activate
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            # Hide splash screen after a brief delay
            if self.splash_screen:
                QTimer.singleShot(1500, self.hide_splash_screen)
            
            self.logger.info("Main window displayed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to show main window: {str(e)}"
            self.logger.error(error_msg)
            ThemedMessageBox.critical(None, "Display Error", error_msg)
            return False
    
    def hide_splash_screen(self):
        """Hide the splash screen"""
        if self.splash_screen:
            self.splash_screen.close()
            self.splash_screen = None
            self.logger.info("Splash screen closed")
    
    def on_window_closing(self):
        """Handle main window closing"""
        self.logger.info("Main window closing")
        
        # Perform cleanup
        self.cleanup()
        
        # Quit application
        self.app.quit()
    
    def cleanup(self):
        """Perform application cleanup"""
        try:
            # Clean up temporary files
            temp_dir = os.path.join(os.path.dirname(__file__), "temp")
            if os.path.exists(temp_dir):
                import shutil
                for file in os.listdir(temp_dir):
                    try:
                        file_path = os.path.join(temp_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except:
                        pass  # Ignore cleanup errors
            
            if self.logger:
                self.logger.info("Application cleanup completed")
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Cleanup error: {e}")
            # If logger is None, just ignore the error silently
    
    def run(self):
        """Run the application main loop"""
        try:
            # Initialize application
            if not self.initialize_application():
                return 1
            
            # Create main window
            if not self.create_main_window():
                return 1
            
            # Show main window
            if not self.show_main_window():
                return 1
            
            # Start the application event loop
            self.logger.info("Starting application event loop")
            return self.app.exec_()
            
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            return 0
            
        except Exception as e:
            error_msg = f"Unhandled application error: {str(e)}"
            self.logger.critical(error_msg)
            print(f"CRITICAL ERROR: {error_msg}")
            traceback.print_exc()
            
            # Show error dialog if app is available
            if self.app:
                ThemedMessageBox.critical(
                    None, 
                    "Critical Error",
                    f"A critical error occurred:\n\n{str(e)}\n\n"
                    f"The application will now exit. Please check the logs for more details."
                )
            
            return 1
        
        finally:
            # Ensure cleanup happens
            self.cleanup()


def main():
    """
    Main application entry point
    Task 21: Enhanced main function with comprehensive error handling and logging
    """
    try:
        # Set Qt attributes BEFORE creating QApplication
        # This must be done before QApplication is instantiated
        from PyQt5.QtCore import Qt
        import os
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
        
        # Create and run application
        app_instance = MiniEmailCRMApplication()
        exit_code = app_instance.run()
        
        # Exit with appropriate code
        sys.exit(exit_code)
        
    except Exception as e:
        # Last resort error handling
        print(f"FATAL ERROR: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()