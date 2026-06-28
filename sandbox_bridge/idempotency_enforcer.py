from __future__ import annotations

import hashlib
import json

from sandbox_bridge.sanitizer import bridge_boundary, sanitize_bridge_payload


class IdempotencyEnforcer:
    def __init__(self) -> None:
        self._records: dict[str, dict] = {}

    def generate_key(self, request: dict) -> str:
        clean = sanitize_bridge_payload(request)
        payload = json.dumps(clean, sort_keys=True, default=str)
        return "bridge_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]

    def check_duplicate(self, request: dict) -> dict:
        key = self.generate_key(request)
        if key in self._records:
            return {"duplicate": True, "idempotency_key": key, "cached_response": self._records[key], **bridge_boundary()}
        return {"duplicate": False, "idempotency_key": key, "cached_response": {}, **bridge_boundary()}

    def record_request(self, request: dict, response: dict) -> dict:
        key = self.generate_key(request)
        clean_response = sanitize_bridge_payload(response)
        self._records[key] = clean_response
        return {"recorded": True, "idempotency_key": key, **bridge_boundary()}
