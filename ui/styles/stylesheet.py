"""
Global Stylesheet for Mini Email CRM
Defines color scheme, typography, spacing, and widget styles
Follows UI Design Guidelines
"""

# Prefer theme-managed colors when available. Fall back to these defaults.
_DEFAULTS = {
    "primary": "#2196F3",
    "success": "#4CAF50",
    "error": "#F44336",
    "background": "#F5F5F5",
    "text_primary": "#333333",
    "border": "#DDDDDD",
    "disabled": "#CCCCCC",
    "warning": "#FF9800",
}

# Attempt to import ThemeManager and read the current theme. If unavailable,
# fall back to the static defaults above so existing code keeps working.
try:
    from core.theme_manager import ThemeManager

    _theme = ThemeManager.instance().get_theme()
    PRIMARY_BLUE = _theme.get("primary", _DEFAULTS["primary"])
    SUCCESS_GREEN = _theme.get("success", _DEFAULTS["success"])
    ERROR_RED = _theme.get("error", _DEFAULTS["error"])
    LIGHT_GREY = _theme.get("background", _DEFAULTS["background"])
    DARK_GREY = _theme.get("text_primary", _DEFAULTS["text_primary"])
    BORDER_GREY = _theme.get("border", _DEFAULTS["border"])
    DISABLED_GREY = _theme.get("disabled", _DEFAULTS["disabled"])
    WARNING_ORANGE = _theme.get("warning", _DEFAULTS["warning"])
except Exception:
    # Theme system not initialized or import failed; use defaults
    PRIMARY_BLUE = _DEFAULTS["primary"]
    SUCCESS_GREEN = _DEFAULTS["success"]
    ERROR_RED = _DEFAULTS["error"]
    LIGHT_GREY = _DEFAULTS["background"]
    DARK_GREY = _DEFAULTS["text_primary"]
    BORDER_GREY = _DEFAULTS["border"]
    DISABLED_GREY = _DEFAULTS["disabled"]
    WARNING_ORANGE = _DEFAULTS["warning"]

# Additional theme-derived tokens for wider coverage in existing styles
try:
    _theme = ThemeManager.instance().get_theme()
    SURFACE = _theme.get("surface", LIGHT_GREY)
    SURFACE_ELEVATED = _theme.get("surface_elevated", SURFACE)
    SURFACE_CONTAINER = _theme.get("surface_container", SURFACE)
    TEXT_SECONDARY = _theme.get("text_secondary", "#666666")
    TEXT_TERTIARY = _theme.get("text_tertiary", "#9E9E9E")
    PRIMARY_HOVER = _theme.get("primary_hover", PRIMARY_BLUE)
    SUCCESS_HOVER = _theme.get("success_hover", SUCCESS_GREEN)
    WARNING_HOVER = _theme.get("warning_hover", WARNING_ORANGE)
    SELECTION = _theme.get("selection", "#E3F2FD")
except Exception:
    SURFACE = LIGHT_GREY
    SURFACE_ELEVATED = LIGHT_GREY
    SURFACE_CONTAINER = LIGHT_GREY
    TEXT_SECONDARY = "#666666"
    TEXT_TERTIARY = "#9E9E9E"
    PRIMARY_HOVER = PRIMARY_BLUE
    SUCCESS_HOVER = SUCCESS_GREEN
    WARNING_HOVER = WARNING_ORANGE
    SELECTION = "#E3F2FD"

FONT_FAMILY = "Arial, Helvetica, sans-serif"
FONT_SIZE = "14px"
FONT_SIZE_SMALL = "12px"
FONT_SIZE_LARGE = "18px"

SPACING_SMALL = "8px"
SPACING_MEDIUM = "16px"
SPACING_LARGE = "24px"
BORDER_RADIUS = "6px"

# --- Button Styles ---
BUTTON_STYLE = f"""
QPushButton {{
    background-color: {PRIMARY_BLUE};
    color: white;
    border: none;
    border-radius: {BORDER_RADIUS};
    padding: 10px 20px;
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
    font-weight: bold;
    letter-spacing: 0.5px;
}}
QPushButton:hover {{
    background-color: #1976D2;
}}
QPushButton:pressed {{
    background-color: #1565C0;
}}
QPushButton:focus {{
    outline: 2px solid {PRIMARY_BLUE};
    outline-offset: 2px;
}}
QPushButton:disabled {{
    background-color: {DISABLED_GREY};
    color: #666666;
}}
"""

SUCCESS_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {SUCCESS_GREEN};
    color: white;
    border: none;
    border-radius: {BORDER_RADIUS};
    padding: 10px 20px;
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: #388E3C;
}}
QPushButton:pressed {{
    background-color: #2E7D32;
}}
"""

ERROR_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {ERROR_RED};
    color: white;
    border: none;
    border-radius: {BORDER_RADIUS};
    padding: 10px 20px;
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: #D32F2F;
}}
QPushButton:pressed {{
    background-color: #B71C1C;
}}
"""

WARNING_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {WARNING_ORANGE};
    color: white;
    border: none;
    border-radius: {BORDER_RADIUS};
    padding: 10px 20px;
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: #F57C00;
}}
QPushButton:pressed {{
    background-color: #E65100;
}}
"""

# --- Input Styles ---
INPUT_STYLE = f"""
QLineEdit, QTextEdit {{
    background-color: {SURFACE_ELEVATED};
    border: 1px solid {BORDER_GREY};
    border-radius: {BORDER_RADIUS};
    padding: 8px;
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
    color: {DARK_GREY};
}}
QLineEdit:focus, QTextEdit:focus {{
    border: 2px solid {PRIMARY_BLUE};
    outline: none;
}}
QLineEdit:disabled, QTextEdit:disabled {{
    background-color: {DISABLED_GREY};
    color: #666666;
}}
QLineEdit::placeholder, QTextEdit::placeholder {{
    color: #999999;
}}
"""

# --- Container Styles ---
CONTAINER_STYLE = f"""
QWidget, QFrame {{
    background-color: {LIGHT_GREY};
    border-radius: {BORDER_RADIUS};
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
    color: {DARK_GREY};
}}
"""

CARD_STYLE = f"""
QFrame {{
    background-color: {SURFACE};
    border: 1px solid {BORDER_GREY};
    border-radius: {BORDER_RADIUS};
    padding: {SPACING_MEDIUM};
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
    color: {DARK_GREY};
}}
"""

# --- Typography ---
TITLE_STYLE = f"""
QLabel {{
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE_LARGE};
    font-weight: bold;
    color: {DARK_GREY};
}}
"""

SUBTITLE_STYLE = f"""
QLabel {{
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
    font-weight: 500;
    color: #666666;
}}
"""

BODY_STYLE = f"""
QLabel {{
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
    color: {DARK_GREY};
}}
"""

SMALL_TEXT_STYLE = f"""
QLabel {{
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE_SMALL};
    color: #888888;
}}
"""

# --- Badge Styles ---
SUCCESS_BADGE_STYLE = f"""
QLabel {{
    background-color: {SUCCESS_GREEN};
    color: white;
    border-radius: 15px;
    font-size: {FONT_SIZE};
    font-weight: bold;
    min-width: 30px;
    max-width: 50px;
    min-height: 30px;
    max-height: 30px;
    text-align: center;
}}
"""

ERROR_BADGE_STYLE = f"""
QLabel {{
    background-color: {ERROR_RED};
    color: white;
    border-radius: 15px;
    font-size: {FONT_SIZE};
    font-weight: bold;
    min-width: 30px;
    max-width: 50px;
    min-height: 30px;
    max-height: 30px;
    text-align: center;
}}
"""

# --- Utility Styles ---
SPACING_STYLE = f"""
QWidget {{
    margin: {SPACING_MEDIUM};
    padding: {SPACING_MEDIUM};
}}
"""

# --- Exported Styles ---
__all__ = [
    "PRIMARY_BLUE", "SUCCESS_GREEN", "ERROR_RED", "LIGHT_GREY", "DARK_GREY", "BORDER_GREY", "DISABLED_GREY", "WARNING_ORANGE",
    "FONT_FAMILY", "FONT_SIZE", "FONT_SIZE_SMALL", "FONT_SIZE_LARGE",
    "BUTTON_STYLE", "SUCCESS_BUTTON_STYLE", "ERROR_BUTTON_STYLE", "WARNING_BUTTON_STYLE",
    "INPUT_STYLE", "CONTAINER_STYLE", "CARD_STYLE",
    "TITLE_STYLE", "SUBTITLE_STYLE", "BODY_STYLE", "SMALL_TEXT_STYLE",
    "SUCCESS_BADGE_STYLE", "ERROR_BADGE_STYLE", "SPACING_STYLE",
    # Additional tokens
    "SURFACE", "SURFACE_ELEVATED", "SURFACE_CONTAINER", "TEXT_SECONDARY", "TEXT_TERTIARY",
    "PRIMARY_HOVER", "SUCCESS_HOVER", "WARNING_HOVER", "SELECTION"
]
