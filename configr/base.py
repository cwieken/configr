"""
Configuration management base module.

This module provides a generic framework for loading, parsing, and validating
configuration files of different formats (JSON, YAML). It handles the conversion
of configuration data to strongly typed dataclass instances, with support for
nested dataclasses and complex type validation.

The module includes:
- ConfigBase class: The main class for loading and validating configuration
- Type validation utilities
- Support for different configuration file formats

Typical usage:
    @config_class(file_name="database")
    class DatabaseConfig:
        host: str
        port: int = 5432

    config = ConfigBase.load(DatabaseConfig)
"""
import dataclasses
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Generic, TypeVar, get_args, get_origin

from configr.exceptions import ConfigFileNotFoundError, ConfigLoadError
from configr.loaders.loader_base import ConfigLoader, FileConfigLoader
from configr.loaders.loader_dotenv import DotEnvConfigLoader
from configr.loaders.loader_env_var import EnvVarConfigLoader
from configr.loaders.loader_json import JSONConfigLoader
from configr.loaders.loader_yaml import YAMLConfigLoader

T = TypeVar('T')


class ConfigBase(Generic[T]):
    """
    Base class for configuration management.

    Handles loading configuration from files and conversion to dataclasses.
    """

    _loaders: list[type[ConfigLoader]] = [
        JSONConfigLoader,
        YAMLConfigLoader,
        DotEnvConfigLoader,
        EnvVarConfigLoader,
    ]

    @classmethod
    def set_config_dir(cls, config_dir: str | Path) -> None:
        """
        Set the directory where configuration files are stored.

        Args:
            config_dir (str | Path): The directory path for configuration files.
        """
        FileConfigLoader.set_config_dir(config_dir)

    @classmethod
    def get_available_loaders(cls) -> list[type[ConfigLoader]]:
        """
        Get available loaders for different file extensions.

        Returns:
            list[type[ConfigLoader]]: A list of available configuration loaders.
        """
        return cls._loaders

    @classmethod
    def get_available_file_loaders(cls) -> list[type[FileConfigLoader]]:
        """
        Get available file-based loaders for different file extensions.

        Returns:
            list[type[FileConfigLoader]]: A list of file-based configuration loaders.
        """
        return [loader for loader in cls._loaders
                if issubclass(loader, FileConfigLoader)]

    @classmethod
    def add_loader(cls, loader: type[ConfigLoader]) -> None:
        """
        Add a loader for a specific file extension.

        Args:
            loader (type[ConfigLoader]): The loader to add.
        """
        if loader not in cls._loaders:
            cls._loaders.append(loader)

    @classmethod
    def remove_loader(cls, loader: type[ConfigLoader]) -> None:
        """
        Remove a specific loader.

        Args:
            loader (type[ConfigLoader]): The loader to remove.
        """
        if loader in cls._loaders:
            cls._loaders.remove(loader)

    @classmethod
    def load(cls, config_class: type[T], config_data: dict | None = None) -> T:
        """
        Load configuration from file and convert to the specified dataclass.

        Args:
            config_class (type[T]): The dataclass to convert configuration to.
            config_data (dict | None): Optional dictionary with configuration
                                       data. If not provided, the configuration
                                       will be loaded from file.

        Returns:
            T: An instance of the specified dataclass with loaded configuration.

        Raises:
            TypeError: If `config_class` is not a dataclass.
            ConfigValidationError: If configuration validation fails.
        """
        # Ensure config_class is a dataclass
        if not dataclasses.is_dataclass(config_class):
            raise TypeError(f"{config_class.__name__} must be a dataclass")

        if config_data is None:
            config_data = cls.__load_config_data(config_class)

        # Extract field names and types from the dataclass
        fields = {f.name: f.type for f in dataclasses.fields(config_class)}
        filtered_data = cls.__filter_fields(fields, config_data)

        # Load config data recursively for nested dataclasses
        config_data = cls.__load_nested_dataclasses(fields, filtered_data)

        # Validate the types of the fields in the dataclass
        loader = cls._get_loader(config_class)
        loader.check_types(fields, filtered_data)

        # Create an instance of the dataclass and return it
        return config_class(**config_data)

    @classmethod
    def __filter_fields(cls, fields: dict[str, type],
                        raw_config_data: dict[str, Any]) -> dict[str, Any]:
        """
        Filter the data to include only the fields defined in the dataclass.

        This method takes a dictionary of field definitions and a dictionary
        of raw configuration data, and filters the configuration data to include
        only the keys that match the field names in the dataclass.

        Args:
            fields (dict[str, type]): A dictionary mapping field names to
                                      their types, extracted from the
                                      dataclass.
            raw_config_data (dict[str, Any]): A dictionary containing the
                                              raw configuration data to be
                                              filtered.

        Returns:
            dict[str, Any]: A dictionary containing only the key-value pairs from
                            `raw_config_data` that match the field names in `fields`.
        """
        # Get the set of field names
        field_names = fields.keys()

        # Filter the configuration data to include only keys that match field names
        # and return the field definitions and the filtered data
        return {k: v for k, v in raw_config_data.items() if k in field_names}

    @classmethod
    def __load_config_data(cls, config_class: type[T]) -> dict:
        """
        Load configuration data from file or loader and return as a dictionary.

        Args:
            config_class: The dataclass type for which to load configuration data.

        Returns:
            dict: The loaded configuration data.
        """
        loader = cls._get_loader(config_class)
        name = loader.get_config_name(config_class)
        config_data = loader.load(name, config_class)

        if not config_data:
            raise ConfigLoadError(f"Failed to load configuration for {name} "
                                  f"using {loader.__name__}")

        return config_data

    @classmethod
    def __load_nested_dataclasses(cls, fields: dict[str, type], data: dict) -> dict:
        """
        Recursively load nested dataclasses.

        Args:
            fields (dict[str, type]): A dictionary mapping field names to their types.
            data (dict): The configuration data to process.

        Returns:
            dict: The processed configuration data with nested dataclasses loaded.
        """
        for key, value in data.items():
            field_type = fields[key]
            if get_origin(field_type) is not None:
                if any(dataclasses.is_dataclass(arg) for arg in get_args(field_type)):
                    field_type = next(arg for arg in get_args(field_type))
            if dataclasses.is_dataclass(field_type):
                if isinstance(value, dict):
                    data[key] = cls.load(field_type, value)
                elif value is None:
                    # Try to create a new (empty) instance of nested dataclass
                    # if value is None.
                    # This only works if the nested dataclass has no required arguments,
                    # otherwise the value will remain None
                    try:
                        data[key] = field_type()
                    except TypeError:
                        pass
            elif isinstance(value, Iterable):
                origin_types = get_args(field_type)
                if origin_types and dataclasses.is_dataclass(origin_types[0]):
                    for i, value_elem in enumerate(value):
                        if isinstance(value_elem, dict):
                            value[i] = cls.load(origin_types[0], value_elem)
                    data[key] = value

        return data

    @classmethod
    def _get_loader(cls, config_class: type) -> type[ConfigLoader]:
        """
        Determine the appropriate loader for the given configuration class.

        Args:
            config_class (type): The configuration class for which to find a loader.

        Returns:
            type[ConfigLoader]: The loader for the configuration class.

        Raises:
            IndexError: If more than one non-file loader is found.
            ValueError: If no valid loader is found.
        """
        for loader in cls.get_available_file_loaders():
            if loader.config_file_exists(loader.get_config_file_name(config_class)):
                return loader

        # If file loader is expected but could not be found,
        # raise ConfigFileNotFoundError
        if len(Path(config_class._config_file_name).suffixes) >= 1:
            raise ConfigFileNotFoundError(
                f"Configuration file not found: {config_class._config_file_name}")

        # Return the first non-file loader if no file loader is found
        # and not extension is specified
        _non_file_loaders = [loader for loader in cls.get_available_loaders()
                             if loader not in cls.get_available_file_loaders()]

        if len(_non_file_loaders) > 1:
            raise IndexError(f"Found more than one non-file "
                             f"loader: {_non_file_loaders}")

        if len(_non_file_loaders) == 1:
            return _non_file_loaders[0]

        raise ValueError(f"No valid loader found for {config_class}")
