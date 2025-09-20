"""
Base Themed Widgets for Mini Email CRM
Provides base classes for theme-aware UI components with enhanced text visibility
"""

from PyQt5.QtWidgets import QWidget, QFrame, QDialog, QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import pyqtSignal
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.theme_manager import ThemeManager
from utils.text_visibility import ThemedTextHelper, TextVisibilityManager

import os
import sys
from PyQt5.QtWidgets import QWidget, QFrame, QDialog
from PyQt5.QtCore import pyqtSignal

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.theme_manager import ThemeManager
from ui.styles.dynamic_stylesheet import DynamicStylesheetGenerator


class ThemedWidget(QWidget):
    """
    Base widget class that provides automatic theme support with enhanced text visibility.
    All themed widgets should inherit from this class.
    """
    
    theme_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Try to automatically initialize with ThemeManager instance
        self.theme_manager = ThemeManager.instance()
        if self.theme_manager is None:
            # Fallback: create a new instance if singleton failed
            self.theme_manager = ThemeManager()
        
        self.text_helper = ThemedTextHelper(self.theme_manager)
        self.visibility_manager = TextVisibilityManager(self.theme_manager)
        self._theme_initialized = True
    
    def set_theme_manager(self, theme_manager: ThemeManager):
        """Set the theme manager and initialize text helpers"""
        self.theme_manager = theme_manager
        self.text_helper = ThemedTextHelper(theme_manager)
        self.visibility_manager = TextVisibilityManager(theme_manager)
        self._theme_initialized = True
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Apply initial theme
        self.apply_current_theme()
    
    def on_theme_changed(self):
        """Handle theme change notification"""
        self.apply_current_theme()
        self.theme_changed.emit()
    
    def apply_current_theme(self):
        """Apply the current theme to this widget"""
        if not self._theme_initialized:
            return
        
        # Apply base widget styling
        self._apply_base_theme()
        
        # Allow subclasses to customize
        self.apply_theme_customizations()
    
    def _apply_base_theme(self):
        """Apply base theme styling to the widget"""
        if not self.theme_manager:
            return
        
        theme = self.theme_manager.get_current_theme()
        text_color = self.visibility_manager.get_optimal_text_color(
            theme['background'], None, 'primary'
        )
        
        # Apply base styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                color: {text_color};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                font-size: 14px;
            }}
        """)
    
    def apply_theme_customizations(self):
        """
        Override this method in subclasses to provide custom theme styling.
        This method is called after the base theme is applied.
        """
        pass
    
    def get_optimal_text_color(self, background_color: str = None, text_type: str = "primary") -> str:
        """Get optimal text color for the given background"""
        if not self.visibility_manager:
            return "#000000"  # Fallback
        
        if background_color is None:
            theme = self.theme_manager.get_current_theme()
            background_color = theme['surface']
        
        return self.visibility_manager.get_optimal_text_color(background_color, None, text_type)
    
    def get_text_style(self, context: str = "body", text_type: str = "primary", 
                      background_key: str = "surface") -> str:
        """Get complete text style for the given context"""
        if not self.text_helper:
            return ""
        
        return self.text_helper.get_text_style(context, text_type, background_key)
    
    def create_themed_label(self, text: str = "", label_type: str = "default") -> QLabel:
        """Create a label with automatic theme styling"""
        label = QLabel(text)
        self._apply_label_theme(label, label_type)
        return label
    
    def create_themed_button(self, text: str = "", button_type: str = "primary") -> QPushButton:
        """Create a button with automatic theme styling"""
        button = QPushButton(text)
        self._apply_button_theme(button, button_type)
        return button
    
    def _apply_label_theme(self, label: QLabel, label_type: str = "default"):
        """Apply theme styling to a label"""
        if not self.text_helper:
            return
        
        style = self.text_helper.get_label_style(label_type)
        label.setStyleSheet(f"QLabel {{ {style} }}")
    
    def _apply_button_theme(self, button: QPushButton, button_type: str = "primary"):
        """Apply theme styling to a button"""
        if not self.theme_manager:
            return
        
        theme = self.theme_manager.get_theme()
        
        if button_type == "secondary":
            bg_color = theme['surface']
            text_color = self.get_optimal_text_color(bg_color)
            border_color = theme['border']
            hover_bg = theme['hover_overlay']
            pressed_bg = theme['active_overlay']
            
            style = f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: 500;
                    font-size: 14px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                    border-color: {theme['primary']};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_bg};
                }}
                QPushButton:disabled {{
                    background-color: {theme['disabled_background']};
                    color: {theme['text_disabled']};
                    border-color: {theme['disabled']};
                }}
            """
        else:  # primary, success, error, warning
            color_map = {
                'primary': (theme['primary'], theme['primary_hover'], theme['primary_pressed']),
                'success': (theme['success'], theme['success_hover'], theme['success_pressed']),
                'error': (theme['error'], theme['error_hover'], theme['error_pressed']),
                'warning': (theme['warning'], theme['warning_hover'], theme['warning_pressed'])
            }
            
            bg_color, hover_bg, pressed_bg = color_map.get(button_type, color_map['primary'])
            text_color = self.get_optimal_text_color(bg_color)
            
            style = f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 14px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    letter-spacing: 0.3px;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_bg};
                }}
                QPushButton:disabled {{
                    background-color: {theme['disabled']};
                    color: {theme['text_disabled']};
                }}
                QPushButton:focus {{
                    outline: 2px solid {theme['border_focus']};
                    outline-offset: 2px;
                }}
            """
        
        button.setStyleSheet(style)


class ThemedFrame(QFrame):
    """
    Base frame class with automatic theme support.
    Use this for containers, cards, and layout frames.
    """
    
    theme_applied = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize theme system
        self.theme_manager = ThemeManager.instance()
        if self.theme_manager is None:
            # Fallback: create a new instance if singleton failed
            self.theme_manager = ThemeManager()
        self.stylesheet_generator = DynamicStylesheetGenerator(self.theme_manager)
        
        # Connect to theme changes
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Apply initial theme
        self.apply_current_theme()
    
    def on_theme_changed(self, theme_name: str):
        """Called when the system theme changes"""
        self.apply_current_theme()
        self.theme_applied.emit(theme_name)
    
    def apply_current_theme(self):
        """Apply the current theme to this frame"""
        stylesheet = self.get_frame_stylesheet()
        if stylesheet:
            self.setStyleSheet(stylesheet)
        
        self.apply_theme_customizations()
    
    def get_frame_stylesheet(self) -> str:
        """
        Get the stylesheet for this frame.
        Override this method to provide custom styling.
        """
        return self.stylesheet_generator.get_component_style('card')
    
    def apply_theme_customizations(self):
        """
        Apply custom theme-specific changes beyond stylesheets.
        Override this method to handle colors, icons, or other theme-dependent elements.
        """
        pass
    
    def get_current_theme(self) -> dict:
        """Get the current theme configuration"""
        return self.theme_manager.get_theme()
    
    def get_current_theme_name(self) -> str:
        """Get the current theme name"""
        return self.theme_manager.get_current_theme_name()


class ThemedDialog(QDialog):
    """
    Base dialog class with automatic theme support.
    Use this for all dialogs and modal windows.
    """
    
    theme_applied = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize theme system
        self.theme_manager = ThemeManager.instance()
        if self.theme_manager is None:
            # Fallback: create a new instance if singleton failed
            self.theme_manager = ThemeManager()
        self.stylesheet_generator = DynamicStylesheetGenerator(self.theme_manager)
        
        # Connect to theme changes
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Apply initial theme
        self.apply_current_theme()
    
    def on_theme_changed(self, theme_name: str):
        """Called when the system theme changes"""
        self.apply_current_theme()
        self.theme_applied.emit(theme_name)
    
    def apply_current_theme(self):
        """Apply the current theme to this dialog"""
        stylesheet = self.get_dialog_stylesheet()
        if stylesheet:
            self.setStyleSheet(stylesheet)
        
        self.apply_theme_customizations()
    
    def get_dialog_stylesheet(self) -> str:
        """
        Get the stylesheet for this dialog.
        Override this method to provide custom styling.
        """
        theme = self.theme_manager.get_theme()
        
        return f"""
        QDialog {{
            background-color: {theme['surface']};
            color: {theme['text_primary']};
            font-family: Arial, Helvetica, sans-serif;
        }}
        """
    
    def apply_theme_customizations(self):
        """
        Apply custom theme-specific changes beyond stylesheets.
        Override this method to handle colors, icons, or other theme-dependent elements.
        """
        pass
    
    def get_current_theme(self) -> dict:
        """Get the current theme configuration"""
        return self.theme_manager.get_theme()
    
    def get_current_theme_name(self) -> str:
        """Get the current theme name"""
        return self.theme_manager.get_current_theme_name()


class ThemeAwareMixin:
    """
    Mixin class to add theme awareness to existing widgets.
    Use this when you can't change the inheritance hierarchy.
    """
    
    def __init_theme_awareness__(self):
        """Initialize theme awareness for this widget (call this in __init__)"""
        self.theme_manager = ThemeManager.instance()
        if self.theme_manager is None:
            # Fallback: create a new instance if singleton failed
            self.theme_manager = ThemeManager()
        self.stylesheet_generator = DynamicStylesheetGenerator(self.theme_manager)
        
        # Connect to theme changes
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Apply initial theme
        self.apply_current_theme()
    
    def on_theme_changed(self, theme_name: str):
        """Called when the system theme changes"""
        self.apply_current_theme()
    
    def apply_current_theme(self):
        """Apply the current theme to this widget"""
        if hasattr(self, 'get_themed_stylesheet'):
            stylesheet = self.get_themed_stylesheet()
            if stylesheet and hasattr(self, 'setStyleSheet'):
                self.setStyleSheet(stylesheet)
        
        if hasattr(self, 'apply_theme_customizations'):
            self.apply_theme_customizations()
    
    def get_current_theme(self) -> dict:
        """Get the current theme configuration"""
        return self.theme_manager.get_theme()
    
    def get_current_theme_name(self) -> str:
        """Get the current theme name"""
        return self.theme_manager.get_current_theme_name()


# Convenience functions for common theme operations
def get_theme_color(color_name: str, theme_name: str = None) -> str:
    """Get a specific color from the current or specified theme"""
    theme_manager = ThemeManager.instance()
    if theme_manager is None:
        theme_manager = ThemeManager()
    theme = theme_manager.get_theme(theme_name)
    return theme.get(color_name, "#000000")  # Default to black if color not found


def get_current_theme_colors() -> dict:
    """Get all colors from the current theme"""
    theme_manager = ThemeManager.instance()
    if theme_manager is None:
        theme_manager = ThemeManager()
    return theme_manager.get_theme()


def is_dark_theme(theme_name: str = None) -> bool:
    """Check if the current or specified theme is a dark theme"""
    theme_manager = ThemeManager.instance()
    if theme_manager is None:
        theme_manager = ThemeManager()
    if theme_name is None:
        theme_name = theme_manager.get_current_theme_name()
    return theme_name == "dark"


def apply_button_style(button, style_type: str = "primary"):
    """Apply themed button style to a QPushButton"""
    theme = get_current_theme_colors()
    
    style_map = {
        "primary": {
            "bg": theme['primary'],
            "hover": theme['primary_hover'],
            "pressed": theme['primary_pressed']
        },
        "success": {
            "bg": theme['success'],
            "hover": theme['success_hover'],
            "pressed": theme['success_pressed']
        },
        "error": {
            "bg": theme['error'],
            "hover": theme['error_hover'],
            "pressed": theme['error_pressed']
        },
        "warning": {
            "bg": theme['warning'],
            "hover": theme['warning_hover'],
            "pressed": theme['warning_pressed']
        }
    }
    
    colors = style_map.get(style_type, style_map["primary"])
    
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {colors['bg']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {colors['hover']};
        }}
        QPushButton:pressed {{
            background-color: {colors['pressed']};
        }}
    """)