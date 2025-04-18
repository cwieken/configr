# Basic Usage

This guide walks through the common usage patterns for Configr in your Python applications.

## Project Setup

Let's begin with a simple project structure:

```
my_project/
├── _config/
│   ├── database.json
│   └── app_settings.yaml
├── app.py
└── requirements.txt
```

## Configuration Files

Here are examples of configuration files:

### `_config/database.json`

```json
{
  "host": "localhost",
  "port": 5432,
  "username": "admin",
  "password": "secure_password",
  "database": "my_app"
}
```

### `_config/app_settings.yaml`

```yaml
debug: true
log_level: DEBUG
max_connections: 50
timeout: 30
enable_caching: true
enable_metrics: false
```

## Defining Configuration Classes

First, define your configuration classes that match your configuration files:

```python
# config.py
from configr import config_class

@config_class(file_name="database.json")
class DatabaseConfig:
    username: str
    password: str
    database: str
    host: str
    port: int = 5432

@config_class(file_name="app_settings.yaml")
class AppSettings:
    debug: bool = False
    log_level: str = "INFO"
    max_connections: int = 100
    timeout: int = 60
    enabled_cachine: bool = false
    enable_metrics: bool = false
```

## Loading Configuration

Next, load the configuration in your application:

```python
# app.py
from configr import ConfigBase
from config import DatabaseConfig, AppSettings

# Load configurations
db_config = ConfigBase.load(DatabaseConfig)
app_settings = ConfigBase.load(AppSettings)

# Use configurations
if app_settings.debug:
    print(f"Running in DEBUG mode with log level {app_settings.log_level}")
    print(f"Caching enabled: {app_settings.features['enable_caching']}")

# Database connection example
print(f"Connecting to database {db_config.database} at {db_config.host}:{db_config.port}")
print(f"Using credentials: {db_config.username}:{'*' * len(db_config.password)}")
```

## Error Handling

Here's how to handle common errors:

```python
from configr import ConfigBase, ConfigFileNotFoundError, ConfigValidationError

try:
    config = ConfigBase.load(DatabaseConfig)
except ConfigFileNotFoundError as e:
    print(f"Configuration file not found: {e}")
    print("Using default configuration...")
    config = DatabaseConfig(
        host="localhost",
        username="default",
        password="default",
        database="default_db"
    )
except ConfigValidationError as e:
    print(f"Configuration validation failed: {e}")
    raise  # Re-raise if validation is critical
except Exception as e:
    print(f"Unexpected error: {e}")
    raise
```

## Environment-Specific Configuration

For different environments (development, testing, production), you can:

1. **Use environment variables to select configuration files**:

    ```python
    import os
    
    ENV = os.environ.get("ENV", "development")
    
    @config_class(file_name=f"database.{ENV}.json")
    class DatabaseConfig:
        # ...
    ```

2. **Override values with environment variables**:

    ```python
    import os
    from configr import ConfigBase
    
    db_config = ConfigBase.load(DatabaseConfig)
    
    # Override with environment variables if present
    if "DB_HOST" in os.environ:
        db_config.host = os.environ["DB_HOST"]
    if "DB_PORT" in os.environ:
        db_config.port = int(os.environ["DB_PORT"])
    ```

## Working with Nested Configurations

Configr automatically handles nested dataclass structures in your configuration hierarchy. This allows you to organize complex configuration in a type-safe and well-structured manner.

### Defining Nested Configuration Classes

```python
from configr import config_class
from dataclasses import dataclass

@dataclass
class LoggingConfig:
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = None
    
@dataclass
class Tag:
   name: str = None
   category: str = None

@config_class(file_name="app_config.json")
class AppConfig:
    name: str
    version: str
    debug: bool = False
    logging: LoggingConfig = None
    tags: list[Tags] = None
```

### Configuration File Structure

The corresponding JSON file structure would look like:

```json
{
  "name": "MyApp",
  "version": "1.0.0",
  "debug": true,
  "logging": {
    "level": "DEBUG",
    "file": "app.log"
  },
  "tags": [
    {"name":  "MyApp", "category":  "application"},
    {"name":  "1.0.0", "category":  "version"}
  ]
}
```

### Automatic Conversion

Configr will automatically:

1. Detect that `logging` is a field typed as `LoggingConfig` dataclass
2. Convert the nested JSON object to a `LoggingConfig` instance
3. Detect that 'tags' is a field with a list of type `Tag` dataclass
4. Convert each list element JSON object to a `Tag` instance
5. Perform this conversion recursively for any level of nesting

### Accessing Nested Configuration

You can access the nested configuration with native dot notation:

```python
config = ConfigBase.load(AppConfig)

# Access nested configuration using dot notation
log_level = config.logging.level
log_file = config.logging.file
tag1 = config.tags[0].name

print(f"Logging to {log_file} with level {log_level}")

for tag in config.tags:
    print(f"Tag: {tag.name=}, {tag.category=}")
```

### Default Values in Nested Classes

You can provide default values at any level of the configuration hierarchy:

```python
@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    username: str = None
    password: str = None
    
@dataclass
class CacheConfig:
    enabled: bool = False
    ttl: int = 300
    
@config_class(file_name="server_config.json")
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    database: DatabaseConfig = None
    cache: CacheConfig = None
```

With this approach, if the configuration file doesn't specify certain nested objects, they'll be created with their default values.

## Configuration Directory

By default, Configr looks for configuration files in the `_config/` directory. You can customize this:

```python
from configr import ConfigBase
from pathlib import Path

# Set configuration directory
ConfigBase.set_config_dir("path/to/config")
# Or using a Path object
ConfigBase.set_config_dir(Path("path/to/config"))

# Then load configuration
config = ConfigBase.load(AppConfig)
```

## Putting It All Together

Here's a complete example integrating the concepts above:

```python
# config.py
import os
from configr import config_class, ConfigBase, ConfigFileNotFoundError
from dataclasses import dataclass

# Get environment
ENV = os.environ.get("ENV", "development")

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    username: str = None
    password: str = None
    database: str = None

@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = None

@config_class(file_name=f"app.{ENV}.json")
class AppConfig:
    name: str = "MyApp"
    version: str = "1.0.0"
    debug: bool = False
    database: DatabaseConfig = None
    logging: LoggingConfig = None
    
    def __post_init__(self):
        # Apply environment variable overrides
        if "LOG_LEVEL" in os.environ:
            self.logging.level = os.environ["LOG_LEVEL"]
```

## Next Steps

Now that you understand the basics of using Configr, you might want to explore:

- [Configuration Classes](config-classes.md) for more details on defining configuration structures
- [Custom Loaders](custom-loaders.md) to learn how to extend Configr with support for additional file formats