# com0com GUI Manager

A Windows GUI application for managing com0com virtual serial ports, built with PyQt6. Provides a modern ribbon interface to wrap com0com's setupc.exe command-line tool.


<img width="1368" height="736" alt="com0com screenshot 1" src="https://github.com/user-attachments/assets/f62a34a7-3152-4368-bbe3-793f13a06227" />


## Features

- **Modern Interface**: Windows 10/11-style ribbon with SVG icons
- **Port Management**: Create, configure, and remove virtual serial port pairs
- **Real-time Output**: Live command execution feedback
- **Driver Operations**: Install, update, reload, and uninstall drivers
- **Parameter Validation**: Comprehensive input validation for all setupc.exe parameters
- **Error Handling**: User-friendly error messages and recovery guidance
- **Settings Persistence**: Saves window geometry, paths, and preferences

## Requirements

**System**
- Windows 10/11
- com0com virtual serial port driver
- Administrator privileges (for driver operations)

**Development**
- Python 3.8+
- PyQt6 >= 6.4.0
- PyInstaller >= 5.10.0 (for building)

## Quick Start

**For Users**
1. Download `com0com-gui.exe` from releases
2. Run as administrator (UAC elevation required)
3. Install com0com driver if needed ([download here](https://sourceforge.net/projects/com0com/))
4. Launch the executable directly

**For Developers**
```bash
git clone <repository-url>
cd Serial
pip install -r scripts/requirements-build.txt
python main.py
```

**Build Executable**
```bash
python build.py
```

## Architecture

**Core Components**
- **Command Manager** (`src/core/command_manager.py`): Async setupc.exe execution with QThread workers
- **Data Models** (`src/core/models.py`): PortPair, Port, CommandResult, DriverInfo classes
- **Parameter Validation** (`src/core/validators.py`): Input validation for setupc.exe parameters
- **Configuration Manager** (`src/core/config_manager.py`): JSON-based settings persistence

**GUI Components**
- **Main Window** (`src/gui/main_window.py`): Central interface with ribbon, tree, properties panel
- **Ribbon Toolbar** (`src/gui/components/ribbon_toolbar.py`): Microsoft-style command interface
- **Port Tree Widget** (`src/gui/components/port_tree_widget.py`): Hierarchical port display
- **Properties Panel** (`src/gui/components/properties_panel.py`): Dynamic configuration forms
- **Command Output Panel** (`src/gui/components/command_output.py`): Real-time logging

**Dialog System**
- **New Port Dialog** (`src/gui/dialogs/new_port_dialog.py`): Create port pairs
- **Configure Dialog** (`src/gui/dialogs/configure_dialog.py`): Edit port parameters
- **Driver Operations Dialog** (`src/gui/dialogs/driver_ops_dialog.py`): Driver management
- **Setup Wizard** (`src/gui/dialogs/setup_wizard_dialog.py`): First-time setup

## Visual Design

**SVG Icon System**
- Custom serial port themed application icon
- Hierarchical tree icons for port pairs and individual ports
- Complete ribbon command set with semantic colour coding
- Native PyQt6 SVG support for crisp scaling

**Windows Theme**
- Custom QSS stylesheet (`assets/styles/windows_theme.qss`)
- Matches Windows 10/11 design language
- High DPI display support

## setupc.exe Integration

**Supported Commands**
- `setupc list` - List current port pairs
- `setupc install <pair> <params>` - Create port pair
- `setupc remove <pair>` - Remove port pair
- `setupc change <port> <params>` - Modify port parameters
- `setupc preinstall/update/reload/uninstall` - Driver operations

**Parameter Validation**
- Port numbers: 0-999
- Port identifiers: CNC[AB]\d+ pattern
- Boolean values: "yes"/"no"
- COM ports: COM1-COM999 or COM# for auto-assignment
- EmuNoise: 0.0-0.99999999 range
- Pin assignments: Comprehensive validation

## Testing

Testing framework is planned but not yet implemented. The application uses manual testing with setupc.exe integration.

## Building

**Create Executable**
```bash
python build.py    # Creates single-file executable with UAC elevation
```

**Build Features**
- PyInstaller single-file executable with `--onefile`
- Built-in UAC elevation using `--uac-admin`
- SVG and asset bundling
- Windows GUI application (`--windowed`)
- All dependencies included in single executable

## Configuration

Settings are stored in JSON format at:
```
%LOCALAPPDATA%\com0com-gui\config.json
```

**Configurable Options**
- setupc.exe path specification
- Command execution timeout
- Window geometry persistence
- Logging level

**Setup Wizard**
The application includes a first-time setup wizard that:
1. Detects com0com driver installation
2. Locates setupc.exe in common paths
3. Tests setupc.exe functionality
4. Configures initial settings

## Development

**Code Standards**
- PyQt6 framework with type hints throughout
- Qt signal-slot architecture for component communication
- Model-View-Controller pattern for clean separation
- QThread workers for non-blocking operations
- Comprehensive error handling

**Adding Features**
1. Define command template in constants
2. Implement in CommandManager with validation
3. Add UI action in RibbonToolbar
4. Wire signal-slot connections
5. Test manually with setupc.exe integration

**GUI Guidelines**
- Follow Windows design patterns
- Use QThread for blocking operations
- Provide real-time user feedback
- Support high DPI displays

## Troubleshooting

**Common Issues**

**setupc.exe Not Found**
- Solution: Install com0com or specify path in Settings
- Check: Verify com0com installation completed

**Permission Denied**
- Solution: Run as administrator
- Cause: Driver operations require elevated privileges

**Port Already Exists**
- Solution: Use different port number or remove existing
- Alternative: Use COM# for automatic assignment

**Driver Not Detected**
- Solution: Restart after com0com installation
- Check: Device Manager for com0com devices

**Logs**
Error logs stored at: `%LOCALAPPDATA%\com0com-gui\logs\error.log`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test manually
4. Ensure build succeeds
5. Submit a pull request

**Development Setup**
```bash
pip install -r scripts/requirements-build.txt
python main.py    # Run application
python build.py   # Test build process
```

## Related Projects

- [com0com](https://sourceforge.net/projects/com0com/) - Virtual serial port driver
- [PyQt6](https://doc.qt.io/qtforpython/) - Python GUI framework
- [setupc.exe Documentation](readme_com0com) - Command reference

## License

MIT License - see [LICENSE.txt](LICENSE.txt) for details.

---

**Note**: This application is a GUI wrapper for com0com and requires the com0com driver to be installed separately. com0com is developed and maintained by the com0com project team.
