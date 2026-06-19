from __future__ import annotations

import re
from dataclasses import dataclass


SAFE_USER_PATTERN = re.compile(r"[^A-Za-z0-9_.-]+")


def normalize_user_id(user_id: str | None = None) -> str:
    clean = SAFE_USER_PATTERN.sub("_", str(user_id or "default").strip())
    return clean or "default"


@dataclass(frozen=True)
class UserContext:
    user_id: str = "default"

    def __post_init__(self) -> None:
        object.__setattr__(self, "user_id", normalize_user_id(self.user_id))

    @property
    def report_namespace(self) -> str:
        return f"user:{self.user_id}:reports"

    def report_key(self, report_id: str) -> str:
        return f"{self.report_namespace}:{report_id}"

    def cache_key(self, key: str) -> str:
        return f"user:{self.user_id}:cache:{key}"

    def dashboard_key(self, key: str) -> str:
        return f"user:{self.user_id}:dashboard:{key}"

    def as_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "report_namespace": self.report_namespace,
        }
