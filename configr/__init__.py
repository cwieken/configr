"""
Configuration management system.

A flexible, type-safe configuration management system that loads structured
configuration data from files and converts it to strongly-typed Python objects.
The system supports multiple file formats, nested configuration structures,
and comprehensive type validation.

Features:
- Strong type validation using Python's type annotations
- Support for JSON and YAML configuration formats (extensible to other formats)
- Automatic conversion to dataclasses with full type checking
- Support for nested configuration structures
- Configurable file paths and naming conventions

Typical usage:
    from config_manager import ConfigBase, config_class

    @config_class(file_name="database")
    class DatabaseConfig:
        username: str
        password: str
        host: str
        port: int = 5432

    # Load configuration from file
    config = ConfigBase.load(DatabaseConfig)

    # Use strongly-typed configuration
    db_connection = connect(
        config.host,
        config.port,
        config.username,
        config.password
    )
"""
import sys

# Import the main classes and functions to expose them at the package level
from configr.base import ConfigBase
from configr.config_class import config_class
from configr.exceptions import ConfigFileNotFoundError, ConfigValidationError

# Define what should be accessible when someone does 'from configr import *'
__all__ = [
    'ConfigBase',
    'config_class',
    'ConfigFileNotFoundError',
    'ConfigValidationError',
]

if sys.version_info < (3, 10):
    raise RuntimeError("This package requires Python 3.10 or newer")
