from __future__ import annotations


BLOCKED_STATES = {"LIVE_APPROVED", "REAL_ORDER_READY", "AUTO_APPROVED"}
ALLOWED_TRANSITIONS = {
    "DRAFT": {"PENDING_REVIEW", "REJECTED", "EXPIRED"},
    "PENDING_REVIEW": {"APPROVED_SIMULATED", "REJECTED", "EXPIRED"},
    "APPROVED_SIMULATED": {"REJECTED", "EXPIRED"},
    "REJECTED": set(),
    "EXPIRED": set(),
}


class ApprovalStateMachine:
    def can_transition(self, current: str, target: str) -> bool:
        if target in BLOCKED_STATES:
            return False
        return target in ALLOWED_TRANSITIONS.get(current, set())

    def transition(self, current: str, target: str) -> str:
        return target if self.can_transition(current, target) else "REJECTED"

    def expire_if_timed_out(self, current: str, age_seconds: int, timeout_seconds: int = 3600) -> str:
        if current in {"REJECTED", "EXPIRED"}:
            return current
        return "EXPIRED" if age_seconds >= timeout_seconds else current

    def describe(self) -> dict:
        return {
            "states": ["DRAFT", "PENDING_REVIEW", "APPROVED_SIMULATED", "REJECTED", "EXPIRED"],
            "allowed_transitions": {key: sorted(value) for key, value in ALLOWED_TRANSITIONS.items()},
            "blocked_states": sorted(BLOCKED_STATES),
            "real_order_path_exists": False,
            "auto_approval_enabled": False,
            "paper_trading": True,
        }
