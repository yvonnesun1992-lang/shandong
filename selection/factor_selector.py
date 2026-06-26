from __future__ import annotations


class FactorSelector:
    def __init__(self, stability_threshold: float = 0.6) -> None:
        self.stability_threshold = stability_threshold

    def select(self, factor_rows: list[dict]) -> dict:
        best: list[str] = []
        rejected: list[dict] = []
        for row in factor_rows:
            factor = str(row.get("factor", "unknown"))
            reasons = []
            if float(row.get("ic_mean", 0.0) or 0.0) <= 0:
                reasons.append("ic<=0")
            if float(row.get("ic_ir", 0.0) or 0.0) <= 1:
                reasons.append("ic_ir<=1")
            if float(row.get("ic_stability", row.get("stability", 0.0)) or 0.0) < self.stability_threshold:
                reasons.append("stability_below_threshold")
            if reasons:
                rejected.append({"factor": factor, "reason": ",".join(reasons)})
            else:
                best.append(factor)
        return {"best_factors": best, "rejected_factors": rejected}
