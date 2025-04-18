"""
Configuration management system.

A flexible, type-safe configuration management system that loads structured
configuration data from files and converts it to strongly-typed Python objects.
The system supports multiple file formats, nested configuration structures,
and comprehensive type validation.

Features:
- Strong type validation using Python's type annotations
- Support for JSON and YAML configuration formats (extensible to other formats)
- Automatic conversion to dataclasses with full type checking
- Support for nested configuration structures
- Configurable file paths and naming conventions

Typical usage:
    from config_manager import ConfigBase, config_class

    @config_class(file_name="database")
    class DatabaseConfig:
        host: str
        port: int = 5432
        username: str
        password: str

    # Load configuration from file
    config = ConfigBase.load(DatabaseConfig)

    # Use strongly-typed configuration
    db_connection = connect(
        config.host,
        config.port,
        config.username,
        config.password
    )
"""
