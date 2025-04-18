"""
Configuration file loaders module.

This module provides a set of loaders for different configuration file formats,
allowing the configuration system to handle various file types. It implements
an extensible loader system through a common interface.

The module includes:
- ConfigLoader abstract base class: Defines the interface for all loaders
- JSONConfigLoader: Loader for JSON configuration files
- YAMLConfigLoader: Loader for YAML configuration files (requires PyYAML)

Typical usage:
    # Loading a JSON configuration file
    loader = JSONConfigLoader()
    config_data = loader.load(Path("config.json"))

    # Adding support for a new format
    class XMLConfigLoader(ConfigLoader):
        def load(self, path: Path) -> dict[str, Any]:
            # XML loading implementation
            ...

    ConfigBase.add_loader(".xml", XMLConfigLoader)
"""
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigLoader(ABC):
    """Abstract base class for configuration loaders."""

    @abstractmethod
    def load(self, path: Path) -> dict[str, Any]:
        """Load configuration from the specified path."""
        pass


class JSONConfigLoader(ConfigLoader):
    """Loader for JSON configuration files."""

    def load(self, path: Path) -> dict[str, Any]:
        """Load JSON configuration from the specified path."""
        with open(path) as f:
            return json.load(f)


class YAMLConfigLoader(ConfigLoader):
    """Loader for YAML configuration files."""

    def load(self, path: Path) -> dict[str, Any]:
        """Load YAML configuration from the specified path."""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML support. "
                              "Install with 'pip install pyyaml'.")

        with open(path) as f:
            return yaml.safe_load(f)
