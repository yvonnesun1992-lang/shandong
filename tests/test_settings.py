from __future__ import annotations

from pathlib import Path

import pytest

from src.config.settings import (
    DEFAULT_SETTINGS,
    get_setting,
    load_settings,
    reset_settings,
    save_settings,
    update_setting,
    validate_settings,
)


def settings_path(tmp_path: Path) -> Path:
    return tmp_path / "config" / "settings.json"


def test_load_settings_creates_default_file(tmp_path):
    path = settings_path(tmp_path)

    settings = load_settings(path)

    assert path.exists()
    assert settings["cache"]["enabled"] is True
    assert settings["dashboard"]["default_market"] == "us"


def test_load_settings_reads_default_settings(tmp_path):
    settings = load_settings(settings_path(tmp_path))

    assert settings["cache"]["max_age_days"] == DEFAULT_SETTINGS["cache"]["max_age_days"]
    assert settings["paper_trading"]["initial_cash"] == DEFAULT_SETTINGS["paper_trading"]["initial_cash"]


def test_save_settings_can_save_and_reload(tmp_path):
    path = settings_path(tmp_path)
    settings = load_settings(path)
    settings["cache"]["enabled"] = False
    settings["cache"]["max_age_days"] = 14

    save_settings(settings, path)
    loaded = load_settings(path)

    assert loaded["cache"]["enabled"] is False
    assert loaded["cache"]["max_age_days"] == 14


def test_reset_settings_restores_default(tmp_path):
    path = settings_path(tmp_path)
    settings = load_settings(path)
    settings["dashboard"]["default_market"] = "cn"
    save_settings(settings, path)

    reset = reset_settings(path)

    assert reset["dashboard"]["default_market"] == "us"
    assert load_settings(path)["dashboard"]["default_market"] == "us"


def test_validate_settings_accepts_valid_settings():
    settings = validate_settings(DEFAULT_SETTINGS)

    assert settings["cache"]["enabled"] is True


def test_validate_settings_rejects_non_positive_cache_max_age():
    settings = {**DEFAULT_SETTINGS, "cache": {**DEFAULT_SETTINGS["cache"], "max_age_days": 0}}

    with pytest.raises(ValueError, match="cache.max_age_days"):
        validate_settings(settings)


def test_validate_settings_rejects_invalid_default_market():
    settings = {**DEFAULT_SETTINGS, "dashboard": {**DEFAULT_SETTINGS["dashboard"], "default_market": "hk"}}

    with pytest.raises(ValueError, match="dashboard.default_market"):
        validate_settings(settings)


def test_validate_settings_rejects_non_positive_initial_cash():
    settings = {**DEFAULT_SETTINGS, "paper_trading": {"initial_cash": -1}}

    with pytest.raises(ValueError, match="initial_cash"):
        validate_settings(settings)


def test_load_settings_invalid_json_raises_value_error(tmp_path):
    path = settings_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{bad json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid settings JSON"):
        load_settings(path)


def test_settings_path_traversal_is_rejected(tmp_path):
    path = tmp_path / "config" / ".." / "settings.json"

    with pytest.raises(ValueError, match="path traversal"):
        load_settings(path)


def test_settings_rejects_non_settings_json_path(tmp_path):
    outside_path = tmp_path / "config" / "other.json"

    with pytest.raises(ValueError, match="config/settings.json"):
        save_settings(DEFAULT_SETTINGS, outside_path)
    assert not outside_path.exists()


def test_get_and_update_setting(tmp_path):
    path = settings_path(tmp_path)

    update_setting("cache", "max_age_days", 21, path)

    assert get_setting("cache", "max_age_days", path=path) == 21


def test_settings_reject_sensitive_keys(tmp_path):
    settings = {**DEFAULT_SETTINGS, "api_key": "bad"}

    with pytest.raises(ValueError, match="API keys"):
        save_settings(settings, settings_path(tmp_path))


def test_settings_file_does_not_save_sensitive_keys(tmp_path):
    path = settings_path(tmp_path)
    save_settings(DEFAULT_SETTINGS, path)
    text = path.read_text(encoding="utf-8").lower()

    for word in ["api_key", "secret", "password", "token"]:
        assert word not in text


def test_settings_module_does_not_reference_broker_or_ai_clients():
    import src.config.settings as settings_module

    source = Path(settings_module.__file__).read_text(encoding="utf-8")
    forbidden = [
        "IBKR",
        "富途",
        "Alpaca",
        "Robinhood",
        "broker order",
        "place_order",
        "real trade",
        "OpenAI API",
        "AI prediction",
    ]

    for word in forbidden:
        assert word not in source
