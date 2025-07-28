"""Main window for com0com GUI Manager."""

import os
from typing import Optional
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QMenuBar, QMenu, QStatusBar, QMessageBox,
                            QProgressBar, QLabel, QFrame, QApplication, QDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QKeyEvent

from ..core.command_manager import CommandManager
from ..core.models import PortPair, Port, CommandResult, DriverInfo, DriverStatus
from ..core.config_manager import ConfigManager
from ..utils.constants import (WINDOW_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
                              WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
from .components.ribbon_toolbar import RibbonToolbar
from .components.port_tree_widget import PortTreeWidget
from .components.properties_panel import PropertiesPanel
from .components.command_output import CommandOutputPanel
from .dialogs.new_port_dialog import NewPortDialog
from .dialogs.configure_dialog import ConfigurePortDialog
from .dialogs.driver_ops_dialog import DriverOperationsDialog
from .dialogs.help_dialog import HelpDialog
from .dialogs.about_dialog import AboutDialog


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.command_manager = CommandManager(self.config_manager.get_setupc_path())
        self.current_selection = None
        
        self.setup_ui()
        self.setup_connections()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.apply_saved_geometry()
        
        # Configure command manager from settings
        self.command_manager.set_timeout(self.config_manager.get_command_timeout())
        
        # Initialize application
        # Serialize startup commands to avoid concurrent execution
        self.command_manager.port_list_updated.connect(self._on_initial_port_list_loaded, Qt.ConnectionType.SingleShotConnection)
        self.refresh_port_list()
    
    def setup_ui(self):
        """Set up the main window UI."""
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create ribbon toolbar
        self.ribbon_toolbar = RibbonToolbar()
        self.addToolBar(self.ribbon_toolbar)
        
        # Create main vertical splitter (top content, bottom command output)
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.setChildrenCollapsible(False)
        
        # Create horizontal content splitter
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setChildrenCollapsible(False)
        
        # Left panel - Port tree
        self.port_tree = PortTreeWidget()
        self.port_tree.setMinimumWidth(300)
        
        # Right panel - Properties
        self.properties_panel = PropertiesPanel()
        self.properties_panel.setMinimumWidth(350)
        
        content_splitter.addWidget(self.port_tree)
        content_splitter.addWidget(self.properties_panel)
        
        # Set splitter proportions (60% tree, 40% properties)
        content_splitter.setSizes([600, 400])
        
        # Create command output panel
        self.command_output = CommandOutputPanel()
        
        # Add to main vertical splitter
        main_splitter.addWidget(content_splitter)
        main_splitter.addWidget(self.command_output)
        
        # Set vertical proportions (most space for content, small for output)
        main_splitter.setSizes([500, 30])  # Command output starts collapsed
        
        main_layout.addWidget(main_splitter)
    
    def setup_connections(self):
        """Set up signal connections between components."""
        # Ribbon toolbar signals
        self.ribbon_toolbar.new_port_pair.connect(self.show_new_port_dialog)
        self.ribbon_toolbar.remove_port_pair.connect(self.remove_selected_port_pair)
        self.ribbon_toolbar.configure_port.connect(self.configure_selected_port)
        self.ribbon_toolbar.refresh_ports.connect(self.refresh_port_list)
        
        self.ribbon_toolbar.preinstall_driver.connect(self.preinstall_driver)
        self.ribbon_toolbar.update_driver.connect(self.update_driver)
        self.ribbon_toolbar.reload_driver.connect(self.reload_driver)
        self.ribbon_toolbar.uninstall_driver.connect(self.uninstall_driver)
        
        self.ribbon_toolbar.enable_all_ports.connect(self.enable_all_ports)
        self.ribbon_toolbar.disable_all_ports.connect(self.disable_all_ports)
        
        # Port tree signals
        self.port_tree.port_pair_selected.connect(self.on_port_pair_selected)
        self.port_tree.port_selected.connect(self.on_port_selected)
        self.port_tree.port_pair_double_clicked.connect(self.on_port_pair_double_clicked)
        self.port_tree.context_menu_requested.connect(self.show_context_menu)
        
        # Properties panel signals
        self.properties_panel.apply_changes.connect(self.apply_port_changes)
        
        # Command manager signals
        self.command_manager.port_list_updated.connect(self.on_port_list_updated)
        self.command_manager.command_completed.connect(self.on_command_completed)
        self.command_manager.driver_status_changed.connect(self.on_driver_status_changed)
        self.command_manager.error_occurred.connect(self.show_error_message)
        
        # Command output panel signals
        self.command_manager.command_completed.connect(self.command_output.on_command_completed)
    
    def setup_menu_bar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self.refresh_port_list)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        expand_all_action = QAction("Expand All", self)
        expand_all_action.triggered.connect(self.port_tree.expandAll)
        view_menu.addAction(expand_all_action)
        
        collapse_all_action = QAction("Collapse All", self)
        collapse_all_action.triggered.connect(self.port_tree.collapseAll)
        view_menu.addAction(collapse_all_action)
        
        # Action menu
        action_menu = menubar.addMenu("Action")
        
        new_pair_action = QAction("New Port Pair...", self)
        new_pair_action.setShortcut(QKeySequence.StandardKey.New)
        new_pair_action.triggered.connect(self.show_new_port_dialog)
        action_menu.addAction(new_pair_action)
        
        remove_action = QAction("Remove Selected", self)
        remove_action.setShortcut(QKeySequence.StandardKey.Delete)
        remove_action.triggered.connect(self.remove_selected_port_pair)
        action_menu.addAction(remove_action)
        
        configure_action = QAction("Configure...", self)
        configure_action.triggered.connect(self.configure_selected_port)
        action_menu.addAction(configure_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        clean_inf_action = QAction("Clean INF Files", self)
        clean_inf_action.triggered.connect(self.command_manager.clean_inf_files)
        tools_menu.addAction(clean_inf_action)
        
        list_names_action = QAction("List Friendly Names", self)
        list_names_action.triggered.connect(self.command_manager.list_friendly_names)
        tools_menu.addAction(list_names_action)
        
        update_names_action = QAction("Update Friendly Names", self)
        update_names_action.triggered.connect(self.command_manager.update_friendly_names)
        tools_menu.addAction(update_names_action)
        
        tools_menu.addSeparator()
        
        check_busy_action = QAction("Check Busy Names...", self)
        check_busy_action.triggered.connect(self.show_check_busy_names_dialog)
        tools_menu.addAction(check_busy_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        help_contents_action = QAction("Help Contents", self)
        help_contents_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_contents_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(help_contents_action)
        
        help_menu.addSeparator()
        
        driver_ops_action = QAction("Driver Operations...", self)
        driver_ops_action.triggered.connect(self.show_driver_operations_dialog)
        help_menu.addAction(driver_ops_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Driver status label
        self.driver_status_label = QLabel("Driver: Unknown")
        self.status_bar.addPermanentWidget(self.driver_status_label)
    
    # Slot implementations
    @pyqtSlot()
    def refresh_port_list(self):
        """Refresh the port list."""
        self.set_busy(True)
        self.status_label.setText("Refreshing port list...")
        self.command_manager.list_ports()
    
    @pyqtSlot()
    def show_new_port_dialog(self):
        """Show dialog for creating new port pair."""
        dialog = NewPortDialog(self)
        dialog.create_port_pair.connect(self.create_port_pair)
        dialog.exec()
    
    @pyqtSlot()
    def remove_selected_port_pair(self):
        """Remove the currently selected port pair."""
        selected_pair = self.port_tree.get_selected_port_pair()
        if not selected_pair:
            self.show_error_message("No port pair selected for removal.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Removal",
            f"Are you sure you want to remove port pair {selected_pair.number}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.set_busy(True)
            self.status_label.setText(f"Removing port pair {selected_pair.number}...")
            self.command_manager.remove_port_pair(selected_pair.number)
    
    @pyqtSlot()
    def configure_selected_port(self):
        """Configure the currently selected port."""
        selected_port = self.port_tree.get_selected_port()
        if selected_port:
            dialog = ConfigurePortDialog(selected_port, self)
            dialog.apply_configuration.connect(self.apply_port_configuration)
            dialog.exec()
        else:
            self.show_error_message("No port selected for configuration.")
    
    @pyqtSlot(PortPair)
    def on_port_pair_selected(self, pair: PortPair):
        """Handle port pair selection."""
        self.current_selection = ("pair", pair)
        self.ribbon_toolbar.update_selection("pair", pair)
        self.properties_panel.show_port_pair_properties(pair)
    
    @pyqtSlot(Port)
    def on_port_selected(self, port: Port):
        """Handle individual port selection."""
        self.current_selection = ("port", port)
        self.ribbon_toolbar.update_selection("port", port)
        self.properties_panel.show_port_properties(port)
    
    @pyqtSlot(PortPair)
    def on_port_pair_double_clicked(self, pair: PortPair):
        """Handle port pair double click."""
        from .dialogs.configure_dialog import ConfigurePortDialog
        dialog = ConfigurePortDialog(pair.port_a, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Apply configuration changes to port A
            parameters = dialog.get_parameters()
            self.apply_port_changes(pair.port_a.identifier, parameters)
    
    @pyqtSlot(str, object)
    @pyqtSlot(object, object)
    def show_context_menu(self, item_type: str, item_data: object):
        """Show context menu for tree items."""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        menu = QMenu(self)
        
        if item_type == "pair":
            # Port pair context menu
            configure_action = QAction("Configure", self)
            configure_action.triggered.connect(lambda: self.on_port_pair_double_clicked(item_data))
            menu.addAction(configure_action)
            
            remove_action = QAction("Remove Pair", self)
            remove_action.triggered.connect(lambda: self.command_manager.remove_port_pair(item_data.number))
            menu.addAction(remove_action)
            
            menu.addSeparator()
            
            refresh_action = QAction("Refresh", self)
            refresh_action.triggered.connect(self.command_manager.refresh_port_list)
            menu.addAction(refresh_action)
            
        elif item_type == "port":
            # Individual port context menu
            configure_action = QAction("Configure", self)
            configure_action.triggered.connect(lambda: self.show_configure_port_dialog(item_data))
            menu.addAction(configure_action)
            
            menu.addSeparator()
            
            copy_id_action = QAction("Copy Port ID", self)
            copy_id_action.triggered.connect(lambda: self.copy_to_clipboard(item_data.identifier))
            menu.addAction(copy_id_action)
            
            if item_data.port_name:
                copy_name_action = QAction("Copy Port Name", self)
                copy_name_action.triggered.connect(lambda: self.copy_to_clipboard(item_data.port_name))
                menu.addAction(copy_name_action)
        
        # Show menu at cursor position
        menu.exec(self.cursor().pos())
    
    @pyqtSlot(str, dict)
    def apply_port_changes(self, port_id: str, parameters: dict):
        """Apply port configuration changes."""
        if not parameters:
            self.show_error_message("No changes to apply.")
            return
        
        # Convert parameters to setupc format
        param_pairs = []
        for key, value in parameters.items():
            if value is not None and value != "":
                param_pairs.append(f"{key}={value}")
        
        param_string = ",".join(param_pairs) if param_pairs else "-"
        
        self.set_busy(True)
        self.status_label.setText(f"Applying changes to {port_id}...")
        self.command_manager.change_port_config(port_id, param_string)
    
    @pyqtSlot(object, str, str)
    def create_port_pair(self, pair_number, params_a, params_b):
        """Create a new port pair from dialog."""
        self.set_busy(True)
        if pair_number is not None:
            self.status_label.setText(f"Creating port pair {pair_number}...")
        else:
            self.status_label.setText("Creating new port pair...")
        self.command_manager.install_port_pair(pair_number, params_a, params_b)
    
    @pyqtSlot(str, dict)
    def apply_port_configuration(self, port_id, parameters):
        """Apply port configuration from dialog."""
        if not parameters:
            self.show_error_message("No changes to apply.")
            return
        
        # Convert parameters to setupc format
        param_pairs = []
        for key, value in parameters.items():
            if value is not None and value != "":
                param_pairs.append(f"{key}={value}")
        
        param_string = ",".join(param_pairs) if param_pairs else "-"
        
        self.set_busy(True)
        self.status_label.setText(f"Configuring {port_id}...")
        self.command_manager.change_port_config(port_id, param_string)
    
    def show_driver_operations_dialog(self):
        """Show driver operations dialog."""
        dialog = DriverOperationsDialog(self)
        
        # Connect dialog signals to command manager
        dialog.preinstall_requested.connect(self.command_manager.preinstall_driver)
        dialog.update_requested.connect(self.command_manager.update_driver)
        dialog.reload_requested.connect(self.command_manager.reload_driver)
        dialog.uninstall_requested.connect(self.command_manager.uninstall_driver)
        dialog.refresh_status_requested.connect(self._handle_driver_dialog_refresh)
        
        # Connect command manager signals to dialog
        self.command_manager.command_completed.connect(dialog.on_operation_completed)
        self.command_manager.driver_status_changed.connect(dialog.update_driver_status)
        
        # Get initial status only if no command is running
        if not self.command_manager.is_busy():
            self.command_manager.get_driver_status()
        
        dialog.exec()
    
    @pyqtSlot()
    def _handle_driver_dialog_refresh(self):
        """Handle driver dialog refresh request with busy check."""
        if not self.command_manager.is_busy():
            self.command_manager.get_driver_status()
    
    def apply_saved_geometry(self):
        """Apply saved window geometry."""
        geometry = self.config_manager.get_window_geometry()
        self.setGeometry(
            geometry['x'],
            geometry['y'],
            geometry['width'],
            geometry['height']
        )
    
    def save_window_geometry(self):
        """Save current window geometry."""
        geometry = self.geometry()
        self.config_manager.update_window_geometry(
            geometry.x(),
            geometry.y(),
            geometry.width(),
            geometry.height()
        )
    
    @pyqtSlot(list)
    def on_port_list_updated(self, port_pairs: list):
        """Handle port list update."""
        self.port_tree.update_port_pairs(port_pairs)
        count = len(port_pairs)
        self.status_label.setText(f"Ready - {count} port pair{'s' if count != 1 else ''}")
        self.set_busy(False)
    
    @pyqtSlot(list)
    def _on_initial_port_list_loaded(self, port_pairs: list):
        """Handle initial port list load during startup - triggers driver status check."""
        # Now that port list is loaded, check driver status
        self.command_manager.get_driver_status()
    
    @pyqtSlot(CommandResult)
    def on_command_completed(self, result: CommandResult):
        """Handle command completion."""
        if result.success:
            self.status_label.setText("Command completed successfully")
        else:
            self.status_label.setText("Command failed")
        self.set_busy(False)
    
    @pyqtSlot(DriverInfo)
    def on_driver_status_changed(self, driver_info: DriverInfo):
        """Handle driver status change."""
        if driver_info.status == DriverStatus.INSTALLED:
            status_text = "Driver: Installed"
        else:
            status_text = "Driver: Not Installed"
        self.driver_status_label.setText(status_text)
    
    @pyqtSlot(str)
    def show_error_message(self, message: str):
        """Show error message to user."""
        QMessageBox.critical(self, "Error", message)
        self.status_label.setText("Error occurred")
        self.set_busy(False)
    
    def show_info_message(self, title: str, message: str):
        """Show information message to user."""
        QMessageBox.information(self, title, message)
    
    def show_help_dialog(self):
        """Show help dialog with technical documentation."""
        HelpDialog.show_help(self)
    
    def show_about_dialog(self):
        """Show about dialog."""
        AboutDialog.show_about(self)
    
    def copy_to_clipboard(self, text: str):
        """Copy text to system clipboard."""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.status_label.setText(f"Copied '{text}' to clipboard")
    
    def show_configure_port_dialog(self, port):
        """Show port configuration dialog."""
        dialog = ConfigurePortDialog(port, self)
        dialog.apply_configuration.connect(self.apply_port_configuration)
        dialog.exec()
    
    def show_check_busy_names_dialog(self):
        """Show dialog to check busy names with a pattern."""
        from PyQt6.QtWidgets import QInputDialog
        pattern, ok = QInputDialog.getText(
            self,
            "Check Busy Names",
            "Enter pattern to check (e.g., 'COM?*'):",
            text="COM?*"
        )
        if ok and pattern.strip():
            self.command_manager.check_busy_names(pattern.strip())
    
    # Driver operations
    @pyqtSlot()
    def preinstall_driver(self):
        """Preinstall the driver."""
        reply = QMessageBox.question(
            self,
            "Preinstall Driver",
            "This will preinstall the com0com driver. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.set_busy(True)
            self.status_label.setText("Preinstalling driver...")
            self.command_manager.preinstall_driver()
    
    @pyqtSlot()
    def update_driver(self):
        """Update the driver."""
        reply = QMessageBox.question(
            self,
            "Update Driver",
            "This will update the com0com driver. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.set_busy(True)
            self.status_label.setText("Updating driver...")
            self.command_manager.update_driver()
    
    @pyqtSlot()
    def reload_driver(self):
        """Reload the driver."""
        self.set_busy(True)
        self.status_label.setText("Reloading driver...")
        self.command_manager.reload_driver()
    
    @pyqtSlot()
    def uninstall_driver(self):
        """Uninstall the driver."""
        reply = QMessageBox.question(
            self,
            "Uninstall Driver",
            "This will uninstall all ports and the com0com driver. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.set_busy(True)
            self.status_label.setText("Uninstalling driver...")
            self.command_manager.uninstall_driver()
    
    @pyqtSlot()
    def enable_all_ports(self):
        """Enable all ports."""
        self.set_busy(True)
        self.status_label.setText("Enabling all ports...")
        self.command_manager.enable_all_ports()
    
    @pyqtSlot()
    def disable_all_ports(self):
        """Disable all ports."""
        self.set_busy(True)
        self.status_label.setText("Disabling all ports...")
        self.command_manager.disable_all_ports()
    
    def set_busy(self, busy: bool):
        """Set the application busy state."""
        # Update UI elements
        self.ribbon_toolbar.set_busy(busy)
        self.progress_bar.setVisible(busy)
        
        if busy:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        else:
            QApplication.restoreOverrideCursor()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_F1:
            # F1 opens help dialog
            self.show_help_dialog()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save window geometry
        self.save_window_geometry()
        
        # Cancel any running commands
        if self.command_manager.is_busy():
            self.command_manager.cancel_current_command()
        
        event.accept()