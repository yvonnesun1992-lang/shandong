from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from approval.approval_audit_trail import ApprovalAuditTrail
from approval.approval_request import ApprovalRequest
from approval.approval_risk_summary import build_approval_risk_summary
from approval.approval_state_machine import ApprovalStateMachine
from config.v5_manual_approval_config import get_manual_approval_policy, get_manual_approval_status


class ManualApprovalGate:
    def __init__(self, audit_trail: ApprovalAuditTrail | None = None) -> None:
        self.audit_trail = audit_trail or ApprovalAuditTrail()
        self.state_machine = ApprovalStateMachine()
        self._requests: dict[str, ApprovalRequest] = {}

    def create_approval_request(self, order_intent: dict[str, Any], risk_summary: dict[str, Any] | None = None) -> ApprovalRequest:
        summary = risk_summary or build_approval_risk_summary(order_intent)
        request = ApprovalRequest.create(
            order_intent_id=str(order_intent.get("order_intent_id", "planned-intent")),
            symbol=str(order_intent.get("symbol", "")),
            side=str(order_intent.get("side", order_intent.get("action", ""))),
            quantity=float(order_intent.get("quantity", 0) or 0),
            order_type=str(order_intent.get("order_type", "MARKET")),
            notional_value=float(order_intent.get("notional_value", summary.get("estimated_notional", 0)) or 0),
            signal_source=str(order_intent.get("signal_source", "v5_alpha")),
            signal_strength=float(order_intent.get("signal_strength", order_intent.get("strength", 0)) or 0),
            risk_summary=summary,
            status="PENDING_REVIEW",
        )
        self._requests[request.approval_id] = request
        self.audit_trail.record_approval_event("approval_created", request.approval_id, metadata={"symbol": request.symbol, "side": request.side})
        return request

    def review_approval_request(self, approval_id: str, decision: str, reason: str, reviewer: str = "simulated_reviewer") -> dict[str, Any]:
        request = self._requests.get(approval_id)
        current = request.status if request else "PENDING_REVIEW"
        normalized = "APPROVED_SIMULATED" if decision.lower() in {"approve", "approved", "approve_simulated"} else "REJECTED"
        next_status = self.state_machine.transition(current, normalized)
        event_type = "approval_reviewed" if next_status == "APPROVED_SIMULATED" else "approval_rejected"
        if request:
            request.status = next_status
            request.reviewed_at = datetime.now(UTC).isoformat()
            request.reviewer = reviewer
            request.reason = reason
        self.audit_trail.record_approval_event(event_type, approval_id, metadata={"decision": next_status, "reason": reason})
        return {
            "approval_id": approval_id,
            "status": next_status,
            "reason": reason,
            "reviewer": reviewer,
            **_approval_boundary(),
        }

    def reject_by_default(self, order_intent: dict[str, Any]) -> dict[str, Any]:
        approval_id = str(order_intent.get("approval_id", "approval-default-reject"))
        self.audit_trail.record_approval_event("real_order_attempt_rejected", approval_id, metadata={"symbol": order_intent.get("symbol"), "side": order_intent.get("side")})
        return {"approval_id": approval_id, "status": "REJECTED", "reason": "reject-by-default manual approval planning policy", **_approval_boundary()}

    def approval_readiness_summary(self) -> dict[str, Any]:
        return approval_readiness_summary()


def approval_readiness_summary() -> dict[str, Any]:
    status = get_manual_approval_status()
    policy = get_manual_approval_policy()
    return {
        "readiness": "planning_only",
        "manual_approval_required": status["manual_approval_required"],
        "auto_approval_enabled": status["auto_approval_enabled"],
        "real_order_after_approval": status["real_order_after_approval"],
        "real_orders_enabled": status["real_orders_enabled"],
        "real_money_enabled": status["real_money_enabled"],
        "paper_trading": status["paper_trading"],
        "planning_only": True,
        "policy": policy,
        "missing_production_requirements": [
            "real human identity and role review",
            "dual approval workflow",
            "broker sandbox certification",
            "immutable audit storage",
            "independent kill switch",
            "legal and operational approval",
        ],
    }


def _approval_boundary() -> dict[str, Any]:
    return {
        "manual_approval_required": True,
        "auto_approval_enabled": False,
        "real_order_after_approval": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
    }
