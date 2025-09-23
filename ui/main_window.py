"""
Main Window for Mini Email CRM
Task 20: Main Window & Navigation Implementation

This module provides the main application window with navigation
between different screens and central application management.
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QStackedWidget, QMenuBar, QAction, QMessageBox,
    QStatusBar, QToolBar, QFrame, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette
from typing import Dict

# Import themed error dialogs
from ui.error_dialogs import ThemedMessageBox, ErrorDialogManager

# Import screens
from ui.screens.login_screen import LoginScreen
from ui.screens.upload_screen import UploadScreen
from ui.screens.compose_screen import ComposeScreen  
from ui.screens.preview_screen import PreviewScreen
from ui.screens.progress_screen import ProgressScreen
from ui.screens.complete_screen import CompleteScreen

# Import styles and theme system
from ui.styles.stylesheet import (
    BUTTON_STYLE, SUCCESS_BUTTON_STYLE, ERROR_BUTTON_STYLE,
    INPUT_STYLE, CARD_STYLE, TITLE_STYLE, SUBTITLE_STYLE,
    PRIMARY_BLUE, SUCCESS_GREEN, ERROR_RED, LIGHT_GREY, BORDER_GREY,
    WARNING_ORANGE, DARK_GREY
)

# Import theme system
from core.theme_manager import ThemeManager
from ui.styles.dynamic_stylesheet import DynamicStylesheetGenerator


class MainWindow(QMainWindow):
    """
    Main application window with navigation between screens
    Task 20: Provides screen switching, window management, and menu bar
    """
    
    # Window management signals
    window_closing = pyqtSignal()
    screen_changed = pyqtSignal(str)  # Screen name
    
    # Screen indices for navigation
    SCREEN_LOGIN = 0
    SCREEN_UPLOAD = 1
    SCREEN_COMPOSE = 2
    SCREEN_PREVIEW = 3
    SCREEN_PROGRESS = 4
    SCREEN_COMPLETE = 5
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize theme system
        self.theme_manager = ThemeManager.instance()
        if self.theme_manager is None:
            # Fallback: create a new instance if singleton failed
            self.theme_manager = ThemeManager()
        self.stylesheet_generator = DynamicStylesheetGenerator(self.theme_manager)
        
        # Window state
        self.current_screen_index = 0
        self.campaign_data = {}
        self.navigation_history = []
        self.smtp_credentials = None  # Store validated SMTP credentials
        
        # Set up the main window
        self.setup_theme_system()
        self.setup_window_properties()
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.connect_signals()
        
        # Start with login screen
        self.show_login_screen()
        
    def setup_theme_system(self):
        """Initialize and configure the theme system"""
        # Connect to theme changes
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Apply initial theme
        self.apply_current_theme()
        
        # Set up system theme monitoring (already handled by ThemeManager)
        print(f"Theme system initialized. Current theme: {self.theme_manager.get_current_theme_name()}")
    
    def on_theme_changed(self, theme_name: str):
        """Handle theme changes from the theme manager"""
        print(f"Theme changed to: {theme_name}")
        self.apply_current_theme()
        
        # Notify all child widgets that support theme changes
        self.propagate_theme_change(theme_name)
    
    def apply_current_theme(self):
        """Apply the current theme to this window"""
        stylesheet = self.stylesheet_generator.generate_stylesheet()
        self.setStyleSheet(stylesheet)
    
    def propagate_theme_change(self, theme_name: str):
        """Propagate theme changes to all child widgets"""
        # Find all widgets that have theme change handlers
        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'on_theme_changed'):
                try:
                    widget.on_theme_changed(theme_name)
                except Exception as e:
                    print(f"Warning: Failed to apply theme to widget {widget}: {e}")
        
        # Update navigation header colors
        self.update_navigation_header_theme()
    
    def update_navigation_header_theme(self):
        """Update navigation header with current theme"""
        theme = self.theme_manager.get_theme()
        
        if hasattr(self, 'navigation_header'):
            self.navigation_header.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme['surface']};
                    border-bottom: 1px solid {theme['border']};
                }}
            """)
        
        if hasattr(self, 'screen_title'):
            self.screen_title.setStyleSheet(f"color: {theme['text_primary']};")
        
        if hasattr(self, 'step_indicator'):
            self.step_indicator.setStyleSheet(f"color: {theme['primary']}; font-weight: bold;")
    
    def toggle_theme(self):
        """Toggle between light and dark themes (for testing/manual switching)"""
        current_theme = self.theme_manager.get_current_theme_name()
        new_theme = "dark" if current_theme == "light" else "light"
        
        # Temporarily disable auto-detection for manual switching
        self.theme_manager.set_auto_detect(False)
        self.theme_manager.set_theme(new_theme)
    
    def enable_auto_theme(self):
        """Re-enable automatic theme detection"""
        self.theme_manager.set_auto_detect(True)
        
    def setup_window_properties(self):
        """Configure main window properties"""
        # Window title and icon
        self.setWindowTitle("Mini Email CRM - Campaign Manager")
        
        # Window size and position
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Center window on screen
        self.center_window()
        
        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        # Theme-based styling is now handled by apply_current_theme()
        # which is called from setup_theme_system()
        
    def center_window(self):
        """Center the window on the screen"""
        if QApplication.desktop():
            screen = QApplication.desktop().screenGeometry()
            window = self.frameGeometry()
            window.moveCenter(screen.center())
            self.move(window.topLeft())
    
    def setup_ui(self):
        """Set up the main UI with stacked widget for screen navigation"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        # Create navigation header (optional)
        self.navigation_header = self.create_navigation_header()
        main_layout.addWidget(self.navigation_header)
        
        # Create stacked widget for screens
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Initialize screens
        self.setup_screens()
        
    def create_navigation_header(self):
        """Create optional navigation header with breadcrumb"""
        header_frame = QFrame()
        header_frame.setFixedHeight(50)
        # Styling will be applied by update_navigation_header_theme()
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        header_frame.setLayout(layout)
        
        # Screen title
        self.screen_title = QLabel("Upload Contacts")
        self.screen_title.setFont(QFont("Arial", 16, QFont.Bold))
        # Styling will be applied by update_navigation_header_theme()
        layout.addWidget(self.screen_title)
        
        layout.addStretch()
        
        # Step indicator
        self.step_indicator = QLabel("Step 1 of 4")
        # Styling will be applied by update_navigation_header_theme()
        layout.addWidget(self.step_indicator)
        
        return header_frame
        
    def setup_screens(self):
        """Initialize and add all screens to the stacked widget"""
        try:
            # Screen 0: Login
            print("Initializing Login Screen...")
            self.login_screen = LoginScreen()
            self.stacked_widget.addWidget(self.login_screen)
            print("✅ Login Screen initialized successfully")
            
            # Screen 1: Upload Contacts
            print("Initializing Upload Screen...")
            self.upload_screen = UploadScreen()
            self.stacked_widget.addWidget(self.upload_screen)
            print("✅ Upload Screen initialized successfully")
            
            # Screen 2: Compose Email  
            print("Initializing Compose Screen...")
            self.compose_screen = ComposeScreen()
            self.stacked_widget.addWidget(self.compose_screen)
            print("✅ Compose Screen initialized successfully")
            
            # Screen 3: Preview Campaign
            print("Initializing Preview Screen...")
            self.preview_screen = PreviewScreen()
            self.stacked_widget.addWidget(self.preview_screen)
            print("✅ Preview Screen initialized successfully")
            
            # Screen 4: Progress Display
            print("Initializing Progress Screen...")
            self.progress_screen = ProgressScreen()
            self.stacked_widget.addWidget(self.progress_screen)
            print("✅ Progress Screen initialized successfully")
            
            # Screen 5: Campaign Complete
            print("Initializing Complete Screen...")
            self.complete_screen = CompleteScreen()
            self.stacked_widget.addWidget(self.complete_screen)
            print("✅ Complete Screen initialized successfully")
            
        except Exception as e:
            print(f"❌ Error during screen initialization: {str(e)}")
            import traceback
            traceback.print_exc()
            ThemedMessageBox.critical(self, "Initialization Error", 
                               f"Failed to initialize screens: {str(e)}")
    
    def setup_menu_bar(self):
        """Set up the application menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('&File')
        
        new_campaign_action = QAction('&New Campaign', self)
        new_campaign_action.setShortcut('Ctrl+N')
        new_campaign_action.setStatusTip('Start a new email campaign')
        new_campaign_action.triggered.connect(self.new_campaign)
        file_menu.addAction(new_campaign_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close_application)
        file_menu.addAction(exit_action)
        
        # Navigation Menu
        nav_menu = menubar.addMenu('&Navigation')
        
        login_action = QAction('&Login', self)
        login_action.setShortcut('Ctrl+0')
        login_action.triggered.connect(self.show_login_screen)
        nav_menu.addAction(login_action)
        
        nav_menu.addSeparator()
        
        upload_action = QAction('&Upload Contacts', self)
        upload_action.setShortcut('Ctrl+1')
        upload_action.triggered.connect(self.show_upload_screen)
        nav_menu.addAction(upload_action)
        
        compose_action = QAction('&Compose Email', self)
        compose_action.setShortcut('Ctrl+2')
        compose_action.triggered.connect(self.show_compose_screen)
        nav_menu.addAction(compose_action)
        
        preview_action = QAction('&Preview Campaign', self)
        preview_action.setShortcut('Ctrl+3')
        preview_action.triggered.connect(self.show_preview_screen)
        nav_menu.addAction(preview_action)
        
        progress_action = QAction('P&rogress', self)
        progress_action.setShortcut('Ctrl+4')
        progress_action.triggered.connect(self.show_progress_screen)
        nav_menu.addAction(progress_action)
        
        complete_action = QAction('&Complete', self)
        complete_action.setShortcut('Ctrl+5')
        complete_action.triggered.connect(self.show_complete_screen)
        nav_menu.addAction(complete_action)
        
        # Help Menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Theme Menu (for manual theme control)
        theme_menu = menubar.addMenu('&Theme')
        
        auto_theme_action = QAction('&Auto (Follow System)', self)
        auto_theme_action.setCheckable(True)
        auto_theme_action.setChecked(self.theme_manager.get_auto_detect())
        auto_theme_action.triggered.connect(self.set_auto_theme)
        theme_menu.addAction(auto_theme_action)
        
        theme_menu.addSeparator()
        
        light_theme_action = QAction('&Light Theme', self)
        light_theme_action.triggered.connect(lambda: self.set_manual_theme('light'))
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction('&Dark Theme', self)
        dark_theme_action.triggered.connect(lambda: self.set_manual_theme('dark'))
        theme_menu.addAction(dark_theme_action)
        
        # Store theme actions for updating
        self.auto_theme_action = auto_theme_action
        
    def setup_status_bar(self):
        """Set up the status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Upload contacts to begin")
        
        # Add permanent widgets to status bar
        self.screen_status = QLabel("Screen: Upload")
        self.status_bar.addPermanentWidget(self.screen_status)
        
    def connect_signals(self):
        """Connect signals from all screens"""
        try:
            # Login Screen signals
            if hasattr(self.login_screen, 'login_successful'):
                self.login_screen.login_successful.connect(self.on_login_success)
            if hasattr(self.login_screen, 'exit_requested'):
                self.login_screen.exit_requested.connect(self.close_application)
                
            # Upload Screen signals
            if hasattr(self.upload_screen, 'next_screen'):
                self.upload_screen.next_screen.connect(self.on_upload_next)
            if hasattr(self.upload_screen, 'exit_clicked'):
                self.upload_screen.exit_clicked.connect(self.close_application)
                
            # Compose Screen signals
            if hasattr(self.compose_screen, 'back_clicked'):
                self.compose_screen.back_clicked.connect(self.show_upload_screen)
            if hasattr(self.compose_screen, 'preview_clicked'):
                self.compose_screen.preview_clicked.connect(self.on_compose_preview)
            if hasattr(self.compose_screen, 'exit_clicked'):
                self.compose_screen.exit_clicked.connect(self.close_application)
                
            # Preview Screen signals
            if hasattr(self.preview_screen, 'previous_clicked'):
                self.preview_screen.previous_clicked.connect(self.show_compose_screen)
            if hasattr(self.preview_screen, 'send_all_clicked'):
                self.preview_screen.send_all_clicked.connect(self.on_preview_send)
            if hasattr(self.preview_screen, 'exit_clicked'):
                self.preview_screen.exit_clicked.connect(self.close_application)
                
            # Progress Screen signals
            if hasattr(self.progress_screen, 'campaign_completed'):
                self.progress_screen.campaign_completed.connect(self.on_campaign_completed)
            if hasattr(self.progress_screen, 'exit_clicked'):
                self.progress_screen.exit_clicked.connect(self.close_application)
                
            # Complete Screen signals
            if hasattr(self.complete_screen, 'new_campaign_clicked'):
                self.complete_screen.new_campaign_clicked.connect(self.new_campaign)
            if hasattr(self.complete_screen, 'exit_clicked'):
                self.complete_screen.exit_clicked.connect(self.close_application)
                
        except Exception as e:
            print(f"Warning: Some signals could not be connected: {e}")
    
    # Navigation Methods
    def show_login_screen(self):
        """Navigate to login screen"""
        self.current_screen_index = self.SCREEN_LOGIN
        self.stacked_widget.setCurrentIndex(self.current_screen_index)
        self.update_navigation_display("SMTP Login", "Login")
        self.status_bar.showMessage("Enter your SMTP credentials to continue")
        self.screen_changed.emit("login")
        
    def show_upload_screen(self):
        """Navigate to upload screen"""
        self.current_screen_index = self.SCREEN_UPLOAD
        self.stacked_widget.setCurrentIndex(self.current_screen_index)
        self.update_navigation_display("Upload Contacts", "Step 1 of 4")
        self.status_bar.showMessage("Upload contacts to begin campaign")
        self.screen_changed.emit("upload")
        
    def show_compose_screen(self):
        """Navigate to compose screen"""
        self.current_screen_index = self.SCREEN_COMPOSE
        self.stacked_widget.setCurrentIndex(self.current_screen_index)
        self.update_navigation_display("Compose Email", "Step 2 of 4")
        self.status_bar.showMessage("Compose your email campaign")
        self.screen_changed.emit("compose")
        
    def show_preview_screen(self):
        """Navigate to preview screen"""
        self.current_screen_index = self.SCREEN_PREVIEW
        self.stacked_widget.setCurrentIndex(self.current_screen_index)
        self.update_navigation_display("Preview Campaign", "Step 3 of 4")
        self.status_bar.showMessage("Review campaign before sending")
        self.screen_changed.emit("preview")
        
    def show_progress_screen(self):
        """Navigate to progress screen"""
        self.current_screen_index = self.SCREEN_PROGRESS
        self.stacked_widget.setCurrentIndex(self.current_screen_index)
        self.update_navigation_display("Sending Progress", "Step 4 of 4")
        self.status_bar.showMessage("Campaign in progress...")
        self.screen_changed.emit("progress")
        
    def show_complete_screen(self):
        """Navigate to complete screen"""
        self.current_screen_index = self.SCREEN_COMPLETE
        self.stacked_widget.setCurrentIndex(self.current_screen_index)
        self.update_navigation_display("Campaign Complete", "Complete")
        self.status_bar.showMessage("Campaign completed")
        self.screen_changed.emit("complete")
        
    def update_navigation_display(self, title, step):
        """Update the navigation header display"""
        if hasattr(self, 'screen_title'):
            self.screen_title.setText(title)
        if hasattr(self, 'step_indicator'):
            self.step_indicator.setText(step)
        if hasattr(self, 'screen_status'):
            self.screen_status.setText(f"Screen: {title}")
    
    # Screen transition handlers
    def on_login_success(self, credentials: dict):
        """Handle successful login with validated credentials"""
        self.smtp_credentials = credentials
        
        # Store credentials in campaign data for use by other screens
        self.campaign_data['smtp_credentials'] = credentials
        
        # Update config settings with validated credentials for the session
        try:
            from config.settings import SMTP_SETTINGS
            SMTP_SETTINGS.update(credentials)
        except Exception as e:
            print(f"Warning: Could not update SMTP settings: {e}")
        
        # Proceed to upload screen
        self.show_upload_screen()
        
    def on_upload_next(self):
        """Handle transition from upload to compose screen"""
        # Get upload data from the upload screen
        upload_data = {}
        if hasattr(self.upload_screen, 'get_uploaded_file'):
            file_path = self.upload_screen.get_uploaded_file()
            if file_path:
                upload_data['uploaded_file'] = file_path
                upload_data['file_path'] = file_path
                
                # Try to get contact count from CSV
                try:
                    import csv
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        reader = csv.reader(file)
                        next(reader)  # Skip header
                        contact_count = sum(1 for _ in reader)
                        upload_data['contact_count'] = contact_count
                except:
                    upload_data['contact_count'] = 0
        
        self.campaign_data.update(upload_data)
        
        # Pass contact data to compose screen
        if hasattr(self.compose_screen, 'set_contact_data'):
            self.compose_screen.set_contact_data(upload_data)
            
        # Refresh SMTP settings in compose screen
        if hasattr(self.compose_screen, 'refresh_smtp_settings'):
            self.compose_screen.refresh_smtp_settings()
            
        self.show_compose_screen()
        
    def on_compose_preview(self, email_data):
        """Handle transition from compose to preview screen"""
        self.campaign_data.update(email_data)
        
        # Pass campaign data to preview screen
        if hasattr(self.preview_screen, 'set_campaign_data'):
            self.preview_screen.set_campaign_data(self.campaign_data)
            
        self.show_preview_screen()
        
    def on_preview_send(self, final_data):
        """Handle transition from preview to progress screen"""
        self.campaign_data.update(final_data)
        
        # Start the campaign in progress screen
        if hasattr(self.progress_screen, 'start_campaign'):
            self.progress_screen.start_campaign(self.campaign_data)
            
        self.show_progress_screen()
        
    def on_campaign_completed(self, completion_data):
        """Handle campaign completion"""
        self.campaign_data.update(completion_data)
        
        # Pass completion data to complete screen
        if hasattr(self.complete_screen, 'set_completion_data'):
            self.complete_screen.set_completion_data(completion_data)
            
        self.show_complete_screen()
    
    # Application management
    def new_campaign(self):
        """Start a new campaign"""
        if self.current_screen_index != self.SCREEN_LOGIN:
            reply = ThemedMessageBox.question(
                self, 'New Campaign',
                'Are you sure you want to start a new campaign? Any unsaved progress will be lost.',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.campaign_data.clear()
                self.smtp_credentials = None
                self.show_login_screen()
        else:
            self.show_login_screen()
    
    def close_application(self):
        """Handle application close request"""
        if self.current_screen_index in [self.SCREEN_PROGRESS]:
            reply = ThemedMessageBox.question(
                self, 'Exit Application',
                'A campaign is currently in progress. Are you sure you want to exit?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
                
        self.window_closing.emit()
        self.close()
    
    def set_auto_theme(self):
        """Enable automatic theme detection"""
        self.theme_manager.set_auto_detect(True)
        self.auto_theme_action.setChecked(True)
        print("Auto theme detection enabled")
    
    def set_manual_theme(self, theme_name: str):
        """Set manual theme and disable auto-detection"""
        self.theme_manager.set_auto_detect(False)
        self.theme_manager.set_theme(theme_name)
        self.auto_theme_action.setChecked(False)
        print(f"Manual theme set to: {theme_name}")
    
    def show_about(self):
        """Show about dialog"""
        ThemedMessageBox.information(
            self, 'About Mini Email CRM',
            '<h3>Mini Email CRM</h3>'
            '<p>Version 1.0.0</p>'
            '<p>A simple yet powerful email campaign management system.</p>'
            '<p>Built with PyQt5 and designed for small to medium businesses.</p>'
            '<p><b>Features:</b></p>'
            '<ul>'
            '<li>Contact list management</li>'
            '<li>Email template editing</li>'
            '<li>Campaign preview and validation</li>'
            '<li>Real-time sending progress</li>'
            '<li>Comprehensive completion statistics</li>'
            '</ul>'
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.current_screen_index == self.SCREEN_PROGRESS:
            reply = ThemedMessageBox.question(
                self, 'Exit Application',
                'A campaign is currently in progress. Are you sure you want to exit?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
                
        self.window_closing.emit()
        event.accept()
    
    # Utility methods
    def get_current_screen_name(self):
        """Get the name of the current screen"""
        screen_names = {
            self.SCREEN_LOGIN: "login",
            self.SCREEN_UPLOAD: "upload",
            self.SCREEN_COMPOSE: "compose", 
            self.SCREEN_PREVIEW: "preview",
            self.SCREEN_PROGRESS: "progress",
            self.SCREEN_COMPLETE: "complete"
        }
        return screen_names.get(self.current_screen_index, "unknown")
    
    def get_campaign_data(self):
        """Get the current campaign data"""
        return self.campaign_data.copy()
    
    def get_smtp_credentials(self) -> Dict[str, str]:
        """Get the validated SMTP credentials"""
        return self.smtp_credentials or {}
    
    def set_campaign_data(self, data):
        """Set campaign data (useful for testing)"""
        self.campaign_data = data.copy() if data else {}