# FieldTypeChecker

The `FieldTypeChecker` is a utility class in Configr that handles type checking for configuration fields. It ensures
that loaded configuration values match their expected types according to the type annotations in your configuration
classes.

## Overview

```python
class FieldTypeChecker:
    """
    A utility class for checking if values match their expected types.

    This class provides strict type checking for dataclass fields,
    supporting basic types, generic types (List, Dict, Set, Tuple),
    Union types, and nested type structures.

    It does not perform type conversion.
    """
```

The `FieldTypeChecker` provides comprehensive type validation, supporting:

1. Basic Python types (str, int, float, bool, etc.)
2. Generic collection types (List, Dict, Set, Tuple)
3. Union and Optional types
4. Nested dataclasses
5. Complex nested structures (e.g., List[Dict[str, Any]])

## Methods

### check_types

```python
@classmethod
def check_types(cls, fields: dict[str, type], data: dict) -> None:
    """
    Check that all values match their expected types as defined in fields.

    Args:
        fields: A dictionary mapping field names to their type annotations.
        data: A dictionary mapping field names to their values.

    Raises:
        TypeError: If any value doesn't match its expected type.
    """
```

#### Parameters

| Parameter | Type              | Description                                    |
|-----------|-------------------|------------------------------------------------|
| `fields`  | `dict[str, type]` | Dictionary mapping field names to their types  |
| `data`    | `dict`            | Dictionary mapping field names to their values |

#### Raises

- `TypeError`: If any value doesn't match its expected type

## Implementation Details

The `FieldTypeChecker` class includes several private helper methods for different types of validation:

### __check_basic_types

```python
@classmethod
def __check_basic_types(cls, field_name: str, field_types: type | tuple[Any, ...], value: any) -> None:
    """
    Check if a value matches a basic (non-generic) type annotation.

    Args:
        field_name: The name of the field being checked.
        field_types: The expected type or tuple of types.
        value: The value to check.

    Raises:
        TypeError: If the value doesn't match the expected type(s).
    """
```

This method checks if a value matches basic (non-generic) types like `str`, `int`, `bool`, etc.

- It accepts single types or tuples of types
- Skips checks for `Any` or `any` types
- Handles `None` values
- Uses `isinstance()` for type checking

### __check_generic_types

```python
@classmethod
def __check_generic_types(cls, field_name: str, field_type: type | tuple[Any, ...], value: any) -> None:
    """
    Check if a value matches a generic type annotation.

    This includes List, Dict, Set, Tuple, Union, etc.

    Args:
        field_name: The name of the field being checked.
        field_type: The expected generic type.
        value: The value to check.

    Raises:
        TypeError: If the value doesn't match the expected generic type structure.
    """
```

This method checks if a value matches generic type annotations like `List[T]`, `Dict[K, V]`, etc.

- Extracts origin type and type arguments using `get_origin()` and `get_args()`
- Handles container types (list, dict, set, tuple)
- Recursively checks nested generic types
- Delegates to specialized checkers for specific containers

### __check_tuple_type

```python
@classmethod
def __check_tuple_type(cls, field_name: str, field_types: tuple[Any, ...], value: any) -> None:
    """
    Check if a value matches a tuple type annotation.

    This includes fixed-size and variable-size tuples.

    Args:
        field_name: The name of the field being checked.
        field_types: The tuple of expected types for each element.
        value: The tuple value to check.

    Raises:
        TypeError: If the tuple doesn't match the expected structure
                   or element types.
    """
```

This method checks if a tuple value matches a tuple type annotation:

- Validates tuple length
- Checks each element against its expected type
- Handles variable-length tuples (with `Ellipsis`)

### __check_dict_type

```python
@classmethod
def __check_dict_type(cls, field_name: str, field_types: tuple[Any, ...], value: any) -> None:
    """
    Check if a value matches a dictionary type annotation.

    This includes checking both its keys and values.

    Args:
        field_name: The name of the field being checked.
        field_types: A tuple containing (key_type, value_type).
        value: The dictionary value to check.

    Raises:
        TypeError: If any key or value in the dictionary doesn't match its
                   expected type.
    """
```

This method checks if a dictionary value matches a dictionary type annotation:

- Validates key types against the expected key type
- Validates value types against the expected value type
- Provides detailed error messages for key or value type mismatches

### __check_union_types

```python
@classmethod
def __check_union_types(cls, field_name: str, field_types: tuple[Any, ...], value: any) -> None:
    """
    Check if a value matches any of the types in a Union type annotation.

    Args:
        field_name: The name of the field being checked.
        field_types: The tuple of possible types from the Union.
        value: The value to check.

    Raises:
        TypeError: If the value doesn't match any type in the Union.
    """
```

This method checks if a value matches any of the types in a Union type annotation:

- Tries each type in the union
- Succeeds if the value matches any of the possible types
- Provides a comprehensive error message if no match is found

### convert_ellipsis_to_types

```python
@staticmethod
def convert_ellipsis_to_types(field_types: tuple[Any, ...], value: tuple) -> tuple[Any, ...]:
    """
    Convert a tuple type with Ellipsis to concrete types.

    This handles variable-length tuples by repeating the type
    before the Ellipsis, e.g. (Tuple[float, int, ...]) becomes
    (float, int, int, int) for a tuple of length 4.

    Args:
        field_types: The tuple of types, potentially containing an Ellipsis.
        value: The actual tuple value being checked.

    Returns:
        A tuple of concrete types matching the length of the value.
    """
```

This method handles variable-length tuple types with Ellipsis (e.g., `Tuple[int, ...]`):

- Identifies the Ellipsis in the type arguments
- Extracts the repeated type (the type before Ellipsis)
- Creates a concrete tuple of types matching the actual tuple's length

## Supported Type Validations

The `FieldTypeChecker` provides validation for:

1. **Basic Types**:
    - `str`, `int`, `float`, `bool`, etc.
    - Any custom type that can be checked with `isinstance()`

2. **Generic Types**:
    - `List[T]`: Lists of any type T
    - `Dict[K, V]`: Dictionaries with keys of type K and values of type V
    - `Set[T]`: Sets of any type T
    - `Tuple[T1, T2, ...]`: Tuples with specific element types

3. **Union Types**:
    - `Union[T1, T2, ...]`: Values that match any of the given types
    - `Optional[T]` (same as `Union[T, None]`): Values of type T or None

4. **Nested Generics**:
    - `List[Dict[str, Any]]`: Lists of dictionaries with string keys
    - `Dict[str, List[int]]`: Dictionaries with string keys and integer list values
    - Any other valid nested generic structure

5. **Special Cases**:
    - `Any`: Accepts any type (type checking is skipped)
    - `Tuple[T, ...]`: Variable-length tuples with elements of type T

## Type Checking Behavior

The `FieldTypeChecker` has several important behaviors to note:

1. **No Type Conversion**: It only checks types and does not attempt to convert values between types.

2. **None Handling**: `None` values are allowed in most cases, especially for optional fields or when the field is part
   of a Union with `None`.

3. **Any Type**: If a field is typed as `Any`, type checking is skipped for that field.

4. **Collection Contents**: For collections like lists, sets, and dictionaries, it recursively checks the contents
   against the expected element types.

5. **Detailed Error Messages**: It provides specific error messages that identify exactly which field and element failed
   validation.

## Examples of Type Checking

### Basic Types

```python
@config_class
class ServerConfig:
    host: str
    port: int
    debug: bool


# Valid configuration
config_data = {
    "host": "localhost",
    "port": 8080,
    "debug": True
}

# Invalid configuration - will raise TypeError
invalid_data = {
    "host": "localhost",
    "port": "8080",  # String instead of int
    "debug": True
}
```

### Generic Types

```python
@config_class
class AppConfig:
    name: str
    version: str
    tags: List[str]
    features: Dict[str, bool]


# Valid configuration
config_data = {
    "name": "MyApp",
    "version": "1.0.0",
    "tags": ["web", "api", "backend"],
    "features": {
        "dark_mode": True,
        "analytics": False
    }
}

# Invalid configuration - will raise TypeError
invalid_data = {
    "name": "MyApp",
    "version": "1.0.0",
    "tags": ["web", "api", 123],  # Number instead of string
    "features": {
        "dark_mode": True,
        "analytics": "no"  # String instead of bool
    }
}
```

### Union and Optional Types

```python
from typing import Union, Optional


@config_class
class LogConfig:
    level: str
    file: Optional[str] = None
    rotation: Union[int, str] = 1024


# Valid configurations
config1 = {
    "level": "INFO",
    "file": "app.log",
    "rotation": 2048  # int
}

config2 = {
    "level": "DEBUG",
    "file": None,  # Optional can be None
    "rotation": "daily"  # Union can be str
}
```

### Nested Structures

```python
from typing import List, Dict


@config_class
class ComplexConfig:
    name: str
    endpoints: List[Dict[str, Union[str, int]]]


# Valid configuration
config_data = {
    "name": "API Service",
    "endpoints": [
        {"path": "/users", "method": "GET", "rate_limit": 100},
        {"path": "/auth", "method": "POST", "rate_limit": 20}
    ]
}
```

## Integration with ConfigBase

The `FieldTypeChecker` is used by `ConfigBase` during configuration loading to ensure type safety:

```python
# In ConfigBase.load:
try:
    FieldTypeChecker.check_types(fields, filtered_data)
except TypeError as exc:
    raise ConfigValidationError(f"Configuration validation failed: {exc}") from exc
```

This integration ensures that all configuration values are properly validated against their expected types before the
configuration class is instantiated.