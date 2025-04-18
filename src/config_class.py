import dataclasses

from .utils import to_snake_case


def config_class(cls=None, *, file_name: str = None):
    """
    Decorator to mark a class as a configuration class.
    This allows specifying a custom file name for the configuration.

    Usage:
        @config_class(file_name="database.json")
        class DatabaseConfig:
            host: str
            port: int = 5432
    """

    def wrapper(cls):
        # Mark as dataclass if not already, that way @dataclass does not need to be used
        if not dataclasses.is_dataclass(cls):
            cls = dataclasses.dataclass(cls)

        # Add file_name as a class variable
        if file_name is not None:
            cls._config_file_name = file_name

        elif not hasattr(cls, '_config_file_name'):
            # Default to class name in snake_case
            cls._config_file_name = to_snake_case(cls.__name__)

        return cls

    # Handle both @config_class and @config_class(file_name="...")
    if cls is None:
        return wrapper
    return wrapper(cls)
