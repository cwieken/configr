"""
Configuration loaders module.

This module provides various configuration loaders that handle loading configuration
data from different sources (files, environment variables, etc). Each loader implements
a common interface defined by the abstract ConfigLoader class.

The module includes:
- Base classes for configuration loaders
- Specialized loaders for specific file formats (JSON, YAML)
- Environment variable loader
- Utility functions for working with configuration files

Loaders are responsible for finding, reading, and parsing configuration sources,
but not for validation or conversion to dataclasses (which is handled by ConfigBase).
"""
import os
from abc import ABC, abstractmethod
from collections.abc import Generator
from pathlib import Path
from typing import Any, ClassVar, TypeVar

from configr.exceptions import ConfigFileNotFoundError, ConfigValidationError
from configr.field_type_checker import FieldTypeChecker

T = TypeVar('T')


class ConfigLoader(ABC):
    """
    Abstract base class for configuration loaders.

    Defines the common interface that all configuration loaders must implement.
    Configuration loaders are responsible for loading configuration data from
    various sources and returning it as a dictionary.
    """

    @classmethod
    @abstractmethod
    def load(cls, name: str, config_class: type[T]) -> dict[str, Any]:
        """
        Load configuration data for the specified configuration class.

        Args:
            name (str): The name or identifier of the configuration to load.
            config_class (type[T]): The dataclass type for which to load configuration.

        Returns:
            dict[str, Any]: The loaded configuration data as a dictionary.

        Raises:
            ConfigFileNotFoundError: If the configuration cannot be found.
            TypeError: If the config_class is not a dataclass.
        """
        pass

    @classmethod
    def check_types(cls, fields: dict[str, type], config_data: dict[str, Any]) -> None:
        """
        Check the types of configuration data against field definitions.

        Args:
            fields: Dictionary mapping field names to their types
            config_data: Configuration data to validate

        Raises:
            ConfigValidationError: If type validation fails
        """
        try:
            FieldTypeChecker.check_types(fields, config_data)
        except TypeError as exc:
            raise ConfigValidationError(
                f"Configuration validation failed: {exc}") from exc

    @classmethod
    def get_config_file_name(cls, config_class: type) -> str:
        """Get file name from config class."""
        if hasattr(config_class, '_config_file_name'):
            file_name = config_class._config_file_name
        else:
            raise ValueError(f"{config_class.__name__} must have a "
                             f"_config_file_name attribute")
        return file_name

    @classmethod
    def get_config_name(cls, config_class: type) -> str:
        """Get config name."""
        return cls.get_config_file_name(config_class)


class FileConfigLoader(ConfigLoader, ABC):
    """
    Abstract base class for file-based configuration loaders.

    Extends the ConfigLoader interface with file-specific functionality,
    providing common methods for locating and loading configuration files.
    File-based loaders support specific file extensions and search in a
    configurable directory.
    """
    _config_dir: ClassVar[str] = os.environ.get('CONFIG_DIR', '_config')
    ext: list[str]

    @classmethod
    def get_extensions(cls) -> list[str]:
        """Get the supported file extensions."""
        return cls.ext

    @classmethod
    def get_config_path(cls) -> Path:
        """Get the base configuration directory path."""
        return Path(cls._config_dir)

    @classmethod
    def set_config_dir(cls, config_dir: str | Path) -> None:
        """Set the base config directory path if default should not be used."""
        if isinstance(config_dir, Path):
            cls._config_dir = str(config_dir)
        else:
            cls._config_dir = config_dir

    @classmethod
    def _iter_config_file_paths(cls, name: str) -> Generator[Path, Any, None]:
        """Iterate over all possible configuration file paths."""
        file_name = name
        if Path(file_name).suffix in cls.get_extensions():
            yield cls.get_config_path() / file_name
            return
        for ext in cls.ext:
            yield cls.get_config_path() / f"{file_name}{ext}"

    @classmethod
    def _get_config_file_path(cls, name: str) -> Path:
        """Get full path to config file (first that exists)."""
        for config_file_path in cls._iter_config_file_paths(name):
            if config_file_path.exists():
                return config_file_path

        raise ConfigFileNotFoundError(
            f"No configuration file found for: '{name}' "
            f"with possible extensions: {cls.ext}")

    @classmethod
    def config_file_exists(cls, name: str) -> bool:
        """Check if config file exists."""
        for config_path in cls._iter_config_file_paths(name):
            if config_path.exists():
                return True

        return False
