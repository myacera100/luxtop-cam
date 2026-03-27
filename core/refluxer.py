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


class RefluxerBaseException(Exception):
    """Base exception for the module."""
    def __init__(self, msg, *args, **kwargs):
        super().__init__(*args)
        logger.error(msg)


class DeviceException(RefluxerBaseException):
    """Error occurred during image capturing process."""
    ...

    
class InitializationException(RefluxerBaseException):
    """Error occurred during refluxer initialization."""
    ...

    
class SamplingException(RefluxerBaseException):
    """Error occurred during computing lightness from image."""
    ...

    
class CalculationException(RefluxerBaseException):
    """Error occurred during mapping ambient lightness to system brightness."""
    ...

    
class MonitorReadException(RefluxerBaseException):
    """Error occurred during read operation from system monitor."""
    ...

    
class MonitorWriteException(RefluxerBaseException):
    """Error occurred during write operation to system monitor."""
    ...
    

class Refluxer:
    """Manages brightness detection and system brightness control."""
    
    def __init__(self, camera_index: int = 0, min_brightness: int = 10, max_brightness: int = 100,
                 sensitivity: float = 0.8):
        """
        Initialize the brightness controller.
        
        Args:
            camera_index: Index of the webcam to use (default: 0)
        """
        self.camera_index = camera_index
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.sensitivity = sensitivity
        
        self.cap = None
        self.is_initialized = False
        self.ema = EMA(timeperiod=5)
        
        self._initialize_camera()
    
    def _initialize_camera(self):
        """
        Initialize the image-capturing camera device.
        """
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise DeviceException(f'Error initializing camera at index <{self.camera_index}>.')
        
        self.is_initialized = True
        logger.info(f"Camera <{self.camera_index}> initialized successfully.")
            
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a frame from the webcam.
        
        Returns:
            np.ndarray: The captured frame, or None if capture failed
        """
        if not self.is_initialized or self.cap is None:
            return None
        
        success, frame = self.cap.read()
        if not success:
            raise SamplingException(f'Error capturing frame from camera <{self.camera_index}>.')
        return frame
    
    def get_image_lightness(self, frame: np.ndarray) -> float:
        """
        Calculate ambient lightness value from image frame.
        
        Uses multiple methods to determine ambient brightness:
        - Average pixel intensity
        - Weighted luminosity calculation
        
        Args:
            frame: Input image frame
        
        Returns:
            float: ambient lightness value
        """
        if frame is None or frame.size == 0:
            return 0.0
        
        if self.cap is not None:
            # Retrieve EV from the capturing device which is commonly available
            camera_ev = self.cap.get(cv2.CAP_PROP_EXPOSURE)
        else:
            # Specify a typical EV for indoor lighting
            camera_ev = 6.0
        
        try:
            luma = ImageLightness(camera_ev)
            perceived_lightness = luma.calculate_perceived_lightness(frame)

        except Exception as e:
            raise CalculationException(f"Error calculating brightness: {e}") from None

        else:
            logger.debug(f"Calculated brightness: {perceived_lightness:.2f}")
            return perceived_lightness
    
    def calc_system_brightness(
        self,
        detected_lightness: float,
        sensitivity: float = None
    ) -> int:
        """
        Map detected lightness to monitor brightness level.
        
        Uses non-linear mapping to provide better control across the brightness range.
        
        Args:
            detected_lightness: Detected lightness from camera (0-255)
            min_bright: Minimum monitor brightness to set (0-100)
            max_bright: Maximum monitor brightness to set (0-100)
            sensitivity: Sensitivity multiplier for brightness changes (0-1)
        
        Returns:
            int: Monitor brightness to set (0-100)
        """
        
        # Normalize detected lightness to 0-1 range
        normalized = detected_lightness / 255.0
        
        if not sensitivity:
            sensitivity = self.sensitivity
        
        # Apply non-linear mapping (logarithmic for better perception)
        if normalized < 0.3:
            # Dark region - use lower part of monitor brightness
            sensitive_brightness = self.min_brightness+ (normalized / 0.3) * (50 - self.min_brightness)
        elif normalized > 0.7:
            # Bright region - use upper part of monitor brightness
            sensitive_brightness = 50 + ((normalized - 0.7) / 0.3) * (self.max_brightness - 50)
        else:
            # Mid range - linear interpolation
            sensitive_brightness = 50
        
        try:
            # Apply sensitivity factor (smoothing)
            current_brightness = self.get_system_brightness()

        except MonitorReadException as e:
            raise CalculationException(f'Error calculating system brightness: {e}') from None
        
        else:
            if current_brightness is not None:
                sensitive_brightness = (sensitive_brightness * sensitivity) + (current_brightness * (1 - sensitivity))
            
            # Clamp to valid range
            monitor_brightness = max(self.min_brightness, min(int(sensitive_brightness), self.max_brightness))
            
            logger.debug(
                f"Calculated brightness: detected={detected_lightness:.2f}, monitor={monitor_brightness}"
            )
            return monitor_brightness
    
    def set_system_brightness(self, brightness: int) -> bool:
        """
        Set the system monitor brightness.
        
        Args:
            brightness: Brightness level to set (0-100)
        
        Returns:
            bool: True if successful, False otherwise
        """
        
        # 
        brightness = max(0, min(100, brightness))
        try:
            results = sbc.set_brightness(brightness, no_return=False)

        except Exception as e:
            raise MonitorWriteException(f"Error setting system brightness: {e}") from None
        
        else:
            return True
    
    def get_system_brightness(self) -> Optional[int]:
        """
        Get current system monitor brightness.
        
        Returns:
            int: Current brightness level (0-100), or None if retrieval failed
        """
        try:
            brightness = sbc.get_brightness()
            if isinstance(brightness, list):
                brightness = brightness[self.camera_index]
            return int(brightness)
        except IndexError as e:
            raise MonitorReadException(f'Error identifying system monitor: {e}')
        
        except Exception as e:
            raise MonitorReadException(f'Error reading brightness from system monitor: {e}') from None
    
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
    
    def __init__(self, controller: Refluxer, config: Dict[str, Any]):
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
                    monitor_brightness = self.controller.calc_system_brightness(
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
