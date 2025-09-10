"""
Global Stylesheet for Mini Email CRM
Defines color scheme, typography, spacing, and widget styles
Follows UI Design Guidelines
"""

PRIMARY_BLUE = "#2196F3"
SUCCESS_GREEN = "#4CAF50"
ERROR_RED = "#F44336"
LIGHT_GREY = "#F5F5F5"
DARK_GREY = "#333333"
BORDER_GREY = "#DDDDDD"
DISABLED_GREY = "#CCCCCC"
WARNING_ORANGE = "#FF9800"

FONT_FAMILY = "'Segoe UI', 'Roboto', 'Arial', sans-serif"
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
    transition: background 0.2s;
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
    background-color: white;
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
    background-color: white;
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
    "SUCCESS_BADGE_STYLE", "ERROR_BADGE_STYLE", "SPACING_STYLE"
]
