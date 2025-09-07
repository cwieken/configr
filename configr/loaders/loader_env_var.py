"""
Environment variable configuration loader.

This module provides functionality for loading configuration data from environment
variables. It automatically converts environment variable string values to appropriate
Python types based on the expected types defined in a dataclass.

The module includes:
- EnvVarConfigLoader class: Loads configuration from environment variables
  using prefix-based naming
- Type conversion utilities for string values to Python types (bool, int, float, etc.)

Environment variables are expected to follow the naming convention:
PREFIX_FIELD_NAME (e.g., DATABASE_HOST, DATABASE_PORT)

Example usage:
    @config_class(file_name="database")
    class DatabaseConfig:
        host: str
        port: int = 5432

    # Will look for environment variables like DATABASE_HOST, DATABASE_PORT
    config = ConfigBase.load(DatabaseConfig)
"""
import dataclasses
import os
from collections.abc import Iterable
from dataclasses import Field, is_dataclass
from types import UnionType
from typing import Any, Union, get_args, get_origin

from configr.loaders.loader_base import ConfigLoader
from configr.loaders.loader_yaml import T


class EnvVarConfigLoader(ConfigLoader):
    """
    Loader for environment variable-based configuration.

    This class provides functionality to load configuration data from
    environment variables and convert them to the appropriate types
    based on the fields defined in a dataclass.
    """

    @classmethod
    def __load_fields(cls, config_class: type[T]) -> tuple[Field[Any], ...]:
        """
        Load the fields of a dataclass.

        Args:
            config_class (type[T]): The dataclass type whose fields are to be loaded.

        Returns:
            tuple[Field[Any], ...]: A tuple containing the fields of the dataclass.

        Raises:
            TypeError: If the provided class is not a dataclass.
        """
        if not dataclasses.is_dataclass(config_class):
            raise TypeError("Config class must be a dataclass.")

        return dataclasses.fields(config_class)

    @classmethod
    def __convert_value(cls, value: str, key: str,
                        field_types: dict[str, type]) -> Any:
        """
        Convert a string value from an env variable to the appropriate type.

        Args:
            value (str): The string value from the environment variable.
            key (str): The key corresponding to the value.
            field_types (dict[str, type]): A dictionary mapping field names
                                           to their types.

        Returns:
            Any: The converted value with the appropriate type.
        """
        # Handle empty strings
        if value.strip() == "":
            return None

        # Keep original behavior: if field_types isn't iterable, wrap it (even though
        # the signature says dict[str, type]). This preserves existing semantics.
        if not isinstance(field_types, Iterable):
            field_types = [field_types]

        # If we have type information, use it for conversion
        if key in field_types:
            field_type = field_types[key]
            # Normalize Optional[T] / T | None to its base T
            field_type = cls._unwrap_optional(field_type)

            # Handle basic types (compare types with identity, not isinstance)
            if field_type is bool:
                return value.lower() in ('true', 'yes', 'y', '1')
            elif field_type is int:
                return int(value)
            elif field_type is float:
                return float(value)

        # Default string conversion logic (without type hints)
        # Try to convert to appropriate Python type
        low = value.lower()
        if low in ('true', 'yes', 'y', '1'):
            return True
        elif low in ('false', 'no', 'n', '0'):
            return False

        # Try to convert to number if it looks like one
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            # Return as string if no other conversion works
            return value

    @staticmethod
    def _unwrap_optional(t: type) -> type:
        """Return the base type if t is Optional, otherwise return t itself."""
        origin = get_origin(t)
        if origin in (Union, UnionType):
            args = get_args(t)
            if any(a is type(None) for a in args):
                non_none = [a for a in args if a is not type(None)]
                if len(non_none) == 1:
                    return non_none[0]
        return t

    @classmethod
    def load(cls, name: str | None, config_class: type[T]) -> dict[str, Any]:
        """
        Load configuration data from environment variables.

        Args:
            name (str): The prefix for environment variable names.
            config_class (type[T]): The dataclass type to load configuration for.

        Returns:
            dict[str, Any]: A dictionary containing the loaded configuration data.

        Raises:
            TypeError: If the provided class is not a dataclass.
        """
        if not dataclasses.is_dataclass(config_class):
            raise TypeError("Config class must be a dataclass.")

        config_data = {}
        for field in cls.__load_fields(config_class):
            if field.default is not dataclasses.MISSING:
                default_value = field.default
            else:
                default_value = None
            if name:
                env_var_name = f"{name.upper()}_{field.name.upper()}"
            else:
                env_var_name = field.name.upper()

            value = os.environ.get(env_var_name, default_value)
            key = field.name
            if value is not None and isinstance(value, str):
                config_data[key] = cls.__convert_value(value, key, field.type)
            if is_dataclass(field.type):
                # Recursively load nested dataclass fields
                nested_config = cls.load(f"{name}_{key}", field.type)
                config_data[key] = nested_config
            elif get_origin(field.type) is not None:
                if any(is_dataclass(arg) for arg in get_args(field.type)):
                    arg = next(arg for arg in get_args(field.type) if is_dataclass(arg))
                    # Recursively load nested dataclass fields
                    nested_config = cls.load(f"{name}_{key}", arg)
                    config_data[key] = nested_config

        return config_data if config_data else None
