from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


SAFE_ACCOUNT_PATTERN = re.compile(r"[^A-Za-z0-9_.-]+")


def normalize_account_id(user_id: str | None = None) -> str:
    clean = SAFE_ACCOUNT_PATTERN.sub("_", str(user_id or "default").strip())
    return clean or "default"


@dataclass(frozen=True)
class AccountContext:
    user_id: str = "default"
    base_dir: Path = Path("data/users")

    def __post_init__(self) -> None:
        object.__setattr__(self, "user_id", normalize_account_id(self.user_id))

    @property
    def user_root(self) -> Path:
        return self.base_dir / self.user_id

    @property
    def report_dir(self) -> Path:
        return self.user_root / "reports"

    @property
    def cache_dir(self) -> Path:
        return self.user_root / "cache"

    @property
    def dashboard_dir(self) -> Path:
        return self.user_root / "dashboard"

    def report_path(self, report_id: str) -> Path:
        return self.report_dir / str(report_id)

    def cache_path(self, key: str) -> Path:
        return self.cache_dir / str(key)

    def dashboard_path(self, key: str) -> Path:
        return self.dashboard_dir / str(key)

    def as_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "user_root": self.user_root.as_posix(),
            "report_dir": self.report_dir.as_posix(),
            "cache_dir": self.cache_dir.as_posix(),
            "dashboard_dir": self.dashboard_dir.as_posix(),
        }


def create_account_context(user_id: str | None = None) -> AccountContext:
    return AccountContext(user_id=user_id or "default")
