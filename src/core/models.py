"""Data models for com0com GUI application."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class PortStatus(Enum):
    """Port pair status enumeration."""
    ACTIVE = "Active"
    DISABLED = "Disabled"
    ERROR = "Error"
    UNKNOWN = "Unknown"


class DriverStatus(Enum):
    """Driver installation status enumeration."""
    INSTALLED = "Installed"
    NOT_INSTALLED = "Not Installed"
    NEEDS_UPDATE = "Needs Update"
    ERROR = "Error"


@dataclass
class Port:
    """Individual virtual port model."""
    identifier: str  # e.g., "CNCA0", "CNCB0"
    port_name: str = ""  # e.g., "COM8", "COM9"
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get a parameter value with optional default."""
        return self.parameters.get(name, default)
    
    def set_parameter(self, name: str, value: Any) -> None:
        """Set a parameter value."""
        self.parameters[name] = value
    
    def get_parameter_string(self) -> str:
        """Convert parameters to setupc.exe format string."""
        if not self.parameters:
            return "-"
        
        param_pairs = []
        for key, value in self.parameters.items():
            if value is not None and value != "":
                param_pairs.append(f"{key}={value}")
        
        return ",".join(param_pairs) if param_pairs else "-"


@dataclass
class PortPair:
    """Virtual port pair model."""
    number: int
    port_a: Port
    port_b: Port
    status: PortStatus = PortStatus.UNKNOWN
    
    def __post_init__(self):
        """Initialize port identifiers if not set."""
        if not self.port_a.identifier:
            self.port_a.identifier = f"CNCA{self.number}"
        if not self.port_b.identifier:
            self.port_b.identifier = f"CNCB{self.number}"
    
    def get_display_name(self) -> str:
        """Get display name for the port pair."""
        port_a_name = self.port_a.port_name or self.port_a.identifier
        port_b_name = self.port_b.port_name or self.port_b.identifier
        return f"Pair {self.number}: {port_a_name} ↔ {port_b_name}"
    
    def is_active(self) -> bool:
        """Check if port pair is active."""
        return self.status == PortStatus.ACTIVE


@dataclass
class CommandResult:
    """Result of a setupc.exe command execution."""
    success: bool
    output: str = ""
    error: str = ""
    return_code: int = 0
    execution_time: float = 0.0
    command: str = ""
    
    def get_error_message(self) -> str:
        """Get user-friendly error message."""
        if self.success:
            return ""
        
        if self.error:
            return self.error
        elif self.return_code != 0:
            return f"Command failed with exit code {self.return_code}"
        else:
            return "Unknown error occurred"


@dataclass
class DriverInfo:
    """com0com driver information."""
    status: DriverStatus
    install_path: str = ""
    error_message: str = ""
    
    def is_available(self) -> bool:
        """Check if driver is available for use."""
        return self.status == DriverStatus.INSTALLED


@dataclass
class ApplicationConfig:
    """Application configuration settings."""
    setupc_path: str = r"C:\Program Files (x86)\com0com\setupc.exe"
    command_timeout: int = 30
    auto_refresh_interval: int = 0
    window_geometry: Dict[str, int] = field(default_factory=lambda: {
        "width": 1000,
        "height": 700,
        "x": 100,
        "y": 100
    })
    log_level: str = "INFO"
    theme: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for JSON serialization."""
        return {
            "setupc_path": self.setupc_path,
            "command_timeout": self.command_timeout,
            "auto_refresh_interval": self.auto_refresh_interval,
            "window_geometry": self.window_geometry,
            "log_level": self.log_level,
            "theme": self.theme
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApplicationConfig":
        """Create config from dictionary."""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


class PortListParser:
    """Parser for setupc.exe list command output."""
    
    @staticmethod
    def parse_port_list(output: str) -> List[PortPair]:
        """Parse setupc.exe list output into PortPair objects."""
        port_pairs = []
        current_pair = None
        
        for line in output.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Look for port identifiers (CNCA0, CNCB0, etc.)
            if line.startswith('CNC'):
                parts = line.split()
                if len(parts) >= 1:
                    port_id = parts[0]
                    
                    # Extract pair number
                    pair_num = int(port_id[4:])  # Skip "CNCA" or "CNCB"
                    port_type = port_id[3]  # "A" or "B"
                    
                    # Find or create port pair
                    pair = next((p for p in port_pairs if p.number == pair_num), None)
                    if not pair:
                        pair = PortPair(
                            number=pair_num,
                            port_a=Port(identifier=f"CNCA{pair_num}"),
                            port_b=Port(identifier=f"CNCB{pair_num}"),
                            status=PortStatus.ACTIVE
                        )
                        port_pairs.append(pair)
                    
                    # Set port data
                    port = pair.port_a if port_type == 'A' else pair.port_b
                    port.identifier = port_id
                    
                    # Parse parameters from the rest of the line
                    if len(parts) > 1:
                        params_str = ' '.join(parts[1:])
                        port.parameters = PortListParser._parse_parameters(params_str)
                        
                        # Extract port name if present
                        if 'PortName' in port.parameters:
                            port.port_name = port.parameters['PortName']
        
        return sorted(port_pairs, key=lambda p: p.number)
    
    @staticmethod
    def _parse_parameters(params_str: str) -> Dict[str, str]:
        """Parse parameter string into dictionary."""
        parameters = {}
        
        # Simple parameter parsing - can be enhanced for complex cases
        for param in params_str.split(','):
            param = param.strip()
            if '=' in param:
                key, value = param.split('=', 1)
                parameters[key.strip()] = value.strip()
        
        return parameters