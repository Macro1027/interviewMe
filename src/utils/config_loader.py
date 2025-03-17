"""
Configuration Loader Module

This module provides utilities for loading and accessing configuration files.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)

class ConfigLoader:
    """
    Class for loading and accessing configuration files.
    
    Provides methods to load YAML and JSON configuration files and
    access configuration values.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_dir: Path to the configuration directory. If None,
                        uses the default 'config' directory.
        """
        if config_dir is None:
            # Get the project root directory
            project_root = Path(__file__).parent.parent.parent
            self.config_dir = project_root / 'config'
        else:
            self.config_dir = Path(config_dir)
        
        # Ensure the config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Config directory not found: {self.config_dir}. Using current directory.")
            self.config_dir = Path('.')
        
        logger.debug(f"Config directory: {self.config_dir}")
        
        # Cache for loaded configurations
        self._config_cache = {}
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load global settings from settings.yaml.
        
        Returns:
            Dictionary containing the settings.
        """
        return self._load_yaml('settings.yaml')
    
    def load_model_config(self) -> Dict[str, Any]:
        """
        Load model configuration from model_config.json.
        
        Returns:
            Dictionary containing the model configuration.
        """
        return self._load_json('model_config.json')
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file.
        
        Args:
            filename: Name of the YAML file to load.
            
        Returns:
            Dictionary containing the YAML configuration.
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist.
            yaml.YAMLError: If the YAML file is invalid.
        """
        if filename in self._config_cache:
            return self._config_cache[filename]
        
        file_path = self.config_dir / filename
        logger.debug(f"Loading YAML configuration: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
            
            self._config_cache[filename] = config
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {file_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in configuration file: {file_path}")
            logger.error(f"Error: {e}")
            raise
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """
        Load a JSON configuration file.
        
        Args:
            filename: Name of the JSON file to load.
            
        Returns:
            Dictionary containing the JSON configuration.
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist.
            json.JSONDecodeError: If the JSON file is invalid.
        """
        if filename in self._config_cache:
            return self._config_cache[filename]
        
        file_path = self.config_dir / filename
        logger.debug(f"Loading JSON configuration: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            self._config_cache[filename] = config
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {file_path}")
            logger.error(f"Error: {e}")
            raise
    
    def get_value(self, file_path: str, key_path: str, default: Any = None) -> Any:
        """
        Get a specific value from a configuration file using a key path.
        
        Args:
            file_path: Path to the configuration file.
            key_path: Path to the key, using dot notation (e.g., 'database.host').
            default: Default value to return if the key doesn't exist.
            
        Returns:
            The value for the specified key, or the default value if not found.
        """
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            config = self._load_yaml(file_path)
        elif file_path.endswith('.json'):
            config = self._load_json(file_path)
        else:
            logger.error(f"Unsupported configuration file type: {file_path}")
            return default
        
        # Navigate the dictionary using the key path
        keys = key_path.split('.')
        value = config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            logger.warning(f"Key not found in configuration: {key_path}")
            return default


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    config_loader = ConfigLoader()
    
    try:
        # Load settings
        settings = config_loader.load_settings()
        print("Settings:")
        print(f"  Environment: {settings.get('environment')}")
        print(f"  API Port: {settings.get('api', {}).get('port')}")
        
        # Load model configuration
        model_config = config_loader.load_model_config()
        print("\nModel Configuration:")
        
        nlp_model = model_config.get('models', {}).get('nlp', {}).get('transformer_model', {})
        print(f"  NLP Model: {nlp_model.get('name')}")
        
        # Get a specific value using key path
        api_port = config_loader.get_value('settings.yaml', 'api.port', 8080)
        print(f"\nAPI Port using get_value: {api_port}")
        
    except Exception as e:
        logger.error(f"Error loading configuration: {e}") 