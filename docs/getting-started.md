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

## Basic Setup

1. Create a configuration directory in your project (default is `_config/`)
2. Define your configuration classes using the `@config_class` decorator
3. Create corresponding configuration files (JSON or YAML)
4. Load and use your configuration in your application

## Configuration Directory

By default, Configr looks for configuration files in a `_config/` directory at the root of your project. You can customize this by setting the `CONFIG_DIR` environment variable:

```bash
export CONFIG_DIR=path/to/your/config
```

Or programmatically:

```python
import os
os.environ["CONFIG_DIR"] = "path/to/your/config"
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

By default, the library will look for a file named after the class in snake_case with a `.json` extension. For the `AppConfig` example above, it would look for `_config/app_config.json`.

You can specify a custom file name:

```python
@config_class(file_name="settings.yaml")
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

## Handling Missing Files

If a configuration file is missing, Configr will raise a `ConfigFileNotFoundError`. You can handle this gracefully:

```python
from configr import ConfigBase, ConfigFileNotFoundError

try:
    app_config = ConfigBase.load(AppConfig)
except ConfigFileNotFoundError:
    print("Configuration file not found, using defaults")
    app_config = AppConfig()
```

## Complete Example

Here's a complete example of how to use Configr in a project:

```python
import os
from dataclasses import dataclass
from configr import config_class, ConfigBase, ConfigFileNotFoundError

# Define configuration classes
@config_class(file_name="database.json")
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str
    database: str

@config_class(file_name="app.json")
class AppConfig:
    debug: bool = False
    log_level: str = "INFO"
    max_connections: int = 100

# Load configuration
try:
    db_config = ConfigBase.load(DatabaseConfig)
    app_config = ConfigBase.load(AppConfig)
    
    # Use configuration
    print(f"Application running in {'debug' if app_config.debug else 'production'} mode")
    print(f"Connecting to database {db_config.database} at {db_config.host}:{db_config.port}")
    
except ConfigFileNotFoundError as e:
    print(f"Configuration error: {e}")
    print("Using default configuration")
    
    # Fall back to defaults
    db_config = DatabaseConfig(
        username="default_user",
        password="default_password",
        database="default_db"
    )
    app_config = AppConfig()
```

## Next Steps

Now that you have the basics of Configr, you can explore more advanced topics:

- [Configuration Classes](user-guide/config-classes.md): Learn more about defining and working with configuration classes
- [Custom Loaders](user-guide/custom-loaders.md): Extend Configr with support for additional file formats
- [Examples](examples.md): See examples of Configr in action