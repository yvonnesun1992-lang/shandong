# Version Migration Map

## Migration Target

`V5.0-alpha-system` is the current quantitative alpha core system.

The V1 line is retained as the legacy research system. No V1.0-V1.3 modules are deleted or moved by this migration layer.

## Legacy Mapping

| Legacy Version | Legacy Name | V5 Mapping |
| --- | --- | --- |
| V1.0 -> Paper Trading Core | Market data, paper broker, simple strategy backtest | V5 portfolio and evaluation runtime foundation |
| V1.1 -> Risk + Multi Strategy | Regime detection, strategy ensemble, risk controls | V5 regime and risk modules |
| V1.2 -> Factor Research System | Factor matrices, IC analysis, factor scoring, factor simulation | V5 factor engine and scoring system |
| V1.3 -> Multi-Factor Alpha System | Normalization, alpha score construction, weighting, attribution | V5 alpha engine system |

## New Version Identity

- V1.0-V1.3: legacy research system
- V5.0-alpha-system: current alpha engine system

## V5 Module Mapping

| V5 Module | Source Logic |
| --- | --- |
| `quant_core_v5/alpha_engine` | Reuses V1.3 `alpha_engine` |
| `quant_core_v5/factor_engine` | Reuses V1.2 `evaluation.ic_analysis` and V1.3 factor weighting |
| `quant_core_v5/portfolio` | Reuses V1.3 multi-factor portfolio construction |
| `quant_core_v5/risk` | Reuses V1.1/V1.3 risk controls |
| `quant_core_v5/regime` | Reuses V1.1/V1.3 regime detection and adjustment |
| `quant_core_v5/evaluation` | Reuses V1.3 backtest and attribution |

## Safety Boundary

- No broker connection
- No real trading
- No real-money execution
- No external AI API
- No deletion of legacy V1 code
