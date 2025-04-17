# Custom Loaders

Configr comes with built-in support for JSON and YAML configuration files, but you can extend it to support additional file formats by creating custom loaders.

## Built-in Loaders

Configr includes the following loaders by default:

- `JSONConfigLoader`: For `.json` files
- `YAMLConfigLoader`: For `.yaml` and `.yml` files (requires PyYAML)

These loaders are registered in the `ConfigBase._loaders` dictionary:

```python
_loaders: ClassVar[dict[str, Type[ConfigLoader]]] = {
    '.json': JSONConfigLoader,
    '.yaml': YAMLConfigLoader,
    '.yml': YAMLConfigLoader
}
```

## Creating a Custom Loader

To create a custom loader, you need to:

1. Create a subclass of `ConfigLoader`
2. Implement the `load` method
3. Register the loader with `ConfigBase.add_loader` method

### Step 1: Create a ConfigLoader Subclass

Create a class that inherits from `ConfigLoader` and implements the `load` method:

```python
from pathlib import Path
from typing import Dict, Any
from configr import ConfigLoader

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
```

### Step 2: Register the Loader

Register your loader with `ConfigBase.add_loader`:

```python
from configr import ConfigBase

# Register the TOML loader
ConfigBase.add_loader('.toml', TomlConfigLoader)
```

### Step 3: Use Your Custom Loader

Now you can use TOML files for your configuration:

```python
from configr import config_class, ConfigBase

@config_class(file_name="database.toml")
class DatabaseConfig:
    host: str = 'localhost'
    port: str = '5432'
    username: str = None
    password: str = None
    database: str = None
    
# This will use the TOMLConfigLoader to load database.toml
db_config = ConfigBase.load(DatabaseConfig)
```

## Example: INI Configuration Loader

Here's an example of a loader for INI files using Python's `configparser`:

```python
import configparser
from pathlib import Path

from configr import ConfigLoader


class INIConfigLoader(ConfigLoader):
    """Loader for INI configuration files."""

    def load(self, path: Path) -> dict[str, dict[str, any]]:
        config = configparser.ConfigParser(interpolation=None)
        config.read(path)
        return self.as_dict(config)

    @staticmethod
    def as_dict(config: configparser.ConfigParser):
        """
        Convert the parsed INI configuration to a nested dictionary.

        This method transforms the ConfigParser representation into a dictionary structure
        where each section becomes a top-level key containing a dictionary of its options.
        Default values are included at the top level of the resulting dictionary.

        Returns:
            dict[str, dict[str, any]]: A nested dictionary representation of the configuration.
                The outer dictionary keys are section names, and the inner dictionaries
                contain option name-value pairs for each section. Default values are included
                directly in the outer dictionary.
        """
        config_dict = {}

        for default_name, default_value in config.defaults().items():
            config_dict[default_name] = default_value

        for section in config.sections():
            config_dict[section] = {
                option: config.get(section, option) for option in config.options(section) if
                option not in config.defaults()
            }
        return config_dict
```

Then register it:

```python
ConfigBase.add_loader('.ini', INIConfigLoader)
```

And use it:

```python
@dataclass
class DatabaseConfig:
    host: str = 'localhost'
    port: str = '5432'
    username: str = None
    password: str = None
    database: str = None


@dataclass
class LoggingConfig:
    level: str
    file: str
    format: str


@config_class(file_name="app_config.ini")
class AppConfig:
    application: str
    database: DatabaseConfig
    logging: LoggingConfig

appConfig = ConfigBase.load(AppConfig)
```

Example INI file:

```ini
[DEFAULT]
application = MyApp

[database]
host = localhost
port = 5432
username = admin
password = secret
database = my_app

[logging]
level = INFO
file = app.log
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
```