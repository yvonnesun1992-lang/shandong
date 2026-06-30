from __future__ import annotations

from sandbox_read_only_connector.init import boundary


REQUIREMENTS = [
    "sandbox read-only credential required",
    "no trading permission",
    "no fund transfer permission",
    "no withdrawal permission",
    "no real account permission",
    "market data read scope separated",
    "account read scope separated",
    "frontend access forbidden",
    "audit access required",
    "emergency revoke required",
]


def build_read_only_credential_scope(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "credential_scope": {"requirements": REQUIREMENTS.copy(), "runtime_enabled": False},
        "credential_scope_ready": False,
        "secret_read_enabled": False,
        "blocking_items": REQUIREMENTS.copy(),
    }
