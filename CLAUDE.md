# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PyQt6-based GUI application for managing com0com virtual serial ports on Windows. It provides a modern ribbon interface to wrap com0com's setupc.exe command-line tool with features like port management, driver operations, and parameter validation.

## Development Commands

### Build and Distribution
```bash
# Create executable (from project root)
python build.py                    # Simple launcher for scripts/build.py
python scripts/build.py           # Full PyInstaller build with UAC elevation
scripts/build.bat                 # Windows batch wrapper for build.py

# Manual PyInstaller (if needed)
pyinstaller com0com-gui.spec      # Uses existing spec file
```

### Running the Application
```bash
# Development mode
python main.py

# Test specific components (no formal test framework yet)
python -m src.core.command_manager
python -m src.gui.main_window
```

### Dependencies
The project uses PyQt6 as the primary framework. Install dependencies with:
```bash
pip install PyQt6>=6.4.0 PyInstaller>=5.10.0
```

Note: No requirements.txt exists yet - dependencies are mentioned in the build scripts and README.

## Architecture Overview

### Core Components
- **Command Manager** (`src/core/command_manager.py`): Async setupc.exe execution with QThread workers
- **Data Models** (`src/core/models.py`): PortPair, Port, CommandResult, DriverInfo classes with setupc.exe parameter formatting
- **Parameter Validation** (`src/core/validators.py`): Input validation for all setupc.exe parameters (port numbers, noise values, pin assignments)
- **Configuration Manager** (`src/core/config_manager.py`): JSON-based settings persistence in %LOCALAPPDATA%

### GUI Architecture
- **Main Window** (`src/gui/main_window.py`): Central interface with ribbon toolbar, port tree view, and properties panel
- **Ribbon Toolbar** (`src/gui/components/ribbon_toolbar.py`): Microsoft-style command interface with contextual groups
- **Port Tree Widget** (`src/gui/components/port_tree_widget.py`): Hierarchical display of port pairs and individual ports
- **Properties Panel** (`src/gui/components/properties_panel.py`): Dynamic configuration forms based on current selection
- **Command Output Panel** (`src/gui/components/command_output.py`): Real-time logging of setupc.exe commands

### Dialog System
All dialogs in `src/gui/dialogs/`:
- **New Port Dialog**: Create port pairs with parameter validation
- **Configure Dialog**: Edit existing port parameters
- **Driver Operations Dialog**: Install/update/reload/uninstall driver operations
- **Setup Wizard Dialog**: First-time configuration and setupc.exe detection

## setupc.exe Integration

### Command Patterns
The application wraps setupc.exe commands defined in `src/utils/constants.py`:
- Port management: `install`, `remove`, `change`, `list`
- Driver operations: `preinstall`, `update`, `reload`, `uninstall`
- System control: `disable all`, `enable all`
- Utilities: `infclean`, `listfnames`, `busynames`

### Parameter Handling
Parameters are validated and formatted according to setupc.exe requirements:
- Port numbers: 0-999
- Port identifiers: CNC[AB]\d+ pattern
- Boolean values: "yes"/"no"
- COM ports: COM1-COM999 or COM# for auto-assignment
- EmuNoise: 0.0-0.99999999 range
- Pin assignments: Comprehensive validation with inversion support

### Threading Model
All setupc.exe commands run in QThread workers to keep the UI responsive. Command execution includes timeout handling and proper error propagation.

## Asset System

### Icons and Theming
- **SVG Icons**: Complete icon set in `assets/icons/` with app icon, port icons, and toolbar commands
- **Windows Theme**: Custom QSS stylesheet (`assets/styles/windows_theme.qss`) matching Windows 10/11 design language
- **High DPI Support**: Native PyQt6 SVG rendering for crisp scaling

### Build Integration
Assets are bundled into the executable via PyInstaller's `--add-data` directive in the build scripts.

## Configuration and Settings

### Settings Storage
- Location: `%LOCALAPPDATA%\com0com-gui\config.json`
- Contains: setupc.exe path, window geometry, UI preferences, command timeouts
- Managed by: `src/core/config_manager.py`

### Logging
- Error logs: `%LOCALAPPDATA%\com0com-gui\logs\error.log`
- Real-time command output displayed in GUI

## Code Conventions

### PyQt6 Patterns
- Use Qt's signal/slot mechanism for component communication
- Implement proper QThread workers for background operations
- Follow Qt's model/view architecture for data display
- Use Qt's resource system for icons and stylesheets

### Error Handling
- Convert technical setupc.exe errors to user-friendly messages
- Provide actionable guidance (e.g., "Run as administrator", "Install com0com driver")
- Log detailed errors while showing simplified messages to users

### Parameter Management
- Use dataclass models from `src/core/models.py` for type safety
- Validate all user inputs before sending to setupc.exe
- Support special values like "-" (defaults), "*" (current), "COM#" (auto-assign)

## Windows-Specific Considerations

### UAC and Privileges
- Application requires Administrator privileges for driver operations
- PyInstaller builds include UAC manifest for automatic elevation
- Handle permission-denied errors gracefully with user guidance

### Path Handling
- Default setupc.exe locations checked: Program Files, Program Files (x86), C:\com0com
- Support custom setupc.exe path configuration
- Use Windows-style path separators in all file operations

### Integration Points
- COM port enumeration and validation
- Windows Device Manager-style interface design
- Support for Windows 7/8/10/11 compatibility

## Development Notes

### Testing Strategy
- No formal test framework implemented yet
- Manual testing with actual setupc.exe integration
- Consider adding pytest for unit testing core components
- GUI testing can be done with PyQt6's QTest framework

### Future Enhancements
- Configuration import/export functionality
- Advanced error diagnostics
- Multi-language support
- Plugin system for custom parameter sets

### Performance Considerations
- Port list refresh is throttled to 5-second intervals
- Use QThread workers for all setupc.exe operations to maintain UI responsiveness
- Asset bundling optimized for single-file executable distribution