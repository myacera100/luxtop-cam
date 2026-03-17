"""
System tray icon and menu for Windows.
"""
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from pathlib import Path

from utils.logger import setup_logger

logger = setup_logger(__name__)


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon widget with context menu."""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        
        # Create icon (simple colored square as placeholder)
        icon = self.create_icon()
        self.setIcon(icon)
        
        # Create context menu
        self.create_menu()
    
    def create_icon(self) -> QIcon:
        """
        Create a simple icon for the system tray.
        
        Returns:
            QIcon: The tray icon
        """
        try:
            # Try to load from assets directory
            icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
            if icon_path.exists():
                return QIcon(str(icon_path))
        except Exception as e:
            logger.error(f"Error loading icon: {e}")
        
        # Create a simple default icon if file doesn't exist
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.blue)
        return QIcon(pixmap)
    
    def create_menu(self):
        """Create the context menu for the tray icon."""
        menu = QMenu()
        
        # Show/Hide window action
        show_action = menu.addAction("Show/Hide")
        show_action.triggered.connect(self.toggle_window)
        
        # Toggle enable/disable action
        self.toggle_action = menu.addAction("Disable")
        self.toggle_action.triggered.connect(self.toggle_brightness_control)
        
        menu.addSeparator()
        
        # Exit action
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_application)
        
        self.setContextMenu(menu)
    
    def toggle_window(self):
        """Toggle main window visibility."""
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.main_window.show()
            self.main_window.activateWindow()
    
    def toggle_brightness_control(self):
        """Toggle brightness control on/off."""
        is_enabled = self.main_window.config.get('enabled', True)
        self.main_window.config['enabled'] = not is_enabled
        
        # Update checkbox and worker
        self.main_window.enable_checkbox.blockSignals(True)
        self.main_window.enable_checkbox.setChecked(self.main_window.config['enabled'])
        self.main_window.enable_checkbox.blockSignals(False)
        
        if self.main_window.worker is not None:
            self.main_window.worker.config = self.main_window.config
        
        # Update menu text
        new_text = "Enable" if self.main_window.config['enabled'] else "Disable"
        self.toggle_action.setText(new_text)
        
        status = "enabled" if self.main_window.config['enabled'] else "disabled"
        logger.info(f"Brightness control {status} from tray menu")
    
    def exit_application(self):
        """Exit the application."""
        self.main_window.close()