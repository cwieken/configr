# Loaders

The Configr library provides a flexible loading system for different configuration file formats. This page documents the
loaders included with Configr and how to create custom loaders for additional file formats.

## Overview

Loaders in Configr:

1. Read configuration files in specific formats (JSON, YAML, etc.)
2. Parse those files into Python dictionaries
3. Allow the `ConfigBase` class to convert the dictionaries into typed dataclasses

## Base Classes

### ConfigLoader

All loaders in Configr inherit from the abstract base class `ConfigLoader`.

```python
from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar('T')


class ConfigLoader(ABC):
    """
    Abstract base class for configuration loaders.
    
    Defines the common interface that all configuration loaders must implement.
    Configuration loaders are responsible for loading configuration data from
    various sources and returning it as a dictionary.
    """

    @classmethod
    @abstractmethod
    def load(cls, name: str, config_class: type[T]) -> dict[str, Any]:
        """
        Load configuration data for the specified configuration class.
        
        Args:
            name (str): The name or identifier of the configuration to load.
            config_class (type[T]): The dataclass type for which to load configuration.
            
        Returns:
            dict[str, Any]: The loaded configuration data as a dictionary.
            
        Raises:
            ConfigFileNotFoundError: If the configuration cannot be found.
            TypeError: If the config_class is not a dataclass.
        """
        pass
```

### FileConfigLoader

For file-based configuration sources, Configr provides the `FileConfigLoader` abstract class:

```python
class FileConfigLoader(ConfigLoader, ABC):
    """
    Abstract base class for file-based configuration loaders.
    
    Extends the ConfigLoader interface with file-specific functionality,
    providing common methods for locating and loading configuration files.
    File-based loaders support specific file extensions and search in a
    configurable directory.
    """
    _config_dir: ClassVar[str] = os.environ.get('CONFIG_DIR', '_config')
    ext: list[str]  # Register list of supported file extensions

    @classmethod
    def get_extensions(cls) -> list[str]:
        """Get the supported file extensions."""
        return cls.ext

    @classmethod
    def get_config_path(cls) -> Path:
        """Get the base configuration directory path."""
        return Path(cls._config_dir)

    @classmethod
    def set_config_dir(cls, config_dir: str | Path) -> None:
        """Set the base config directory path if default should not be used."""
        if isinstance(config_dir, Path):
            cls._config_dir = str(config_dir)
        else:
            cls._config_dir = config_dir

    @classmethod
    def _iter_config_file_paths(cls, name: str) -> Generator[Path, Any, None]:
        """Iterate over all possible configuration file paths."""
        # Implementation details

    @classmethod
    def _get_config_file_path(cls, name: str) -> Path:
        """Get full path to config file (first that exists)."""
        # Implementation details

    @classmethod
    def config_file_exists(cls, name: str) -> bool:
        """Check if config file exists."""
        # Implementation details
```

## Built-in Loaders

### JSONConfigLoader

Loader for JSON configuration files.

```python
class JSONConfigLoader(FileConfigLoader):
    """
    Loader for JSON configuration files.
    
    This class provides functionality to load configuration data from JSON files
    and map it to the fields of a dataclass.
    """
    ext: list[str] = ['.json']  # Supported file extensions for JSON configuration files.

    @classmethod
    def load(cls, name: str, config_class: type[T] = None) -> dict[str, Any]:
        """
        Load JSON configuration from the specified path.
        
        Args:
            name (str): The name of the configuration file (without extension).
            config_class (type[T]): The dataclass type to map the configuration data to.
            
        Returns:
            dict[str, Any]: A dictionary containing the loaded configuration data.
            
        Raises:
            FileNotFoundError: If the specified configuration file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        # Implementation details
```

Example JSON configuration file:

```json
{
  "host": "localhost",
  "port": 5432,
  "username": "admin",
  "password": "secure_password",
  "database": "my_app"
}
```

### YAMLConfigLoader

Loader for YAML configuration files. Requires PyYAML to be installed.

```python
class YAMLConfigLoader(FileConfigLoader):
    """
    Loader for YAML configuration files.
    
    This class provides functionality to load configuration data from YAML files
    and map it to the fields of a dataclass. It supports files with `.yaml` and `.yml` extensions.
    """
    ext: list[str] = ['.yaml', '.yml']  # Supported file extensions for YAML configuration files.

    @classmethod
    def load(cls, name: str, config_class: type[T] = None) -> dict[str, Any]:
        """
        Load YAML configuration from the specified path.
        
        Args:
            name (str): The name of the configuration file (without extension).
            config_class (type[T]): The dataclass type to map the configuration data to.
            
        Returns:
            dict[str, Any]: A dictionary containing the loaded configuration data.
            
        Raises:
            ImportError: If PyYAML is not installed.
            FileNotFoundError: If the specified configuration file does not exist.
            yaml.YAMLError: If the file contains invalid YAML.
        """
        # Implementation details
```

Example YAML configuration file:

```yaml
host: localhost
port: 5432
username: admin
password: secure_password
database: my_app
```

### EnvVarConfigLoader

Loader for environment variable configuration.

```python
from configr.loaders.loader_env_var import EnvVarConfigLoader


class EnvVarConfigLoader(ConfigLoader):
    """
    Loader for environment variable configuration.
    
    This class provides functionality to load configuration data from environment
    variables. Environment variables should follow the pattern:
    {CONFIG_NAME}_{FIELD_NAME} where both parts are uppercase.
    
    For nested dataclasses, the pattern extends to:
    {CONFIG_NAME}_{PARENT_FIELD}_{CHILD_FIELD}
    
    Type conversion is performed automatically for:
    - Booleans: "true", "false", "1", "0" 
    - Integers: Numeric strings
    - Floats: Decimal numeric strings
    - Lists: Comma-separated values
    """

    @classmethod
    def load(cls, name: str, config_class: type[T]) -> dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Args:
            name (str): The prefix for environment variables (converted to uppercase).
            config_class (type[T]): The dataclass type to map the configuration data to.
            
        Returns:
            dict[str, Any]: A dictionary containing the loaded configuration data.
        """
        # Implementation details
```

Example usage:

```python
from configr import config_class, ConfigBase


# When no file_name is specified, and no file with ending for
# configured loader exists, EnvVarConfigLoader is used
@config_class()
class AppConfig:
    debug: bool = False
    host: str = "localhost"
    port: int = 8080
    database_url: str = None


# Set environment variables
# export APPCONFIG_DEBUG=true
# export APPCONFIG_HOST=0.0.0.0
# export APPCONFIG_PORT=3000
# export APPCONFIG_DATABASE_URL=postgresql://localhost/mydb

# Load from environment variables
config = ConfigBase.load(AppConfig)
```

### DotEnvConfigLoader

Loader for .env configuration files. Requires python-dotenv to be installed.

```python
class DotEnvConfigLoader(FileConfigLoader):
    """
    Loader for .env configuration files.
    
    This class provides functionality to load configuration data from .env files
    and map it to the fields of a dataclass. It leverages the environment variable
    processing logic for type conversion and nested structure handling.
    """
    ext: list[str] = ['.env']  # Supported file extensions for .env configuration files.

    @classmethod
    def load(cls, name: str, config_class: type[T]) -> dict[str, Any]:
        """
        Load .env configuration from the specified path.
        
        Args:
            name (str): The prefix for environment variable names (used for variable naming).
            config_class (type[T]): The dataclass type to map the configuration data to.
            
        Returns:
            dict[str, Any]: A dictionary containing the loaded configuration data.
            
        Raises:
            ImportError: If python-dotenv is not installed.
            FileNotFoundError: If the .env file does not exist in the config directory.
        """
        # Implementation details

    @classmethod
    def config_file_exists(cls, name: str) -> bool:
        """
        Check if .env file exists in the config directory.
        
        Args:
            name (str): The configuration name (not used for .env files).
            
        Returns:
            bool: True if .env file exists, False otherwise.
        """
        # Implementation details

    @classmethod
    def get_config_name(cls, config_class: type) -> str:
        """
        Get config name from the dataclass name.
        
        Args:
            config_class (type): The dataclass type to extract the name from.
            
        Returns:
            str: The configuration name in uppercase, derived from the class name.
        """
        # Implementation details
```

Example .env configuration file:

```bash
# Configuration for AppConfig class (uses APP_ prefix)
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=3000
APP_DATABASE_URL=postgresql://localhost/mydb

# Nested configuration example
APP_DATABASE_HOST=localhost
APP_DATABASE_PORT=5432
APP_DATABASE_USERNAME=admin
APP_DATABASE_PASSWORD=secret
```

Example usage:

```python
from configr import config_class, ConfigBase
from typing import Optional


@config_class(file_name=".env")
class AppConfig:
    debug: bool = False
    host: str = "localhost"
    port: int = 8080
    database_url: Optional[str] = None


# Load from .env file (requires python-dotenv)
config = ConfigBase.load(AppConfig)
```

## Creating Custom Loaders

You can extend Configr with support for additional file formats by creating custom loaders.

### Example: TOMLConfigLoader

Here's an example of how to create a loader for TOML files:

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


# Register the loader with Configr
from configr import ConfigBase

ConfigBase.add_loader(TOMLConfigLoader)
```

Once registered, you can use TOML files with your configuration classes:

```python
from configr import config_class


@config_class(file_name="database.toml")
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str
```

Example TOML configuration file:

```toml
host = "localhost"
port = 5432
username = "admin"
password = "secure_password"
database = "my_app"
```

### Example: INIConfigLoader

Here's an example of a loader for INI files using Python's built-in `configparser`:

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


# Register the loader with Configr
from configr import ConfigBase

ConfigBase.add_loader(INIConfigLoader)
```

Example INI configuration file:

```ini
[DEFAULT]
application = MyApp

[database]
host = localhost
port = 5432
username = admin
password = secure_password
database = my_app

[logging]
level = INFO
file = app.log
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Managing Loaders

### Registering Custom Loaders

Register a custom loader with `ConfigBase.add_loader`:

```python
from configr import ConfigBase
from my_loaders import CustomLoader

ConfigBase.add_loader(CustomLoader)
```

### Removing Loaders

Remove a loader with `ConfigBase.remove_loader`:

```python
from configr import ConfigBase
from configr.loaders.loader_yaml import YAMLConfigLoader

ConfigBase.remove_loader(YAMLConfigLoader)
```

### Getting Available Loaders

Get all available loaders with `ConfigBase.get_available_loaders`:

```python
from configr import ConfigBase

loaders = ConfigBase.get_available_loaders()
print(loaders)  # [JSONConfigLoader, YAMLConfigLoader, ...]
```

### Getting Available File Loaders

Get all available file-based loaders with `ConfigBase.get_available_file_loaders`:

```python
from configr import ConfigBase

file_loaders = ConfigBase.get_available_file_loaders()
print(file_loaders)  # [JSONConfigLoader, YAMLConfigLoader, ...]
```

## Loader Selection Process

When loading a configuration, Configr selects the appropriate loader based on the following process:

1. If explicit `config_data` is provided to `ConfigBase.load()`, no loader is used.
2. For file-based configuration:
    - If a file extension is specified in `_config_file_name`, Configr looks for that exact file.
    - Otherwise, it tries each available file loader to find a matching file.
3. If no file loader can find a matching file, it tries any non-file loaders.
4. If no loader can be found, a `ValueError` is raised.

## Best Practices for Custom Loaders

1. **Error Handling**: Include clear error messages for missing dependencies or file format issues.
2. **Dependencies**: Document any external dependencies required by your loader.
3. **Type Conversion**: Ensure your loader returns data as expected by Configr (dictionaries with the correct types).
4. **Configuration Directory**: Use the `_config_dir` path provided by `FileConfigLoader` for file locations.
5. **File Extension List**: Define a clear list of supported file extensions in the `ext` class variable.

## Example Usage

```python
from configr import config_class, ConfigBase
from my_loaders import XMLConfigLoader

# Register custom XML loader
ConfigBase.add_loader(XMLConfigLoader)


@config_class(file_name="database.xml")
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str


# Load from XML file
db_config = ConfigBase.load(DatabaseConfig)
```