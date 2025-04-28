"""
Environment variable configuration loader.

This module provides functionality for loading configuration data from environment
variables. It automatically converts environment variable string values to appropriate
Python types based on the expected types defined in a dataclass.

The module includes:
- EnvVarConfigLoader: Loads configuration from environment variables with
  prefix-based naming
- Type conversion utilities for converting string values to appropriate
  Python types

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
# Check if PyYAML is available
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
