"""
.env file configuration loader.

This module provides functionality for loading configuration data from .env files.
It handles finding, reading, and parsing .env files with appropriate error handling
and type conversion.

The module includes:
- DotEnvConfigLoader: A class for loading configuration from .env files.
- Integration with environment variable processing for type conversion.
- Support for standard configuration directory structure.

.env files are expected to contain key-value pairs in the format KEY=value.
The loader uses the environment variable processing logic to handle type conversion
and nested dataclass structures.

This module requires the python-dotenv package to be installed. If not available, an
ImportError will be raised when attempting to load .env files.

Example usage:
    @config_class(file_name="database")
    class DatabaseConfig:
        host: str
        port: int = 5432

    # Will load from _config/.env with variables like DATABASE_HOST, DATABASE_PORT
    config = ConfigBase.load(DatabaseConfig)
"""

import os
from pathlib import Path
from typing import Any, TypeVar

from configr.utils import to_snake_case

# Check if python-dotenv is available
try:
    from dotenv import dotenv_values

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

from configr.loaders.loader_base import FileConfigLoader
from configr.loaders.loader_env_var import EnvVarConfigLoader

T = TypeVar("T")


class DotEnvConfigLoader(FileConfigLoader):
    """
    Loader for .env configuration files.

    This class provides functionality to load configuration data from .env files
    and map it to the fields of a dataclass. It leverages the environment variable
    processing logic for type conversion and nested structure handling.
    """

    # Supported file extensions for .env configuration files.
    ext: list[str] = [".env"]

    @classmethod
    def load(cls, name: str, config_class: type[T]) -> dict[str, Any]:
        """
        Load .env configuration from the specified path.

        Args:
            name (str): The prefix for environment variable names
                        (used for variable naming).
            config_class (type[T]): The dataclass type to map the configuration data to.

        Returns:
            dict[str, Any]: A dictionary containing the loaded configuration data.

        Raises:
            ImportError: If python-dotenv is not installed.
            FileNotFoundError: If the .env file does not exist in the config directory.
        """
        if not DOTENV_AVAILABLE:
            raise ImportError(
                "python-dotenv is required for .env support. "
                "Install with 'pip install python-dotenv'."
            )

        # Always use .env as the filename
        config_file_path = cls.get_config_path() / ".env"

        if not config_file_path.exists():
            raise FileNotFoundError(f"No .env file found at: {config_file_path}")

        # Load the .env file values
        env_values = dotenv_values(config_file_path)

        # Temporarily update environment variables and use EnvVarConfigLoader
        original_env = os.environ.copy()
        try:
            # Update environment with .env values
            os.environ.update(env_values)

            # Use EnvVarConfigLoader to handle type conversion and nested structures
            # The 'name' parameter is used as the prefix for env variables
            return EnvVarConfigLoader.load(name, config_class)
        finally:
            # Restore original environment variables
            os.environ.clear()
            os.environ.update(original_env)

    @classmethod
    def config_file_exists(cls, name: str) -> bool:
        """
        Check if .env file exists in the config directory.

        Args:
            name (str): The configuration name (not used for .env files).

        Returns:
            bool: True if .env file exists, False otherwise.
        """
        return (cls.get_config_path() / ".env").exists()

    @classmethod
    def _get_config_file_path(cls, name: str) -> Path:
        """
        Get path to .env file (always returns .env regardless of name).

        Args:
            name (str): The configuration name (not used for .env files).

        Returns:
            Path: The path to the .env file.

        Raises:
            FileNotFoundError: If the .env file does not exist.
        """
        config_file_path = cls.get_config_path() / ".env"
        if not config_file_path.exists():
            raise FileNotFoundError(f"No .env file found at: {config_file_path}")
        return config_file_path

    @classmethod
    def get_config_name(cls, config_class: type) -> str:
        """
        Get config name from the dataclass name.

        Args:
            config_class (type): The dataclass type to extract the name from.

        Returns:
            str: The configuration name in uppercase, derived from the class name.
        """
        name = to_snake_case(config_class.__name__).replace("_config", "")
        return name.upper()
