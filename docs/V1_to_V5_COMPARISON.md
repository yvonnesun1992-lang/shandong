# V1 to V5 Comparison

## Summary

V1 is a legacy research system. It records the incremental path from paper trading to factor research and multi-factor alpha experiments.

V5 is the current alpha engine system. It keeps the V1 research history intact while exposing a cleaner production-facing alpha pipeline.

## V1 System

- Research-oriented modules
- Incremental development history from V1.0 to V1.3
- Useful for understanding how the quant stack evolved
- Keeps paper trading, strategy ensemble, factor research, and multi-factor alpha experiments visible

## V5 System

- Current core alpha identity: `V5.0-alpha-system`
- Unified entrypoints for factor scoring, alpha model construction, and portfolio construction
- Clean module boundaries around alpha, factor scoring, portfolio, risk, regime, and evaluation
- Reuses proven V1.3 logic rather than duplicating or deleting legacy code

## Key Difference

| Area | V1 Legacy Research System | V5 Alpha Engine System |
| --- | --- | --- |
| Purpose | Explore and validate quant research components | Run the current alpha system through unified entrypoints |
| Structure | Version-history modules | Current system modules under `quant_core_v5` |
| Code Policy | Preserved as legacy | Thin wrappers and orchestration around V1.3 logic |
| Risk | Research controls and tests | Current alpha-system risk and causal backtest path |
| Portfolio | Paper and factor simulations | Optimized allocation interface |

## Coexistence

V1 and V5 can run at the same time because V5 imports legacy logic through stable wrappers instead of moving old files.
