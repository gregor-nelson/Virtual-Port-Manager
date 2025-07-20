# com0com GUI Wrapper - Design Specification

## Project Overview

### Purpose
Create a Windows 10/11 optimized GUI wrapper for com0com's setupc.exe command-line tool using PyQt6. The application should provide a Microsoft-style interface that feels like an official Windows system management utility.

### Target Users
- Windows developers needing virtual serial ports
- System administrators managing COM port configurations
- Testers requiring serial port emulation for applications

### Core Requirements
- Native Windows look and feel (Device Manager/Control Panel style)
- Complete coverage of setupc.exe functionality
- Real-time command feedback and validation
- Robust error handling and user guidance

## Technical Architecture

### Technology Stack
- **Framework**: PyQt6 (for native Windows controls and advanced styling)
- **Language**: Python 3.8+
- **Command Interface**: subprocess for setupc.exe execution
- **Configuration**: JSON-based settings management
- **Logging**: Python logging module with file output

### Dependencies
```
PyQt6>=6.4.0
PyQt6-tools>=6.4.0
```

### Project Structure
```
com0com_gui/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                       # Project documentation
├── assets/                         # Icons and resources
│   ├── icons/
│   │   ├── port_pair.png
│   │   ├── configure.png
│   │   ├── remove.png
│   │   └── refresh.png
│   └── styles/
│       └── windows_theme.qss       # PyQt6 stylesheet
├── src/
│   ├── __init__.py
│   ├── core/                       # Business logic
│   │   ├── __init__.py
│   │   ├── command_manager.py      # setupc.exe interface
│   │   ├── config_manager.py       # Configuration handling
│   │   ├── validators.py           # Parameter validation
│   │   └── models.py              # Data models
│   ├── gui/                        # User interface
│   │   ├── __init__.py
│   │   ├── main_window.py          # Main application window
│   │   ├── components/             # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   ├── port_tree_widget.py
│   │   │   ├── properties_panel.py
│   │   │   ├── ribbon_toolbar.py
│   │   │   └── command_output.py
│   │   └── dialogs/                # Modal dialogs
│   │       ├── __init__.py
│   │       ├── new_port_dialog.py
│   │       ├── configure_dialog.py
│   │       └── driver_ops_dialog.py
│   └── utils/                      # Utilities
│       ├── __init__.py
│       ├── constants.py            # Application constants
│       └── helpers.py              # Helper functions
└── tests/                          # Unit tests
    ├── __init__.py
    ├── test_command_manager.py
    ├── test_validators.py
    └── test_gui_components.py
```

## Detailed Component Specifications

### 1. Main Window (main_window.py)

**Layout**: Microsoft-style with ribbon + dual-pane layout

**Components**:
- Menu bar (File, View, Action, Help)
- Ribbon toolbar with contextual commands
- Left pane: Tree view of port pairs
- Right pane: Properties panel
- Bottom: Status bar
- Optional: Collapsible command output panel

**Key Features**:
- Automatic refresh of port list
- Context-sensitive ribbon commands
- Real-time status updates
- Keyboard shortcuts (F5 for refresh, Del for remove, etc.)

### 2. Command Manager (command_manager.py)

**Purpose**: Interface with setupc.exe safely and efficiently

**Class Structure**:
```python
class CommandManager:
    def __init__(self, setupc_path: str = "setupc.exe"):
        self.setupc_path = setupc_path
        self.timeout = 30  # seconds
        
    def execute_command(self, command: str, args: List[str]) -> CommandResult:
        """Execute setupc command with validation and error handling"""
        
    def list_ports(self) -> List[PortPair]:
        """Get all current port pairs"""
        
    def install_port_pair(self, pair_number: int, params_a: str, params_b: str) -> bool:
        """Install new port pair"""
        
    def remove_port_pair(self, pair_number: int) -> bool:
        """Remove existing port pair"""
        
    def change_port_config(self, port_id: str, parameters: str) -> bool:
        """Modify port parameters"""
        
    def get_driver_status(self) -> DriverStatus:
        """Check driver installation status"""
```

**Error Handling**:
- Command timeout handling
- Invalid parameter detection
- Windows permission issues
- Driver not installed scenarios

### 3. Data Models (models.py)

**Core Classes**:
```python
@dataclass
class PortPair:
    number: int
    port_a: Port
    port_b: Port
    status: str  # "Active", "Disabled", "Error"

@dataclass
class Port:
    identifier: str  # e.g., "CNCA0"
    port_name: str   # e.g., "COM8"
    parameters: Dict[str, Any]
    
@dataclass
class CommandResult:
    success: bool
    output: str
    error: str
    return_code: int
    execution_time: float
```

### 4. Parameter Validation (validators.py)

**Validation Rules** (based on JSON specification):
```python
class ParameterValidator:
    @staticmethod
    def validate_port_number(value: str) -> bool:
        """Validate port pair number (0-999)"""
        
    @staticmethod
    def validate_emu_noise(value: str) -> bool:
        """Validate EmuNoise (0.0-0.99999999)"""
        
    @staticmethod
    def validate_port_identifier(value: str) -> bool:
        """Validate CNC[AB]\d+ pattern"""
        
    @staticmethod
    def validate_pin_assignment(value: str) -> bool:
        """Validate pin wiring values"""
```

### 5. Port Tree Widget (port_tree_widget.py)

**Features**:
- Hierarchical display: Root → Port Pairs → Individual Ports
- Icons for different states (active, disabled, error)
- Context menu with relevant actions
- Drag-and-drop for reordering (future enhancement)
- Multi-selection support

**Tree Structure**:
```
📂 com0com Virtual Ports (2 pairs)
  └📌 Pair 0 (Active)
    ├ CNCA0 → COM8
    └ CNCB0 → COM9
  └📌 Pair 1 (Disabled)
    ├ CNCA1 → COM10
    └ CNCB1 → COM11
```

### 6. Properties Panel (properties_panel.py)

**Dynamic Content** based on selection:
- Port pair properties when pair selected
- Individual port configuration when port selected
- Driver information when root selected
- Quick action buttons contextual to selection

**Port Configuration Form**:
- Grouped parameter sections (Basic, Emulation, Timing, Modes, Pin Wiring)
- Real-time validation with visual feedback
- Tooltips explaining each parameter
- Apply/Reset buttons

### 7. Ribbon Toolbar (ribbon_toolbar.py)

**Command Groups**:
- **Port Management**: New Pair, Remove, Configure
- **View**: Refresh, Show Details, Filter
- **Driver**: Install, Update, Reload, Uninstall
- **Tools**: Export Config, Import Config, Diagnostics

**Context Sensitivity**: Commands enable/disable based on current selection

## Implementation Guidelines

### PyQt6 Specific Requirements

**Main Window Setup**:
```python
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("com0com Manager")
        self.setWindowIcon(QIcon("assets/icons/app.png"))
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.setup_style()
```

**Windows Theme Integration**:
- Use native Windows colors and fonts
- Implement proper DPI scaling
- Support dark/light theme detection
- Use Windows-standard icons where possible

**Threading**:
- All setupc.exe commands must run in background threads
- Use QThread for long-running operations
- Implement proper progress feedback
- Ensure UI remains responsive

### Error Handling Strategy

**User-Friendly Error Messages**:
- Convert technical errors to plain language
- Provide actionable solutions
- Log detailed errors for debugging
- Show progress for time-consuming operations

**Common Error Scenarios**:
- setupc.exe not found → Guide to com0com installation
- Permission denied → Suggest running as administrator
- Port already in use → Show which application is using it
- Driver not installed → Offer to install driver

### Configuration Management

**Settings Storage**: JSON file in user's AppData
**Configurable Items**:
- setupc.exe path location
- Default port parameters
- UI preferences (window size, panel layout)
- Command timeout values
- Logging level

## Development Phases

### Phase 1: Core Infrastructure (Week 1-2)
- Basic PyQt6 application structure
- Command manager with basic setupc.exe interface
- Simple port list display
- Basic install/remove functionality

**Deliverables**:
- Working main window with menu
- Port list that refreshes from setupc.exe
- Basic new port pair creation
- Remove port pair functionality

### Phase 2: User Interface Polish (Week 3-4)
- Complete ribbon toolbar implementation
- Properties panel with parameter editing
- Windows-style theming
- Error handling and validation

**Deliverables**:
- Full ribbon interface with icons
- Complete port configuration forms
- Parameter validation with visual feedback
- Professional Windows styling

### Phase 3: Advanced Features (Week 5-6)
- Driver management operations
- Configuration import/export
- Advanced error handling
- Performance optimization

**Deliverables**:
- Driver install/update/reload functionality
- Configuration backup/restore
- Comprehensive error messages
- Performance testing results

### Phase 4: Testing & Documentation (Week 7-8)
- Comprehensive testing on different Windows versions
- User documentation
- Installation package creation
- Bug fixes and polish

**Deliverables**:
- Tested application on Windows 10/11
- User manual and help system
- Installer package
- Final release candidate

## Getting Started Instructions

### For the Implementing Developer

1. **Environment Setup**:
   ```bash
   python -m venv com0com_gui_env
   com0com_gui_env\Scripts\activate
   pip install PyQt6 PyQt6-tools
   ```

2. **Initial Implementation Order**:
   - Create basic project structure
   - Implement CommandManager with list_ports() method
   - Create MainWindow with basic layout
   - Add PortTreeWidget with hardcoded test data
   - Connect real data from CommandManager
   - Implement basic port pair creation

3. **Testing Strategy**:
   - Use com0com's actual setupc.exe for integration testing
   - Create mock CommandManager for unit testing UI components
   - Test on Windows 10 and 11 with different DPI settings

4. **Key Implementation Tips**:
   - Always use QThread for subprocess calls
   - Implement proper signal/slot communication between threads
   - Use Qt's model/view architecture for port list display
   - Leverage Qt Designer for complex dialog layouts
   - Follow Windows HIG for consistent user experience

This specification provides complete guidance for implementing a professional com0com GUI wrapper that integrates seamlessly with Windows and provides comprehensive access to all setupc.exe functionality.