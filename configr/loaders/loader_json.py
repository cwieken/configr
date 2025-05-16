"""
JSON configuration loader.

This module provides functionality for loading configuration data from JSON files.
It handles finding, reading, and parsing JSON configuration files with appropriate
error handling.

The module includes:
- JSONConfigLoader: A class for loading configuration from JSON files with
  a .json extension.
- Support for standard configuration directory structure.

JSON files are expected to contain valid JSON data that can be mapped to dataclass
fields. The file structure should match the structure of the target dataclass.

Example usage:
    @config_class(file_name="database.json")
    class DatabaseConfig:
        host: str
        port: int = 5432

    # Will load from _config/database.json
    config = ConfigBase.load(DatabaseConfig)
"""

import json
from typing import Any

from configr.loaders.loader_base import FileConfigLoader
from configr.loaders.loader_yaml import T


class JSONConfigLoader(FileConfigLoader):
    """
    Loader for JSON configuration files.

    This class provides functionality to load configuration data from JSON files
    and map it to the fields of a dataclass.
    """
    # Supported file extensions for JSON configuration files.
    ext: list[str] = ['.json']

    @classmethod
    def load(cls, name: str, config_class: type[T] = None) -> dict[str, Any]:
        """
        Load JSON configuration from the specified path.

        Args:
            name (str): The name of the configuration file (without extension).
            config_class (type[T]): The dataclass type to map the configuration data to.

        Returns:
            dict[str, Any]: A dictionary containing the loaded configuration data.

        Raises:
            FileNotFoundError: If the specified configuration file
                               does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        # Get the full path to the config file.
        config_file_path = cls._get_config_file_path(name)
        with open(config_file_path) as f:
            return json.load(f)  # Load and parse the JSON file.
