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
- 's': Settings/Configuration mode -> configure EVE features interactively
- 'f': Face ID Registration mode -> register or clear face IDs
- 'u': Toggle ULP mode (Ultra Low Power) - [e] enabled / [d] disabled
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

from eve_wrapper_ext import EveWrapperExt

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
    - Configure EVE features interactively
    - Exit the program
    
    Controls:
    - 'c': Capture frame (image + metadata) -> saves to image.jpg and metadata.txt
    - 'm': Capture metadata only -> saves to metadata.txt
    - 'i': Capture image only -> saves to image.jpg
    - 's': Settings/Configuration mode -> configure EVE features interactively
    - 'f': Face ID Registration mode -> register or clear face IDs
    - 'u': Toggle ULP mode (Ultra Low Power) - [e] enabled / [d] disabled
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
        
        wrapper = EveWrapperExt(
            comport=eve_config.get('comport', 0),
            i2cAdapter=i2c_config.get('bus', 0),
            i2cDevice=i2c_config.get('device_address', 0x30),
            i2cIRQ=i2c_config.get('irq_pin', 26),
            pipelineVersion=eve_config.get('pipeline_version', 0),
            evePath=eve_config.get('eve_path', '/opt/EVE-6.7.21-Source/bin'),
            toJpg=eve_config.get('to_jpg', True),
            copyImage=eve_config.get('copy_image', True),  # Enable image copying for capture
            maxWidth=eve_config.get('max_width', 800),
            driverPath=eve_config.get('driver_path', '/home/lattice/mY_Work/eve-cam/clnx_camDrvEn'),
            objectDetection=eve_config.get('object_detection', False)
        )
        
        # Initialize with metadata camera setting from config
        use_metadata_camera = eve_config.get('use_metadata_camera', True)
        wrapper.init(useMetadataCamera=use_metadata_camera)
        print("✅ EVE SDK initialized successfully")
        
        # Configure features from config
        features = config.get('features', {
            "face_detection": {"enabled": True},
            "face_validation": {"enabled": False},
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
        print("  's' - Settings/Configuration mode")
        print("  'f' - Face ID Registration mode")
        print("  'u' - Toggle ULP mode")        
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
        ulp_enabled = wrapper.isUlpEnabled()
        
        print(f"📊 Status: Frame ID: {frame_id} | FPGA: {'✅' if fpga_enabled else '❌'} | Metadata Camera: {'✅' if using_metadata else '❌'} | ULP: {'✅' if ulp_enabled else '❌'}")
    
    def show_configuration_menu():
        """Display the configuration menu"""
        print("\n" + "=" * 60)
        print("⚙️  CONFIGURATION MODE")
        print("=" * 60)
        print("Current Feature Settings:")
        
        # Display current feature status
        for feature_name, feature_config in features.items():
            enabled = feature_config.get('enabled', False)
            status = "🟢 ON " if enabled else "🔴 OFF"
            print(f"  {feature_name.replace('_', ' ').title()}: {status}")
        
        print("\nConfiguration Options:")
        print("  '1' - Toggle Face Detection")
        print("  '2' - Toggle Face Validation")
        print("  '3' - Toggle Person Detection") 
        print("  '4' - Toggle Hand Landmarks")
        print("  '5' - Toggle Face ID")
        print("  '6' - Toggle Face ID Multi")
        print("  '7' - Toggle Object Detection")
        print("  'a' - Enable All Features")
        print("  'd' - Disable All Features")
        print("  'r' - Reset to Config File Defaults")
        print("  's' - Save Current Settings to Config File")
        print("  'b' - Back to Main Menu")
        print("=" * 60)
    
    def toggle_feature(feature_key):
        """Toggle a specific feature on/off"""
        if feature_key in features:
            current_state = features[feature_key].get('enabled', False)
            features[feature_key]['enabled'] = not current_state
            new_state = "enabled" if not current_state else "disabled"
            feature_name = feature_key.replace('_', ' ').title()
            print(f"✅ {feature_name} {new_state}")
            return True
        return False
    
    def enable_all_features():
        """Enable all features"""
        for feature_key in features:
            features[feature_key]['enabled'] = True
        print("✅ All features enabled")
    
    def disable_all_features():
        """Disable all features"""
        for feature_key in features:
            features[feature_key]['enabled'] = False
        print("✅ All features disabled")
    
    def reset_to_defaults():
        """Reset features to config file defaults"""
        try:
            with open("config.yaml") as f:
                default_config = yaml.safe_load(f)
            
            default_features = default_config.get('features', {})
            for feature_key in features:
                if feature_key in default_features:
                    features[feature_key]['enabled'] = default_features[feature_key].get('enabled', False)
            
            print("✅ Features reset to config file defaults")
        except Exception as e:
            print(f"❌ Failed to reset to defaults: {e}")
    
    def save_config_to_file():
        """Save current feature settings to config file"""
        try:
            # Load current config
            with open("config.yaml") as f:
                current_config = yaml.safe_load(f)
            
            # Update features section
            current_config['features'] = features
            
            # Write back to file
            with open("config.yaml", 'w') as f:
                yaml.dump(current_config, f, default_flow_style=False, indent=2)
            
            print("✅ Configuration saved to config.yaml")
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
    
    def apply_feature_configuration():
        """Apply current feature configuration to EVE"""
        try:
            print("🔄 Applying feature configuration...")
            
            if wrapper.isFpgaEnabled():
                wrapper.configureFpga(features)
                # Poll settings to get actual state from FPGA
                time.sleep(0.2)  # Give FPGA time to process
                wrapper.poll_settings()
                # Update features dict with actual FPGA state
                actual_state = wrapper.getFpgaState()
                for feature_name, state in actual_state.items():
                    if feature_name in features:
                        features[feature_name]['enabled'] = state['enabled']
                        if 'max_ips' in state:
                            features[feature_name]['max_ips'] = state['max_ips']
                print("✅ Feature configuration applied and verified")
            else:
                wrapper.configure(features)
                print("✅ Feature configuration applied successfully")
        except Exception as e:
            print(f"❌ Failed to apply configuration: {e}")
    
    def show_face_id_menu():
        """Display the Face ID registration menu"""
        print("\n" + "=" * 50)
        print("👤 FACE ID MODE")
        print("=" * 50)
        
        # Check current Face ID status
        face_id_enabled = features.get('face_id', {}).get('enabled', False)
        face_id_multi_enabled = features.get('face_id_multi', {}).get('enabled', False)
        
        print("Current Status:")
        print(f"  Face ID: {'🟢 ENABLED' if face_id_enabled else '🔴 DISABLED'}")
        print(f"  Multi Face ID: {'🟢 ENABLED' if face_id_multi_enabled else '🔴 DISABLED'}")
        
        print("\nCommands:")
        print("  'r' - Register Face ID")
        print("  'c' - Clear Face ID")
        print("  'b' - Back to Main Menu")
        print("=" * 50)
    
    def register_face_id():
        """Register a new Face ID"""
        try:
            print("🔄 Registering Face ID...")
            wrapper.registerFaceID()
            print("✅ Face ID registration command sent!")
            return True
        except Exception as e:
            print(f"❌ Failed to register Face ID: {e}")
            return False
    
    def clear_face_ids():
        """Clear all Face IDs from the system"""
        try:
            print("🔄 Clearing Face IDs...")
            wrapper.clearFaceID()
            print("✅ Face ID clear command sent!")
            return True
        except Exception as e:
            print(f"❌ Failed to clear Face IDs: {e}")
            return False
    

    
    def run_face_id_mode():
        """Run the interactive Face ID registration mode"""
        while True:
            show_face_id_menu()
            
            try:
                print("\nEnter Face ID command: ", end="", flush=True)
                cmd = input().strip().lower()
                
                if cmd == 'r':
                    register_face_id()
                elif cmd == 'c':
                    clear_face_ids()
                elif cmd == 'b':
                    print("🔙 Returning to main menu...")
                    break
                elif cmd == '':
                    continue
                else:
                    print(f"❌ Unknown command: '{cmd}'")
                    print("Please use: 'r' (register), 'c' (clear), or 'b' (back)")
                    
            except KeyboardInterrupt:
                print("\n🔙 Returning to main menu...")
                break
            except EOFError:
                print("\n🔙 End of input detected, returning to main menu...")
                break
    
    def run_configuration_mode():
        """Run the interactive configuration mode"""
        while True:
            show_configuration_menu()
            
            try:
                print("\nEnter configuration command: ", end="", flush=True)
                cmd = input().strip().lower()
                
                if cmd == '1':
                    toggle_feature('face_detection')
                    apply_feature_configuration()
                elif cmd == '2':
                    toggle_feature('face_validation')
                    apply_feature_configuration()
                elif cmd == '3':
                    toggle_feature('person_detection')
                    apply_feature_configuration()
                elif cmd == '4':
                    toggle_feature('hand_landmarks')
                    apply_feature_configuration()
                elif cmd == '5':
                    toggle_feature('face_id')
                    apply_feature_configuration()
                elif cmd == '6':
                    toggle_feature('face_id_multi')
                    apply_feature_configuration()
                elif cmd == '7':
                    toggle_feature('object_detection')
                    apply_feature_configuration()
                elif cmd == 'a':
                    enable_all_features()
                    apply_feature_configuration()
                elif cmd == 'd':
                    disable_all_features()
                    apply_feature_configuration()
                elif cmd == 'r':
                    reset_to_defaults()
                    apply_feature_configuration()
                elif cmd == 's':
                    save_config_to_file()
                elif cmd == 'b':
                    print("🔙 Returning to main menu...")
                    break
                elif cmd == '':
                    continue
                else:
                    print(f"❌ Unknown command: '{cmd}'")
                    print("Please use valid configuration commands")
                    
            except KeyboardInterrupt:
                print("\n🔙 Returning to main menu...")
                break
            except EOFError:
                print("\n🔙 End of input detected, returning to main menu...")
                break
    
    def handle_ulp_command():
        """Handle ULP mode toggle - toggles between enabled and disabled based on current state"""
        # Check current ULP state
        current_state = wrapper.isUlpEnabled()
        
        # Toggle to opposite state
        if current_state:
            print("\n🔄 Disabling ULP mode...")
            result = wrapper.enableUlp(False)
            if "ULP Not available" in result:
                print("❌ ULP mode is not available (requires FPGA and metadata camera)")
            elif not wrapper.isUlpEnabled():
                print("✅ ULP mode disabled successfully")
            else:
                print(f"⚠️  ULP disable result: {result}")
        else:
            print("\n🔄 Enabling ULP mode...")
            result = wrapper.enableUlp(True)
            if "ULP Not available" in result:
                print("❌ ULP mode is not available (requires FPGA and metadata camera)")
            elif wrapper.isUlpEnabled():
                print("✅ ULP mode enabled successfully")
            else:
                print(f"⚠️  ULP enable result: {result}")
    
    # Main program loop
    try:
        while True:
            
            show_menu()
            
            # Show current status
            get_status_info()
            
            # Get user input
            try:
                # For cross-platform compatibility, use input() instead of getch()
                print("\nEnter command (c/m/i/s/f/u/x): ", end="", flush=True)
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
                
                elif command == 's':
                    print("\n⚙️  Entering configuration mode...")
                    run_configuration_mode()
                
                elif command == 'f':
                    print("\n👤 Entering Face ID registration mode...")
                    run_face_id_mode()
                
                elif command == 'u':
                    # Toggle ULP mode
                    handle_ulp_command()
                
                elif command == 'x':
                    print("\n👋 Exiting program...")
                    break
                
                elif command == '':
                    # Empty input, just continue
                    continue
                    
                else:
                    print(f"\n❌ Unknown command: '{command}'")
                    print("Please use: 'c' (capture), 'm' (metadata), 'i' (image), 's' (settings), 'f' (face ID), 'u' (toggle ULP mode), or 'x' (exit)")
                    
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
