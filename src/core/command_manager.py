"""Command manager for interfacing with setupc.exe."""

import subprocess
import threading
import time
import os
from typing import List, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer

from .models import PortPair, CommandResult, DriverInfo, DriverStatus, PortListParser
from .validators import ParameterValidator
from ..utils.constants import DEFAULT_SETUPC_PATH, DEFAULT_COMMAND_TIMEOUT, SETUPC_COMMANDS


class SetupCommandWorker(QThread):
    """Worker thread for executing setupc.exe commands."""
    
    command_finished = pyqtSignal(CommandResult)
    
    def __init__(self, command: str, timeout: int = DEFAULT_COMMAND_TIMEOUT, working_directory: Optional[str] = None):
        super().__init__()
        self.command = command
        self.timeout = timeout
        self.working_directory = working_directory
        self.result = None
    
    def run(self):
        """Execute the command in background thread."""
        start_time = time.time()
        
        try:
            result = subprocess.run(
                self.command.split(),
                capture_output=True,
                text=True,
                timeout=self.timeout,
                shell=False,  # Security: don't use shell
                cwd=self.working_directory  # Set working directory for .inf file access
            )
            
            execution_time = time.time() - start_time
            
            command_result = CommandResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
                command=self.command
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            command_result = CommandResult(
                success=False,
                output="",
                error=f"Command timed out after {self.timeout} seconds",
                return_code=-1,
                execution_time=execution_time,
                command=self.command
            )
            
        except FileNotFoundError:
            execution_time = time.time() - start_time
            command_result = CommandResult(
                success=False,
                output="",
                error="setupc.exe not found. Please ensure com0com is installed and setupc.exe is in your PATH.",
                return_code=-2,
                execution_time=execution_time,
                command=self.command
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            command_result = CommandResult(
                success=False,
                output="",
                error=f"Unexpected error: {str(e)}",
                return_code=-3,
                execution_time=execution_time,
                command=self.command
            )
        
        self.result = command_result
        self.command_finished.emit(command_result)


class CommandManager(QObject):
    """Manager for setupc.exe command execution and port management."""
    
    # Signals for UI updates
    port_list_updated = pyqtSignal(list)  # List[PortPair]
    command_completed = pyqtSignal(CommandResult)
    driver_status_changed = pyqtSignal(DriverInfo)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, setupc_path: str = DEFAULT_SETUPC_PATH):
        super().__init__()
        self.setupc_path = setupc_path
        self.timeout = DEFAULT_COMMAND_TIMEOUT
        self.current_worker = None
        self._port_pairs_cache = []
        
    def set_setupc_path(self, path: str) -> None:
        """Set the path to setupc.exe."""
        self.setupc_path = path
    
    def set_timeout(self, timeout: int) -> None:
        """Set command execution timeout."""
        if timeout > 0:
            self.timeout = timeout
    
    
    def _execute_command_async(self, command: str, callback: Optional[Callable] = None) -> None:
        """Execute setupc command asynchronously."""
        if self.current_worker and self.current_worker.isRunning():
            self.error_occurred.emit("Another command is already running. Please wait.")
            return
        
        full_command = f"{self.setupc_path} {command}"
        
        # Extract working directory from setupc.exe path for .inf file access
        working_directory = os.path.dirname(self.setupc_path) if self.setupc_path else None
        
        self.current_worker = SetupCommandWorker(full_command, self.timeout, working_directory)
        self.current_worker.command_finished.connect(self._on_command_finished)
        
        if callback:
            self.current_worker.command_finished.connect(callback)
        
        self.current_worker.start()
    
    def _on_command_finished(self, result: CommandResult) -> None:
        """Handle command completion."""
        self.command_completed.emit(result)
        
        if not result.success:
            self.error_occurred.emit(result.get_error_message())
    
    def list_ports(self) -> None:
        """Get all current port pairs asynchronously."""
        def handle_list_result(result: CommandResult):
            if result.success:
                try:
                    port_pairs = PortListParser.parse_port_list(result.output)
                    self._port_pairs_cache = port_pairs
                    self.port_list_updated.emit(port_pairs)
                except Exception as e:
                    self.error_occurred.emit(f"Failed to parse port list: {str(e)}")
            else:
                self.error_occurred.emit(f"Failed to list ports: {result.get_error_message()}")
        
        self._execute_command_async(SETUPC_COMMANDS["LIST"], handle_list_result)
    
    def refresh_port_list(self) -> None:
        """Refresh the port list (convenience method)."""
        self.list_ports()
    
    def get_cached_port_pairs(self) -> List[PortPair]:
        """Get the last cached port pairs list."""
        return self._port_pairs_cache.copy()
    
    def install_port_pair(self, pair_number: Optional[int] = None, 
                         params_a: str = "-", params_b: str = "-") -> None:
        """Install new port pair."""
        # Validate parameters
        if params_a != "-":
            valid, error = ParameterValidator.validate_parameter_string(params_a)
            if not valid:
                self.error_occurred.emit(f"Invalid parameters for port A: {error}")
                return
        
        if params_b != "-":
            valid, error = ParameterValidator.validate_parameter_string(params_b)
            if not valid:
                self.error_occurred.emit(f"Invalid parameters for port B: {error}")
                return
        
        # Build command
        if pair_number is not None:
            valid, error = ParameterValidator.validate_port_number(pair_number)
            if not valid:
                self.error_occurred.emit(f"Invalid port number: {error}")
                return
            command = SETUPC_COMMANDS["INSTALL_NUMBERED"].format(pair_number, params_a, params_b)
        else:
            command = SETUPC_COMMANDS["INSTALL_AUTO"].format(params_a, params_b)
        
        def handle_install_result(result: CommandResult):
            if result.success:
                # Refresh port list after successful installation
                self.list_ports()
            else:
                self.error_occurred.emit(f"Failed to install port pair: {result.get_error_message()}")
        
        self._execute_command_async(command, handle_install_result)
    
    def remove_port_pair(self, pair_number: int) -> None:
        """Remove existing port pair."""
        valid, error = ParameterValidator.validate_port_number(pair_number)
        if not valid:
            self.error_occurred.emit(f"Invalid port number: {error}")
            return
        
        command = SETUPC_COMMANDS["REMOVE"].format(pair_number)
        
        def handle_remove_result(result: CommandResult):
            if result.success:
                # Refresh port list after successful removal
                self.list_ports()
            else:
                self.error_occurred.emit(f"Failed to remove port pair: {result.get_error_message()}")
        
        self._execute_command_async(command, handle_remove_result)
    
    def change_port_config(self, port_id: str, parameters: str) -> None:
        """Modify port parameters."""
        valid, error = ParameterValidator.validate_port_identifier(port_id)
        if not valid:
            self.error_occurred.emit(f"Invalid port identifier: {error}")
            return
        
        valid, error = ParameterValidator.validate_parameter_string(parameters)
        if not valid:
            self.error_occurred.emit(f"Invalid parameters: {error}")
            return
        
        command = SETUPC_COMMANDS["CHANGE"].format(port_id, parameters)
        
        def handle_change_result(result: CommandResult):
            if result.success:
                # Refresh port list after successful change
                self.list_ports()
            else:
                self.error_occurred.emit(f"Failed to change port configuration: {result.get_error_message()}")
        
        self._execute_command_async(command, handle_change_result)
    
    def get_driver_status(self) -> None:
        """Check driver installation status."""
        def handle_list_result(result: CommandResult):
            if result.success:
                # If list command works, driver is installed
                driver_info = DriverInfo(
                    status=DriverStatus.INSTALLED,
                    install_path=self.setupc_path
                )
            else:
                # Determine error type
                if "not found" in result.error.lower():
                    driver_info = DriverInfo(
                        status=DriverStatus.NOT_INSTALLED,
                        error_message="setupc.exe not found"
                    )
                else:
                    driver_info = DriverInfo(
                        status=DriverStatus.ERROR,
                        error_message=result.get_error_message()
                    )
            
            self.driver_status_changed.emit(driver_info)
        
        self._execute_command_async(SETUPC_COMMANDS["LIST"], handle_list_result)
    
    def preinstall_driver(self) -> None:
        """Preinstall the driver."""
        def handle_preinstall_result(result: CommandResult):
            if result.success:
                # Update driver status after successful preinstall (delayed)
                QTimer.singleShot(50, self.get_driver_status)
        
        self._execute_command_async(SETUPC_COMMANDS["PREINSTALL"], handle_preinstall_result)
    
    def update_driver(self) -> None:
        """Update the driver."""
        def handle_update_result(result: CommandResult):
            if result.success:
                # Update driver status after successful update (delayed)
                QTimer.singleShot(50, self.get_driver_status)
        
        self._execute_command_async(SETUPC_COMMANDS["UPDATE"], handle_update_result)
    
    def reload_driver(self) -> None:
        """Reload the driver."""
        def handle_reload_result(result: CommandResult):
            if result.success:
                # Refresh port list after successful reload
                self.list_ports()
                # Status will be updated when the list command completes
        
        self._execute_command_async(SETUPC_COMMANDS["RELOAD"], handle_reload_result)
    
    def uninstall_driver(self) -> None:
        """Uninstall all ports and driver."""
        def handle_uninstall_result(result: CommandResult):
            if result.success:
                # Clear port list cache and emit empty list
                self._port_pairs_cache = []
                self.port_list_updated.emit([])
                # Update driver status after successful uninstall (delayed)
                QTimer.singleShot(50, self.get_driver_status)
        
        self._execute_command_async(SETUPC_COMMANDS["UNINSTALL"], handle_uninstall_result)
    
    def disable_all_ports(self) -> None:
        """Disable all ports in current hardware profile."""
        def handle_disable_result(result: CommandResult):
            if result.success:
                # Refresh port list after successful disable
                self.list_ports()
        
        self._execute_command_async(SETUPC_COMMANDS["DISABLE_ALL"], handle_disable_result)
    
    def enable_all_ports(self) -> None:
        """Enable all ports in current hardware profile."""
        def handle_enable_result(result: CommandResult):
            if result.success:
                # Refresh port list after successful enable
                self.list_ports()
        
        self._execute_command_async(SETUPC_COMMANDS["ENABLE_ALL"], handle_enable_result)
    
    def is_busy(self) -> bool:
        """Check if a command is currently executing."""
        return self.current_worker is not None and self.current_worker.isRunning()
    
    def cancel_current_command(self) -> None:
        """Cancel the currently running command."""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait(3000)  # Wait up to 3 seconds
            if self.current_worker.isRunning():
                self.current_worker.kill()  # Force kill if still running
    
    # Utility Commands
    def clean_inf_files(self) -> None:
        """Clean old INF files using setupc.exe infclean."""
        def handle_infclean_result(result: CommandResult):
            if result.success:
                # Success feedback is handled by the command_completed signal
                pass
            else:
                self.error_occurred.emit(f"Failed to clean INF files: {result.get_error_message()}")
        
        self._execute_command_async(SETUPC_COMMANDS["INFCLEAN"], handle_infclean_result)
    
    def list_friendly_names(self) -> None:
        """Get friendly names using setupc.exe listfnames."""
        def handle_listfnames_result(result: CommandResult):
            if not result.success:
                self.error_occurred.emit(f"Failed to list friendly names: {result.get_error_message()}")
        
        self._execute_command_async(SETUPC_COMMANDS["LISTFNAMES"], handle_listfnames_result)
    
    def check_busy_names(self, pattern: str) -> None:
        """Check names in use using setupc.exe busynames."""
        if not pattern.strip():
            self.error_occurred.emit("Pattern cannot be empty for busy names check")
            return
        
        def handle_busynames_result(result: CommandResult):
            if not result.success:
                self.error_occurred.emit(f"Failed to check busy names: {result.get_error_message()}")
        
        command = SETUPC_COMMANDS["BUSYNAMES"].format(pattern)
        self._execute_command_async(command, handle_busynames_result)
    
    def update_friendly_names(self) -> None:
        """Update friendly names using setupc.exe updatefnames."""
        def handle_updatefnames_result(result: CommandResult):
            if result.success:
                # Refresh port list after updating friendly names
                self.list_ports()
            else:
                self.error_occurred.emit(f"Failed to update friendly names: {result.get_error_message()}")
        
        self._execute_command_async(SETUPC_COMMANDS["UPDATEFNAMES"], handle_updatefnames_result)