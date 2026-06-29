from __future__ import annotations

from provider_onboarding import boundary


PHASES = [
    "preflight checklist",
    "credential vault validation",
    "sandbox connector dry startup",
    "account read-only test planned",
    "order preview test planned",
    "manual approval simulation",
    "sandbox order disabled by default",
    "kill switch test planned",
    "rollback rehearsal",
    "post-run review",
]


def build_sandbox_dry_run_runbook(provider: str) -> dict:
    return {
        "provider": provider,
        "dry_run_ready": False,
        "phases": PHASES.copy(),
        "blocking_items": [
            "dry run cannot execute until a future connector design is approved",
            "sandbox orders remain disabled by default",
            "credential vault validation is only a future checklist item",
        ],
        "sandbox_orders_enabled": False,
        **boundary(),
    }
