# Utilities

Configr includes utility functions that support the configuration management functionality. This page documents the core utility functions available in Configr.

## to_snake_case

```python
def to_snake_case(name: str) -> str:
    """
    Convert name to snake case, special chars are replaced with _
    and numbers are kept.
    """
```

The `to_snake_case` function converts a string in camelCase, PascalCase, or other formats to snake_case.

### Parameters

| Parameter | Type  | Description                                |
|-----------|-------|--------------------------------------------|
| `name`    | `str` | The string to convert to snake_case format |

### Returns

A string converted to snake_case format.

### Examples

```python
from configr.utils import to_snake_case

# Converting PascalCase
result = to_snake_case("DatabaseConfig")
print(result)  # "database_config"

# Converting camelCase
result = to_snake_case("databaseConfig")
print(result)  # "database_config"

# With numbers
result = to_snake_case("API123Config")
print(result)  # "api123_config"

# With acronyms
result = to_snake_case("DBConfig")
print(result)  # "db_config"

# With mixed case
result = to_snake_case("JSONAPIConfig")
print(result)  # "json_api_config"
```

### Implementation Details

The function:

1. If the input is a simple lowercase word without special characters, returns it as is
2. Otherwise, uses regular expressions to find:
    - Lowercase letters and numbers together
    - Uppercase letters, optionally followed by uppercase letters, numbers, or lowercase letters
3. Joins these elements with underscores
4. Converts everything to lowercase

The core regular expression pattern is:
```python
re.findall(r'[a-z0-9]+|[A-Z](?:[A-Z0-9]*(?![a-z])|[a-z0-9]*)', name)
```

This pattern matches:

- Groups of lowercase letters and numbers: `[a-z0-9]+`

OR

- An uppercase letter: `[A-Z]` followed by either:
    - Zero or more uppercase letters and numbers not followed by a lowercase letter: `[A-Z0-9]*(?![a-z])`

    OR

    - Zero or more lowercase letters and numbers: `[a-z0-9]*`

## Usage in Configr

The `to_snake_case` function is used internally by Configr in the `config_class` decorator to derive default configuration file names from class names when a specific file name is not provided.

For example, a class named `DatabaseConfig` would, by default, look for a configuration file named `database_config.json` (or other supported extensions).

```python
@config_class  # Will use database_config.json by default
class DatabaseConfig:
    host: str
    port: int
```

This helps maintain a consistent naming convention for configuration files that follows Python's standard style guidelines.