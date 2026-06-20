from __future__ import annotations

from dataclasses import dataclass

from src.config import auth_config


@dataclass(frozen=True)
class SecurityPolicy:
    auth_mode: str
    require_auth: bool
    allow_local_admin_fallback: bool
    session_ttl_minutes: int
    api_key_required_for_production: bool

    def warnings(self) -> list[str]:
        warnings: list[str] = []
        if self.auth_mode == "local" and self.allow_local_admin_fallback:
            warnings.append("local admin fallback enabled")
        if self.auth_mode == "production" and not self.require_auth:
            warnings.append("production auth is not required")
        if self.auth_mode == "production" and self.allow_local_admin_fallback:
            warnings.append("production local admin fallback must be disabled")
        return warnings

    def production_ready(self) -> bool:
        if self.auth_mode != "production":
            return False
        return self.require_auth and not self.allow_local_admin_fallback and self.api_key_required_for_production

    def as_dict(self) -> dict:
        return {
            "auth_mode": self.auth_mode,
            "require_auth": self.require_auth,
            "allow_local_admin_fallback": self.allow_local_admin_fallback,
            "api_key_required_for_production": self.api_key_required_for_production,
            "session_ttl_minutes": self.session_ttl_minutes,
            "production_ready": self.production_ready(),
            "warnings": self.warnings(),
        }


def get_security_policy() -> SecurityPolicy:
    mode = auth_config.auth_mode()
    return SecurityPolicy(
        auth_mode=mode,
        require_auth=auth_config.require_auth(),
        allow_local_admin_fallback=auth_config.allow_local_admin_fallback() if mode != "production" else False,
        session_ttl_minutes=auth_config.session_ttl_minutes(),
        api_key_required_for_production=auth_config.api_key_required_for_production(),
    )


def is_production_auth() -> bool:
    return get_security_policy().auth_mode == "production"


def can_use_local_admin_fallback() -> bool:
    policy = get_security_policy()
    return policy.auth_mode == "local" and policy.allow_local_admin_fallback


def require_production_auth() -> bool:
    policy = get_security_policy()
    return policy.auth_mode == "production" and policy.require_auth
