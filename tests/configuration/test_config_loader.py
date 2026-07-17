import pytest
from core.configuration.service import get_config, set_config, _config_manager

def test_config_get_section():
    sys_config = get_config("system")
    assert isinstance(sys_config, dict)
    assert sys_config.get("system", {}).get("name") == "Hikmara AI"

def test_config_get_with_key():
    val = get_config("system", "system", {})
    assert val.get("name") == "Hikmara AI"
    assert val.get("offline_mode") is True

def test_config_set_and_get():
    # Store old value
    old_val = get_config("user", "user", {}).get("username")

    # Set temporary config value
    set_config("user", "test_key", "test_value")
    assert get_config("user", "test_key") == "test_value"

    # Clean up / reset
    set_config("user", "test_key", None)
