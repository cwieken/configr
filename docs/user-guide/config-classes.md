# Configuration Classes

Configuration classes are at the heart of Configr. They define the structure of your configuration using Python's dataclasses and type hints, providing a type-safe approach to configuration management.

## Basic Configuration Class

At its simplest, a configuration class is just a dataclass decorated with `@config_class`:

```python
from configr import config_class

@config_class
class DatabaseConfig:
    username: str
    password: str
    database: str
    host: str = 'localhost'
    port: int = 5432
```

This class defines a configuration with five fields:

  - `host`: A string with a default value of localhost (optional)
  - `port`: An integer with a default value of 5432 (optional)
  - `username`: A string with no default value (required)
  - `password`: A string with no default value (required)
  - `database`: A string with no default value (required)

## The `@config_class` Decorator

The `@config_class` decorator does several things:

1. It ensures the class is a dataclass (converts it if it's not already)
2. It adds a `_config_file_name` attribute to specify which file to load
3. It ensures the file has a supported extension (.json by default)

### Specifying a Custom File Name

By default, Configr will look for a file named after the class in snake_case with a `.json` extension. For example, `DatabaseConfig` will look for `_config/database_config.json`.
If the file does not exist, it will look for each of the registered extensions, e.g. `_config/database_config.yaml` or `_config/database_config.yml` 

You can specify a custom file name:

```python
@config_class(file_name="db_settings.yaml")
class DatabaseConfig:
    host: str = 'localhost'
    port: int = 5432
    # ...
```

Now Configr will look for `_config/db_settings.yaml`.

### Using with Existing Dataclasses

If your class is already a dataclass, the decorator will preserve that:

```python
from dataclasses import dataclass
from configr import config_class

@config_class  # This works
@dataclass
class AppConfig:
    debug: bool = False
    log_level: str = "INFO"

# Or this way:
@dataclass
@config_class  # This also works
class ServerConfig:
    host: str = 'localhost'
    port: int = 8080
```

## Type Safety and Validation

Configr leverages Python's type hints to provide type safety for your configuration.

### Basic Types

You can use all standard Python types:

```python
@config_class
class AppConfig:
    name: str
    version: str
    port: int
    debug: bool
    rate_limit: float
    tags: list 
    options: dict
    handler: callable = None
```

### Type Validation

Configr doesn't perform automatic type conversion or validation when loading configuration. Instead, it relies on Python's dataclass mechanism to handle type checking:

```python
# _config/app_config.json
{
  "name": "MyApp",
  "version": "1.0.0",
  "port": "8080",  # This is a string, not an int!
  "debug": true,
  "rate_limit": 100.0,
  "tags": ["tag1", "tag2"],
  "options": {}
}

# This will raise a ConfigValidationError when instantiating the dataclass
config = ConfigBase.load(AppConfig)
```

To add custom validation, use the `__post_init__` method in your config class:

```python
from configr import config_class, ConfigValidationError

@config_class
class ServerConfig:
    host: str
    port: int
    
    def __post_init__(self):
        if self.port < 1024 or self.port > 65535:
            raise ConfigValidationError(f"Invalid port: {self.port}")
```

## Default Values

Specify default values for optional configuration parameters:

```python
@config_class
class AppConfig:
    debug: bool = False
    log_level: str = "INFO"
    max_connections: int = 100
    timeout: int = 30
```

Fields without default values are considered required and must be provided in the configuration file.


## Inheritance

You can use inheritance to create specialized configuration classes:

```python
@config_class
class BaseConfig:
    debug: bool = False
    log_level: str = "INFO"

@config_class
class DevelopmentConfig(BaseConfig):
    debug: bool = True
    database_url: str = "sqlite:///dev.db"

@config_class
class ProductionConfig(BaseConfig):
    log_level: str = "WARNING"
    database_url: str = "postgresql://user:pass@localhost/prod"
```

## Configuration Class Methods

You can add methods to your configuration classes for convenience:

```python
@config_class
class DatabaseConfig:
    driver: str
    host: str
    port: int
    username: str
    password: str
    database: str
    
    def get_connection_string(self):
        """Generate a database connection string."""
        return f"{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def get_connection_params(self):
        """Return connection parameters as a dictionary."""
        return {
            "driver": self.driver,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "database": self.database
        }
```

## Nested Configuration

Configr provides robust support for nested configuration structures, allowing you to organize complex configurations in a clean, type-safe manner. The library automatically handles the conversion between nested JSON/YAML structures and Python dataclasses.

### Using Nested Dataclasses

You can define nested configuration structures by using dataclasses as field types within your config classes:

```python
from configr import config_class
from dataclasses import dataclass

# Define nested dataclass for database configuration
@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    username: str = None
    password: str = None
    database: str = None

# Define nested dataclass for logging configuration
@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = None
    format: str = "%(asctime)s - %(levelname)s - %(message)s"

# Main configuration class using nested dataclasses
@config_class(file_name="app_config.json")
class AppConfig:
    name: str
    version: str
    debug: bool = False
    database: DatabaseConfig = None  # Nested dataclass field
    logging: LoggingConfig = None    # Nested dataclass field
```

With a corresponding JSON file like:

```json
{
  "name": "MyApp",
  "version": "1.0.0",
  "debug": true,
  "database": {
    "host": "db.example.com",
    "port": 5432,
    "username": "admin",
    "password": "secure_password",
    "database": "myapp_db"
  },
  "logging": {
    "level": "DEBUG",
    "file": "app.log"
  }
}
```

When you load the configuration, Configr will automatically:

1. Recognize that `database` is a field of type `DatabaseConfig`
2. Convert the nested JSON object to a `DatabaseConfig` instance
3. Similarly convert the `logging` field to a `LoggingConfig` instance
4. Handle any level of nesting recursively

Accessing nested configuration is done with standard dot notation:

```python
from configr import ConfigBase

# Load the configuration
config = ConfigBase.load(AppConfig)

# Access nested fields with dot notation
db_host = config.database.host        # "db.example.com"
log_level = config.logging.level      # "DEBUG"
log_format = config.logging.format    # Uses default value
```

### Collections of Dataclasses

Configr also supports collections of dataclasses, such as lists or dictionaries of dataclass instances. This is useful for configuration items that can have multiple instances or variations.

#### Lists of Dataclasses

```python
from configr import config_class
from dataclasses import dataclass
from typing import List

@dataclass
class ServiceConfig:
    name: str
    url: str
    timeout: int = 30
    retries: int = 3

@config_class(file_name="services_config.json")
class ServicesConfig:
    enabled: bool = True
    services: List[ServiceConfig] = None  # List of dataclass instances
```

With a JSON file like:

```json
{
  "enabled": true,
  "services": [
    {
      "name": "authentication",
      "url": "https://auth.example.com/api",
      "timeout": 10
    },
    {
      "name": "storage",
      "url": "https://storage.example.com/api",
      "timeout": 60,
      "retries": 5
    }
  ]
}
```

Configr will automatically convert each object in the `services` list to a `ServiceConfig` instance:

```python
config = ConfigBase.load(ServicesConfig)

# Access the first service
auth_service = config.services[0]
print(auth_service.name)     # "authentication"
print(auth_service.timeout)  # 10
print(auth_service.retries)  # 3 (default value)

# Iterate through all services
for service in config.services:
    print(f"{service.name}: {service.url}")
```

### Default Values and None Handling

Configr intelligently handles default values in nested dataclasses:

1. If a nested dataclass field is `None` in the configuration file, Configr will attempt to create an empty instance using the class's default constructor.
2. If the nested dataclass constructor requires arguments with no defaults, the field will remain `None`.
3. Default values in nested dataclasses are respected at all levels of nesting.

Example:

```python
@dataclass
class DatabaseConfig:
    # These fields have no defaults and are required
    username: str
    password: str
    database: str
    host: str = "localhost"
    port: int = 5432

@config_class
class AppConfig:
    debug: bool = False
    # This will be None if not in the config file, since DatabaseConfig
    # has required fields with no defaults
    database: DatabaseConfig = None
```

### Type Validation in Nested Structures

Configr performs type validation for nested dataclass fields just like it does for top-level fields. If the data in your configuration file doesn't match the expected types in your nested dataclasses, Configr will raise a `ConfigValidationError`.

This ensures that your entire configuration hierarchy maintains type safety.

### Customizing Nested Configuration

You can add methods to your nested dataclasses for additional functionality:

```python
@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str
    
    def get_connection_string(self):
        """Generate a database connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def __post_init__(self):
        """Validate database configuration."""
        if self.port < 1024 or self.port > 65535:
            raise ValueError(f"Invalid port: {self.port}")
```

Then use these methods in your code:

```python
config = ConfigBase.load(AppConfig)
connection_str = config.database.get_connection_string()
```

### Best Practices for Nested Configuration

1. **Keep nesting reasonable**: While Configr supports arbitrary nesting, keep your hierarchy sensible for maintainability.

2. **Use explicit types**: Always use explicit type annotations, especially for collections of dataclasses.

3. **Provide defaults where appropriate**: Use default values for optional fields to make your configuration more robust.

4. **Add validation in `__post_init__`**: Add custom validation in the `__post_init__` method of your dataclasses.

5. **Break complex configurations into logical modules**: For very complex configurations, consider splitting your config classes across multiple modules.





## Environment-Specific Configuration

For environment-specific configuration:

```python
import os

ENV = os.environ.get("ENV", "development")

@config_class(file_name=f"app.{ENV}.json")
class AppConfig:
    debug: bool = ENV != "production"
    log_level: str = "DEBUG" if ENV != "production" else "INFO"
    # ...
```

## Best Practices

When working with configuration classes:

1. **Use Meaningful Default Values**: Provide sensible defaults whenever possible

2. **Add Validation Logic**: Use `__post_init__` to validate configuration beyond the type checking offered by Configr

3. **Organize Related Settings**: Group related settings in separate classes

4. **Use Strong Typing**: Leverage Python's type hints for better code quality

5. **Manage Secrets Carefully**: Consider separating sensitive information from regular configuration


## Next Steps

Now that you understand how to work with configuration classes in Configr, you might want to explore:

- [Custom Loaders](custom-loaders.md) to learn how to extend Configr with support for additional file formats