"""Ribbon-style toolbar for main commands."""

import os
from typing import Optional
from PyQt6.QtWidgets import (QToolBar, QWidget, QHBoxLayout, QVBoxLayout, 
                            QLabel, QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon

from ...core.models import PortPair, Port


class RibbonButton(QPushButton):
    """Windows 10-style ribbon button."""
    
    def __init__(self, text: str, icon_name: str = None, parent=None):
        super().__init__(parent)
        self.setText(text)
        
        # Windows 10-like button sizing and styling
        self.setStyleSheet("QPushButton { padding: 4px 8px; }")
        
        # Set icon if provided
        if icon_name:
            icon = self._load_svg_icon(icon_name)
            if not icon.isNull():
                self.setIcon(icon)
                self.setIconSize(QSize(16, 16))  # Standard Windows icon size
        
    
    def _load_svg_icon(self, icon_name: str):
        """Load SVG icon and return QIcon."""
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        icon_path = os.path.join(project_root, "assets", "icons", "toolbar", f"{icon_name}.svg")
        
        if os.path.exists(icon_path):
            # Create QIcon from SVG
            return QIcon(icon_path)
        else:
            # Return null icon if SVG not found
            return QIcon()


class RibbonGroup(QFrame):
    """Group of related ribbon buttons."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setup_ui(title)
    
    def setup_ui(self, title: str):
        """Set up the group UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 2)
        
        # Buttons area
        self.buttons_widget = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_widget)
        self.buttons_layout.setSpacing(4)  # Windows 10-like spacing
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.buttons_widget)
    
    def add_button(self, button: RibbonButton):
        """Add a button to the group."""
        self.buttons_layout.addWidget(button)
    
    def add_separator(self):
        """Add a Windows 10-style vertical separator."""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.buttons_layout.addWidget(separator)


class RibbonToolbar(QToolBar):
    """Ribbon-style toolbar with contextual commands."""
    
    # Signals for actions
    new_port_pair = pyqtSignal()
    remove_port_pair = pyqtSignal()
    configure_port = pyqtSignal()
    refresh_ports = pyqtSignal()
    
    preinstall_driver = pyqtSignal()
    update_driver = pyqtSignal()
    reload_driver = pyqtSignal()
    uninstall_driver = pyqtSignal()
    
    enable_all_ports = pyqtSignal()
    disable_all_ports = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_selection = None
        self.setup_ui()
        self.setup_actions()
    
    def setup_ui(self):
        """Set up the ribbon toolbar UI."""
        self.setMovable(False)
        self.setFloatable(False)
        self.setMinimumHeight(48)
        self.setMaximumHeight(48)
                
        # Main widget to hold ribbon groups
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Port Management group
        self.port_group = RibbonGroup("Port Management")
        
        self.new_button = RibbonButton("New Pair", "new")
        self.new_button.setToolTip("Create a new virtual port pair")
        
        self.remove_button = RibbonButton("Remove", "remove")
        self.remove_button.setToolTip("Remove selected port pair")
        self.remove_button.setEnabled(False)
        
        self.configure_button = RibbonButton("Configure", "configure")
        self.configure_button.setToolTip("Configure selected port")
        self.configure_button.setEnabled(False)
        
        self.port_group.add_button(self.new_button)
        self.port_group.add_button(self.remove_button)
        self.port_group.add_separator()
        self.port_group.add_button(self.configure_button)
        
        # View group
        self.view_group = RibbonGroup("View")
        
        self.refresh_button = RibbonButton("Refresh", "refresh")
        self.refresh_button.setToolTip("Refresh port list")
        
        self.view_group.add_button(self.refresh_button)
        
        # Driver group
        self.driver_group = RibbonGroup("Driver")
        
        self.preinstall_button = RibbonButton("Preinstall", "preinstall")
        self.preinstall_button.setToolTip("Preinstall com0com driver")
        
        self.update_button = RibbonButton("Update", "update")
        self.update_button.setToolTip("Update com0com driver")
        
        self.reload_button = RibbonButton("Reload", "reload")
        self.reload_button.setToolTip("Reload com0com driver")
        
        self.uninstall_button = RibbonButton("Uninstall", "uninstall")
        self.uninstall_button.setToolTip("Uninstall com0com driver")
        
        self.driver_group.add_button(self.preinstall_button)
        self.driver_group.add_button(self.update_button)
        self.driver_group.add_separator()
        self.driver_group.add_button(self.reload_button)
        self.driver_group.add_button(self.uninstall_button)
        
        # System group
        self.system_group = RibbonGroup("System")
        
        self.enable_all_button = RibbonButton("Enable All", "enable")
        self.enable_all_button.setToolTip("Enable all ports")
        
        self.disable_all_button = RibbonButton("Disable All", "disable")
        self.disable_all_button.setToolTip("Disable all ports")
        
        self.system_group.add_button(self.enable_all_button)
        self.system_group.add_button(self.disable_all_button)
        
        # Add groups to main layout
        main_layout.addWidget(self.port_group)
        main_layout.addWidget(self.view_group)
        main_layout.addWidget(self.driver_group)
        main_layout.addWidget(self.system_group)
        main_layout.addStretch()
        
        # Add main widget to toolbar
        self.addWidget(main_widget)
    
    def setup_actions(self):
        """Set up button actions."""
        self.new_button.clicked.connect(self.new_port_pair.emit)
        self.remove_button.clicked.connect(self.remove_port_pair.emit)
        self.configure_button.clicked.connect(self.configure_port.emit)
        self.refresh_button.clicked.connect(self.refresh_ports.emit)
        
        self.preinstall_button.clicked.connect(self.preinstall_driver.emit)
        self.update_button.clicked.connect(self.update_driver.emit)
        self.reload_button.clicked.connect(self.reload_driver.emit)
        self.uninstall_button.clicked.connect(self.uninstall_driver.emit)
        
        self.enable_all_button.clicked.connect(self.enable_all_ports.emit)
        self.disable_all_button.clicked.connect(self.disable_all_ports.emit)
    
    def update_selection(self, selection_type: str, selection_data: Optional[object] = None):
        """Update button states based on current selection."""
        self.current_selection = (selection_type, selection_data)
        
        if selection_type == "pair":
            # Port pair selected
            self.remove_button.setEnabled(True)
            self.configure_button.setEnabled(False)
            self.configure_button.setText("Configure")
            
        elif selection_type == "port":
            # Individual port selected
            self.remove_button.setEnabled(False)
            self.configure_button.setEnabled(True)
            self.configure_button.setText("Configure")
            
        elif selection_type == "root":
            # Root node selected
            self.remove_button.setEnabled(False)
            self.configure_button.setEnabled(False)
            self.configure_button.setText("Configure")
            
        else:
            # Nothing selected
            self.remove_button.setEnabled(False)
            self.configure_button.setEnabled(False)
            self.configure_button.setText("Configure")
    
    def set_busy(self, busy: bool):
        """Enable/disable buttons based on busy state."""
        buttons = [
            self.new_button, self.remove_button, self.configure_button,
            self.preinstall_button, self.update_button, self.reload_button,
            self.uninstall_button, self.enable_all_button, self.disable_all_button
        ]
        
        for button in buttons:
            if not busy:
                # Re-apply selection-based enabling
                if button in [self.remove_button, self.configure_button]:
                    continue  # These will be handled by update_selection
                button.setEnabled(True)
            else:
                button.setEnabled(False)
        
        # Refresh button should always be enabled unless specifically busy
        self.refresh_button.setEnabled(not busy)
        
        # Re-apply selection state if not busy
        if not busy and self.current_selection:
            self.update_selection(self.current_selection[0], self.current_selection[1])
