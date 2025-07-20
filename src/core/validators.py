"""Parameter validation functions for setupc.exe commands."""

import re
from typing import Tuple, Union


class ParameterValidator:
    """Validation functions for setupc.exe parameters."""
    
    @staticmethod
    def validate_port_number(value: Union[str, int]) -> Tuple[bool, str]:
        """Validate port pair number (0-999)."""
        try:
            num = int(value)
            if 0 <= num <= 999:
                return True, ""
            else:
                return False, "Port number must be between 0 and 999"
        except (ValueError, TypeError):
            return False, "Port number must be a valid integer"
    
    @staticmethod
    def validate_emu_noise(value: Union[str, float]) -> Tuple[bool, str]:
        """Validate EmuNoise parameter (0.0-0.99999999)."""
        try:
            noise = float(value)
            if 0.0 <= noise <= 0.99999999:
                return True, ""
            else:
                return False, "EmuNoise must be between 0.0 and 0.99999999"
        except (ValueError, TypeError):
            return False, "EmuNoise must be a valid floating point number"
    
    @staticmethod
    def validate_port_identifier(value: str) -> Tuple[bool, str]:
        """Validate port identifier (CNC[AB]\\d+ pattern)."""
        if not isinstance(value, str):
            return False, "Port identifier must be a string"
        
        pattern = r"^CNC[AB]\d+$"
        if re.match(pattern, value):
            return True, ""
        else:
            return False, "Port identifier must match pattern CNC[AB]<number> (e.g., CNCA0, CNCB1)"
    
    @staticmethod
    def validate_pin_assignment(value: str) -> Tuple[bool, str]:
        """Validate pin wiring assignment values."""
        if not isinstance(value, str):
            return False, "Pin assignment must be a string"
        
        # Handle inversion prefix
        clean_value = value
        if value.startswith('!'):
            clean_value = value[1:]
        
        # Check for special values
        if clean_value in ["-", "*"]:
            return True, ""
        
        # Valid pin values
        valid_pins = [
            "rrts", "lrts", "rdtr", "ldtr",
            "rout1", "lout1", "rout2", "lout2",
            "ropen", "lopen", "on"
        ]
        
        if clean_value in valid_pins:
            return True, ""
        else:
            return False, f"Invalid pin assignment. Must be one of: {', '.join(valid_pins)} (optionally prefixed with !)"
    
    @staticmethod
    def validate_boolean(value: str) -> Tuple[bool, str]:
        """Validate boolean parameter values."""
        if not isinstance(value, str):
            return False, "Boolean value must be a string"
        
        if value.lower() in ["yes", "no"]:
            return True, ""
        else:
            return False, "Boolean value must be 'yes' or 'no'"
    
    @staticmethod
    def validate_positive_integer(value: Union[str, int]) -> Tuple[bool, str]:
        """Validate positive integer values."""
        try:
            num = int(value)
            if num >= 0:
                return True, ""
            else:
                return False, "Value must be a positive integer (0 or greater)"
        except (ValueError, TypeError):
            return False, "Value must be a valid integer"
    
    @staticmethod
    def validate_com_port_name(value: str) -> Tuple[bool, str]:
        """Validate COM port name format."""
        if not isinstance(value, str):
            return False, "COM port name must be a string"
        
        # Special values
        if value in ["COM#", "-", "*"]:
            return True, ""
        
        # Standard COM port pattern
        pattern = r"^COM\d+$"
        if re.match(pattern, value):
            return True, ""
        else:
            return False, "COM port name must be in format COM<number> or special value COM#"
    
    @staticmethod
    def validate_parameter_string(param_string: str) -> Tuple[bool, str]:
        """Validate complete parameter string format."""
        if not isinstance(param_string, str):
            return False, "Parameter string must be a string"
        
        # Special values
        if param_string in ["-", "*"]:
            return True, ""
        
        # Parse individual parameters
        parameters = param_string.split(',')
        for param in parameters:
            param = param.strip()
            if '=' not in param:
                return False, f"Invalid parameter format: '{param}'. Expected format: key=value"
            
            key, value = param.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if not key:
                return False, "Parameter key cannot be empty"
            if not value:
                return False, f"Parameter value for '{key}' cannot be empty"
        
        return True, ""
    
    @staticmethod
    def validate_command_timeout(value: Union[str, int]) -> Tuple[bool, str]:
        """Validate command timeout value."""
        try:
            timeout = int(value)
            if 1 <= timeout <= 600:  # 1 second to 10 minutes
                return True, ""
            else:
                return False, "Timeout must be between 1 and 600 seconds"
        except (ValueError, TypeError):
            return False, "Timeout must be a valid integer"


class ParameterBuilder:
    """Helper class for building parameter strings."""
    
    @staticmethod
    def build_parameter_string(parameters: dict) -> str:
        """Convert parameter dictionary to setupc.exe format string."""
        if not parameters:
            return "-"
        
        param_pairs = []
        for key, value in parameters.items():
            if value is not None and value != "":
                # Handle special boolean values
                if isinstance(value, bool):
                    value = "yes" if value else "no"
                param_pairs.append(f"{key}={value}")
        
        return ",".join(param_pairs) if param_pairs else "-"
    
    @staticmethod
    def parse_parameter_string(param_string: str) -> dict:
        """Parse parameter string into dictionary."""
        if param_string in ["-", "*"]:
            return {}
        
        parameters = {}
        for param in param_string.split(','):
            param = param.strip()
            if '=' in param:
                key, value = param.split('=', 1)
                parameters[key.strip()] = value.strip()
        
        return parameters
    
    @staticmethod
    def validate_and_build(parameters: dict) -> Tuple[bool, str, str]:
        """Validate parameters and build parameter string."""
        # Validate individual parameters
        for key, value in parameters.items():
            if key == "PortName":
                valid, error = ParameterValidator.validate_com_port_name(str(value))
                if not valid:
                    return False, "", f"Invalid PortName: {error}"
            elif key == "EmuNoise":
                valid, error = ParameterValidator.validate_emu_noise(value)
                if not valid:
                    return False, "", f"Invalid EmuNoise: {error}"
            elif key in ["EmuBR", "EmuOverrun", "PlugInMode", "ExclusiveMode", "HiddenMode", "AllDataBits"]:
                valid, error = ParameterValidator.validate_boolean(str(value))
                if not valid:
                    return False, "", f"Invalid {key}: {error}"
            elif key in ["AddRTTO", "AddRITO"]:
                valid, error = ParameterValidator.validate_positive_integer(value)
                if not valid:
                    return False, "", f"Invalid {key}: {error}"
            elif key in ["cts", "dsr", "dcd", "ri"]:
                valid, error = ParameterValidator.validate_pin_assignment(str(value))
                if not valid:
                    return False, "", f"Invalid {key}: {error}"
        
        # Build parameter string
        param_string = ParameterBuilder.build_parameter_string(parameters)
        return True, param_string, ""