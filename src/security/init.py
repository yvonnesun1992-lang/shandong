from __future__ import annotations

from src.security.policy import get_security_policy


def initialize_security_policy() -> dict:
    return get_security_policy().as_dict()
