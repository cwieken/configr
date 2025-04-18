"""
Type checking utilities for configuration fields.

This module provides strict type checking for dataclass fields used in
configuration classes. It supports validating basic types, generic types
(List, Dict, Set, Tuple), Union types, and nested type structures.

The module includes:
- FieldTypeChecker class: Utility class for validating that values match their
  expected types according to type annotations without performing type conversion
- Specialized type checking methods for different type structures
- Support for complex nested type validation

Typical usage:
    fields = {f.name: f.type for f in dataclasses.fields(config_class)}
    filtered_data = {k: v for k, v in config_data.items() if k in fields}

    try:
        FieldTypeChecker.check_types(fields, filtered_data)
    except TypeError as exc:
        raise ConfigValidationError(f"Configuration validation failed: {exc}")
"""
from typing import Any, Union, get_args, get_origin


class FieldTypeChecker:
    """
    A utility class for checking if values match their expected types.

    This class provides strict type checking for dataclass fields,
    supporting basic types, generic types (List, Dict, Set, Tuple),
    Union types, and nested type structures.

    It does not perform type conversion.
    """
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
        # Check type of fields
        for field_name, field_type in fields.items():
            value = data.get(field_name)

            # Skip type checking for Any
            if field_type is Any or field_type is any:
                continue

            origin_type = get_origin(field_type)
            if origin_type is not None:
                # Handle other generic types
                cls.__check_generic_types(field_name, field_type, value)
            else:
                # Handle basic types
                cls.__check_basic_types(field_name, field_type, value)

    @classmethod
    def __check_basic_types(cls, field_name: str,
                            field_types: type | tuple[Any, ...], value: any) -> None:
        """
        Check if a value matches a basic (non-generic) type annotation.

        Args:
            field_name: The name of the field being checked.
            field_types: The expected type or tuple of types.
            value: The value to check.

        Raises:
            TypeError: If the value doesn't match the expected type(s).
        """
        if not isinstance(field_types, tuple):
            field_types = (field_types,)

        # Skip check for any
        if any in field_types or Any in field_types:
            return

        # Handle basic types
        # we use non-strict type checking, e.g., an int of 0 or 1
        # is allowed if a bool is required
        if value is not None and not isinstance(value, field_types):
            expected_types = ', '.join(str(expected_type) for
                                       expected_type in field_types)
            raise TypeError(f"Expected {field_name} to be of type "
                            f"{expected_types}, got {type(value)}")

    @classmethod
    def __check_generic_types(cls, field_name: str,
                              field_type: type | tuple[Any, ...], value: any) -> None:
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
        if value is None:
            return  # Skip type checking for None values

        # Check for typing generics (List, Dict, Set, Tuple, etc.)
        origin_type, origin_args = get_origin(field_type), get_args(field_type)
        if origin_type is not None:

            # Skip type checking for Any
            if origin_type is Any or field_type is any:
                return

            # Handle lists, tuples, sets and dictionaries
            if origin_type in (list, tuple, set, dict):
                for i, value_elem in enumerate(value):
                    if origin_type is tuple:
                        # Handle tuple type to check length and types
                        cls.__check_tuple_type(field_name, origin_args, value)

                    if origin_type is dict:
                        # Handle tuple type to check length and types
                        cls.__check_dict_type(field_name, origin_args, value)

                    try:
                        # Handle nested generic types
                        if get_origin(origin_args[0]) is not None:
                            cls.__check_generic_types(
                                field_name, origin_args[0], value_elem)

                        else:
                            cls.__check_basic_types(
                                field_name, origin_args, value_elem)
                    except TypeError as exc:
                        raise TypeError(f"Element {i} of {field_name}: "
                                        f"{exc}") from exc
                return

            elif origin_type is Union:
                cls.__check_union_types(field_name, origin_args, value)

            # Handle other generic types, e.g. Optional[str] or Union[str, int]
            cls.__check_basic_types(field_name, origin_args, value)
            return

    @classmethod
    def __check_tuple_type(cls, field_name: str,
                           field_types: tuple[Any, ...], value: any) -> None:
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
        field_types = cls.convert_ellipsis_to_types(field_types, value)
        if len(value) != len(field_types):
            raise TypeError(f"Expected {field_name} to be of length "
                            f"{len(field_types)}, but is {len(value)}")

        for i, (item, expected_type) in enumerate(zip(
                value, field_types, strict=True)):
            try:
                if get_origin(item) is not None:
                    cls.__check_generic_types(field_name, expected_type, item)
                else:
                    cls.__check_basic_types(field_name, expected_type, item)
            except TypeError as exc:
                raise TypeError(f"Element {i} of {field_name}: {exc}") from exc

    @classmethod
    def __check_dict_type(cls, field_name: str,
                          field_types: tuple[Any, ...], value: any) -> None:
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
        for key, elem_value in value.items():
            key_type, value_type = field_types
            try:
                cls.__check_basic_types(field_name, key_type, key)
            except TypeError as exc:
                raise TypeError(f"Key {key} of {field_name}: {exc}") from exc

            try:
                cls.__check_basic_types(field_name, value_type, elem_value)
            except TypeError as exc:
                raise TypeError(f"Value {elem_value} of {field_name}: "
                                f"{exc}") from exc

    @classmethod
    def __check_union_types(cls, field_name: str,
                            field_types: tuple[Any, ...], value: any) -> None:
        """
        Check if a value matches any of the types in a Union type annotation.

        Args:
            field_name: The name of the field being checked.
            field_types: The tuple of possible types from the Union.
            value: The value to check.

        Raises:
            TypeError: If the value doesn't match any type in the Union.
        """
        found_correct_type = False
        for arg_type in field_types:
            try:
                if get_origin(arg_type) is not None:
                    cls.__check_generic_types(field_name, arg_type, value)
                    found_correct_type = True
                else:
                    cls.__check_basic_types(field_name, arg_type, value)
                    found_correct_type = True

            except TypeError:
                continue

        if not found_correct_type:
            expected_types = ', '.join(str(expected_type) for
                                       expected_type in field_types)
            raise TypeError(f"Value for '{field_name}' doesn't match "
                            f"any type in {expected_types}, got {type(value)}")

    @staticmethod
    def convert_ellipsis_to_types(field_types: tuple[Any, ...],
                                  value: tuple) -> tuple[Any, ...]:
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
        # Find the index of the last valid type before the Ellipsis
        index = field_types.index(Ellipsis) if Ellipsis in field_types else -1

        if index == -1:
            # If there is no Ellipsis, return as is
            return field_types

        # Get the type before the Ellipsis
        previous_type = field_types[index - 1]

        # Replace the Ellipsis with the previous type
        # for the length of elements in the tuple
        new_field_list = field_types[:index] + (previous_type,) * (len(value) - index)

        return new_field_list
