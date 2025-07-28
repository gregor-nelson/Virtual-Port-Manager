"""Command output panel component for displaying setupc.exe output."""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QFrame, QSplitter)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QTextCharFormat, QColor

from ...core.models import CommandResult


class CommandOutputPanel(QWidget):
    """Collapsible panel showing command execution output and logs."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_expanded = False
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with toggle button and title
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_frame.setFixedHeight(30)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 2, 5, 2)
        
        self.toggle_button = QPushButton("▲ Command Output")
        self.toggle_button.setFlat(True)
        
        clear_button = QPushButton("Clear")
        clear_button.setMaximumWidth(60)
        
        header_layout.addWidget(self.toggle_button)
        header_layout.addStretch()
        header_layout.addWidget(clear_button)
        
        layout.addWidget(header_frame)
        
        # Content area with text output
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        # Command output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(200)
        self.output_text.setMinimumHeight(100)
        
        # Set monospace font for proper console output formatting
        # Try modern fonts first, fallback to system defaults
        font_families = ["Cascadia Code", "Cascadia Mono", "JetBrains Mono", "Fira Code", "Consolas", "Courier New"]
        console_font = QFont()
        console_font.setStyleHint(QFont.StyleHint.Monospace)
        console_font.setPointSize(9)
        
        for family in font_families:
            console_font.setFamily(family)
            if console_font.exactMatch():
                break
        
        self.output_text.setFont(console_font)
        
        content_layout.addWidget(self.output_text)
        layout.addWidget(self.content_widget)
        
        # Initially collapsed
        self.content_widget.hide()
        self.setFixedHeight(30)
        
        # Store references
        self.clear_button = clear_button
    
    def setup_connections(self):
        """Connect signals and slots."""
        self.toggle_button.clicked.connect(self.toggle_panel)
        self.clear_button.clicked.connect(self.clear_output)
    
    @pyqtSlot()
    def toggle_panel(self):
        """Toggle panel expanded/collapsed state."""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.content_widget.show()
            self.toggle_button.setText("▼ Command Output")
            self.setFixedHeight(230)  # Header + content height
        else:
            self.content_widget.hide()
            self.toggle_button.setText("▲ Command Output")
            self.setFixedHeight(30)   # Header only
    
    @pyqtSlot()
    def clear_output(self):
        """Clear all output text."""
        self.output_text.clear()
    
    @pyqtSlot(CommandResult)
    def on_command_completed(self, result: CommandResult):
        """Handle command completion and display output."""
        self.add_command_entry(result)
        
        # Auto-expand if there was an error
        if not result.success and not self.is_expanded:
            self.toggle_panel()
    
    def add_command_entry(self, result: CommandResult):
        """Add a command result entry to the output."""
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        
        # Add timestamp and command
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        cursor.insertText(f"[{timestamp}] {result.command}\n")
        
        # Format and add output
        if result.output.strip():
            format_normal = QTextCharFormat()
            format_normal.setForeground(self.palette().color(self.palette().ColorRole.Text))
            cursor.setCharFormat(format_normal)
            cursor.insertText("Output:\n")
            cursor.insertText(f"{result.output.strip()}\n")
        
        # Format and add error (if any)
        if result.error.strip():
            format_error = QTextCharFormat()
            format_error.setForeground(QColor("#cc0000"))
            cursor.setCharFormat(format_error)
            cursor.insertText("Error:\n")
            cursor.insertText(f"{result.error.strip()}\n")
        
        # Add execution time and result
        format_info = QTextCharFormat()
        format_info.setForeground(self.palette().color(self.palette().ColorRole.PlaceholderText))
        cursor.setCharFormat(format_info)
        
        status = "SUCCESS" if result.success else "FAILED"
        cursor.insertText(f"Status: {status} (took {result.execution_time:.2f}s)\n")
        cursor.insertText("-" * 60 + "\n")
        
        # Scroll to bottom
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )
    
    def log_message(self, message: str, level: str = "INFO"):
        """Add a log message to the output."""
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Format based on level
        format_text = QTextCharFormat()
        if level == "ERROR":
            format_text.setForeground(QColor("#cc0000"))
        elif level == "WARNING":
            format_text.setForeground(QColor("#ff8800"))
        else:
            format_text.setForeground(self.palette().color(self.palette().ColorRole.Link))
        
        cursor.setCharFormat(format_text)
        cursor.insertText(f"[{timestamp}] {level}: {message}\n")
        
        # Scroll to bottom
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )