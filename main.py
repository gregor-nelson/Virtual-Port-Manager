#!/usr/bin/env python3
"""
Virtual Port Manager - Main Application Entry Point
A PyQt6-based GUI wrapper for com0com's setupc.exe command-line tool.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.gui.main_window import MainWindow
from src.utils.constants import APP_NAME, APP_VERSION


def main():
    """Initialize and run the Virtual Port Manager application."""
    # Disable dark mode detection
    os.environ['QT_QPA_PLATFORMTHEME'] = ''
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("Virtual Port Manager")
    
    # Set native Windows style for best fusiontegration
    app.setStyle('fusion')
    
    
    # Set Windows-specific attributes for better integration
    if sys.platform == "win32":
        pass  # High DPI support is enabled by default in Qt6
    
    # Set application icon (try SVG first, then ICO)
    svg_icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "app_icon.svg")
    ico_icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "app.ico")
    
    if os.path.exists(svg_icon_path):
        app.setWindowIcon(QIcon(svg_icon_path))
    elif os.path.exists(ico_icon_path):
        app.setWindowIcon(QIcon(ico_icon_path))
    
    # Apply Windows theme stylesheet
    stylesheet_path = os.path.join(os.path.dirname(__file__), "assets", "styles", "windows_theme.qss")
    if os.path.exists(stylesheet_path):
        with open(stylesheet_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()