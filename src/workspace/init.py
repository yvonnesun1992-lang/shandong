from __future__ import annotations

from src.workspace.workspace_service import ensure_default_workspace


def initialize_workspace_system(user_id: str = "default") -> dict:
    return ensure_default_workspace(user_id=user_id)
