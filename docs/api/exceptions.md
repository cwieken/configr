# Exceptions

Configr defines custom exceptions to provide clear error handling and diagnostics when loading and validating configuration.

## Exception Classes

### ConfigFileNotFoundError

```python
class ConfigFileNotFoundError(FileNotFoundError):
    """Raised when a configuration file is not found."""
    pass
```

This exception is raised when Configr cannot find a configuration file for a given configuration class. It inherits from the built-in `FileNotFoundError` class.

#### When It's Raised

- When `ConfigBase.load()` is called and the specified configuration file does not exist
- When all potential file extensions are tried and no matching file is found

#### Example

```python
from configr import ConfigBase, ConfigFileNotFoundError
from my_config import AppConfig

try:
    config = ConfigBase.load(AppConfig)
except ConfigFileNotFoundError as e:
    print(f"Configuration error: {e}")
    print("Using default configuration instead")
    config = AppConfig()  # Use default values defined in the class
```

### ConfigValidationError

```python
class ConfigValidationError(ValueError):
    """Raised when configuration validation fails."""
    pass
```

This exception is raised when the configuration data fails validation. It inherits from the built-in `ValueError` class.

#### When It's Raised

- When the types in the configuration file don't match the types defined in the configuration class
- When required fields are missing in the configuration data

#### Example

```python
from configr import ConfigBase, ConfigValidationError
from my_config import ServerConfig

try:
    config = ConfigBase.load(ServerConfig)
except ConfigValidationError as e:
    print(f"Invalid configuration: {e}")
    print("Please check your configuration file and ensure all values are correct")
    raise  # Re-raise because this is a critical error
```

## Handling Exceptions

### Best Practices

1. **Graceful Fallbacks**: Handle `ConfigFileNotFoundError` by falling back to default values when possible

    ```python
    try:
        db_config = ConfigBase.load(DatabaseConfig)
    except ConfigFileNotFoundError:
        print("Database configuration not found, using defaults")
        db_config = DatabaseConfig(
            host="localhost",
            username="default_user",
            password="default_password",
            database="default_db"
        )
    ```

2. **Detailed Error Messages**: Provide clear information when configuration validation fails

    ```python
    try:
        app_config = ConfigBase.load(AppConfig)
    except ConfigValidationError as e:
        print(f"Configuration error in app_config.json: {e}")
        print("Please refer to the documentation for correct configuration format")
        sys.exit(1)  # Exit application if configuration is invalid
    ```

3. **Combined Exception Handling**: Handle multiple exception types appropriately

    ```python
    try:
        config = ConfigBase.load(AppConfig)
    except ConfigFileNotFoundError:
        print("Configuration file not found, using defaults")
        config = AppConfig()
    except ConfigValidationError as e:
        print(f"Configuration validation failed: {e}")
        raise  # Re-raise critical validation errors
    except Exception as e:
        print(f"Unexpected error loading configuration: {e}")
        raise
    ```

### Custom Validation Exceptions

You can raise `ConfigValidationError` in your own `__post_init__` methods to provide custom validation:

```python
from configr import config_class, ConfigValidationError

@config_class
class ServerConfig:
    host: str
    port: int
    workers: int
    
    def __post_init__(self):
        if self.port < 1024 or self.port > 65535:
            raise ConfigValidationError(f"Invalid port: {self.port}. Must be between 1024 and 65535.")
        if self.workers < 1:
            raise ConfigValidationError(f"Invalid workers: {self.workers}. Must be at least 1.")
```

## Exception Hierarchy

The exception hierarchy in Configr is designed to be intuitive and integrate well with Python's built-in exceptions:

```
BaseException
 └── Exception
      ├── ValueError
      │    └── ConfigValidationError
      └── OSError
           └── FileNotFoundError
                └── ConfigFileNotFoundError
```

This hierarchy allows you to catch exceptions at different levels depending on your needs:

```python
# Catch only Configr-specific file not found errors
except ConfigFileNotFoundError as e:
    # Handle missing configuration files

# Catch any file not found errors
except FileNotFoundError as e:
    # Handle any missing files

# Catch only Configr-specific validation errors
except ConfigValidationError as e:
    # Handle validation errors

# Catch any value errors
except ValueError as e:
    # Handle any value errors

# Catch any exceptions
except Exception as e:
    # Handle any exceptions
```

## Example: Complete Error Handling

Here's a complete example of robust error handling with Configr:

```python
from configr import ConfigBase, config_class, ConfigFileNotFoundError, ConfigValidationError

@config_class(file_name="database.json")
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    username: str = None
    password: str = None
    database: str = None
    
    def __post_init__(self):
        if self.port < 1024 or self.port > 65535:
            raise ConfigValidationError(f"Invalid port: {self.port}")
        if not self.username and not self.password:
            # This is allowed, will use default authentication
            pass
        elif not self.username or not self.password:
            # This is not allowed, must provide both or neither
            raise ConfigValidationError("Both username and password must be provided")

def load_database_config():
    """Load database configuration with robust error handling."""
    try:
        return ConfigBase.load(DatabaseConfig)
    except ConfigFileNotFoundError as e:
        print(f"Warning: {e}")
        print("Using default database configuration")
        return DatabaseConfig()
    except ConfigValidationError as e:
        print(f"Error: Database configuration is invalid: {e}")
        print("Please check your database.json file")
        raise
    except Exception as e:
        print(f"Unexpected error loading database configuration: {e}")
        raise

# Usage
db_config = load_database_config()
print(f"Connecting to {db_config.database} at {db_config.host}:{db_config.port}")
```