from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from src.strategies import presets as presets_module
from src.strategies.presets import (
    DEFAULT_STRATEGY_PRESETS,
    delete_strategy_preset,
    load_strategy_preset,
    load_strategy_presets,
    normalize_preset_name,
    reset_strategy_presets,
    save_strategy_preset,
    validate_strategy_preset,
)


def preset_path(tmp_path: Path) -> Path:
    return tmp_path / "config" / "strategy_presets.json"


def valid_preset(name: str = "custom_trend") -> dict:
    return {
        "name": name,
        "description": "Test preset.",
        "strategy_type": "trend_score",
        "min_score_to_buy": 80,
        "min_score_to_hold": 60,
        "max_position_pct": 0.15,
        "rebalance_frequency": "monthly",
    }


def test_missing_presets_file_is_created(tmp_path):
    path = preset_path(tmp_path)

    presets = load_strategy_presets(path)

    assert path.exists()
    assert "trend_default" in presets


def test_load_strategy_presets_reads_defaults(tmp_path):
    presets = reset_strategy_presets(preset_path(tmp_path))

    assert presets == DEFAULT_STRATEGY_PRESETS


def test_load_strategy_preset_reads_named_preset(tmp_path):
    path = preset_path(tmp_path)
    reset_strategy_presets(path)

    preset = load_strategy_preset("trend_default", path)

    assert preset["name"] == "trend_default"
    assert preset["strategy_type"] == "trend_score"


def test_save_strategy_preset_can_round_trip(tmp_path):
    path = preset_path(tmp_path)
    reset_strategy_presets(path)

    save_strategy_preset("custom_trend", valid_preset("custom_trend"), path)
    loaded = load_strategy_preset("custom_trend", path)

    assert loaded["name"] == "custom_trend"
    assert loaded["min_score_to_buy"] == 80


def test_delete_strategy_preset_removes_non_default(tmp_path):
    path = preset_path(tmp_path)
    reset_strategy_presets(path)
    save_strategy_preset("custom_trend", valid_preset("custom_trend"), path)

    delete_strategy_preset("custom_trend", path)

    assert "custom_trend" not in load_strategy_presets(path)


def test_delete_strategy_preset_rejects_trend_default(tmp_path):
    path = preset_path(tmp_path)
    reset_strategy_presets(path)

    with pytest.raises(ValueError, match="Default strategy presets cannot be deleted"):
        delete_strategy_preset("trend_default", path)

    presets = load_strategy_presets(path)
    assert "trend_default" in presets
    assert {"trend_default", "trend_conservative", "trend_aggressive"}.issubset(presets)


def test_delete_strategy_preset_rejects_trend_conservative(tmp_path):
    path = preset_path(tmp_path)
    reset_strategy_presets(path)

    with pytest.raises(ValueError, match="Default strategy presets cannot be deleted"):
        delete_strategy_preset("trend_conservative", path)

    presets = load_strategy_presets(path)
    assert "trend_conservative" in presets
    assert {"trend_default", "trend_conservative", "trend_aggressive"}.issubset(presets)


def test_delete_strategy_preset_rejects_trend_aggressive(tmp_path):
    path = preset_path(tmp_path)
    reset_strategy_presets(path)

    with pytest.raises(ValueError, match="Default strategy presets cannot be deleted"):
        delete_strategy_preset("trend_aggressive", path)

    presets = load_strategy_presets(path)
    assert "trend_aggressive" in presets
    assert {"trend_default", "trend_conservative", "trend_aggressive"}.issubset(presets)


def test_reset_strategy_presets_restores_defaults(tmp_path):
    path = preset_path(tmp_path)
    reset_strategy_presets(path)
    save_strategy_preset("custom_trend", valid_preset("custom_trend"), path)

    presets = reset_strategy_presets(path)

    assert set(presets) == set(DEFAULT_STRATEGY_PRESETS)


def test_validate_strategy_preset_accepts_valid_input():
    preset = validate_strategy_preset(valid_preset())

    assert preset["name"] == "custom_trend"
    assert preset["max_position_pct"] == 0.15


@pytest.mark.parametrize("value", [-1, 101, 80.5, True])
def test_min_score_to_buy_invalid(value):
    preset = valid_preset()
    preset["min_score_to_buy"] = value

    with pytest.raises(ValueError, match="min_score_to_buy"):
        validate_strategy_preset(preset)


@pytest.mark.parametrize("value", [-1, 101, 60.5, True])
def test_min_score_to_hold_invalid(value):
    preset = valid_preset()
    preset["min_score_to_hold"] = value

    with pytest.raises(ValueError, match="min_score_to_hold"):
        validate_strategy_preset(preset)


def test_buy_score_cannot_be_below_hold_score():
    preset = valid_preset()
    preset["min_score_to_buy"] = 50
    preset["min_score_to_hold"] = 60

    with pytest.raises(ValueError, match="greater than or equal"):
        validate_strategy_preset(preset)


@pytest.mark.parametrize("value", [0, -0.1, 1.1, True])
def test_max_position_pct_invalid(value):
    preset = valid_preset()
    preset["max_position_pct"] = value

    with pytest.raises(ValueError, match="max_position_pct"):
        validate_strategy_preset(preset)


def test_strategy_type_must_be_trend_score():
    preset = valid_preset()
    preset["strategy_type"] = "other"

    with pytest.raises(ValueError, match="strategy_type"):
        validate_strategy_preset(preset)


def test_rebalance_frequency_must_be_monthly():
    preset = valid_preset()
    preset["rebalance_frequency"] = "weekly"

    with pytest.raises(ValueError, match="rebalance_frequency"):
        validate_strategy_preset(preset)


@pytest.mark.parametrize("name", ["../bad", "bad/name", "bad\\name", "", "bad name"])
def test_preset_name_path_or_format_is_rejected(name):
    with pytest.raises(ValueError):
        normalize_preset_name(name)


def test_json_damage_raises_value_error(tmp_path):
    path = preset_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text("{bad json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid strategy preset JSON"):
        load_strategy_presets(path)


def test_path_traversal_is_rejected(tmp_path):
    bad_path = tmp_path / "config" / ".." / "strategy_presets.json"

    with pytest.raises(ValueError, match="path traversal"):
        load_strategy_presets(bad_path)


def test_wrong_file_location_is_rejected(tmp_path):
    bad_path = tmp_path / "other" / "strategy_presets.json"

    with pytest.raises(ValueError, match="config/strategy_presets.json"):
        load_strategy_presets(bad_path)


def test_sensitive_keys_are_rejected():
    preset = valid_preset()
    preset["api_key"] = "bad"

    with pytest.raises(ValueError, match="API keys"):
        validate_strategy_preset(preset)


def test_module_does_not_call_broker_or_ai_api():
    source = inspect.getsource(presets_module)
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
