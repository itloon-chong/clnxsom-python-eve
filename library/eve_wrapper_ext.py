"""
Extended EVE Wrapper with additional functionality for FPGA state management.
This class inherits from the EVE library's EveWrapper without modifying the library itself.
"""

import sys
import os

# Add the library path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

from eve.eve_wrapper import EveWrapper
from eve.eve_python import eve_sdk as sdk


class EveWrapperExt(EveWrapper):
    """Extended EVE Wrapper with additional helper methods"""
    
    def getFpgaState(self):
        """
        Get the current FPGA state in a user-friendly format.
        Returns a dictionary mapping feature names to their enabled state and settings.
        """
        # Map pipeline types to feature names
        type_to_feature = {
            sdk.structs.pipeline_config_type_t.PT_FD: "face_detection",
            sdk.structs.pipeline_config_type_t.PT_LM_FV: "face_validation",
            sdk.structs.pipeline_config_type_t.PT_FID: "face_id",
            sdk.structs.pipeline_config_type_t.PT_PD: "person_detection",
            sdk.structs.pipeline_config_type_t.PT_HD: "hand_landmarks",
        }
        
        features_state = {}
        
        for pipeline_type, feature_name in type_to_feature.items():
            if pipeline_type in self._fpgaState:
                feature_settings = self._fpgaState[pipeline_type]
                enabled_value = feature_settings.get(sdk.structs.setting_type_t.CS_ENABLED, 0)
                features_state[feature_name] = {
                    "enabled": bool(enabled_value)
                }
                # Add IPS if available
                if sdk.structs.setting_type_t.CS_IPS in feature_settings:
                    features_state[feature_name]["max_ips"] = feature_settings[sdk.structs.setting_type_t.CS_IPS]
        
        return features_state
