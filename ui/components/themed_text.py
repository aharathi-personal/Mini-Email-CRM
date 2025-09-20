"""
Enhanced Text Components for Mini Email CRM
Provides themed text widgets with automatic visibility optimization
"""

from PyQt5.QtWidgets import QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.theme_manager import ThemeManager
from utils.text_visibility import ThemedTextHelper, TextVisibilityManager


class ThemedLabel(QLabel):
    """Enhanced QLabel with automatic theme-aware styling and optimal text visibility."""
    
    def __init__(self, text: str = "", label_type: str = "default", parent=None):
        super().__init__(text, parent)
        self.label_type = label_type
        self.theme_manager = None
        self.text_helper = None
        self._setup_label()
    
    def _setup_label(self):
        """Set up the label with basic properties"""
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
    
    def set_theme_manager(self, theme_manager: ThemeManager):
        """Set the theme manager and initialize text helper"""
        self.theme_manager = theme_manager
        self.text_helper = ThemedTextHelper(theme_manager)
        self.apply_theme()
    
    def apply_theme(self):
        """Apply theme-specific styling"""
        if not self.text_helper:
            return
        
        style = self.text_helper.get_label_style(self.label_type)
        self.setStyleSheet(f"QLabel {{ {style} }}")
    
    def set_label_type(self, label_type: str):
        """Change the label type and reapply styling"""
        self.label_type = label_type
        self.apply_theme()


class ThemedButton(QPushButton):
    """Enhanced QPushButton with automatic theme-aware styling and optimal text visibility."""
    
    def __init__(self, text: str = "", button_type: str = "primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.theme_manager = None
        self.text_helper = None
        self._setup_button()
    
    def _setup_button(self):
        """Set up the button with basic properties"""
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
    
    def set_theme_manager(self, theme_manager: ThemeManager):
        """Set the theme manager and initialize text helper"""
        self.theme_manager = theme_manager
        self.text_helper = ThemedTextHelper(theme_manager)
        self.apply_theme()
    
    def apply_theme(self):
        """Apply theme-specific styling"""
        if not self.text_helper or not self.theme_manager:
            return
        
        theme = self.theme_manager.get_current_theme()
        visibility_manager = TextVisibilityManager(self.theme_manager)
        
        # Get appropriate colors based on button type
        if self.button_type == "secondary":
            bg_color = theme['surface']
            text_color = visibility_manager.get_optimal_text_color(bg_color)
            border_color = theme['border']
            hover_bg = theme['hover_overlay']
            pressed_bg = theme['active_overlay']
        elif self.button_type == "success":
            bg_color = theme['success']
            text_color = visibility_manager.get_optimal_text_color(bg_color)
            hover_bg = theme['success_hover']
            pressed_bg = theme['success_pressed']
        elif self.button_type == "error":
            bg_color = theme['error']
            text_color = visibility_manager.get_optimal_text_color(bg_color)
            hover_bg = theme['error_hover']
            pressed_bg = theme['error_pressed']
        elif self.button_type == "warning":
            bg_color = theme['warning']
            text_color = visibility_manager.get_optimal_text_color(bg_color)
            hover_bg = theme['warning_hover']
            pressed_bg = theme['warning_pressed']
        else:  # primary
            bg_color = theme['primary']
            text_color = visibility_manager.get_optimal_text_color(bg_color)
            hover_bg = theme['primary_hover']
            pressed_bg = theme['primary_pressed']
        
        # Build style based on type
        if self.button_type == "secondary":
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
        else:
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
        
        self.setStyleSheet(style)
    
    def set_button_type(self, button_type: str):
        """Change the button type and reapply styling"""
        self.button_type = button_type
        self.apply_theme()


class ThemedLineEdit(QLineEdit):
    """Enhanced QLineEdit with automatic theme-aware styling and optimal text visibility."""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.theme_manager = None
        self.text_helper = None
        self._setup_input()
    
    def _setup_input(self):
        """Set up the input with basic properties"""
        self.setFocusPolicy(Qt.StrongFocus)
    
    def set_theme_manager(self, theme_manager: ThemeManager):
        """Set the theme manager and initialize text helper"""
        self.theme_manager = theme_manager
        self.text_helper = ThemedTextHelper(theme_manager)
        self.apply_theme()
    
    def apply_theme(self):
        """Apply theme-specific styling"""
        if not self.text_helper or not self.theme_manager:
            return
        
        theme = self.theme_manager.get_current_theme()
        visibility_manager = TextVisibilityManager(self.theme_manager)
        
        text_color = visibility_manager.get_optimal_text_color(theme['surface'])
        selection_text = visibility_manager.get_optimal_text_color(theme['selection'])
        
        style = f"""
            QLineEdit {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {text_color};
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                selection-background-color: {theme['selection']};
                selection-color: {selection_text};
            }}
            QLineEdit:focus {{
                border: 2px solid {theme['border_focus']};
                background-color: {theme['surface_container']};
                padding: 7px 11px;
            }}
            QLineEdit:disabled {{
                background-color: {theme['disabled_background']};
                color: {theme['text_disabled']};
                border-color: {theme['disabled']};
            }}
        """
        
        self.setStyleSheet(style)
        
        # Set placeholder text style
        palette = self.palette()
        palette.setColor(QPalette.PlaceholderText, 
                        visibility_manager.contrast_checker.hex_to_rgb(theme['text_placeholder']))
        self.setPalette(palette)


class ThemedTextEdit(QTextEdit):
    """Enhanced QTextEdit with automatic theme-aware styling and optimal text visibility."""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.theme_manager = None
        self.text_helper = None
        self._setup_input()
    
    def _setup_input(self):
        """Set up the text edit with basic properties"""
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAcceptRichText(False)  # Plain text by default
    
    def set_theme_manager(self, theme_manager: ThemeManager):
        """Set the theme manager and initialize text helper"""
        self.theme_manager = theme_manager
        self.text_helper = ThemedTextHelper(theme_manager)
        self.apply_theme()
    
    def apply_theme(self):
        """Apply theme-specific styling"""
        if not self.text_helper or not self.theme_manager:
            return
        
        theme = self.theme_manager.get_current_theme()
        visibility_manager = TextVisibilityManager(self.theme_manager)
        
        text_color = visibility_manager.get_optimal_text_color(theme['surface'])
        selection_text = visibility_manager.get_optimal_text_color(theme['selection'])
        
        style = f"""
            QTextEdit {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {text_color};
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.5;
                selection-background-color: {theme['selection']};
                selection-color: {selection_text};
            }}
            QTextEdit:focus {{
                border: 2px solid {theme['border_focus']};
                background-color: {theme['surface_container']};
                padding: 7px 11px;
            }}
            QTextEdit:disabled {{
                background-color: {theme['disabled_background']};
                color: {theme['text_disabled']};
                border-color: {theme['disabled']};
            }}
        """
        
        self.setStyleSheet(style)


class ThemedComboBox(QComboBox):
    """Enhanced QComboBox with automatic theme-aware styling and optimal text visibility."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = None
        self.text_helper = None
        self._setup_combo()
    
    def _setup_combo(self):
        """Set up the combo box with basic properties"""
        self.setFocusPolicy(Qt.StrongFocus)
    
    def set_theme_manager(self, theme_manager: ThemeManager):
        """Set the theme manager and initialize text helper"""
        self.theme_manager = theme_manager
        self.text_helper = ThemedTextHelper(theme_manager)
        self.apply_theme()
    
    def apply_theme(self):
        """Apply theme-specific styling"""
        if not self.text_helper or not self.theme_manager:
            return
        
        theme = self.theme_manager.get_current_theme()
        visibility_manager = TextVisibilityManager(self.theme_manager)
        
        text_color = visibility_manager.get_optimal_text_color(theme['surface'])
        dropdown_text = visibility_manager.get_optimal_text_color(theme['surface_elevated'])
        selection_text = visibility_manager.get_optimal_text_color(theme['selection'])
        
        style = f"""
            QComboBox {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {text_color};
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                min-width: 100px;
            }}
            QComboBox:focus {{
                border: 2px solid {theme['border_focus']};
                padding: 7px 11px;
            }}
            QComboBox:disabled {{
                background-color: {theme['disabled_background']};
                color: {theme['text_disabled']};
                border-color: {theme['disabled']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 2px solid {theme['text_secondary']};
                width: 6px;
                height: 6px;
                border-top: none;
                border-right: none;
                transform: rotate(-45deg);
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme['surface_elevated']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                color: {dropdown_text};
                selection-background-color: {theme['selection']};
                selection-color: {selection_text};
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {theme['divider']};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {theme['hover_overlay']};
            }}
        """
        
        self.setStyleSheet(style)


class StatusLabel(ThemedLabel):
    """Specialized label for displaying status information with color coding."""
    
    def __init__(self, text: str = "", status_type: str = "info", parent=None):
        super().__init__(text, "status", parent)
        self.status_type = status_type
    
    def apply_theme(self):
        """Apply theme-specific styling with status colors"""
        if not self.text_helper or not self.theme_manager:
            return
        
        theme = self.theme_manager.get_current_theme()
        
        # Get status-specific colors
        status_colors = {
            'info': theme['text_secondary'],
            'success': theme['success'],
            'warning': theme['warning'],
            'error': theme['error'],
            'primary': theme['primary']
        }
        
        color = status_colors.get(self.status_type, theme['text_secondary'])
        
        style = f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                font-weight: 500;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            }}
        """
        
        self.setStyleSheet(style)
    
    def set_status_type(self, status_type: str):
        """Change the status type and reapply styling"""
        self.status_type = status_type
        self.apply_theme()
    
    def set_status(self, text: str, status_type: str = None):
        """Set both text and status type"""
        self.setText(text)
        if status_type:
            self.set_status_type(status_type)


class TitleLabel(ThemedLabel):
    """Specialized label for titles with enhanced typography."""
    
    def __init__(self, text: str = "", level: int = 1, parent=None):
        super().__init__(text, "title", parent)
        self.level = level  # 1-6, like HTML headings
        self._setup_title()
    
    def _setup_title(self):
        """Set up title-specific properties"""
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    
    def apply_theme(self):
        """Apply theme-specific styling with title hierarchy"""
        if not self.text_helper or not self.theme_manager:
            return
        
        theme = self.theme_manager.get_current_theme()
        visibility_manager = TextVisibilityManager(self.theme_manager)
        
        # Size and weight based on level
        sizes = {1: '24px', 2: '20px', 3: '18px', 4: '16px', 5: '14px', 6: '12px'}
        weights = {1: 'bold', 2: 'bold', 3: '600', 4: '600', 5: '500', 6: '500'}
        
        size = sizes.get(self.level, '18px')
        weight = weights.get(self.level, 'bold')
        
        text_color = visibility_manager.get_optimal_text_color(
            theme['background'], None, 'primary'
        )
        
        style = f"""
            QLabel {{
                color: {text_color};
                font-size: {size};
                font-weight: {weight};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                margin: 8px 0px 4px 0px;
            }}
        """
        
        self.setStyleSheet(style)
    
    def set_level(self, level: int):
        """Change the title level and reapply styling"""
        self.level = max(1, min(6, level))  # Clamp between 1-6
        self.apply_theme()


# Convenience factory functions
def create_themed_label(text: str = "", label_type: str = "default", theme_manager: ThemeManager = None) -> ThemedLabel:
    """Create a themed label with optional theme manager setup"""
    label = ThemedLabel(text, label_type)
    if theme_manager:
        label.set_theme_manager(theme_manager)
    return label


def create_themed_button(text: str = "", button_type: str = "primary", theme_manager: ThemeManager = None) -> ThemedButton:
    """Create a themed button with optional theme manager setup"""
    button = ThemedButton(text, button_type)
    if theme_manager:
        button.set_theme_manager(theme_manager)
    return button


def create_status_label(text: str = "", status_type: str = "info", theme_manager: ThemeManager = None) -> StatusLabel:
    """Create a status label with optional theme manager setup"""
    label = StatusLabel(text, status_type)
    if theme_manager:
        label.set_theme_manager(theme_manager)
    return label


def create_title_label(text: str = "", level: int = 1, theme_manager: ThemeManager = None) -> TitleLabel:
    """Create a title label with optional theme manager setup"""
    label = TitleLabel(text, level)
    if theme_manager:
        label.set_theme_manager(theme_manager)
    return label