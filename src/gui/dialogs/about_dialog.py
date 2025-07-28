"""About dialog for com0com GUI Manager."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QWidget, QFrame)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices, QPainter
from PyQt6.QtSvg import QSvgRenderer


class AboutDialog(QDialog):
    """Custom about dialog with GitHub source link."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About com0com Manager")
        self.setModal(True)
        self.setFixedSize(400, 280)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Icon and title section
        header_layout = QHBoxLayout()
        
        # App icon placeholder (system information icon)
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        # Use system information icon
        info_icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        icon_label.setPixmap(info_icon.pixmap(48, 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title and version
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        title_label = QLabel("com0com Manager")
        
        version_label = QLabel("Version 1.0.0")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(version_label)
        title_layout.addStretch()
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(separator)
        
        # Description text
        description_label = QLabel(
            "A PyQt6-based GUI wrapper for com0com's setupc.exe command-line tool.\n\n"
            "com0com is a virtual serial port driver that creates pairs of virtual COM ports "
            "for Windows development and testing."
        )
        description_label.setWordWrap(True)
        layout.addWidget(description_label)
        
        # GitHub link section
        github_layout = QHBoxLayout()
        github_layout.setContentsMargins(0, 8, 0, 0)
        
        # GitHub icon button
        self.github_button = QPushButton()
        self.github_button.setFixedSize(24, 24)
        self.github_button.setToolTip("View source code on GitHub")
        
        # Create GitHub SVG icon
        github_svg = '''
        <svg width="20" height="20" viewBox="0 0 24 24" fill="#666666">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
        </svg>
        '''
        
        # Convert SVG to QIcon
        github_icon = self.create_github_icon(github_svg)
        self.github_button.setIcon(github_icon)
        self.github_button.setIconSize(self.github_button.size())
        
        
        # Set cursor to pointer on hover
        self.github_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        github_layout.addStretch()
        github_layout.addWidget(self.github_button)
        github_layout.addStretch()
        
        layout.addLayout(github_layout)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setFixedSize(80, 32)
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
    
    def create_github_icon(self, svg_content):
        """Create a QIcon from SVG content."""
        try:
            # Try to use SVG renderer
            renderer = QSvgRenderer()
            renderer.load(svg_content.encode('utf-8'))
            
            pixmap = QPixmap(20, 20)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            return QIcon(pixmap)
        except ImportError:
            # Fallback if QtSvg is not available - use Unicode icon
            return self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.github_button.clicked.connect(self.open_github_repository)
    
    def open_github_repository(self):
        """Open the GitHub repository in the default browser."""
        # Replace with your actual GitHub repository URL
        github_url = "https://github.com/gregor-nelson/VirtualPortManager"
        QDesktopServices.openUrl(QUrl(github_url))
    
    @staticmethod
    def show_about(parent=None):
        """Static method to show the about dialog."""
        dialog = AboutDialog(parent)
        dialog.exec()