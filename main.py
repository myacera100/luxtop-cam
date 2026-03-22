"""
Main entry point for the Auto Brightness Controller application.
"""
import sys
import json
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from gui.lux_panel import LuxWindow
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Define config path
CONFIG_DIR = Path(__file__).parent
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config():
    """Load configuration from JSON file."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
    
    # Return default config if file doesn't exist
    return {
        "capture_interval": 2.0,
        "min_brightness": 10,
        "max_brightness": 100,
        "brightness_sensitivity": 0.8,
        "dark_threshold": 50,
        "bright_threshold": 150,
        "enabled": True,
        "camera_index": 0
    }


def save_config(config):
    """Save configuration to JSON file."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info("Configuration saved successfully")
    except Exception as e:
        logger.error(f"Error saving config: {e}")


def main():
    """Main application entry point."""
    logger.info("Starting Auto Brightness Controller")
    
    # Load configuration
    config = load_config()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Auto Brightness Controller")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = LuxWindow(config, save_config)
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()