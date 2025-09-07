# ConfigBase

`ConfigBase` is the core class of the Configr library that handles loading configuration from files and converting it to
dataclasses.

## Overview

`ConfigBase` provides a robust mechanism for loading and validating configuration data from various file formats (JSON,
YAML, etc.) and converting it to strongly-typed Python dataclasses. It supports nested dataclass structures and provides
a flexible, extensible interface for adding custom loaders.

## Class Definition

```python
class ConfigBase(Generic[T]):
    """
    Base class for configuration management.
    Handles loading configuration from files and conversion to dataclasses.
    """
```

## Class Variables

| Variable   | Type                       | Description                                     |
|------------|----------------------------|-------------------------------------------------|
| `_loaders` | `list[type[ConfigLoader]]` | List of available configuration loader classes. |

## Methods

### `set_config_dir`

Set the directory where configuration files are stored.

```python
@classmethod
def set_config_dir(cls, config_dir: str | Path) -> None:
```

#### Parameters

- `config_dir`: A string or Path object representing the directory where configuration files are stored.

#### Example

```python
from configr import ConfigBase

# Set the configuration directory
ConfigBase.set_config_dir("configs")

# Or using a Path object
from pathlib import Path

ConfigBase.set_config_dir(Path("configs"))
```

### `get_available_loaders`

Get all available configuration loader classes.

```python
@classmethod
def get_available_loaders(cls) -> list[type[ConfigLoader]]:
```

#### Returns

A list of available configuration loader classes.

#### Example

```python
from configr import ConfigBase

# Get all available loaders
loaders = ConfigBase.get_available_loaders()
print(loaders)  # [JSONConfigLoader, YAMLConfigLoader, DotEnvConfigLoader, EnvVarConfigLoader]
```

### `get_available_file_loaders`

Get all available file-based configuration loader classes.

```python
@classmethod
def get_available_file_loaders(cls) -> list[type[FileConfigLoader]]:
```

#### Returns

A list of available file-based configuration loader classes.

#### Example

```python
from configr import ConfigBase

# Get all available file loaders
file_loaders = ConfigBase.get_available_file_loaders()
print(file_loaders)  # [JSONConfigLoader, YAMLConfigLoader, DotEnvConfigLoader]
```

### `add_loader`

Add another loader

```python
@classmethod
def add_loader(cls, loader: type[ConfigLoader]) -> None:
```

#### Parameters

- `loader`: The loader class to add.

#### Example

```python
from configr import ConfigBase, FileConfigLoader
from typing import Any, TypeVar

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


# Register the TOML loader
ConfigBase.add_loader(TOMLConfigLoader)
```

### `remove_loader`

Remove a specific loader.

```python
@classmethod
def remove_loader(cls, loader: type[ConfigLoader]) -> None:
```

#### Parameters

- `loader`: The loader to remove.

#### Example

```python
from configr import ConfigBase
from configr.loaders.loader_yaml import YAMLConfigLoader

# Remove the YAML loader
ConfigBase.remove_loader(YAMLConfigLoader)
```

### `load`

Load configuration from file and convert it to the specified dataclass.

```python
@classmethod
def load(cls, config_class: type[T], config_data: dict | None = None) -> T:
```

#### Parameters

- `config_class`: The dataclass to convert configuration to.
- `config_data`: Optional dictionary containing configuration data. If not provided, it will be loaded from the file.

#### Returns

An instance of the specified dataclass with loaded configuration.

#### Raises

- `TypeError`: If `config_class` is not a dataclass.
- `ConfigFileNotFoundError`: If the configuration file is not found.
- `ConfigValidationError`: If the configuration fails validation.
- `ConfigLoadError`: If the configuration loading fails.

#### Example

```python
from configr import ConfigBase, config_class


@config_class
class DatabaseConfig:
    username: str
    password: str
    database: str
    host: str = "localhost"
    port: int = 5432


# Load configuration from file
db_config = ConfigBase.load(DatabaseConfig)

# Or with explicit configuration data
config_data = {
    "host": "db.example.com",
    "port": 5432,
    "username": "admin",
    "password": "secure_password",
    "database": "my_app"
}
db_config = ConfigBase.load(DatabaseConfig, config_data)
```

## Private Methods

These methods are intended for internal use by the ConfigBase class:

### `__load_config_data`

Load configuration data from file or loader and return as a dictionary.

```python
@classmethod
def __load_config_data(cls, config_class: type[T]) -> dict:
```

### `__filter_fields`

Filter the data to include only the fields defined in the dataclass.

```python
@classmethod
def __filter_fields(cls, fields: dict[str, type], raw_config_data: dict[str, Any]) -> dict[str, Any]:
```

### `__load_nested_dataclasses`

Recursively load nested dataclasses.

```python
@classmethod
def __load_nested_dataclasses(cls, fields: dict[str, type], data: dict) -> dict:
```

### `_get_loader`

Determine the appropriate loader for the given configuration class.

```python
@classmethod
def _get_loader(cls, config_class: type) -> type[ConfigLoader]:
```



## Implementation Details

The `ConfigBase` class:

1. Determines the appropriate file to load based on the configuration class
2. Tries to find the file with different supported extensions from available loaders
3. Uses the appropriate loader to parse the file into a dictionary
4. Filters the data to include only fields defined in the dataclass
5. Handles nested dataclass structures recursively
6. Performs type validation using `FieldTypeChecker`
7. Creates and returns an instance of the specified dataclass with the loaded configuration data

## Example Usage

```python
from configr import ConfigBase, config_class
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    username: str
    password: str
    name: str
    host: str = "localhost"
    port: int = 5432


@config_class(file_name="app.yaml")
class AppConfig:
    debug: bool = False
    log_level: str = "INFO"
    database: DatabaseConfig = None  # Nested configuration


# Set custom configuration directory
ConfigBase.set_config_dir("my_configs")

# Load configurations
app_config = ConfigBase.load(AppConfig)

# Use the loaded configuration
print(f"Debug mode: {app_config.debug}, Log level: {app_config.log_level}")
if app_config.database:
    print(f"Connecting to {app_config.database.name} at {app_config.database.host}:{app_config.database.port}")
```