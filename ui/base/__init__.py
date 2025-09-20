"""
Base UI Components for Mini Email CRM
Provides themed base classes and utilities for all UI components
"""

from .themed_widgets import (
    ThemedWidget,
    ThemedFrame, 
    ThemedDialog,
    ThemeAwareMixin,
    get_theme_color,
    get_current_theme_colors,
    is_dark_theme,
    apply_button_style
)

__all__ = [
    'ThemedWidget',
    'ThemedFrame',
    'ThemedDialog', 
    'ThemeAwareMixin',
    'get_theme_color',
    'get_current_theme_colors',
    'is_dark_theme',
    'apply_button_style'
]