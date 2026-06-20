from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

from src.auth import User
from src.core.rbac import require_permission


def _b64url_encode(payload: bytes) -> str:
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def _b64url_decode(payload: str) -> bytes:
    padded = payload + "=" * (-len(payload) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


class JwtAuthService:
    def __init__(self, signing_key: str = "local-demo-key", issuer: str = "shandong-saas") -> None:
        self.signing_key = str(signing_key)
        self.issuer = issuer
        self._users: dict[str, User] = {}

    def signup(self, user_id: str, role: str = "user") -> User:
        user = User(user_id=user_id, role=role)
        self._users[user.user_id] = user
        return user

    def login(self, user_id: str) -> str:
        user = self._users.get(User(user_id).user_id)
        if user is None:
            user = self.signup(user_id)
        now = int(time.time())
        return self._encode(
            {
                "iss": self.issuer,
                "sub": user.user_id,
                "role": user.role,
                "iat": now,
                "exp": now + 3600,
            }
        )

    def validate_session(self, jwt_value: str) -> dict:
        payload = self._decode(jwt_value)
        if payload is None:
            return {"valid": False, "reason": "invalid_jwt", "user": None}
        if int(payload.get("exp", 0)) < int(time.time()):
            return {"valid": False, "reason": "expired_jwt", "user": None}
        user = User(payload.get("sub", "anonymous"), role=payload.get("role", "viewer"))
        return {"valid": True, "reason": "ok", "user": user.as_dict()}

    def protected_route(self, jwt_value: str, resource: str, action: str) -> dict:
        session = self.validate_session(jwt_value)
        if not session["valid"]:
            return {"allowed": False, "reason": session["reason"]}
        user = User(session["user"]["user_id"], role=session["user"]["role"])
        decision = require_permission(user, resource, action)
        return {"allowed": decision["allowed"], "reason": "ok" if decision["allowed"] else "forbidden", "decision": decision}

    def _encode(self, payload: dict) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        header_part = _b64url_encode(json.dumps(header, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        payload_part = _b64url_encode(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        signature = self._sign(f"{header_part}.{payload_part}")
        return f"{header_part}.{payload_part}.{signature}"

    def _decode(self, jwt_value: str) -> dict | None:
        parts = str(jwt_value).split(".")
        if len(parts) != 3:
            return None
        signed = f"{parts[0]}.{parts[1]}"
        expected = self._sign(signed)
        if not hmac.compare_digest(expected, parts[2]):
            return None
        try:
            return json.loads(_b64url_decode(parts[1]).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    def _sign(self, payload: str) -> str:
        digest = hmac.new(self.signing_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()
        return _b64url_encode(digest)
