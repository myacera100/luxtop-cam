"""
Core brightness control logic.
Handles webcam image capture, brightness analysis, and system brightness adjustment.
"""
import cv2
import numpy as np
from typing import Dict, Optional, Any
import screen_brightness_control as sbc
from PyQt5.QtCore import pyqtSignal, QThread, QTimer
from numta.streaming import StreamingEMA as EMA

from utils.logger import setup_logger
from core.luminance import ImageLightness

logger = setup_logger(__name__)


class BrightnessController:
    """Manages brightness detection and system brightness control."""
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize the brightness controller.
        
        Args:
            camera_index: Index of the webcam to use (default: 0)
        """
        self.camera_index = camera_index
        self.cap = None
        self.is_initialized = False
        self.refluxer = EMA(timeperiod=5)
        
        self._initialize_camera()
    
    def _initialize_camera(self) -> bool:
        """
        Initialize the webcam capture.
        
        Returns:
            bool: True if camera initialized successfully, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera at index {self.camera_index}")
                return False
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            # self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_initialized = True
            logger.info(f"Camera initialized successfully at index {self.camera_index}")
            return True
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a frame from the webcam.
        
        Returns:
            np.ndarray: The captured frame, or None if capture failed
        """
        if not self.is_initialized or self.cap is None:
            return None
        
        try:
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                logger.warning("Failed to capture frame from camera")
                return None
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def get_image_lightness(self, frame: np.ndarray) -> float:
        """
        Calculate brightness value from image frame.
        
        Uses multiple methods to determine ambient brightness:
        - Average pixel intensity
        - Weighted luminosity calculation
        
        Args:
            frame: Input image frame (BGR)
        
        Returns:
            float: Brightness value (0-255)
        """
        if frame is None or frame.size == 0:
            return 0.0
        
        try:
            if self.cap is not None:
                # Retrieve EV from the capturing device which is commonly available
                camera_ev = self.cap.get(cv2.CAP_PROP_EXPOSURE)
            else:
                # Specify a typical EV for indoor lighting
                camera_ev = 6.0
            luma = ImageLightness(camera_ev)
            perceived_lightness = luma.calculate_perceived_lightness(frame)
            
            logger.debug(f"Calculated brightness: {perceived_lightness:.2f}")
            return perceived_lightness

        except Exception as e:
            logger.error(f"Error calculating brightness: {e}")
            return 0.0
    
    def get_monitor_brightness(
        self,
        detected_lightness: float,
        min_bright: int = 10,
        max_bright: int = 100,
        sensitivity: float = 0.8
    ) -> int:
        """
        Map detected brightness to monitor brightness level.
        
        Uses non-linear mapping to provide better control across the brightness range.
        
        Args:
            detected_lightness: Detected lightness from camera (0-255)
            min_bright: Minimum monitor brightness to set (0-100)
            max_bright: Maximum monitor brightness to set (0-100)
            sensitivity: Sensitivity multiplier for brightness changes (0-1)
        
        Returns:
            int: Monitor brightness to set (0-100)
        """
        try:
            # Normalize detected brightness to 0-1 range
            normalized = detected_lightness / 255.0
            
            # Apply non-linear mapping (logarithmic for better perception)
            if normalized < 0.3:
                # Dark region - use lower part of monitor brightness
                mapped = min_bright + (normalized / 0.3) * (50 - min_bright)
            elif normalized > 0.7:
                # Bright region - use upper part of monitor brightness
                mapped = 50 + ((normalized - 0.7) / 0.3) * (max_bright - 50)
            else:
                # Mid range - linear interpolation
                mapped = 50
            
            # Apply sensitivity factor (smoothing)
            current_brightness = self.get_system_brightness()
            if current_brightness is not None:
                mapped = (mapped * sensitivity) + (current_brightness * (1 - sensitivity))
            
            # Clamp to valid range
            monitor_brightness = max(min_bright, min(int(mapped), max_bright))
            
            logger.debug(
                f"Mapped brightness: detected={detected_lightness:.2f}, "
                f"normalized={normalized:.2f}, monitor={monitor_brightness}"
            )
            return monitor_brightness
        except Exception as e:
            logger.error(f"Error calculating brightness: {e}")
            return 50
    
    def set_system_brightness(self, brightness: int) -> bool:
        """
        Set the system monitor brightness.
        
        Args:
            brightness: Brightness level to set (0-100)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            brightness = max(0, min(100, brightness))
            sbc.set_brightness(brightness)
            logger.info(f"System brightness set to {brightness}%")
            return True
        except Exception as e:
            logger.error(f"Error setting system brightness: {e}")
            return False
    
    def get_system_brightness(self) -> Optional[int]:
        """
        Get current system monitor brightness.
        
        Returns:
            int: Current brightness level (0-100), or None if retrieval failed
        """
        try:
            brightness = sbc.get_brightness()
            if isinstance(brightness, list):
                brightness = brightness[0]  # Get first monitor if multiple
            return int(brightness)
        except Exception as e:
            logger.error(f"Error getting system brightness: {e}")
            return None
    
    def cleanup(self):
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
            logger.info("Camera resources released")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()
        
        
class BrightnessWorker(QThread):
    """Worker thread for brightness control to prevent GUI freezing."""
    
    brightness_updated = pyqtSignal(float, int)  # detected_brightness, system_brightness
    error_occurred = pyqtSignal(str)
    
    def __init__(self, controller: BrightnessController, config: Dict[str, Any]):
        super().__init__()
        self.controller = controller
        self.config = config
        self.is_running = False
        self.should_process = True
    
    def run(self):
        """Main worker loop."""
        self.is_running = True
        
        while self.is_running and self.should_process:
            try:
                # Capture frame
                frame = self.controller.capture_frame()
                
                if frame is None:
                    self.error_occurred.emit("Failed to capture frame from camera")
                    self.msleep(int(self.config.get('capture_interval', 2.0) * 1000))
                    continue
                
                # Calculate brightness
                perceived_lightness = self.controller.get_image_lightness(frame)
                
                # Map and set brightness if enabled
                if self.config.get('enabled', True):
                    monitor_brightness = self.controller.get_monitor_brightness(
                        perceived_lightness,
                        min_bright=self.config.get('min_brightness', 10),
                        max_bright=self.config.get('max_brightness', 100),
                        dark_threshold=self.config.get('dark_threshold', 50),
                        bright_threshold=self.config.get('bright_threshold', 150),
                        sensitivity=self.config.get('brightness_sensitivity', 0.8)
                    )
                    
                    # Set system brightness
                    self.controller.set_system_brightness(monitor_brightness)
                
                else:
                    monitor_brightness = self.controller.get_system_brightness() or 50
                
                # Emit signal with updated values
                self.brightness_updated.emit(perceived_lightness, monitor_brightness)
                
                # Sleep for configured interval
                self.msleep(int(self.config.get('capture_interval', 2.0) * 1000))
                
            except Exception as e:
                logger.error(f"Error in brightness worker: {e}")
                self.error_occurred.emit(f"Error: {str(e)}")
                self.msleep(2000)
    
    def stop(self):
        """Stop the worker thread."""
        self.is_running = False
        self.wait()
