from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QSpinBox, QDoubleSpinBox, QPushButton,
    QCheckBox, QStatusBar, QMessageBox, QSystemTrayIcon, QAction,
    QMenu, QDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QPropertyAnimation
from typing import Callable, Dict, Any

from gui.tray import SystemTrayIcon
from core.controller import BrightnessController, BrightnessWorker
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MainWindow(QMainWindow):
    """Alternative Main application window."""
    
    def __init__(self, config: Dict[str, Any], save_config: Callable):
        super().__init__()
        self.config = config
        self.save_config = save_config
        self.controller = None
        self.worker = None
        self.worker_thread = None
        
        # Initialize UI
        self.init_ui()
        
        # Setup system tray
        self.tray_icon = SystemTrayIcon(self)
        self.tray_icon.show()
        
        # Connect signals
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Start background worker
        self.start_brightness_controller()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Auto Brightness Controller")
        self.setGeometry(100, 100, 600, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Enable/Disable control
        enable_group = QGroupBox("Control")
        enable_layout = QHBoxLayout()
        
        self.enable_checkbox = QCheckBox("Enable Automatic Brightness Control")
        self.enable_checkbox.setChecked(self.config.get('enabled', True))
        self.enable_checkbox.stateChanged.connect(self.on_enable_changed)
        enable_layout.addWidget(self.enable_checkbox)
        enable_group.setLayout(enable_layout)
        main_layout.addWidget(enable_group)
        
        # Current brightness display
        status_group = QGroupBox("Current Status")
        status_layout = QVBoxLayout()
        
        self.detected_brightness_label = QLabel("Detected Brightness: -- %")
        self.detected_brightness_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        status_layout.addWidget(self.detected_brightness_label)
        
        self.system_brightness_label = QLabel("System Brightness: -- %")
        self.system_brightness_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        status_layout.addWidget(self.system_brightness_label)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Camera settings
        camera_group = QGroupBox("Camera Settings")
        camera_layout = QVBoxLayout()
        
        camera_index_layout = QHBoxLayout()
        camera_index_layout.addWidget(QLabel("Camera Index:"))
        self.camera_index_spinbox = QSpinBox()
        self.camera_index_spinbox.setMinimum(0)
        self.camera_index_spinbox.setMaximum(10)
        self.camera_index_spinbox.setValue(self.config.get('camera_index', 0))
        self.camera_index_spinbox.valueChanged.connect(self.on_camera_index_changed)
        camera_index_layout.addWidget(self.camera_index_spinbox)
        camera_index_layout.addStretch()
        camera_layout.addLayout(camera_index_layout)
        
        capture_interval_layout = QHBoxLayout()
        capture_interval_layout.addWidget(QLabel("Capture Interval (seconds):"))
        self.capture_interval_spinbox = QDoubleSpinBox()
        self.capture_interval_spinbox.setMinimum(0.5)
        self.capture_interval_spinbox.setMaximum(10.0)
        self.capture_interval_spinbox.setSingleStep(0.5)
        self.capture_interval_spinbox.setValue(self.config.get('capture_interval', 2.0))
        self.capture_interval_spinbox.valueChanged.connect(self.on_capture_interval_changed)
        capture_interval_layout.addWidget(self.capture_interval_spinbox)
        capture_interval_layout.addStretch()
        camera_layout.addLayout(capture_interval_layout)
        
        camera_group.setLayout(camera_layout)
        main_layout.addWidget(camera_group)
        
        # Brightness control settings
        brightness_group = QGroupBox("Brightness Control")
        brightness_layout = QVBoxLayout()
        
        # Min brightness
        min_bright_layout = QHBoxLayout()
        min_bright_layout.addWidget(QLabel("Minimum Brightness:"))
        self.min_brightness_spinbox = QSpinBox()
        self.min_brightness_spinbox.setMinimum(0)
        self.min_brightness_spinbox.setMaximum(100)
        self.min_brightness_spinbox.setValue(self.config.get('min_brightness', 10))
        self.min_brightness_spinbox.valueChanged.connect(self.on_min_brightness_changed)
        min_bright_layout.addWidget(self.min_brightness_spinbox)
        min_bright_layout.addWidget(QLabel("%"))
        min_bright_layout.addStretch()
        brightness_layout.addLayout(min_bright_layout)
        
        # Max brightness
        max_bright_layout = QHBoxLayout()
        max_bright_layout.addWidget(QLabel("Maximum Brightness:"))
        self.max_brightness_spinbox = QSpinBox()
        self.max_brightness_spinbox.setMinimum(0)
        self.max_brightness_spinbox.setMaximum(100)
        self.max_brightness_spinbox.setValue(self.config.get('max_brightness', 100))
        self.max_brightness_spinbox.valueChanged.connect(self.on_max_brightness_changed)
        max_bright_layout.addWidget(self.max_brightness_spinbox)
        max_bright_layout.addWidget(QLabel("%"))
        max_bright_layout.addStretch()
        brightness_layout.addLayout(max_bright_layout)
        
        # Sensitivity
        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(QLabel("Brightness Sensitivity:"))
        self.sensitivity_spinbox = QDoubleSpinBox()
        self.sensitivity_spinbox.setMinimum(0.1)
        self.sensitivity_spinbox.setMaximum(1.0)
        self.sensitivity_spinbox.setSingleStep(0.1)
        self.sensitivity_spinbox.setValue(self.config.get('brightness_sensitivity', 0.8))
        self.sensitivity_spinbox.valueChanged.connect(self.on_sensitivity_changed)
        sensitivity_layout.addWidget(self.sensitivity_spinbox)
        sensitivity_layout.addStretch()
        brightness_layout.addLayout(sensitivity_layout)
        
        brightness_group.setLayout(brightness_layout)
        main_layout.addWidget(brightness_group)
        
        # Thresholds
        threshold_group = QGroupBox("Brightness Thresholds")
        threshold_layout = QVBoxLayout()
        
        # Dark threshold
        dark_threshold_layout = QHBoxLayout()
        dark_threshold_layout.addWidget(QLabel("Dark Threshold:"))
        self.dark_threshold_spinbox = QSpinBox()
        self.dark_threshold_spinbox.setMinimum(0)
        self.dark_threshold_spinbox.setMaximum(255)
        self.dark_threshold_spinbox.setValue(self.config.get('dark_threshold', 50))
        self.dark_threshold_spinbox.valueChanged.connect(self.on_dark_threshold_changed)
        dark_threshold_layout.addWidget(self.dark_threshold_spinbox)
        dark_threshold_layout.addStretch()
        threshold_layout.addLayout(dark_threshold_layout)
        
        # Bright threshold
        bright_threshold_layout = QHBoxLayout()
        bright_threshold_layout.addWidget(QLabel("Bright Threshold:"))
        self.bright_threshold_spinbox = QSpinBox()
        self.bright_threshold_spinbox.setMinimum(0)
        self.bright_threshold_spinbox.setMaximum(255)
        self.bright_threshold_spinbox.setValue(self.config.get('bright_threshold', 150))
        self.bright_threshold_spinbox.valueChanged.connect(self.on_bright_threshold_changed)
        bright_threshold_layout.addWidget(self.bright_threshold_spinbox)
        bright_threshold_layout.addStretch()
        threshold_layout.addLayout(bright_threshold_layout)
        
        threshold_group.setLayout(threshold_layout)
        main_layout.addWidget(threshold_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_button)
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def start_brightness_controller(self):
        """Start the brightness controller worker thread."""
        try:
            if self.controller is None:
                self.controller = BrightnessController(
                    camera_index=self.config.get('camera_index', 0)
                )
            
            if not self.controller.is_initialized:
                QMessageBox.warning(
                    self,
                    "Camera Error",
                    "Failed to initialize camera. Please check your webcam connection."
                )
                return
            
            # Create and start worker thread
            self.worker = BrightnessWorker(self.controller, self.config)
            self.worker.brightness_updated.connect(self.on_brightness_updated)
            self.worker.error_occurred.connect(self.on_worker_error)
            self.worker.start()
            
            self.status_bar.showMessage("Running - Adjusting brightness...")
            logger.info("Brightness controller started")
        except Exception as e:
            logger.error(f"Error starting brightness controller: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start brightness controller: {e}")
    
    def stop_brightness_controller(self):
        """Stop the brightness controller worker thread."""
        if self.worker is not None:
            self.worker.stop()
            self.status_bar.showMessage("Stopped")
            logger.info("Brightness controller stopped")
    
    def on_brightness_updated(self, detected_brightness: float, system_brightness: int):
        """Update UI with new brightness values."""
        detected_percent = (detected_brightness / 255.0) * 100
        self.detected_brightness_label.setText(
            f"Detected Brightness: {detected_percent:.1f}%"
        )
        self.system_brightness_label.setText(
            f"System Brightness: {system_brightness}%"
        )
    
    def on_worker_error(self, error_msg: str):
        """Handle worker errors."""
        logger.error(f"Worker error: {error_msg}")
        self.status_bar.showMessage(f"Error: {error_msg}")
    
    def on_enable_changed(self, state):
        """Handle enable/disable checkbox change."""
        self.config['enabled'] = self.enable_checkbox.isChecked()
        if self.worker is not None:
            self.worker.config = self.config
        logger.info(f"Brightness control {'enabled' if self.config['enabled'] else 'disabled'}")
    
    def on_camera_index_changed(self, value):
        """Handle camera index change."""
        self.config['camera_index'] = value
        # Restart controller with new camera
        self.stop_brightness_controller()
        if self.controller is not None:
            self.controller.cleanup()
        self.controller = None
        self.start_brightness_controller()
    
    def on_capture_interval_changed(self, value):
        """Handle capture interval change."""
        self.config['capture_interval'] = value
        if self.worker is not None:
            self.worker.config = self.config
    
    def on_min_brightness_changed(self, value):
        """Handle minimum brightness change."""
        self.config['min_brightness'] = value
        if self.worker is not None:
            self.worker.config = self.config
    
    def on_max_brightness_changed(self, value):
        """Handle maximum brightness change."""
        self.config['max_brightness'] = value
        if self.worker is not None:
            self.worker.config = self.config
    
    def on_sensitivity_changed(self, value):
        """Handle sensitivity change."""
        self.config['brightness_sensitivity'] = value
        if self.worker is not None:
            self.worker.config = self.config
    
    def on_dark_threshold_changed(self, value):
        """Handle dark threshold change."""
        self.config['dark_threshold'] = value
        if self.worker is not None:
            self.worker.config = self.config
    
    def on_bright_threshold_changed(self, value):
        """Handle bright threshold change."""
        self.config['bright_threshold'] = value
        if self.worker is not None:
            self.worker.config = self.config
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config = {
                "capture_interval": 2.0,
                "min_brightness": 10,
                "max_brightness": 100,
                "brightness_sensitivity": 0.8,
                "dark_threshold": 50,
                "bright_threshold": 150,
                "enabled": True,
                "camera_index": 0
            }
            
            # Update UI
            self.enable_checkbox.setChecked(self.config['enabled'])
            self.camera_index_spinbox.setValue(self.config['camera_index'])
            self.capture_interval_spinbox.setValue(self.config['capture_interval'])
            self.min_brightness_spinbox.setValue(self.config['min_brightness'])
            self.max_brightness_spinbox.setValue(self.config['max_brightness'])
            self.sensitivity_spinbox.setValue(self.config['brightness_sensitivity'])
            self.dark_threshold_spinbox.setValue(self.config['dark_threshold'])
            self.bright_threshold_spinbox.setValue(self.config['bright_threshold'])
            
            logger.info("Settings reset to defaults")
    
    def save_settings(self):
        """Save current settings to config file."""
        self.save_config(self.config)
        QMessageBox.information(
            self,
            "Settings Saved",
            "Settings have been saved successfully."
        )
        logger.info("Settings saved by user")
    
    def tray_icon_activated(self, reason):
        """Handle system tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def changeEvent(self, event):
        """Handle window state changes (minimize to tray)."""
        if event.type() == event.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.hide()
                event.ignore()
        super().changeEvent(event)
    
    def closeEvent(self, event):
        """Handle window close event."""
        reply = QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit? The brightness controller will stop.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.stop_brightness_controller()
            if self.controller is not None:
                self.controller.cleanup()
            event.accept()
        else:
            event.ignore()
            
