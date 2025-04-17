# config_class

`config_class` is a decorator used to mark classes as configuration classes in the Configr library. It simplifies the creation of configuration classes by automatically converting them to dataclasses and managing the association with configuration files.

## Overview

The `config_class` decorator:

1. Ensures the decorated class is a dataclass
2. Associates a configuration file name with the class
3. Provides a convention for naming configuration files based on the class name

## Function Signature

```python
def config_class(cls=None, *, file_name: str = None):
    """
    Decorator to mark a class as a configuration class.
    This allows specifying a custom file name for the configuration.
    """
```

## Parameters

| Parameter  | Type        | Default | Description                                          |
|------------|-------------|---------|------------------------------------------------------|
| `cls`      | `type`      | `None`  | The class to decorate                                |
| `file_name`| `str`       | `None`  | Optional name of the configuration file to associate with the class |

## Return Value

Returns the decorated class, which is:


- Converted to a dataclass if it's not already
- Enhanced with a `_config_file_name` class attribute


## Implementation Details

The decorator works in two ways:

1. **Direct decoration**: When used as `@config_class` (without parentheses), the class is passed directly as the first argument.

2. **Parameterized decoration**: When used as `@config_class(file_name=...)`, a wrapper function is created that receives the class and applies the decoration.

The decorator:

* Converts the class to a dataclass if it isn't already one
* Sets the `_config_file_name` class attribute based on:
    * The explicitly provided `file_name` parameter
    * The class name converted to snake_case (as a fallback)

## Example Usage

### Basic Example

```python
from configr import config_class, ConfigBase

@config_class
class DatabaseConfig:
    host: str
    port: int = 5432
    username: str
    password: str
    database: str

# Load configuration
db_config = ConfigBase.load(DatabaseConfig)
```

### Custom File Name Example

```python
from configr import config_class, ConfigBase

@config_class(file_name="db_config.yaml")
class DatabaseConfig:
    host: str
    port: int = 5432
    username: str
    password: str
    database: str

# Load configuration from db_config.yaml
db_config = ConfigBase.load(DatabaseConfig)
```

### With Nested Configuration

```python
from configr import config_class, ConfigBase
from dataclasses import dataclass

@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = None
    format: str = "%(asctime)s - %(levelname)s - %(message)s"

@config_class(file_name="app_config.json")
class AppConfig:
    name: str
    version: str
    logging: LoggingConfig = None

# Load configuration with nested structure
app_config = ConfigBase.load(AppConfig)
```

## Notes

- When no `file_name` is specified, the default is to use the class name converted to snake_case
- The extension (.json, .yaml, etc.) determines which loader will be used
- If the extension is omitted, Configr will try each registered loader in order until it finds a matching file