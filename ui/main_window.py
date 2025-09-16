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

# Import screens
from ui.screens.upload_screen import UploadScreen
from ui.screens.compose_screen import ComposeScreen  
from ui.screens.preview_screen import PreviewScreen
from ui.screens.progress_screen import ProgressScreen
from ui.screens.complete_screen import CompleteScreen

# Import styles
from ui.styles.stylesheet import (
    BUTTON_STYLE, SUCCESS_BUTTON_STYLE, ERROR_BUTTON_STYLE,
    INPUT_STYLE, CARD_STYLE, TITLE_STYLE, SUBTITLE_STYLE,
    PRIMARY_BLUE, SUCCESS_GREEN, ERROR_RED, LIGHT_GREY, BORDER_GREY,
    WARNING_ORANGE, DARK_GREY
)


class MainWindow(QMainWindow):
    """
    Main application window with navigation between screens
    Task 20: Provides screen switching, window management, and menu bar
    """
    
    # Window management signals
    window_closing = pyqtSignal()
    screen_changed = pyqtSignal(str)  # Screen name
    
    # Screen indices for navigation
    SCREEN_UPLOAD = 0
    SCREEN_COMPOSE = 1
    SCREEN_PREVIEW = 2
    SCREEN_PROGRESS = 3
    SCREEN_COMPLETE = 4
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Window state
        self.current_screen_index = 0
        self.campaign_data = {}
        self.navigation_history = []
        
        # Set up the main window
        self.setup_window_properties()
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.connect_signals()
        
        # Start with upload screen
        self.show_upload_screen()
        
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
            
        # Apply application style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {LIGHT_GREY};
                color: {DARK_GREY};
                font-family: Arial, Helvetica, sans-serif;
            }}
            QMenuBar {{
                background-color: white;
                border-bottom: 1px solid {BORDER_GREY};
                padding: 4px;
            }}
            QMenuBar::item {{
                padding: 8px 12px;
                background-color: transparent;
            }}
            QMenuBar::item:selected {{
                background-color: {PRIMARY_BLUE};
                color: white;
            }}
            QStatusBar {{
                background-color: white;
                border-top: 1px solid {BORDER_GREY};
                color: {DARK_GREY};
            }}
        """)
        
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
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-bottom: 1px solid {BORDER_GREY};
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        header_frame.setLayout(layout)
        
        # Screen title
        self.screen_title = QLabel("Upload Contacts")
        self.screen_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.screen_title.setStyleSheet(f"color: {DARK_GREY};")
        layout.addWidget(self.screen_title)
        
        layout.addStretch()
        
        # Step indicator
        self.step_indicator = QLabel("Step 1 of 4")
        self.step_indicator.setStyleSheet(f"color: {PRIMARY_BLUE}; font-weight: bold;")
        layout.addWidget(self.step_indicator)
        
        return header_frame
        
    def setup_screens(self):
        """Initialize and add all screens to the stacked widget"""
        try:
            # Screen 1: Upload Contacts
            self.upload_screen = UploadScreen()
            self.stacked_widget.addWidget(self.upload_screen)
            
            # Screen 2: Compose Email  
            self.compose_screen = ComposeScreen()
            self.stacked_widget.addWidget(self.compose_screen)
            
            # Screen 3: Preview Campaign
            self.preview_screen = PreviewScreen()
            self.stacked_widget.addWidget(self.preview_screen)
            
            # Screen 4: Progress Display
            self.progress_screen = ProgressScreen()
            self.stacked_widget.addWidget(self.progress_screen)
            
            # Screen 5: Campaign Complete
            self.complete_screen = CompleteScreen()
            self.stacked_widget.addWidget(self.complete_screen)
            
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", 
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
            if hasattr(self.preview_screen, 'back_clicked'):
                self.preview_screen.back_clicked.connect(self.show_compose_screen)
            if hasattr(self.preview_screen, 'send_clicked'):
                self.preview_screen.send_clicked.connect(self.on_preview_send)
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
        if self.current_screen_index != self.SCREEN_UPLOAD:
            reply = QMessageBox.question(
                self, 'New Campaign',
                'Are you sure you want to start a new campaign? Any unsaved progress will be lost.',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.campaign_data.clear()
                self.show_upload_screen()
        else:
            self.show_upload_screen()
    
    def close_application(self):
        """Handle application close request"""
        if self.current_screen_index in [self.SCREEN_PROGRESS]:
            reply = QMessageBox.question(
                self, 'Exit Application',
                'A campaign is currently in progress. Are you sure you want to exit?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
                
        self.window_closing.emit()
        self.close()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
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
            reply = QMessageBox.question(
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
    
    def set_campaign_data(self, data):
        """Set campaign data (useful for testing)"""
        self.campaign_data = data.copy() if data else {}