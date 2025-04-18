import dataclasses
import json
import tempfile
from pathlib import Path
from typing import Any, Optional, Union

import pytest

from configr.base import ConfigBase
from configr.exceptions import ConfigValidationError


@dataclasses.dataclass
class ConfigClassTypeTest:
    """Test config class with various typed fields."""
    _config_file_name = "test_config.json"

    # Basic types
    int_field: int
    float_field: float
    str_field: str
    bool_field: bool

    # Union types
    union_int_str: Union[int, str]

    # Collection types
    list_of_ints: list[int]
    dict_of_str_int: dict[str, int]

    # Set type
    set_of_strs: set[str]

    # Tuple types - fixed size and variable size
    tuple_fixed: tuple[int, str, bool]
    tuple_variable: tuple[int, ...]

    # Any type
    any_field: Any

    # Nested collections
    list_of_dicts: list[dict[str, int]]
    list_of_list: list[list[float]]

    # Optional types
    optional_int: Optional[int] = None
    optional_str: Optional[str] = None

    def __post_init__(self):
        """ Convert JSON types to Python types after loading. """
        # JSON has no sets, so we use a list and fix it here
        if isinstance(self.set_of_strs, list):
            self.set_of_strs = set(self.set_of_strs)
        # JSON has no tuples, so we use a list and fix it here
        if isinstance(self.tuple_fixed, list):
            self.tuple_fixed = tuple(self.tuple_fixed)
        # Variable size tuple, converted to tuple here
        if isinstance(self.tuple_variable, list):
            self.tuple_variable = tuple(self.tuple_variable)


@pytest.fixture
def config_dir():
    """Fixture to create and clean up a temporary config directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        ConfigBase.set_config_dir(temp_dir)
        yield temp_dir


def create_config_file(config_dir, data):
    """Helper to create a config file with the given data."""
    config_path = Path(config_dir) / ConfigClassTypeTest._config_file_name
    with open(config_path, 'w') as f:
        json.dump(data, f)


def test_valid_types(config_dir):
    """Test with all valid types."""
    config_data = {
        "int_field": 42,
        "float_field": 3.14,
        "str_field": "hello",
        "bool_field": True,
        "optional_int": 10,
        "optional_str": "optional",
        "union_int_str": 5,
        "list_of_ints": [1, 2, 3],
        "dict_of_str_int": {"a": 1, "b": 2},
        "set_of_strs": ["apple", "banana", "cherry"],
        "tuple_fixed": [1, "text", True],
        "tuple_variable": [1, 2, 3, 4],
        "any_field": {"complex": ["nested", "structure"]},
        "list_of_dicts": [{"x": 1}, {"y": 2}],
        "list_of_list": [[1.0, 2.0], [3.0, 4.0]]
    }
    create_config_file(config_dir, config_data)

    # This should not raise any exceptions
    config = ConfigBase.load(ConfigClassTypeTest)

    # Verify the values
    assert config.int_field == 42
    assert config.float_field == 3.14
    assert config.str_field == "hello"
    assert config.bool_field is True
    assert config.optional_int == 10
    assert config.optional_str == "optional"
    assert config.union_int_str == 5
    assert config.list_of_ints == [1, 2, 3]
    assert config.dict_of_str_int == {"a": 1, "b": 2}
    assert isinstance(config.set_of_strs, set)
    assert config.set_of_strs == {"apple", "banana", "cherry"}
    assert isinstance(config.tuple_fixed, tuple)
    assert config.tuple_fixed == (1, "text", True)
    assert isinstance(config.tuple_variable, tuple)
    assert config.tuple_variable == (1, 2, 3, 4)
    assert config.any_field == {"complex": ["nested", "structure"]}
    assert config.list_of_dicts == [{"x": 1}, {"y": 2}]
    assert config.list_of_list == [[1.0, 2.0], [3.0, 4.0]]


def test_optional_none_values(config_dir):
    """Test with None values for optional fields."""
    config_data = {
        "int_field": 42,
        "float_field": 3.14,
        "str_field": "hello",
        "bool_field": True,
        "optional_int": None,
        "optional_str": None,
        "union_int_str": 5,
        "list_of_ints": [1, 2, 3],
        "dict_of_str_int": {"a": 1, "b": 2},
        "set_of_strs": ["apple", "banana"],
        "tuple_fixed": [1, "text", True],
        "tuple_variable": [1, 2, 3],
        "any_field": None,  # Any can be None
        "list_of_dicts": [{"x": 1}, {"y": 2}],
        "list_of_list": [[1.0, 2.0], [3.0, 4.0]]
    }
    create_config_file(config_dir, config_data)

    # This should not raise any exceptions
    config = ConfigBase.load(ConfigClassTypeTest)

    assert config.optional_int is None
    assert config.optional_str is None
    assert config.any_field is None


def test_union_types_int(config_dir):
    """Test union types with int value."""
    config_data = {
        "int_field": 42,
        "float_field": 3.14,
        "str_field": "hello",
        "bool_field": True,
        "union_int_str": 5,  # Using int
        "list_of_ints": [1, 2, 3],
        "dict_of_str_int": {"a": 1, "b": 2},
        "set_of_strs": ["apple", "banana"],
        "tuple_fixed": [1, "text", True],
        "tuple_variable": [1, 2, 3],
        "any_field": "anything",
        "list_of_dicts": [{"x": 1}, {"y": 2}],
        "list_of_list": [[1.0, 2.0], [3.0, 4.0]]
    }
    create_config_file(config_dir, config_data)

    # This should not raise any exceptions
    config = ConfigBase.load(ConfigClassTypeTest)

    assert config.union_int_str == 5
    assert isinstance(config.union_int_str, int)


def test_union_types_str(config_dir):
    """Test union types with string value."""
    config_data = {
        "int_field": 42,
        "float_field": 3.14,
        "str_field": "hello",
        "bool_field": True,
        "union_int_str": "test",  # Using string
        "list_of_ints": [1, 2, 3],
        "dict_of_str_int": {"a": 1, "b": 2},
        "set_of_strs": ["apple", "banana"],
        "tuple_fixed": [1, "text", True],
        "tuple_variable": [1, 2, 3],
        "any_field": "anything",
        "list_of_dicts": [{"x": 1}, {"y": 2}],
        "list_of_list": [[1.0, 2.0], [3.0, 4.0]]
    }
    create_config_file(config_dir, config_data)

    # This should not raise any exceptions
    config = ConfigBase.load(ConfigClassTypeTest)

    assert config.union_int_str == "test"
    assert isinstance(config.union_int_str, str)


def test_any_field_types(config_dir):
    """Test Any field with different types."""
    # Test with various types for the Any field
    for test_value in [
        42,  # int
        3.14,  # float
        "string",  # str
        True,  # bool
        [1, 2, 3],  # list
        {"key": "value"},  # dict
        None,  # None
    ]:
        config_data = {
            "int_field": 42,
            "float_field": 3.14,
            "str_field": "hello",
            "bool_field": True,
            "union_int_str": 5,
            "list_of_ints": [1, 2, 3],
            "dict_of_str_int": {"a": 1, "b": 2},
            "set_of_strs": ["apple", "banana"],
            "tuple_fixed": [1, "text", True],
            "tuple_variable": [1, 2, 3],
            "any_field": test_value,  # Varies in each iteration
            "list_of_dicts": [{"x": 1}, {"y": 2}],
            "list_of_list": [[1.0, 2.0], [3.0, 4.0]]
        }
        create_config_file(config_dir, config_data)

        # This should not raise any exceptions
        config = ConfigBase.load(ConfigClassTypeTest)
        assert config.any_field == test_value


def test_union_wrong_type(config_dir):
    """Test wrong type for union field."""
    config_data = {
        "int_field": 42,
        "float_field": 3.14,
        "str_field": "hello",
        "bool_field": True,
        "union_int_str": 2.5,  # Using float instead of int or str
        "list_of_ints": [1, 2, 3],
        "dict_of_str_int": {"a": 1, "b": 2},
        "set_of_strs": ["apple", "banana", "cherry"],
        "tuple_fixed": [1, "text", True],
        "tuple_variable": [1, 2, 3],
        "any_field": "anything",
        "list_of_dicts": [{"x": 1}, {"y": 2}],
        "list_of_list": [[1.0, 2.0], [3.0, 4.0]]
    }
    create_config_file(config_dir, config_data)

    # This is expected to raise a ConfigValidationError
    with pytest.raises(ConfigValidationError) as exc_info:
        ConfigBase.load(ConfigClassTypeTest)

    # Check if the exception message matches the expected message
    assert str(exc_info.value) == ("Configuration validation failed: Value "
                                   "for 'union_int_str' doesn't match any "
                                   "type in <class 'int'>, <class 'str'>, "
                                   "got <class 'float'>")


def test_list_wrong_type(config_dir):
    """Test wrong type for list field."""
    config_data = {
        "int_field": 42,
        "float_field": 3.14,
        "str_field": "hello",
        "bool_field": True,
        "union_int_str": 5,
        "list_of_ints": [1, 2, 3.0],  # Using a float instead of int
        "dict_of_str_int": {"a": 1, "b": 2},
        "set_of_strs": ["apple", "banana", "cherry"],
        "tuple_fixed": [1, "text", True],
        "tuple_variable": [1, 2, 3],
        "any_field": "anything",
        "list_of_dicts": [{"x": 1}, {"y": 2}],
        "list_of_list": [[1.0, 2.0], [3.0, 4.0]]
    }
    create_config_file(config_dir, config_data)

    # This is expected to raise a ConfigValidationError
    with pytest.raises(ConfigValidationError) as exc_info:
        ConfigBase.load(ConfigClassTypeTest)

    # Check if the exception message matches the expected message
    assert str(
        exc_info.value) == ("Configuration validation failed: "
                            "Element 2 of list_of_ints: Expected list_of_ints "
                            "to be of type <class 'int'>, got <class 'float'>")


def test_dict_wrong_value_type(config_dir):
    """Test wrong value type for dict field."""
    config_data = {
        "int_field": 42,
        "float_field": 3.14,
        "str_field": "hello",
        "bool_field": True,
        "union_int_str": 5,
        "list_of_ints": [1, 2, 3],
        # Using a str instead of int as value
        "dict_of_str_int": {"a": "a", "b": 2},
        "set_of_strs": ["apple", "banana", "cherry"],
        "tuple_fixed": [1, "text", True],
        "tuple_variable": [1, 2, 3],
        "any_field": "anything",
        "list_of_dicts": [{"x": 1}, {"y": 2}],
        "list_of_list": [[1.0, 2.0], [3.0, 4.0]]
    }
    create_config_file(config_dir, config_data)

    # This is expected to raise a ConfigValidationError
    with pytest.raises(ConfigValidationError) as exc_info:
        ConfigBase.load(ConfigClassTypeTest)

    # Check if the exception message matches the expected message
    assert str(
        exc_info.value) == ("Configuration validation failed: "
                            "Value a of dict_of_str_int: Expected "
                            "dict_of_str_int to be of type <class 'int'>, "
                            "got <class 'str'>")


def test_list_of_dict_wrong_type(config_dir):
    """Test wrong value type for dict field."""
    config_data = {
        "int_field": 42,
        "float_field": 3.14,
        "str_field": "hello",
        "bool_field": True,
        "union_int_str": 5,
        "list_of_ints": [1, 2, 3],
        "dict_of_str_int": {"a": 1, "b": 2},
        "set_of_strs": ["apple", "banana", "cherry"],
        "tuple_fixed": [1, "text", True],
        "tuple_variable": [1, 2, 3],
        "any_field": "anything",
        "list_of_dicts": [{"x": "1"}, {"y": 2}],  # Using a str instead of int as value
        "list_of_list": [[1.0, 2.0], [3.0, 4.0]]
    }
    create_config_file(config_dir, config_data)

    # This is expected to raise a ConfigValidationError
    with pytest.raises(ConfigValidationError) as exc_info:
        ConfigBase.load(ConfigClassTypeTest)

    # Check if the exception message matches the expected message
    assert str(
        exc_info.value) == ("Configuration validation failed: "
                            "Element 0 of list_of_dicts: Value 1 of "
                            "list_of_dicts: Expected list_of_dicts to be of "
                            "type <class 'int'>, got <class 'str'>")


def test_list_of_list_wrong_type(config_dir):
    """Test wrong list value type for list of list field."""
    config_data = {
        "int_field": 42,
        "float_field": 3.14,
        "str_field": "hello",
        "bool_field": True,
        "union_int_str": 5,
        "list_of_ints": [1, 2, 3],
        "dict_of_str_int": {"a": 1, "b": 2},
        "set_of_strs": ["apple", "banana", "cherry"],
        "tuple_fixed": [1, "text", True],
        "tuple_variable": [1, 2, 3],
        "any_field": "anything",
        "list_of_dicts": [{"x": 1}, {"y": 2}],
        # Using an int instead of float as value
        "list_of_list": [[1.0, 2.0], [1, 4.0]]
    }
    create_config_file(config_dir, config_data)

    # This is expected to raise a ConfigValidationError
    with pytest.raises(ConfigValidationError) as exc_info:
        ConfigBase.load(ConfigClassTypeTest)

    # Check if the exception message matches the expected message
    assert str(
        exc_info.value) == ("Configuration validation failed: Element 1 of "
                            "list_of_list: Element 0 of list_of_list: "
                            "Expected list_of_list to be of type "
                            "<class 'float'>, got <class 'int'>")


def test_set_wrong_type(config_dir):
    """Test wrong type for set field."""
    config_data = {
        "int_field": 42,
        "float_field": 3.14,
        "str_field": "hello",
        "bool_field": True,
        "union_int_str": 5,
        "list_of_ints": [1, 2, 3],
        "dict_of_str_int": {"a": 1, "b": 2},
        "set_of_strs": [1, 2, 3],  # Should be strings, not ints
        "tuple_fixed": [1, "text", True],
        "tuple_variable": [1, 2, 3],
        "any_field": "anything",
        "list_of_dicts": [{"x": 1}, {"y": 2}],
        "list_of_list": [[1.0, 2.0], [3.0, 4.0]]
    }
    create_config_file(config_dir, config_data)

    # This is expected to raise a ConfigValidationError
    with pytest.raises(ConfigValidationError) as exc_info:
        ConfigBase.load(ConfigClassTypeTest)

    # Check if the exception message matches the expected message
    assert str(
        exc_info.value) == ("Configuration validation failed: Element 0 of "
                            "set_of_strs: Expected set_of_strs to be of type "
                            "<class 'str'>, got <class 'int'>")


def test_tuple_fixed_length_wrong_type(config_dir):
    """Test tuple with incorrect type."""
    config_data = {
        "int_field": 42,
        "float_field": 3.14,
        "str_field": "hello",
        "bool_field": True,
        "union_int_str": 5,
        "list_of_ints": [1, 2, 3],
        "dict_of_str_int": {"a": 1, "b": 2},
        "set_of_strs": ["apple", "banana"],
        "tuple_fixed": [1, "text", 1],  # Should be int, str, bool
        "tuple_variable": [1, 2, 3],
        "any_field": "anything",
        "list_of_dicts": [{"x": 1}, {"y": 2}],
        "list_of_list": [[1.0, 2.0], [3.0, 4.0]]
    }
    create_config_file(config_dir, config_data)

    with pytest.raises(ConfigValidationError) as exc_info:
        ConfigBase.load(ConfigClassTypeTest)

    # Check if the exception message matches the expected message
    assert str(
        exc_info.value) == ("Configuration validation failed: Element 2 of "
                            "tuple_fixed: Expected tuple_fixed to be of type "
                            "<class 'bool'>, got <class 'int'>")


def test_tuple_fixed_incorrect_length(config_dir):
    """Test tuple with incorrect length."""
    config_data = {
        "int_field": 42,
        "float_field": 3.14,
        "str_field": "hello",
        "bool_field": True,
        "union_int_str": 5,
        "list_of_ints": [1, 2, 3],
        "dict_of_str_int": {"a": 1, "b": 2},
        "set_of_strs": ["apple", "banana"],
        "tuple_fixed": [1, "text"],  # Missing the boolean element
        "tuple_variable": [1, 2, 3],
        "any_field": "anything",
        "list_of_dicts": [{"x": 1}, {"y": 2}],
        "list_of_list": [[1.0, 2.0], [3.0, 4.0]]
    }
    create_config_file(config_dir, config_data)

    with pytest.raises(ConfigValidationError) as exc_info:
        ConfigBase.load(ConfigClassTypeTest)

    # Check if the exception message matches the expected message
    assert str(exc_info.value) == ("Configuration validation failed: "
                                   "Expected tuple_fixed to be of length 3, but is 2")
