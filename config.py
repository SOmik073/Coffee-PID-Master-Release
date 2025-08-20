"""
Configuration settings for Coffee PID Controller
"""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    'pid': {
        'kp': 2.0,
        'ki': 0.1,
        'kd': 0.05,
        'target_temp': 95.0,
        'min_temp': 0.0,
        'max_temp': 120.0
    },
    'system': {
        'control_interval': 0.1,
        'max_history_size': 1000,
        'database_path': 'coffee_pid.db'
    },
    'security': {
        'max_login_attempts': 3,
        'session_timeout': 3600
    }
}

class Config:
    def __init__(self, config_file: str = None):
        self.config = DEFAULT_CONFIG.copy()
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def load_config(self, config_file: str):
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                import json
                file_config = json.load(f)
                # FIXED: Implement deep merge to preserve nested configurations
                self._deep_merge(self.config, file_config)
        except Exception as e:
            print(f"Failed to load config: {e}")
    
    def _deep_merge(self, base_dict: Dict, update_dict: Dict):
        """Recursively merge nested dictionaries"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self, config_file: str):
        """Save configuration to file"""
        try:
            with open(config_file, 'w') as f:
                import json
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

# Global configuration instance
config = Config()