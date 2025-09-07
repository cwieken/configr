"""
Configuration loaders module.

This module provides functionality for loading configuration data from various sources
including JSON files, YAML files, .env files, and environment variables. Each loader
automatically converts string values to appropriate Python types based on the expected
types defined in dataclasses.

Available loaders:
- JSONConfigLoader: Loads configuration from JSON files
- YAMLConfigLoader: Loads configuration from YAML files (requires PyYAML)
- DotEnvConfigLoader: Loads configuration from .env files (requires python-dotenv)
- EnvVarConfigLoader: Loads configuration from environment variables with
                      prefix-based naming

Example usage:
    @config_class(file_name="config.json")
    class AppConfig:
        host: str
        port: int = 8080

    config = ConfigBase.load(AppConfig)
"""

from configr.loaders.loader_base import ConfigLoader, FileConfigLoader
from configr.loaders.loader_dotenv import DotEnvConfigLoader
from configr.loaders.loader_env_var import EnvVarConfigLoader
from configr.loaders.loader_json import JSONConfigLoader
from configr.loaders.loader_yaml import YAMLConfigLoader

__all__ = [
    "ConfigLoader",
    "FileConfigLoader",
    "DotEnvConfigLoader",
    "EnvVarConfigLoader",
    "JSONConfigLoader",
    "YAMLConfigLoader",
]
