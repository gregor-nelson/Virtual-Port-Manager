"""Dialog for configuring existing ports."""

from typing import Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QSpinBox, QCheckBox, QComboBox, QLabel,
                            QPushButton, QGroupBox, QMessageBox, QFrame,
                            QDialogButtonBox, QDoubleSpinBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ...core.models import Port, PortPair
from ...core.validators import ParameterValidator
from ...utils.constants import BOOLEAN_VALUES, PIN_ASSIGNMENT_VALUES


class ConfigurePortDialog(QDialog):
    """Dialog for configuring an existing port."""
    
    # Signal emitted when configuration should be applied
    apply_configuration = pyqtSignal(str, dict)  # (port_id, parameters)
    
    def __init__(self, port: Port, parent=None):
        super().__init__(parent)
        self.port = port
        self.parameter_widgets = {}
        
        self.setWindowTitle(f"Configure {port.identifier}")
        self.setModal(True)
        self.resize(450, 630)
        self.setup_ui()
        self.populate_current_values()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(f"Configure {self.port.identifier}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(f"Modify the configuration parameters for virtual port {self.port.identifier}.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: gray; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Create scroll area for all configuration content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create container widget for scrollable content
        scroll_content = QFrame()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)
        
        # Current status
        status_group = QGroupBox("Current Status")
        status_layout = QFormLayout(status_group)
        
        current_name = self.port.port_name or "Not assigned"
        status_layout.addRow("Port Name:", QLabel(current_name))
        status_layout.addRow("Identifier:", QLabel(self.port.identifier))
        
        scroll_layout.addWidget(status_group)
        
        # Configuration form
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout(config_group)
        
        form_widget = self.create_configuration_form()
        config_layout.addWidget(form_widget)
        
        scroll_layout.addWidget(config_group)
        
        # Set the scroll content and add scroll area to main layout
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Reset
        )
        
        self.apply_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.apply_button.setText("Apply Changes")
        
        self.reset_button = button_box.button(QDialogButtonBox.StandardButton.Reset)
        
        layout.addWidget(button_box)
        
        # Connect button signals
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.reset_button.clicked.connect(self.reset_to_current)
    
    def create_configuration_form(self):
        """Create the configuration form."""
        form_widget = QFrame()
        layout = QVBoxLayout(form_widget)
        layout.setSpacing(15)
        
        # Basic settings
        basic_group = QGroupBox("Basic Settings")
        basic_layout = QFormLayout(basic_group)
        
        # Port Name
        self.port_name_edit = QLineEdit()
        self.port_name_edit.setPlaceholderText("e.g., COM8 or COM# for auto-assign")
        self.parameter_widgets["PortName"] = self.port_name_edit
        basic_layout.addRow("Port Name:", self.port_name_edit)
        
        layout.addWidget(basic_group)
        
        # Emulation settings
        emulation_group = QGroupBox("Emulation Settings")
        emulation_layout = QFormLayout(emulation_group)
        
        # EmuBR
        self.emubr_combo = QComboBox()
        self.emubr_combo.addItems(BOOLEAN_VALUES)
        self.parameter_widgets["EmuBR"] = self.emubr_combo
        emulation_layout.addRow("Baud Rate Emulation:", self.emubr_combo)
        
        # EmuOverrun
        self.overrun_combo = QComboBox()
        self.overrun_combo.addItems(BOOLEAN_VALUES)
        self.parameter_widgets["EmuOverrun"] = self.overrun_combo
        emulation_layout.addRow("Buffer Overrun:", self.overrun_combo)
        
        # EmuNoise
        self.noise_spin = QDoubleSpinBox()
        self.noise_spin.setRange(0.0, 0.99999999)
        self.noise_spin.setDecimals(8)
        self.noise_spin.setSingleStep(0.001)
        self.parameter_widgets["EmuNoise"] = self.noise_spin
        emulation_layout.addRow("Noise Level:", self.noise_spin)
        
        layout.addWidget(emulation_group)
        
        # Timing settings
        timing_group = QGroupBox("Timing Settings")
        timing_layout = QFormLayout(timing_group)
        
        # AddRTTO
        self.rtto_spin = QSpinBox()
        self.rtto_spin.setRange(0, 99999)
        self.rtto_spin.setSuffix(" ms")
        self.parameter_widgets["AddRTTO"] = self.rtto_spin
        timing_layout.addRow("Read Total Timeout:", self.rtto_spin)
        
        # AddRITO
        self.rito_spin = QSpinBox()
        self.rito_spin.setRange(0, 99999)
        self.rito_spin.setSuffix(" ms")
        self.parameter_widgets["AddRITO"] = self.rito_spin
        timing_layout.addRow("Read Interval Timeout:", self.rito_spin)
        
        layout.addWidget(timing_group)
        
        # Mode settings
        mode_group = QGroupBox("Mode Settings")
        mode_layout = QFormLayout(mode_group)
        
        # PlugInMode
        self.plugin_check = QCheckBox()
        self.parameter_widgets["PlugInMode"] = self.plugin_check
        mode_layout.addRow("Plug-in Mode:", self.plugin_check)
        
        # ExclusiveMode
        self.exclusive_check = QCheckBox()
        self.parameter_widgets["ExclusiveMode"] = self.exclusive_check
        mode_layout.addRow("Exclusive Mode:", self.exclusive_check)
        
        # HiddenMode
        self.hidden_check = QCheckBox()
        self.parameter_widgets["HiddenMode"] = self.hidden_check
        mode_layout.addRow("Hidden Mode:", self.hidden_check)
        
        # AllDataBits
        self.databits_check = QCheckBox()
        self.parameter_widgets["AllDataBits"] = self.databits_check
        mode_layout.addRow("All Data Bits:", self.databits_check)
        
        layout.addWidget(mode_group)
        
        # Pin wiring settings
        wiring_group = QGroupBox("Pin Wiring")
        wiring_layout = QFormLayout(wiring_group)
        
        self.pin_widgets = {}
        for pin in ["cts", "dsr", "dcd", "ri"]:
            pin_widget = self.create_pin_assignment_widget(pin)
            self.pin_widgets[pin] = pin_widget
            wiring_layout.addRow(f"{pin.upper()}:", pin_widget)
        
        layout.addWidget(wiring_group)
        
        return form_widget
    
    def create_pin_assignment_widget(self, pin: str):
        """Create pin assignment widget with combo and invert checkbox."""
        widget = QFrame()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Combo box for pin assignment
        combo = QComboBox()
        combo.addItems(PIN_ASSIGNMENT_VALUES)
        
        # Checkbox for inversion
        invert_check = QCheckBox("Invert")
        
        layout.addWidget(combo)
        layout.addWidget(invert_check)
        
        # Store both widgets for retrieval
        widget.combo = combo
        widget.invert_check = invert_check
        
        return widget
    
    def populate_current_values(self):
        """Populate form with current port values."""
        # Basic settings
        if self.port.port_name:
            self.port_name_edit.setText(self.port.port_name)
        
        # Emulation settings
        self.emubr_combo.setCurrentText(self.port.get_parameter("EmuBR", "no"))
        self.overrun_combo.setCurrentText(self.port.get_parameter("EmuOverrun", "no"))
        self.noise_spin.setValue(float(self.port.get_parameter("EmuNoise", "0")))
        
        # Timing settings
        self.rtto_spin.setValue(int(self.port.get_parameter("AddRTTO", "0")))
        self.rito_spin.setValue(int(self.port.get_parameter("AddRITO", "0")))
        
        # Mode settings
        self.plugin_check.setChecked(self.port.get_parameter("PlugInMode", "no") == "yes")
        self.exclusive_check.setChecked(self.port.get_parameter("ExclusiveMode", "no") == "yes")
        self.hidden_check.setChecked(self.port.get_parameter("HiddenMode", "no") == "yes")
        self.databits_check.setChecked(self.port.get_parameter("AllDataBits", "no") == "yes")
        
        # Pin wiring
        for pin, widget in self.pin_widgets.items():
            default_value = "rrts" if pin == "cts" else "rdtr" if pin in ["dsr", "dcd"] else "!on"
            current_value = self.port.get_parameter(pin, default_value)
            
            inverted = current_value.startswith("!")
            clean_value = current_value[1:] if inverted else current_value
            
            if clean_value in PIN_ASSIGNMENT_VALUES:
                widget.combo.setCurrentText(clean_value)
            widget.invert_check.setChecked(inverted)
    
    def get_configuration_parameters(self) -> Dict[str, Any]:
        """Get configuration parameters from form."""
        parameters = {}
        
        # Collect parameters from widgets
        for param_name, widget in self.parameter_widgets.items():
            if isinstance(widget, QLineEdit):
                value = widget.text().strip()
                if value:
                    parameters[param_name] = value
            elif isinstance(widget, QComboBox):
                parameters[param_name] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                parameters[param_name] = "yes" if widget.isChecked() else "no"
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
                if value != 0:  # Only include non-zero values
                    parameters[param_name] = str(value)
        
        # Pin assignments
        for pin, widget in self.pin_widgets.items():
            combo_value = widget.combo.currentText()
            if widget.invert_check.isChecked():
                value = f"!{combo_value}"
            else:
                value = combo_value
            parameters[pin] = value
        
        return parameters
    
    def validate_configuration(self) -> tuple[bool, str]:
        """Validate the configuration."""
        parameters = self.get_configuration_parameters()
        
        # Build parameter string for validation
        param_pairs = []
        for key, value in parameters.items():
            if value is not None and value != "":
                param_pairs.append(f"{key}={value}")
        
        param_string = ",".join(param_pairs) if param_pairs else "-"
        
        if param_string != "-":
            return ParameterValidator.validate_parameter_string(param_string)
        
        return True, ""
    
    def reset_to_current(self):
        """Reset form to current port values."""
        self.populate_current_values()
    
    def accept(self):
        """Handle dialog acceptance."""
        # Validate configuration
        valid, error = self.validate_configuration()
        if not valid:
            QMessageBox.warning(self, "Invalid Configuration", error)
            return
        
        # Get parameters
        parameters = self.get_configuration_parameters()
        
        # Check if there are any changes
        if not self.has_changes(parameters):
            QMessageBox.information(self, "No Changes", "No configuration changes were made.")
            super().reject()
            return
        
        # Emit signal
        self.apply_configuration.emit(self.port.identifier, parameters)
        
        super().accept()
    
    def has_changes(self, new_parameters: Dict[str, Any]) -> bool:
        """Check if the configuration has changed."""
        # Compare with current port parameters
        for key, new_value in new_parameters.items():
            current_value = self.port.get_parameter(key, "")
            if str(new_value) != str(current_value):
                return True
        
        return False