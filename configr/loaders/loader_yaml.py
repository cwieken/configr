"""
YAML configuration loader.

This module provides functionality for loading configuration data from YAML files.
It handles finding, reading, and parsing YAML configuration files with appropriate
error handling.

The module includes:
- YAMLConfigLoader: A class for loading configuration from YAML files
  with .yaml and .yml extensions.
- Support for standard configuration directory structure.

YAML files are expected to contain valid YAML data that can be mapped to dataclass
fields. The file structure should match the structure of the target dataclass.

This module requires the PyYAML package to be installed. If not available, an
ImportError will be raised when attempting to load YAML files.

Example usage:
    @config_class(file_name="database.yaml")
    class DatabaseConfig:
        host: str
        port: int = 5432

    # Will load from _config/database.yaml
    config = ConfigBase.load(DatabaseConfig)
"""
from typing import Any, TypeVar

# Check if PyYAML is available
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from configr.loaders.loader_base import FileConfigLoader

T = TypeVar('T')


class YAMLConfigLoader(FileConfigLoader):
    """
    Loader for YAML configuration files.

    This class provides functionality to load configuration data from YAML files
    and map it to the fields of a dataclass. It supports files with `.yaml`
    and `.yml` extensions.
    """
    # Supported file extensions for YAML configuration files.
    ext: list[str] = ['.yaml', '.yml']

    @classmethod
    def load(cls, name: str, config_class: type[T] = None) -> dict[str, Any]:
        """
        Load YAML configuration from the specified path.

        Args:
            name (str): The name of the configuration file (without extension).
            config_class (type[T]): The dataclass type to map the configuration data to.

        Returns:
            dict[str, Any]: A dictionary containing the loaded configuration data.

        Raises:
            ImportError: If PyYAML is not installed.
            FileNotFoundError: If the specified configuration file does not exist.
            yaml.YAMLError: If the file contains invalid YAML.
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML support. "
                              "Install with 'pip install pyyaml'.")

        # Get the full path to the configuration file
        config_file_path = cls._get_config_file_path(name)
        with open(config_file_path) as f:
            # Load and parse the YAML file
            return yaml.safe_load(f)
