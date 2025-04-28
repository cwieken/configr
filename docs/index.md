# Configr

A flexible, type-safe configuration management library for Python.

##  

!!! note

    The API documentation and usage examples in this project were initially generated with the assistance of Claude, an AI assistant. All content has been reviewed and edited by the project maintainers to ensure accuracy and clarity.

## Overview

Configr simplifies configuration management by leveraging Python's dataclasses and type hints to provide a robust,
type-safe approach to application configuration.
It seamlessly converts configuration files to strongly-typed Python classes, making configuration both safer and easier
to work with.

## Key Features

- **Type Safety**: Leverage Python's type hints for configuration validation
- **Dataclass Integration**: Seamlessly map configuration files to Python dataclasses
- **Multiple Format Support**: Load configuration from JSON and YAML
- **Extendable**: Easily add support for custom configuration formats through the loader system, such as TOML or XML
- **Nested Configuration**: Support for complex nested dataclass structures
- **Validation**: Strict type checking for all configuration values
- **Simple API**: Convenient decorator-based approach for defining configuration classes

## Quick Example

```python
from configr import config_class, ConfigBase


@config_class(file_name="database.json")
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str


# Load configuration
db_config = ConfigBase.load(DatabaseConfig)

# Use configuration
print(f"Connecting to {db_config.database} at {db_config.host}:{db_config.port}")
```

With a JSON file at `_config/database.json`:

```json
{
  "host": "localhost",
  "username": "admin",
  "password": "secure_password",
  "database": "my_app"
}
```

## Installation

Install Configr using pip:

```bash
pip install py-configr
```

For YAML support, install with the YAML extra:

```bash
pip install py-configr[yaml]
```

## Why Choose Configr?

- **Developer Experience**: Get IDE autocompletion and type checking for configuration
- **Type Safety**: Catch configuration errors early with type validation
- **Clean Codebase**: Separate configuration concerns from application logic
- **Flexibility**: Support for different file formats with a consistent API
- **Simplicity**: Define your configuration structure once as a dataclass
- **Extensibility**: Easily extend with custom loaders for different configuration sources

## Next Steps

- Read the [Getting Started](getting-started.md) guide
- Check out the [Examples](examples.md)
- Browse the [API Reference](api/config-base.md)