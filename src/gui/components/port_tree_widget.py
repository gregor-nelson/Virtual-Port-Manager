"""Port tree widget for displaying virtual port pairs."""

from typing import List, Optional
from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QHeaderView, 
                            QMenu, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from ...core.models import PortPair, Port, PortStatus


class PortTreeWidget(QTreeWidget):
    """Tree widget for displaying com0com virtual port pairs."""
    
    # Signals
    port_pair_selected = pyqtSignal(PortPair)
    port_selected = pyqtSignal(Port)
    port_pair_double_clicked = pyqtSignal(PortPair)
    context_menu_requested = pyqtSignal(object, object)  # (item_type, item_data)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.port_pairs = []
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Initialize the tree widget UI."""
        # Set up columns
        self.setHeaderLabels(["Port", "Status", "Parameters"])
        self.setColumnCount(3)
        
        # Configure tree appearance
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # Set column widths
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # Set initial column widths
        self.setColumnWidth(0, 250)
        self.setColumnWidth(1, 100)
        
        # Create root item
        self.create_root_item()
    
    def setup_connections(self):
        """Set up signal connections."""
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)
    
    def create_root_item(self):
        """Create the root tree item."""
        self.clear()
        root_item = QTreeWidgetItem(["com0com Virtual Ports", "", ""])
        root_item.setData(0, Qt.ItemDataRole.UserRole, "root")
        self.addTopLevelItem(root_item)
        self.expandItem(root_item)
    
    def update_port_pairs(self, port_pairs: List[PortPair]):
        """Update the tree with new port pair data."""
        self.port_pairs = port_pairs
        
        # Clear existing items (except root)
        root_item = self.topLevelItem(0)
        root_item.takeChildren()
        
        # Update root item text with count
        count = len(port_pairs)
        root_item.setText(0, f"com0com Virtual Ports ({count} pair{'s' if count != 1 else ''})")
        
        # Add port pairs
        for pair in port_pairs:
            self._add_port_pair_item(root_item, pair)
        
        # Expand all items
        self.expandAll()
    
    def _add_port_pair_item(self, parent_item: QTreeWidgetItem, pair: PortPair):
        """Add a port pair item to the tree."""
        # Create pair item
        pair_name = f"Pair {pair.number}"
        status_text = pair.status.value
        pair_info = f"{pair.port_a.port_name or pair.port_a.identifier} ↔ {pair.port_b.port_name or pair.port_b.identifier}"
        
        pair_item = QTreeWidgetItem([pair_name, status_text, pair_info])
        pair_item.setData(0, Qt.ItemDataRole.UserRole, ("pair", pair))
        
        # Set status-based styling
        self._set_status_styling(pair_item, pair.status)
        
        parent_item.addChild(pair_item)
        
        # Add individual port items
        self._add_port_item(pair_item, pair.port_a, f"Port A ({pair.port_a.identifier})")
        self._add_port_item(pair_item, pair.port_b, f"Port B ({pair.port_b.identifier})")
    
    def _add_port_item(self, parent_item: QTreeWidgetItem, port: Port, display_name: str):
        """Add an individual port item to the tree."""
        port_name = port.port_name or "Not assigned"
        parameters = self._format_parameters(port.parameters)
        
        port_item = QTreeWidgetItem([display_name, port_name, parameters])
        port_item.setData(0, Qt.ItemDataRole.UserRole, ("port", port))
        
        parent_item.addChild(port_item)
    
    def _format_parameters(self, parameters: dict) -> str:
        """Format port parameters for display."""
        if not parameters:
            return "Default settings"
        
        # Show key parameters in abbreviated form
        key_params = []
        
        if parameters.get("EmuBR") == "yes":
            key_params.append("BR")
        if parameters.get("EmuOverrun") == "yes":
            key_params.append("Overrun")
        if parameters.get("PlugInMode") == "yes":
            key_params.append("PlugIn")
        if parameters.get("HiddenMode") == "yes":
            key_params.append("Hidden")
        if "EmuNoise" in parameters and float(parameters["EmuNoise"]) > 0:
            key_params.append(f"Noise:{parameters['EmuNoise']}")
        
        if key_params:
            return ", ".join(key_params)
        else:
            param_count = len(parameters)
            return f"{param_count} custom parameter{'s' if param_count != 1 else ''}"
    
    def _set_status_styling(self, item: QTreeWidgetItem, status: PortStatus):
        """Apply status-based styling to tree item."""
        # This could be enhanced with icons or colors
        if status == PortStatus.ERROR:
            item.setForeground(1, self.palette().color(self.palette().ColorRole.Text))
        elif status == PortStatus.DISABLED:
            item.setForeground(1, self.palette().color(self.palette().ColorRole.PlaceholderText))
    
    def _on_selection_changed(self):
        """Handle selection change."""
        current_item = self.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple):
            item_type, item_data = data
            if item_type == "pair":
                self.port_pair_selected.emit(item_data)
            elif item_type == "port":
                self.port_selected.emit(item_data)
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple):
            item_type, item_data = data
            if item_type == "pair":
                self.port_pair_double_clicked.emit(item_data)
    
    def _on_context_menu_requested(self, position):
        """Handle context menu request."""
        item = self.itemAt(position)
        if not item:
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple):
            item_type, item_data = data
            self.context_menu_requested.emit(item_type, item_data)
        elif data == "root":
            self.context_menu_requested.emit("root", None)
    
    def get_selected_port_pair(self) -> Optional[PortPair]:
        """Get the currently selected port pair."""
        current_item = self.currentItem()
        if not current_item:
            return None
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple):
            item_type, item_data = data
            if item_type == "pair":
                return item_data
        
        return None
    
    def get_selected_port(self) -> Optional[Port]:
        """Get the currently selected individual port."""
        current_item = self.currentItem()
        if not current_item:
            return None
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple):
            item_type, item_data = data
            if item_type == "port":
                return item_data
        
        return None
    
    def select_port_pair(self, pair_number: int):
        """Select a specific port pair by number."""
        root_item = self.topLevelItem(0)
        for i in range(root_item.childCount()):
            pair_item = root_item.child(i)
            data = pair_item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(data, tuple):
                item_type, item_data = data
                if item_type == "pair" and item_data.number == pair_number:
                    self.setCurrentItem(pair_item)
                    return True
        return False
    
    def refresh(self):
        """Refresh the tree display with current data."""
        self.update_port_pairs(self.port_pairs)