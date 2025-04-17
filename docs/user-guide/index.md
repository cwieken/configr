# User Guide Overview

Welcome to the Configr User Guide. This guide provides comprehensive information about using the Configr library effectively in your projects.

## Key Concepts

Configr is built around a few core concepts:

### Configuration Classes

Configuration classes define the structure of your configuration using Python dataclasses. They specify what configuration values are available, their types, and default values.

### Configuration Loading

Configr provides mechanisms to load configuration data from files and convert it to your configuration classes, ensuring type safety and validation.

### File Formats

The library supports multiple file formats, including JSON and YAML, and can be extended to support additional formats through custom loaders.

## Structure

This user guide is organized into the following sections:

- **[Basic Usage](basic-usage.md)**: Step-by-step guide to using Configr in common scenarios
- **[Configuration Classes](config-classes.md)**: Details about defining and working with configuration classes
- **[Custom Loaders](custom-loaders.md)**: Information about extending Configr with support for additional file formats

## Common Patterns

Here are some common patterns and best practices when using Configr:

### Centralized Configuration

Create a central module for all your configuration classes:

```python
# config.py
from configr import config_class, ConfigBase

@config_class
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str
    database: str

@config_class
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0

# Load all configurations at once
def load_all():
    return {
        "db": ConfigBase.load(DatabaseConfig),
        "redis": ConfigBase.load(RedisConfig)
    }
```

### Environment-Specific Configuration

Use different files for different environments:

```python
import os

@config_class(file_name=f"database.{os.environ.get('ENV', 'dev')}.json")
class DatabaseConfig:
    host: str
    port: int = 5432
    username: str
    password: str
    database: str
```

### Configuration Validation

Add validation logic to your configuration classes:

```python
from configr import config_class, ConfigValidationError

@config_class
class ServerConfig:
    host: str
    port: int
    workers: int
    
    def __post_init__(self):
        if self.port < 1024 or self.port > 65535:
            raise ConfigValidationError(f"Invalid port: {self.port}")
        if self.workers < 1:
            raise ConfigValidationError(f"Workers must be at least 1, got {self.workers}")
```

## Next Steps

Continue to the [Basic Usage](basic-usage.md) section to learn how to use Configr in your projects.