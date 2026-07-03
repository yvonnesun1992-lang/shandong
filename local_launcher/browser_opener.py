from __future__ import annotations

import webbrowser
from urllib.parse import urlparse

from config.v5_local_launcher_config import LOCAL_HOSTS, get_local_frontend_url
from local_launcher.init import boundary


def build_browser_open_target() -> str:
    target = get_local_frontend_url()
    parsed = urlparse(target)
    if parsed.hostname not in LOCAL_HOSTS:
        return "http://127.0.0.1:3000"
    return target


def open_browser(dry_run: bool = True) -> dict:
    target = build_browser_open_target()
    payload = {"dry_run": dry_run, "browser_target": target, "status": "dry_run" if dry_run else "opened", **boundary()}
    if not dry_run:
        webbrowser.open(target)
    return payload
