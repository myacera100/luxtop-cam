import cv2
import numpy as np
from utils.logger import setup_logger


logger = setup_logger(__name__)

class ImageLightness:
    def __init__(self, target_exposure_value=0.0):
        """
        Initialize lightness calculator with exposure awareness
        
        Args:
            target_exposure_value: Target EV (Exposure Value) compensation (0 = no additional exposure)
        """
        self.target_exposure_value = target_exposure_value
        
    def linearize_srgb(self, channel):
        """Convert sRGB to linear space"""
        channel = np.clip(channel / 255.0, 0, 1)
        mask = channel <= 0.04045
        channel_linear = np.where(
            mask,
            channel / 12.92,
            ((channel + 0.055) / 1.055) ** 2.4
        )
        return channel_linear
    
    def calculate_luma_709(self, r, g, b):
        """BT.709 luma calculation"""
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
    def analyze_image_exposure(self, image_linear):
        """
        Analyze exposure characteristics from image data
        
        Returns:
            dict: Exposure metrics
        """
        mean_luminance = np.mean(image_linear)
        
        # Calculate clipping (over/underexposure)
        overexposed_ratio = np.sum(image_linear >= 0.98) / image_linear.size
        underexposed_ratio = np.sum(image_linear <= 0.02) / image_linear.size
        
        # Calculate dynamic range utilization
        percentiles = np.percentile(image_linear, [1, 5, 95, 99])
        dynamic_range_used = percentiles[3] - percentiles[0]
        
        # Calculate exposure deviation from 18% gray
        # Assume 0.18 (18% gray) is ideal exposure in linear space
        exposure_deviation = np.log2(mean_luminance / 0.18)
        
        return {
            'overexposed_ratio': overexposed_ratio,
            'underexposed_ratio': underexposed_ratio,
            'dynamic_range_used': dynamic_range_used,
            'exposure_deviation': exposure_deviation,
        }
        
    def get_external_compensation(self):
        if self.target_exposure_value is not None:
            return 2.5 * (2 ** self.target_exposure_value)
        return 1.0
    
    def calculate_exposure_compensation(self, exposure_analysis):
        """
        Calculate exposure compensation factor
        
        Args:
            exposure_analysis: Metrics from analyze_image_exposure()
            
        Returns:
            float: Exposure compensation factor (0.5-2.0 range)
        """
        # Start with deviation from ideal exposure (18% gray)
        deviation_stops = exposure_analysis['exposure_deviation']
        
        # Adjust for clipping
        clipping_penalty = 1.0
        if exposure_analysis['overexposed_ratio'] > 0.05:
            # Overexposed - reduce perceived lightness penalty
            clipping_penalty = 1.0 - (exposure_analysis['overexposed_ratio'] * 2)
        
        if exposure_analysis['underexposed_ratio'] > 0.1:
            # Underexposed - increase perceived lightness penalty
            clipping_penalty *= 1.0 - (exposure_analysis['underexposed_ratio'])
        
        # Convert stops to linear compensation factor
        # 1 stop = factor of 2 in linear lightness
        exposure_compensation = (2 ** (-deviation_stops)) * clipping_penalty
        
        # Clamp to reasonable range
        exposure_compensation = np.clip(exposure_compensation, 0.5, 2.0)
        
        return exposure_compensation
    
    def calculate_dynamic_range_factor(self, exposure_analysis):
        """
        Calculate dynamic range adjustment factor
        
        High dynamic range scenes affect perceived lightness
        """
        dr_used = exposure_analysis['dynamic_range_used']
        
        # If using less dynamic range, image may appear less contrasty
        # which affects perceived lightness
        if dr_used < 0.5:
            # Low contrast scene - perceived lightness reduced
            return 0.9 + (dr_used * 0.2)
        elif dr_used > 0.8:
            # High contrast scene - perceived lightness increased
            return 1.0 + ((dr_used - 0.8) * 0.5)
        else:
            return 1.0
    
    def calculate_perceived_lightness(self, image_rgb):
        """
        Calculate perceived lightness with exposure analysis
        
        Args:
            image_rgb: RGB image (0-255 range)
            image_path: Path to image file (for EXIF extraction)
            
        Returns:
            float or dict: Perceived lightness value
        """
        # Convert to linear space
        r_linear = self.linearize_srgb(image_rgb[:, :, 0])
        g_linear = self.linearize_srgb(image_rgb[:, :, 1])
        b_linear = self.linearize_srgb(image_rgb[:, :, 2])
        
        # Calculate base luma
        luma_map = self.calculate_luma_709(r_linear, g_linear, b_linear)
        base_lightness = np.mean(luma_map)
        
        # Analyze exposure from image data
        exposure_analysis = self.analyze_image_exposure(luma_map)
        
        # Calculate exposure compensation
        exposure_compensation = self.calculate_exposure_compensation(exposure_analysis)
        
        # Calculate dynamic range adjustment
        dr_adjustment = self.calculate_dynamic_range_factor(exposure_analysis)
        
        # Calculate compensation from external EV
        external_compensation = self.get_external_compensation()
        
        return base_lightness * exposure_compensation * external_compensation * dr_adjustment
    
    def calculate_zone_system_lightness(self, image_rgb):
        """
        Calculate lightness using Ansel Adams Zone System approach
        
        Maps image zones (0-10) to perceived lightness
        """
        # Convert to linear space
        r_linear = self.linearize_srgb(image_rgb[:, :, 0])
        g_linear = self.linearize_srgb(image_rgb[:, :, 1])
        b_linear = self.linearize_srgb(image_rgb[:, :, 2])
        
        luma_map = self.calculate_luma_709(r_linear, g_linear, b_linear)
        
        # Convert to log space (stops)
        log_luma = np.log2(luma_map + 0.0001)  # Add small offset to avoid -inf
        
        # Zone System mapping (0-10 zones)
        # Zone V = 18% gray = 0.18 linear
        zone_values = (log_luma - np.log2(0.18)) + 5
        zone_values = np.clip(zone_values, 0, 10)
        
        # Calculate weighted average (mid-tones weighted more)
        weights = 1.0 - np.abs(zone_values - 5) / 5  # Weight zone V highest
        weighted_zone = np.average(zone_values, weights=weights)
        
        # Convert zone back to perceived lightness (0-1)
        perceived_lightness = weighted_zone / 10
        
        return perceived_lightness