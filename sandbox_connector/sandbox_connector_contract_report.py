from __future__ import annotations

from pathlib import Path

from config.v5_sandbox_connector_contract_config import get_connector_contract_status
from sandbox_connector.connector_interface_contract import build_interface_contract
from sandbox_connector.connector_safety_validator import build_connector_readiness_summary, validate_connector_contract
from sandbox_connector.credential_boundary_contract import build_credential_boundary_contract
from sandbox_connector.error_code_contract import list_error_codes
from sandbox_connector.idempotency_policy import build_idempotency_policy
from sandbox_connector.rate_limit_policy import build_rate_limit_policy
from sandbox_connector.request_schema_contract import build_request_schema_contract
from sandbox_connector.response_schema_contract import build_response_schema_contract
from sandbox_connector.retry_policy import build_retry_policy


REPORT_PATH = Path("reports/v5_13_sandbox_connector_contract_report.md")


def build_sandbox_connector_contract_summary() -> dict:
    status = get_connector_contract_status()
    safety = validate_connector_contract()
    verdict = "PASS" if safety["safe"] and status["contract_only"] else "FAIL"
    return {
        "version": "V5.13",
        "verdict": verdict,
        "status": status,
        "interface_contract": build_interface_contract(),
        "request_schema": build_request_schema_contract(),
        "response_schema": build_response_schema_contract(),
        "error_codes": list_error_codes(),
        "idempotency_policy": build_idempotency_policy(),
        "rate_limit_policy": build_rate_limit_policy(),
        "retry_policy": build_retry_policy(),
        "credential_boundary": build_credential_boundary_contract(),
        "connector_safety": safety,
        "readiness": build_connector_readiness_summary(),
        "missing_production_requirements": ["credential vault", "provider SDK review", "sandbox runtime implementation"],
        "contract_only": True,
    }


def generate_sandbox_connector_contract_report() -> dict:
    payload = build_sandbox_connector_contract_summary()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# V5.13 Sandbox Connector Contract Report",
                "",
                f"Final verdict: {payload['verdict']}",
                "",
                "Current mode is sandbox connector contract planning only.",
                "",
                "Safety boundary:",
                "",
                "- Sandbox API connection: no",
                "- Real broker connection: no",
                "- Real order submission: no",
                "- Real capital movement: no",
                "- Production live trading: no",
                "",
                "Contract sections:",
                "",
                "- Connector interface contract",
                "- Request and response schemas",
                "- Error code contract",
                "- Idempotency policy",
                "- Rate limit policy",
                "- Retry policy",
                "- Credential boundary contract",
                "- Connector safety validator",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {"path": REPORT_PATH.as_posix(), "verdict": payload["verdict"], "summary": payload, "contract_only": True}
