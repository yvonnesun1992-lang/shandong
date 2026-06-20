from __future__ import annotations

import re
from typing import Any

from src.api.v2.response import error_response


SENSITIVE_KEY_PATTERN = re.compile(r"(secret|token|password|api[_-]?key)", re.IGNORECASE)
PATH_PATTERN = re.compile(r"(/[^\s:,}]+)+")
DATABASE_FILE_PATTERN = re.compile(r"\b[\w.-]+\.db\b", re.IGNORECASE)
ASSIGNMENT_PATTERN = re.compile(r"(secret|token|password|api[_-]?key)\\s*=\\s*[^\\s,}]+", re.IGNORECASE)


def sanitize_error_value(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            if SENSITIVE_KEY_PATTERN.search(str(key)):
                continue
            clean[str(key)] = sanitize_error_value(item)
        return clean
    if isinstance(value, list):
        return [sanitize_error_value(item) for item in value]
    text = str(value)
    text = ASSIGNMENT_PATTERN.sub("[redacted]", text)
    text = PATH_PATTERN.sub("[path]", text)
    text = DATABASE_FILE_PATTERN.sub("[database]", text)
    text = SENSITIVE_KEY_PATTERN.sub("[redacted]", text)
    return text


class ApiError(Exception):
    code = "API_ERROR"
    status_code = 400

    def __init__(self, message: str, code: str | None = None, status_code: int | None = None, detail: dict | None = None) -> None:
        self.message = str(message or "API error")
        self.detail = detail or {}
        if code:
            self.code = code
        if status_code is not None:
            self.status_code = int(status_code)
        super().__init__(self.message)

    def to_response(self) -> dict:
        return error_response(
            message=str(sanitize_error_value(self.message)),
            code=self.code,
            status_code=self.status_code,
            detail=sanitize_error_value(self.detail),
        )


class ValidationApiError(ApiError):
    code = "VALIDATION_ERROR"
    status_code = 422


class NotFoundApiError(ApiError):
    code = "NOT_FOUND"
    status_code = 404


class DatabaseApiError(ApiError):
    code = "DATABASE_ERROR"
    status_code = 503

    def __init__(self, message: str = "Database is unavailable", detail: dict | None = None) -> None:
        super().__init__(message, code=self.code, status_code=self.status_code, detail=detail)


class RateLimitApiError(ApiError):
    code = "RATE_LIMITED"
    status_code = 429

    def __init__(self, message: str = "Rate limit exceeded", detail: dict | None = None) -> None:
        super().__init__(message, code=self.code, status_code=self.status_code, detail=detail)
