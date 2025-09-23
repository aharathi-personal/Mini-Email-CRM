"""
Enhanced Error Dialog System with Dark Mode Support
Provides consistent theming for all error dialogs and message boxes
"""

from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from core.theme_manager import ThemeManager


class ThemedMessageBox(QMessageBox):
    """Custom message box with theme support"""
    
    # Re-export QMessageBox constants for convenience
    Critical = QMessageBox.Critical
    Warning = QMessageBox.Warning
    Information = QMessageBox.Information
    Question = QMessageBox.Question
    
    Ok = QMessageBox.Ok
    Cancel = QMessageBox.Cancel
    Yes = QMessageBox.Yes
    No = QMessageBox.No
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager()
        self.apply_theme()
    
    def apply_theme(self):
        """Apply current theme to the message box"""
        current_theme = self.theme_manager.get_current_theme_name()
        colors = self.theme_manager.get_theme(current_theme)
        
        # Create themed stylesheet with higher specificity and !important
        style = f"""
            QMessageBox {{
                background-color: {colors['surface']} !important;
                color: {colors['text_primary']} !important;
                border: 1px solid {colors['border']} !important;
                border-radius: 6px !important;
                padding: 15px !important;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
                font-size: 14px !important;
                min-width: 300px !important;
            }}
            
            QMessageBox QLabel {{
                color: {colors['text_primary']} !important;
                background: transparent !important;
                margin: 5px !important;
                line-height: 1.4 !important;
                font-size: 14px !important;
                font-weight: normal !important;
            }}
            
            QMessageBox QPushButton {{
                min-width: 100px !important;
                min-height: 32px !important;
                padding: 8px 16px !important;
                border: 1px solid {colors['primary']} !important;
                border-radius: 6px !important;
                background-color: {colors['primary']} !important;
                color: white !important;
                font-weight: 600 !important;
                font-size: 13px !important;
            }}
            
            QMessageBox QPushButton:hover {{
                background-color: {colors['primary_hover']} !important;
                border-color: {colors['primary_hover']} !important;
            }}
            
            QMessageBox QPushButton:pressed {{
                background-color: {colors['primary_pressed']} !important;
                border-color: {colors['primary_pressed']} !important;
            }}
            
            QMessageBox QPushButton:default {{
                background-color: {colors['primary']} !important;
                border: 2px solid {colors['primary']} !important;
                font-weight: bold !important;
            }}
            
            QMessageBox QPushButton:default:hover {{
                background-color: {colors['primary_hover']} !important;
                border-color: {colors['primary_hover']} !important;
            }}
            
            /* Secondary/Cancel buttons */
            QMessageBox QPushButton[text="Cancel"],
            QMessageBox QPushButton[text="No"],
            QMessageBox QPushButton[text="Close"] {{
                background-color: transparent !important;
                color: {colors['text_primary']} !important;
                border: 1px solid {colors['border']} !important;
            }}
            
            QMessageBox QPushButton[text="Cancel"]:hover,
            QMessageBox QPushButton[text="No"]:hover,
            QMessageBox QPushButton[text="Close"]:hover {{
                background-color: {colors['border']} !important;
                color: {colors['text_primary']} !important;
            }}
        """
        
        self.setStyleSheet(style)
    
    @staticmethod
    def critical(parent, title, text, buttons=QMessageBox.Ok, defaultButton=QMessageBox.NoButton):
        """Show themed critical error dialog"""
        msg_box = ThemedMessageBox(parent)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(buttons)
        msg_box.setDefaultButton(defaultButton)
        
        # Add error-specific styling
        colors = msg_box.theme_manager.get_theme(msg_box.theme_manager.get_current_theme_name())
        error_style = f"""
            QMessageBox {{
                border-left: 4px solid {colors['error']};
            }}
            QMessageBox QLabel {{
                color: {colors['error']};
                font-weight: 600;
            }}
        """
        msg_box.setStyleSheet(msg_box.styleSheet() + error_style)
        
        return msg_box.exec_()
    
    @staticmethod
    def warning(parent, title, text, buttons=QMessageBox.Ok, defaultButton=QMessageBox.NoButton):
        """Show themed warning dialog"""
        msg_box = ThemedMessageBox(parent)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(buttons)
        msg_box.setDefaultButton(defaultButton)
        
        # Add warning-specific styling
        colors = msg_box.theme_manager.get_theme(msg_box.theme_manager.get_current_theme_name())
        warning_style = f"""
            QMessageBox {{
                border-left: 4px solid {colors['warning']};
            }}
            QMessageBox QLabel {{
                color: {colors['warning']};
                font-weight: 600;
            }}
        """
        msg_box.setStyleSheet(msg_box.styleSheet() + warning_style)
        
        return msg_box.exec_()
    
    @staticmethod
    def information(parent, title, text, buttons=QMessageBox.Ok, defaultButton=QMessageBox.NoButton):
        """Show themed information dialog"""
        msg_box = ThemedMessageBox(parent)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(buttons)
        msg_box.setDefaultButton(defaultButton)
        
        # Add info-specific styling
        colors = msg_box.theme_manager.get_theme(msg_box.theme_manager.get_current_theme_name())
        info_style = f"""
            QMessageBox {{
                border-left: 4px solid {colors['primary']};
            }}
        """
        msg_box.setStyleSheet(msg_box.styleSheet() + info_style)
        
        return msg_box.exec_()
    
    @staticmethod
    def question(parent, title, text, buttons=QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No):
        """Show themed question dialog"""
        msg_box = ThemedMessageBox(parent)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(buttons)
        msg_box.setDefaultButton(defaultButton)
        
        return msg_box.exec_()


class ErrorDialogManager:
    """
    Centralized error dialog management with consistent theming
    """
    
    @staticmethod
    def show_error(parent, title, message, details=None):
        """
        Show a themed error dialog with optional details
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Main error message
            details: Optional detailed error information
        """
        if details:
            # Create detailed error dialog
            msg_box = ThemedMessageBox(parent)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setDetailedText(details)
            msg_box.setStandardButtons(QMessageBox.Ok)
            
            # Style the detailed text area
            colors = msg_box.theme_manager.get_theme_colors(msg_box.theme_manager.get_current_theme())
            detail_style = f"""
                QTextEdit {{
                    background-color: {colors['background']};
                    color: {colors['text_secondary']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 8px;
                    font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
                    font-size: 12px;
                }}
            """
            msg_box.setStyleSheet(msg_box.styleSheet() + detail_style)
            
            return msg_box.exec_()
        else:
            return ThemedMessageBox.critical(parent, title, message)
    
    @staticmethod
    def show_network_error(parent, operation="operation"):
        """Show network-specific error dialog"""
        title = "Network Error"
        message = f"Unable to complete {operation} due to network issues."
        details = """Common solutions:
• Check your internet connection
• Verify proxy settings if applicable
• Try again in a few moments
• Contact IT support if the problem persists"""
        
        return ErrorDialogManager.show_error(parent, title, message, details)
    
    @staticmethod
    def show_file_error(parent, file_path, operation="access"):
        """Show file-specific error dialog"""
        title = "File Error"
        message = f"Unable to {operation} the file:\n{file_path}"
        details = """Common solutions:
• Check if the file exists
• Verify file permissions
• Ensure the file is not open in another program
• Try selecting the file again
• Contact system administrator if needed"""
        
        return ErrorDialogManager.show_error(parent, title, message, details)
    
    @staticmethod
    def show_attachment_error(parent, file_path):
        """Show attachment-specific error dialog"""
        title = "Attachment Error"
        message = f"Problem processing attachment:\n{file_path}"
        details = """Possible causes:
• File is corrupted or invalid
• File format not supported
• File is too large (max 25MB)
• File contains potentially harmful content

Solutions:
• Try re-saving the file
• Convert to a different format
• Compress large files
• Scan with antivirus software"""
        
        return ErrorDialogManager.show_error(parent, title, message, details)


def apply_global_messagebox_theme():
    """
    Apply theme to all standard QMessageBox instances globally
    This is a fallback for any non-themed message boxes
    """
    try:
        theme_manager = ThemeManager.instance()
        current_theme = theme_manager.get_current_theme_name()
        colors = theme_manager.get_theme(current_theme)
        
        global_style = f"""
            QMessageBox {{
                background-color: {colors['surface']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            
            QMessageBox QLabel {{
                color: {colors['text_primary']};
                background: transparent;
            }}
            
            QMessageBox QPushButton {{
                min-width: 80px;
                min-height: 28px;
                padding: 6px 12px;
                border: 1px solid {colors['primary']};
                border-radius: 4px;
                background-color: {colors['primary']};
                color: white;
                font-weight: 600;
            }}
            
            QMessageBox QPushButton:hover {{
                background-color: {colors['primary_hover']};
            }}
            
            QMessageBox QPushButton:pressed {{
                background-color: {colors['primary_pressed']};
            }}
        """
        
        # Apply to application
        app = QApplication.instance()
        if app:
            current_stylesheet = app.styleSheet()
            # Remove old QMessageBox styles and add new ones
            lines = current_stylesheet.split('\n')
            filtered_lines = [line for line in lines if 'QMessageBox' not in line]
            new_stylesheet = '\n'.join(filtered_lines) + '\n' + global_style
            app.setStyleSheet(new_stylesheet)
            
    except Exception as e:
        print(f"Warning: Could not apply global message box theme: {e}")


# Auto-apply global theme when module is imported
try:
    apply_global_messagebox_theme()
except:
    pass  # Silently fail if theme manager isn't ready