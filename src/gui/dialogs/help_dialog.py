"""Help dialog for com0com GUI Manager."""

from typing import Dict, Any
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                            QTreeWidgetItem, QTextBrowser, QPushButton,
                            QSplitter, QMessageBox, QWidget)
from PyQt6.QtCore import Qt


class HelpDialog(QDialog):
    """Professional help dialog for com0com technical documentation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("com0com Help")
        self.setModal(False)
        self.resize(650, 500)
        self.setMinimumSize(600, 450)
        
        
        # Help content data
        self.help_content = self._load_help_content()
        
        self.setup_ui()
        self.setup_connections()
        self.populate_tree()
        
        # Show overview by default
        self.tree_widget.setCurrentItem(self.tree_widget.topLevelItem(0))
    
    def setup_ui(self):
        """Set up the dialog UI with tree navigation and content display."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tree widget for navigation
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Topics")
        self.tree_widget.setMaximumWidth(200)
        self.tree_widget.setMinimumWidth(150)
        splitter.addWidget(self.tree_widget)
        
        # Content area with proper widget hierarchy
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        # Content browser
        self.content_browser = QTextBrowser()
        content_layout.addWidget(self.content_browser)
        
        # Button bar
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        content_layout.addWidget(button_widget)
        splitter.addWidget(content_container)
        
        # Apply splitter proportions
        splitter.setSizes([180, 470])
        layout.addWidget(splitter)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.tree_widget.currentItemChanged.connect(self._on_tree_selection_changed)
    
    def populate_tree(self):
        """Populate the tree widget with help topics."""
        self.tree_widget.clear()
        
        for section_key, section_data in self.help_content.items():
            if section_key == 'overview':
                # Add overview as top-level item
                overview_item = QTreeWidgetItem(self.tree_widget, ["Overview"])
                overview_item.setData(0, Qt.ItemDataRole.UserRole, ('overview', None))
                continue
                
            # Create main section
            section_item = QTreeWidgetItem(self.tree_widget, [section_data['title']])
            section_item.setData(0, Qt.ItemDataRole.UserRole, (section_key, None))
            
            # Add subsections
            if 'subsections' in section_data:
                for sub_key, sub_data in section_data['subsections'].items():
                    sub_item = QTreeWidgetItem(section_item, [sub_data['title']])
                    sub_item.setData(0, Qt.ItemDataRole.UserRole, (section_key, sub_key))
        
        # Expand all items by default
        self.tree_widget.expandAll()
    
    def _on_tree_selection_changed(self, current, previous):
        """Handle tree selection changes."""
        if not current:
            return
            
        section_key, sub_key = current.data(0, Qt.ItemDataRole.UserRole)
        self._display_content(section_key, sub_key)
    
    def _display_content(self, section_key: str, sub_key: str = None):
        """Display content for the selected section."""
        try:
            if section_key == 'overview':
                content_data = self.help_content['overview']
            elif sub_key:
                content_data = self.help_content[section_key]['subsections'][sub_key]
            else:
                content_data = self.help_content[section_key]
            
            # Display content
            self.content_browser.setHtml(content_data['content'])
            
        except KeyError:
            self.content_browser.setHtml("<h3>Content not found</h3><p>The requested help content could not be loaded.</p>")
    
    
    def _load_help_content(self) -> Dict[str, Any]:
        """Load comprehensive help content with technical accuracy."""
        return {
            'overview': {
                'title': 'Overview',
                'content': '''
                <h2>com0com Virtual Serial Port Manager</h2>
                <p>This application provides a graphical interface for managing com0com virtual serial port pairs. 
                com0com creates pairs of interconnected virtual COM ports that behave like physical serial ports 
                connected by a null-modem cable.</p>
                
                <h3>Key Concepts</h3>
                <ul>
                <li><strong>Port Pairs:</strong> Two virtual COM ports (CNCA0/CNCB0) that are internally connected</li>
                <li><strong>setupc.exe:</strong> The underlying command-line tool that manages all port operations</li>
                <li><strong>Parameters:</strong> Configuration settings that control port behaviour and emulation features</li>
                <li><strong>Driver Operations:</strong> System-level commands for installing and managing the com0com driver</li>
                </ul>
                
                <h3>Navigation</h3>
                <p>Use the tree on the left to browse help topics.</p>
                '''
            },
            
            'commands': {
                'title': 'Commands Reference',
                'content': '''
                <h2>setupc.exe Commands</h2>
                <p>All operations in this GUI execute setupc.exe commands. Understanding these commands helps 
                troubleshoot issues and use advanced features.</p>
                ''',
                'subsections': {
                    'port_management': {
                        'title': 'Port Management',
                        'content': '''
                        <h3>Port Management Commands</h3>
                        
                        <h4>Install Port Pair</h4>
                        <p><strong>Purpose:</strong> Creates a new virtual port pair with specified parameters.</p>
                        <p><strong>Syntax:</strong> <code>setupc.exe install [n] &lt;paramsA&gt; &lt;paramsB&gt;</code></p>
                        <ul>
                        <li><strong>Numbered installation:</strong> Assigns specific pair number (0, 1, 2...)</li>
                        <li><strong>Auto-numbered:</strong> Omit pair number for automatic assignment</li>
                        <li><strong>Parameters:</strong> Use "-" for defaults or specify custom settings</li>
                        </ul>
                        
                        <h4>Remove Port Pair</h4>
                        <p><strong>Purpose:</strong> Permanently removes a virtual port pair.</p>
                        <p><strong>Syntax:</strong> <code>setupc.exe remove &lt;n&gt;</code></p>
                        <p><strong>Warning:</strong> This operation cannot be undone.</p>
                        
                        <h4>Modify Port Configuration</h4>
                        <p><strong>Purpose:</strong> Changes parameters of an existing port.</p>
                        <p><strong>Syntax:</strong> <code>setupc.exe change &lt;portid&gt; &lt;params&gt;</code></p>
                        <p><strong>Port ID Format:</strong> CNCA0, CNCB0, CNCA1, CNCB1, etc.</p>
                        
                        <h4>List All Ports</h4>
                        <p><strong>Purpose:</strong> Displays current port configuration and status.</p>
                        <p><strong>Syntax:</strong> <code>setupc.exe list</code></p>
                        ''',
                        'snippet': 'setupc.exe install - -'
                    },
                    
                    'driver_operations': {
                        'title': 'Driver Operations',
                        'content': '''
                        <h3>Driver Management Commands</h3>
                        
                        <h4>Preinstall Driver</h4>
                        <p><strong>Purpose:</strong> Prepares the com0com driver for installation without creating ports.</p>
                        <p><strong>Syntax:</strong> <code>setupc.exe preinstall</code></p>
                        <p><strong>When to use:</strong> During system setup or driver updates.</p>
                        
                        <h4>Update Driver</h4>
                        <p><strong>Purpose:</strong> Updates the com0com driver to the latest version.</p>
                        <p><strong>Syntax:</strong> <code>setupc.exe update</code></p>
                        <p><strong>Effect:</strong> May require system restart.</p>
                        
                        <h4>Reload Driver</h4>
                        <p><strong>Purpose:</strong> Restarts the driver service without system reboot.</p>
                        <p><strong>Syntax:</strong> <code>setupc.exe reload</code></p>
                        <p><strong>When to use:</strong> After configuration changes or to resolve driver issues.</p>
                        
                        <h4>Uninstall Driver</h4>
                        <p><strong>Purpose:</strong> Completely removes com0com from the system.</p>
                        <p><strong>Syntax:</strong> <code>setupc.exe uninstall</code></p>
                        <p><strong>Warning:</strong> This removes all virtual ports and driver components.</p>
                        ''',
                        'snippet': 'setupc.exe reload'
                    },
                    
                    'utilities': {
                        'title': 'Utility Commands',
                        'content': '''
                        <h3>System Utilities</h3>
                        
                        <h4>Enable/Disable All Ports</h4>
                        <p><strong>Purpose:</strong> Quickly control all virtual ports in the current hardware profile.</p>
                        <p><strong>Syntax:</strong> <code>setupc.exe enable all</code> or <code>setupc.exe disable all</code></p>
                        <p><strong>Use case:</strong> Troubleshooting or temporarily freeing system resources.</p>
                        
                        <h4>Check Busy Names</h4>
                        <p><strong>Purpose:</strong> Lists COM port names already in use by the system.</p>
                        <p><strong>Syntax:</strong> <code>setupc.exe busynames &lt;pattern&gt;</code></p>
                        <p><strong>Example:</strong> <code>setupc.exe busynames COM?*</code> checks COM1-COM9999</p>
                        
                        <h4>Clean INF Files</h4>
                        <p><strong>Purpose:</strong> Removes old driver installation files.</p>
                        <p><strong>Syntax:</strong> <code>setupc.exe infclean</code></p>
                        <p><strong>When to use:</strong> After driver updates or when troubleshooting installation issues.</p>
                        
                        <h4>Friendly Names Management</h4>
                        <p><strong>List names:</strong> <code>setupc.exe listfnames</code></p>
                        <p><strong>Update names:</strong> <code>setupc.exe updatefnames</code></p>
                        <p><strong>Purpose:</strong> Manages the descriptive names shown in Device Manager.</p>
                        ''',
                        'snippet': 'setupc.exe busynames COM?*'
                    }
                }
            },
            
            'parameters': {
                'title': 'Parameters Reference',
                'content': '''
                <h2>Port Parameters</h2>
                <p>Port parameters control the behaviour and characteristics of virtual serial ports. 
                Understanding these parameters is essential for proper configuration.</p>
                ''',
                'subsections': {
                    'basic_settings': {
                        'title': 'Basic Settings',
                        'content': '''
                        <h3>Basic Port Settings</h3>
                        
                        <h4>PortName</h4>
                        <p><strong>Purpose:</strong> Sets the system name for the virtual port.</p>
                        <p><strong>Default:</strong> Uses the port identifier (e.g., CNCA0)</p>
                        <p><strong>Special value COM#:</strong> Automatically assigns an available COM port number</p>
                        <p><strong>Example:</strong> <code>PortName=COM8</code></p>
                        <p><strong>Note:</strong> Applications typically connect using the PortName, not the identifier.</p>
                        
                        <h4>RealPortName</h4>
                        <p><strong>Purpose:</strong> Changes the actual port name when PortName=COM# is used.</p>
                        <p><strong>Requirement:</strong> Only valid when PortName is set to COM#</p>
                        <p><strong>Use case:</strong> Force assignment to a specific COM number</p>
                        <p><strong>Example:</strong> <code>RealPortName=COM3</code></p>
                        
                        <h4>Special Parameter Values</h4>
                        <p><strong>"-" (hyphen):</strong> Use driver defaults for all parameters</p>
                        <p><strong>"*" (asterisk):</strong> Use current settings for all parameters (preserves existing configuration)</p>
                        <p><strong>Example:</strong> <code>setupc.exe change CNCA0 *</code> keeps current CNCA0 settings unchanged</p>
                        ''',
                        'snippet': 'PortName=COM8'
                    },
                    
                    'emulation_features': {
                        'title': 'Emulation Features',
                        'content': '''
                        <h3>Hardware Emulation Parameters</h3>
                        
                        <h4>EmuBR (Baud Rate Emulation)</h4>
                        <p><strong>Purpose:</strong> Simulates the transmission speed limitations of physical serial hardware.</p>
                        <p><strong>Values:</strong> yes, no</p>
                        <p><strong>Default:</strong> no</p>
                        <p><strong>Effect:</strong> When enabled, data transmission speed matches the configured baud rate</p>
                        <p><strong>Use case:</strong> Testing applications that depend on specific timing characteristics</p>
                        
                        <h4>EmuOverrun (Buffer Overrun Emulation)</h4>
                        <p><strong>Purpose:</strong> Simulates buffer overflow conditions found in physical serial ports.</p>
                        <p><strong>Values:</strong> yes, no</p>
                        <p><strong>Default:</strong> no</p>
                        <p><strong>Effect:</strong> Generates overrun errors when data arrives faster than it can be processed</p>
                        <p><strong>Use case:</strong> Testing application error handling and flow control</p>
                        
                        <h4>EmuNoise (Transmission Error Simulation)</h4>
                        <p><strong>Purpose:</strong> Introduces controlled transmission errors for robustness testing.</p>
                        <p><strong>Range:</strong> 0.0 to 0.99999999</p>
                        <p><strong>Default:</strong> 0 (no errors)</p>
                        <p><strong>Unit:</strong> Probability of error per character frame</p>
                        <p><strong>Example:</strong> 0.01 = 1% error rate, 0.1 = 10% error rate</p>
                        <p><strong>Use case:</strong> Testing application resilience to line noise and transmission errors</p>
                        ''',
                        'snippet': 'EmuBR=yes,EmuOverrun=yes,EmuNoise=0.01'
                    },
                    
                    'timing_control': {
                        'title': 'Timing Control',
                        'content': '''
                        <h3>Read Timeout Parameters</h3>
                        
                        <h4>AddRTTO (Additional Read Total Timeout)</h4>
                        <p><strong>Purpose:</strong> Extends the maximum time allowed for read operations.</p>
                        <p><strong>Type:</strong> Positive integer</p>
                        <p><strong>Unit:</strong> Milliseconds</p>
                        <p><strong>Default:</strong> 0 (no additional timeout)</p>
                        <p><strong>Effect:</strong> Added to the application's specified total timeout</p>
                        <p><strong>Use case:</strong> Accommodating slower applications or network-based serial connections</p>
                        
                        <h4>AddRITO (Additional Read Interval Timeout)</h4>
                        <p><strong>Purpose:</strong> Extends the maximum time between character arrivals during read operations.</p>
                        <p><strong>Type:</strong> Positive integer</p>
                        <p><strong>Unit:</strong> Milliseconds</p>
                        <p><strong>Default:</strong> 0 (no additional timeout)</p>
                        <p><strong>Effect:</strong> Added to the application's specified interval timeout</p>
                        <p><strong>Technical note:</strong> Interval timeout controls when a partial read operation completes</p>
                        <p><strong>Use case:</strong> Fine-tuning behaviour with applications that have specific timing requirements</p>
                        ''',
                        'snippet': 'AddRTTO=1000,AddRITO=500'
                    },
                    
                    'port_modes': {
                        'title': 'Port Modes',
                        'content': '''
                        <h3>Port Visibility and Behaviour Modes</h3>
                        
                        <h4>PlugInMode</h4>
                        <p><strong>Purpose:</strong> Controls port visibility based on paired port status.</p>
                        <p><strong>Values:</strong> yes, no</p>
                        <p><strong>Default:</strong> no</p>
                        <p><strong>Behaviour:</strong> Port remains hidden until its paired port is opened by an application</p>
                        <p><strong>Use case:</strong> Reducing system COM port enumeration when ports are not actively used</p>
                        
                        <h4>ExclusiveMode</h4>
                        <p><strong>Purpose:</strong> Hides the port when it is currently opened by an application.</p>
                        <p><strong>Values:</strong> yes, no</p>
                        <p><strong>Default:</strong> no</p>
                        <p><strong>Behaviour:</strong> Port disappears from system enumeration whilst in use</p>
                        <p><strong>Use case:</strong> Preventing multiple applications from attempting to access the same port</p>
                        
                        <h4>HiddenMode</h4>
                        <p><strong>Purpose:</strong> Completely hides the port from system port enumerators.</p>
                        <p><strong>Values:</strong> yes, no</p>
                        <p><strong>Default:</strong> no</p>
                        <p><strong>Behaviour:</strong> Port is not listed in Device Manager or application COM port lists</p>
                        <p><strong>Access:</strong> Applications can still connect using the exact port name</p>
                        <p><strong>Use case:</strong> Creating dedicated ports for specific applications</p>
                        
                        <h4>AllDataBits</h4>
                        <p><strong>Purpose:</strong> Controls whether all data bits are transferred regardless of the configured data bits setting.</p>
                        <p><strong>Values:</strong> yes, no</p>
                        <p><strong>Default:</strong> no</p>
                        <p><strong>Technical effect:</strong> Bypasses normal 5/6/7/8 data bit masking</p>
                        <p><strong>Use case:</strong> Applications requiring full 8-bit data transparency</p>
                        ''',
                        'snippet': 'PlugInMode=yes,HiddenMode=yes'
                    },
                    
                    'pin_wiring': {
                        'title': 'Pin Wiring',
                        'content': '''
                        <h3>Serial Control Signal Wiring</h3>
                        <p>Pin wiring parameters control how control signals (CTS, DSR, DCD, RI) are connected between port pairs. 
                        This emulates the behaviour of different cable configurations. All signals are logical states (high/low), 
                        not physical voltages.</p>
                        
                        <h4>Available Signal Sources</h4>
                        <ul>
                        <li><strong>rrts:</strong> Remote RTS (paired port's RTS output)</li>
                        <li><strong>lrts:</strong> Local RTS (this port's RTS output)</li>
                        <li><strong>rdtr:</strong> Remote DTR (paired port's DTR output)</li>
                        <li><strong>ldtr:</strong> Local DTR (this port's DTR output)</li>
                        <li><strong>rout1:</strong> Remote OUT1 (paired port's OUT1 output)</li>
                        <li><strong>lout1:</strong> Local OUT1 (this port's OUT1 output)</li>
                        <li><strong>rout2:</strong> Remote OUT2 (paired port's OUT2 output)</li>
                        <li><strong>lout2:</strong> Local OUT2 (this port's OUT2 output)</li>
                        <li><strong>ropen:</strong> Logical high when paired port is open</li>
                        <li><strong>lopen:</strong> Logical high when local port is open</li>
                        <li><strong>on:</strong> Permanently logical high</li>
                        </ul>
                        
                        <h4>Signal Inversion</h4>
                        <p>Prefix any signal source with "!" to invert the signal (logical NOT operation).</p>
                        <p><strong>Example:</strong> <code>cts=!rrts</code> connects CTS to inverted remote RTS</p>
                        
                        <h4>Individual Pin Configurations</h4>
                        
                        <h5>CTS (Clear To Send)</h5>
                        <p><strong>Default:</strong> rrts</p>
                        <p><strong>Typical use:</strong> Flow control input signal</p>
                        
                        <h5>DSR (Data Set Ready)</h5>
                        <p><strong>Default:</strong> rdtr</p>
                        <p><strong>Typical use:</strong> Modem status indication</p>
                        
                        <h5>DCD (Data Carrier Detect)</h5>
                        <p><strong>Default:</strong> rdtr</p>
                        <p><strong>Typical use:</strong> Connection status indication</p>
                        
                        <h5>RI (Ring Indicator)</h5>
                        <p><strong>Default:</strong> !on (inverted logical high = logical low/off)</p>
                        <p><strong>Typical use:</strong> Incoming call indication</p>
                        
                        <h4>Common Wiring Patterns</h4>
                        <p><strong>Null modem:</strong> <code>cts=rrts,dsr=rdtr,dcd=rdtr</code></p>
                        <p><strong>Loopback:</strong> <code>cts=lrts,dsr=ldtr,dcd=ldtr</code></p>
                        <p><strong>Always ready:</strong> <code>cts=on,dsr=on,dcd=on</code></p>
                        ''',
                        'snippet': 'cts=rrts,dsr=rdtr,dcd=rdtr,ri=!on'
                    }
                }
            },
            
            'examples': {
                'title': 'Configuration Examples',
                'content': '''
                <h2>Common Configuration Examples</h2>
                <p>These examples demonstrate typical port configurations for different use cases.</p>
                
                <h3>Basic Port Pair</h3>
                <p><strong>Command:</strong> <code>setupc.exe install - -</code></p>
                <p><strong>Result:</strong> Creates a port pair with default settings and auto-assigned numbers</p>
                
                <h3>Named COM Ports</h3>
                <p><strong>Command:</strong> <code>setupc.exe install PortName=COM8 PortName=COM9</code></p>
                <p><strong>Result:</strong> Creates ports accessible as COM8 and COM9</p>
                
                <h3>Hardware Emulation Testing</h3>
                <p><strong>Command:</strong> <code>setupc.exe install EmuBR=yes,EmuOverrun=yes,EmuNoise=0.01 PortName=COM10</code></p>
                <p><strong>Result:</strong> Port with realistic timing, buffer overrun simulation, and 1% error rate</p>
                
                <h3>Hidden Dedicated Ports</h3>
                <p><strong>Command:</strong> <code>setupc.exe install HiddenMode=yes,PlugInMode=yes PortName=COM20</code></p>
                <p><strong>Result:</strong> Ports hidden from enumeration, appear only when paired port opens</p>
                
                <h3>Custom Pin Wiring</h3>
                <p><strong>Command:</strong> <code>setupc.exe change CNCA0 cts=on,dsr=on,dcd=ropen</code></p>
                <p><strong>Result:</strong> Always-ready CTS/DSR, DCD indicates when remote port is open</p>
                ''',
                'snippet': 'setupc.exe install PortName=COM8 PortName=COM9'
            }
        }

    @staticmethod
    def show_help(parent=None):
        """Static method to show the help dialog."""
        dialog = HelpDialog(parent)
        dialog.show()
        return dialog


