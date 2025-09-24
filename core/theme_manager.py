"""
Theme Manager for Mini Email CRM
Handles system theme detection, theme switching, and theme persistence
Supports Windows, macOS, and Linux theme detection
"""

import sys
import os
import json
from typing import Dict, Any, Optional
from PyQt5.QtCore import QSettings, pyqtSignal, QObject, QTimer
from PyQt5.QtWidgets import QApplication


class ThemeManager(QObject):
    """
    Central theme management system for the application.
    Provides system theme detection, theme switching, and persistence.
    """
    
    theme_changed = pyqtSignal(str)  # Signal when theme changes
    _instance = None
    
    def __init__(self):
        super().__init__()
        # Don't check _instance here as it causes issues with singleton creation
        
        self.settings = QSettings('MiniCRM', 'ThemeSettings')
        self.current_theme = None
        self.themes = self._load_themes()
        self.auto_detect = True
        
        # Timer for periodic system theme checking
        self.theme_check_timer = QTimer()
        self.theme_check_timer.timeout.connect(self._check_system_theme_change)
        self.theme_check_timer.start(5000)  # Check every 5 seconds
        
        # Initialize theme
        self._initialize_theme()
    
    @classmethod
    def instance(cls):
        """Get the singleton instance of ThemeManager"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _initialize_theme(self):
        """Initialize theme on startup"""
        # Load saved preferences
        self.auto_detect = self.settings.value('auto_detect_theme', True, type=bool)
        saved_theme = self.settings.value('manual_theme', 'light', type=str)
        
        if self.auto_detect:
            detected_theme = self.detect_system_theme()
            self.set_theme(detected_theme)
        else:
            self.set_theme(saved_theme)
    
    def _load_themes(self) -> Dict[str, Dict[str, str]]:
        """Load theme configurations from themes.json"""
        themes_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config', 'themes.json'
        )
        
        try:
            with open(themes_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load themes.json: {e}")
            # Return default themes as fallback
            return self._get_default_themes()
    
    def _get_default_themes(self) -> Dict[str, Dict[str, str]]:
        """Return default theme configurations if themes.json is not available"""
        # Provide a more complete set of theme tokens used across the UI so
        # missing or minimal themes.json files do not cause KeyError during
        # styling lookups.
        return {
            "light": {
                "primary": "#2196F3",
                "primary_hover": "#1976D2",
                "primary_pressed": "#1565C0",
                "success": "#4CAF50",
                "success_hover": "#388E3C",
                "success_pressed": "#2E7D32",
                "error": "#F44336",
                "warning": "#FF9800",
                "warning_hover": "#FB8C00",
                "warning_pressed": "#F57C00",
                "background": "#F5F5F5",
                "surface": "#FFFFFF",
                "surface_elevated": "#FAFAFA",
                "surface_container": "#FFFFFF",
                "surface_hover": "#F0F0F0",
                "text_primary": "#333333",
                "text_secondary": "#666666",
                "text_tertiary": "#9E9E9E",
                "text_placeholder": "#BDBDBD",
                "text_disabled": "#9E9E9E",
                "border": "#DDDDDD",
                "border_focus": "#90CAF9",
                "disabled": "#E0E0E0",
                "disabled_background": "#F0F0F0",
                "hover_overlay": "#F3F7FB",
                "attachment_bg": "#E3F2FD",
                "selection": "#E3F2FD"
            },
            "dark": {
                "primary": "#64B5F6",
                "primary_hover": "#42A5F5",
                "primary_pressed": "#2196F3",
                "success": "#66BB6A",
                "success_hover": "#4CAF50",
                "success_pressed": "#388E3C",
                "error": "#EF5350",
                "warning": "#FFB74D",
                "warning_hover": "#FFB74D",
                "warning_pressed": "#FFA726",
                "background": "#121212",
                "surface": "#1E1E1E",
                "surface_elevated": "#2A2A2A",
                "surface_container": "#232323",
                "surface_hover": "#2C2C2C",
                "text_primary": "#FFFFFF",
                "text_secondary": "#AAAAAA",
                "text_tertiary": "#9E9E9E",
                "text_placeholder": "#757575",
                "text_disabled": "#555555",
                "border": "#333333",
                "border_focus": "#64B5F6",
                "disabled": "#3A3A3A",
                "disabled_background": "#2B2B2B",
                "hover_overlay": "#1F1F1F",
                "attachment_bg": "#263238",
                "selection": "#263238"
            }
        }
    
    def detect_system_theme(self) -> str:
        """Detect system theme preference"""
        if sys.platform == "win32":
            return self._detect_windows_theme()
        elif sys.platform == "darwin":
            return self._detect_macos_theme()
        else:
            return self._detect_linux_theme()
    
    def _detect_windows_theme(self) -> str:
        """Windows 10/11 theme detection"""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "light" if value else "dark"
        except Exception:
            return "light"  # Default fallback
    
    def _detect_macos_theme(self) -> str:
        """macOS theme detection"""
        try:
            import subprocess
            result = subprocess.run([
                "defaults", "read", "-g", "AppleInterfaceStyle"
            ], capture_output=True, text=True, timeout=5)
            return "dark" if "Dark" in result.stdout else "light"
        except Exception:
            return "light"
    
    def _detect_linux_theme(self) -> str:
        """Linux theme detection (GNOME/KDE)"""
        try:
            import subprocess
            
            # Try GNOME first
            try:
                result = subprocess.run([
                    "gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"
                ], capture_output=True, text=True, timeout=5)
                if "dark" in result.stdout.lower():
                    return "dark"
            except Exception:
                pass
            
            # Try KDE
            try:
                result = subprocess.run([
                    "kreadconfig5", "--group", "General", "--key", "ColorScheme"
                ], capture_output=True, text=True, timeout=5)
                if "dark" in result.stdout.lower():
                    return "dark"
            except Exception:
                pass
            
            return "light"
        except Exception:
            return "light"
    
    def _check_system_theme_change(self):
        """Periodically check for system theme changes"""
        if not self.auto_detect:
            return
        
        detected_theme = self.detect_system_theme()
        if detected_theme != self.current_theme:
            self.set_theme(detected_theme)
    
    def set_theme(self, theme_name: str):
        """Set the current theme"""
        if theme_name not in self.themes:
            print(f"Warning: Theme '{theme_name}' not found. Using 'light' theme.")
            theme_name = "light"
        
        if self.current_theme != theme_name:
            self.current_theme = theme_name
            self.theme_changed.emit(theme_name)
            
            # Save to settings if not auto-detecting
            if not self.auto_detect:
                self.settings.setValue('manual_theme', theme_name)
    
    def get_theme(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Get theme configuration"""
        if theme_name is None:
            theme_name = self.current_theme or "light"
        # Return a theme dict merged with the defaults so missing tokens from
        # a user-provided themes.json don't cause KeyError elsewhere.
        loaded = self.themes.get(theme_name, {})
        defaults = self._get_default_themes().get(theme_name, {})

        # Merge defaults with loaded values (loaded takes precedence)
        merged = defaults.copy()
        merged.update(loaded)
        return merged
    
    def get_current_theme_name(self) -> str:
        """Get the current theme name"""
        return self.current_theme or "light"
    
    def set_auto_detect(self, enabled: bool):
        """Enable or disable automatic theme detection"""
        self.auto_detect = enabled
        self.settings.setValue('auto_detect_theme', enabled)
        
        if enabled:
            # Immediately check and apply system theme
            detected_theme = self.detect_system_theme()
            self.set_theme(detected_theme)
        else:
            # Stop the timer
            self.theme_check_timer.stop()
    
    def get_auto_detect(self) -> bool:
        """Check if auto-detection is enabled"""
        return self.auto_detect
    
    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return list(self.themes.keys())
    
    def reload_themes(self):
        """Reload themes from configuration file"""
        self.themes = self._load_themes()
        # Reapply current theme to pick up any changes
        if self.current_theme:
            self.theme_changed.emit(self.current_theme)
