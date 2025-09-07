# Custom Loaders

Configr comes with built-in support for JSON and YAML configuration files, but you can extend it to support additional
file formats by creating custom loaders.

## Built-in Loaders

Configr includes the following loaders by default:

- `JSONConfigLoader`: For `.json` files
- `YAMLConfigLoader`: For `.yaml` and `.yml` files (requires PyYAML)
- `DotEnvConfigLoader`: For `.env` files (requires python-dotenv)
- `EnvVarConfigLoader`: For loading configuration from environment variables

These loaders are registered in the `ConfigBase._loaders` list:

```python
_loaders: list[type[ConfigLoader]] = [
    JSONConfigLoader,
    YAMLConfigLoader,
    DotEnvConfigLoader,
    EnvVarConfigLoader
]
```

## Creating a Custom Loader

To create a custom loader, you need to:

1. Create a subclass of `FileConfigLoader`
2. Implement the `load` method and define extensions
3. Register the loader with `ConfigBase.add_loader` method

### Step 1: Create a FileConfigLoader Subclass

Create a class that inherits from `FileConfigLoader` and implements the `load` method:

```python
from typing import Any, TypeVar
from configr.loaders.loader_base import FileConfigLoader

T = TypeVar('T')


class TOMLConfigLoader(FileConfigLoader):
    """Loader for TOML configuration files."""
    ext: list[str] = ['.toml']  # Supported file extensions

    @classmethod
    def load(cls, name: str, config_class: type[T] = None) -> dict[str, Any]:
        """Load TOML configuration from the specified path."""
        try:
            import toml
        except ImportError:
            raise ImportError("The 'toml' package is required for TOML support. Install with 'pip install toml'.")

        config_file_path = cls._get_config_file_path(name)
        with open(config_file_path) as f:
            return toml.load(f)
```

### Step 2: Register the Loader

Register your loader with `ConfigBase.add_loader`:

```python
from configr import ConfigBase

# Register the TOML loader
ConfigBase.add_loader(TOMLConfigLoader)
```

### Step 3: Use Your Custom Loader

Now you can use TOML files for your configuration:

```python
from configr import config_class, ConfigBase


@config_class(file_name="database.toml")
class DatabaseConfig:
    host: str = 'localhost'
    port: int = 5432
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
from typing import Any, TypeVar

from configr.loaders.loader_base import FileConfigLoader

T = TypeVar('T')


class INIConfigLoader(FileConfigLoader):
    """Loader for INI configuration files."""
    ext: list[str] = ['.ini']  # Supported file extensions

    @classmethod
    def load(cls, name: str, config_class: type[T] = None) -> dict[str, Any]:
        """Load INI configuration from the specified path."""
        config_file_path = cls._get_config_file_path(name)

        config = configparser.ConfigParser(interpolation=None)
        config.read(config_file_path)
        return cls.as_dict(config)

    @staticmethod
    def as_dict(config: configparser.ConfigParser) -> dict[str, Any]:
        """
        Convert the parsed INI configuration to a nested dictionary.
  
        This method transforms the ConfigParser representation into a dictionary structure
        where each section becomes a top-level key containing a dictionary of its options.
        Default values are included at the top level of the resulting dictionary.
  
        Returns:
            dict[str, Any]: A nested dictionary representation of the configuration.
                The outer dictionary keys are section names, and the inner dictionaries
                contain option name-value pairs for each section. Default values are included
                directly in the outer dictionary.
        """
        config_dict = {}

        for default_name, default_value in config.defaults().items():
            config_dict[default_name] = default_value

        for section in config.sections():
            config_dict[section] = {
                option: config.get(section, option)
                for option in config.options(section)
                if option not in config.defaults()
            }
        return config_dict
```

Then register it:

```python
from configr import ConfigBase

ConfigBase.add_loader(INIConfigLoader)
```

And use it:

```python
from dataclasses import dataclass
from configr import config_class, ConfigBase


@dataclass
class DatabaseConfig:
    host: str = 'localhost'
    port: str = '5432'
    username: str = None
    password: str = None
    database: str = None


@dataclass
class LoggingConfig:
    level: str = None
    file: str = None
    format: str = None


@config_class(file_name="app_config.ini")
class AppConfig:
    application: str = None
    database: DatabaseConfig = None
    logging: LoggingConfig = None


app_config = ConfigBase.load(AppConfig)
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

## Understanding the Loader System

Configr's loader system is built around the following classes:

1. `ConfigLoader` - Abstract base class that defines the interface all loaders must implement
2. `FileConfigLoader` - Base class for file-based loaders that adds functionality for finding and loading configuration
   files.

The `ConfigBase` class maintains a list of available loaders and selects the appropriate one based on the configuration
class's file name or extension.

## Available Loader Types

In Configr, you can create two types of loaders:

1. **File Loaders**: These loaders extend `FileConfigLoader` and handle loading configuration from files with specific
   extensions.

2. **Non-File Loaders**: These loaders extend the base `ConfigLoader` class directly and can load configuration from
   non-file sources, e.g. environment variables.

## Loading Process

When you call `ConfigBase.load(MyConfig)`, Configr:

1. Checks if a data dictionary is provided (for in-memory configuration)
2. If not, it determines which loader to use based on the configuration class's file name
3. The appropriate loader loads the configuration data
4. The data is filtered to include only fields defined in the dataclass
5. Nested dataclasses are recursively loaded
6. Type validation is performed on all fields
7. The dataclass instance is created and returned

## Best Practices for Custom Loaders

1. **Proper Error Handling**: Provide clear error messages when configurations cannot be loaded
2. **Type Conversion**: Handle type conversion appropriately in your loader
3. **Validation**: Consider adding validation specific to your configuration format
4. **Documentation**: Document any special requirements or behavior of your loader
5. **Testing**: Thoroughly test your loader with various configuration scenarios