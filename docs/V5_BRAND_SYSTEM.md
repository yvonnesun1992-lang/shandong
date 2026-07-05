# V5.44 Shandong Quant Brand System

V5.44 unifies the local product into the Shandong Quantitative System brand.

## Scope

- Adds locked brand config.
- Adds brand design system.
- Adds cleaned deep navy + gold mountain candlestick logo.
- Updates frontend shell, product home, metadata, loading state, and theme tokens.
- Adds CLI brand banner.
- Adds brand consistency and safety checks.

## Positioning

Shandong Quantitative System is an institutional-grade, local-first quant research and paper trading platform.

## Safety Boundary

- No broker connection.
- No sandbox API connection.
- No secret reading.
- No account, balance, or position reading.
- No order submission.
- No real-money execution.
- No alpha, factor, or strategy logic changes.

## Assets

- Frontend logo: `web/frontend/public/brand/shandong-quant-logo.png`
- Brand reference logo: `brand_system/assets/shandong-quant-logo.png`
- Brand guide: `brand_system/BRAND_GUIDE.md`

## Verification

Run:

```bash
python -m py_compile config/v5_brand_system_config.py brand_system/design_system.py brand_system/brand_safety_validator.py brand_system/brand_orchestrator.py runtime/brand_consistency_check.py scripts/run_v544_brand_system.py
python scripts/run_v544_brand_system.py
python -m pytest tests/test_v544_brand_system.py
```
