"""Setup wizard dialog for first-time users."""

import os
import subprocess
from typing import Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QStackedWidget, QWidget, QTextEdit,
                            QProgressBar, QCheckBox, QLineEdit, QFileDialog,
                            QMessageBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

from ...core.models import DriverInfo
from ...utils.constants import SETUPC_PATHS, APP_NAME


class SetupWizardWorker(QThread):
    """Worker thread for setup operations."""
    
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, operation, setupc_path=None):
        super().__init__()
        self.operation = operation
        self.setupc_path = setupc_path
    
    def run(self):
        """Run setup operation."""
        try:
            if self.operation == "detect_driver":
                self._detect_driver()
            elif self.operation == "test_setupc":
                self._test_setupc()
            else:
                self.finished.emit(False, f"Unknown operation: {self.operation}")
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def _detect_driver(self):
        """Detect com0com driver installation."""
        self.progress_updated.emit(25, "Checking Windows drivers...")
        
        # Check for com0com driver in Windows
        try:
            result = subprocess.run([
                "driverquery", "/FO", "CSV"
            ], capture_output=True, text=True, timeout=10)
            
            self.progress_updated.emit(50, "Analyzing driver list...")
            
            if "com0com" in result.stdout.lower():
                self.progress_updated.emit(75, "com0com driver found!")
                self.progress_updated.emit(100, "Driver detection complete")
                self.finished.emit(True, "com0com driver is installed")
            else:
                self.progress_updated.emit(100, "Driver detection complete")
                self.finished.emit(False, "com0com driver not found")
                
        except subprocess.TimeoutExpired:
            self.finished.emit(False, "Driver detection timed out")
        except Exception as e:
            self.finished.emit(False, f"Driver detection failed: {e}")
    
    def _test_setupc(self):
        """Test setupc.exe functionality."""
        if not self.setupc_path:
            self.finished.emit(False, "No setupc.exe path provided")
            return
        
        self.progress_updated.emit(33, "Testing setupc.exe...")
        
        try:
            # Test basic setupc.exe functionality with working directory set
            working_directory = os.path.dirname(self.setupc_path) if self.setupc_path else None
            result = subprocess.run([
                self.setupc_path, "list"
            ], capture_output=True, text=True, timeout=15, cwd=working_directory)
            
            self.progress_updated.emit(66, "Analyzing setupc.exe response...")
            
            if result.returncode == 0:
                self.progress_updated.emit(100, "setupc.exe test successful")
                self.finished.emit(True, f"setupc.exe is working properly")
            else:
                self.finished.emit(False, f"setupc.exe failed with code {result.returncode}")
                
        except subprocess.TimeoutExpired:
            self.finished.emit(False, "setupc.exe test timed out")
        except FileNotFoundError:
            self.finished.emit(False, "setupc.exe not found at specified path")
        except Exception as e:
            self.finished.emit(False, f"setupc.exe test failed: {e}")


class WizardPage(QWidget):
    """Base class for wizard pages."""
    
    def __init__(self, title: str, description: str):
        super().__init__()
        self.title = title
        self.description = description
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the page UI."""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0078D4; margin-bottom: 10px;")
        
        # Description
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #333; margin-bottom: 20px;")
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        
        # Add page content
        content_widget = self.create_content()
        if content_widget:
            layout.addWidget(content_widget)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def create_content(self) -> Optional[QWidget]:
        """Create page-specific content. Override in subclasses."""
        return None
    
    def validate(self) -> tuple[bool, str]:
        """Validate page input. Override in subclasses."""
        return True, ""
    
    def get_result(self) -> dict:
        """Get page result data. Override in subclasses."""
        return {}


class WelcomePage(WizardPage):
    """Welcome page of the setup wizard."""
    
    def __init__(self):
        super().__init__(
            "Welcome to com0com GUI Manager",
            f"This wizard will help you set up {APP_NAME} and verify your com0com installation."
        )
    
    def create_content(self):
        """Create welcome page content."""
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Welcome message
        welcome_text = QLabel("""
        <b>What this wizard will do:</b>
        <ul>
        <li>Detect your com0com driver installation</li>
        <li>Locate and test setupc.exe</li>
        <li>Verify system requirements</li>
        <li>Configure initial settings</li>
        </ul>
        
        <p><b>Before you begin:</b></p>
        <ul>
        <li>Make sure com0com is installed on your system</li>
        <li>You may need administrator privileges for some operations</li>
        <li>Close any other applications using virtual serial ports</li>
        </ul>
        """)
        welcome_text.setWordWrap(True)
        
        layout.addWidget(welcome_text)
        
        return content


class DriverDetectionPage(WizardPage):
    """Driver detection page."""
    
    def __init__(self):
        super().__init__(
            "Detecting com0com Driver",
            "Checking if the com0com virtual serial port driver is installed on your system."
        )
        self.detection_complete = False
        self.driver_found = False
        self.worker = None
    
    def create_content(self):
        """Create driver detection content."""
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        # Status label
        self.status_label = QLabel("Click 'Start Detection' to begin...")
        self.status_label.setStyleSheet("color: #666;")
        
        # Start button
        self.start_button = QPushButton("Start Detection")
        self.start_button.clicked.connect(self.start_detection)
        
        # Results area
        self.results_area = QTextEdit()
        self.results_area.setMaximumHeight(100)
        self.results_area.setVisible(False)
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.results_area)
        
        return content
    
    def start_detection(self):
        """Start driver detection."""
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting detection...")
        
        # Start worker thread
        self.worker = SetupWizardWorker("detect_driver")
        self.worker.progress_updated.connect(self.on_progress)
        self.worker.finished.connect(self.on_detection_finished)
        self.worker.start()
    
    def on_progress(self, value: int, message: str):
        """Handle progress updates."""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def on_detection_finished(self, success: bool, message: str):
        """Handle detection completion."""
        self.detection_complete = True
        self.driver_found = success
        
        if success:
            self.status_label.setText("✅ " + message)
            self.status_label.setStyleSheet("color: #0D7377;")
        else:
            self.status_label.setText("❌ " + message)
            self.status_label.setStyleSheet("color: #D73027;")
            
            # Show troubleshooting info
            self.results_area.setVisible(True)
            self.results_area.setPlainText(
                "Driver not found. Please check:\n"
                "• com0com is properly installed\n"
                "• Installation was completed with administrator rights\n"
                "• System was restarted after installation\n\n"
                "Download com0com from: https://sourceforge.net/projects/com0com/"
            )
        
        self.start_button.setText("Re-run Detection")
        self.start_button.setEnabled(True)
    
    def validate(self):
        """Validate driver detection."""
        if not self.detection_complete:
            return False, "Please run driver detection first"
        
        if not self.driver_found:
            # Allow to continue even if driver not found, but warn user
            return True, "Warning: Driver not detected, but you can continue"
        
        return True, ""
    
    def get_result(self):
        """Get detection results."""
        return {
            "driver_detected": self.driver_found,
            "detection_complete": self.detection_complete
        }


class SetupcDetectionPage(WizardPage):
    """setupc.exe detection page."""
    
    def __init__(self):
        super().__init__(
            "Locating setupc.exe",
            "Finding the setupc.exe command-line tool used to manage virtual serial ports."
        )
        self.setupc_path = None
        self.test_complete = False
        self.test_successful = False
    
    def create_content(self):
        """Create setupc detection content."""
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Auto-detection results
        self.detection_label = QLabel("Searching for setupc.exe...")
        layout.addWidget(self.detection_label)
        
        # Path input
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Path to setupc.exe")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_setupc)
        
        path_layout.addWidget(QLabel("setupc.exe path:"))
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        layout.addLayout(path_layout)
        
        # Test button and progress
        self.test_button = QPushButton("Test setupc.exe")
        self.test_button.clicked.connect(self.test_setupc)
        self.test_button.setEnabled(False)
        
        self.test_progress = QProgressBar()
        self.test_progress.setVisible(False)
        
        self.test_status = QLabel("")
        
        layout.addWidget(self.test_button)
        layout.addWidget(self.test_progress)
        layout.addWidget(self.test_status)
        
        # Auto-detect on page creation
        QTimer.singleShot(100, self.auto_detect_setupc)
        
        # Connect path input changes
        self.path_input.textChanged.connect(self.on_path_changed)
        
        return content
    
    def auto_detect_setupc(self):
        """Auto-detect setupc.exe in common locations."""
        self.detection_label.setText("🔍 Searching common locations...")
        
        for path in SETUPC_PATHS:
            if os.path.exists(path):
                self.setupc_path = path
                self.path_input.setText(path)
                self.detection_label.setText(f"✅ Found setupc.exe: {path}")
                self.test_button.setEnabled(True)
                return
        
        self.detection_label.setText("❌ setupc.exe not found in common locations")
    
    def browse_setupc(self):
        """Browse for setupc.exe manually."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select setupc.exe",
            "C:\\Program Files",
            "Executable files (*.exe);;All files (*.*)"
        )
        
        if file_path:
            self.path_input.setText(file_path)
    
    def on_path_changed(self, path: str):
        """Handle path input changes."""
        self.setupc_path = path if path.strip() else None
        self.test_button.setEnabled(bool(self.setupc_path))
        self.test_complete = False
        self.test_successful = False
    
    def test_setupc(self):
        """Test setupc.exe functionality."""
        if not self.setupc_path:
            return
        
        self.test_button.setEnabled(False)
        self.test_progress.setVisible(True)
        self.test_progress.setRange(0, 100)
        self.test_progress.setValue(0)
        self.test_status.setText("Testing setupc.exe...")
        
        # Start worker thread
        self.worker = SetupWizardWorker("test_setupc", self.setupc_path)
        self.worker.progress_updated.connect(self.on_test_progress)
        self.worker.finished.connect(self.on_test_finished)
        self.worker.start()
    
    def on_test_progress(self, value: int, message: str):
        """Handle test progress updates."""
        self.test_progress.setValue(value)
        self.test_status.setText(message)
    
    def on_test_finished(self, success: bool, message: str):
        """Handle test completion."""
        self.test_complete = True
        self.test_successful = success
        
        self.test_progress.setVisible(False)
        
        if success:
            self.test_status.setText("✅ " + message)
            self.test_status.setStyleSheet("color: #0D7377;")
        else:
            self.test_status.setText("❌ " + message)
            self.test_status.setStyleSheet("color: #D73027;")
        
        self.test_button.setText("Re-test")
        self.test_button.setEnabled(True)
    
    def validate(self):
        """Validate setupc detection."""
        if not self.setupc_path:
            return False, "Please specify the path to setupc.exe"
        
        if not os.path.exists(self.setupc_path):
            return False, "The specified setupc.exe file does not exist"
        
        if not self.test_complete:
            return False, "Please test setupc.exe functionality first"
        
        if not self.test_successful:
            return False, "setupc.exe test failed. Please check the path and try again"
        
        return True, ""
    
    def get_result(self):
        """Get setupc detection results."""
        return {
            "setupc_path": self.setupc_path,
            "test_successful": self.test_successful
        }


class CompletionPage(WizardPage):
    """Setup completion page."""
    
    def __init__(self):
        super().__init__(
            "Setup Complete",
            "Your com0com GUI Manager is now configured and ready to use."
        )
        self.launch_app = True
    
    def create_content(self):
        """Create completion page content."""
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Success message
        success_label = QLabel("✅ Setup completed successfully!")
        success_label.setStyleSheet("color: #0D7377; font-size: 14px; font-weight: bold;")
        layout.addWidget(success_label)
        
        # Summary
        summary_text = QLabel("""
        <b>What's configured:</b>
        <ul>
        <li>com0com driver detection completed</li>
        <li>setupc.exe path configured</li>
        <li>Application settings saved</li>
        </ul>
        
        <p><b>You can now:</b></p>
        <ul>
        <li>Create virtual serial port pairs</li>
        <li>Configure port parameters</li>
        <li>Manage driver operations</li>
        <li>Monitor port usage</li>
        </ul>
        """)
        summary_text.setWordWrap(True)
        layout.addWidget(summary_text)
        
        # Launch option
        self.launch_checkbox = QCheckBox("Launch com0com GUI Manager now")
        self.launch_checkbox.setChecked(True)
        self.launch_checkbox.toggled.connect(self.on_launch_toggled)
        layout.addWidget(self.launch_checkbox)
        
        return content
    
    def on_launch_toggled(self, checked: bool):
        """Handle launch checkbox toggle."""
        self.launch_app = checked
    
    def get_result(self):
        """Get completion results."""
        return {
            "launch_app": self.launch_app
        }


class SetupWizardDialog(QDialog):
    """Main setup wizard dialog."""
    
    setup_completed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.results = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the wizard UI."""
        self.setWindowTitle(f"{APP_NAME} - Setup Wizard")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Page stack
        self.page_stack = QStackedWidget()
        
        # Create pages
        self.pages = [
            WelcomePage(),
            DriverDetectionPage(),
            SetupcDetectionPage(),
            CompletionPage()
        ]
        
        for page in self.pages:
            self.page_stack.addWidget(page)
        
        layout.addWidget(self.page_stack)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        
        self.back_button = QPushButton("< Back")
        self.back_button.clicked.connect(self.previous_page)
        self.back_button.setEnabled(False)
        
        self.next_button = QPushButton("Next >")
        self.next_button.clicked.connect(self.next_page)
        
        self.finish_button = QPushButton("Finish")
        self.finish_button.clicked.connect(self.finish_wizard)
        self.finish_button.setVisible(False)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.finish_button)
        nav_layout.addWidget(self.cancel_button)
        
        layout.addLayout(nav_layout)
        self.setLayout(layout)
        
        # Set current page
        self.current_page_index = 0
        self.update_navigation()
    
    def create_header(self):
        """Create wizard header."""
        header = QFrame()
        header.setFrameStyle(QFrame.Shape.Box)
        header.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 0px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # Icon (if available)
        # icon_label = QLabel()
        # icon_pixmap = QPixmap("assets/icons/app_icon.svg").scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio)
        # icon_label.setPixmap(icon_pixmap)
        # layout.addWidget(icon_label)
        
        # Title and description
        text_layout = QVBoxLayout()
        
        title_label = QLabel(f"{APP_NAME} Setup Wizard")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        desc_label = QLabel("Configure your virtual serial port manager")
        desc_label.setStyleSheet("color: #666;")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return header
    
    def previous_page(self):
        """Go to previous page."""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.page_stack.setCurrentIndex(self.current_page_index)
            self.update_navigation()
    
    def next_page(self):
        """Go to next page."""
        # Validate current page
        current_page = self.pages[self.current_page_index]
        valid, message = current_page.validate()
        
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return
        
        # Store page results
        self.results.update(current_page.get_result())
        
        # Move to next page
        if self.current_page_index < len(self.pages) - 1:
            self.current_page_index += 1
            self.page_stack.setCurrentIndex(self.current_page_index)
            self.update_navigation()
    
    def update_navigation(self):
        """Update navigation button states."""
        self.back_button.setEnabled(self.current_page_index > 0)
        
        is_last_page = self.current_page_index == len(self.pages) - 1
        self.next_button.setVisible(not is_last_page)
        self.finish_button.setVisible(is_last_page)
    
    def finish_wizard(self):
        """Finish the wizard."""
        # Get final page results
        current_page = self.pages[self.current_page_index]
        self.results.update(current_page.get_result())
        
        # Emit completion signal
        self.setup_completed.emit(self.results)
        
        # Close dialog
        self.accept()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication([])
    
    wizard = SetupWizardDialog()
    wizard.setup_completed.connect(lambda results: print("Setup results:", results))
    wizard.show()
    
    app.exec()