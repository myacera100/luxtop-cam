# Auto Brightness Controller

An intelligent Python application that automatically adjusts your system monitor brightness based on ambient light detection from your webcam.

## Features

- **Real-time Light Detection**: Captures images from your webcam and analyzes brightness levels
- **Automatic Brightness Control**: Adjusts monitor brightness based on ambient lighting conditions
- **PyQt5 GUI**: User-friendly interface for configuring parameters
- **System Tray Integration**: Minimize to system tray on Windows with quick access
- **Customizable Settings**: Adjust sensitivity, capture intervals, and brightness ranges
- **Logging**: Comprehensive logging for debugging and monitoring

## Requirements

- Python 3.8+
- Windows OS (primary support)
- Webcam
- Monitor with brightness control support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/auto-brightness-controller.git
cd auto-brightness-controller
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python src/main.py
```

## Configuration

Settings can be configured through the GUI or by editing `config/config.json`:

```json
{
  "capture_interval": 2.0,
  "min_brightness": 10,
  "max_brightness": 100,
  "brightness_sensitivity": 0.8,
  "dark_threshold": 50,
  "bright_threshold": 150,
  "enabled": true,
  "camera_index": 0
}
```

### Configuration Parameters

- **capture_interval**: Time in seconds between webcam captures (default: 2.0)
- **min_brightness**: Minimum brightness level to set (0-100, default: 10)
- **max_brightness**: Maximum brightness level to set (0-100, default: 100)
- **brightness_sensitivity**: Sensitivity multiplier for brightness changes (default: 0.8)
- **dark_threshold**: Pixel intensity below which image is considered dark (default: 50)
- **bright_threshold**: Pixel intensity above which image is considered bright (default: 150)
- **enabled**: Enable/disable automatic brightness control (default: true)
- **camera_index**: Webcam index to use (default: 0)

## Usage

### GUI Window

The main application window provides:
- **Enable/Disable Toggle**: Turn automatic brightness control on/off
- **Current Brightness Display**: Shows current monitor and detected ambient brightness
- **Parameter Settings**: Adjust all configuration parameters
- **Status Information**: Real-time feedback on brightness adjustments
- **System Tray Integration**: Minimize to tray for background operation

### System Tray

Right-click the system tray icon to:
- Show/Hide main window
- Enable/Disable brightness control
- Exit application

## How It Works

1. **Image Capture**: Periodically captures frames from the webcam
2. **Brightness Analysis**: Calculates average pixel intensity (0-255)
3. **Mapping**: Maps detected brightness to monitor brightness level
4. **Adjustment**: Sets monitor brightness accordingly
5. **Smoothing**: Applies sensitivity factor to prevent flickering

## Architecture

- **BrightnessController**: Core logic for brightness calculation and system control
- **MainWindow**: PyQt5 GUI for user interaction and settings management
- **SystemTrayIcon**: Windows system tray integration and quick actions
- **Logger**: Centralized logging for debugging

## Troubleshooting

### Camera not detected
- Ensure your webcam is properly connected
- Check if another application is using the camera
- Try changing the `camera_index` in configuration

### Brightness not changing
- Verify your monitor supports brightness control
- Check Windows display settings allow brightness adjustment
- Ensure the application has necessary permissions

### GUI not responding
- The application may be processing heavy image data
- Increase `capture_interval` to reduce CPU usage

## License

MIT License

## Support

For issues and feature requests, please open an issue on GitHub.