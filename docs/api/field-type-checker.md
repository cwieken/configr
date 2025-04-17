# FieldTypeChecker

The `FieldTypeChecker` is a utility class in Configr that handles type checking for configuration fields. It ensures that loaded configuration values match their expected types according to the type annotations in your configuration classes.

## Overview

```python
class FieldTypeChecker:
    """
    A utility class for checking if values match their expected types according to type annotations.

    This class provides strict type checking for dataclass fields, supporting basic types,
    generic types (List, Dict, Set, Tuple), Union types, and nested type structures.

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
def check_types(cls, fields: dict[str, Type], data: dict) -> None:
    """
    Check that all values in data match their expected types as defined in fields.

    Args:
        fields: A dictionary mapping field names to their type annotations.
        data: A dictionary mapping field names to their values.

    Raises:
        TypeError: If any value doesn't match its expected type.
    """
```

#### Parameters

| Parameter | Type              | Description                                     |
|-----------|-----------------|-------------------------------------------------|
| `fields`  | `dict[str, Type]` | Dictionary mapping field names to their types   |
| `data`    | `dict`          | Dictionary mapping field names to their values  |

#### Raises

- `TypeError`: If any value doesn't match its expected type


## Implementation Details

The `FieldTypeChecker` class includes several private helper methods:

### __check_basic_types

```python
@classmethod
def __check_basic_types(cls, field_name: str, field_types: Type | tuple[Any, ...], value: any) -> None:
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

This method checks if a value matches basic (non-generic) types.

### __check_generic_types

```python
@classmethod
def __check_generic_types(cls, field_name: str, field_type: Type | tuple[Any, ...], value: any) -> None:
    """
    Check if a value matches a generic type annotation (List, Dict, Set, Tuple, Union, etc.).

    Args:
        field_name: The name of the field being checked.
        field_type: The expected generic type.
        value: The value to check.

    Raises:
        TypeError: If the value doesn't match the expected generic type structure.
    """
```

This method checks if a value matches generic types like List, Dict, Set, Tuple, Union, etc.

### __check_tuple_type

```python
@classmethod
def __check_tuple_type(cls, field_name: str, field_types: tuple[Any, ...], value: any) -> None:
    """
    Check if a value matches a tuple type annotation, including fixed-size and variable-size tuples.

    Args:
        field_name: The name of the field being checked.
        field_types: The tuple of expected types for each element.
        value: The tuple value to check.

    Raises:
        TypeError: If the tuple doesn't match the expected structure or element types.
    """
```

This method checks if a tuple value matches a tuple type annotation, handling both fixed-size and variable-size tuples.

### __check_dict_type

```python
@classmethod
def __check_dict_type(cls, field_name: str, field_types: tuple[Any, ...], value: any) -> None:
    """
    Check if a value matches a dictionary type annotation, including checking key and value types.

    Args:
        field_name: The name of the field being checked.
        field_types: A tuple containing (key_type, value_type).
        value: The dictionary value to check.

    Raises:
        TypeError: If any key or value in the dictionary doesn't match its expected type.
    """
```

This method checks if a dictionary value matches a dictionary type annotation, validating both key and value types.

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
        TypeError: If the value doesn't match any of the types in the Union.
    """
```

This method checks if a value matches any of the types in a Union type annotation, providing support for Union and Optional types.

### convert_ellipsis_to_types

```python
@staticmethod
def convert_ellipsis_to_types(field_types: tuple[Any, ...], value: tuple) -> tuple[Any, ...]:
    """
    Convert a tuple type with Ellipsis (e.g., Tuple[int, ...]) to a tuple of concrete types.

    This handles variable-length tuples by repeating the type before the Ellipsis.

    Args:
        field_types: The tuple of types, potentially containing an Ellipsis.
        value: The actual tuple value being checked.

    Returns:
        A tuple of concrete types matching the length of the value.
    """
```

This method handles variable-length tuple types (like Tuple[int, ...]) by converting them to concrete types for validation.

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

2. **None Handling**: None values are allowed for fields that don't have explicit None in a Union or Optional type.

3. **Instance Checking**: It uses `isinstance()` for type checking, which means subclasses are accepted where their base class is expected.

4. **Union Resolution**: For Union types, it tries each possible type until it finds a match or exhausts all options.

## Integration with ConfigBase

The `FieldTypeChecker` is used by `ConfigBase` during configuration loading to ensure type safety:

```python
# In ConfigBase.load:
try:
    FieldTypeChecker.check_types(fields, filtered_data)
except TypeError as exc:
    raise ConfigValidationError(f"Configuration validation failed: {exc}") from exc
```

If type validation fails, Configr raises a `ConfigValidationError` with details about the specific type mismatch.