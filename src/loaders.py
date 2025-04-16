import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigLoader(ABC):
    """Abstract base class for configuration loaders."""

    @abstractmethod
    def load(self, path: Path) -> Dict[str, Any]:
        """Load configuration from the specified path."""
        pass


class JSONConfigLoader(ConfigLoader):
    """Loader for JSON configuration files."""

    def load(self, path: Path) -> Dict[str, Any]:
        """Load JSON configuration from the specified path."""
        with open(path, 'r') as f:
            return json.load(f)


class YAMLConfigLoader(ConfigLoader):
    """Loader for YAML configuration files."""

    def load(self, path: Path) -> Dict[str, Any]:
        """Load YAML configuration from the specified path."""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML support. Install with 'pip install pyyaml'.")

        with open(path, 'r') as f:
            return yaml.safe_load(f)