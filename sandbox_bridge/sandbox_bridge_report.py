from __future__ import annotations

from pathlib import Path

from runtime.security_scan import scan_sandbox_bridge_outputs
from sandbox_bridge.bridge_safety_gate import validate_bridge_safety
from sandbox_bridge.error_translation_layer import translate_error
from sandbox_bridge.idempotency_enforcer import IdempotencyEnforcer
from sandbox_bridge.request_transformer import transform_submit_order
from sandbox_bridge.response_normalizer import normalize_order_response
from sandbox_bridge.retry_orchestrator import schedule_retry
from sandbox_bridge.sandbox_bridge_core import SandboxBridgeCore
from sandbox_bridge.sandbox_router import route_request
from sandbox_bridge.sandbox_session import SandboxSession


REPORT_PATH = Path("reports/v5_16_sandbox_connector_bridge_report.md")


def build_sandbox_bridge_summary(test_name: str = "route") -> dict:
    bridge = SandboxBridgeCore()
    session = SandboxSession()
    idempotency = IdempotencyEnforcer()
    request = {"symbol": "AAPL", "side": "BUY", "quantity": 1}
    idempotency.record_request(request, {"status": "MOCK_ACCEPTED"})
    safety = validate_bridge_safety({"bridge_only": True})
    summary = {
        "bridge_only": True,
        "real_connection": False,
        "real_orders": False,
        "paper_trading": True,
        "test": test_name,
    }
    payload = {
        "version": "V5.16",
        "summary": summary,
        "bridge": bridge.status(),
        "session": session.start_session(),
        "routing": route_request({"backend": "bridge", **request}),
        "transform": transform_submit_order(request),
        "normalize": normalize_order_response({"status": "accepted"}),
        "error_translation": translate_error({"type": "timeout"}),
        "retry": schedule_retry("TIMEOUT", 1),
        "idempotency": idempotency.check_duplicate(request),
        "safety": safety,
        "missing_production_requirements": [
            "provider sandbox credentials vault",
            "sandbox certification",
            "network allowlist review",
            "manual release approval",
            "production runbook signoff",
        ],
        "verdict": "PASS" if safety["safe"] else "FAIL",
        "warnings": [] if safety["safe"] else ["bridge safety check failed"],
    }
    return payload


def generate_sandbox_bridge_report(test_name: str = "route") -> dict:
    payload = build_sandbox_bridge_summary(test_name)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(payload), encoding="utf-8")
    scan = scan_sandbox_bridge_outputs(payload, REPORT_PATH)
    if not scan["safe"]:
        payload["verdict"] = "FAIL"
        payload.setdefault("warnings", []).append("safety scan found blocked output")
    return {
        "path": REPORT_PATH.as_posix(),
        "verdict": payload["verdict"],
        "summary": payload["summary"],
        "warnings": payload.get("warnings", []),
        "bridge_only": True,
        "real_connection": False,
        "paper_trading": True,
    }


def _render_report(payload: dict) -> str:
    return f"""# V5.16 Sandbox Connector Bridge

Verdict: {payload["verdict"]}

## Bridge Architecture

- Broker adapter skeleton to sandbox bridge abstraction.
- Future sandbox API remains disconnected.
- Future real broker remains disconnected.

## Layers

- Transformation layer: local schema mapping only.
- Normalization layer: sanitized V5 response format.
- Routing logic: mock, skeleton, or bridge simulated route only.
- Error translation: standardized sanitized error codes.
- Retry policy: delay plan only, no real sleep.
- Idempotency policy: local in-memory duplicate protection.
- Session lifecycle: simulated only.
- Safety gate: blocks real connection and network runtime config.

## Boundary

- Current stage is sandbox connector bridge abstraction only.
- Current stage does not connect to sandbox API.
- Current stage does not connect to a real broker.
- Current stage does not submit real orders.
- Current stage does not trade real money.
- Current stage is not a production trading system.
"""
