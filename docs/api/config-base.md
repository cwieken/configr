# ConfigBase

`ConfigBase` is the core class of the Configr library that handles loading configuration from files and converting it to dataclasses.

## Overview

`ConfigBase` provides a robust mechanism for loading and validating configuration data from various file formats (JSON, YAML, etc.) and converting it to strongly-typed Python dataclasses. It supports nested dataclass structures and provides a flexible, extensible interface for adding custom loaders.

## Class Definition

```python
class ConfigBase(Generic[T]):
    """
    Base class for configuration management.
    Handles loading configuration from files and conversion to dataclasses.
    """
```

## Class Variables

| Variable      | Type                                 | Description                                  |
|---------------|--------------------------------------|----------------------------------------------|
| `_config_dir` | `ClassVar[str]`                     | Directory path where configuration files are stored. Defaults to environment variable `CONFIG_DIR` or `_config` if not set. |
| `_loaders`    | `ClassVar[dict[str, Type[ConfigLoader]]]` | Dictionary mapping file extensions to their loader classes. |

## Methods

### `set_config_dir`

Set the base configuration directory path.

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

Get the dictionary of available configuration loaders.

```python
@classmethod
def get_available_loaders(cls) -> dict[str, Type[ConfigLoader]]:
```

#### Returns
A dictionary mapping file extensions to their respective loader classes.

#### Example

```python
from configr import ConfigBase

# Get all available loaders
loaders = ConfigBase.get_available_loaders()
print(loaders)  # {'.json': JSONConfigLoader, '.yaml': YAMLConfigLoader, '.yml': YAMLConfigLoader}
```

### `add_loader`

Register a new configuration loader for a specific file extension.

```python
@classmethod
def add_loader(cls, ext: str, loader: Type[ConfigLoader]) -> None:
```

#### Parameters
- `ext`: The file extension (including the dot) to associate with the loader.
- `loader`: The loader class that implements the `ConfigLoader` interface.

#### Example

```python
from configr import ConfigBase, ConfigLoader
from pathlib import Path
import toml

class TOMLConfigLoader(ConfigLoader):
    def load(self, path: Path) -> dict:
        with open(path, 'r') as f:
            return toml.load(f)

# Register the TOML loader
ConfigBase.add_loader('.toml', TOMLConfigLoader)
```

### `remove_loader`

Remove a configuration loader for a specific file extension.

```python
@classmethod
def remove_loader(cls, ext: str) -> None:
```

#### Parameters
- `ext`: The file extension to remove from the available loaders.

#### Example

```python
from configr import ConfigBase

# Remove the YAML loader
ConfigBase.remove_loader('.yaml')
```

### `get_config_path`

Get the base configuration directory path.

```python
@classmethod
def get_config_path(cls) -> Path:
```

#### Returns
A `Path` object representing the configuration directory.

#### Example

```python
from configr import ConfigBase

# Get the configuration directory path
config_path = ConfigBase.get_config_path()
print(config_path)  # /path/to/_config
```

### `load`

Load configuration from a file and convert it to the specified dataclass.

```python
@classmethod
def load(cls, config_class: Type[T], config_data: dict | None = None) -> T:
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

#### Example

```python
from configr import ConfigBase, config_class

@config_class
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str
    database: str

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

### `_get_loader`

Determine the appropriate loader based on the file extension.

```python
@classmethod
def _get_loader(cls, file_name) -> ConfigLoader:
```

#### Parameters
- `file_name`: The name of the configuration file.

#### Returns
An instance of the appropriate `ConfigLoader` for the given file extension.

### `_get_config_file_path`

Get the full path to the configuration file.

```python
@classmethod
def _get_config_file_path(cls, file_name: str) -> Path:
```

#### Parameters
- `file_name`: The name of the configuration file.

#### Returns
A `Path` object representing the full path to the configuration file.

### `_get_config_file_name`

Get the file name from the configuration class.

```python
@classmethod
def _get_config_file_name(cls, config_class: Type) -> str:
```

#### Parameters
- `config_class`: The configuration class.

#### Returns
The file name associated with the configuration class.

## Implementation Details

The `ConfigBase` class:

1. Determines the appropriate file to load based on the configuration class and extensions
2. Uses the corresponding loader to parse the file into a dictionary
3. Performs type validation using `FieldTypeChecker`
4. Handles nested dataclass structures recursively
5. Creates and returns an instance of the specified dataclass with the loaded configuration data

## Example Usage

```python
from configr import ConfigBase, config_class

@config_class(file_name="database.json")
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str
    database: str

@config_class(file_name="app.yaml")
class AppConfig:
    debug: bool = False
    log_level: str = "INFO"
    database: DatabaseConfig = None  # Nested configuration

# Set custom configuration directory
ConfigBase.set_config_dir("my_configs")

# Load configurations
db_config = ConfigBase.load(DatabaseConfig)
app_config = ConfigBase.load(AppConfig)

# Use the loaded configuration
print(f"Connecting to {db_config.database} at {db_config.host}:{db_config.port}")
print(f"Debug mode: {app_config.debug}, Log level: {app_config.log_level}")
```