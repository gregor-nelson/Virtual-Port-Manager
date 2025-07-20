"""Properties panel for displaying and editing port configuration."""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QComboBox, QCheckBox, QPushButton,
                            QGroupBox, QFormLayout, QTextEdit, QScrollArea,
                            QDoubleSpinBox, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ...core.models import PortPair, Port
from ...utils.constants import BOOLEAN_VALUES, PIN_ASSIGNMENT_VALUES


class PropertiesPanel(QScrollArea):
    """Properties panel for port configuration."""
    
    # Signals
    apply_changes = pyqtSignal(str, dict)  # (port_id, parameters)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_port = None
        self.current_pair = None
        self.parameter_widgets = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the properties panel UI."""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create header
        self.header_label = QLabel("Properties")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.header_label.setFont(font)
        self.main_layout.addWidget(self.header_label)
        
        # Create content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(10)
        self.main_layout.addWidget(self.content_widget)
        
        # Add stretch to push content to top
        self.main_layout.addStretch()
        
        self.setWidget(main_widget)
        
        # Show default content
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """Show welcome message when nothing is selected."""
        self.clear_content()
        self.header_label.setText("Properties")
        
        welcome_label = QLabel("Select a port pair or individual port to view and edit its properties.")
        welcome_label.setWordWrap(True)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: gray; font-style: italic; padding: 20px;")
        
        self.content_layout.addWidget(welcome_label)
    
    def show_port_pair_properties(self, pair: PortPair):
        """Display properties for a port pair."""
        self.clear_content()
        self.current_pair = pair
        self.current_port = None
        
        self.header_label.setText(f"Port Pair {pair.number} Properties")
        
        # Pair summary
        summary_group = QGroupBox("Pair Summary")
        summary_layout = QFormLayout(summary_group)
        
        summary_layout.addRow("Pair Number:", QLabel(str(pair.number)))
        summary_layout.addRow("Status:", QLabel(pair.status.value))
        summary_layout.addRow("Port A:", QLabel(f"{pair.port_a.identifier} → {pair.port_a.port_name or 'Not assigned'}"))
        summary_layout.addRow("Port B:", QLabel(f"{pair.port_b.identifier} → {pair.port_b.port_name or 'Not assigned'}"))
        
        self.content_layout.addWidget(summary_group)
        
        # Port A details
        port_a_group = QGroupBox(f"Port A ({pair.port_a.identifier})")
        port_a_layout = QVBoxLayout(port_a_group)
        port_a_details = self._create_port_details_widget(pair.port_a, read_only=True)
        port_a_layout.addWidget(port_a_details)
        
        self.content_layout.addWidget(port_a_group)
        
        # Port B details
        port_b_group = QGroupBox(f"Port B ({pair.port_b.identifier})")
        port_b_layout = QVBoxLayout(port_b_group)
        port_b_details = self._create_port_details_widget(pair.port_b, read_only=True)
        port_b_layout.addWidget(port_b_details)
        
        self.content_layout.addWidget(port_b_group)
    
    def show_port_properties(self, port: Port):
        """Display properties for an individual port."""
        self.clear_content()
        self.current_port = port
        self.current_pair = None
        
        self.header_label.setText(f"{port.identifier} Properties")
        
        # Port configuration form
        config_group = QGroupBox("Port Configuration")
        config_layout = QVBoxLayout(config_group)
        
        form_widget = self._create_port_configuration_form(port)
        config_layout.addWidget(form_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self._apply_changes)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self._reset_changes)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        
        config_layout.addLayout(button_layout)
        
        self.content_layout.addWidget(config_group)
    
    def _create_port_details_widget(self, port: Port, read_only: bool = True) -> QWidget:
        """Create a widget showing port details."""
        details_widget = QWidget()
        layout = QFormLayout(details_widget)
        
        # Port name
        port_name = port.port_name or "Not assigned"
        layout.addRow("Port Name:", QLabel(port_name))
        
        # Parameters
        if port.parameters:
            for key, value in port.parameters.items():
                layout.addRow(f"{key}:", QLabel(str(value)))
        else:
            layout.addRow("Parameters:", QLabel("Using default settings"))
        
        return details_widget
    
    def _create_port_configuration_form(self, port: Port) -> QWidget:
        """Create editable configuration form for a port."""
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        self.parameter_widgets = {}
        
        # Basic settings
        basic_group = QGroupBox("Basic Settings")
        basic_layout = QFormLayout(basic_group)
        
        # Port Name
        port_name_edit = QLineEdit(port.port_name or "")
        port_name_edit.setPlaceholderText("e.g., COM8 or COM# for auto-assign")
        self.parameter_widgets["PortName"] = port_name_edit
        basic_layout.addRow("Port Name:", port_name_edit)
        
        form_layout.addWidget(basic_group)
        
        # Emulation settings
        emulation_group = QGroupBox("Emulation Settings")
        emulation_layout = QFormLayout(emulation_group)
        
        # EmuBR
        emubr_combo = QComboBox()
        emubr_combo.addItems(BOOLEAN_VALUES)
        emubr_combo.setCurrentText(port.get_parameter("EmuBR", "no"))
        self.parameter_widgets["EmuBR"] = emubr_combo
        emulation_layout.addRow("Baud Rate Emulation:", emubr_combo)
        
        # EmuOverrun
        overrun_combo = QComboBox()
        overrun_combo.addItems(BOOLEAN_VALUES)
        overrun_combo.setCurrentText(port.get_parameter("EmuOverrun", "no"))
        self.parameter_widgets["EmuOverrun"] = overrun_combo
        emulation_layout.addRow("Buffer Overrun:", overrun_combo)
        
        # EmuNoise
        noise_spin = QDoubleSpinBox()
        noise_spin.setRange(0.0, 0.99999999)
        noise_spin.setDecimals(8)
        noise_spin.setSingleStep(0.001)
        noise_spin.setValue(float(port.get_parameter("EmuNoise", "0")))
        self.parameter_widgets["EmuNoise"] = noise_spin
        emulation_layout.addRow("Noise Level:", noise_spin)
        
        form_layout.addWidget(emulation_group)
        
        # Timing settings
        timing_group = QGroupBox("Timing Settings")
        timing_layout = QFormLayout(timing_group)
        
        # AddRTTO
        rtto_spin = QSpinBox()
        rtto_spin.setRange(0, 99999)
        rtto_spin.setSuffix(" ms")
        rtto_spin.setValue(int(port.get_parameter("AddRTTO", "0")))
        self.parameter_widgets["AddRTTO"] = rtto_spin
        timing_layout.addRow("Read Total Timeout:", rtto_spin)
        
        # AddRITO
        rito_spin = QSpinBox()
        rito_spin.setRange(0, 99999)
        rito_spin.setSuffix(" ms")
        rito_spin.setValue(int(port.get_parameter("AddRITO", "0")))
        self.parameter_widgets["AddRITO"] = rito_spin
        timing_layout.addRow("Read Interval Timeout:", rito_spin)
        
        form_layout.addWidget(timing_group)
        
        # Mode settings
        mode_group = QGroupBox("Mode Settings")
        mode_layout = QFormLayout(mode_group)
        
        # PlugInMode
        plugin_check = QCheckBox()
        plugin_check.setChecked(port.get_parameter("PlugInMode", "no") == "yes")
        self.parameter_widgets["PlugInMode"] = plugin_check
        mode_layout.addRow("Plug-in Mode:", plugin_check)
        
        # ExclusiveMode
        exclusive_check = QCheckBox()
        exclusive_check.setChecked(port.get_parameter("ExclusiveMode", "no") == "yes")
        self.parameter_widgets["ExclusiveMode"] = exclusive_check
        mode_layout.addRow("Exclusive Mode:", exclusive_check)
        
        # HiddenMode
        hidden_check = QCheckBox()
        hidden_check.setChecked(port.get_parameter("HiddenMode", "no") == "yes")
        self.parameter_widgets["HiddenMode"] = hidden_check
        mode_layout.addRow("Hidden Mode:", hidden_check)
        
        # AllDataBits
        databits_check = QCheckBox()
        databits_check.setChecked(port.get_parameter("AllDataBits", "no") == "yes")
        self.parameter_widgets["AllDataBits"] = databits_check
        mode_layout.addRow("All Data Bits:", databits_check)
        
        form_layout.addWidget(mode_group)
        
        # Pin wiring settings
        wiring_group = QGroupBox("Pin Wiring")
        wiring_layout = QFormLayout(wiring_group)
        
        for pin in ["cts", "dsr", "dcd", "ri"]:
            pin_widget = self._create_pin_assignment_widget(port, pin)
            self.parameter_widgets[pin] = pin_widget
            wiring_layout.addRow(f"{pin.upper()}:", pin_widget)
        
        form_layout.addWidget(wiring_group)
        
        return form_widget
    
    def _create_pin_assignment_widget(self, port: Port, pin: str) -> QWidget:
        """Create pin assignment widget with combo and invert checkbox."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Get current value
        current_value = port.get_parameter(pin, "rrts" if pin == "cts" else "rdtr" if pin in ["dsr", "dcd"] else "!on")
        inverted = current_value.startswith("!")
        clean_value = current_value[1:] if inverted else current_value
        
        # Combo box for pin assignment
        combo = QComboBox()
        combo.addItems(PIN_ASSIGNMENT_VALUES)
        if clean_value in PIN_ASSIGNMENT_VALUES:
            combo.setCurrentText(clean_value)
        
        # Checkbox for inversion
        invert_check = QCheckBox("Invert")
        invert_check.setChecked(inverted)
        
        layout.addWidget(combo)
        layout.addWidget(invert_check)
        
        # Store both widgets for retrieval
        widget.combo = combo
        widget.invert_check = invert_check
        
        return widget
    
    def _apply_changes(self):
        """Apply configuration changes."""
        if not self.current_port:
            return
        
        # Collect parameters from widgets
        parameters = {}
        
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
            elif hasattr(widget, 'combo'):  # Pin assignment widget
                combo_value = widget.combo.currentText()
                if widget.invert_check.isChecked():
                    value = f"!{combo_value}"
                else:
                    value = combo_value
                parameters[param_name] = value
        
        # Emit signal with changes
        self.apply_changes.emit(self.current_port.identifier, parameters)
    
    def _reset_changes(self):
        """Reset form to original values."""
        if self.current_port:
            self.show_port_properties(self.current_port)
    
    def clear_content(self):
        """Clear the content area."""
        # Remove all widgets from content layout
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.parameter_widgets = {}
    
    def show_driver_info(self):
        """Show driver information."""
        self.clear_content()
        self.current_port = None
        self.current_pair = None
        
        self.header_label.setText("Driver Information")
        
        info_label = QLabel("com0com driver information will be displayed here.")
        info_label.setWordWrap(True)
        self.content_layout.addWidget(info_label)