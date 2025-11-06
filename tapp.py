#!/usr/bin/env python3

"""
EVE SDK Interactive Test Program for Raspberry Pi.
This module provides an interactive menu-driven program for testing EVE SDK functionality:

FEATURES:
1. Interactive frame and metadata capture
2. Real-time status monitoring
3. Multiple capture modes (image, metadata, or both)
4. User-friendly menu interface
5. Proper error handling and cleanup
6. Cross-platform compatibility

CAPTURE MODES:
- 'c': Capture frame (image + metadata) -> saves to image.jpg and metadata.txt
- 'm': Capture metadata only -> saves to metadata.txt
- 'i': Capture image only -> saves to image.jpg
- 'x': Exit program

RASPBERRY PI SETUP REQUIREMENTS:
1. Enable I2C interface: sudo raspi-config > Interface Options > I2C
2. Enable camera (if using): sudo raspi-config > Interface Options > Camera
3. Install required packages:
   sudo apt-get update
   sudo apt-get install python3-opencv python3-numpy python3-rpi.gpio python3-pytest
4. Add user to required groups:
   sudo usermod -a -G i2c,spi,gpio,dialout $USER
5. Install EVE SDK in /home/pi/eve_sdk/ or update path in config

USAGE:
   python app.py                          # Interactive menu selection
   python app.py interactive              # Run interactive program directly
   python app.py -i                       # Run interactive program directly
   pytest app.py                          # Run with pytest (if needed)
"""

import time
import json
import cv2
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime

# Add the library path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

from eve.eve_wrapper import EveWrapper

def test_prerequisites():
    """Test for required modules and packages"""
    missing_modules = []
    
    # Required modules
    required_modules = ['yaml', 'cv2', 'numpy', 'pytest']
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Install with: pip install " + " ".join(missing_modules))
        return False
    else:
        print("✅ All required modules available")
        return True


def run_test_program():
    """
    Interactive test program for EVE SDK frame and metadata capture.
    
    This function runs an interactive menu-driven program that allows users to:
    - Capture current frame (image + metadata)
    - Capture metadata only
    - Capture image only
    - Exit the program
    
    Controls:
    - 'c': Capture frame (image + metadata) -> saves to image.jpg and metadata.txt
    - 'm': Capture metadata only -> saves to metadata.txt
    - 'i': Capture image only -> saves to image.jpg  
    - 'x': Exit program
    """
    
    print("EVE SDK Interactive Test Program")
    print("=" * 50)
    
    # Load configuration
    try:
        with open("config.yaml") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ config.yaml not found. Please ensure the configuration file exists.")
        return
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    # Initialize EVE wrapper
    try:
        print("🔧 Initializing EVE SDK...")
        
        # Get configuration
        i2c_config = config.get('i2c', {})
        eve_config = config.get('eve', {})
        
        wrapper = EveWrapper(
            comport=eve_config.get('comport', 0),
            i2cAdapter=i2c_config.get('bus', 0),
            i2cDevice=i2c_config.get('device_address', 0x30),
            i2cIRQ=i2c_config.get('irq_pin', 26),
            pipelineVersion=eve_config.get('pipeline_version', 0),
            evePath=eve_config.get('eve_path', '/opt/EVE-6.6.0-Source/bin'),
            toJpg=eve_config.get('to_jpg', True),
            copyImage=eve_config.get('copy_image', True),  # Enable image copying for capture
            maxWidth=eve_config.get('max_width', 800),
            driverPath=eve_config.get('driver_path', '/home/lattice/mY_Work/eve-cam/clnx_camDrvEn')
        )
        
        # Initialize with metadata camera
        wrapper.init(useMetadataCamera=True)
        print("✅ EVE SDK initialized successfully")
        
        # Configure features from config
        features = config.get('features', {
            "face_detection": {"enabled": True},
            "person_detection": {"enabled": True},
            "hand_landmarks": {"enabled": True},
            "face_id": {"enabled": False},
            "face_id_multi": {"enabled": False},
            "object_detection": {"enabled": False}
        })
        
        if wrapper.isFpgaEnabled():
            wrapper.configureFpga(features)
        else:
            wrapper.configure(features)
            
        print("✅ Features configured")
        
    except Exception as e:
        print(f"❌ Failed to initialize EVE SDK: {e}")
        return
    
    # Helper functions
    def show_menu():
        print("\n" + "=" * 50)
        print("📋 INTERACTIVE MENU")
        print("=" * 50)
        print("Commands:")
        print("  'c' - Capture frame (image + metadata)")
        print("  'm' - Capture metadata only")
        print("  'i' - Capture image only")
        print("  'x' - Exit program")
        print("=" * 50)
    
    def save_metadata(filename="metadata.txt"):
        """Save current metadata to file"""
        try:
            metadata = wrapper.get_json()
            if metadata:
                with open(filename, 'w') as f:
                    json.dump(metadata, f, indent=2)
                print(f"✅ Metadata saved to {filename}")
                return True
            else:
                print("⚠️  No metadata available to save")
                return False
        except Exception as e:
            print(f"❌ Failed to save metadata: {e}")
            return False
    
    def save_image(filename="image.jpg"):
        """Save current image to file"""
        try:
            # Try to get image array first
            image_array = wrapper.get_image()
            if image_array is not None:
                cv2.imwrite(filename, image_array)
                print(f"✅ Image saved to {filename}")
                return True
            else:
                # Try to get JPG data as fallback
                jpg_data = wrapper.get_image_jpg()
                if jpg_data:
                    with open(filename, 'wb') as f:
                        f.write(jpg_data)
                    print(f"✅ Image (JPG) saved to {filename}")
                    return True
                else:
                    print("⚠️  No image available to save")
                    return False
        except Exception as e:
            print(f"❌ Failed to save image: {e}")
            return False
    
    def get_status_info():
        """Get current system status"""
        frame_id = wrapper.get_frame_id()
        fpga_enabled = wrapper.isFpgaEnabled()
        using_metadata = wrapper.isUsingMetadata()
        
        print(f"📊 Status: Frame ID: {frame_id} | FPGA: {'✅' if fpga_enabled else '❌'} | Metadata Camera: {'✅' if using_metadata else '❌'}")
    
    # Main program loop
    try:
        show_menu()
        
        while True:
            # Show current status
            get_status_info()
            
            # Get user input
            try:
                # For cross-platform compatibility, use input() instead of getch()
                print("\nEnter command (c/m/i/x): ", end="", flush=True)
                command = input().strip().lower()
                
                if command == 'c':
                    print("\n🔄 Capturing frame (image + metadata)...")
                    # Allow some time for frame capture
                    time.sleep(0.1)
                    
                    saved_metadata = save_metadata("metadata.txt")
                    saved_image = save_image("image.jpg")
                    
                    if saved_metadata and saved_image:
                        print("🎉 Frame capture completed!")
                    elif saved_metadata or saved_image:
                        print("⚠️  Partial frame capture completed")
                    else:
                        print("❌ Frame capture failed")
                
                elif command == 'm':
                    print("\n🔄 Capturing metadata...")
                    time.sleep(0.1)
                    save_metadata("metadata.txt")
                
                elif command == 'i':
                    print("\n🔄 Capturing image...")
                    time.sleep(0.1)
                    save_image("image.jpg")
                
                elif command == 'x':
                    print("\n👋 Exiting program...")
                    break
                
                elif command == '':
                    # Empty input, just continue
                    continue
                    
                else:
                    print(f"\n❌ Unknown command: '{command}'")
                    print("Please use: 'c' (capture), 'm' (metadata), 'i' (image), or 'x' (exit)")
                    
            except KeyboardInterrupt:
                print("\n\n⏹️  Program interrupted by user (Ctrl+C)")
                break
            except EOFError:
                print("\n\n⏹️  End of input detected")
                break
                
    except Exception as e:
        print(f"\n❌ Unexpected error in main loop: {e}")
    
    finally:
        # Cleanup
        try:
            print("\n🧹 Cleaning up...")
            wrapper.stop()
            print("✅ EVE SDK stopped successfully")
        except Exception as e:
            print(f"⚠️  Warning during cleanup: {e}")
        
        print("📄 Program ended")


def run_interactive_program():
    """
    Wrapper function to run the interactive test program.
    This can be called directly or from the command line.
    """
    if not test_prerequisites():
        print("\n❌ Prerequisites check failed. Please install missing dependencies.")
        return
    
    run_test_program()


# Main execution - just run the interactive program directly
if __name__ == "__main__":
    run_interactive_program()
