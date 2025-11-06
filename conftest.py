#!/usr/bin/env python3

"""
Pytest configuration and fixtures for EVE SDK and I2C communication testing.
"""

import pytest
import yaml
import os
import sys
from pathlib import Path

# Add the library path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

from eve.eve_wrapper import EveWrapper

@pytest.fixture(scope="session")
def config():
    """Load configuration from config.yaml"""
    with open("config.yaml") as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def eve_wrapper(config):
    """
    Pytest fixture to create and initialize EveWrapper instance.
    """
    # Get I2C config from YAML
    i2c_config = config.get('i2c', {})
    
    # Get EVE config from YAML
    eve_config = config.get('eve', {})
    
    wrapper = EveWrapper(
        comport=eve_config.get('comport', 0),
        i2cAdapter=i2c_config.get('bus', 0),
        i2cDevice=i2c_config.get('device_address', 0x30),
        i2cIRQ=i2c_config.get('irq_pin', 26),
        pipelineVersion=eve_config.get('pipeline_version', 0),
        evePath=eve_config.get('eve_path', '/opt/EVE-6.6.0-Source/bin'),
        toJpg=eve_config.get('to_jpg', True),
        copyImage=eve_config.get('copy_image', False),
        maxWidth=eve_config.get('max_width', 800),
        driverPath=eve_config.get('driver_path', '/home/lattice/mY_Work/eve-cam/clnx_camDrvEn')
    )
    
    # Initialize the wrapper
    wrapper.init(useMetadataCamera=True)
    
    yield wrapper
    
    # Cleanup
    try:
        wrapper.stop()
    except Exception as e:
        print(f"Warning: Error during wrapper cleanup: {e}")

@pytest.fixture
def features_config():
    """
    Pytest fixture for EVE features configuration.
    """
    return {
        "face_detection": {"enabled": True},
        "person_detection": {"enabled": True},
        "hand_landmarks": {"enabled": True},
        "face_id": {"enabled": False},
        "object_detection": {"enabled": False}
    }

# Test discovery functions for pytest
def pytest_runtest_setup(item):
    """
    Setup function called before each test.
    """
    print(f"\n🔧 Setting up test: {item.name}")

def pytest_runtest_teardown(item):
    """
    Teardown function called after each test.
    """
    print(f"🧹 Cleaning up test: {item.name}")
