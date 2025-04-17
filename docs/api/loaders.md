# Loaders

The Configr library provides a flexible loading system for different configuration file formats. This page documents the loaders included with Configr and how to create custom loaders for additional file formats.

## Overview

Loaders in Configr:

1. Read configuration files in specific formats (JSON, YAML, etc.)
2. Parse those files into Python dictionaries
3. Allow the `ConfigBase` class to convert the dictionaries into typed dataclasses

## Base Class: ConfigLoader

All loaders in Configr inherit from the abstract base class `ConfigLoader`.

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class ConfigLoader(ABC):
    """Abstract base class for configuration loaders."""

    @abstractmethod
    def load(self, path: Path) -> Dict[str, Any]:
        """Load configuration from the specified path."""
        pass
```

## Built-in Loaders

### JSONConfigLoader

Loader for JSON configuration files.

```python
class JSONConfigLoader(ConfigLoader):
    """Loader for JSON configuration files."""

    def load(self, path: Path) -> Dict[str, Any]:
        """Load JSON configuration from the specified path."""
        with open(path, 'r') as f:
            return json.load(f)
```

Example JSON configuration file:

```json
{
  "host": "localhost",
  "port": 5432,
  "username": "admin",
  "password": "secure_password",
  "database": "my_app"
}
```

### YAMLConfigLoader

Loader for YAML configuration files. Requires PyYAML to be installed.

```python
class YAMLConfigLoader(ConfigLoader):
    """Loader for YAML configuration files."""

    def load(self, path: Path) -> Dict[str, Any]:
        """Load YAML configuration from the specified path."""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML support. Install with 'pip install pyyaml'.")

        with open(path, 'r') as f:
            return yaml.safe_load(f)
```

Example YAML configuration file:

```yaml
host: localhost
port: 5432
username: admin
password: secure_password
database: my_app
```

## Creating Custom Loaders

You can extend Configr with support for additional file formats by creating custom loaders.

### Example: TOMLConfigLoader

Here's an example of how to create a loader for TOML files:

```python
from pathlib import Path
from typing import Dict, Any
from configr import ConfigLoader, ConfigBase

class TOMLConfigLoader(ConfigLoader):
    """Loader for TOML configuration files."""

    def load(self, path: Path) -> Dict[str, Any]:
        """Load TOML configuration from the specified path."""
        try:
            import toml
        except ImportError:
            raise ImportError("The 'toml' package is required for TOML support. Install with 'pip install toml'.")
            
        with open(path, 'r') as f:
            return toml.load(f)

# Register the loader with Configr
ConfigBase.add_loader('.toml', TOMLConfigLoader)
```

Once registered, you can use TOML files with your configuration classes:

```python
from configr import config_class

@config_class(file_name="database.toml")
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str
```

Example TOML configuration file:

```toml
host = "localhost"
port = 5432
username = "admin"
password = "secure_password"
database = "my_app"
```

### Example: INIConfigLoader

Here's an example of a loader for INI files using Python's built-in `configparser`:

```python
import configparser
from pathlib import Path
from typing import Dict, Any
from configr import ConfigLoader, ConfigBase

class INIConfigLoader(ConfigLoader):
    """Loader for INI configuration files."""

    def load(self, path: Path) -> Dict[str, Dict[str, Any]]:
        """Load INI configuration from the specified path."""
        config = configparser.ConfigParser(interpolation=None)
        config.read(path)
        return self.as_dict(config)

    @staticmethod
    def as_dict(config: configparser.ConfigParser) -> Dict[str, Dict[str, Any]]:
        """Convert the parsed INI configuration to a nested dictionary."""
        config_dict = {}

        for default_name, default_value in config.defaults().items():
            config_dict[default_name] = default_value

        for section in config.sections():
            config_dict[section] = {
                option: config.get(section, option) for option in config.options(section) if
                option not in config.defaults()
            }
        return config_dict

# Register the loader with Configr
ConfigBase.add_loader('.ini', INIConfigLoader)
```

Example INI configuration file:

```ini
[DEFAULT]
application = MyApp

[database]
host = localhost
port = 5432
username = admin
password = secure_password
database = my_app

[logging]
level = INFO
file = app.log
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Managing Loaders

### Registering Custom Loaders

Register a custom loader with `ConfigBase.add_loader`:

```python
from configr import ConfigBase
from my_loaders import CustomLoader

ConfigBase.add_loader('.custom', CustomLoader)
```

### Removing Loaders

Remove a loader with `ConfigBase.remove_loader`:

```python
from configr import ConfigBase

ConfigBase.remove_loader('.yaml')
```

### Getting Available Loaders

Get all available loaders with `ConfigBase.get_available_loaders`:

```python
from configr import ConfigBase

loaders = ConfigBase.get_available_loaders()
print(loaders)  # {'.json': JSONConfigLoader, '.yaml': YAMLConfigLoader, ...}
```

## Loader Selection

When loading a configuration, Configr selects the appropriate loader based on the file extension:

1. If the configuration class has a `_config_file_name` with an extension (e.g., "database.json"), Configr uses the loader for that extension.
2. If the extension is missing, Configr tries each registered loader in order until it finds a matching file.
3. If no matching file is found, a `ConfigFileNotFoundError` is raised.

## Best Practices for Custom Loaders

1. **Error Handling**: Include clear error messages for missing dependencies or file format issues.
2. **Dependencies**: Document any external dependencies required by your loader.
3. **Type Conversion**: Ensure your loader returns data as expected by Configr (dictionaries with the correct types).
4. **File Extension**: Use a unique file extension for your format to avoid conflicts.

## Example Usage

```python
from configr import config_class, ConfigBase
from my_loaders import XML_ConfigLoader

# Register custom XML loader
ConfigBase.add_loader('.xml', XML_ConfigLoader)

@config_class(file_name="database.xml")
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str

# Load from XML file
db_config = ConfigBase.load(DatabaseConfig)
```