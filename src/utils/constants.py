"""Application constants and configuration values."""
import os

APP_NAME = "com0com Manager"
APP_VERSION = "1.0.0"

DEFAULT_SETUPC_PATH = r"C:\Program Files (x86)\com0com\setupc.exe"
DEFAULT_COMMAND_TIMEOUT = 30

# Default com0com installation paths (Windows)
DEFAULT_COM0COM_PATHS = [
    r"C:\Program Files\com0com\setupc.exe",
    r"C:\Program Files (x86)\com0com\setupc.exe",
    r"C:\com0com\setupc.exe"
]

# Alias for backward compatibility
SETUPC_PATHS = DEFAULT_COM0COM_PATHS

WINDOW_TITLE = "com0com Manager"
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1000
WINDOW_DEFAULT_HEIGHT = 700

PORT_TREE_REFRESH_INTERVAL = 5000

SETUPC_COMMANDS = {
    "INSTALL_NUMBERED": "install {} {} {}",
    "INSTALL_AUTO": "install {} {}",
    "INSTALL_UPDATE": "install",
    "REMOVE": "remove {}",
    "CHANGE": "change {} {}",
    "LIST": "list",
    "PREINSTALL": "preinstall",
    "UPDATE": "update",
    "RELOAD": "reload",
    "UNINSTALL": "uninstall",
    "DISABLE_ALL": "disable all",
    "ENABLE_ALL": "enable all",
    "HELP": "help",
    # Utility commands
    "INFCLEAN": "infclean",
    "LISTFNAMES": "listfnames",
    "BUSYNAMES": "busynames {}",
    "UPDATEFNAMES": "updatefnames"
}

PORT_PARAMETERS = {
    "BASIC": ["PortName", "RealPortName"],
    "EMULATION": ["EmuBR", "EmuOverrun", "EmuNoise"],
    "TIMING": ["AddRTTO", "AddRITO"],
    "MODES": ["PlugInMode", "ExclusiveMode", "HiddenMode", "AllDataBits"],
    "PIN_WIRING": ["cts", "dsr", "dcd", "ri"]
}

PIN_ASSIGNMENT_VALUES = [
    "rrts", "lrts", "rdtr", "ldtr",
    "rout1", "lout1", "rout2", "lout2",
    "ropen", "lopen", "on"
]

BOOLEAN_VALUES = ["yes", "no"]

SPECIAL_PARAMETER_VALUES = {
    "DEFAULT": "-",
    "CURRENT": "*",
    "AUTO_COM": "COM#"
}