# Surface Defect Detection System - Raspberry Pi Setup Guide

## Prerequisites
- Raspberry Pi 4 (recommended) or Raspberry Pi 5
- Raspberry Pi OS (64-bit recommended)
- Camera module (Raspberry Pi Camera Module 3 recommended)
- At least 4GB RAM
- At least 16GB SD card

## System Setup

1. **Update System Packages**
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

2. **Install Required System Packages**
```bash
sudo apt-get install -y \
    python3-libcamera \
    python3-kms++ \
    libcamera-dev \
    libcamera-tools \
    python3-prctl \
    libatlas-base-dev \
    ffmpeg \
    python3-pip \
    python3-venv
```

3. **Enable Camera Interface**
```bash
sudo raspi-config
```
- Navigate to Interface Options
- Select Camera
- Enable the camera interface
- Reboot when prompted

## Application Setup

1. **Clone the Repository**
```bash
git clone https://github.com/joshuatmcauley/surface-defect-detection.git
cd surface-defect-detection
```

2. **Create and Activate Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

## Running the Application

1. **Activate Virtual Environment**
```bash
source venv/bin/activate
```

2. **Run the Application**
```bash
python main.py
```

## Troubleshooting

### Camera Issues
- If camera is not detected:
  ```bash
  sudo libcamera-hello
  ```
  This should show a camera preview. If it doesn't work:
  1. Check camera connection
  2. Verify camera is enabled in raspi-config
  3. Try rebooting

### Performance Issues
- If the application runs slowly:
  1. Close other applications
  2. Consider using a lower resolution camera setting
  3. Check CPU temperature: `vcgencmd measure_temp`

### Memory Issues
- If you encounter memory errors:
  1. Increase swap space:
     ```bash
     sudo dphys-swapfile swapoff
     sudo nano /etc/dphys-swapfile
     # Change CONF_SWAPSIZE=2048
     sudo dphys-swapfile setup
     sudo dphys-swapfile swapon
     ```
  2. Consider using a lighter window manager

## Hardware Recommendations

### Camera Setup
- Use Raspberry Pi Camera Module 3 for best results
- Ensure proper lighting conditions
- Mount camera securely to avoid vibrations

### Processing Power
- Raspberry Pi 4 (4GB or 8GB) recommended
- Consider using active cooling for sustained performance
- Use a high-quality power supply (5V 3A minimum)

## Development Notes

- The application uses PySide6 for GUI
- OpenCV and libcamera for camera operations
- Machine learning models for defect detection
- All processing is done locally on the Pi

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review system logs: `journalctl -u surface-defect-detection`
3. Create an issue on GitHub 