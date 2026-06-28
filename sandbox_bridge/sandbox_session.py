from __future__ import annotations

from sandbox_bridge.sanitizer import bridge_boundary


class SandboxSession:
    def __init__(self) -> None:
        self.state = "DISCONNECTED"

    def start_session(self) -> dict:
        self.state = "CONNECTED_SIMULATED"
        return {"state": self.state, "simulated_only": True, **bridge_boundary()}

    def end_session(self) -> dict:
        self.state = "DISCONNECTED"
        return {"state": self.state, "simulated_only": True, **bridge_boundary()}

    def refresh_session(self) -> dict:
        self.state = "CONNECTED_SIMULATED"
        return {"state": self.state, "simulated_only": True, **bridge_boundary()}

    def status(self) -> dict:
        return {"state": self.state, "simulated_only": True, **bridge_boundary()}
