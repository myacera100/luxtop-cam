import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

from utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class BrightnessConfig:
    """Configuration dataclass for brightness controller."""
    capture_interval: int = 5
    min_brightness: int = 10
    max_brightness: int = 100
    enable_auto_adjust: bool = True
    smoothing_enabled: bool = False
    smoothing_alpha: float = 0.7
    logging_enabled: bool = True
    save_stats: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrightnessConfig':
        """Create from dictionary."""
        return cls(**data)
