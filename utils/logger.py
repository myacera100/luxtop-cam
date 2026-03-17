"""
Logging configuration for the application.
"""
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

# Create logs directory
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Create log file name with timestamp
LOG_FILE = LOG_DIR / f"brightness_controller_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Setup and configure logger for the application.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: INFO)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding multiple handlers if logger already has them
    if not logger.handlers:
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger