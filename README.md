# Configr

A flexible, type-safe configuration management library for Python.

Configr simplifies configuration management by leveraging Python's dataclasses and type hints to provide a robust, type-safe approach to application configuration.

[![Python Versions](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12%20|%203.13-blue)](https://www.python.org/)
[![PyPI version](https://img.shields.io/pypi/v/py-configr.svg)](https://pypi.org/project/py-configr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/cwieken/configr/actions/workflows/run-tests.yml/badge.svg)](https://github.com/cwieken/configr/actions/workflows/run-tests.yml)

- **Type Safety**: Leverage Python's type hints for configuration validation
- **Dataclass Integration**: Seamlessly map configuration files to Python dataclasses
- **Multiple Format Support**: Load configuration from JSON and YAML files
- **Extendable**: Easily add support for custom configuration formats
- **Simple API**: Convenient decorator-based approach for defining configuration classes

## Requirements
- Python 3.10 or higher


## Installation

```bash
pip install py-configr

# For YAML support
pip install py-configr[yaml]
```

## Quick Start

Define your configuration class:

```python
from configr import config_class, ConfigBase

@config_class(file_name="database.json")
class DatabaseConfig:
    username: str
    password: str
    database: str
    host: str
    port: int = 5432

# Load configuration
db_config = ConfigBase.load(DatabaseConfig)

# Use configuration
print(f"Connecting to {db_config.database} at {db_config.host}:{db_config.port}")
```

Create a configuration file in `_config/database.json`:

```json
{
  "host": "localhost",
  "username": "admin",
  "password": "secure_password",
  "database": "my_app"
}
```

## Documentation

For complete documentation, visit [our documentation site](https://cwieken.github.io/configr/).

- [Getting Started](https://cwieken.github.io/configr/getting-started/)
- [API Reference](https://cwieken.github.io/configr/api/config-base/)
- [Examples](https://cwieken.github.io/configr/examples/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.