"""Dialog for creating new virtual port pairs."""

from typing import Optional, Tuple
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QSpinBox, QCheckBox, QComboBox, QLabel,
                            QPushButton, QGroupBox, QMessageBox, QFrame,
                            QDialogButtonBox, QTabWidget, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ...core.validators import ParameterValidator
from ...utils.constants import BOOLEAN_VALUES, PIN_ASSIGNMENT_VALUES


class NewPortDialog(QDialog):
    """Dialog for creating new virtual port pairs."""
    
    # Signal emitted when port pair should be created
    create_port_pair = pyqtSignal(object, str, str)  # (pair_number_or_None, params_a, params_b)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Port Pair")
        self.setModal(True)
        self.resize(500, 600)
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Create New Virtual Port Pair")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Configure the settings for your new virtual port pair. "
                           "Each pair consists of two connected virtual COM ports (A and B).")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: gray; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Pair settings group
        pair_group = QGroupBox("Pair Settings")
        pair_layout = QFormLayout(pair_group)
        
        # Auto or manual pair number
        self.auto_number_check = QCheckBox("Auto-assign pair number")
        self.auto_number_check.setChecked(True)
        pair_layout.addRow("", self.auto_number_check)
        
        # Manual pair number
        self.pair_number_spin = QSpinBox()
        self.pair_number_spin.setRange(0, 999)
        self.pair_number_spin.setValue(0)
        self.pair_number_spin.setEnabled(False)
        pair_layout.addRow("Pair Number:", self.pair_number_spin)
        
        layout.addWidget(pair_group)
        
        # Port configuration tabs
        self.tab_widget = QTabWidget()
        
        # Port A tab
        self.port_a_tab = self.create_port_config_tab("A")
        self.tab_widget.addTab(self.port_a_tab, "Port A (CNCA)")
        
        # Port B tab
        self.port_b_tab = self.create_port_config_tab("B")
        self.tab_widget.addTab(self.port_b_tab, "Port B (CNCB)")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        
        self.create_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.create_button.setText("Create Port Pair")
        
        layout.addWidget(button_box)
        
        # Connect button signals
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
    
    def create_port_config_tab(self, port_letter: str) -> QWidget:
        """Create configuration tab for a port."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        # Store widgets in tab for later access
        tab.widgets = {}
        
        # Basic settings
        basic_group = QGroupBox("Basic Settings")
        basic_layout = QFormLayout(basic_group)
        
        # Port name
        port_name_edit = QLineEdit()
        port_name_edit.setPlaceholderText("e.g., COM8 or COM# for auto-assign")
        tab.widgets["PortName"] = port_name_edit
        basic_layout.addRow("Port Name:", port_name_edit)
        
        layout.addWidget(basic_group)
        
        # Emulation settings
        emulation_group = QGroupBox("Emulation Settings")
        emulation_layout = QFormLayout(emulation_group)
        
        # Baud rate emulation
        emubr_combo = QComboBox()
        emubr_combo.addItems(BOOLEAN_VALUES)
        emubr_combo.setCurrentText("no")
        tab.widgets["EmuBR"] = emubr_combo
        emulation_layout.addRow("Baud Rate Emulation:", emubr_combo)
        
        # Buffer overrun
        overrun_combo = QComboBox()
        overrun_combo.addItems(BOOLEAN_VALUES)
        overrun_combo.setCurrentText("no")
        tab.widgets["EmuOverrun"] = overrun_combo
        emulation_layout.addRow("Buffer Overrun:", overrun_combo)
        
        layout.addWidget(emulation_group)
        
        # Mode settings
        mode_group = QGroupBox("Mode Settings")
        mode_layout = QFormLayout(mode_group)
        
        # Plug-in mode
        plugin_check = QCheckBox()
        tab.widgets["PlugInMode"] = plugin_check
        mode_layout.addRow("Plug-in Mode:", plugin_check)
        
        # Exclusive mode
        exclusive_check = QCheckBox()
        tab.widgets["ExclusiveMode"] = exclusive_check
        mode_layout.addRow("Exclusive Mode:", exclusive_check)
        
        # Hidden mode
        hidden_check = QCheckBox()
        tab.widgets["HiddenMode"] = hidden_check
        mode_layout.addRow("Hidden Mode:", hidden_check)
        
        layout.addWidget(mode_group)
        
        # Add stretch to push content to top
        layout.addStretch()
        
        return tab
    
    def setup_connections(self):
        """Set up signal connections."""
        self.auto_number_check.toggled.connect(self.on_auto_number_toggled)
    
    def on_auto_number_toggled(self, checked: bool):
        """Handle auto number checkbox toggle."""
        self.pair_number_spin.setEnabled(not checked)
    
    def get_port_parameters(self, tab: QWidget) -> str:
        """Extract parameters from a port configuration tab."""
        parameters = []
        
        for param_name, widget in tab.widgets.items():
            value = None
            
            if isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:
                    value = text
            elif isinstance(widget, QComboBox):
                if widget.currentText() != "no":  # Only include non-default values
                    value = widget.currentText()
            elif isinstance(widget, QCheckBox):
                if widget.isChecked():
                    value = "yes"
            
            if value:
                parameters.append(f"{param_name}={value}")
        
        return ",".join(parameters) if parameters else "-"
    
    def validate_input(self) -> Tuple[bool, str]:
        """Validate the dialog input."""
        # Validate pair number if manual
        if not self.auto_number_check.isChecked():
            pair_number = self.pair_number_spin.value()
            valid, error = ParameterValidator.validate_port_number(pair_number)
            if not valid:
                return False, f"Invalid pair number: {error}"
        
        # Validate port parameters
        for port_letter, tab in [("A", self.port_a_tab), ("B", self.port_b_tab)]:
            params = self.get_port_parameters(tab)
            if params != "-":
                valid, error = ParameterValidator.validate_parameter_string(params)
                if not valid:
                    return False, f"Invalid parameters for Port {port_letter}: {error}"
        
        return True, ""
    
    def accept(self):
        """Handle dialog acceptance."""
        # Validate input
        valid, error = self.validate_input()
        if not valid:
            QMessageBox.warning(self, "Invalid Input", error)
            return
        
        # Get parameters
        pair_number = None if self.auto_number_check.isChecked() else self.pair_number_spin.value()
        params_a = self.get_port_parameters(self.port_a_tab)
        params_b = self.get_port_parameters(self.port_b_tab)
        
        # Emit signal
        self.create_port_pair.emit(pair_number, params_a, params_b)
        
        super().accept()
    
    def reset_form(self):
        """Reset the form to default values."""
        self.auto_number_check.setChecked(True)
        self.pair_number_spin.setValue(0)
        
        for tab in [self.port_a_tab, self.port_b_tab]:
            for widget in tab.widgets.values():
                if isinstance(widget, QLineEdit):
                    widget.clear()
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText("no")
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(False)