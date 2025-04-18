from configr.utils import to_snake_case


def test_camel_case_to_snake_case():
    """Test converting camel case to snake case."""
    assert to_snake_case("CamelCase") == "camel_case"
    assert to_snake_case("camelCase") == "camel_case"
    assert to_snake_case("CamelCaseString") == "camel_case_string"
    assert to_snake_case("camelCaseString") == "camel_case_string"


def test_already_snake_case():
    """Test that already snake-cased strings remain unchanged."""
    assert to_snake_case("snake_case") == "snake_case"
    assert to_snake_case("snake_case_string") == "snake_case_string"


def test_single_word():
    """Test converting single words."""
    assert to_snake_case("Word") == "word"
    assert to_snake_case("word") == "word"
    assert to_snake_case("WORD") == "word"


def test_empty_string():
    """Test empty string returns empty string."""
    assert to_snake_case("") == ""


def test_single_character():
    """Test single characters."""
    assert to_snake_case("A") == "a"
    assert to_snake_case("a") == "a"


def test_with_numbers():
    """Test strings with numbers."""
    assert to_snake_case("Model3D") == "model3_d"
    assert to_snake_case("Database2Config") == "database2_config"
    assert to_snake_case("API2Service") == "api2_service"


def test_mixed_case_formats():
    """Test strings with mixed case formats."""
    assert to_snake_case("mixed_CaseFormat") == "mixed_case_format"
    assert to_snake_case("API_Config") == "api_config"
    assert to_snake_case("OAuth2_Provider") == "o_auth2_provider"


def test_with_special_characters():
    """Test strings with special characters."""
    assert to_snake_case("Special-Case") == "special_case"
    assert to_snake_case("special.case") == "special_case"
    # Special characters are removed and replaced with _


def test_consecutive_uppercase():
    """Test handling of consecutive uppercase letters."""
    assert to_snake_case("HTTPRequest") == "http_request"
    assert to_snake_case("APIConfig") == "api_config"


def test_class_name_conversion():
    """Test converting class names (the primary use case)."""
    assert to_snake_case("DatabaseConfig") == "database_config"
    assert to_snake_case("APIServiceHandler") == "api_service_handler"
    assert to_snake_case("OAuth2Client") == "o_auth2_client"
