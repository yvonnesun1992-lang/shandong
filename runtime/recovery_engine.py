from __future__ import annotations

from runtime.state_checkpoint import StateCheckpoint


class RecoveryEngine:
    def __init__(self, checkpoint: StateCheckpoint) -> None:
        self.checkpoint = checkpoint

    def load_last_checkpoint(self) -> dict:
        return self.checkpoint.load_latest()

    def restore_account(self, account) -> dict:
        state = self.load_last_checkpoint()
        if not state:
            return {"restored": False, "open_orders": []}
        portfolio = state.get("portfolio", {})
        account.cash = float(portfolio.get("cash", account.cash))
        account.realized_pnl = float(portfolio.get("realized_pnl", getattr(account, "realized_pnl", 0.0)))
        account.positions = state.get("positions", portfolio.get("positions", {})) or {}
        return {"restored": True, "open_orders": state.get("open_orders", state.get("active_orders", [])), "state": state}

    def recover_engine(self, engine) -> dict:
        result = self.restore_account(engine.broker.account)
        if result["restored"] and hasattr(engine, "state_manager"):
            engine.state_manager.active_orders = result.get("open_orders", [])
        return result

