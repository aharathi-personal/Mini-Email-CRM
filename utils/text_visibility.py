"""
Text Visibility Utilities for Mini Email CRM
Provides contrast checking, readability optimization, and accessibility features
"""

import colorsys
from typing import Dict, Tuple, Optional, Any
import re
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.theme_manager import ThemeManager


class ContrastChecker:
    """Utility class for checking and improving text contrast ratios."""
    
    # WCAG 2.1 accessibility standards
    WCAG_AA_NORMAL = 4.5    # Minimum contrast for normal text (AA)
    WCAG_AAA_NORMAL = 7.0   # Enhanced contrast for normal text (AAA)
    WCAG_AA_LARGE = 3.0     # Minimum contrast for large text (AA)
    WCAG_AAA_LARGE = 4.5    # Enhanced contrast for large text (AAA)
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color."""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    @staticmethod
    def get_luminance(rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance of an RGB color."""
        def normalize(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        r, g, b = map(normalize, rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    @classmethod
    def get_contrast_ratio(cls, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors (1:1 to 21:1)."""
        rgb1 = cls.hex_to_rgb(color1)
        rgb2 = cls.hex_to_rgb(color2)
        
        lum1 = cls.get_luminance(rgb1)
        lum2 = cls.get_luminance(rgb2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @classmethod
    def meets_wcag_aa(cls, text_color: str, background_color: str, is_large_text: bool = False) -> bool:
        """Check if color combination meets WCAG AA standards."""
        ratio = cls.get_contrast_ratio(text_color, background_color)
        threshold = cls.WCAG_AA_LARGE if is_large_text else cls.WCAG_AA_NORMAL
        return ratio >= threshold
    
    @classmethod
    def meets_wcag_aaa(cls, text_color: str, background_color: str, is_large_text: bool = False) -> bool:
        """Check if color combination meets WCAG AAA standards."""
        ratio = cls.get_contrast_ratio(text_color, background_color)
        threshold = cls.WCAG_AAA_LARGE if is_large_text else cls.WCAG_AAA_NORMAL
        return ratio >= threshold
    
    @classmethod
    def adjust_color_for_contrast(cls, text_color: str, background_color: str, 
                                 target_ratio: float = WCAG_AA_NORMAL) -> str:
        """Adjust text color to meet target contrast ratio against background."""
        current_ratio = cls.get_contrast_ratio(text_color, background_color)
        
        if current_ratio >= target_ratio:
            return text_color
        
        # Try making the text darker or lighter
        text_rgb = cls.hex_to_rgb(text_color)
        bg_rgb = cls.hex_to_rgb(background_color)
        bg_luminance = cls.get_luminance(bg_rgb)
        
        # If background is light, make text darker
        # If background is dark, make text lighter
        if bg_luminance > 0.5:
            # Light background - darken text
            return cls._darken_until_contrast(text_rgb, background_color, target_ratio)
        else:
            # Dark background - lighten text
            return cls._lighten_until_contrast(text_rgb, background_color, target_ratio)
    
    @classmethod
    def _darken_until_contrast(cls, text_rgb: Tuple[int, int, int], background_color: str, 
                              target_ratio: float) -> str:
        """Darken text color until target contrast is achieved."""
        r, g, b = text_rgb
        
        for darkness in range(10, 101, 10):  # 10%, 20%, ... 100%
            factor = (100 - darkness) / 100
            new_rgb = (int(r * factor), int(g * factor), int(b * factor))
            new_color = cls.rgb_to_hex(new_rgb)
            
            if cls.get_contrast_ratio(new_color, background_color) >= target_ratio:
                return new_color
        
        return "#000000"  # Fallback to black
    
    @classmethod
    def _lighten_until_contrast(cls, text_rgb: Tuple[int, int, int], background_color: str, 
                               target_ratio: float) -> str:
        """Lighten text color until target contrast is achieved."""
        r, g, b = text_rgb
        
        for lightness in range(10, 101, 10):  # 10%, 20%, ... 100%
            factor = lightness / 100
            new_rgb = (
                int(r + (255 - r) * factor),
                int(g + (255 - g) * factor),
                int(b + (255 - b) * factor)
            )
            new_color = cls.rgb_to_hex(new_rgb)
            
            if cls.get_contrast_ratio(new_color, background_color) >= target_ratio:
                return new_color
        
        return "#FFFFFF"  # Fallback to white


class TextVisibilityManager:
    """Manages text visibility and readability across themes."""
    
    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager
        self.contrast_checker = ContrastChecker()
    
    def get_optimal_text_color(self, background_color: str, theme_name: str = None, 
                              text_type: str = "primary") -> str:
        """Get optimal text color for given background, considering theme context."""
        if theme_name is None:
            theme_name = self.theme_manager.get_current_theme_name()
        
        theme = self.theme_manager.get_theme(theme_name)
        
        # Try theme-appropriate text colors first
        text_candidates = [
            theme.get(f'text_{text_type}', theme['text_primary']),
            theme['text_primary'],
            theme['text_secondary'],
            theme['text_high_contrast'],
            "#000000" if theme_name == "light" else "#FFFFFF"
        ]
        
        # Find first candidate that meets WCAG AA standards
        for candidate in text_candidates:
            if self.contrast_checker.meets_wcag_aa(candidate, background_color):
                return candidate
        
        # If none work, adjust the primary text color
        return self.contrast_checker.adjust_color_for_contrast(
            theme['text_primary'], background_color
        )
    
    def get_text_size_weight(self, context: str) -> Dict[str, str]:
        """Get recommended text size and weight for different contexts."""
        size_weight_map = {
            # Headers
            'title': {'size': '18px', 'weight': 'bold'},
            'subtitle': {'size': '16px', 'weight': '600'},
            'section_header': {'size': '15px', 'weight': '600'},
            
            # Body text
            'body': {'size': '14px', 'weight': 'normal'},
            'body_emphasis': {'size': '14px', 'weight': '500'},
            'small': {'size': '12px', 'weight': 'normal'},
            'caption': {'size': '11px', 'weight': 'normal'},
            
            # Interactive elements
            'button': {'size': '14px', 'weight': 'bold'},
            'link': {'size': '14px', 'weight': 'normal'},
            'menu': {'size': '14px', 'weight': 'normal'},
            
            # Status and labels
            'label': {'size': '13px', 'weight': '500'},
            'status': {'size': '12px', 'weight': 'normal'},
            'error': {'size': '12px', 'weight': '500'},
            'warning': {'size': '12px', 'weight': '500'},
            'success': {'size': '12px', 'weight': '500'},
            
            # Input elements
            'input': {'size': '14px', 'weight': 'normal'},
            'placeholder': {'size': '14px', 'weight': 'normal'},
        }
        
        return size_weight_map.get(context, {'size': '14px', 'weight': 'normal'})
    
    def validate_theme_contrast(self, theme_name: str) -> Dict[str, Any]:
        """Validate all text-background combinations in a theme."""
        theme = self.theme_manager.get_theme(theme_name)
        results = {
            'theme': theme_name,
            'passed': [],
            'failed': [],
            'warnings': []
        }
        
        # Define critical text-background pairs to check
        checks = [
            ('text_primary', 'background', 'Primary text on main background'),
            ('text_primary', 'surface', 'Primary text on surface'),
            ('text_secondary', 'background', 'Secondary text on main background'),
            ('text_secondary', 'surface', 'Secondary text on surface'),
            ('text_disabled', 'surface', 'Disabled text on surface'),
            ('text_placeholder', 'surface', 'Placeholder text on surface'),
            ('text_on_primary', 'primary', 'Text on primary color'),
            ('text_primary', 'surface_elevated', 'Primary text on elevated surface'),
            ('text_primary', 'attachment_bg', 'Primary text on attachment background'),
        ]
        
        for text_key, bg_key, description in checks:
            if text_key in theme and bg_key in theme:
                text_color = theme[text_key]
                bg_color = theme[bg_key]
                
                ratio = self.contrast_checker.get_contrast_ratio(text_color, bg_color)
                meets_aa = self.contrast_checker.meets_wcag_aa(text_color, bg_color)
                meets_aaa = self.contrast_checker.meets_wcag_aaa(text_color, bg_color)
                
                result = {
                    'description': description,
                    'text_color': text_color,
                    'background_color': bg_color,
                    'contrast_ratio': round(ratio, 2),
                    'meets_aa': meets_aa,
                    'meets_aaa': meets_aaa
                }
                
                if meets_aa:
                    results['passed'].append(result)
                else:
                    results['failed'].append(result)
                    
                if not meets_aaa:
                    results['warnings'].append(f"{description}: Only meets AA, not AAA")
        
        return results
    
    def generate_accessibility_report(self) -> str:
        """Generate a comprehensive accessibility report for all themes."""
        report = "# Text Visibility and Accessibility Report\n\n"
        
        for theme_name in ['light', 'dark']:
            report += f"## {theme_name.title()} Theme\n\n"
            
            validation = self.validate_theme_contrast(theme_name)
            
            report += f"**Passed WCAG AA:** {len(validation['passed'])}\n"
            report += f"**Failed WCAG AA:** {len(validation['failed'])}\n"
            report += f"**AAA Warnings:** {len(validation['warnings'])}\n\n"
            
            if validation['failed']:
                report += "### Failed Contrast Checks\n"
                for fail in validation['failed']:
                    report += f"- {fail['description']}: {fail['contrast_ratio']}:1 "
                    report += f"({fail['text_color']} on {fail['background_color']})\n"
                report += "\n"
            
            if validation['warnings']:
                report += "### Accessibility Warnings\n"
                for warning in validation['warnings']:
                    report += f"- {warning}\n"
                report += "\n"
        
        return report


class ThemedTextHelper:
    """Helper class for creating theme-aware text with optimal visibility."""
    
    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager
        self.visibility_manager = TextVisibilityManager(theme_manager)
    
    def get_text_style(self, context: str = "body", text_type: str = "primary", 
                      background_key: str = "surface", theme_name: str = None) -> str:
        """Generate complete text style for given context and theme."""
        if theme_name is None:
            theme_name = self.theme_manager.get_current_theme_name()
        
        theme = self.theme_manager.get_theme(theme_name)
        size_weight = self.visibility_manager.get_text_size_weight(context)
        
        # Get optimal text color
        background_color = theme.get(background_key, theme['surface'])
        text_color = self.visibility_manager.get_optimal_text_color(
            background_color, theme_name, text_type
        )
        
        return f"""
            color: {text_color};
            font-size: {size_weight['size']};
            font-weight: {size_weight['weight']};
            font-family: Arial, Helvetica, sans-serif;
        """
    
    def get_label_style(self, label_type: str = "default", theme_name: str = None) -> str:
        """Get optimized label styles for different label types."""
        label_configs = {
            'title': ('title', 'primary', 'background'),
            'subtitle': ('subtitle', 'secondary', 'background'),
            'section': ('section_header', 'primary', 'surface'),
            'field': ('label', 'secondary', 'surface'),
            'status': ('status', 'secondary', 'surface'),
            'error': ('small', 'primary', 'surface'),
            'warning': ('small', 'primary', 'surface'),
            'success': ('small', 'primary', 'surface'),
            'default': ('body', 'primary', 'surface')
        }
        
        context, text_type, bg_key = label_configs.get(label_type, label_configs['default'])
        base_style = self.get_text_style(context, text_type, bg_key, theme_name)
        
        # Add special styling for status labels
        if label_type in ['error', 'warning', 'success']:
            if theme_name is None:
                theme_name = self.theme_manager.get_current_theme_name()
            theme = self.theme_manager.get_theme(theme_name)
            
            color_override = theme.get(label_type, theme['text_primary'])
            base_style = base_style.replace(
                f"color: {theme['text_primary']};",
                f"color: {color_override};"
            )
        
        return base_style