# Getting Started

This guide will help you quickly set up and start using Configr in your projects.

## Installation

Install Configr using pip:

```bash
pip install py-configr
```

If you want to use YAML configuration files, you'll need to install with the YAML extra:

```bash
pip install py-configr[yaml]
```

If you want to use .env configuration files, you'll need to install with the dotenv extra:

```bash
pip install py-configr[dotenv]
```

You can also install multiple extras at once:

```bash
pip install py-configr[yaml,dotenv]
```

## Basic Setup

1. Create a configuration directory in your project (default is `_config/`)
2. Define your configuration classes using the `@config_class` decorator
3. Create corresponding configuration files (JSON or YAML)
4. Load and use your configuration in your application

## Configuration Directory

By default, Configr looks for configuration files at a path from `CONFIG_DIR` environment variable or in a `_config/`
directory at the root of your project. You can change this globally:

By setting the environment variable

```bash
export CONFIG_DIR=path/to/your/config
```

or programmatically:

```python
from configr import ConfigBase
from pathlib import Path

# Set a new configuration directory using string
ConfigBase.set_config_dir("path/to/your/config")

# Or using Path from pathlib
ConfigBase.set_config_dir(Path("path/to/your/config"))
```

## Defining Configuration Classes

Use the `@config_class` decorator to define your configuration structure:

```python
from configr import config_class


@config_class
class AppConfig:
    debug: bool = False
    log_level: str = "INFO"
    max_connections: int = 100
```

By default, the library will look for a file named after the class in snake_case. For the `AppConfig` example above, it
would look for `_config/app_config.json` or `_config/app_config.yaml` depending on the available loaders.

You can specify a custom file name:

```python
@config_class(file_name="settings.json")
class AppConfig:
    debug: bool = False
    log_level: str = "INFO"
    max_connections: int = 100
```

## Loading Configuration

Use the `ConfigBase.load()` method to load your configuration:

```python
from configr import ConfigBase

# Load your configuration
app_config = ConfigBase.load(AppConfig)

# Use the configuration
if app_config.debug:
    print(f"Running in debug mode with log level {app_config.log_level}")
```

## Configuration File Formats

### JSON Example

```json
{
  "debug": true,
  "log_level": "DEBUG",
  "max_connections": 50
}
```

### YAML Example

```yaml
debug: true
log_level: DEBUG
max_connections: 50
```

### .env Example

```bash
# Configuration for AppConfig class
APP_DEBUG=true
APP_LOG_LEVEL=DEBUG
APP_MAX_CONNECTIONS=50
```

**Note**: .env files use environment variable naming with the class name as prefix (e.g., `APP_` for `AppConfig`). Requires the dotenv extra: `pip install py-configr[dotenv]`

## Handling Missing Files and Validation Errors

Configr provides specific exceptions for different error types:

```python
from configr import ConfigBase, ConfigFileNotFoundError, ConfigValidationError

try:
    app_config = ConfigBase.load(AppConfig)
except ConfigFileNotFoundError:
    print("Configuration file not found, using defaults")
    app_config = AppConfig()
except ConfigValidationError as e:
    print(f"Configuration validation failed: {e}")
    # Handle invalid configuration values
```

## Complete Example

Here's a complete example of how to use Configr in a project:

```python
from dataclasses import dataclass
from configr import config_class, ConfigBase, ConfigFileNotFoundError, ConfigValidationError


# Define configuration classes
@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str
    database: str


@config_class(file_name="settings.json")
class AppConfig:
    debug: bool = False
    log_level: str = "INFO"
    max_connections: int = 100
    database: DatabaseConfig


# Load configuration
try:
    app_config = ConfigBase.load(AppConfig)

    # Use configuration
    print(f"Application running in {'debug' if app_config.debug else 'production'} mode")
    print(
        f"Connecting to database {app_config.database.database} at {app_config.database.host}:{app_config.database.port}")
    
except ConfigFileNotFoundError as e:
    print(f"Configuration error: {e}")
    print("Using default configuration")

    # Fall back to defaults with minimal required values
    app_config = AppSettings(
        database=DatabaseConfig(
            username="default_user",
            password="default_password",
            database="default_db"
        )
    )
except ConfigValidationError as e:
    print(f"Configuration validation error: {e}")
    # Handle invalid configuration
```

## Next Steps

Now that you have the basics of Configr, you can explore more advanced topics:

- [Configuration Classes](user-guide/config-classes.md): Learn more about defining and working with configuration
  classes
- [Custom Loaders](user-guide/custom-loaders.md): Extend Configr with support for additional file formats
- [Examples](examples.md): See examples of Configr in action