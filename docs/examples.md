# Examples

This page provides practical examples of using Configr in different scenarios. Each example demonstrates key features
and patterns to help you make the most of the library in your projects.

## Basic Configuration

### Simple Application Configuration

This example shows a basic application configuration setup.

```python
# app_config.py
from configr import config_class, ConfigBase


@config_class(file_name="app_settings.json")
class AppConfig:
    app_name: str
    version: str
    debug: bool = False
    log_level: str = "INFO"
    max_connections: int = 100


# Load the configuration
app_config = ConfigBase.load(AppConfig)

# Use the configuration
print(f"Starting {app_config.app_name} v{app_config.version}")
print(f"Debug mode: {app_config.debug}")
print(f"Log level: {app_config.log_level}")
```

**Configuration file (`_config/app_settings.json`):**

```json
{
  "app_name": "MyApp",
  "version": "1.0.0",
  "debug": true,
  "log_level": "DEBUG"
}
```

## Nested Configuration

### Database and Logging Configuration

This example demonstrates nested configuration structures.

```python
# config.py
from configr import config_class, ConfigBase
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    username: str
    password: str
    database: str
    host: str = "localhost"
    port: int = 5432
    ssl_mode: str = "prefer"

    def get_connection_string(self):
        """Generate a database connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode={self.ssl_mode}"


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = None
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_size: int = 10485760  # 10MB
    backup_count: int = 5


@config_class(file_name="server_config.json")
class ServerConfig:
    name: str
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = None

    def __post_init__(self):
        # Validation
        if self.port < 1024 or self.port > 65535:
            raise ValueError(f"Invalid port: {self.port}")
        if self.workers < 1:
            raise ValueError(f"Workers must be at least 1, got {self.workers}")


# main.py
from config import ServerConfig, ConfigBase

server_config = ConfigBase.load(ServerConfig)

# Access nested configuration
db_conn_string = server_config.database.get_connection_string()

# If server_config.logging is None, it will try to create an instance of LoggingConfig
# with default values if possible, so log level is set to INFO in that case.
log_level = server_config.logging.level

print(f"Server: {server_config.name} running on {server_config.host}:{server_config.port}")
print(f"Database connection: {db_conn_string}")
print(f"Log level: {log_level}")
```

**Configuration file (`_config/server_config.json`):**

```json
{
  "name": "ProductionServer",
  "port": 8080,
  "workers": 8,
  "database": {
    "host": "db.example.com",
    "username": "admin",
    "password": "secure_password",
    "database": "production_db",
    "ssl_mode": "require"
  },
  "logging": {
    "level": "WARNING",
    "file": "/var/log/myapp.log",
    "backup_count": 10
  }
}
```

## Multiple Configuration Files

### Separate Configs for different Components

This example shows how to work with multiple configuration files for different components of your application.

```python
# configs.py
from configr import config_class, ConfigBase


@config_class(file_name="database.json")
class DatabaseConfig:
    username: str
    password: str
    database: str
    host: str = 'localhost'
    port: int = 5432
    max_connections: int = 100


@config_class(file_name="redis.json")
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = None
    socket_timeout: int = 5


@config_class(file_name="app.json")
class AppConfig:
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str
    allowed_hosts: list[str] = None


# Access specific configurations
db_config = ConfigBase.load(DatabaseConfig)
redis_config = ConfigBase.load(RedisConfig)
app_config = ConfigBase.load(AppConfig)

print(f"Database: {db_config.host}:{db_config.port}/{db_config.database}")
print(f"Redis: {redis_config.host}:{redis_config.port}")
print(f"App debug mode: {app_config.debug}")
```

**Configuration files:**

`_config/database.json`:

```json
{
  "host": "db.example.com",
  "username": "admin",
  "password": "secure_password",
  "database": "myapp_db",
  "max_connections": 50
}
```

`_config/redis.json`:

```json
{
  "host": "redis.example.com",
  "password": "redis_password"
}
```

`_config/app.json`:

```json
{
  "debug": false,
  "log_level": "WARNING",
  "secret_key": "very-secret-key-123",
  "allowed_hosts": [
    "example.com",
    "www.example.com"
  ]
}
```

## Environment-Specific Configuration

### Dynamic Configuration Based on Environment

This example demonstrates loading different configurations based on the environment.

```python
# config.py
import os
from configr import config_class, ConfigBase

# Determine environment
ENV = os.environ.get("APP_ENV", "development")


@config_class(file_name=f"app.{ENV}.json")
class AppConfig:
    debug: bool = ENV != "production"
    log_level: str = "DEBUG" if ENV != "production" else "INFO"
    database_url: str
    redis_url: str = None
    secret_key: str
    allowed_hosts: list[str] = None


# app.py
from config import AppConfig, ENV
from configr import ConfigBase

config = ConfigBase.load(AppConfig)
print(f"Running in {ENV} environment")
print(f"Debug mode: {config.debug}")
print(f"Log level: {config.log_level}")
print(f"Database URL: {config.database_url}")
```

**Configuration files:**

`_config/app.development.json`:

```json
{
  "debug": true,
  "log_level": "DEBUG",
  "database_url": "postgresql://dev:dev@localhost/dev_db",
  "secret_key": "dev-secret-key",
  "allowed_hosts": [
    "localhost",
    "127.0.0.1"
  ]
}
```

`_config/app.production.json`:

```json
{
  "debug": false,
  "log_level": "WARNING",
  "database_url": "postgresql://user:pass@db.example.com/prod_db",
  "redis_url": "redis://redis.example.com:6379/0",
  "secret_key": "production-secret-key-very-secure",
  "allowed_hosts": [
    "example.com",
    "www.example.com",
    "api.example.com"
  ]
}
```

## List of Dataclasses

### Service Configuration with Multiple Endpoints

This example shows how to configure a list of service endpoints.

```python
# services_config.py
from configr import config_class, ConfigBase
from dataclasses import dataclass


@dataclass
class ServiceEndpoint:
    name: str
    url: str
    timeout: int = 30
    retries: int = 3
    api_key: str = None


@config_class(file_name="services.json")
class ServicesConfig:
    base_timeout: int = 60
    default_retries: int = 5
    endpoints: list[ServiceEndpoint]

    def get_endpoint(self, name):
        """Find an endpoint by name."""
        for endpoint in self.endpoints:
            if endpoint.name == name:
                return endpoint
        return None


# Load the configuration
services_config = ConfigBase.load(ServicesConfig)

# Get a specific endpoint
auth_service = services_config.get_endpoint("authentication")
if auth_service:
    print(f"Auth service URL: {auth_service.url}")
    print(f"Auth service timeout: {auth_service.timeout}s")

# Iterate through all endpoints
print("Available services:")
for endpoint in services_config.endpoints:
    print(f"- {endpoint.name}: {endpoint.url}")
```

**Configuration file (`_config/services.json`):**

```json
{
  "base_timeout": 30,
  "endpoints": [
    {
      "name": "authentication",
      "url": "https://auth.example.com/api",
      "timeout": 10,
      "api_key": "auth-api-key-123"
    },
    {
      "name": "storage",
      "url": "https://storage.example.com/api",
      "timeout": 60,
      "retries": 5
    },
    {
      "name": "analytics",
      "url": "https://analytics.example.com/api",
      "api_key": "analytics-api-key-456"
    }
  ]
}
```

## Custom Loaders

### TOML Configuration loader

This example demonstrates creating, registering and using a custom loader for TOML files.

```python
# toml_loader.py
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


# config.py
from configr import config_class, ConfigBase
from toml_loader import TOMLConfigLoader

# Register the custom loader
ConfigBase.add_loader(TOMLConfigLoader)


# Now you can use TOML files with your config classes
@config_class(file_name="app_config.toml")
class AppConfig:
    name: str
    version: str
    authors: list[str]
    debug: bool = False

    class Dependencies:
        python: str
        requests: str

    dependencies: Dependencies


# Load TOML configuration
app_config = ConfigBase.load(AppConfig)
print(f"App: {app_config.name} v{app_config.version}")
print(f"Authors: {', '.join(app_config.authors)}")
print(f"Python version: {app_config.dependencies.python}")
```

**Configuration file (`_config/app_config.toml`):**

```toml
name = "MyTOMLApp"
version = "0.1.0"
authors = ["Jane Doe", "John Smith"]
debug = true

[dependencies]
python = ">=3.9"
requests = "^2.28.0"
```

## Error Handling

### Robust Configuration Loading

This example shows how to handle various configuration errors gracefully.

```python
# config.py
from configr import config_class, ConfigBase, ConfigFileNotFoundError, ConfigValidationError


@config_class(file_name="app_settings.json")
class AppSettings:
    debug: bool = False
    log_level: str = "INFO"
    port: int = 8000

    def __post_init__(self):
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self.log_level}. Must be one of {valid_log_levels}")

        if self.port < 1024 or self.port > 65535:
            raise ValueError(f"Invalid port: {self.port}. Must be between 1024 and 65535")


def load_settings():
    """Load settings with robust error handling."""
    try:
        return ConfigBase.load(AppSettings)
    except ConfigFileNotFoundError as e:
        print(f"Configuration file not found: {e}")
        print("Using default settings")
        return AppSettings()
    except ConfigValidationError as e:
        print(f"Configuration validation failed: {e}")
        print("Please check your configuration file format and types")
        raise
    except ValueError as e:
        print(f"Invalid configuration value: {e}")
        print("Please check your configuration settings")
        raise
    except Exception as e:
        print(f"Unexpected error loading configuration: {e}")
        print("Using default settings as fallback")
        return AppSettings()


# app.py
from config import load_settings

# Load settings with error handling
settings = load_settings()

# Use the settings
print(f"Starting server on port {settings.port}")
print(f"Debug mode: {settings.debug}")
print(f"Log level: {settings.log_level}")
```

## Web Application Example

### Flask Web App Configuration

This example demonstrates using Configr with a Flask web application.

```python
# config.py
import os
from configr import config_class, ConfigBase, ConfigFileNotFoundError
from dataclasses import dataclass
from typing import Any

# Determine environment
ENV = os.environ.get("FLASK_ENV", "development")


@dataclass
class DatabaseConfig:
    url: str
    pool_size: int = 10
    pool_recycle: int = 3600
    pool_timeout: int = 30


@dataclass
class CacheConfig:
    type: str = "redis"
    url: str = "redis://localhost:6379/0"
    timeout: int = 300


@config_class(file_name=f"flask_app.{ENV}.json")
class FlaskConfig:
    # Flask settings
    secret_key: str
    debug: bool = ENV != "production"
    testing: bool = ENV == "testing"
    host: str = "127.0.0.1"
    port: int = 5000

    # Database settings
    database: DatabaseConfig = None

    # Cache settings
    cache: CacheConfig = None

    # CORS settings
    cors_origins: list[str] = None

    # Other settings
    upload_folder: str = "/tmp/uploads"
    max_content_length: int = 16 * 1024 * 1024  # 16 MB

    # Custom app settings
    app_name: str = "Flask App"
    admin_emails: list[str] = None

    def to_flask_config(self) -> dict[str, Any]:
        """Convert to a dictionary for Flask configuration."""
        # Extract top-level fields first
        config_dict = {
            "SECRET_KEY": self.secret_key,
            "DEBUG": self.debug,
            "TESTING": self.testing,
            "MAX_CONTENT_LENGTH": self.max_content_length,
            "UPLOAD_FOLDER": self.upload_folder,
            "APP_NAME": self.app_name,
            "ADMIN_EMAILS": self.admin_emails or []
        }

        # Add database settings
        if self.database:
            config_dict["SQLALCHEMY_DATABASE_URI"] = self.database.url
            config_dict["SQLALCHEMY_POOL_SIZE"] = self.database.pool_size
            config_dict["SQLALCHEMY_POOL_RECYCLE"] = self.database.pool_recycle
            config_dict["SQLALCHEMY_POOL_TIMEOUT"] = self.database.pool_timeout
            config_dict["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        # Add cache settings if present
        if self.cache:
            if self.cache.type == "redis":
                config_dict["CACHE_TYPE"] = "RedisCache"
                config_dict["CACHE_REDIS_URL"] = self.cache.url
            else:
                config_dict["CACHE_TYPE"] = self.cache.type
            config_dict["CACHE_DEFAULT_TIMEOUT"] = self.cache.timeout

        # Add CORS settings if present
        if self.cors_origins:
            config_dict["CORS_ORIGINS"] = self.cors_origins

        return config_dict


def get_flask_config():
    """Load and return Flask configuration."""
    try:
        config = ConfigBase.load(FlaskConfig)
        return config
    except ConfigFileNotFoundError:
        print(f"Configuration file for {ENV} environment not found.")
        print("Using default configuration (this is not recommended for production)")

        # Default development config
        if ENV == "development":
            return FlaskConfig(
                secret_key="dev-secret-key",
                database=DatabaseConfig(url="sqlite:///dev.db"),
                admin_emails=["admin@example.com"]
            )
        # Default testing config
        elif ENV == "testing":
            return FlaskConfig(
                secret_key="test-secret-key",
                testing=True,
                database=DatabaseConfig(url="sqlite:///:memory:")
            )
        # For production, do not use defaults
        else:
            raise


# app.py
from flask import Flask
from config import get_flask_config

# Load configuration
config = get_flask_config()

# Create Flask app
app = Flask(__name__)
app.config.update(config.to_flask_config())


@app.route('/')
def index():
    return f"Welcome to {app.config['APP_NAME']}!"


if __name__ == '__main__':
    app.run(host=config.host, port=config.port)
```

**Configuration file (`_config/flask_app.development.json`):**

```json
{
  "secret_key": "dev-secret-key-123",
  "debug": true,
  "port": 5000,
  "database": {
    "url": "sqlite:///dev.db",
    "pool_size": 5
  },
  "cache": {
    "type": "redis",
    "url": "redis://localhost:6379/0"
  },
  "cors_origins": [
    "http://localhost:3000",
    "http://localhost:8080"
  ],
  "app_name": "My Flask App (Dev)",
  "admin_emails": [
    "admin@example.com",
    "dev@example.com"
  ]
}
```

## Advanced Features

### Configuration with immutable (frozen) Dataclasses

This example demonstrates using frozen dataclasses for immutable configuration.

```python
# config.py
from configr import config_class, ConfigBase
from dataclasses import dataclass, field, FrozenInstanceError
from typing import Optional


@dataclass(frozen=True)
class LoggingConfig:
    level: str
    file: Optional[str] = None
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass(frozen=True)
class SecurityConfig:
    secret_key: str
    token_expiration: int = 3600  # seconds
    allowed_hosts: list[str] = field(default_factory=list)
    cors_origins: list[str] = field(default_factory=list)


@config_class(file_name="immutable_config.json")
@dataclass(frozen=True)
class AppConfig:
    name: str
    version: str
    debug: bool = False
    logging: LoggingConfig = None
    security: SecurityConfig = None
    feature_flags: dict[str, bool] = field(default_factory=dict)

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature flag is enabled."""
        return self.feature_flags.get(feature_name, False)


# Load the immutable configuration
try:
    config = ConfigBase.load(AppConfig)

    # Using the configuration
    print(f"App: {config.name} v{config.version}")
    print(f"Debug mode: {config.debug}")

    if config.logging:
        print(f"Log level: {config.logging.level}")

    if config.security:
        print(f"Token expiration: {config.security.token_expiration}s")

    # Check feature flags
    print("Feature flags:")
    for feature, enabled in config.feature_flags.items():
        print(f"- {feature}: {'enabled' if enabled else 'disabled'}")

    # Attempt to modify (will raise an error)
    try:
        config.debug = True  # This will raise FrozenInstanceError
    except FrozenInstanceError as e:
        print(f"Cannot modify immutable config: {e}")

except Exception as e:
    print(f"Error loading configuration: {e}")
```

**Configuration file (`_config/immutable_config.json`):**

```json
{
  "name": "ImmutableApp",
  "version": "1.2.0",
  "debug": false,
  "logging": {
    "level": "INFO",
    "file": "/var/log/app.log"
  },
  "security": {
    "secret_key": "very-secret-key-123",
    "token_expiration": 7200,
    "allowed_hosts": [
      "example.com",
      "api.example.com"
    ],
    "cors_origins": [
      "https://app.example.com"
    ]
  },
  "feature_flags": {
    "new_ui": true,
    "advanced_analytics": false,
    "experimental_api": false
  }
}
```