"""Enhanced error handling and user guidance system."""

import os
import sys
import traceback
import logging
from typing import Optional, Dict, Any
from enum import Enum
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from .constants import APP_NAME


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better handling."""
    DRIVER = "driver"
    SETUPC = "setupc"
    PERMISSION = "permission"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    GUI = "gui"
    SYSTEM = "system"
    VALIDATION = "validation"


class ErrorSolution:
    """Represents a solution to an error."""
    
    def __init__(self, title: str, description: str, action: str = None, url: str = None):
        self.title = title
        self.description = description
        self.action = action  # Action button text
        self.url = url       # URL to open for more info


class ErrorInfo:
    """Comprehensive error information."""
    
    def __init__(self, 
                 category: ErrorCategory,
                 severity: ErrorSeverity,
                 title: str,
                 message: str,
                 technical_details: str = None,
                 solutions: list[ErrorSolution] = None):
        self.category = category
        self.severity = severity
        self.title = title
        self.message = message
        self.technical_details = technical_details or ""
        self.solutions = solutions or []


class ErrorHandler:
    """Enhanced error handler with user-friendly messages and solutions."""
    
    # Error patterns and their friendly messages
    ERROR_PATTERNS = {
        # Driver-related errors
        "access denied": ErrorInfo(
            ErrorCategory.PERMISSION,
            ErrorSeverity.ERROR,
            "Permission Denied",
            "The application doesn't have permission to perform this operation.",
            solutions=[
                ErrorSolution(
                    "Run as Administrator",
                    "Right-click the application and select 'Run as administrator'",
                    "Restart as Admin"
                ),
                ErrorSolution(
                    "Check User Account Control",
                    "Disable UAC temporarily or add the application to trusted programs"
                )
            ]
        ),
        
        "setupc.exe": ErrorInfo(
            ErrorCategory.SETUPC,
            ErrorSeverity.ERROR,
            "setupc.exe Not Found",
            "The setupc.exe command-line tool could not be found or executed.",
            solutions=[
                ErrorSolution(
                    "Install com0com",
                    "Download and install com0com from the official website",
                    "Download com0com",
                    "https://sourceforge.net/projects/com0com/"
                ),
                ErrorSolution(
                    "Specify Path Manually",
                    "Use Tools > Settings to specify the correct path to setupc.exe",
                    "Open Settings"
                ),
                ErrorSolution(
                    "Check Installation",
                    "Verify com0com was installed correctly and restart the computer"
                )
            ]
        ),
        
        "port.*already.*exists": ErrorInfo(
            ErrorCategory.VALIDATION,
            ErrorSeverity.WARNING,
            "Port Already Exists",
            "The specified port number or name is already in use.",
            solutions=[
                ErrorSolution(
                    "Use Different Port",
                    "Try a different port number or let the system auto-assign one"
                ),
                ErrorSolution(
                    "Remove Existing Port",
                    "Remove the existing port pair if it's no longer needed",
                    "Remove Port"
                )
            ]
        ),
        
        "driver.*not.*installed": ErrorInfo(
            ErrorCategory.DRIVER,
            ErrorSeverity.CRITICAL,
            "Driver Not Installed",
            "The com0com virtual serial port driver is not installed on this system.",
            solutions=[
                ErrorSolution(
                    "Install Driver",
                    "Download and install the com0com driver package",
                    "Download Driver",
                    "https://sourceforge.net/projects/com0com/"
                ),
                ErrorSolution(
                    "Run Setup Wizard",
                    "Use the setup wizard to detect and configure the driver",
                    "Run Wizard"
                )
            ]
        ),
        
        "timeout": ErrorInfo(
            ErrorCategory.SYSTEM,
            ErrorSeverity.WARNING,
            "Operation Timed Out",
            "The operation took too long to complete and was cancelled.",
            solutions=[
                ErrorSolution(
                    "Increase Timeout",
                    "Go to Tools > Settings and increase the command timeout value",
                    "Open Settings"
                ),
                ErrorSolution(
                    "Check System Load",
                    "Close other applications and try again when system is less busy"
                ),
                ErrorSolution(
                    "Restart Service",
                    "Restart the Windows Device Manager or reboot the system"
                )
            ]
        ),
        
        "invalid.*parameter": ErrorInfo(
            ErrorCategory.VALIDATION,
            ErrorSeverity.ERROR,
            "Invalid Parameter",
            "One or more parameters have invalid values.",
            solutions=[
                ErrorSolution(
                    "Check Parameter Format",
                    "Verify that parameters follow the correct format (e.g., PortName=COM8)"
                ),
                ErrorSolution(
                    "Use Valid Values",
                    "Ensure boolean values are 'yes' or 'no', and port names start with 'COM'"
                ),
                ErrorSolution(
                    "Reset to Defaults",
                    "Use default parameter values and modify only what's necessary",
                    "Reset Parameters"
                )
            ]
        ),
        
        "busy": ErrorInfo(
            ErrorCategory.SYSTEM,
            ErrorSeverity.WARNING,
            "Port Busy",
            "The port is currently in use by another application.",
            solutions=[
                ErrorSolution(
                    "Close Applications",
                    "Close any applications that might be using virtual serial ports"
                ),
                ErrorSolution(
                    "Check Process List",
                    "Use Task Manager to find and close applications using the port",
                    "Open Task Manager"
                ),
                ErrorSolution(
                    "Wait and Retry",
                    "Wait a moment and try the operation again"
                )
            ]
        )
    }
    
    @classmethod
    def get_error_info(cls, error_text: str) -> ErrorInfo:
        """Get comprehensive error information from error text."""
        error_text_lower = error_text.lower()
        
        # Check for known error patterns
        for pattern, error_info in cls.ERROR_PATTERNS.items():
            if pattern in error_text_lower:
                return error_info
        
        # Default error info for unknown errors
        return ErrorInfo(
            ErrorCategory.SYSTEM,
            ErrorSeverity.ERROR,
            "Unexpected Error",
            "An unexpected error occurred.",
            error_text,
            [
                ErrorSolution(
                    "Check Logs",
                    "Check the application logs for more detailed information",
                    "View Logs"
                ),
                ErrorSolution(
                    "Restart Application",
                    "Try restarting the application to resolve temporary issues"
                ),
                ErrorSolution(
                    "Contact Support",
                    "If the problem persists, contact support with error details",
                    "Report Issue",
                    "https://github.com/com0com/com0com/issues"
                )
            ]
        )
    
    @classmethod
    def show_error_dialog(cls, parent, error_text: str, title: str = None) -> bool:
        """Show enhanced error dialog with solutions."""
        error_info = cls.get_error_info(error_text)
        
        dialog = EnhancedErrorDialog(parent, error_info, title)
        return dialog.exec() == QDialog.DialogCode.Accepted
    
    @classmethod
    def show_setupc_not_found_dialog(cls, parent) -> str:
        """Show specialized dialog for setupc.exe not found."""
        dialog = SetupcNotFoundDialog(parent)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            return dialog.get_selected_path()
        return ""


class EnhancedErrorDialog(QDialog):
    """Enhanced error dialog with solutions and actions."""
    
    action_requested = pyqtSignal(str)
    
    def __init__(self, parent, error_info: ErrorInfo, title: str = None):
        super().__init__(parent)
        self.error_info = error_info
        self.setup_ui(title)
    
    def setup_ui(self, title: str):
        """Set up the error dialog UI."""
        self.setWindowTitle(title or f"{APP_NAME} - {self.error_info.title}")
        self.setMinimumSize(500, 300)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        # Error icon based on severity
        icon_label = QLabel()
        if self.error_info.severity == ErrorSeverity.CRITICAL:
            icon_label.setText("🚨")
        elif self.error_info.severity == ErrorSeverity.ERROR:
            icon_label.setText("❌")
        elif self.error_info.severity == ErrorSeverity.WARNING:
            icon_label.setText("⚠️")
        else:
            icon_label.setText("ℹ️")
        
        header_layout.addWidget(icon_label)
        
        # Title and message
        text_layout = QVBoxLayout()
        
        title_label = QLabel(self.error_info.title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        message_label = QLabel(self.error_info.message)
        message_label.setWordWrap(True)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(message_label)
        
        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Solutions section
        if self.error_info.solutions:
            solutions_label = QLabel("💡 Suggested Solutions:")
            layout.addWidget(solutions_label)
            
            for i, solution in enumerate(self.error_info.solutions):
                solution_widget = self.create_solution_widget(solution, i)
                layout.addWidget(solution_widget)
        
        # Technical details (collapsible)
        if self.error_info.technical_details:
            details_layout = QVBoxLayout()
            
            details_button = QPushButton("Show Technical Details")
            details_button.setCheckable(True)
            details_button.toggled.connect(self.toggle_details)
            
            self.details_text = QTextEdit()
            self.details_text.setPlainText(self.error_info.technical_details)
            self.details_text.setMaximumHeight(100)
            self.details_text.setVisible(False)
            
            details_layout.addWidget(details_button)
            details_layout.addWidget(self.details_text)
            
            layout.addLayout(details_layout)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_solution_widget(self, solution: ErrorSolution, index: int) -> QWidget:
        """Create a widget for a solution."""
        widget = QWidget()
        
        layout = QHBoxLayout(widget)
        
        # Solution text
        text_layout = QVBoxLayout()
        
        title_label = QLabel(f"{index + 1}. {solution.title}")
        
        desc_label = QLabel(solution.description)
        desc_label.setWordWrap(True)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout)
        
        # Action button
        if solution.action:
            action_button = QPushButton(solution.action)
            action_button.clicked.connect(lambda: self.execute_solution_action(solution))
            action_button.setMaximumWidth(120)
            layout.addWidget(action_button)
        
        return widget
    
    def execute_solution_action(self, solution: ErrorSolution):
        """Execute a solution action."""
        if solution.url:
            # Open URL
            import webbrowser
            webbrowser.open(solution.url)
        elif solution.action:
            # Emit action signal
            self.action_requested.emit(solution.action)
    
    def toggle_details(self, visible: bool):
        """Toggle technical details visibility."""
        self.details_text.setVisible(visible)
        
        # Adjust dialog size
        if visible:
            self.resize(self.width(), self.height() + 100)
        else:
            self.resize(self.width(), max(300, self.height() - 100))


class SetupcNotFoundDialog(QDialog):
    """Specialized dialog for setupc.exe not found."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_path = ""
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(f"{APP_NAME} - setupc.exe Not Found")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        icon_label = QLabel("🔧")
        
        text_layout = QVBoxLayout()
        title_label = QLabel("setupc.exe Not Found")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        desc_label = QLabel("The setupc.exe command-line tool is required to manage virtual serial ports.")
        desc_label.setWordWrap(True)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Options
        options_label = QLabel("Please choose an option:")
        layout.addWidget(options_label)
        
        # Option 1: Download com0com
        download_button = QPushButton("📥 Download and Install com0com")
        download_button.clicked.connect(self.download_com0com)
        layout.addWidget(download_button)
        
        # Option 2: Browse for setupc.exe
        browse_button = QPushButton("📁 Browse for Existing setupc.exe")
        browse_button.clicked.connect(self.browse_setupc)
        layout.addWidget(browse_button)
        
        # Option 3: Run setup wizard
        wizard_button = QPushButton("🧙‍♂️ Run Setup Wizard")
        wizard_button.clicked.connect(self.run_wizard)
        layout.addWidget(wizard_button)
        
        # Information text
        info_text = QLabel("""
        <b>About com0com:</b><br>
        com0com is a free Windows virtual serial port driver that creates pairs of virtual COM ports. 
        This application provides a graphical interface for managing these virtual ports.
        
        <br><br><b>System Requirements:</b>
        <ul>
        <li>Windows 10/11 (32-bit or 64-bit)</li>
        <li>Administrator privileges for installation</li>
        <li>Compatible with most serial port applications</li>
        </ul>
        """)
        info_text.setWordWrap(True)
        layout.addWidget(info_text)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def download_com0com(self):
        """Open com0com download page."""
        import webbrowser
        webbrowser.open("https://sourceforge.net/projects/com0com/")
        self.reject()
    
    def browse_setupc(self):
        """Browse for setupc.exe file."""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select setupc.exe",
            "C:\\Program Files",
            "Executable files (*.exe);;All files (*.*)"
        )
        
        if file_path:
            self.selected_path = file_path
            self.accept()
    
    def run_wizard(self):
        """Run setup wizard."""
        # This would trigger the setup wizard
        self.selected_path = "WIZARD"
        self.accept()
    
    def get_selected_path(self) -> str:
        """Get the selected setupc.exe path."""
        return self.selected_path


# Configure logging for error tracking
def setup_error_logging():
    """Set up error logging configuration."""
    log_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", APP_NAME, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "error.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(APP_NAME)


# Global error logger
error_logger = setup_error_logging()


def log_error(error: Exception, context: str = ""):
    """Log an error with context information."""
    error_msg = f"{context}: {str(error)}" if context else str(error)
    error_logger.error(error_msg, exc_info=True)


def log_warning(message: str, context: str = ""):
    """Log a warning message."""
    warning_msg = f"{context}: {message}" if context else message
    error_logger.warning(warning_msg)


def log_info(message: str, context: str = ""):
    """Log an info message."""
    info_msg = f"{context}: {message}" if context else message
    error_logger.info(info_msg)