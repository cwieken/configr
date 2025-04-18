"""
Utility functions for string manipulation and other common operations.

This module provides helper functions that are used across the configuration
management system, such as string case conversion utilities that help with
naming conventions and file path generation.

The module includes:
- to_snake_case: Converts strings from various formats (CamelCase, PascalCase)
  to snake_case, preserving numbers and handling special characters

Typical usage:
    # Convert class name to file name
    file_name = to_snake_case("DatabaseConfig")  # "database_config"

    # Convert mixed-case identifier
    field_name = to_snake_case("maxConnections")  # "max_connections"
"""
import re


def to_snake_case(name: str) -> str:
    """
    Convert name to snake case.

    Special chars are replaced with _and numbers are kept.

    Examples:
        - "TestName" -> "test_name"
        - "TestName123" -> "test_name123"
        - "TestName123_TestName456" -> "test_name123_test_name456"
        - "ABCTestName" -> "abc_test_name"

    Args:
        name: The name/str that should be converted to snake case

    Returns:
        The snake cased name as string
    """
    # If only one lower case word without special char, return it
    if not any(c.isupper() for c in name) and not any(not c.isalnum() for c in name):
        return name.lower()

    elements = re.findall(r'[a-z0-9]+|[A-Z](?:[A-Z0-9]*(?![a-z])|[a-z0-9]*)', name)
    return '_'.join(element.lower() for element in elements)
