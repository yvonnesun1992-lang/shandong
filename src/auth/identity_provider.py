from __future__ import annotations

from dataclasses import asdict, dataclass

from src.config.identity_config import identity_planning_status


@dataclass(frozen=True)
class IdentityProviderStatus:
    mode: str
    current_provider: str
    enabled: bool
    production_ready: bool
    external_provider_enabled: bool
    warnings: tuple[str, ...]

    def as_dict(self) -> dict:
        data = asdict(self)
        data["warnings"] = list(self.warnings)
        return data


@dataclass(frozen=True)
class IdentityProviderPlan:
    status: IdentityProviderStatus
    future_supported_providers: tuple[str, ...]
    boundary: dict

    def as_dict(self) -> dict:
        return {
            "status": self.status.as_dict(),
            "future_supported_providers": list(self.future_supported_providers),
            "boundary": dict(self.boundary),
        }


def validate_identity_provider_boundary() -> dict:
    return {
        "planning_only": True,
        "implemented_external_identity": False,
        "external_calls": False,
        "sensitive_values_required": False,
        "production_ready": False,
    }


def get_identity_provider_plan() -> IdentityProviderPlan:
    status = identity_planning_status()
    provider_status = IdentityProviderStatus(
        mode=status["mode"],
        current_provider=status["provider"],
        enabled=False,
        production_ready=False,
        external_provider_enabled=False,
        warnings=tuple(status["warnings"]),
    )
    return IdentityProviderPlan(
        status=provider_status,
        future_supported_providers=(
            "external_oidc_planned",
            "enterprise_sso_planned",
            "email_magic_link_planned",
        ),
        boundary=validate_identity_provider_boundary(),
    )
