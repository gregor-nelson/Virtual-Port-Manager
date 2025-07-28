"""Dialog for driver operations and status."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QPushButton, QGroupBox, QMessageBox, 
                            QTextEdit, QProgressBar, QDialogButtonBox, QFrame,
                            QScrollArea, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from ...core.models import DriverInfo, DriverStatus, CommandResult


class DriverOperationsDialog(QDialog):
    """Dialog for driver operations and status display."""
    
    # Signals for driver operations
    preinstall_requested = pyqtSignal()
    update_requested = pyqtSignal()
    reload_requested = pyqtSignal()
    uninstall_requested = pyqtSignal()
    refresh_status_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_driver_info = None
        
        self.setWindowTitle("Driver Operations")
        self.setModal(True)
        self.resize(500, 600)
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("com0com Driver Operations")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Manage the com0com virtual serial port driver installation and status.")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Create scroll area for main content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Content widget for scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # Current status group
        self.status_group = QGroupBox("Current Status")
        status_layout = QFormLayout(self.status_group)
        
        self.status_label = QLabel("Unknown")
        status_layout.addRow("Driver Status:", self.status_label)
        
        self.version_label = QLabel("Unknown")
        status_layout.addRow("Version:", self.version_label)
        
        self.path_label = QLabel("Unknown")
        self.path_label.setWordWrap(True)
        status_layout.addRow("Installation Path:", self.path_label)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Status")
        refresh_layout.addWidget(self.refresh_button)
        refresh_layout.addStretch()
        
        status_layout.addRow("", refresh_layout)
        
        content_layout.addWidget(self.status_group)
        
        # Operations group
        ops_group = QGroupBox("Driver Operations")
        ops_layout = QVBoxLayout(ops_group)
        
        # Operation buttons with descriptions
        self.create_operation_button(
            ops_layout,
            "Preinstall Driver",
            "Install the driver without creating any port pairs. "
            "This prepares the system for com0com usage.",
            self.preinstall_requested
        )
        
        self.create_operation_button(
            ops_layout,
            "Update Driver",
            "Update the driver installation to the latest version.",
            self.update_requested
        )
        
        self.create_operation_button(
            ops_layout,
            "Reload Driver",
            "Reload the driver and refresh all port configurations. "
            "This can resolve some connectivity issues.",
            self.reload_requested
        )
        
        self.create_operation_button(
            ops_layout,
            "Uninstall Driver",
            "Remove all virtual ports and uninstall the driver completely. "
            "This action cannot be undone.",
            self.uninstall_requested,
            warning=True
        )
        
        content_layout.addWidget(ops_group)
        
        # Progress and log area
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        content_layout.addWidget(self.progress_bar)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setPlaceholderText("Operation results will appear here...")
        self.log_text.setVisible(False)
        content_layout.addWidget(self.log_text)
        
        # Add stretch to push content to top
        content_layout.addStretch()
        
        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Dialog buttons (fixed at bottom)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        layout.addWidget(button_box)
        
        # Connect button signals
        button_box.rejected.connect(self.reject)
    
    def create_operation_button(self, layout, title, description, signal, warning=False):
        """Create an operation button with description."""
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        
        # Button
        button = QPushButton(title)
        if warning:
            pass
        button.clicked.connect(signal.emit)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        
        frame_layout.addWidget(button)
        frame_layout.addWidget(desc_label)
        
        # Add to layout
        layout.addWidget(frame)
        
        # Store button reference for enabling/disabling
        if title == "Preinstall Driver":
            self.preinstall_button = button
        elif title == "Update Driver":
            self.update_button = button
        elif title == "Reload Driver":
            self.reload_button = button
        elif title == "Uninstall Driver":
            self.uninstall_button = button
    
    def setup_connections(self):
        """Set up signal connections."""
        self.refresh_button.clicked.connect(self.refresh_status_requested.emit)
        
        # Connect operation signals with confirmation dialogs
        self.preinstall_requested.connect(self.confirm_preinstall)
        self.update_requested.connect(self.confirm_update)
        self.reload_requested.connect(self.confirm_reload)
        self.uninstall_requested.connect(self.confirm_uninstall)
    
    @pyqtSlot(DriverInfo)
    def update_driver_status(self, driver_info: DriverInfo):
        """Update the driver status display."""
        self.current_driver_info = driver_info
        
        # Update status labels
        self.status_label.setText(driver_info.status.value)
        self.version_label.setText(driver_info.version or "Unknown")
        self.path_label.setText(driver_info.install_path or "Unknown")
        
        # Update status label styling
        if driver_info.status == DriverStatus.INSTALLED:
            pass
        elif driver_info.status == DriverStatus.NOT_INSTALLED:
            pass
        elif driver_info.status == DriverStatus.ERROR:
            pass
        else:
            pass
        
        # Enable/disable buttons based on status
        self.update_button_states(driver_info.status)
        
        # Show error message if present
        if driver_info.error_message:
            self.show_log(f"Error: {driver_info.error_message}")
    
    def update_button_states(self, status: DriverStatus):
        """Update button enabled states based on driver status."""
        if status == DriverStatus.INSTALLED:
            self.preinstall_button.setEnabled(False)
            self.update_button.setEnabled(True)
            self.reload_button.setEnabled(True)
            self.uninstall_button.setEnabled(True)
        elif status == DriverStatus.NOT_INSTALLED:
            self.preinstall_button.setEnabled(True)
            self.update_button.setEnabled(False)
            self.reload_button.setEnabled(False)
            self.uninstall_button.setEnabled(False)
        else:  # ERROR or NEEDS_UPDATE
            self.preinstall_button.setEnabled(True)
            self.update_button.setEnabled(True)
            self.reload_button.setEnabled(True)
            self.uninstall_button.setEnabled(True)
    
    def show_progress(self, show: bool):
        """Show or hide the progress bar."""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)  # Indeterminate
    
    def show_log(self, message: str):
        """Show a message in the log area."""
        self.log_text.setVisible(True)
        self.log_text.append(message)
    
    def clear_log(self):
        """Clear the log area."""
        self.log_text.clear()
        self.log_text.setVisible(False)
    
    def set_busy(self, busy: bool):
        """Set the dialog busy state."""
        # Disable all operation buttons
        self.preinstall_button.setEnabled(not busy)
        self.update_button.setEnabled(not busy)
        self.reload_button.setEnabled(not busy)
        self.uninstall_button.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        
        self.show_progress(busy)
        
        if not busy and self.current_driver_info:
            self.update_button_states(self.current_driver_info.status)
    
    @pyqtSlot(CommandResult)
    def on_operation_completed(self, result: CommandResult):
        """Handle operation completion."""
        self.set_busy(False)
        
        if result.success:
            self.show_log(f"✓ Operation completed successfully")
            if result.output:
                self.show_log(f"Output: {result.output}")
        else:
            self.show_log(f"✗ Operation failed: {result.get_error_message()}")
        
        # Status will be updated automatically when the command completes
        # No need to explicitly request refresh here
    
    # Confirmation dialogs for operations
    def confirm_preinstall(self):
        """Confirm preinstall operation."""
        reply = QMessageBox.question(
            self,
            "Confirm Preinstall",
            "This will preinstall the com0com driver on your system. "
            "Administrator privileges may be required.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.set_busy(True)
            self.clear_log()
            self.show_log("Preinstalling driver...")
            # The actual signal was already emitted, this is just the confirmation
    
    def confirm_update(self):
        """Confirm update operation."""
        reply = QMessageBox.question(
            self,
            "Confirm Update",
            "This will update the com0com driver to the latest version. "
            "Administrator privileges may be required.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.set_busy(True)
            self.clear_log()
            self.show_log("Updating driver...")
    
    def confirm_reload(self):
        """Confirm reload operation."""
        reply = QMessageBox.question(
            self,
            "Confirm Reload",
            "This will reload the com0com driver and refresh all port configurations. "
            "Existing connections may be temporarily interrupted.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.set_busy(True)
            self.clear_log()
            self.show_log("Reloading driver...")
    
    def confirm_uninstall(self):
        """Confirm uninstall operation."""
        reply = QMessageBox.warning(
            self,
            "Confirm Uninstall",
            "⚠️ WARNING ⚠️\n\n"
            "This will REMOVE ALL virtual port pairs and completely uninstall "
            "the com0com driver from your system.\n\n"
            "This action cannot be undone. All virtual ports will be deleted.\n\n"
            "Are you absolutely sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Double confirmation for destructive action
            final_reply = QMessageBox.warning(
                self,
                "Final Confirmation",
                "This is your final warning.\n\n"
                "Clicking 'Yes' will permanently remove all com0com components.\n\n"
                "Proceed with uninstallation?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if final_reply == QMessageBox.StandardButton.Yes:
                self.set_busy(True)
                self.clear_log()
                self.show_log("Uninstalling driver...")