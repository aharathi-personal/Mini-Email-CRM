"""
Dynamic Stylesheet Generator for Mini Email CRM
Generates complete application stylesheets from theme configurations
Supports all UI components with comprehensive theming and text visibility optimization
"""

from typing import Dict, Any
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.theme_manager import ThemeManager
from utils.text_visibility import TextVisibilityManager, ThemedTextHelper


class DynamicStylesheetGenerator:
    """
    Generates complete Qt stylesheets from theme configurations.
    Provides comprehensive styling for all UI components with optimized text visibility.
    """
    
    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager
        self.text_helper = ThemedTextHelper(theme_manager)
        self.visibility_manager = TextVisibilityManager(theme_manager)
    
    def generate_stylesheet(self, theme_name: str = None) -> str:
        """Generate complete application stylesheet for theme with optimized text visibility"""
        if theme_name is None:
            theme_name = self.theme_manager.get_current_theme_name()
        
        theme = self.theme_manager.get_theme(theme_name)
        
        # Get optimized text colors for different backgrounds
        main_text = self.visibility_manager.get_optimal_text_color(theme['background'], theme_name, 'primary')
        surface_text = self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')
        secondary_text = self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'secondary')
        
        return f"""
/* ==================== MAIN APPLICATION ==================== */
QMainWindow {{
    background-color: {theme['background']};
    color: {main_text};
    font-family: Arial, Helvetica, sans-serif;
    font-size: 14px;
    line-height: 1.4;
}}

QWidget {{
    background-color: transparent;
    color: {surface_text};
    font-family: Arial, Helvetica, sans-serif;
    line-height: 1.4;
}}

/* ==================== ENHANCED TEXT STYLING ==================== */
{self._get_enhanced_text_styles(theme, theme_name)}

/* ==================== BUTTONS ==================== */
{self._get_enhanced_button_styles(theme, theme_name)}

/* ==================== INPUT FIELDS ==================== */
{self._get_enhanced_input_styles(theme, theme_name)}

/* ==================== COMBO BOXES ==================== */
{self._get_enhanced_combo_styles(theme, theme_name)}

/* ==================== LISTS AND TREES ==================== */
{self._get_enhanced_list_styles(theme, theme_name)}

/* ==================== SCROLL BARS ==================== */
{self._get_enhanced_scrollbar_styles(theme)}

/* ==================== PROGRESS BARS ==================== */
{self._get_enhanced_progress_styles(theme, theme_name)}

/* ==================== CARDS AND CONTAINERS ==================== */
{self._get_enhanced_container_styles(theme, theme_name)}

/* ==================== ATTACHMENT AREAS ==================== */
{self._get_enhanced_attachment_styles(theme, theme_name)}

/* ==================== MENUS ==================== */
{self._get_enhanced_menu_styles(theme, theme_name)}

/* ==================== STATUS BAR ==================== */
{self._get_enhanced_statusbar_styles(theme, theme_name)}

/* ==================== TABS ==================== */
{self._get_enhanced_tab_styles(theme, theme_name)}

/* ==================== TOOLTIPS ==================== */
{self._get_enhanced_tooltip_styles(theme, theme_name)}

/* ==================== MESSAGE BOXES ==================== */
{self._get_enhanced_messagebox_styles(theme, theme_name)}

/* ==================== SPLITTERS ==================== */
{self._get_enhanced_splitter_styles(theme)}
"""
    
    def get_component_style(self, component_name: str, theme_name: str = None) -> str:
        """Get stylesheet for a specific component"""
        if theme_name is None:
            theme_name = self.theme_manager.get_current_theme_name()
        
        theme = self.theme_manager.get_theme(theme_name)
        
        # Component-specific styles
        component_styles = {
            'button': self._get_button_style(theme),
            'input': self._get_input_style(theme),
            'list': self._get_list_style(theme),
            'card': self._get_card_style(theme),
            'attachment': self._get_attachment_style(theme),
            'progress': self._get_progress_style(theme)
        }
        
    
    def _get_enhanced_text_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced text styles with optimal visibility"""
        return f"""
/* ==================== ENHANCED LABELS ==================== */
QLabel {{
    {self.text_helper.get_text_style('body', 'primary', 'surface', theme_name).strip()}
}}

QLabel.title {{
    {self.text_helper.get_text_style('title', 'primary', 'background', theme_name).strip()}
}}

QLabel.subtitle {{
    {self.text_helper.get_text_style('subtitle', 'secondary', 'background', theme_name).strip()}
}}

QLabel.section {{
    {self.text_helper.get_text_style('section_header', 'primary', 'surface', theme_name).strip()}
}}

QLabel.field {{
    {self.text_helper.get_text_style('label', 'secondary', 'surface', theme_name).strip()}
}}

QLabel.secondary {{
    {self.text_helper.get_text_style('small', 'secondary', 'surface', theme_name).strip()}
}}

QLabel.small {{
    {self.text_helper.get_text_style('caption', 'tertiary', 'surface', theme_name).strip()}
}}

QLabel.status {{
    {self.text_helper.get_text_style('status', 'secondary', 'surface', theme_name).strip()}
}}

QLabel.error {{
    color: {theme['error']};
    font-size: 12px;
    font-weight: 500;
    font-family: Arial, Helvetica, sans-serif;
}}

QLabel.success {{
    color: {theme['success']};
    font-size: 12px;
    font-weight: 500;
    font-family: Arial, Helvetica, sans-serif;
}}

QLabel.warning {{
    color: {theme['warning']};
    font-size: 12px;
    font-weight: 500;
    font-family: Arial, Helvetica, sans-serif;
}}

QLabel.link {{
    color: {theme['text_link']};
    text-decoration: underline;
    {self.text_helper.get_text_style('link', 'primary', 'surface', theme_name).strip()}
}}

QLabel.link:hover {{
    color: {theme['text_link_hover']};
}}

/* ==================== ENHANCED TEXT ELEMENTS ==================== */
QTextEdit, QPlainTextEdit {{
    {self.text_helper.get_text_style('body', 'primary', 'surface', theme_name).strip()}
    line-height: 1.5;
}}

QTextEdit::placeholder, QPlainTextEdit::placeholder {{
    {self.text_helper.get_text_style('body', 'placeholder', 'surface', theme_name).strip()}
    font-style: italic;
}}
        """
    
    def _get_enhanced_button_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced button styles with optimal text visibility"""
        button_text = self.visibility_manager.get_optimal_text_color(theme['primary'], theme_name, 'on_primary')
        
        return f"""
QPushButton {{
    background-color: {theme['primary']};
    color: {button_text};
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    {self.text_helper.get_text_style('button', 'primary', 'surface', theme_name).strip()}
    letter-spacing: 0.3px;
    min-height: 20px;
    outline: none;
}}

QPushButton:hover {{
    background-color: {theme['primary_hover']};
}}

QPushButton:pressed {{
    background-color: {theme['primary_pressed']};
}}

QPushButton:focus {{
    outline: 2px solid {theme['border_focus']};
    outline-offset: 2px;
}}

QPushButton:disabled {{
    background-color: {theme['disabled']};
    color: {theme['text_disabled']};
    border: 1px solid {theme['disabled']};
}}

/* Button Variants */
QPushButton.success {{
    background-color: {theme['success']};
    color: {self.visibility_manager.get_optimal_text_color(theme['success'], theme_name, 'on_primary')};
}}

QPushButton.success:hover {{
    background-color: {theme['success_hover']};
}}

QPushButton.success:pressed {{
    background-color: {theme['success_pressed']};
}}

QPushButton.error {{
    background-color: {theme['error']};
    color: {self.visibility_manager.get_optimal_text_color(theme['error'], theme_name, 'on_primary')};
}}

QPushButton.error:hover {{
    background-color: {theme['error_hover']};
}}

QPushButton.error:pressed {{
    background-color: {theme['error_pressed']};
}}

QPushButton.warning {{
    background-color: {theme['warning']};
    color: {self.visibility_manager.get_optimal_text_color(theme['warning'], theme_name, 'on_primary')};
}}

QPushButton.warning:hover {{
    background-color: {theme['warning_hover']};
}}

QPushButton.warning:pressed {{
    background-color: {theme['warning_pressed']};
}}

/* Secondary Button Style */
QPushButton.secondary {{
    background-color: {theme['surface']};
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')};
    border: 1px solid {theme['border']};
}}

QPushButton.secondary:hover {{
    background-color: {theme['hover_overlay']};
    border-color: {theme['primary']};
}}

QPushButton.secondary:pressed {{
    background-color: {theme['active_overlay']};
}}

/* Small Button Style */
QPushButton.small {{
    padding: 6px 12px;
    {self.text_helper.get_text_style('small', 'primary', 'surface', theme_name).strip()}
    min-height: 16px;
}}
        """
    
    def _get_enhanced_input_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced input field styles with optimal text visibility"""
        input_text = self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')
        
        return f"""
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {theme['surface']};
    border: 1px solid {theme['border']};
    border-radius: 6px;
    padding: 8px 12px;
    color: {input_text};
    {self.text_helper.get_text_style('input', 'primary', 'surface', theme_name).strip()}
    selection-background-color: {theme['selection']};
    selection-color: {self.visibility_manager.get_optimal_text_color(theme['selection'], theme_name, 'primary')};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {theme['border_focus']};
    background-color: {theme['surface_container']};
    padding: 7px 11px; /* Adjust for thicker border */
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    background-color: {theme['disabled_background']};
    color: {theme['text_disabled']};
    border-color: {theme['disabled']};
}}

QLineEdit::placeholder, QTextEdit::placeholder, QPlainTextEdit::placeholder {{
    color: {theme['text_placeholder']};
    font-style: italic;
}}
        """
    
    def _get_enhanced_combo_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced combo box styles"""
        return f"""
QComboBox {{
    background-color: {theme['surface']};
    border: 1px solid {theme['border']};
    border-radius: 6px;
    padding: 8px 12px;
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')};
    {self.text_helper.get_text_style('input', 'primary', 'surface', theme_name).strip()}
    min-width: 100px;
}}

QComboBox:focus {{
    border: 2px solid {theme['border_focus']};
    padding: 7px 11px; /* Adjust for thicker border */
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
    color: {self.visibility_manager.get_optimal_text_color(theme['surface_elevated'], theme_name, 'primary')};
    selection-background-color: {theme['selection']};
    selection-color: {self.visibility_manager.get_optimal_text_color(theme['selection'], theme_name, 'primary')};
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
    
    def _get_enhanced_list_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced list widget styles"""
        return f"""
QListWidget, QTreeWidget {{
    background-color: {theme['surface']};
    border: 1px solid {theme['border']};
    border-radius: 6px;
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')};
    {self.text_helper.get_text_style('body', 'primary', 'surface', theme_name).strip()}
    outline: none;
}}

QListWidget::item, QTreeWidget::item {{
    padding: 12px 16px;
    border-bottom: 1px solid {theme['divider']};
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')};
    margin: 0px;
}}

QListWidget::item:last, QTreeWidget::item:last {{
    border-bottom: none;
}}

QListWidget::item:hover, QTreeWidget::item:hover {{
    background-color: {theme['hover_overlay']};
    color: {self.visibility_manager.get_optimal_text_color(theme['hover_overlay'], theme_name, 'primary')};
}}

QListWidget::item:selected, QTreeWidget::item:selected {{
    background-color: {theme['selection']};
    color: {self.visibility_manager.get_optimal_text_color(theme['selection'], theme_name, 'primary')};
    border-bottom: 1px solid {theme['selection']};
}}

QListWidget::item:selected:active, QTreeWidget::item:selected:active {{
    background-color: {theme['selection_hover']};
}}
        """
    
    def _get_enhanced_scrollbar_styles(self, theme: Dict[str, str]) -> str:
        """Generate enhanced scroll bar styles"""
        return f"""
QScrollBar:vertical {{
    background-color: {theme['background']};
    width: 12px;
    border-radius: 6px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {theme['border']};
    border-radius: 6px;
    min-height: 20px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {theme['text_secondary']};
}}

QScrollBar::handle:vertical:pressed {{
    background-color: {theme['primary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    border: none;
    background: none;
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {theme['background']};
    height: 12px;
    border-radius: 6px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: {theme['border']};
    border-radius: 6px;
    min-width: 20px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {theme['text_secondary']};
}}

QScrollBar::handle:horizontal:pressed {{
    background-color: {theme['primary']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    border: none;
    background: none;
    width: 0px;
}}
        """
    
    def _get_enhanced_progress_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced progress bar styles"""
        return f"""
QProgressBar {{
    border: 1px solid {theme['border']};
    border-radius: 6px;
    text-align: center;
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')};
    background-color: {theme['surface']};
    {self.text_helper.get_text_style('small', 'primary', 'surface', theme_name).strip()}
    font-weight: 500;
    min-height: 20px;
    padding: 2px;
}}

QProgressBar::chunk {{
    background-color: {theme['primary']};
    border-radius: 4px;
    margin: 1px;
}}

QProgressBar.success::chunk {{
    background-color: {theme['success']};
}}

QProgressBar.error::chunk {{
    background-color: {theme['error']};
}}

QProgressBar.warning::chunk {{
    background-color: {theme['warning']};
}}
        """
    
    def _get_enhanced_container_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced container and card styles"""
        return f"""
QFrame.card {{
    background-color: {theme['surface']};
    border: 1px solid {theme['border']};
    border-radius: 8px;
    padding: 16px;
}}

QFrame.card-elevated {{
    background-color: {theme['surface_elevated']};
    border: 1px solid {theme['border']};
    border-radius: 8px;
    padding: 16px;
    /* box-shadow: 0 2px 8px {theme['shadow']}; */
}}

QGroupBox {{
    {self.text_helper.get_text_style('section_header', 'primary', 'surface', theme_name).strip()}
    border: 1px solid {theme['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 18px;
    background-color: {theme['surface']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px 0 8px;
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')};
    background-color: {theme['surface']};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-weight: 600;
}}
        """
    
    def _get_enhanced_attachment_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced attachment area styles"""
        return f"""
QFrame.attachment-zone {{
    background-color: {theme['attachment_bg']};
    border: 2px dashed {theme['primary']};
    border-radius: 8px;
    padding: 20px;
}}

QFrame.attachment-zone:hover {{
    background-color: {theme['attachment_hover']};
    border-color: {theme['primary_hover']};
}}

QFrame.attachment-item {{
    background-color: {theme['surface']};
    border: 1px solid {theme['border']};
    border-radius: 6px;
    padding: 8px 12px;
    margin: 2px 0px;
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')};
}}

QFrame.attachment-item:hover {{
    background-color: {theme['hover_overlay']};
    border-color: {theme['primary']};
}}

QFrame.attachment-item QLabel {{
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')};
    {self.text_helper.get_text_style('small', 'primary', 'surface', theme_name).strip()}
}}
        """
    
    def _get_enhanced_menu_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced menu styles"""
        return f"""
QMenuBar {{
    background-color: {theme['surface']};
    border-bottom: 1px solid {theme['border']};
    padding: 4px;
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')};
    {self.text_helper.get_text_style('menu', 'primary', 'surface', theme_name).strip()}
}}

QMenuBar::item {{
    padding: 8px 12px;
    background-color: transparent;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {theme['primary']};
    color: {self.visibility_manager.get_optimal_text_color(theme['primary'], theme_name, 'on_primary')};
}}

QMenuBar::item:pressed {{
    background-color: {theme['primary_pressed']};
    color: {self.visibility_manager.get_optimal_text_color(theme['primary_pressed'], theme_name, 'on_primary')};
}}

QMenu {{
    background-color: {theme['surface_elevated']};
    border: 1px solid {theme['border']};
    border-radius: 6px;
    color: {self.visibility_manager.get_optimal_text_color(theme['surface_elevated'], theme_name, 'primary')};
    padding: 4px;
    {self.text_helper.get_text_style('menu', 'primary', 'surface_elevated', theme_name).strip()}
}}

QMenu::item {{
    padding: 8px 16px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {theme['selection']};
    color: {self.visibility_manager.get_optimal_text_color(theme['selection'], theme_name, 'primary')};
}}

QMenu::separator {{
    height: 1px;
    background-color: {theme['divider']};
    margin: 4px 0px;
}}
        """
    
    def _get_enhanced_statusbar_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced status bar styles"""
        return f"""
QStatusBar {{
    background-color: {theme['surface']};
    border-top: 1px solid {theme['border']};
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'secondary')};
    padding: 4px 8px;
    {self.text_helper.get_text_style('status', 'secondary', 'surface', theme_name).strip()}
}}

QStatusBar QLabel {{
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'secondary')};
    {self.text_helper.get_text_style('status', 'secondary', 'surface', theme_name).strip()}
}}
        """
    
    def _get_enhanced_tab_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced tab styles"""
        return f"""
QTabWidget::pane {{
    border: 1px solid {theme['border']};
    background-color: {theme['surface']};
    border-radius: 6px;
    padding: 4px;
}}

QTabBar::tab {{
    background-color: {theme['background']};
    border: 1px solid {theme['border']};
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: {self.visibility_manager.get_optimal_text_color(theme['background'], theme_name, 'secondary')};
    {self.text_helper.get_text_style('menu', 'secondary', 'background', theme_name).strip()}
}}

QTabBar::tab:selected {{
    background-color: {theme['surface']};
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')};
    border-bottom: 1px solid {theme['surface']};
}}

QTabBar::tab:hover {{
    background-color: {theme['hover_overlay']};
    color: {self.visibility_manager.get_optimal_text_color(theme['hover_overlay'], theme_name, 'primary')};
}}
        """
    
    def _get_enhanced_tooltip_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced tooltip styles"""
        return f"""
QToolTip {{
    background-color: {theme['surface_elevated']};
    border: 1px solid {theme['border']};
    border-radius: 4px;
    padding: 8px;
    color: {self.visibility_manager.get_optimal_text_color(theme['surface_elevated'], theme_name, 'primary')};
    {self.text_helper.get_text_style('caption', 'primary', 'surface_elevated', theme_name).strip()}
    /* box-shadow: 0 2px 8px {theme['shadow']}; */
}}
        """
    
    def _get_enhanced_messagebox_styles(self, theme: Dict[str, str], theme_name: str) -> str:
        """Generate enhanced message box styles"""
        return f"""
QMessageBox {{
    background-color: {theme['surface']};
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')};
    {self.text_helper.get_text_style('body', 'primary', 'surface', theme_name).strip()}
}}

QMessageBox QPushButton {{
    min-width: 80px;
    padding: 8px 16px;
    border: 1px solid {theme['primary']};
    border-radius: 4px;
    background-color: {theme['primary']};
    color: {self.visibility_manager.get_optimal_text_color(theme['primary'], theme_name, 'on_primary')};
    {self.text_helper.get_text_style('button', 'primary', 'surface', theme_name).strip()}
}}

QMessageBox QPushButton:hover {{
    background-color: {theme['primary_hover']};
}}

QMessageBox QPushButton:pressed {{
    background-color: {theme['primary_pressed']};
}}

QMessageBox QLabel {{
    color: {self.visibility_manager.get_optimal_text_color(theme['surface'], theme_name, 'primary')};
    {self.text_helper.get_text_style('body', 'primary', 'surface', theme_name).strip()}
}}
        """
    
    def _get_enhanced_splitter_styles(self, theme: Dict[str, str]) -> str:
        """Generate enhanced splitter styles"""
        return f"""
QSplitter::handle {{
    background-color: {theme['border']};
}}

QSplitter::handle:horizontal {{
    width: 3px;
}}

QSplitter::handle:vertical {{
    height: 3px;
}}

QSplitter::handle:hover {{
    background-color: {theme['primary']};
}}

QSplitter::handle:pressed {{
    background-color: {theme['primary_pressed']};
}}
        """
    
    def _get_button_style(self, theme: Dict[str, str]) -> str:
        """Get button-specific stylesheet"""
        return f"""
        QPushButton {{
            background-color: {theme['primary']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {theme['primary_hover']};
        }}
        QPushButton:pressed {{
            background-color: {theme['primary_pressed']};
        }}
        """
    
    def _get_input_style(self, theme: Dict[str, str]) -> str:
        """Get input field stylesheet"""
        return f"""
        QLineEdit, QTextEdit {{
            background-color: {theme['surface']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 8px;
            color: {theme['text_primary']};
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border: 2px solid {theme['border_focus']};
        }}
        """
    
    def _get_list_style(self, theme: Dict[str, str]) -> str:
        """Get list widget stylesheet"""
        return f"""
        QListWidget {{
            background-color: {theme['surface']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            color: {theme['text_primary']};
        }}
        QListWidget::item:selected {{
            background-color: {theme['selection']};
        }}
        QListWidget::item:hover {{
            background-color: {theme['hover_overlay']};
        }}
        """
    
    def _get_card_style(self, theme: Dict[str, str]) -> str:
        """Get card/container stylesheet"""
        return f"""
        QFrame.card {{
            background-color: {theme['surface']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 16px;
        }}
        """
    
    def _get_attachment_style(self, theme: Dict[str, str]) -> str:
        """Get attachment area stylesheet"""
        return f"""
        QFrame.attachment-zone {{
            background-color: {theme['attachment_bg']};
            border: 2px dashed {theme['primary']};
            border-radius: 6px;
        }}
        QFrame.attachment-item {{
            background-color: {theme['surface']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            padding: 8px;
        }}
        """
    
    def _get_progress_style(self, theme: Dict[str, str]) -> str:
        """Get progress bar stylesheet"""
        return f"""
        QProgressBar {{
            border: 1px solid {theme['border']};
            border-radius: 6px;
            text-align: center;
            color: {theme['text_primary']};
            background-color: {theme['surface']};
        }}
        QProgressBar::chunk {{
            background-color: {theme['primary']};
            border-radius: 5px;
        }}
        """
