"""Configuration manager for application settings."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from .models import ApplicationConfig
from ..utils.constants import APP_NAME, DEFAULT_SETUPC_PATH


class ConfigManager(QObject):
    """Manages application configuration and settings persistence."""
    
    # Signal emitted when configuration changes
    config_changed = pyqtSignal(ApplicationConfig)
    
    def __init__(self):
        super().__init__()
        self._config = ApplicationConfig()
        self._config_file_path = self._get_config_file_path()
        self.load_config()
    
    def _get_config_file_path(self) -> Path:
        """Get the path to the configuration file."""
        # Use AppData on Windows, ~/.config on Unix
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', Path.home() / 'AppData/Roaming'))
        else:  # Unix-like
            config_dir = Path.home() / '.config'
        
        app_config_dir = config_dir / APP_NAME.replace(' ', '_').lower()
        app_config_dir.mkdir(parents=True, exist_ok=True)
        
        return app_config_dir / 'config.json'
    
    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            if self._config_file_path.exists():
                with open(self._config_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._config = ApplicationConfig.from_dict(data)
                
                # Check if the configured setupc_path exists, if not use default
                if not os.path.isfile(self._config.setupc_path):
                    self._config.setupc_path = DEFAULT_SETUPC_PATH
                    self.save_config()  # Save the updated path
            else:
                # Create default config file
                self.save_config()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load config from {self._config_file_path}: {e}")
            # Use default configuration
            self._config = ApplicationConfig()
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            # Ensure directory exists
            self._config_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, indent=2)
        except IOError as e:
            print(f"Warning: Failed to save config to {self._config_file_path}: {e}")
    
    @property
    def config(self) -> ApplicationConfig:
        """Get the current configuration."""
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration with new values."""
        updated = False
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                if getattr(self._config, key) != value:
                    setattr(self._config, key, value)
                    updated = True
        
        if updated:
            self.save_config()
            self.config_changed.emit(self._config)
    
    def update_window_geometry(self, x: int, y: int, width: int, height: int) -> None:
        """Update window geometry settings."""
        geometry = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
        
        if self._config.window_geometry != geometry:
            self._config.window_geometry = geometry
            self.save_config()
    
    def get_setupc_path(self) -> str:
        """Get the setupc.exe path."""
        return self._config.setupc_path
    
    def set_setupc_path(self, path: str) -> None:
        """Set the setupc.exe path."""
        if self._config.setupc_path != path:
            self._config.setupc_path = path
            self.save_config()
            self.config_changed.emit(self._config)
    
    def get_command_timeout(self) -> int:
        """Get the command timeout."""
        return self._config.command_timeout
    
    def set_command_timeout(self, timeout: int) -> None:
        """Set the command timeout."""
        if timeout > 0 and self._config.command_timeout != timeout:
            self._config.command_timeout = timeout
            self.save_config()
            self.config_changed.emit(self._config)
    
    def get_auto_refresh_interval(self) -> int:
        """Get the auto refresh interval."""
        return self._config.auto_refresh_interval
    
    def set_auto_refresh_interval(self, interval: int) -> None:
        """Set the auto refresh interval."""
        if interval >= 0 and self._config.auto_refresh_interval != interval:
            self._config.auto_refresh_interval = interval
            self.save_config()
            self.config_changed.emit(self._config)
    
    def get_window_geometry(self) -> Dict[str, int]:
        """Get the window geometry."""
        return self._config.window_geometry.copy()
    
    def get_log_level(self) -> str:
        """Get the logging level."""
        return self._config.log_level
    
    def set_log_level(self, level: str) -> None:
        """Set the logging level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level in valid_levels and self._config.log_level != level:
            self._config.log_level = level
            self.save_config()
            self.config_changed.emit(self._config)
    
    def get_theme(self) -> str:
        """Get the application theme."""
        return self._config.theme
    
    def set_theme(self, theme: str) -> None:
        """Set the application theme."""
        valid_themes = ['system', 'light', 'dark']
        if theme in valid_themes and self._config.theme != theme:
            self._config.theme = theme
            self.save_config()
            self.config_changed.emit(self._config)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = ApplicationConfig()
        self.save_config()
        self.config_changed.emit(self._config)
    
    def export_config(self, file_path: str) -> bool:
        """Export configuration to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, indent=2)
            return True
        except IOError:
            return False
    
    def import_config(self, file_path: str) -> bool:
        """Import configuration from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate the imported data
            imported_config = ApplicationConfig.from_dict(data)
            
            self._config = imported_config
            self.save_config()
            self.config_changed.emit(self._config)
            return True
        except (json.JSONDecodeError, IOError):
            return False


class RecentFilesManager:
    """Manages recently used setupc.exe paths."""
    
    def __init__(self, max_files: int = 10):
        self.max_files = max_files
        self._recent_files = []
        self._config_file = self._get_recent_files_path()
        self.load_recent_files()
    
    def _get_recent_files_path(self) -> Path:
        """Get the path to the recent files configuration."""
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', Path.home() / 'AppData/Roaming'))
        else:  # Unix-like
            config_dir = Path.home() / '.config'
        
        app_config_dir = config_dir / APP_NAME.replace(' ', '_').lower()
        app_config_dir.mkdir(parents=True, exist_ok=True)
        
        return app_config_dir / 'recent_files.json'
    
    def load_recent_files(self) -> None:
        """Load recent files from configuration."""
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._recent_files = data.get('recent_setupc_paths', [])
        except (json.JSONDecodeError, IOError):
            self._recent_files = []
    
    def save_recent_files(self) -> None:
        """Save recent files to configuration."""
        try:
            data = {'recent_setupc_paths': self._recent_files}
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass  # Fail silently for recent files
    
    def add_recent_file(self, file_path: str) -> None:
        """Add a file to the recent files list."""
        # Remove if already exists
        if file_path in self._recent_files:
            self._recent_files.remove(file_path)
        
        # Add to beginning
        self._recent_files.insert(0, file_path)
        
        # Limit to max files
        if len(self._recent_files) > self.max_files:
            self._recent_files = self._recent_files[:self.max_files]
        
        self.save_recent_files()
    
    def get_recent_files(self) -> list:
        """Get the list of recent files."""
        # Filter out files that no longer exist
        existing_files = []
        for file_path in self._recent_files:
            if os.path.exists(file_path):
                existing_files.append(file_path)
        
        # Update the list if any files were removed
        if len(existing_files) != len(self._recent_files):
            self._recent_files = existing_files
            self.save_recent_files()
        
        return self._recent_files.copy()
    
    def clear_recent_files(self) -> None:
        """Clear all recent files."""
        self._recent_files = []
        self.save_recent_files()