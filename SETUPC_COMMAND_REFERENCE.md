# setupc.exe Command Reference for GUI Implementation

This document provides a developer-friendly reference for all setupc.exe commands and parameters that need to be implemented in the GUI wrapper.

## Command Categories for GUI Organization

### Port Management Commands

#### Install Port Pair
```python
# Numbered installation
command = f"setupc.exe install {pair_number} {params_a} {params_b}"
# Example: "setupc.exe install 0 PortName=COM8 PortName=COM9"

# Auto-numbered installation  
command = f"setupc.exe install {params_a} {params_b}"
# Example: "setupc.exe install - -"

# Update after batch operations
command = "setupc.exe install"
```

#### Remove Port Pair
```python
command = f"setupc.exe remove {pair_number}"
# Example: "setupc.exe remove 0"
```

#### Modify Port Configuration
```python
command = f"setupc.exe change {port_id} {parameters}"
# Example: "setupc.exe change CNCA0 EmuBR=yes,EmuOverrun=yes"
```

#### List All Ports
```python
command = "setupc.exe list"
# Returns: Port configurations for parsing
```

### Driver Management Commands

```python
# Driver operations
commands = {
    "preinstall": "setupc.exe preinstall",
    "update": "setupc.exe update", 
    "reload": "setupc.exe reload",
    "uninstall": "setupc.exe uninstall"
}
```

### System Control Commands

```python
# Port control
commands = {
    "disable_all": "setupc.exe disable all",
    "enable_all": "setupc.exe enable all"
}
```

### Utility Commands

```python
# Utilities
commands = {
    "clean_inf": "setupc.exe infclean",
    "update_names": "setupc.exe updatefnames", 
    "list_names": "setupc.exe listfnames",
    "busy_names": f"setupc.exe busynames {pattern}",  # e.g., "COM?*"
    "help": "setupc.exe help"
}
```

## Global Options for All Commands

```python
global_options = {
    "--output": "logfile.txt",           # Redirect output to file
    "--wait": "30",                      # Wait timeout (or "+30" for prompt)
    "--detail-prms": True,               # Show detailed parameters
    "--silent": True,                    # Suppress dialogs
    "--no-update": True,                 # Skip driver update (batch mode)
    "--no-update-fnames": True,          # Skip friendly name updates
    "--show-fnames": True                # Show friendly name activity
}
```

## Port Parameters for GUI Forms

### Basic Settings
```python
basic_params = {
    "PortName": {
        "type": "string",
        "default": "port_identifier",  # e.g., "CNCA0"
        "special": "COM#",             # Auto-assign COM number
        "example": "COM8"
    },
    "RealPortName": {
        "type": "string",
        "requires": "PortName=COM#",   # Only valid with COM# ports
        "example": "COM3"
    }
}
```

### Emulation Settings  
```python
emulation_params = {
    "EmuBR": {
        "type": "boolean",
        "values": ["yes", "no"],
        "default": "no",
        "description": "Baud rate emulation"
    },
    "EmuOverrun": {
        "type": "boolean", 
        "values": ["yes", "no"],
        "default": "no",
        "description": "Buffer overrun emulation"
    },
    "EmuNoise": {
        "type": "float",
        "range": "0.0-0.99999999",
        "default": "0",
        "description": "Error probability per character"
    }
}
```

### Timing Settings
```python
timing_params = {
    "AddRTTO": {
        "type": "integer",
        "unit": "milliseconds",
        "default": "0",
        "description": "Additional read total timeout"
    },
    "AddRITO": {
        "type": "integer", 
        "unit": "milliseconds",
        "default": "0",
        "description": "Additional read interval timeout"
    }
}
```

### Mode Settings
```python
mode_params = {
    "PlugInMode": {
        "type": "boolean",
        "values": ["yes", "no"],
        "default": "no",
        "description": "Hide until paired port opens"
    },
    "ExclusiveMode": {
        "type": "boolean",
        "values": ["yes", "no"], 
        "default": "no",
        "description": "Hide when open"
    },
    "HiddenMode": {
        "type": "boolean",
        "values": ["yes", "no"],
        "default": "no", 
        "description": "Hide from enumerators"
    },
    "AllDataBits": {
        "type": "boolean",
        "values": ["yes", "no"],
        "default": "no",
        "description": "Transfer all data bits"
    }
}
```

### Pin Wiring Settings
```python
pin_params = {
    "cts": {
        "type": "pin_assignment",
        "default": "rrts",
        "values": ["rrts", "lrts", "rdtr", "ldtr", "rout1", "lout1", 
                   "rout2", "lout2", "ropen", "lopen", "on"],
        "invert": True,  # Can prefix with "!" to invert
        "description": "CTS pin wiring"
    },
    "dsr": {
        "type": "pin_assignment",
        "default": "rdtr", 
        "values": ["rrts", "lrts", "rdtr", "ldtr", "rout1", "lout1",
                   "rout2", "lout2", "ropen", "lopen", "on"],
        "invert": True,
        "description": "DSR pin wiring"
    },
    "dcd": {
        "type": "pin_assignment",
        "default": "rdtr",
        "values": ["rrts", "lrts", "rdtr", "ldtr", "rout1", "lout1",
                   "rout2", "lout2", "ropen", "lopen", "on"], 
        "invert": True,
        "description": "DCD pin wiring"
    },
    "ri": {
        "type": "pin_assignment",
        "default": "!on",
        "values": ["rrts", "lrts", "rdtr", "ldtr", "rout1", "lout1",
                   "rout2", "lout2", "ropen", "lopen", "on"],
        "invert": True, 
        "description": "RI pin wiring"
    }
}
```

## Parameter String Formatting

### Building Parameter Strings
```python
def build_parameter_string(params: dict) -> str:
    """Convert parameter dict to setupc.exe format"""
    if not params:
        return "-"  # Use defaults
    
    param_pairs = []
    for key, value in params.items():
        if value is not None and value != "":
            param_pairs.append(f"{key}={value}")
    
    return ",".join(param_pairs)

# Examples:
# {} -> "-"
# {"PortName": "COM8"} -> "PortName=COM8"
# {"PortName": "COM8", "EmuBR": "yes"} -> "PortName=COM8,EmuBR=yes"
```

### Special Parameter Values
```python
special_values = {
    "-": "Use driver defaults for all parameters",
    "*": "Use current settings for all parameters", 
    "COM#": "Auto-assign COM port number"
}
```

## GUI Form Validation Rules

### Input Validation Functions
```python
def validate_inputs(param_type: str, value: str) -> tuple[bool, str]:
    """Validate parameter input and return (is_valid, error_message)"""
    
    validators = {
        "port_number": lambda x: (x.isdigit() and 0 <= int(x) <= 999, "Must be 0-999"),
        "emu_noise": lambda x: validate_float_range(x, 0.0, 0.99999999),
        "port_id": lambda x: validate_regex(x, r"CNC[AB]\d+"), 
        "boolean": lambda x: (x.lower() in ["yes", "no"], "Must be 'yes' or 'no'"),
        "integer": lambda x: (x.isdigit(), "Must be a positive integer"),
        "pin_assignment": lambda x: validate_pin_value(x)
    }
    
    return validators.get(param_type, lambda x: (True, ""))(value)
```

## Command Execution Patterns

### Basic Command Execution
```python
import subprocess
from typing import Tuple

def execute_setupc_command(command: str, timeout: int = 30) -> Tuple[bool, str, str]:
    """Execute setupc command and return (success, stdout, stderr)"""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False  # Security: don't use shell
        )
        return (result.returncode == 0, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (False, "", "Command timed out")
    except FileNotFoundError:
        return (False, "", "setupc.exe not found")
    except Exception as e:
        return (False, "", f"Error: {str(e)}")
```

### Batch Operations Pattern
```python
def install_multiple_pairs(pair_configs: list) -> bool:
    """Install multiple port pairs efficiently using --no-update"""
    success = True
    
    # Install pairs without updating driver
    for config in pair_configs:
        cmd = f"setupc.exe --no-update install {config['params_a']} {config['params_b']}"
        result, _, _ = execute_setupc_command(cmd)
        if not result:
            success = False
            break
    
    # Update driver once at the end
    if success:
        result, _, _ = execute_setupc_command("setupc.exe install")
        return result
    
    return False
```

## Environment Variables (For Advanced Users)

```python
# Installer behavior control
installer_env_vars = {
    "CNC_INSTALL_START_MENU_SHORTCUTS": ["YES", "NO"],
    "CNC_INSTALL_CNCA0_CNCB0_PORTS": ["YES", "NO"], 
    "CNC_INSTALL_COMX_COMX_PORTS": ["YES", "NO"],
    "CNC_INSTALL_SKIP_SETUP_PREINSTALL": ["YES", "NO"]
}

# Uninstaller behavior control  
uninstaller_env_vars = {
    "CNC_UNINSTALL_SKIP_SETUP_UNINSTALL": ["YES", "NO"]
}
```

## Common Usage Patterns for GUI

### Quick Port Pair Creation
```python
# Default pair (auto-numbered)
"setupc.exe install - -"

# Named COM ports  
"setupc.exe install PortName=COM2 PortName=COM4"

# Numbered pair with specific settings
"setupc.exe install 0 PortName=COM8,EmuBR=yes PortName=COM9,EmuBR=yes"
```

### Port Configuration Changes
```python
# Enable emulation features
"setupc.exe change CNCA0 EmuBR=yes,EmuOverrun=yes"

# Set special modes
"setupc.exe change CNCB0 PlugInMode=yes,HiddenMode=yes"

# Pin wiring configuration
"setupc.exe change CNCA0 cts=!rrts,dsr=rdtr"
```

This reference provides all the technical details needed to implement a complete GUI wrapper for setupc.exe functionality.