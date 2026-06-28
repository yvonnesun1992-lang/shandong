from __future__ import annotations


ERROR_CODES = {
    "CONNECTOR_DISABLED": {"retryable": False, "message": "Connector runtime is disabled."},
    "CREDENTIAL_MISSING": {"retryable": False, "message": "Credential handle is missing."},
    "CREDENTIAL_INVALID": {"retryable": False, "message": "Credential handle is invalid."},
    "PROVIDER_UNAVAILABLE": {"retryable": True, "message": "Provider unavailable."},
    "RATE_LIMITED": {"retryable": True, "message": "Rate limit exceeded."},
    "ORDER_REJECTED": {"retryable": False, "message": "Order rejected."},
    "ORDER_DUPLICATE": {"retryable": False, "message": "Duplicate order request."},
    "ORDER_NOT_FOUND": {"retryable": False, "message": "Order not found."},
    "CANCEL_REJECTED": {"retryable": False, "message": "Cancel rejected."},
    "RISK_REJECTED": {"retryable": False, "message": "Risk rejected."},
    "MANUAL_APPROVAL_REQUIRED": {"retryable": False, "message": "Manual approval required."},
    "KILL_SWITCH_ACTIVE": {"retryable": False, "message": "Kill switch active."},
    "TIMEOUT": {"retryable": True, "message": "Provider timeout."},
    "RETRY_EXHAUSTED": {"retryable": False, "message": "Retry exhausted."},
    "UNKNOWN_ERROR": {"retryable": False, "message": "Unknown sanitized error."},
}


def list_error_codes() -> list[str]:
    return list(ERROR_CODES)


def get_error_code_detail(code: str) -> dict:
    detail = ERROR_CODES.get(code, ERROR_CODES["UNKNOWN_ERROR"])
    return {"code": code if code in ERROR_CODES else "UNKNOWN_ERROR", **detail, "sanitized": True}


def normalize_provider_error(provider: str, raw_error: object) -> dict:
    text = str(raw_error).lower()
    if "timeout" in text:
        code = "TIMEOUT"
    elif "rate" in text:
        code = "RATE_LIMITED"
    elif "reject" in text:
        code = "ORDER_REJECTED"
    else:
        code = "UNKNOWN_ERROR"
    return {"provider": provider, "code": code, "message": ERROR_CODES[code]["message"], "sanitized": True, "raw_provider_payload_available": False}
