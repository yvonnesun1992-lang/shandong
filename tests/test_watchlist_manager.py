from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.data.watchlist_manager import (
    delete_watchlist,
    load_watchlist,
    load_watchlists,
    normalize_symbols,
    save_watchlist,
    validate_watchlist_name,
)


def test_missing_watchlist_file_creates_default_config(tmp_path):
    path = tmp_path / "config" / "watchlists.json"

    watchlists = load_watchlists(path)

    assert path.exists()
    assert "us_default" in watchlists
    assert "cn_default" in watchlists


def test_load_watchlists_reads_default_config(tmp_path):
    path = tmp_path / "watchlists.json"
    path.write_text(json.dumps({"us_default": ["nvda", "amd"]}), encoding="utf-8")

    watchlists = load_watchlists(path)

    assert watchlists["us_default"] == ["NVDA", "AMD"]


def test_load_watchlist_reads_selected_list(tmp_path):
    path = tmp_path / "watchlists.json"
    path.write_text(json.dumps({"my_list": ["MSFT"]}), encoding="utf-8")

    symbols = load_watchlist("my_list", path)

    assert symbols == ["MSFT"]


def test_save_watchlist_can_save_and_reload(tmp_path):
    path = tmp_path / "watchlists.json"

    save_watchlist("my_us_watchlist", [" nvda ", "amd", "NVDA", ""], path)

    assert load_watchlist("my_us_watchlist", path) == ["NVDA", "AMD"]


def test_normalize_symbols_cleans_deduplicates_and_filters():
    symbols = normalize_symbols([" nvda ", "", "NVDA", " 300308 ", "977"])

    assert symbols == ["NVDA", "300308", "000977"]


def test_delete_watchlist_removes_selected_list(tmp_path):
    path = tmp_path / "watchlists.json"
    save_watchlist("to_delete", ["NVDA"], path)

    delete_watchlist("to_delete", path)

    assert "to_delete" not in load_watchlists(path)


def test_invalid_json_raises_clear_error(tmp_path):
    path = tmp_path / "watchlists.json"
    path.write_text("{bad json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid watchlist JSON"):
        load_watchlists(path)


@pytest.mark.parametrize("name", ["", "../bad", "bad/name", "bad\\name", "bad name", "bad.name"])
def test_invalid_watchlist_name_is_rejected(name):
    with pytest.raises(ValueError):
        validate_watchlist_name(name)


def test_watchlist_name_does_not_create_path_outside_config(tmp_path):
    path = tmp_path / "config" / "watchlists.json"

    with pytest.raises(ValueError):
        save_watchlist("../outside", ["NVDA"], path)

    assert not (tmp_path / "outside").exists()
    assert not Path("../outside").exists()
