import dataclasses
import os
from pathlib import Path
from typing import Type, TypeVar, Generic, ClassVar

from .exceptions import ConfigFileNotFoundError
from .loaders import ConfigLoader, JSONConfigLoader, YAMLConfigLoader

T = TypeVar('T')


class ConfigBase(Generic[T]):
    """
    Base class for configuration management.
    Handles loading configuration from files and conversion to dataclasses.
    """
    _config_dir: ClassVar[str] = os.environ.get('CONFIG_DIR', '_config')
    _loaders: ClassVar[dict[str, Type[ConfigLoader]]] = {
        '.json': JSONConfigLoader,
        '.yaml': YAMLConfigLoader,
        '.yml': YAMLConfigLoader
    }

    @classmethod
    def get_available_loaders(cls) -> dict[str, Type[ConfigLoader]]:
        return cls._loaders

    @classmethod
    def get_config_path(cls) -> Path:
        """Get the base configuration directory path."""
        return Path(cls._config_dir)

    @classmethod
    def load(cls: Type[T], config_class: Type) -> T:
        """
        Load configuration from file and convert to the specified dataclass.

        Args:
            config_class: The dataclass to convert configuration to

        Returns:
            An instance of the specified dataclass with loaded configuration
        """
        # Ensure config_class is a dataclass
        if not dataclasses.is_dataclass(config_class):
            raise TypeError(f"{config_class.__name__} must be a dataclass")

        file_name = cls._get_config_file_name(config_class)
        config_file_path = cls._get_config_file_path(file_name)
        loader = cls._get_loader(file_name)

        config_data = loader.load(config_file_path)

        # Convert to dataclass
        # Filter config_data to only include fields defined in the dataclass
        field_names = {f.name for f in dataclasses.fields(config_class)}
        filtered_data = {k: v for k, v in config_data.items() if k in field_names}

        # Create instance of the dataclass
        return config_class(**filtered_data)

    @classmethod
    def _get_loader(cls, file_name):
        """ Determine loader from file extension """
        ext = ''.join(Path(file_name).suffixes)

        if ext not in cls._loaders:
            raise ValueError(f"Unsupported file extension: {ext}. Supported: {list(cls._loaders.keys())}")

        return cls._loaders[ext]()

    @classmethod
    def _get_config_file_path(cls, file_name: str) -> Path:
        """ Get full path to config file """
        config_file_path = cls.get_config_path() / file_name

        if not config_file_path.exists():
            print(os.getcwd())
            raise ConfigFileNotFoundError(f"Configuration file not found: {config_file_path}")

        return config_file_path

    @classmethod
    def _get_config_file_name(cls, config_class: Type) -> str:
        """ Get file name from config class"""
        if hasattr(config_class, '_config_file_name'):
            file_name = config_class._config_file_name
        else:
            raise ValueError(f"{config_class.__name__} must have a _config_file_name attribute")
        return file_name
