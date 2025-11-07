# EVE SDK Interactive Test Program

An interactive menu-driven Python application for testing EVE SDK functionality on Raspberry Pi and other platforms. This program provides real-time frame and metadata capture with configurable AI features including face detection, person detection, and hand landmarks.

## Features

- **Interactive Menu Interface**: User-friendly command-driven interface
- **Multiple Capture Modes**: 
  - Frame capture (image + metadata)
  - Metadata-only capture
  - Image-only capture
- **Real-time Configuration**: Interactive settings/configuration mode
- **AI Feature Support**: Face detection, person detection, hand landmarks, face ID, and object detection
- **Cross-platform Compatibility**: Works on Raspberry Pi and other platforms
- **Proper Error Handling**: Comprehensive error handling and cleanup

## Prerequisites

### Required Python Packages

Install the necessary Python packages using pip:

```bash
pip install opencv-python numpy PyYAML pytest
```

**Package Details:**
- `opencv-python` (cv2) - Computer vision and image processing
- `numpy` - Numerical computing support  
- `PyYAML` - YAML configuration file parsing
- `pytest` - Testing framework (optional, for running tests)

### System Requirements

#### For Raspberry Pi:
1. **Enable I2C interface:**
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options > I2C > Enable
   ```

2. **Enable camera (if using camera):**
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options > Camera > Enable
   ```

3. **Install system packages:**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-opencv python3-numpy python3-rpi.gpio python3-pytest
   ```

4. **Add user to required groups:**
   ```bash
   sudo usermod -a -G i2c,spi,gpio,dialout $USER
   ```

5. **EVE SDK Installation:**
   - Install EVE SDK in `/opt/EVE-6.6.0-Source/bin` or update the path in `config.yaml`
   - Ensure proper camera driver setup (path configurable in `config.yaml`)

#### For Other Platforms:
- Ensure Python 3.6+ is installed
- Install the required Python packages listed above
- Configure `config.yaml` with appropriate paths for your system

### Configuration

The program requires a `config.yaml` file in the root directory. Example configuration:

```yaml
i2c:
  start_flag: 0x7E
  bus: 0
  device_address: 0x30
  irq_pin: 26

eve:
  comport: 0
  pipeline_version: 0
  eve_path: '/opt/EVE-6.6.0-Source/bin'
  driver_path: '/home/lattice/mY_Work/eve-cam/clnx_camDrvEn'
  to_jpg: true
  copy_image: false
  max_width: 800
  use_metadata_camera: true

features:
  face_detection:
    enabled: true
  person_detection:
    enabled: true
  hand_landmarks:
    enabled: true
  face_id:
    enabled: false
  face_id_multi:
    enabled: false
  object_detection:
    enabled: false
```

## How to Run

### Basic Usage

1. **Navigate to the project directory:**
   ```bash
   cd /path/to/clnxsom-python-eve
   ```

2. **Run the interactive program:**
   ```bash
   python tapp.py
   ```

### Alternative Run Methods

```bash
# Run interactive program directly
python tapp.py interactive

# Run with short flag
python tapp.py -i

# Run tests (if needed)
pytest tapp.py
```

## Interactive Commands

Once the program starts, you'll see an interactive menu with the following commands:

| Command | Description |
|---------|-------------|
| `c` | **Capture frame** - Saves both image (`image.jpg`) and metadata (`metadata.txt`) |
| `m` | **Capture metadata only** - Saves metadata to `metadata.txt` |
| `i` | **Capture image only** - Saves image to `image.jpg` |
| `s` | **Settings/Configuration mode** - Interactive feature configuration |
| `x` | **Exit program** - Safely stop and exit |

### Configuration Mode Commands

When in settings mode (press `s`), you can use these commands:

| Command | Description |
|---------|-------------|
| `1` | Toggle Face Detection |
| `2` | Toggle Person Detection |
| `3` | Toggle Hand Landmarks |
| `4` | Toggle Face ID |
| `5` | Toggle Face ID Multi |
| `6` | Toggle Object Detection |
| `a` | Enable All Features |
| `d` | Disable All Features |
| `r` | Reset to Config File Defaults |
| `s` | Save Current Settings to Config File |
| `b` | Back to Main Menu |

## Output Files

The program generates the following output files:

- **`image.jpg`** - Captured image file
- **`metadata.txt`** - JSON-formatted metadata containing detection results

## Troubleshooting

### Common Issues

1. **Missing modules error:**
   ```bash
   pip install opencv-python numpy PyYAML pytest
   ```

2. **Config file not found:**
   - Ensure `config.yaml` exists in the project root directory
   - Check the configuration format matches the example above

3. **EVE SDK initialization failed:**
   - Verify EVE SDK is installed at the path specified in `config.yaml`
   - Check I2C permissions and device connectivity
   - Ensure camera driver is properly installed

4. **Permission errors on Raspberry Pi:**
   ```bash
   sudo usermod -a -G i2c,spi,gpio,dialout $USER
   # Then logout and login again
   ```

### System Status Information

The program displays real-time status information including:
- Current frame ID
- FPGA enable status
- Metadata camera status

## Project Structure

```
clnxsom-python-eve/
├── README.md              # This file
├── tapp.py               # Main application script
├── config.yaml           # Configuration file
├── library/              # EVE SDK wrapper library
│   └── eve/
│       ├── eve_wrapper.py
│       └── eve_python/   # EVE SDK Python bindings
└── metadata.txt          # Generated metadata output
```

## License

This project is part of the Lattice Semiconductor EVE SDK ecosystem. Please refer to your EVE SDK license agreement for usage terms.