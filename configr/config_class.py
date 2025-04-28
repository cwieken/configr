"""
Configuration class decorator module.

This module provides a decorator for creating configuration classes that can be
automatically loaded by the ConfigBase class. The decorator handles both marking
the class as a dataclass and setting the configuration file name.

The module includes:
- config_class decorator: Marks a class as a configuration class and sets the
  configuration file name, either explicitly or derived from the class name

Typical usage:
    @config_class(file_name="database.json")
    class DatabaseConfig:
        host: str
        port: int = 5432

    # or with default filename (database_config)
    @config_class
    class DatabaseConfig:
        host: str
        port: int = 5432
"""
import dataclasses

from configr.utils import to_snake_case


def config_class(cls=None, *, file_name: str = None):
    """
    Decorator to mark a class as a configuration class.

    This allows specifying a custom file name for the configuration.

    Usage:
        @config_class(file_name="database.json")
        class DatabaseConfig:
            host: str
            port: int = 5432
    """

    def wrapper(cls):
        # Mark as dataclass if not already, that way @dataclass does not need to be used
        if not dataclasses.is_dataclass(cls):
            cls = dataclasses.dataclass(cls)

        # Add file_name as a class variable
        if file_name is not None:
            cls._config_file_name = file_name

        elif not hasattr(cls, '_config_file_name'):
            # Default to class name in snake_case
            cls._config_file_name = to_snake_case(cls.__name__)

        return cls

    # Handle both @config_class and @config_class(file_name="...")
    if cls is None:
        return wrapper
    return wrapper(cls)
