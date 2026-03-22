from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QSystemTrayIcon, QMessageBox, QMenu, QAction
from PyQt5.QtCore import Qt, QByteArray, QTimer, pyqtSignal, QThread, QPropertyAnimation
from PyQt5.QtGui import QIcon, QPixmap
from typing import Callable, Dict, Any

from gui.widgets import SenseSlider
from gui.tray import SystemTrayIcon
from core.controller import BrightnessController, BrightnessWorker
import lux_res
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Ui_LuxPanel(object):
    def setupUi(self, parent):
        parent.setObjectName("LuxPanel")
        parent.resize(640, 350)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(parent.sizePolicy().hasHeightForWidth())
        parent.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/logo"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        parent.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(parent)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(10, 8, 10, 10)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.briIcoLabel = QtWidgets.QLabel(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.briIcoLabel.sizePolicy().hasHeightForWidth())
        self.briIcoLabel.setSizePolicy(sizePolicy)
        self.briIcoLabel.setText("")
        self.briIcoLabel.setPixmap(QtGui.QPixmap(":/images/bri"))
        self.briIcoLabel.setObjectName("briIcoLabel")
        self.horizontalLayout.addWidget(self.briIcoLabel)
        self.briLabel = QtWidgets.QLabel(parent)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.briLabel.setFont(font)
        self.briLabel.setTextFormat(QtCore.Qt.AutoText)
        self.briLabel.setObjectName("briLabel")
        self.horizontalLayout.addWidget(self.briLabel)
        self.luxLabel = QtWidgets.QLabel(parent)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.luxLabel.setFont(font)
        self.luxLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.luxLabel.setObjectName("luxLabel")
        self.horizontalLayout.addWidget(self.luxLabel)
        self.luxIcoLabel = QtWidgets.QLabel(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.luxIcoLabel.sizePolicy().hasHeightForWidth())
        self.luxIcoLabel.setSizePolicy(sizePolicy)
        self.luxIcoLabel.setText("")
        self.luxIcoLabel.setPixmap(QtGui.QPixmap(":/images/lux"))
        self.luxIcoLabel.setObjectName("luxIcoLabel")
        self.horizontalLayout.addWidget(self.luxIcoLabel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.briLCD = QtWidgets.QLCDNumber(parent)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(89, 170, 252))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(89, 170, 252))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.briLCD.setPalette(palette)
        self.briLCD.setFrameShadow(QtWidgets.QFrame.Plain)
        self.briLCD.setLineWidth(0)
        self.briLCD.setDigitCount(3)
        self.briLCD.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.briLCD.setObjectName("briLCD")
        self.horizontalLayout_2.addWidget(self.briLCD)
        self.assocBtn = QtWidgets.QPushButton(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.assocBtn.sizePolicy().hasHeightForWidth())
        self.assocBtn.setSizePolicy(sizePolicy)
        self.assocBtn.setMinimumSize(QtCore.QSize(64, 64))
        self.assocBtn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/assoc"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.assocBtn.setIcon(icon1)
        self.assocBtn.setIconSize(QtCore.QSize(64, 64))
        self.assocBtn.setObjectName("assocBtn")
        self.horizontalLayout_2.addWidget(self.assocBtn)
        self.luxLCD = QtWidgets.QLCDNumber(parent)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(252, 48, 130))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(252, 48, 130))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.luxLCD.setPalette(palette)
        self.luxLCD.setFrameShadow(QtWidgets.QFrame.Plain)
        self.luxLCD.setLineWidth(0)
        self.luxLCD.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.luxLCD.setObjectName("luxLCD")
        self.horizontalLayout_2.addWidget(self.luxLCD)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.miBriBtn = QtWidgets.QPushButton(parent)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.miBriBtn.setFont(font)
        self.miBriBtn.setObjectName("miBriBtn")
        self.horizontalLayout_3.addWidget(self.miBriBtn)
        self.briSlider = SenseSlider(parent)
        self.briSlider.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.briSlider.setOrientation(QtCore.Qt.Horizontal)
        self.briSlider.setObjectName("briSlider")
        self.horizontalLayout_3.addWidget(self.briSlider)
        self.mxBriBtn = QtWidgets.QPushButton(parent)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.mxBriBtn.setFont(font)
        self.mxBriBtn.setObjectName("mxBriBtn")
        self.horizontalLayout_3.addWidget(self.mxBriBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.toggleBtn = QtWidgets.QPushButton(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toggleBtn.sizePolicy().hasHeightForWidth())
        self.toggleBtn.setSizePolicy(sizePolicy)
        self.toggleBtn.setMinimumSize(QtCore.QSize(48, 48))
        self.toggleBtn.setMaximumSize(QtCore.QSize(50, 50))
        self.toggleBtn.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images/toggle"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toggleBtn.setIcon(icon2)
        self.toggleBtn.setIconSize(QtCore.QSize(48, 48))
        self.toggleBtn.setObjectName("toggleBtn")
        self.horizontalLayout_4.addWidget(self.toggleBtn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.lwProBtn = QtWidgets.QPushButton(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lwProBtn.sizePolicy().hasHeightForWidth())
        self.lwProBtn.setSizePolicy(sizePolicy)
        self.lwProBtn.setMinimumSize(QtCore.QSize(32, 32))
        self.lwProBtn.setMaximumSize(QtCore.QSize(32, 32))
        self.lwProBtn.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/images/hipro"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.lwProBtn.setIcon(icon3)
        self.lwProBtn.setIconSize(QtCore.QSize(32, 32))
        self.lwProBtn.setObjectName("lwProBtn")
        self.horizontalLayout_4.addWidget(self.lwProBtn)
        self.scaleSlider = SenseSlider(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scaleSlider.sizePolicy().hasHeightForWidth())
        self.scaleSlider.setSizePolicy(sizePolicy)
        self.scaleSlider.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.scaleSlider.setOrientation(QtCore.Qt.Horizontal)
        self.scaleSlider.setObjectName("scaleSlider")
        self.horizontalLayout_4.addWidget(self.scaleSlider)
        self.hiProBtn = QtWidgets.QPushButton(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hiProBtn.sizePolicy().hasHeightForWidth())
        self.hiProBtn.setSizePolicy(sizePolicy)
        self.hiProBtn.setMinimumSize(QtCore.QSize(32, 32))
        self.hiProBtn.setMaximumSize(QtCore.QSize(32, 32))
        self.hiProBtn.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/images/lwpro"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.hiProBtn.setIcon(icon4)
        self.hiProBtn.setIconSize(QtCore.QSize(32, 32))
        self.hiProBtn.setObjectName("hiProBtn")
        self.horizontalLayout_4.addWidget(self.hiProBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 4)
        self.verticalLayout.setStretch(2, 2)
        self.verticalLayout.setStretch(3, 1)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(parent)
        QtCore.QMetaObject.connectSlotsByName(parent)

    def retranslateUi(self, LuxPanel):
        _translate = QtCore.QCoreApplication.translate
        LuxPanel.setWindowTitle(_translate("LuxPanel", "Luxtop - Care your eyes 💡"))
        self.briLabel.setText(_translate("LuxPanel", "BRI"))
        self.luxLabel.setText(_translate("LuxPanel", "LUX"))
        self.miBriBtn.setText(_translate("LuxPanel", "Lights Out"))
        self.mxBriBtn.setText(_translate("LuxPanel", "Dazzle"))

LuxPanel = Ui_LuxPanel

class LuxWindow(QtWidgets.QDialog):
    """Luxtop application window."""
    
    def __init__(self, config: Dict[str, Any], save_config: Callable):
        
        self._tray_mode = True
        self._just_launched = True
        self._pending_close = False
        
        super().__init__()
        
        # Configurations
        self.config = config
        self.save_config = save_config
        
        # Lux controller
        self.controller = None
        self.worker = None
        self.worker_thread = None
        
        # Initialize UI components
        self._init_components()
        
        # Start background worker
        self.start_brightness_controller()
        
    def _init_components(self):
        self.ui = LuxPanel()
        self.ui.setupUi(self)
        
        self._anim_in_progress = False
        self._anim_duration = 1500
        self._slider_animator = QPropertyAnimation()
        self._slider_animator.setTargetObject(self.ui.briSlider)
        prop_name = bytearray("value", "ascii")
        self._slider_animator.setPropertyName(b"value")
        
        # Setup system tray
        self._tray_menu = QMenu(self)
        self._text_resume = self.tr("Resume")
        self._text_pause = self.tr("Pause")
        self._icon_pause = QIcon(":/images/pause")
        self._icon_resume = QIcon(":/images/resume")
        self._act_show = QAction(QIcon(":/images/show"), self.tr("Show"))
        self._act_reconnect = QAction(QIcon(":/images/assoc"), self.tr("Reconnect"))
        self._act_quit = QAction(QIcon(":/images/quit"), self.tr("Quit"))
        self._act_pause = QAction(self._icon_pause, self._text_pause)
        # -- Use this action for toggling pause/resume
        self._act_pause.setCheckable(True)
        
        self._tray_menu.addActions([
            self._act_show,
            self._act_reconnect,
            self._act_quit,
            self._act_pause
        ])
        
        self._tray_icon = SystemTrayIcon(self)
        self._tray_icon.setIcon(QIcon(":/images/logo"))
        self._tray_icon.setContextMenu(self._tray_menu)
        
        self._tray_icon.show()
        
        # Connect signals
        self.ui.assocBtn.clicked.connect(self.onAssocBtnClicked)
        self.ui.briSlider.valueChanged.connect(self.onBriSliderChanged)
        self.ui.scaleSlider.valueChanged.connect(self.onScaleSliderChanged)
        for w in [self.ui.miBriBtn, self.ui.mxBriBtn, self.ui.lwProBtn, self.ui.hiProBtn]:
            w.clicked.connect(self.onMinMaxBtnClicked)
        self._slider_animator.stateChanged.connect(self.onAnimationStateChanged)
        
        self._act_show.triggered.connect(self.onShowAction)
        self._act_reconnect.triggered.connect(self.onReconnectAction)
        self._act_quit.triggered.connect(self.onQuitAction)
        self._act_pause.toggled.connect(self.onPauseActToggled)
        self._tray_icon.activated.connect(self.onTrayIconActivated)
        
    def onQuitAction(self, checked: bool):
        if self._anim_in_progress:
            self._pending_close = True
        else:
            self.close()
            
    def onReconnectAction(self, checked: bool):
        self.show()
        
    def onShowAction(self, checked: bool):
        self.controller.connect()
        
    def onPauseActToggled(self, checked: bool):
        if self.controller.paused():
            self._act_pause.setIcon(self._icon_resume)
            self._act_pause.setText(self._text_resume)
            self._tray_icon.setToolTip(self.tr("Manual Mode"))
            self.controller.pause()
        else:
            self._act_pause.setIcon(self._icon_pause)
            self._act_pause.setText(self._text_pause)
            self._tray_icon.setToolTip(self.tr("Auto Mode"))
            self.controller.resume()
            
    def onTrayIconActivated(self, reason: QtWidgets.QSystemTrayIcon.ActivationReason):
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.show()
            else:
                self.hide()
                
    def onAssocBtnClicked(self, checked: bool):
        pass
    
    def onBriSliderChanged(self, value: int):
        pass
    
    def onScaleSliderChanged(self, value: int):
        pass
    
    def onMinMaxBtnClicked(self, checked: bool):
        pass
    
    def onAnimationStateChanged(self, checked: bool):
        pass
    
    def init_controller(self):
        self.controller = BrightnessController(
            camera_index=self.config.get('camera_index', 0)
        )
        if not self.controller.is_initialized:
            QMessageBox.warning(
                self,
                self.tr("Camera Error"),
                self.tr("Failed to initialize camera. Please check your webcam connection.")
            )
            return
        
        
    def _start_controller(self):
        # Create and start worker thread
        self.worker = BrightnessWorker(self.controller, self.config)
        self.worker.brightness_updated.connect(self.on_brightness_updated)
        self.worker.error_occurred.connect(self.on_worker_error)
        self.worker.start()

    def start_brightness_controller(self):
        """Start the brightness controller worker thread."""
        try:
            if self.controller is None:
                self.init_controller()
            self._start_controller()
            
        except Exception as e:
            logger.error(f"Error starting brightness controller: {e}")
            self._tray_icon.showMessage(self.tr("Error"), self.tr("Failed to start brightness controller: {e}").format(e))
        else:
            logger.info("Brightness controller started")
            self._tray_icon.showMessage(self.tr("Running"), self.tr("Adjusting brightness..."))
    
    def stop_brightness_controller(self):
        """Stop the brightness controller worker thread."""
        if self.worker is not None:
            self.worker.stop()
            self._tray_icon.showMessage(self.tr("Paused"), self.tr("Brightness adjusting stopped."))
            logger.info("Brightness controller stopped")
    
    def on_brightness_updated(self, detected_brightness: float, system_brightness: int):
        """Update UI with new brightness values."""
        self.ui.luxLCD.display(detected_brightness)
        self.ui.briLCD.display(system_brightness)
    
    def on_worker_error(self, error_msg: str):
        """Handle worker errors."""
        logger.error(f"Worker error: {error_msg}")
        self._tray_icon.showMessage(self.tr("Error"), self.tr("Something wrong with the daemon controller."))
    
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
            self.tr("Exit Application"),
            self.tr("Are you sure you want to exit? The brightness controller will stop."),
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
