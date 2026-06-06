from __future__ import annotations

import copy
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STRATEGY_PRESETS_PATH = PROJECT_ROOT / "config" / "strategy_presets.json"
PRESET_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
DEFAULT_PRESET_NAMES = {"trend_default", "trend_conservative", "trend_aggressive"}
SENSITIVE_KEYS = {"api_key", "apikey", "secret", "password", "token"}

DEFAULT_STRATEGY_PRESETS = {
    "trend_default": {
        "name": "trend_default",
        "description": "默认趋势策略参数，适合基础研究和演示。",
        "strategy_type": "trend_score",
        "min_score_to_buy": 80,
        "min_score_to_hold": 60,
        "max_position_pct": 0.15,
        "rebalance_frequency": "monthly",
    },
    "trend_conservative": {
        "name": "trend_conservative",
        "description": "更保守的趋势策略参数，买入门槛更高，单票仓位更低。",
        "strategy_type": "trend_score",
        "min_score_to_buy": 85,
        "min_score_to_hold": 65,
        "max_position_pct": 0.10,
        "rebalance_frequency": "monthly",
    },
    "trend_aggressive": {
        "name": "trend_aggressive",
        "description": "更积极的趋势策略参数，买入门槛略低，适合研究对比。",
        "strategy_type": "trend_score",
        "min_score_to_buy": 75,
        "min_score_to_hold": 55,
        "max_position_pct": 0.20,
        "rebalance_frequency": "monthly",
    },
}


def _default_presets() -> dict:
    return copy.deepcopy(DEFAULT_STRATEGY_PRESETS)


def normalize_preset_name(name: str) -> str:
    clean_name = str(name).strip()
    if not clean_name:
        raise ValueError("Strategy preset name cannot be empty.")
    if clean_name in {".", ".."} or "/" in clean_name or "\\" in clean_name:
        raise ValueError("Strategy preset name cannot contain path characters.")
    if not PRESET_NAME_PATTERN.fullmatch(clean_name):
        raise ValueError("Strategy preset name can only contain letters, numbers, underscores, and hyphens.")
    return clean_name


def _preset_path(path: str | Path) -> Path:
    raw_path = Path(path)
    if ".." in raw_path.parts:
        raise ValueError("Strategy preset path cannot contain path traversal.")
    resolved = raw_path.resolve()
    if resolved.name != "strategy_presets.json" or resolved.parent.name != "config":
        raise ValueError("Strategy presets can only be read from or written to config/strategy_presets.json.")
    return resolved


def _contains_sensitive_key(value) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in SENSITIVE_KEYS or normalized.endswith("_secret") or normalized.endswith("_token"):
                return True
            if _contains_sensitive_key(item):
                return True
    elif isinstance(value, list):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def validate_strategy_preset(preset: dict) -> dict:
    if not isinstance(preset, dict):
        raise ValueError("Strategy preset must be a JSON object.")
    if _contains_sensitive_key(preset):
        raise ValueError("Strategy presets must not contain API keys, secrets, passwords, or tokens.")

    normalized = {
        "name": normalize_preset_name(str(preset.get("name", ""))),
        "description": str(preset.get("description", "")).strip(),
        "strategy_type": str(preset.get("strategy_type", "trend_score")).strip(),
        "min_score_to_buy": preset.get("min_score_to_buy"),
        "min_score_to_hold": preset.get("min_score_to_hold"),
        "max_position_pct": preset.get("max_position_pct"),
        "rebalance_frequency": str(preset.get("rebalance_frequency", "monthly")).strip(),
    }

    if normalized["strategy_type"] != "trend_score":
        raise ValueError("strategy_type must be 'trend_score'.")

    for key in ("min_score_to_buy", "min_score_to_hold"):
        value = normalized[key]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0 or value > 100:
            raise ValueError(f"{key} must be an integer from 0 to 100.")
    if normalized["min_score_to_buy"] < normalized["min_score_to_hold"]:
        raise ValueError("min_score_to_buy must be greater than or equal to min_score_to_hold.")

    max_position_pct = normalized["max_position_pct"]
    if (
        not isinstance(max_position_pct, (int, float))
        or isinstance(max_position_pct, bool)
        or max_position_pct <= 0
        or max_position_pct > 1
    ):
        raise ValueError("max_position_pct must be greater than 0 and less than or equal to 1.")
    normalized["max_position_pct"] = float(max_position_pct)

    if normalized["rebalance_frequency"] != "monthly":
        raise ValueError("rebalance_frequency must be 'monthly'.")

    return normalized


def _write_presets(path: Path, presets: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(presets, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def reset_strategy_presets(path: str | Path = DEFAULT_STRATEGY_PRESETS_PATH) -> dict:
    preset_path = _preset_path(path)
    presets = _default_presets()
    _write_presets(preset_path, presets)
    return presets


def load_strategy_presets(path: str | Path = DEFAULT_STRATEGY_PRESETS_PATH) -> dict:
    preset_path = _preset_path(path)
    if not preset_path.exists():
        return reset_strategy_presets(preset_path)
    try:
        raw_presets = json.loads(preset_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid strategy preset JSON in {preset_path.name}: {error}") from error
    if not isinstance(raw_presets, dict):
        raise ValueError("Strategy presets JSON must be an object.")

    presets = {}
    for name, preset in raw_presets.items():
        clean_name = normalize_preset_name(str(name))
        normalized = validate_strategy_preset({**preset, "name": preset.get("name", clean_name)})
        if normalized["name"] != clean_name:
            raise ValueError(f"Strategy preset key and name must match: {clean_name}")
        presets[clean_name] = normalized
    return presets


def load_strategy_preset(name: str, path: str | Path = DEFAULT_STRATEGY_PRESETS_PATH) -> dict:
    clean_name = normalize_preset_name(name)
    presets = load_strategy_presets(path)
    if clean_name not in presets:
        raise ValueError(f"Strategy preset not found: {clean_name}")
    return copy.deepcopy(presets[clean_name])


def save_strategy_preset(name: str, preset: dict, path: str | Path = DEFAULT_STRATEGY_PRESETS_PATH) -> None:
    clean_name = normalize_preset_name(name)
    normalized = validate_strategy_preset({**preset, "name": clean_name})
    presets = load_strategy_presets(path)
    presets[clean_name] = normalized
    _write_presets(_preset_path(path), presets)


def delete_strategy_preset(name: str, path: str | Path = DEFAULT_STRATEGY_PRESETS_PATH) -> None:
    clean_name = normalize_preset_name(name)

    if clean_name in DEFAULT_PRESET_NAMES:
        raise ValueError("Default strategy presets cannot be deleted.")

    presets = load_strategy_presets(path)

    if clean_name not in presets:
        raise ValueError(f"Strategy preset not found: {clean_name}")

    del presets[clean_name]
    _write_presets(_preset_path(path), presets)
