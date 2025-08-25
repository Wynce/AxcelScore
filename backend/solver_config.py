#!/usr/bin/env python3
"""
solver_config.py - Configuration management for AI Solver System
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class SolverConfig:
    """Configuration management for AI Solver System"""
    
    DEFAULT_CONFIG = {
        "deepseek": {
            "api_key": "",
            "model": "deepseek-vl-7b-chat",
            "fallback_model": "deepseek-chat",
            "max_tokens": 2000,
            "temperature": 0.1
        },
        "claude": {
            "api_key": "",
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2000,
            "temperature": 0.1
        },
        "openai": {
            "api_key": "",
            "model": "gpt-4-vision-preview",
            "max_tokens": 2000,
            "temperature": 0.1
        },
        "gemini": {
            "api_key": "",
            "model": "gemini-pro-vision"
        },
        "paths": {
            "question_bank_base": "question_banks",
            "default_paper": "physics_2025_mar_13",
            "uploads_dir": "uploads"
        },
        "processing": {
            "max_concurrent": 3,
            "retry_attempts": 2,
            "timeout_seconds": 60
        },
        "validation": {
            "primary_model": "deepseek",
            "validation_model": "claude", 
            "confidence_threshold": 0.92,
            "claude_validation_threshold": 0.92,
            "high_confidence_threshold": 0.95,
            "manual_review_threshold": 0.92
        }
    }
    
    def __init__(self, config_file: str = "solver_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                return self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            except Exception as e:
                print(f"Error loading config file: {e}")
                print("Using default configuration")
        
        self.save_config(self.DEFAULT_CONFIG)
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'openai.api_key')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self.save_config()

    def update_api_key(self, service: str, api_key: str):
        """Helper method to update API keys"""
        if service.lower() in ['deepseek', 'openai', 'claude', 'gemini']:
            self.set(f"{service.lower()}.api_key", api_key)
            print(f"✅ Updated {service} API key")
        else:
            print(f"❌ Unknown service: {service}")
    
    def check_api_keys(self):
        """Check which API keys are configured"""
        keys_status = {}
        for service in ['deepseek', 'openai', 'claude', 'gemini']:
            api_key = self.get(f'{service}.api_key')
            keys_status[service] = bool(api_key and api_key.strip())
            status = "✅ Configured" if keys_status[service] else "❌ Not configured"
            print(f"{service.title()}: {status}")
        
        return keys_status

if __name__ == "__main__":
    # Test the configuration system
    config = SolverConfig()
    print("Configuration loaded successfully!")
    config.check_api_keys()