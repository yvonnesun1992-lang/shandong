from __future__ import annotations

import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WATCHLIST_PATH = PROJECT_ROOT / "config" / "watchlists.json"
WATCHLIST_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

DEFAULT_WATCHLISTS = {
    "us_default": ["NVDA", "AMD", "PLTR", "TSLA", "MSFT", "GOOGL", "META", "AVGO", "CORZ"],
    "cn_default": ["300308", "300502", "601138", "002371", "603986", "000977", "002463", "300476", "688256"],
}


def validate_watchlist_name(name: str) -> str:
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Watchlist name cannot be empty.")
    if clean_name in {".", ".."} or "/" in clean_name or "\\" in clean_name:
        raise ValueError("Watchlist name cannot contain path characters.")
    if not WATCHLIST_NAME_PATTERN.fullmatch(clean_name):
        raise ValueError("Watchlist name can only contain letters, numbers, underscores, and hyphens.")
    return clean_name


def normalize_symbols(symbols: list[str]) -> list[str]:
    normalized = []
    seen = set()
    for symbol in symbols:
        clean_symbol = str(symbol).strip().upper()
        if not clean_symbol:
            continue
        if clean_symbol.isdigit() and len(clean_symbol) <= 6:
            clean_symbol = clean_symbol.zfill(6)
        if clean_symbol in seen:
            continue
        seen.add(clean_symbol)
        normalized.append(clean_symbol)
    return normalized


def _default_watchlists() -> dict[str, list[str]]:
    return {name: symbols.copy() for name, symbols in DEFAULT_WATCHLISTS.items()}


def _write_watchlists(path: Path, watchlists: dict[str, list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(watchlists, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _ensure_watchlist_file(path: Path) -> None:
    if not path.exists():
        _write_watchlists(path, _default_watchlists())


def load_watchlists(path: str | Path = DEFAULT_WATCHLIST_PATH) -> dict[str, list[str]]:
    watchlist_path = Path(path)
    _ensure_watchlist_file(watchlist_path)
    try:
        raw_data = json.loads(watchlist_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid watchlist JSON in {watchlist_path}: {error}") from error

    if not isinstance(raw_data, dict):
        raise ValueError("Watchlist JSON must be an object with list values.")

    watchlists: dict[str, list[str]] = {}
    for name, symbols in raw_data.items():
        clean_name = validate_watchlist_name(str(name))
        if not isinstance(symbols, list):
            raise ValueError(f"Watchlist '{clean_name}' must be a list of symbols.")
        watchlists[clean_name] = normalize_symbols([str(symbol) for symbol in symbols])
    return watchlists


def load_watchlist(name: str, path: str | Path = DEFAULT_WATCHLIST_PATH) -> list[str]:
    clean_name = validate_watchlist_name(name)
    watchlists = load_watchlists(path)
    if clean_name not in watchlists:
        raise ValueError(f"Watchlist not found: {clean_name}")
    return watchlists[clean_name].copy()


def save_watchlist(name: str, symbols: list[str], path: str | Path = DEFAULT_WATCHLIST_PATH) -> None:
    clean_name = validate_watchlist_name(name)
    watchlists = load_watchlists(path)
    watchlists[clean_name] = normalize_symbols(symbols)
    _write_watchlists(Path(path), watchlists)


def delete_watchlist(name: str, path: str | Path = DEFAULT_WATCHLIST_PATH) -> None:
    clean_name = validate_watchlist_name(name)
    watchlists = load_watchlists(path)
    if clean_name not in watchlists:
        raise ValueError(f"Watchlist not found: {clean_name}")
    del watchlists[clean_name]
    _write_watchlists(Path(path), watchlists)
