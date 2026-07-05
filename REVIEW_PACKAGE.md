# V5.47 Backtest Result Dashboard

This update adds a user-friendly backtest result dashboard. It is a UI / UX / information architecture layer only.

New files:

```text
config/v5_backtest_dashboard_config.py
backtest_dashboard/
scripts/run_v547_backtest_dashboard.py
web/frontend/app/backtest/[strategyId]/page.tsx
reports/v5_47_backtest_dashboard_report.md
tests/test_v547_backtest_dashboard.py
```

Updated files:

```text
README.md
REVIEW_PACKAGE.md
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/components/ProductionShell.tsx
web/frontend/app/lib/apiClient.ts
web/frontend/app/page.tsx
web/frontend/app/strategies/page.tsx
web/frontend/app/strategies/[strategyId]/page.tsx
web/frontend/app/styles.css
```

Product changes:

```text
Backtest result page: added
Backtest result model: added
Conclusion engine: added
Metric explanation copy: added
Chart data models: added
Risk analysis: added
Action panel: added
Core / advanced metric cards: added
API endpoints: /api/v5/backtest-dashboard/*
Strategy Center one-click backtest route: /backtest/{strategyId}
Advanced metrics: collapsed by default
```

Safety boundaries:

```text
No broker connection
No sandbox API
No secret read
No account read
No balance read
No position read
No order preview
No order submission
No real money
No auto trading
No alpha model change
No factor logic change
No strategy logic change
This is UI / UX / information architecture only
```

Validation:

```text
py_compile: passed
V5.47 CLI safety/report checks: passed
pytest tests/test_v547_backtest_dashboard.py: 5 passed
related V5.46 / V5.47 tests: 10 passed
pytest: 906 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
```

# V5.46 Strategy Center

This update adds a user-friendly strategy library for ordinary investors. It is a product UI / information architecture layer only.

New files:

```text
config/v5_strategy_center_config.py
strategy_center/
scripts/run_v546_strategy_center.py
web/frontend/app/strategies/page.tsx
web/frontend/app/strategies/[strategyId]/page.tsx
reports/v5_46_strategy_center_report.md
tests/test_v546_strategy_center.py
```

Updated files:

```text
README.md
REVIEW_PACKAGE.md
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/components/ProductionShell.tsx
web/frontend/app/lib/apiClient.ts
web/frontend/app/page.tsx
web/frontend/app/styles.css
```

Product changes:

```text
Strategy Center page: added
Strategy detail page: added
Strategy catalog/search/filter/recommendation/card/detail models: added
Backtest preview and paper-trading preview: added as local preview only
API endpoints: /api/v5/strategy-center/*
Navigation: strategy entry renamed to 策略中心
Advanced tools remain under Advanced Settings
```

Safety boundaries:

```text
No broker connection
No sandbox API
No secret read
No account read
No balance read
No position read
No order preview
No order submission
No real money
No alpha model change
No factor logic change
No strategy logic change
This is UI / UX / information architecture only
```

Validation:

```text
py_compile: passed
V5.46 CLI safety/report checks: passed
pytest tests/test_v546_strategy_center.py: 5 passed
related UI / product tests: 9 passed
pytest: 901 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
```

# V5.45 Product UI Prototype

This update reframes the V5 frontend from an engineering-oriented dashboard into a user-friendly quant investment product prototype.

New files:

```text
product_ui/__init__.py
product_ui/init.py
product_ui/one_click_investment.py
product_ui/ui_design_system.py
tests/test_v545_product_ui_prototype.py
```

Updated files:

```text
README.md
REVIEW_PACKAGE.md
web/frontend/app/components/ProductionShell.tsx
web/frontend/app/page.tsx
web/frontend/app/styles.css
```

Product UI changes:

```text
Home page: investor-facing product dashboard
Core CTA: one-click investment prototype
Visible navigation: Home / Strategy / Backtest / Paper Trading / Risk / Data / Help
Engineering tools: moved under Advanced Settings
Recommended strategy module: added
Simplified return chart: added
Recent run records: added
Safety notices: added
```

Safety boundaries:

```text
No broker connection
No sandbox API
No secret read
No account read
No balance read
No position read
No order submission
No real money
No alpha model change
No factor logic change
No strategy logic change
This is UI / UX / information architecture only
```

Validation:

```text
py_compile product_ui modules: passed
pytest tests/test_v545_product_ui_prototype.py: 4 passed
related UI / product / brand tests: 18 passed
pytest: 896 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
pnpm run build: blocked by local pnpm sharp build-approval policy, not by frontend source errors
```

# V5.44: Shandong Quant Brand System

This update adds an institutional brand system for Shandong Quantitative System / 山洞量化系统.

New files:

```text
config/v5_brand_system_config.py
brand_system/BRAND_GUIDE.md
brand_system/__init__.py
brand_system/design_system.py
brand_system/brand_safety_validator.py
brand_system/brand_orchestrator.py
brand_system/assets/shandong-quant-logo.png
runtime/brand_consistency_check.py
scripts/run_v544_brand_system.py
web/frontend/app/components/BrandLogo.tsx
web/frontend/public/brand/shandong-quant-logo.png
docs/V5_BRAND_SYSTEM.md
tests/test_v544_brand_system.py
```

Updated files:

```text
README.md
REVIEW_PACKAGE.md
scripts/start_shandong_mac.command
scripts/start_shandong_windows.bat
src/api/v2/server.py
web/frontend/app/components/LoadingState.tsx
web/frontend/app/components/ProductionShell.tsx
web/frontend/app/layout.tsx
web/frontend/app/page.tsx
web/frontend/app/styles.css
```

Branding:

```text
Brand name: Shandong Quantitative System
Chinese name: 山洞量化系统
Logo: deep navy + gold mountain candlestick style
Theme: institutional_quant
Frontend style: institutional dark navy + gold accent
CLI banner: added
README branding: added
```

Safety boundaries:

```text
Broker connection: no
Sandbox API connection: no
Secret read: no
Account read: no
Balance read: no
Position read: no
Order preview: no
Order submission: no
Real money: no
Alpha model changed: no
Factor logic changed: no
Strategy logic changed: no
This is brand system only: yes
```

Validation:

```text
py_compile: passed
run_v544_brand_system.py: passed, verdict PASS
pytest tests/test_v544_brand_system.py: 4 passed
pytest tests/test_v540_product_home_dashboard.py tests/test_v544_brand_system.py: 8 passed
related V5 navigation compatibility tests: 269 passed
pytest: 892 passed
system_doctor: OK
frontend structure check: passed
```

# V5.38: Sandbox Read-Only Connector Final Review Board

This update adds a local-only read-only connector final review board. It reviews V5.34 mock replay evidence, V5.35 fault injection evidence, V5.36 stability gate evidence, and V5.37 evidence pack material without enabling runtime, sandbox API, credential read, account read, balance read, position read, order preview, order submission, broker connection, real money, or production trading.

New files:

```text
config/v5_read_only_final_review_config.py
sandbox_read_only_final_review/__init__.py
sandbox_read_only_final_review/init.py
sandbox_read_only_final_review/final_review_charter.py
sandbox_read_only_final_review/reviewer_role_matrix.py
sandbox_read_only_final_review/evidence_review_matrix.py
sandbox_read_only_final_review/risk_acceptance_matrix.py
sandbox_read_only_final_review/missing_requirement_register.py
sandbox_read_only_final_review/final_review_decision.py
sandbox_read_only_final_review/final_review_audit_trail.py
sandbox_read_only_final_review/final_review_safety_validator.py
sandbox_read_only_final_review/final_review_orchestrator.py
sandbox_read_only_final_review/sandbox_read_only_final_review_report.py
scripts/run_v538_read_only_final_review.py
web/frontend/app/v5-read-only-final-review/page.tsx
tests/test_v538_read_only_final_review.py
docs/V5_READ_ONLY_FINAL_REVIEW.md
reports/v5_38_sandbox_read_only_final_review_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Final review coverage:

```text
Final review charter: covered
Reviewer role matrix: covered
Evidence review matrix: covered
Risk acceptance matrix: covered and not ready by design
Missing requirement register: covered
Final review decision: covered and review-only by design
Final review audit trail: covered with placeholders only
Final review safety validation: covered and warning by design
API endpoint coverage: covered
Frontend structure coverage: covered
```

Safety boundaries:

```text
Final review runtime: no
Final review pass: no
Read-only connector allowed: no
Sandbox API connection: no
Credential read: no
Account read: no
Balance read: no
Position read: no
Order preview: no
Order submission: no
Real broker connection: no
Broker SDK imports: no
Provider portal access: no
Raw real provider payload storage: no
Real provider endpoint URL field: no
Unredacted real balances or positions: no
Real funds: no
External network requests: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is sandbox read-only final review board only: yes
```

Validation:

```text
py_compile: passed
run_v538_read_only_final_review.py: passed, WARNING verdict by design because final review remains review-only
run_v538_read_only_final_review.py --provider alpaca: passed, WARNING verdict by design
run_v538_read_only_final_review.py --provider ibkr: passed, WARNING verdict by design
run_v538_read_only_final_review.py --check evidence: passed, WARNING verdict by design
run_v538_read_only_final_review.py --check risks: passed, WARNING verdict by design
run_v538_read_only_final_review.py --check missing: passed, WARNING verdict by design
run_v538_read_only_final_review.py --check decision: passed, WARNING verdict by design
run_v538_read_only_final_review.py --check safety: passed, WARNING verdict by design
pytest tests/test_v538_read_only_final_review.py: 4 passed
pytest: 868 passed
system_doctor: OK
frontend structure check: passed
```

# V5.37: Sandbox Read-Only Connector Evidence Pack

This update adds a local-only read-only connector evidence pack. It consolidates V5.34 mock replay evidence, V5.35 fault injection evidence, and V5.36 stability gate evidence into a single evidence package without enabling runtime, sandbox API, credential read, account read, balance read, position read, order preview, order submission, broker connection, real money, or production trading.

New files:

```text
config/v5_read_only_evidence_pack_config.py
sandbox_read_only_evidence_pack/__init__.py
sandbox_read_only_evidence_pack/init.py
sandbox_read_only_evidence_pack/evidence_source_collector.py
sandbox_read_only_evidence_pack/evidence_completeness_check.py
sandbox_read_only_evidence_pack/redaction_evidence_pack.py
sandbox_read_only_evidence_pack/schema_evidence_pack.py
sandbox_read_only_evidence_pack/audit_evidence_pack.py
sandbox_read_only_evidence_pack/order_blocking_evidence_pack.py
sandbox_read_only_evidence_pack/safety_boundary_evidence_pack.py
sandbox_read_only_evidence_pack/evidence_pack_decision.py
sandbox_read_only_evidence_pack/evidence_pack_safety_validator.py
sandbox_read_only_evidence_pack/evidence_pack_orchestrator.py
sandbox_read_only_evidence_pack/sandbox_read_only_evidence_pack_report.py
scripts/run_v537_read_only_evidence_pack.py
web/frontend/app/v5-read-only-evidence-pack/page.tsx
tests/test_v537_read_only_evidence_pack.py
docs/V5_READ_ONLY_EVIDENCE_PACK.md
reports/v5_37_sandbox_read_only_evidence_pack_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Evidence pack coverage:

```text
Evidence source collection: covered
Evidence completeness check: covered
Redaction evidence pack: covered
Schema evidence pack: covered
Audit evidence pack: covered
Order blocking evidence pack: covered
Safety boundary evidence pack: covered
Evidence pack decision: covered and evidence-only by design
Evidence pack safety validation: covered and warning by design
API endpoint coverage: covered
Frontend structure coverage: covered
```

Safety boundaries:

```text
Evidence pack runtime: no
Evidence pack pass: no
Read-only connector allowed: no
Sandbox API connection: no
Credential read: no
Account read: no
Balance read: no
Position read: no
Order preview: no
Order submission: no
Real broker connection: no
Broker SDK imports: no
Provider portal access: no
Raw real provider payload storage: no
Real provider endpoint URL field: no
Unredacted real balances or positions: no
Real funds: no
External network requests: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is sandbox read-only evidence pack only: yes
```

Validation:

```text
py_compile: passed
run_v537_read_only_evidence_pack.py: passed, WARNING verdict by design because evidence pack remains evidence-only
run_v537_read_only_evidence_pack.py --provider alpaca: passed, WARNING verdict by design
run_v537_read_only_evidence_pack.py --provider ibkr: passed, WARNING verdict by design
run_v537_read_only_evidence_pack.py --check sources: passed
run_v537_read_only_evidence_pack.py --check completeness: passed, WARNING verdict by design
run_v537_read_only_evidence_pack.py --check redaction: passed
run_v537_read_only_evidence_pack.py --check schema: passed
run_v537_read_only_evidence_pack.py --check order-blocking: passed
run_v537_read_only_evidence_pack.py --check decision: passed, WARNING verdict by design
run_v537_read_only_evidence_pack.py --check safety: passed, WARNING verdict by design
pytest tests/test_v537_read_only_evidence_pack.py: 4 passed
pytest: 863 passed
system_doctor: OK
frontend structure check: passed
```

# V5.36: Sandbox Read-Only Connector Stability Gate

This update adds a local-only sandbox read-only connector stability gate. It aggregates V5.34 mock replay evidence and V5.35 fault injection evidence, then keeps the connector gate blocked by design. Even when replay, fault, redaction, schema, audit, and order-path evidence is acceptable, V5.36 cannot enable sandbox API access, credential reads, account reads, balance reads, position reads, order preview, order submission, broker connection, real money, or production trading.

New files:

```text
config/v5_read_only_stability_gate_config.py
sandbox_read_only_stability_gate/__init__.py
sandbox_read_only_stability_gate/init.py
sandbox_read_only_stability_gate/replay_evidence_collector.py
sandbox_read_only_stability_gate/fault_evidence_collector.py
sandbox_read_only_stability_gate/redaction_stability_check.py
sandbox_read_only_stability_gate/schema_stability_check.py
sandbox_read_only_stability_gate/audit_stability_check.py
sandbox_read_only_stability_gate/order_path_stability_check.py
sandbox_read_only_stability_gate/stability_gate_decision.py
sandbox_read_only_stability_gate/stability_gate_safety_validator.py
sandbox_read_only_stability_gate/stability_gate_orchestrator.py
sandbox_read_only_stability_gate/sandbox_read_only_stability_gate_report.py
scripts/run_v536_read_only_stability_gate.py
web/frontend/app/v5-read-only-stability-gate/page.tsx
tests/test_v536_read_only_stability_gate.py
docs/V5_READ_ONLY_STABILITY_GATE.md
reports/v5_36_sandbox_read_only_stability_gate_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Stability gate coverage:

```text
Replay evidence aggregation: covered
Fault evidence aggregation: covered
Redaction stability check: covered
Schema stability check: covered
Audit stability check: covered
Order path stability check: covered
Gate decision: covered and blocked by design
Safety validation: covered and warning by design
API endpoint coverage: covered
Frontend structure coverage: covered
```

Safety boundaries:

```text
Stability gate runtime: no
Sandbox API connection: no
Credential read: no
Account read: no
Balance read: no
Position read: no
Order preview: no
Order submission: no
Read-only connector allowed: no
Stability gate passed: no
Real broker connection: no
Broker SDK imports: no
Provider portal access: no
Raw real provider payload storage: no
Real provider endpoint URL field: no
Unredacted real balances or positions: no
Real funds: no
External network requests: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is sandbox read-only stability gate evidence only: yes
```

Validation:

```text
py_compile: passed
run_v536_read_only_stability_gate.py: passed, WARNING verdict by design because the stability gate remains blocked
run_v536_read_only_stability_gate.py --provider alpaca: passed, WARNING verdict by design
run_v536_read_only_stability_gate.py --provider ibkr: passed, WARNING verdict by design
run_v536_read_only_stability_gate.py --check replay: passed
run_v536_read_only_stability_gate.py --check fault: passed
run_v536_read_only_stability_gate.py --check redaction: passed
run_v536_read_only_stability_gate.py --check schema: passed
run_v536_read_only_stability_gate.py --check order-path: passed
run_v536_read_only_stability_gate.py --check decision: passed, WARNING verdict by design
run_v536_read_only_stability_gate.py --check safety: passed, WARNING verdict by design
pytest tests/test_v536_read_only_stability_gate.py: 4 passed
pytest: 859 passed
system_doctor: OK
frontend structure check: passed
```

# V5.35: Sandbox Read-Only Connector Fault Injection

This update adds a local-only read-only connector fault injection suite. It defines mock fault payloads, schema fault validation, redaction failure detection, stale snapshot detection, audit failure simulation, rate limit fault simulation, order path intrusion detection, fault runner, safety validation, API endpoints, frontend page, documentation, report, CLI, and tests without enabling runtime, sandbox API, credential read, account read, balance read, position read, order preview, order submission, broker connection, or real money paths.

New files:

```text
config/v5_read_only_fault_injection_config.py
sandbox_read_only_fault_injection/__init__.py
sandbox_read_only_fault_injection/init.py
sandbox_read_only_fault_injection/fault_payload_catalog.py
sandbox_read_only_fault_injection/fault_schema_validator.py
sandbox_read_only_fault_injection/redaction_failure_detector.py
sandbox_read_only_fault_injection/stale_snapshot_detector.py
sandbox_read_only_fault_injection/audit_failure_simulator.py
sandbox_read_only_fault_injection/rate_limit_fault_simulator.py
sandbox_read_only_fault_injection/order_path_intrusion_detector.py
sandbox_read_only_fault_injection/fault_injection_runner.py
sandbox_read_only_fault_injection/fault_injection_safety_validator.py
sandbox_read_only_fault_injection/fault_injection_orchestrator.py
sandbox_read_only_fault_injection/sandbox_read_only_fault_injection_report.py
scripts/run_v535_read_only_fault_injection.py
web/frontend/app/v5-read-only-fault-injection/page.tsx
tests/test_v535_read_only_fault_injection.py
docs/V5_READ_ONLY_FAULT_INJECTION.md
reports/v5_35_sandbox_read_only_fault_injection_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Fault coverage:

```text
Redaction failure: covered
Malformed account snapshot: covered
Malformed balance snapshot: covered
Malformed position snapshot: covered
Stale snapshot: covered
Rate limit error: covered
Audit write failure: covered
Unexpected raw provider payload placeholder: covered
Unexpected account reference exposure: covered
Unexpected numeric balance or position exposure: covered
Unexpected order preview / submission path: covered
```

Safety boundaries:

```text
Fault injection runtime: no
Sandbox API connection: no
Credential read: no
Account read: no
Balance read: no
Position read: no
Order preview: no
Order submission: no
Real broker connection: no
Broker SDK imports: no
Provider portal access: no
Account, balance, or position read: no
Sandbox orders: no
Real orders: no
Raw real provider payload storage: no
Real provider endpoint URL field: no
Unredacted real balances or positions: no
Real funds: no
External network requests: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is sandbox read-only fault injection only: yes
```

Validation:

```text
py_compile: passed
run_v535_read_only_fault_injection.py: passed, WARNING verdict by design because all injected faults are blocked/warned
run_v535_read_only_fault_injection.py --provider alpaca: passed, WARNING verdict by design
run_v535_read_only_fault_injection.py --provider ibkr: passed, WARNING verdict by design
run_v535_read_only_fault_injection.py --check redaction: passed, WARNING verdict by design
run_v535_read_only_fault_injection.py --check stale: passed, WARNING verdict by design
run_v535_read_only_fault_injection.py --check order-intrusion: passed, WARNING verdict by design
run_v535_read_only_fault_injection.py --check safety: passed, WARNING verdict by design
pytest tests/test_v535_read_only_fault_injection.py: 4 passed
pytest: 855 passed
system_doctor: OK
frontend structure check: passed
```

# V5.34: Sandbox Read-Only Connector Mock Replay

This update adds a local-only read-only connector mock replay layer. It defines redacted mock payloads, schema validation, redaction validation, replay execution, audit replay, safety validation, API endpoints, frontend page, documentation, report, CLI, and tests without enabling runtime, sandbox API, credential read, account read, balance read, position read, order preview, order submission, broker connection, or real money paths.

New files:

```text
config/v5_read_only_mock_replay_config.py
sandbox_read_only_mock_replay/__init__.py
sandbox_read_only_mock_replay/init.py
sandbox_read_only_mock_replay/mock_read_only_payloads.py
sandbox_read_only_mock_replay/read_only_schema_validator.py
sandbox_read_only_mock_replay/redaction_replay_validator.py
sandbox_read_only_mock_replay/read_only_replay_runner.py
sandbox_read_only_mock_replay/read_only_audit_replay.py
sandbox_read_only_mock_replay/read_only_mock_replay_safety_validator.py
sandbox_read_only_mock_replay/read_only_mock_replay_orchestrator.py
sandbox_read_only_mock_replay/sandbox_read_only_mock_replay_report.py
scripts/run_v534_read_only_mock_replay.py
web/frontend/app/v5-read-only-mock-replay/page.tsx
tests/test_v534_read_only_mock_replay.py
docs/V5_READ_ONLY_MOCK_REPLAY.md
reports/v5_34_sandbox_read_only_mock_replay_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Mock replay runtime: no
Sandbox API connection: no
Credential read: no
Account read: no
Balance read: no
Position read: no
Order preview: no
Order submission: no
Real broker connection: no
Broker SDK imports: no
Provider portal access: no
Account, balance, or position read: no
Sandbox orders: no
Real orders: no
Raw provider payload storage: no
Provider endpoint URL field: no
Unredacted balances or positions: no
Real funds: no
External network requests: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is sandbox read-only mock replay only: yes
```

Validation:

```text
py_compile: passed
run_v534_read_only_mock_replay.py: passed, WARNING verdict by design because read-only mock replay runtime remains disabled
run_v534_read_only_mock_replay.py --provider alpaca: passed, WARNING verdict by design
run_v534_read_only_mock_replay.py --provider ibkr: passed, WARNING verdict by design
run_v534_read_only_mock_replay.py --check schema: passed
run_v534_read_only_mock_replay.py --check redaction: passed
run_v534_read_only_mock_replay.py --check safety: passed, WARNING verdict by design
pytest tests/test_v534_read_only_mock_replay.py: 4 passed
pytest: 851 passed
system_doctor: OK
frontend structure check: passed
```

# V5.33: Sandbox Dry-Run Read-Only Connector Blueprint

This update adds a design-only sandbox read-only connector blueprint. It defines read-only scope, credential scope, account snapshot schema, balance snapshot schema, position snapshot schema, redaction policy, rate limit policy, audit policy, safety validation, API endpoints, frontend page, documentation, report, CLI, and tests without enabling runtime, sandbox API, credential read, account read, balance read, position read, order preview, order submission, broker connection, or real money paths.

New files:

```text
config/v5_read_only_connector_config.py
sandbox_read_only_connector/__init__.py
sandbox_read_only_connector/init.py
sandbox_read_only_connector/read_only_scope_definition.py
sandbox_read_only_connector/read_only_credential_scope.py
sandbox_read_only_connector/account_snapshot_schema.py
sandbox_read_only_connector/balance_snapshot_schema.py
sandbox_read_only_connector/position_snapshot_schema.py
sandbox_read_only_connector/read_only_redaction_policy.py
sandbox_read_only_connector/read_only_rate_limit_policy.py
sandbox_read_only_connector/read_only_audit_policy.py
sandbox_read_only_connector/read_only_safety_validator.py
sandbox_read_only_connector/read_only_connector_orchestrator.py
sandbox_read_only_connector/sandbox_read_only_connector_report.py
scripts/run_v533_read_only_connector.py
web/frontend/app/v5-read-only-connector/page.tsx
tests/test_v533_read_only_connector.py
docs/V5_READ_ONLY_CONNECTOR_BLUEPRINT.md
reports/v5_33_sandbox_read_only_connector_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Read-only runtime: no
Sandbox API connection: no
Credential read: no
Account read: no
Balance read: no
Position read: no
Order preview: no
Order submission: no
Real broker connection: no
Broker SDK imports: no
Provider portal access: no
Credential read or storage: no
Account, balance, or position read: no
Sandbox orders: no
Real orders: no
Raw provider payload storage: no
Provider endpoint URL field: no
Unredacted balances or positions: no
Real funds: no
External network requests: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is sandbox dry-run read-only connector blueprint only: yes
```

Validation:

```text
py_compile: passed
run_v533_read_only_connector.py: passed, WARNING verdict by design because read-only connector runtime remains disabled
run_v533_read_only_connector.py --provider alpaca: passed, WARNING verdict by design
run_v533_read_only_connector.py --provider ibkr: passed, WARNING verdict by design
run_v533_read_only_connector.py --check scope: passed, WARNING verdict by design
run_v533_read_only_connector.py --check redaction: passed, WARNING verdict by design
run_v533_read_only_connector.py --check safety: passed, WARNING verdict by design
frontend structure check: passed
pytest tests/test_v533_read_only_connector.py: 4 passed
pytest full suite: 847 passed
system_doctor: OK
security scan: safe true, findings 0
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for user review unless explicitly authorized
```

# V5.32: Sandbox Dry-Run Controlled Enablement Blueprint

This update adds a design-only controlled enablement blueprint for a future path from V5.31 `NO_GO` toward a controlled dry-run process. It defines controlled enablement conditions, staged unlock planning, feature flag dependencies, secret-read conditions, sandbox API conditions, account-read conditions, order-preview conditions, order-submission blocking, emergency stop conditions, decision records, safety validation, API endpoints, frontend page, documentation, report, CLI, and tests without enabling runtime, controlled GO, sandbox API, credential read, account read, order preview, order submission, broker connection, or real money paths.

New files:

```text
config/v5_controlled_enablement_config.py
sandbox_controlled_enablement/__init__.py
sandbox_controlled_enablement/init.py
sandbox_controlled_enablement/controlled_enablement_conditions.py
sandbox_controlled_enablement/staged_unlock_plan.py
sandbox_controlled_enablement/feature_flag_dependency_graph.py
sandbox_controlled_enablement/secret_read_enablement_conditions.py
sandbox_controlled_enablement/sandbox_api_enablement_conditions.py
sandbox_controlled_enablement/account_read_enablement_conditions.py
sandbox_controlled_enablement/order_preview_enablement_conditions.py
sandbox_controlled_enablement/order_submission_blocker.py
sandbox_controlled_enablement/emergency_stop_conditions.py
sandbox_controlled_enablement/controlled_enablement_decision_record.py
sandbox_controlled_enablement/controlled_enablement_safety_validator.py
sandbox_controlled_enablement/controlled_enablement_orchestrator.py
sandbox_controlled_enablement/sandbox_controlled_enablement_report.py
scripts/run_v532_controlled_enablement.py
web/frontend/app/v5-controlled-enablement/page.tsx
tests/test_v532_controlled_enablement.py
docs/V5_CONTROLLED_ENABLEMENT_BLUEPRINT.md
reports/v5_32_sandbox_controlled_enablement_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Controlled enablement runtime: no
Controlled GO: no
Sandbox API connection: no
Secret read: no
Account read: no
Order preview: no
Order submission: no
Real broker connection: no
Broker SDK imports: no
Provider portal access: no
Credential read or storage: no
Account, balance, or position read: no
Sandbox orders: no
Real orders: no
Raw provider payload storage: no
Provider endpoint URL field: no
Real funds: no
External network requests: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is sandbox dry-run controlled enablement blueprint only: yes
Final decision remains CONTROLLED_GO_BLOCKED: yes
```

Validation:

```text
py_compile: passed
run_v532_controlled_enablement.py: passed, WARNING verdict by design because controlled GO remains blocked
run_v532_controlled_enablement.py --provider alpaca: passed, WARNING verdict by design
run_v532_controlled_enablement.py --provider ibkr: passed, WARNING verdict by design
run_v532_controlled_enablement.py --check conditions: passed, WARNING verdict by design
run_v532_controlled_enablement.py --check feature-flags: passed, WARNING verdict by design
run_v532_controlled_enablement.py --check decision: passed, WARNING verdict by design, controlled_go_enabled false
run_v532_controlled_enablement.py --check safety: passed, WARNING verdict by design
frontend structure check: passed
pytest tests/test_v532_controlled_enablement.py: 4 passed
pytest full suite: 843 passed
system_doctor: OK
security scan: safe true, findings 0
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for user review unless explicitly authorized
```

# V5.31: Sandbox Dry-Run Final Preflight Packet

This update adds a design-only final sandbox dry-run preflight packet. It defines the final preflight checklist, artifact manifest, blocking item register, preflight evidence digest, final NO-GO record, preflight audit trail, safety validation, API endpoints, frontend page, and documentation without enabling preflight runtime, packet approval, sandbox API, credential read, account read, broker connection, order submission, or real money paths.

New files:

```text
config/v5_sandbox_preflight_packet_config.py
sandbox_preflight_packet/__init__.py
sandbox_preflight_packet/init.py
sandbox_preflight_packet/final_preflight_checklist.py
sandbox_preflight_packet/artifact_manifest.py
sandbox_preflight_packet/blocking_item_register.py
sandbox_preflight_packet/preflight_evidence_digest.py
sandbox_preflight_packet/final_decision_record.py
sandbox_preflight_packet/preflight_audit_trail.py
sandbox_preflight_packet/preflight_safety_validator.py
sandbox_preflight_packet/preflight_packet_orchestrator.py
sandbox_preflight_packet/sandbox_preflight_packet_report.py
scripts/run_v531_sandbox_preflight_packet.py
web/frontend/app/v5-sandbox-preflight-packet/page.tsx
tests/test_v531_sandbox_preflight_packet.py
docs/V5_SANDBOX_PREFLIGHT_PACKET.md
reports/v5_31_sandbox_preflight_packet_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Preflight runtime: no
Packet approval: no
Sandbox API connection: no
Credential read: no
Account read: no
Provider portal access: no
Real broker connection: no
Broker SDK imports: no
Account creation: no
API key creation: no
Balance/position read: no
Order submission: no
Sandbox orders: no
Real orders: no
Raw provider payload storage: no
Provider endpoint URL field: no
Real funds: no
External network requests: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is sandbox dry-run final preflight packet only: yes
Final decision remains NO_GO: yes
```

Validation:

```text
py_compile: passed
run_v531_sandbox_preflight_packet.py: passed, WARNING verdict by design because final decision remains NO_GO
run_v531_sandbox_preflight_packet.py --provider alpaca: passed, WARNING verdict by design
run_v531_sandbox_preflight_packet.py --provider ibkr: passed, WARNING verdict by design
run_v531_sandbox_preflight_packet.py --check checklist: passed, WARNING verdict by design
run_v531_sandbox_preflight_packet.py --check artifacts: passed, WARNING verdict by design
run_v531_sandbox_preflight_packet.py --check decision: passed, WARNING verdict by design, sandbox_dry_run_allowed false
run_v531_sandbox_preflight_packet.py --check safety: passed, WARNING verdict by design
frontend structure check: passed
pytest tests/test_v531_sandbox_preflight_packet.py: 4 passed
pytest full suite: 839 passed
system_doctor: OK
security scan: safe true, findings 0
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for user review unless explicitly authorized
```

# V5.30: Sandbox Dry-Run Readiness Review Board

This update adds a design-only sandbox dry-run readiness review board. It defines the review board charter, reviewer role matrix, evidence review matrix, risk acceptance matrix, readiness scoring, Go / No-Go decision record, review audit trail, safety validation, API endpoints, frontend page, and documentation without enabling review runtime, reviewer approval, sandbox API, credential read, account read, broker connection, order submission, or real money paths.

New files:

```text
config/v5_sandbox_review_board_config.py
sandbox_review_board/__init__.py
sandbox_review_board/init.py
sandbox_review_board/review_board_charter.py
sandbox_review_board/reviewer_role_matrix.py
sandbox_review_board/evidence_review_matrix.py
sandbox_review_board/risk_acceptance_matrix.py
sandbox_review_board/readiness_scoring.py
sandbox_review_board/go_no_go_decision_record.py
sandbox_review_board/review_audit_trail.py
sandbox_review_board/review_board_safety_validator.py
sandbox_review_board/review_board_orchestrator.py
sandbox_review_board/sandbox_review_board_report.py
scripts/run_v530_sandbox_review_board.py
web/frontend/app/v5-sandbox-review-board/page.tsx
tests/test_v530_sandbox_review_board.py
docs/V5_SANDBOX_REVIEW_BOARD.md
reports/v5_30_sandbox_review_board_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Review runtime: no
Reviewer approval: no
Sandbox API connection: no
Credential read: no
Account read: no
Provider portal access: no
Real broker connection: no
Broker SDK imports: no
Account creation: no
API key creation: no
Balance/position read: no
Order submission: no
Sandbox orders: no
Real orders: no
Raw provider payload storage: no
Provider endpoint URL field: no
Real funds: no
External network requests: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is sandbox dry-run readiness review board only: yes
Go / No-Go decision remains NO_GO: yes
```

Validation:

```text
py_compile: passed
run_v530_sandbox_review_board.py: passed, verdict WARNING by design because decision remains NO_GO
run_v530_sandbox_review_board.py --provider alpaca: passed, verdict WARNING by design
run_v530_sandbox_review_board.py --provider ibkr: passed, verdict WARNING by design
run_v530_sandbox_review_board.py --check evidence: passed, verdict WARNING by design
run_v530_sandbox_review_board.py --check risks: passed, verdict WARNING by design
run_v530_sandbox_review_board.py --check decision: passed, verdict WARNING by design
run_v530_sandbox_review_board.py --check safety: passed, verdict WARNING by design
frontend structure check: passed by file/navigation/API-client presence checks
pytest tests/test_v530_sandbox_review_board.py: 4 passed
pytest full suite: 835 passed
system_doctor: OK
security scan: safe true, findings 0; no review runtime, reviewer approval, sandbox API, credential read, account read, broker SDK imports, account/order path, raw provider payload, endpoint URL, or real money path
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for user review unless explicitly authorized
```

# V5.29: Sandbox Dry-Run Launch Plan

This update adds a design-only sandbox dry-run launch plan. It defines dry-run scope, feature flags, responsibility matrix, preflight checklist, launch sequence, rollback plan, go/no-go gate, audit trail, safety validation, API endpoints, frontend page, and documentation without enabling launch runtime, sandbox API, credential read, account read, broker connection, order submission, or real money paths.

New files:

```text
config/v5_sandbox_dry_run_launch_config.py
sandbox_dry_run_launch/__init__.py
sandbox_dry_run_launch/init.py
sandbox_dry_run_launch/dry_run_scope_definition.py
sandbox_dry_run_launch/feature_flag_launch_plan.py
sandbox_dry_run_launch/responsibility_matrix.py
sandbox_dry_run_launch/preflight_checklist.py
sandbox_dry_run_launch/launch_sequence_plan.py
sandbox_dry_run_launch/dry_run_rollback_plan.py
sandbox_dry_run_launch/go_no_go_gate.py
sandbox_dry_run_launch/launch_audit_trail.py
sandbox_dry_run_launch/launch_safety_validator.py
sandbox_dry_run_launch/dry_run_launch_orchestrator.py
sandbox_dry_run_launch/sandbox_dry_run_launch_report.py
scripts/run_v529_sandbox_dry_run_launch.py
web/frontend/app/v5-sandbox-dry-run-launch/page.tsx
tests/test_v529_sandbox_dry_run_launch.py
docs/V5_SANDBOX_DRY_RUN_LAUNCH.md
reports/v5_29_sandbox_dry_run_launch_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Launch runtime: no
Sandbox API connection: no
Credential read: no
Account read: no
Provider portal access: no
Real broker connection: no
Broker SDK imports: no
Account creation: no
API key creation: no
Balance/position read: no
Order submission: no
Sandbox orders: no
Real orders: no
Raw provider payload storage: no
Provider endpoint URL field: no
Real funds: no
External network requests: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is sandbox dry-run launch plan only: yes
Go / No-Go gate remains NO_GO: yes
```

Validation:

```text
py_compile: passed
run_v529_sandbox_dry_run_launch.py: passed, verdict WARNING by design because go/no-go remains NO_GO
run_v529_sandbox_dry_run_launch.py --provider alpaca: passed, verdict WARNING by design
run_v529_sandbox_dry_run_launch.py --provider ibkr: passed, verdict WARNING by design
run_v529_sandbox_dry_run_launch.py --check preflight: passed, verdict WARNING by design
run_v529_sandbox_dry_run_launch.py --check gate: passed, verdict WARNING by design
run_v529_sandbox_dry_run_launch.py --check safety: passed, verdict WARNING by design
frontend structure check: passed by file/navigation/API-client presence checks
pytest tests/test_v529_sandbox_dry_run_launch.py: 4 passed
pytest full suite: 831 passed
system_doctor: OK
security scan: safe true, findings 0; no launch runtime, sandbox API, credential read, account read, broker SDK imports, account/order path, raw provider payload, endpoint URL, or real money path
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for user review unless explicitly authorized
```

# V5.28: Pre-Sandbox Operator Approval Gate

This update adds a design-only pre-sandbox operator approval gate. It defines approval request placeholders, evidence requirements, role policy, risk acknowledgements, gate evaluation, audit trail, safety validation, API endpoints, frontend page, and documentation without enabling approval runtime, sandbox API, credential read, broker connection, order submission, or real money paths.

New files:

```text
config/v5_pre_sandbox_approval_config.py
pre_sandbox_approval/__init__.py
pre_sandbox_approval/init.py
pre_sandbox_approval/approval_request_schema.py
pre_sandbox_approval/evidence_requirement_validator.py
pre_sandbox_approval/operator_role_policy.py
pre_sandbox_approval/risk_acknowledgement_policy.py
pre_sandbox_approval/approval_gate_evaluator.py
pre_sandbox_approval/approval_audit_trail.py
pre_sandbox_approval/approval_safety_validator.py
pre_sandbox_approval/pre_sandbox_approval_orchestrator.py
pre_sandbox_approval/pre_sandbox_approval_report.py
scripts/run_v528_pre_sandbox_approval.py
web/frontend/app/v5-pre-sandbox-approval/page.tsx
tests/test_v528_pre_sandbox_approval.py
docs/V5_PRE_SANDBOX_APPROVAL.md
reports/v5_28_pre_sandbox_approval_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Approval runtime: no
Operator approval granted: no
Sandbox API connection: no
Credential read: no
Provider portal access: no
Real broker connection: no
Broker SDK imports: no
Account creation: no
API key creation: no
Account read: no
Order submission: no
Sandbox orders: no
Real orders: no
Raw provider payload storage: no
Provider endpoint URL field: no
Real funds: no
External network requests: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is pre-sandbox approval gate design only: yes
Simulated approval cannot unlock sandbox/credential/order paths: yes
```

Validation:

```text
py_compile: passed
run_v528_pre_sandbox_approval.py: passed, verdict WARNING by design because approval gate remains blocked
run_v528_pre_sandbox_approval.py --provider alpaca: passed, verdict WARNING by design
run_v528_pre_sandbox_approval.py --provider ibkr: passed, verdict WARNING by design
run_v528_pre_sandbox_approval.py --check evidence: passed, verdict WARNING by design
run_v528_pre_sandbox_approval.py --check gate: passed, verdict WARNING by design
run_v528_pre_sandbox_approval.py --check safety: passed, verdict WARNING by design
frontend structure check: passed by file/navigation/API-client presence checks; node is not installed in this local shell, so npm build was not run
pytest tests/test_v528_pre_sandbox_approval.py: 4 passed
pytest full suite: 827 passed
system_doctor: OK
security scan: safe true, findings 0; no approval runtime, sandbox API, credential read, broker SDK imports, account/order path, raw provider payload, endpoint URL, or real money path
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, user requested direct merge after completion
```

# V5.27: Credential Vault Interface Design

This update adds a design-only credential vault interface layer for future sandbox credential handling. It defines placeholder-only references, scope and access policies, rotation/revocation runbooks, audit design, safety validation, API endpoints, frontend page, and documentation without enabling vault runtime or credential read/write paths.

New files:

```text
config/v5_credential_vault_design_config.py
credential_vault_design/__init__.py
credential_vault_design/init.py
credential_vault_design/vault_interface_contract.py
credential_vault_design/secret_scope_policy.py
credential_vault_design/secret_access_policy.py
credential_vault_design/rotation_revocation_runbook.py
credential_vault_design/vault_audit_design.py
credential_vault_design/vault_safety_validator.py
credential_vault_design/vault_design_orchestrator.py
credential_vault_design/credential_vault_design_report.py
scripts/run_v527_credential_vault_design.py
web/frontend/app/v5-credential-vault-design/page.tsx
tests/test_v527_credential_vault_design.py
docs/V5_CREDENTIAL_VAULT_DESIGN.md
reports/v5_27_credential_vault_design_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
src/system/health_check.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Vault runtime: no
Credential read: no
Credential write: no
Real vault connection: no
Provider portal access: no
Real broker connection: no
Sandbox API connection: no
Broker SDK imports: no
Credential creation: no
OAuth: no
Real account read: no
Sandbox account read: no
Order submission: no
Real orders: no
Sandbox orders: no
Raw provider payload storage: no
Provider endpoint URL field: no
Real funds: no
External network requests: no
External log upload: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is credential vault interface design only: yes
No credential path can be enabled in V5.27: yes
```

Validation:

```text
py_compile: passed
run_v527_credential_vault_design.py: passed, verdict WARNING by design because vault runtime and credential access remain blocked
run_v527_credential_vault_design.py --provider alpaca: passed, verdict WARNING by design
run_v527_credential_vault_design.py --provider ibkr: passed, verdict WARNING by design
run_v527_credential_vault_design.py --check safety: passed, verdict WARNING by design
run_v527_credential_vault_design.py --check access-policy: passed, verdict WARNING by design
frontend structure check: passed
pytest tests/test_v527_credential_vault_design.py: 4 passed
pytest full suite: 823 passed
system_doctor: OK
security scan: no real vault, no credential read/write, no broker SDK imports, no sandbox endpoint, no account/order submission, no raw provider payload, no credential values
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, user requested direct merge after completion
```

# V5.26: Provider Sandbox Readiness Evidence Pack

This update adds a sandbox readiness evidence pack for the selected provider. It summarizes local evidence from V5.23 offline replay, V5.24 fault injection, and V5.25 offline soak while keeping the sandbox entry gate blocked by design.

New files:

```text
config/v5_sandbox_readiness_evidence_config.py
provider_sandbox_evidence/__init__.py
provider_sandbox_evidence/init.py
provider_sandbox_evidence/evidence_source_collector.py
provider_sandbox_evidence/replay_evidence_summary.py
provider_sandbox_evidence/fault_evidence_summary.py
provider_sandbox_evidence/soak_evidence_summary.py
provider_sandbox_evidence/readiness_gap_analyzer.py
provider_sandbox_evidence/sandbox_entry_gate.py
provider_sandbox_evidence/evidence_safety_validator.py
provider_sandbox_evidence/evidence_orchestrator.py
provider_sandbox_evidence/provider_sandbox_evidence_report.py
scripts/run_v526_sandbox_readiness_evidence.py
web/frontend/app/v5-sandbox-evidence/page.tsx
tests/test_v526_sandbox_readiness_evidence.py
docs/V5_SANDBOX_READINESS_EVIDENCE.md
reports/v5_26_sandbox_readiness_evidence_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Evidence runtime: no
Provider portal access: no
Real broker connection: no
Sandbox API connection: no
Broker SDK imports: no
Credential creation: no
Credential storage: no
OAuth: no
Real account read: no
Sandbox account read: no
Real balance read: no
Real position read: no
Order submission: no
Real orders: no
Sandbox orders: no
Raw provider payload storage: no
Provider endpoint URL field: no
Real funds: no
External network requests: no
External log upload: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is sandbox readiness evidence pack only: yes
Sandbox entry gate remains blocked in V5.26: yes
```

Validation:

```text
py_compile: passed
run_v526_sandbox_readiness_evidence.py: passed, verdict WARNING because sandbox entry remains blocked by design
run_v526_sandbox_readiness_evidence.py --provider alpaca: passed, verdict WARNING by design
run_v526_sandbox_readiness_evidence.py --provider ibkr: passed, verdict WARNING by design
run_v526_sandbox_readiness_evidence.py --check gate: passed, verdict WARNING by design
run_v526_sandbox_readiness_evidence.py --check safety: passed, verdict WARNING by design
run_v526_sandbox_readiness_evidence.py --check gaps: passed, verdict WARNING by design
pytest tests/test_v526_sandbox_readiness_evidence.py: 5 passed
pytest full suite: 819 passed
system_doctor: OK
frontend structure check: passed
security scan: no broker SDK imports, no network calls, no sandbox endpoint, no account read, no order submission, no raw provider payload storage, no provider_endpoint_url field, no credential handling in sandbox evidence modules
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, user requested direct merge after completion
```

# V5.25: Provider Sandbox Offline Soak & Stability Gate

This update adds an offline soak and stability gate for the selected provider sandbox connector path. It validates replay stability, fault recovery stability, idempotency stability, state-machine stability, audit consistency, memory growth placeholders, error budget checks, scenario coverage, safety boundary stability, and readiness gate behavior without enabling any runtime, sandbox API, provider portal, account read, or order submission path.

New files:

```text
config/v5_provider_offline_soak_config.py
provider_offline_soak/__init__.py
provider_offline_soak/init.py
provider_offline_soak/soak_scenario_plan.py
provider_offline_soak/soak_event_generator.py
provider_offline_soak/soak_runner.py
provider_offline_soak/stability_metrics.py
provider_offline_soak/stability_gate.py
provider_offline_soak/soak_coverage_validator.py
provider_offline_soak/soak_safety_validator.py
provider_offline_soak/offline_soak_orchestrator.py
provider_offline_soak/provider_offline_soak_report.py
scripts/run_v525_provider_offline_soak.py
web/frontend/app/v5-provider-offline-soak/page.tsx
tests/test_v525_provider_offline_soak.py
docs/V5_PROVIDER_OFFLINE_SOAK.md
reports/v5_25_provider_offline_soak_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Offline soak runtime: no
Provider portal access: no
Real broker connection: no
Sandbox API connection: no
Broker SDK imports: no
Credential creation: no
Credential storage: no
OAuth: no
Real account read: no
Sandbox account read: no
Real balance read: no
Real position read: no
Order submission: no
Real orders: no
Sandbox orders: no
Raw provider payload storage: no
Provider endpoint URL field: no
Real funds: no
External network requests: no
External log upload: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is provider sandbox connector offline soak only: yes
No real path can be enabled in V5.25: yes
```

Validation:

```text
py_compile: passed
run_v525_provider_offline_soak.py: passed, verdict PASS
run_v525_provider_offline_soak.py --provider alpaca: passed, verdict PASS
run_v525_provider_offline_soak.py --provider ibkr: passed, verdict PASS
run_v525_provider_offline_soak.py --scenario short_soak_100_events: passed, verdict PASS
run_v525_provider_offline_soak.py --scenario mixed_replay_fault_soak: passed, verdict PASS
run_v525_provider_offline_soak.py --check safety: passed, verdict PASS
run_v525_provider_offline_soak.py --check gate: passed, verdict PASS
run_v525_provider_offline_soak.py --check coverage: passed, verdict PASS
pytest tests/test_v525_provider_offline_soak.py: 6 passed
pytest full suite: 814 passed
system_doctor: OK
frontend structure check: passed
security scan: no broker SDK imports, no network calls, no sandbox endpoint, no account read, no order submission, no raw provider payload storage, no provider_endpoint_url field, no credential handling in provider offline soak modules
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, user requested direct merge after completion
```

# V5.24: Provider Sandbox Connector Fault Injection Suite

This update adds an offline fault injection suite for the selected provider sandbox connector path. It validates connector timeout handling, provider rejection handling, duplicate order idempotency, stale responses, out-of-order events, partial fill mismatches, rate limit storms, audit loss, state-machine corruption, recovery rollback, kill switch triggering, and idempotency collisions without enabling any connector runtime, sandbox API, provider portal, account read, or order submission path.

New files:

```text
config/v5_provider_fault_injection_config.py
provider_fault_injection/__init__.py
provider_fault_injection/fault_scenario_catalog.py
provider_fault_injection/fault_injector.py
provider_fault_injection/fault_replay_runner.py
provider_fault_injection/fault_detection_validator.py
provider_fault_injection/fault_recovery_validator.py
provider_fault_injection/kill_switch_simulation.py
provider_fault_injection/fault_audit_trail.py
provider_fault_injection/fault_safety_validator.py
provider_fault_injection/fault_injection_orchestrator.py
provider_fault_injection/provider_fault_injection_report.py
scripts/run_v524_provider_fault_injection.py
web/frontend/app/v5-provider-fault-injection/page.tsx
tests/test_v524_provider_fault_injection.py
docs/V5_PROVIDER_FAULT_INJECTION.md
docs/superpowers/plans/2026-06-30-v524-provider-fault-injection-suite.md
reports/v5_24_provider_fault_injection_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Fault injection runtime: no
Provider portal access: no
Real broker connection: no
Sandbox API connection: no
Broker SDK imports: no
API key creation: no
Credential storage: no
OAuth: no
Real account read: no
Sandbox account read: no
Real balance read: no
Real position read: no
Order submission: no
Real orders: no
Sandbox orders: no
Raw provider payload storage: no
Provider endpoint URL field: no
Real funds: no
External network requests: no
External log upload: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is provider sandbox connector offline fault injection only: yes
No real path can be enabled in V5.24: yes
```

Validation:

```text
py_compile: passed
provider_fault_injection_report safety check: passed, verdict PASS
pytest tests/test_v523_provider_offline_replay.py tests/test_v524_provider_fault_injection.py: 13 passed
pytest tests/test_v524_provider_fault_injection.py: 6 passed
pytest full suite: 808 passed
system_doctor: OK
security scan: no broker SDK imports, no network calls, no sandbox endpoint, no account read, no order submission, no raw provider payload storage, no provider_endpoint_url field, no credential handling in provider fault injection modules
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.23: Provider Sandbox Connector Offline Replay Harness

This update adds an offline replay harness for the selected provider mock connector. It validates placeholder event sequencing, order lifecycle replay, partial fill replay, rejection replay, timeout recovery, duplicate order replay, rate limit backoff, consistency validation, audit trail generation, and replay safety boundaries without enabling any replay runtime, sandbox API, provider portal, account read, or order submission path.

New files:

```text
config/v5_provider_offline_replay_config.py
provider_offline_replay/__init__.py
provider_offline_replay/replay_event_catalog.py
provider_offline_replay/replay_event_loader.py
provider_offline_replay/replay_state_machine.py
provider_offline_replay/replay_runner.py
provider_offline_replay/replay_consistency_validator.py
provider_offline_replay/replay_failure_recovery_validator.py
provider_offline_replay/replay_audit_trail.py
provider_offline_replay/replay_safety_validator.py
provider_offline_replay/offline_replay_orchestrator.py
provider_offline_replay/provider_offline_replay_report.py
scripts/run_v523_provider_offline_replay.py
web/frontend/app/v5-provider-offline-replay/page.tsx
tests/test_v523_provider_offline_replay.py
docs/V5_PROVIDER_OFFLINE_REPLAY.md
docs/superpowers/plans/2026-06-29-v523-provider-offline-replay-harness.md
reports/v5_23_provider_offline_replay_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Offline replay runtime: no
Provider portal access: no
Real broker connection: no
Sandbox API connection: no
Broker SDK imports: no
API key creation: no
Credential storage: no
OAuth: no
Real account read: no
Sandbox account read: no
Real balance read: no
Real position read: no
Order submission: no
Real orders: no
Sandbox orders: no
Raw provider payload storage: no
Provider endpoint URL field: no
Real funds: no
External network requests: no
External log upload: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is provider sandbox connector offline replay only: yes
No real path can be enabled in V5.23: yes
```

Validation:

```text
py_compile: passed
run_v523_provider_offline_replay.py: passed, verdict PASS
pytest tests/test_v522_provider_mock_contract.py tests/test_v523_provider_offline_replay.py: 16 passed
pytest tests/test_v523_provider_offline_replay.py: 7 passed
pytest full suite: 802 passed
system_doctor: OK
frontend structure check: passed
security scan: no broker SDK imports, no network calls, no sandbox endpoint, no account read, no order submission, no raw provider payload storage, no provider_endpoint_url field, no credential handling in provider offline replay modules
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.22: Provider Sandbox Connector Mock Contract Test

This update adds an offline provider sandbox connector mock contract test layer for the selected provider. It validates placeholder payload shape, request mapping, response normalization, error mapping, idempotency policy, and order state-machine behavior without enabling any connector runtime, sandbox API, provider portal, account read, or order submission path.

New files:

```text
config/v5_provider_mock_contract_config.py
provider_mock_contract/__init__.py
provider_mock_contract/mock_provider_payloads.py
provider_mock_contract/contract_schema_validator.py
provider_mock_contract/request_mapping_contract_test.py
provider_mock_contract/response_normalization_contract_test.py
provider_mock_contract/error_mapping_contract_test.py
provider_mock_contract/idempotency_contract_test.py
provider_mock_contract/order_state_machine_contract_test.py
provider_mock_contract/mock_contract_safety_validator.py
provider_mock_contract/mock_contract_test_orchestrator.py
provider_mock_contract/provider_mock_contract_report.py
scripts/run_v522_provider_mock_contract.py
web/frontend/app/v5-provider-mock-contract/page.tsx
tests/test_v522_provider_mock_contract.py
docs/V5_PROVIDER_MOCK_CONTRACT.md
reports/v5_22_provider_mock_contract_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Mock contract runtime: no
Provider portal access: no
Real broker connection: no
Sandbox API connection: no
Broker SDK imports: no
API key creation: no
Credential storage: no
OAuth: no
Real account read: no
Sandbox account read: no
Real balance read: no
Real position read: no
Order submission: no
Real orders: no
Sandbox orders: no
Raw provider payload storage: no
Real funds: no
External network requests: no
External log upload: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is provider sandbox connector mock contract test only: yes
No real path can be enabled in V5.22: yes
```

Validation:

```text
py_compile: passed
run_v522_provider_mock_contract.py: passed, verdict WARNING because mock contract tests are offline only and runtime validation remains future work
run_v522_provider_mock_contract.py --provider alpaca: passed, verdict WARNING by design
run_v522_provider_mock_contract.py --provider ibkr: passed, verdict WARNING by design
run_v522_provider_mock_contract.py --check safety: passed, verdict WARNING by design
run_v522_provider_mock_contract.py --check schema: passed, verdict WARNING by design
run_v522_provider_mock_contract.py --check state-machine: passed, verdict WARNING by design
pytest tests/test_v522_provider_mock_contract.py: 9 passed
pytest full suite: 795 passed
system_doctor: OK
frontend structure check: passed
security scan: no broker SDK imports, no network calls, no sandbox endpoint, no account read, no order submission, no raw provider payload storage, no credential handling in provider mock contract modules
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.21: Provider-Specific Sandbox Connector Design

This update adds a provider-specific sandbox connector design layer for the selected provider. It defines placeholder field mappings, order request/response mappings, account and position mappings, error mappings, rate limit policy, idempotency policy, order state machine, and safety boundary without enabling connector runtime or any broker/sandbox API path.

New files:

```text
config/v5_provider_connector_design_config.py
provider_connector_design/__init__.py
provider_connector_design/provider_field_mapping.py
provider_connector_design/order_request_mapping.py
provider_connector_design/order_response_mapping.py
provider_connector_design/account_position_mapping.py
provider_connector_design/provider_error_mapping.py
provider_connector_design/rate_limit_policy.py
provider_connector_design/idempotency_policy.py
provider_connector_design/order_state_machine_design.py
provider_connector_design/connector_safety_boundary.py
provider_connector_design/provider_connector_design_report.py
scripts/run_v521_provider_connector_design.py
web/frontend/app/v5-provider-connector-design/page.tsx
tests/test_v521_provider_connector_design.py
docs/V5_PROVIDER_CONNECTOR_DESIGN.md
reports/v5_21_provider_connector_design_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Connector runtime: no
Provider portal access: no
Real broker connection: no
Sandbox API connection: no
Broker SDK imports: no
API key creation: no
Credential storage: no
OAuth: no
Real account read: no
Sandbox account read: no
Real balance read: no
Real position read: no
Order submission: no
Real orders: no
Sandbox orders: no
Real funds: no
External network requests: no
External log upload: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is provider-specific connector design only: yes
No real path can be enabled in V5.21: yes
```

Validation:

```text
py_compile: passed
run_v521_provider_connector_design.py: passed, verdict WARNING because connector design is design-only and runtime prerequisites remain incomplete by design
run_v521_provider_connector_design.py --provider alpaca: passed, verdict WARNING by design
run_v521_provider_connector_design.py --provider ibkr: passed, verdict WARNING by design
run_v521_provider_connector_design.py --check safety: passed, verdict WARNING by design
run_v521_provider_connector_design.py --check state-machine: passed, verdict WARNING by design
pytest tests/test_v521_provider_connector_design.py: 8 passed
pytest full suite: 786 passed
system_doctor: OK
frontend structure check: passed
security scan: no broker SDK imports, no network calls, no sandbox endpoint, no account read, no order submission, no credential handling in provider connector design modules
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.20: Selected Provider Sandbox Onboarding Runbook

This update adds a runbook-only onboarding layer for the selected provider from V5.19. It prepares account opening, sandbox access, API key handling, market data, approval/risk, and dry-run checklists without accessing any provider portal, connecting to sandbox APIs, creating keys, reading accounts, or placing orders.

New files:

```text
config/v5_provider_onboarding_config.py
provider_onboarding/__init__.py
provider_onboarding/selected_provider_resolver.py
provider_onboarding/account_opening_runbook.py
provider_onboarding/sandbox_access_runbook.py
provider_onboarding/api_key_preparation_runbook.py
provider_onboarding/market_data_onboarding_runbook.py
provider_onboarding/approval_risk_runbook.py
provider_onboarding/sandbox_dry_run_runbook.py
provider_onboarding/onboarding_safety_validator.py
provider_onboarding/provider_onboarding_report.py
scripts/run_v520_provider_onboarding.py
web/frontend/app/v5-provider-onboarding/page.tsx
tests/test_v520_provider_onboarding.py
docs/V5_PROVIDER_ONBOARDING.md
reports/v5_20_provider_onboarding_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Provider portal access: no
Real broker connection: no
Sandbox API connection: no
Broker SDK imports: no
API key creation: no
Credential storage: no
OAuth: no
Real account read: no
Sandbox account read: no
Real balance read: no
Real position read: no
Real orders: no
Sandbox orders: no
Real funds: no
External network requests: no
External log upload: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is provider onboarding runbook only: yes
No real path can be enabled in V5.20: yes
```

Validation:

```text
py_compile: passed
run_v520_provider_onboarding.py: passed, verdict WARNING because onboarding is runbook-only and production prerequisites remain incomplete by design
run_v520_provider_onboarding.py --provider alpaca: passed, verdict WARNING by design
run_v520_provider_onboarding.py --provider ibkr: passed, verdict WARNING by design
run_v520_provider_onboarding.py --check safety: passed, verdict WARNING by design
run_v520_provider_onboarding.py --check dry-run: passed, verdict WARNING by design
pytest tests/test_v520_provider_onboarding.py: 8 passed
pytest full suite: 778 passed
system_doctor: OK
frontend structure check: passed
security scan: no broker SDK imports, no network calls, no portal access, no key creation, no account/order runtime calls in provider onboarding modules
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.19: Broker Sandbox Provider Selection & Account Preparation

This update adds a provider selection and account preparation layer for future broker sandbox review. It ranks candidate providers with static metadata and produces account, API, market data, and compliance preparation checklists without enabling provider connections.

New files:

```text
config/v5_provider_selection_config.py
provider_selection/__init__.py
provider_selection/provider_universe.py
provider_selection/provider_capability_matrix.py
provider_selection/provider_risk_matrix.py
provider_selection/account_preparation_checklist.py
provider_selection/api_permission_checklist.py
provider_selection/market_data_permission_checklist.py
provider_selection/compliance_checklist.py
provider_selection/provider_selection_scoring.py
provider_selection/provider_selection_safety_validator.py
provider_selection/provider_selection_report.py
scripts/run_v519_provider_selection.py
web/frontend/app/v5-provider-selection/page.tsx
tests/test_v519_provider_selection.py
docs/V5_PROVIDER_SELECTION.md
reports/v5_19_provider_selection_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Sandbox API connection: no
Broker SDK imports: no
Real orders: no
Sandbox orders: no
Real account read: no
Real balance read: no
Real position read: no
Real funds: no
Credential storage: no
OAuth: no
External network requests: no
External log upload: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is provider selection and account preparation only: yes
Provider connection env vars are ignored and blocked as warnings: yes
No real path can be enabled in V5.19: yes
```

Validation:

```text
py_compile: passed
run_v519_provider_selection.py: passed, verdict WARNING because future account/API/market data/compliance preparation remains incomplete by design
run_v519_provider_selection.py --provider alpaca: passed, verdict WARNING by design
run_v519_provider_selection.py --provider ibkr: passed, verdict WARNING by design
run_v519_provider_selection.py --ranking: passed, verdict WARNING by design
run_v519_provider_selection.py --check safety: passed, verdict WARNING by design
pytest tests/test_v519_provider_selection.py: 8 passed
pytest full suite: 770 passed
system_doctor: OK
frontend structure check: passed
security scan: no broker SDK imports, no network calls, no order/account runtime calls in provider selection modules
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.18: Sandbox to Real Broker Transition Blueprint

This update adds the final transition blueprint before any future broker sandbox provider selection or account preparation work. It does not enable any real broker, sandbox API, account read, order submission, or real-money path.

New files:

```text
config/v5_transition_blueprint_config.py
transition/__init__.py
transition/transition_readiness_blueprint.py
transition/credential_vault_blueprint.py
transition/environment_separation_blueprint.py
transition/feature_flag_blueprint.py
transition/sandbox_enablement_checklist.py
transition/real_order_blocker_policy.py
transition/kill_switch_blueprint.py
transition/rollback_blueprint.py
transition/transition_safety_validator.py
transition/transition_blueprint_report.py
scripts/run_v518_transition_blueprint.py
web/frontend/app/v5-transition/page.tsx
tests/test_v518_transition_blueprint.py
docs/V5_TRANSITION_BLUEPRINT.md
reports/v5_18_transition_blueprint_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Sandbox API connection: no
Broker SDK imports: no
Real orders: no
Sandbox orders: no
Real account read: no
Real balance read: no
Real position read: no
Real funds: no
Credential storage: no
OAuth: no
External network requests: no
External log upload: no
Production trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is transition blueprint only: yes
V5.18 ignores real-path enablement env vars: yes
Requested real broker / sandbox / real order / real money flags are blocked and reported as warnings: yes
No real path can be enabled in V5.18: yes
```

Validation:

```text
python -m py_compile config/v5_transition_blueprint_config.py transition/transition_readiness_blueprint.py transition/credential_vault_blueprint.py transition/environment_separation_blueprint.py transition/feature_flag_blueprint.py transition/sandbox_enablement_checklist.py transition/real_order_blocker_policy.py transition/kill_switch_blueprint.py transition/rollback_blueprint.py transition/transition_safety_validator.py transition/transition_blueprint_report.py scripts/run_v518_transition_blueprint.py src/api/v2/server.py: passed
python -m py_compile config/v5_transition_blueprint_config.py transition/transition_safety_validator.py scripts/run_v518_transition_blueprint.py src/api/v2/server.py: passed after review fix
python scripts/run_v518_transition_blueprint.py: exit 0, verdict WARNING because future sandbox enablement checklist intentionally has blocking items
python scripts/run_v518_transition_blueprint.py --check safety: exit 0, verdict WARNING
python scripts/run_v518_transition_blueprint.py --check sandbox-checklist: exit 0, verdict WARNING
python scripts/run_v518_transition_blueprint.py --check real-order-blocker: exit 0, verdict WARNING
python -m pytest tests/test_v518_transition_blueprint.py: 8 passed
python -m pytest: 762 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
Safety scan: no transition module imports broker SDKs or performs network/order/account runtime calls; matches only blocked-term lists in runtime/security_scan.py
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.17: Sandbox Connector Integration Test Harness

This update adds an end-to-end integration test harness for the simulated future broker path. It validates Alpha Signal to Paper Trading Engine to Manual Approval to Broker Adapter Skeleton to Mock Connector to Sandbox Bridge to execution simulation, monitoring, risk, and audit outputs without enabling external runtime access.

New files:

```text
integration_test/__init__.py
integration_test/sanitizer.py
integration_test/integration_test_core.py
integration_test/layered_pipeline_tester.py
integration_test/failure_injection_engine.py
integration_test/cross_layer_consistency_validator.py
integration_test/integration_scenario_matrix.py
integration_test/integration_test_orchestrator.py
integration_test/integration_safety_gate.py
integration_test/integration_test_report.py
scripts/run_v517_integration_test_harness.py
web/frontend/app/v5-integration-test/page.tsx
tests/test_v517_integration_test_harness.py
docs/V5_INTEGRATION_TEST_HARNESS.md
reports/v5_17_integration_test_harness_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Sandbox API connection: no
Real orders: no
Sandbox orders: no
Real trading API: no
Real account read: no
Real position read: no
Real balance read: no
Broker credential read/save: no
Connector runtime enabled: no
Network calls: no
Real capital: no
Payment system: no
Production live trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is integration test harness only: yes
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile integration_test/integration_test_core.py integration_test/layered_pipeline_tester.py integration_test/failure_injection_engine.py integration_test/cross_layer_consistency_validator.py integration_test/integration_scenario_matrix.py integration_test/integration_test_orchestrator.py integration_test/integration_safety_gate.py integration_test/integration_test_report.py scripts/run_v517_integration_test_harness.py src/api/v2/server.py: passed
python scripts/run_v517_integration_test_harness.py --scenario normal_flow: exit 0, verdict PASS
python scripts/run_v517_integration_test_harness.py --scenario full_failure_chain: exit 0, verdict PASS
python scripts/run_v517_integration_test_harness.py --all: exit 0, verdict PASS
python -m pytest tests/test_v517_integration_test_harness.py: 8 passed
python -m pytest: 754 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.17 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.16: Sandbox Connector Bridge

This update adds a bridge-only sandbox connector abstraction layer between the V5.15 broker adapter skeleton and any future sandbox connector. It includes request transformation, response normalization, error translation, retry orchestration, idempotency enforcement, simulated session lifecycle, routing, safety gate, API endpoints, CLI/report, frontend page, documentation, and tests without enabling external runtime access.

New files:

```text
sandbox_bridge/__init__.py
sandbox_bridge/sanitizer.py
sandbox_bridge/sandbox_bridge_core.py
sandbox_bridge/request_transformer.py
sandbox_bridge/response_normalizer.py
sandbox_bridge/error_translation_layer.py
sandbox_bridge/retry_orchestrator.py
sandbox_bridge/idempotency_enforcer.py
sandbox_bridge/sandbox_session.py
sandbox_bridge/sandbox_router.py
sandbox_bridge/bridge_safety_gate.py
sandbox_bridge/sandbox_bridge_report.py
scripts/run_v516_sandbox_bridge.py
web/frontend/app/v5-sandbox-bridge/page.tsx
tests/test_v516_sandbox_bridge.py
docs/V5_SANDBOX_CONNECTOR_BRIDGE.md
reports/v5_16_sandbox_connector_bridge_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Sandbox API connection: no
Real orders: no
Sandbox orders: no
Real trading API: no
Real account read: no
Real position read: no
Real balance read: no
Broker credential read/save: no
Connector runtime enabled: no
Network calls: no
Real capital: no
Payment system: no
Production live trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is sandbox bridge abstraction only: yes
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile sandbox_bridge/sandbox_bridge_core.py sandbox_bridge/request_transformer.py sandbox_bridge/response_normalizer.py sandbox_bridge/error_translation_layer.py sandbox_bridge/retry_orchestrator.py sandbox_bridge/idempotency_enforcer.py sandbox_bridge/sandbox_session.py sandbox_bridge/sandbox_router.py sandbox_bridge/bridge_safety_gate.py sandbox_bridge/sandbox_bridge_report.py scripts/run_v516_sandbox_bridge.py src/api/v2/server.py: passed
python scripts/run_v516_sandbox_bridge.py --test route: exit 0, verdict PASS
python scripts/run_v516_sandbox_bridge.py --test transform: exit 0, verdict PASS
python scripts/run_v516_sandbox_bridge.py --test normalize: exit 0, verdict PASS
python -m pytest tests/test_v516_sandbox_bridge.py: 8 passed
python -m pytest: 746 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.16 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.15: Broker Adapter Skeleton + Sandbox Bridge

This update adds a skeleton-only broker adapter layer for future provider integrations. It defines the base adapter interface, registry, factory, provider skeleton adapters, V5.14 mock bridge, capability matrix, compatibility checks, safety guard, API endpoints, CLI/report, frontend page, documentation, and tests without enabling broker runtime or external provider access.

New files:

```text
broker_adapter/__init__.py
broker_adapter/base_adapter.py
broker_adapter/adapter_registry.py
broker_adapter/adapter_factory.py
broker_adapter/ibkr_skeleton_adapter.py
broker_adapter/alpaca_skeleton_adapter.py
broker_adapter/skeleton_adapters.py
broker_adapter/mock_adapter.py
broker_adapter/compatibility_layer.py
broker_adapter/capability_matrix.py
broker_adapter/safety_guard.py
broker_adapter/broker_adapter_report.py
scripts/run_v515_broker_adapter_skeleton.py
web/frontend/app/v5-broker-adapter/page.tsx
tests/test_v515_broker_adapter_skeleton.py
docs/V5_BROKER_ADAPTER_SKELETON.md
reports/v5_15_broker_adapter_skeleton_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Sandbox API connection: no
Real orders: no
Sandbox orders: no
Real trading API: no
Real account read: no
Real position read: no
Real balance read: no
Broker credential read/save: no
Connector runtime enabled: no
Real capital: no
Payment system: no
Production live trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is adapter skeleton only: yes
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile broker_adapter/base_adapter.py broker_adapter/adapter_registry.py broker_adapter/adapter_factory.py broker_adapter/ibkr_skeleton_adapter.py broker_adapter/alpaca_skeleton_adapter.py broker_adapter/skeleton_adapters.py broker_adapter/mock_adapter.py broker_adapter/compatibility_layer.py broker_adapter/capability_matrix.py broker_adapter/safety_guard.py broker_adapter/broker_adapter_report.py scripts/run_v515_broker_adapter_skeleton.py src/api/v2/server.py: passed
python scripts/run_v515_broker_adapter_skeleton.py --list: exit 0, verdict PASS
python scripts/run_v515_broker_adapter_skeleton.py --test ibkr_skeleton: exit 0, verdict PASS
python scripts/run_v515_broker_adapter_skeleton.py --test alpaca_skeleton: exit 0, verdict PASS
python -m pytest tests/test_v515_broker_adapter_skeleton.py: 8 passed
python -m pytest: 738 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.15 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.14: Sandbox Connector Mock Implementation

This update adds a local-only mock implementation for the V5.13 sandbox connector contract. It supports safe connector demos, API integration checks, frontend status display, deterministic mock order lifecycle scenarios, safety validation, CLI/report output, and local tests without enabling connector runtime or external broker access.

New files:

```text
config/v5_sandbox_connector_mock_config.py
sandbox_connector/mock_sandbox_connector.py
sandbox_connector/mock_connector_state_store.py
sandbox_connector/mock_order_lifecycle.py
sandbox_connector/mock_response_factory.py
sandbox_connector/mock_connector_scenario_runner.py
sandbox_connector/mock_connector_safety_validator.py
sandbox_connector/mock_connector_report.py
scripts/run_v514_sandbox_connector_mock.py
web/frontend/app/v5-sandbox-connector-mock/page.tsx
tests/test_v514_sandbox_connector_mock.py
docs/V5_SANDBOX_CONNECTOR_MOCK.md
reports/v5_14_sandbox_connector_mock_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Sandbox API connection: no
Sandbox orders: no
Real orders: no
Real trading API: no
Real account read: no
Real position read: no
Real balance read: no
Credential read/save: no
Connector runtime enabled: no
Real capital: no
Payment system: no
Production live trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is local mock only: yes
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile config/v5_sandbox_connector_mock_config.py sandbox_connector/mock_sandbox_connector.py sandbox_connector/mock_connector_state_store.py sandbox_connector/mock_order_lifecycle.py sandbox_connector/mock_response_factory.py sandbox_connector/mock_connector_scenario_runner.py sandbox_connector/mock_connector_safety_validator.py sandbox_connector/mock_connector_report.py scripts/run_v514_sandbox_connector_mock.py src/api/v2/server.py: passed
python scripts/run_v514_sandbox_connector_mock.py --scenario accepted: exit 0, verdict PASS
python scripts/run_v514_sandbox_connector_mock.py --all-scenarios: exit 0, verdict PASS
python -m pytest tests/test_v514_sandbox_connector_mock.py: 12 passed
python -m pytest: 730 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.14 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.13: Sandbox Connector Contract Planning

This update adds a contract-only planning layer for a future broker sandbox connector. It defines the interface contract, request/response schemas, error code contract, idempotency policy, rate limit policy, retry policy, credential boundary, safety validator, API endpoints, CLI/report, and frontend page without enabling connector runtime or external broker access.

New files:

```text
config/v5_sandbox_connector_contract_config.py
sandbox_connector/__init__.py
sandbox_connector/connector_interface_contract.py
sandbox_connector/request_schema_contract.py
sandbox_connector/response_schema_contract.py
sandbox_connector/error_code_contract.py
sandbox_connector/idempotency_policy.py
sandbox_connector/rate_limit_policy.py
sandbox_connector/retry_policy.py
sandbox_connector/credential_boundary_contract.py
sandbox_connector/connector_safety_validator.py
sandbox_connector/sandbox_connector_contract_report.py
scripts/run_v513_sandbox_connector_contract.py
web/frontend/app/v5-sandbox-connector/page.tsx
tests/test_v513_sandbox_connector_contract.py
docs/V5_SANDBOX_CONNECTOR_CONTRACT.md
reports/v5_13_sandbox_connector_contract_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Sandbox API connection: no
Real orders: no
Sandbox orders: no
Real trading API: no
Real account read: no
Real position read: no
Real balance read: no
Credential read/save: no
Connector runtime enabled: no
Real capital: no
Payment system: no
Production live trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
This is connector contract only: yes
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile config/v5_sandbox_connector_contract_config.py sandbox_connector/connector_interface_contract.py sandbox_connector/request_schema_contract.py sandbox_connector/response_schema_contract.py sandbox_connector/error_code_contract.py sandbox_connector/idempotency_policy.py sandbox_connector/rate_limit_policy.py sandbox_connector/retry_policy.py sandbox_connector/credential_boundary_contract.py sandbox_connector/connector_safety_validator.py sandbox_connector/sandbox_connector_contract_report.py scripts/run_v513_sandbox_connector_contract.py src/api/v2/server.py: passed
python scripts/run_v513_sandbox_connector_contract.py: exit 0, verdict PASS
python -m pytest tests/test_v513_sandbox_connector_contract.py: 13 passed
python -m pytest: 718 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.13 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.12: Sandbox Simulation Robustness Suite

This update adds a local-only robustness suite for the V5.11 sandbox simulation harness. It covers scenario matrix validation, multi-symbol simulation, combined fault testing, long-run robustness, consistency validation, API endpoints, CLI/report, and a frontend page without connecting to any broker or sandbox API.

New files:

```text
config/v5_sandbox_robustness_config.py
sandbox_sim/robustness_scenario_matrix.py
sandbox_sim/multi_symbol_simulator.py
sandbox_sim/fault_combination_runner.py
sandbox_sim/robustness_consistency_validator.py
sandbox_sim/long_run_robustness_runner.py
sandbox_sim/sandbox_robustness_report.py
scripts/run_v512_sandbox_robustness.py
web/frontend/app/v5-sandbox-robustness/page.tsx
tests/test_v512_sandbox_simulation_robustness.py
docs/V5_SANDBOX_SIMULATION_ROBUSTNESS.md
reports/v5_12_sandbox_simulation_robustness_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Sandbox API connection: no
Real orders: no
Sandbox orders: no
Real trading API: no
Real account read: no
Real position read: no
Real balance read: no
Credential read/save: no
Real capital: no
Payment system: no
Production live trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
All tests are local simulated robustness tests: yes
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile config/v5_sandbox_robustness_config.py sandbox_sim/robustness_scenario_matrix.py sandbox_sim/multi_symbol_simulator.py sandbox_sim/fault_combination_runner.py sandbox_sim/robustness_consistency_validator.py sandbox_sim/long_run_robustness_runner.py sandbox_sim/sandbox_robustness_report.py scripts/run_v512_sandbox_robustness.py src/api/v2/server.py: passed
python scripts/run_v512_sandbox_robustness.py --scenario full_fill --ticks 500: exit 0, verdict PASS
python scripts/run_v512_sandbox_robustness.py --all-scenarios --ticks 1000: exit 0, verdict WARNING
python -m pytest tests/test_v512_sandbox_simulation_robustness.py: 11 passed
python -m pytest: 705 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.12 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.11: Sandbox Simulation Harness

This update adds a local-only sandbox simulation harness. It models simulated sandbox account state, simulated orders and fills, lifecycle transitions, local fault scenarios, API endpoints, CLI/report, and a frontend page without connecting to any broker or sandbox API.

New files:

```text
config/v5_sandbox_simulation_config.py
sandbox_sim/__init__.py
sandbox_sim/simulated_sandbox_account.py
sandbox_sim/simulated_sandbox_order.py
sandbox_sim/sandbox_simulation_broker.py
sandbox_sim/order_lifecycle_simulator.py
sandbox_sim/sandbox_simulation_faults.py
sandbox_sim/sandbox_simulation_runner.py
sandbox_sim/sandbox_simulation_report.py
scripts/run_v511_sandbox_simulation.py
web/frontend/app/v5-sandbox-sim/page.tsx
tests/test_v511_sandbox_simulation_harness.py
docs/V5_SANDBOX_SIMULATION_HARNESS.md
reports/v5_11_sandbox_simulation_harness_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Sandbox API connection: no
Real orders: no
Sandbox orders: no
Real trading API: no
Real account read: no
Real position read: no
Real balance read: no
Credential read/save: no
Real capital: no
Payment system: no
Production live trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
All orders are local simulated orders: yes
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile config/v5_sandbox_simulation_config.py sandbox_sim/simulated_sandbox_account.py sandbox_sim/simulated_sandbox_order.py sandbox_sim/sandbox_simulation_broker.py sandbox_sim/order_lifecycle_simulator.py sandbox_sim/sandbox_simulation_faults.py sandbox_sim/sandbox_simulation_runner.py sandbox_sim/sandbox_simulation_report.py scripts/run_v511_sandbox_simulation.py src/api/v2/server.py: passed
python scripts/run_v511_sandbox_simulation.py --scenario full_fill --ticks 100: exit 0, verdict PASS
python scripts/run_v511_sandbox_simulation.py --scenario reject --ticks 100: exit 0, verdict WARNING
python -m pytest tests/test_v511_sandbox_simulation_harness.py: 11 passed
python -m pytest: 694 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.11 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.10: Broker Sandbox Readiness Planning System

This update adds a planning-only broker sandbox readiness layer. It documents sandbox provider options, credential isolation, sandbox order lifecycle, safety checklist, rollback plan, readiness API endpoints, CLI/report, and frontend page without connecting to any sandbox API or submitting sandbox orders.

New files:

```text
config/v5_broker_sandbox_config.py
sandbox/__init__.py
sandbox/sandbox_provider_plan.py
sandbox/credential_isolation_plan.py
sandbox/sandbox_order_lifecycle_plan.py
sandbox/sandbox_safety_checklist.py
sandbox/sandbox_rollback_plan.py
sandbox/sandbox_readiness_report.py
scripts/run_v510_broker_sandbox_readiness.py
web/frontend/app/v5-sandbox/page.tsx
tests/test_v510_broker_sandbox_readiness.py
docs/V5_BROKER_SANDBOX_READINESS.md
reports/v5_10_broker_sandbox_readiness_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Sandbox API connection: no
Real orders: no
Sandbox orders: no
Real trading API: no
Real account read: no
Real position read: no
Real balance read: no
Credential read/save: no
Real capital: no
Payment system: no
Production live trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
Sandbox order submission rejected by default: yes
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile config/v5_broker_sandbox_config.py sandbox/sandbox_provider_plan.py sandbox/credential_isolation_plan.py sandbox/sandbox_order_lifecycle_plan.py sandbox/sandbox_safety_checklist.py sandbox/sandbox_rollback_plan.py sandbox/sandbox_readiness_report.py scripts/run_v510_broker_sandbox_readiness.py src/api/v2/server.py: passed
python scripts/run_v510_broker_sandbox_readiness.py: exit 0, verdict WARNING
python -m pytest tests/test_v510_broker_sandbox_readiness.py: 11 passed
python -m pytest: 683 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.10 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.9: Manual Approval Gate Planning System

This update adds a planning-only manual approval safety gate. It models approval requests, state transitions, reject-by-default behavior, local audit trail, paper-only risk summaries, API endpoints, CLI/report, and frontend page without enabling real broker order release.

New files:

```text
config/v5_manual_approval_config.py
approval/__init__.py
approval/approval_request.py
approval/manual_approval_gate.py
approval/approval_state_machine.py
approval/approval_audit_trail.py
approval/approval_risk_summary.py
approval/manual_approval_report.py
scripts/run_v59_manual_approval_gate.py
web/frontend/app/v5-approval/page.tsx
tests/test_v59_manual_approval_gate.py
docs/V5_MANUAL_APPROVAL_GATE_PLANNING.md
reports/v5_9_manual_approval_gate_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Real orders: no
Real trading API: no
Real account read: no
Real position read: no
Real balance read: no
Real capital: no
Payment system: no
Production live trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
Real order attempts rejected by default: yes
Auto approval: no
Manual approval simulated only: yes
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile config/v5_manual_approval_config.py approval/approval_request.py approval/manual_approval_gate.py approval/approval_state_machine.py approval/approval_audit_trail.py approval/approval_risk_summary.py approval/manual_approval_report.py scripts/run_v59_manual_approval_gate.py src/api/v2/server.py: passed
python scripts/run_v59_manual_approval_gate.py: exit 0, verdict WARNING
python -m pytest tests/test_v59_manual_approval_gate.py: 10 passed
python -m pytest: 672 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.9 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.8: Broker Integration Planning System

This update adds a planning-only broker integration layer. It documents the future adapter shape, order mapping, safety gate, API, CLI, report, and frontend page without connecting to any real broker or submitting real orders.

New files:

```text
config/v5_broker_integration_config.py
broker/broker_adapter_interface.py
broker/planned_broker_adapter.py
broker/order_mapping_plan.py
broker/broker_safety_gate.py
broker/broker_integration_report.py
scripts/run_v58_broker_integration_planning.py
web/frontend/app/v5-broker/page.tsx
tests/test_v58_broker_integration_planning.py
docs/V5_BROKER_INTEGRATION_PLANNING.md
reports/v5_8_broker_integration_planning_report.md
```

Updated files:

```text
runtime/security_scan.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Real orders: no
Real trading API: no
Real account read: no
Real position read: no
Real balance read: no
Real capital: no
Payment system: no
Production live trading: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
Real order attempts rejected by default: yes
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile config/v5_broker_integration_config.py broker/broker_adapter_interface.py broker/planned_broker_adapter.py broker/order_mapping_plan.py broker/broker_safety_gate.py broker/broker_integration_report.py scripts/run_v58_broker_integration_planning.py src/api/v2/server.py: passed
python scripts/run_v58_broker_integration_planning.py: exit 0, verdict WARNING
python -m pytest tests/test_v58_broker_integration_planning.py: 10 passed
python -m pytest: 662 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.8 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.7: Live Alpha Signal Integration for Live Paper

This update upgrades V5 live paper staging from heartbeat validation to V5 alpha signal driven paper trading.

New files:

```text
runtime/live_feature_buffer.py
runtime/live_alpha_signal_adapter.py
runtime/live_paper_alpha_runner.py
runtime/live_alpha_report.py
scripts/run_v57_live_alpha_paper.py
web/frontend/app/v5-live-alpha/page.tsx
tests/test_v57_live_alpha_signal_integration.py
docs/V5_LIVE_ALPHA_SIGNAL_INTEGRATION.md
```

Updated files:

```text
runtime/live_paper_staging_runner.py
src/api/v2/server.py
runtime/security_scan.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Real orders: no
Real trading API: no
Real capital: no
Payment system: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
Production live trading: no
V5.6 heartbeat order replaced: yes
V5 alpha signal driven paper trading: yes
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile runtime/live_feature_buffer.py runtime/live_alpha_signal_adapter.py runtime/live_paper_alpha_runner.py runtime/live_alpha_report.py scripts/run_v57_live_alpha_paper.py src/api/v2/server.py: passed
python scripts/run_v57_live_alpha_paper.py --mode mock_live --ticks 100: exit 0, verdict WARNING
python scripts/run_v57_live_alpha_paper.py --mode yfinance_polling --ticks 20: exit 0, verdict WARNING with mock_live fallback
python -m pytest tests/test_v57_live_alpha_signal_integration.py: 8 passed
python -m pytest: 652 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.7 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.6: Live Paper Trading Staging System

This update adds a live market data paper trading staging layer. It allows market-data-like ticks to feed the V5 paper runtime shape while all order, execution, account, and portfolio state remains simulated.

New files:

```text
config/v5_live_data_config.py
runtime/live_market_data.py
runtime/live_data_normalizer.py
runtime/live_paper_staging_runner.py
runtime/live_paper_report.py
scripts/run_v56_live_paper_staging.py
web/frontend/app/v5-live-paper/page.tsx
tests/test_v56_live_paper_trading_staging.py
docs/V5_LIVE_PAPER_TRADING_STAGING.md
```

Updated files:

```text
src/api/v2/server.py
runtime/security_scan.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Real orders: no
Real trading API: no
Real capital: no
Payment system: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
Production live trading: no
Live market data: mock_live by default, yfinance_polling optional
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile config/v5_live_data_config.py runtime/live_market_data.py runtime/live_data_normalizer.py runtime/live_paper_staging_runner.py runtime/live_paper_report.py scripts/run_v56_live_paper_staging.py src/api/v2/server.py: passed
python scripts/run_v56_live_paper_staging.py --mode mock_live --ticks 20: exit 0, verdict PASS
python scripts/run_v56_live_paper_staging.py --mode yfinance_polling --ticks 5: exit 0, verdict WARNING with mock_live fallback
python -m pytest tests/test_v56_live_paper_trading_staging.py: 8 passed
python -m pytest: 644 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.6 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.5: Production Deployment Dry Run System

This update adds a production deployment dry run layer for the V5 paper trading system. It validates deployment shape only and does not perform a real production launch.

New files:

```text
config/v5_deployment_config.py
scripts/v55_deployment_dry_run_check.py
scripts/run_v55_deployment_dry_run.py
runtime/v55_deployment_report.py
web/frontend/app/v5-deployment/page.tsx
tests/test_v55_production_deployment_dry_run.py
docs/V5_PRODUCTION_DEPLOYMENT_DRY_RUN.md
```

Updated files:

```text
src/api/v2/server.py
runtime/security_scan.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Real orders: no
Real trading API: no
Real capital: no
Payment system: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
Production deployment: no
Real cloud service: no
Production database: no
Production credentials committed: no
External AI API: no
External log upload: no
```

Validation:

```text
python -m py_compile config/v5_deployment_config.py runtime/v55_deployment_report.py scripts/v55_deployment_dry_run_check.py scripts/run_v55_deployment_dry_run.py src/api/v2/server.py: passed
python scripts/v55_deployment_dry_run_check.py: exit 0, dry_run_ready true, deployment_ready false
python scripts/run_v55_deployment_dry_run.py: exit 0, verdict WARNING
python -m pytest tests/test_v55_production_deployment_dry_run.py: 6 passed
python -m pytest: 636 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.5 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.4: Live Paper Trading Dashboard / Monitoring API

This update adds V5.4 monitoring API and dashboard-ready monitoring layer for the paper trading runtime.

New files:

```text
runtime/monitoring_data_reader.py
runtime/monitoring_summary.py
runtime/monitoring_report.py
scripts/run_v54_monitoring_snapshot.py
web/frontend/app/v5-monitoring/page.tsx
tests/test_v54_live_paper_trading_monitoring_api.py
docs/V5_LIVE_PAPER_TRADING_MONITORING.md
```

Updated files:

```text
src/api/v2/server.py
runtime/security_scan.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Real broker connection: no
Real orders: no
Real trading API: no
Real capital: no
Payment system: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
Production deployment: no
External AI API: no
External database dependency: no
External log upload: no
Plaintext API key / secret / token / password / authorization: no
```

Validation:

```text
python -m py_compile runtime/monitoring_data_reader.py runtime/monitoring_summary.py runtime/monitoring_report.py scripts/run_v54_monitoring_snapshot.py src/api/v2/server.py: passed
python scripts/run_v54_monitoring_snapshot.py: exit 0, verdict WARNING
python -m pytest tests/test_v54_live_paper_trading_monitoring_api.py: 6 passed
python -m pytest: 630 passed
python scripts/system_doctor.py: OK
web/frontend node scripts/verify-build.mjs: passed
web/frontend pnpm run build: blocked by local pnpm supply-chain policy requiring interactive approval for sharp build scripts; no V5.4 TypeScript/runtime error was emitted before that policy stop
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.3: Long-Run Paper Trading Soak Test System

This update adds a long-run paper trading soak test system to validate that the V5.2 runtime stability layer survives repeated ticks, controlled faults, checkpoints, recovery paths, logging, and consistency checks.

New files:

```text
runtime/soak_test_runner.py
runtime/synthetic_market.py
runtime/fault_injection.py
runtime/consistency_validator.py
runtime/soak_report.py
runtime/security_scan.py
scripts/run_v53_soak_test.py
tests/test_v53_long_run_soak_test.py
docs/V5_LONG_RUN_SOAK_TEST.md
```

Safety boundaries:

```text
Real broker connection: no
Real orders: no
Real trading API: no
Real capital: no
Payment system: no
Alpha model changed: no
Factor logic changed: no
New strategy added: no
Production deployment: no
External AI API: no
External database dependency: no
Plaintext API key / secret / token / password: no
```

Validation:

```text
python -m py_compile runtime/soak_test_runner.py runtime/synthetic_market.py runtime/fault_injection.py runtime/consistency_validator.py runtime/soak_report.py runtime/security_scan.py scripts/run_v53_soak_test.py: passed
python scripts/run_v53_soak_test.py --mode synthetic --ticks 1000: exit 0, final_verdict WARNING
python scripts/run_v53_soak_test.py --mode synthetic --ticks 1000 --faults: exit 0, final_verdict WARNING
python -m pytest tests/test_v53_long_run_soak_test.py: 9 passed
python -m pytest: 624 passed
python scripts/system_doctor.py: OK
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.2: Production Stability Engineering System

This update adds production stability engineering around the V5.1 runtime:

Live Trading System -> 24/7 Stability -> No Crash -> Auto Recovery -> Risk Safe Operation

New files:

```text
runtime/watchdog.py
runtime/recovery_engine.py
runtime/state_checkpoint.py
runtime/health_monitor.py
runtime/error_handler.py
runtime/mode_manager.py
runtime/logger.py
tests/test_v52_production_stability_engineering.py
docs/V5_PRODUCTION_STABILITY_ENGINEERING.md
```

Updated files:

```text
runtime/trading_engine.py
runtime/monitor.py
README.md
REVIEW_PACKAGE.md
```

Safety boundaries:

```text
Alpha model changed: no
Factor logic changed: no
New strategy added: no
Trading logic changed: no
Real trading: no
Broker connection: no
Real account: no
Payment system: no
External database dependency: no
Plaintext API key / secret / token / password: no
```

Validation:

```text
python -m py_compile runtime/watchdog.py runtime/recovery_engine.py runtime/state_checkpoint.py runtime/health_monitor.py runtime/error_handler.py runtime/mode_manager.py runtime/logger.py runtime/trading_engine.py runtime/monitor.py: passed
python -m pytest tests/test_v52_production_stability_engineering.py: 6 passed
python -m pytest: 615 passed
python scripts/system_doctor.py: OK
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.1: Trading Engine Runtime System

This update adds the runtime system that turns V5.0 paper trading components into a continuous engine loop:

Market Data Tick -> Signal Engine -> Signal to Order -> Risk Check -> Execution Engine -> Portfolio Update -> PnL Update -> Log -> Next Tick

New files:

```text
runtime/__init__.py
runtime/trading_engine.py
runtime/market_simulator.py
runtime/state_manager.py
runtime/event_bus.py
runtime/pnl_engine.py
runtime/system_controller.py
runtime/risk_gate.py
runtime/monitor.py
tests/test_v51_trading_engine_runtime.py
docs/V5_TRADING_ENGINE_RUNTIME.md
```

Safety boundaries:

```text
Alpha model changed: no
Factor logic changed: no
New strategy added: no
Real trading: no
Broker connection: no
Real account: no
Payment system: no
Plaintext API key / secret / token / password: no
```

Validation:

```text
python -m py_compile runtime/trading_engine.py runtime/market_simulator.py runtime/state_manager.py runtime/event_bus.py runtime/pnl_engine.py runtime/system_controller.py runtime/risk_gate.py runtime/monitor.py: passed
python -m pytest tests/test_v51_trading_engine_runtime.py: 6 passed
python -m pytest: 609 passed
python scripts/system_doctor.py: OK
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V5.0: Paper Trading Core System

This update adds a paper trading core for the closed loop:

Signal -> Order -> Execution -> Position -> Cash -> Portfolio Value -> PnL -> Risk Check -> Trade Log

New files:

```text
trading/__init__.py
trading/order.py
trading/execution_engine.py
trading/paper_account.py
trading/paper_broker.py
trading/signal_to_order.py
trading/paper_trading_runner.py
trading/performance.py
trading/risk_limits.py
tests/test_v50_paper_trading_core.py
docs/V5_PAPER_TRADING_CORE.md
```

Safety boundaries:

```text
Real broker connection: no
Real orders: no
Real account: no
Real capital: no
Payment system: no
Alpha model changed: no
Factor logic changed: no
Production deployment: no
Plaintext API key / secret / token / password: no
```

Validation:

```text
python -m py_compile trading/order.py trading/execution_engine.py trading/paper_account.py trading/paper_broker.py trading/signal_to_order.py trading/paper_trading_runner.py trading/performance.py trading/risk_limits.py: passed
python -m pytest tests/test_v50_paper_trading_core.py: 10 passed
python -m pytest: 603 passed
python scripts/system_doctor.py: OK
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V4.3 Production Deployment Target Selection

V4.3 adds 生产部署目标选择规划 for future frontend, backend, database, configuration, and monitoring hosting choices. It does not deploy to a real cloud provider, commit cloud credentials, commit a deployment token, connect a production database, perform a real production launch, connect real payments, upload logs externally, connect brokers, call external AI services, or change core strategy logic.

New files:

```text
src/config/deployment_target_config.py
src/deployment/__init__.py
src/deployment/deployment_target_plan.py
scripts/deployment_target_selection_check.py
docs/PRODUCTION_DEPLOYMENT_TARGET_SELECTION.md
tests/test_v43_production_deployment_target_selection.py
```

Updated files:

```text
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/admin/page.tsx
docs/V4_PRODUCTION_LAUNCH_READINESS.md
README.md
REVIEW_PACKAGE.md
```

Deployment target planning scope:

- Added deployment target configuration planning layer.
- Added deployment target plan module.
- Added deployment target selection API endpoint.
- Added deployment target selection check script.
- Added Admin Console production deployment target module.
- Added frontend fetchDeploymentTarget helper.
- Added production deployment target selection documentation.

Safety boundaries:

- Real production deployment: no
- Real cloud service connected: no
- Cloud token committed: no
- DATABASE_URL committed: no
- Production secret committed: no
- Real production database connected: no
- Real payment connected: no
- Broker connection: no
- Auto trading: no
- AI API calls: no
- Core strategy logic changed: no

Validation:

```text
py_compile deployment target modules/server: passed
deployment_target_selection_check: success true
tests/test_v43_production_deployment_target_selection.py: 5 passed
pytest: 539 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm/pnpm unavailable in this shell; only bundled node is available
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review per V4.3 instruction
```

# V4.2 Production Identity Integration Plan

V4.2 adds 生产身份集成规划 and identity mapping readiness preparation. It does not connect a real identity provider, implement OAuth, add Google/GitHub login, commit identity provider credentials, store external identity tokens, perform a real production launch, connect real cloud services, connect real payments, upload logs externally, connect brokers, call external AI services, or change core strategy logic.

New files:

```text
src/config/production_identity_config.py
src/auth/production_identity_plan.py
scripts/production_identity_integration_check.py
docs/PRODUCTION_IDENTITY_INTEGRATION_PLAN.md
tests/test_v42_production_identity_integration_plan.py
```

Updated files:

```text
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/admin/page.tsx
docs/V4_PRODUCTION_LAUNCH_READINESS.md
README.md
REVIEW_PACKAGE.md
```

Production identity planning scope:

- Added production identity configuration planning layer.
- Added production identity integration plan module.
- Added identity integration readiness API endpoint.
- Added production identity integration check script.
- Added Admin Console production identity integration module.
- Added frontend fetchIdentityIntegration helper.
- Added production identity integration planning documentation.

Safety boundaries:

- Real identity service connected: no
- OAuth connected: no
- Google/GitHub login connected: no
- client_id/client_secret committed: no
- access/refresh token stored: no
- Real production launch: no
- Real cloud service connected: no
- Real payment connected: no
- Broker connection: no
- Auto trading: no
- AI API calls: no
- Core strategy logic changed: no

Validation:

```text
py_compile production identity modules/server: passed
production_identity_integration_check: success true
tests/test_v42_production_identity_integration_plan.py: 5 passed
pytest: 534 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm/pnpm unavailable in this shell; only bundled node is available
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, after checks pass per user instruction
```

# V4.1 Production Database Plan

V4.1 adds 生产数据库规划 and migration readiness preparation. It does not connect a real production database, commit a real database URL, commit database credentials, migrate real customer data, perform a real production launch, connect real cloud services, connect real identity services, connect real payments, upload logs externally, connect brokers, call external AI services, or change core strategy logic.

New files:

```text
src/config/production_database_config.py
src/db/production_database_plan.py
scripts/production_database_plan_check.py
docs/PRODUCTION_DATABASE_PLAN.md
tests/test_v41_production_database_plan.py
```

Updated files:

```text
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/admin/page.tsx
docs/V4_PRODUCTION_LAUNCH_READINESS.md
README.md
REVIEW_PACKAGE.md
```

Production database planning scope:

- Added production database configuration planning layer.
- Added production database plan module.
- Added production database API endpoint.
- Added production database plan check script.
- Added Admin Console production database module.
- Added frontend fetchProductionDatabase helper.
- Added production database planning documentation.

Safety boundaries:

- Real production database connected: no
- DATABASE_URL committed: no
- Database credentials committed: no
- Real customer data migration: no
- Real production launch: no
- Real cloud service connected: no
- Real identity service connected: no
- Real payment connected: no
- Broker connection: no
- Auto trading: no
- AI API calls: no
- Core strategy logic changed: no

Validation:

```text
py_compile production database modules/server: passed
production_database_plan_check: success true
tests/test_v41_production_database_plan.py: 5 passed
pytest: 529 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm/pnpm unavailable in this shell; only bundled node is available
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, after checks pass per user instruction
```

# V4.0 Production Launch Readiness Freeze

V4.0 adds production launch readiness freeze checks and V4 roadmap documentation. It does not perform a real production launch, connect real cloud services, connect a production database, commit production credentials, connect real identity services, connect real payments, upload logs externally, connect brokers, call external AI services, or change core strategy logic.

New files:

```text
scripts/production_launch_readiness_check.py
docs/V4_PRODUCTION_LAUNCH_READINESS.md
tests/test_v40_production_launch_readiness_freeze.py
```

Updated files:

```text
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/admin/page.tsx
README.md
REVIEW_PACKAGE.md
```

Production launch readiness scope:

- Added production launch readiness check script.
- Added production readiness API endpoint.
- Added frontend fetchProductionReadiness helper.
- Added Admin Console production launch readiness module.
- Added V4 production launch readiness documentation.

Readiness status:

- demo_ready: true
- production_ready: false

Safety boundaries:

- Real production launch: no
- Real cloud service connected: no
- Real production secret committed: no
- Real production database connected: no
- Real identity service connected: no
- Real payment connected: no
- External log upload: no
- Broker connection: no
- Auto trading: no
- AI API calls: no
- Core strategy logic changed: no

Validation:

```text
py_compile production launch readiness/server modules: passed
production_launch_readiness_check: success true
v3_release_candidate_check: success true
deployment_dry_run_check: success true
tests/test_v40_production_launch_readiness_freeze.py: 5 passed
pytest: 524 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm/pnpm unavailable in this shell; only bundled node is available
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, after checks pass per user instruction
```

# V3.9 Pricing / Packaging / Commercial Readiness

V3.9 adds pricing / packaging / commercial readiness for future SaaS packaging demos. It does not add trading functionality, change core strategy logic, connect real payments, connect Stripe live, collect cards, connect real customers, perform a production launch, connect real cloud services, connect real identity services, execute payments, upload logs externally, connect brokers, call external AI services, or commit production credentials.

New files:

```text
web/frontend/app/pricing/page.tsx
web/frontend/app/components/PricingPlanCard.tsx
docs/COMMERCIAL_READINESS.md
tests/test_v39_pricing_packaging_commercial_readiness.py
```

Updated files:

```text
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
web/frontend/app/admin/page.tsx
web/frontend/scripts/verify-build.mjs
README.md
REVIEW_PACKAGE.md
```

Commercial readiness scope:

- Added Pricing page.
- Added PricingPlanCard component.
- Added pricing plan API endpoint.
- Added frontend fetchPricingPlan helper.
- Added Admin Console commercial readiness module.
- Added Pricing navigation.
- Added commercial readiness documentation.

Safety boundaries:

- Real payment connected: no
- Stripe live connected: no
- Credit card storage: no
- Real customer connected: no
- New trading functionality: no
- Core strategy logic changed: no
- Real production launch: no
- Real cloud service connected: no
- Real production secret committed: no
- Real identity service connected: no
- Real payment execution: no
- External log upload: no
- Broker connection: no
- Auto trading: no
- AI API calls: no

Validation:

```text
py_compile server module: passed
tests/test_v39_pricing_packaging_commercial_readiness.py: 5 passed
pytest: 519 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm/pnpm unavailable in this shell; only bundled node is available
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, after checks pass per user instruction
```

# V3.8 Customer Workspace Demo Flow

V3.8 adds a customer workspace demo flow for product walkthroughs. It does not add trading functionality, change core strategy logic, connect real customers, connect real billing, perform a production launch, connect real cloud services, connect real identity services, execute payments, upload logs externally, connect brokers, call external AI services, or commit production credentials.

New files:

```text
web/frontend/app/workspace-demo/page.tsx
web/frontend/app/components/WorkspaceDemoCard.tsx
docs/WORKSPACE_DEMO_FLOW.md
tests/test_v38_customer_workspace_demo_flow.py
```

Updated files:

```text
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
web/frontend/app/admin/page.tsx
web/frontend/scripts/verify-build.mjs
README.md
REVIEW_PACKAGE.md
```

Workspace demo scope:

- Added Workspace Demo page.
- Added WorkspaceDemoCard component.
- Added workspace demo API endpoint.
- Added frontend fetchWorkspaceDemo helper.
- Added Admin Console workspace demo module.
- Added Workspace Demo navigation.
- Added workspace demo documentation.

Safety boundaries:

- New trading functionality: no
- Core strategy logic changed: no
- Real customer connected: no
- Real billing connected: no
- Production launch: no
- Real cloud service connected: no
- Real production secret committed: no
- Real identity service connected: no
- Real payment execution: no
- External log upload: no
- Broker connection: no
- Auto trading: no
- AI API calls: no

Validation:

```text
py_compile server module: passed
tests/test_v38_customer_workspace_demo_flow.py: 5 passed
pytest: 514 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm/pnpm unavailable in this shell; only bundled node is available
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, after checks pass per user instruction
```

# V3.7 Product Onboarding & First-Run Experience

V3.7 adds product onboarding and first-run experience. It does not add trading functionality, change core strategy logic, perform a production launch, connect real cloud services, connect real identity services, execute payments, upload logs externally, connect brokers, call external AI services, or commit production credentials.

New files:

```text
web/frontend/app/onboarding/page.tsx
web/frontend/app/components/FirstRunChecklist.tsx
docs/PRODUCT_ONBOARDING.md
tests/test_v37_product_onboarding_first_run_experience.py
```

Updated files:

```text
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/components/ProductionShell.tsx
web/frontend/app/admin/page.tsx
web/frontend/scripts/verify-build.mjs
README.md
REVIEW_PACKAGE.md
```

Onboarding scope:

- Added onboarding page.
- Added first-run checklist component.
- Added onboarding API endpoint.
- Added frontend fetchOnboarding helper.
- Added Admin Console onboarding readiness module.
- Added onboarding navigation.
- Added product onboarding documentation.

Safety boundaries:

- New trading functionality: no
- Core strategy logic changed: no
- Production launch: no
- Real cloud service connected: no
- Real production secret committed: no
- Real identity service connected: no
- Real payment execution: no
- External log upload: no
- Broker connection: no
- Auto trading: no
- AI API calls: no

Validation:

```text
py_compile server module: passed
tests/test_v37_product_onboarding_first_run_experience.py: 5 passed
pytest: 509 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm/pnpm unavailable in this shell; only bundled node is available
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, after checks pass per user instruction
```

# V3.6 Release Candidate QA & Product Demo Freeze

V3.6 adds V3 release candidate QA and product demo freeze checks. It does not add trading functionality, change core strategy logic, perform a production launch, connect real cloud services, connect a production database, configure a real domain or TLS certificate, connect real identity services, execute payments, upload logs externally, connect brokers, call external AI services, or commit production credentials.

New files:

```text
scripts/v3_release_candidate_check.py
docs/V3_PRODUCT_DEMO_FREEZE.md
tests/test_v36_release_candidate_qa_product_demo_freeze.py
```

Updated files:

```text
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/admin/page.tsx
docs/LOCAL_DEMO_GUIDE.md
docs/EXTERNAL_DEPLOYMENT_DRY_RUN.md
docs/OPERATIONS_RUNBOOK.md
README.md
REVIEW_PACKAGE.md
```

Release candidate QA scope:

- Added V3 release candidate check script.
- Added V3 product demo freeze documentation.
- Added V3 release candidate API endpoint.
- Added Admin Console release candidate freeze module.
- Added frontend fetchV3ReleaseCandidate helper.
- Updated local demo and operations docs.

Safety boundaries:

- New trading functionality: no
- Core strategy logic changed: no
- Production launch: no
- Real cloud service connected: no
- Real production secret committed: no
- Real production database connected: no
- Real domain / TLS connected: no
- Real identity service connected: no
- Real payment execution: no
- External log upload: no
- Broker connection: no
- Auto trading: no
- AI API calls: no

Validation:

```text
py_compile v3 release candidate/server modules: passed
v3_release_candidate_check: success true
deployment_dry_run_check: success true
tests/test_v36_release_candidate_qa_product_demo_freeze.py: 6 passed
pytest: 504 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm/pnpm unavailable in this shell; only bundled node is available
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V3.5 External Deployment Dry Run

V3.5 adds external deployment dry run planning and deployment readiness checks. It is not a real production launch and does not add real cloud services, production database connectivity, real domains, TLS material, external log upload, trading functionality, payment execution, broker connectivity, external AI calls, or core strategy logic changes.

New files:

```text
src/config/deployment_config.py
scripts/deployment_dry_run_check.py
docs/EXTERNAL_DEPLOYMENT_DRY_RUN.md
tests/test_v35_external_deployment_dry_run.py
```

Updated files:

```text
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/admin/page.tsx
docs/DEPLOYMENT.md
docs/OPERATIONS_RUNBOOK.md
README.md
REVIEW_PACKAGE.md
```

External deployment dry run scope:

- Added deployment configuration planning layer.
- Added deployment dry run check script.
- Added deployment dry run API endpoint.
- Added Admin Console deployment dry run module.
- Added frontend fetchDeploymentDryRun helper.
- Added external deployment dry run documentation.
- Updated deployment docs and operations runbook.

Safety boundaries:

- Real cloud service connected: no
- Real production secret committed: no
- Real production database connected: no
- Real domain / TLS connected: no
- External log upload: no
- New trading functionality: no
- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Stripe live API calls: no
- AI API calls: no

Validation:

```text
py_compile deployment/server modules: passed
deployment_dry_run_check: success true
tests/test_v35_external_deployment_dry_run.py: 6 passed
pytest: 498 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm/pnpm unavailable in this shell; only bundled node is available
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V3.4 Observability / Logs / Metrics Planning

V3.4 adds observability planning and local metrics summaries. It does not add an external monitoring service, Sentry, Datadog, Grafana Cloud, external log upload, trading functionality, payment execution, broker connectivity, external AI calls, or core strategy logic changes.

New files:

```text
src/config/observability_config.py
src/observability/__init__.py
src/observability/metrics.py
docs/OBSERVABILITY_PLAN.md
tests/test_v34_observability_logs_metrics_planning.py
```

Updated files:

```text
src/api/v2/logging.py
src/api/v2/server.py
web/frontend/app/lib/apiClient.ts
web/frontend/app/admin/page.tsx
README.md
REVIEW_PACKAGE.md
```

Observability planning scope:

- Added observability configuration planning layer.
- Added local metrics collector.
- Added local health timeline summary.
- Added observability API endpoint.
- Added Admin Console observability module.
- Added frontend fetchObservability helper.
- Added observability planning documentation.

Safety boundaries:

- External monitoring service: no
- Sentry / Datadog / Grafana: no
- External log upload: no
- Raw session / token / header logging: no
- New trading functionality: no
- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Stripe live API calls: no
- AI API calls: no
- Production credentials committed: no

Validation:

```text
py_compile observability/server modules: passed
tests/test_v34_observability_logs_metrics_planning.py: 6 passed
pytest: 492 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm/pnpm unavailable in this shell; only bundled node is available
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V3.3 Production Identity Provider Planning

V3.3 adds production identity system planning. It does not add a real identity service, OAuth, Google/GitHub login, production password auth, trading functionality, payment execution, broker connectivity, external AI calls, or core strategy logic changes.

New files:

```text
src/config/identity_config.py
src/auth/identity_provider.py
web/frontend/app/lib/identityStatus.ts
docs/PRODUCTION_IDENTITY_PLAN.md
tests/test_v33_production_identity_provider_planning.py
```

Updated files:

```text
src/api/v2/server.py
web/frontend/app/login/page.tsx
web/frontend/app/admin/page.tsx
web/frontend/app/styles.css
README.md
REVIEW_PACKAGE.md
```

Identity planning scope:

- Added identity configuration planning layer.
- Added identity provider planning interface.
- Added public identity plan endpoint.
- Added frontend identity status helper.
- Updated login page identity boundary copy.
- Updated Admin Console identity provider module.
- Added production identity planning documentation.

Safety boundaries:

- Real identity service: no
- OAuth: no
- Google/GitHub login: no
- Password storage: no
- Provider secret storage: no
- New trading functionality: no
- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Stripe live API calls: no
- AI API calls: no
- Production credentials committed: no

Validation:

```text
py_compile identity/server modules: passed
tests/test_v33_production_identity_provider_planning.py: 6 passed
pytest: 486 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm/pnpm unavailable in this shell; only bundled node is available
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V3.2 Frontend Auth Flow & Session UX

V3.2 adds frontend demo auth and session UX. It does not add a real identity service, OAuth, trading functionality, payment execution, broker connectivity, external AI calls, or core strategy logic changes.

New files:

```text
web/frontend/app/lib/authClient.ts
web/frontend/app/components/AuthStatus.tsx
web/frontend/app/components/PermissionNotice.tsx
docs/FRONTEND_AUTH_FLOW.md
tests/test_v32_frontend_auth_flow_session_ux.py
```

Updated files:

```text
web/frontend/app/lib/apiClient.ts
web/frontend/app/lib/sanitize.ts
web/frontend/app/login/page.tsx
web/frontend/app/admin/page.tsx
web/frontend/app/dashboard/page.tsx
web/frontend/app/styles.css
README.md
REVIEW_PACKAGE.md
```

Auth/session UX scope:

- Added frontend demo auth client.
- Added demo login / logout UX.
- Added role-aware frontend session state.
- Added API client session header support.
- Added AuthStatus and PermissionNotice components.
- Updated Admin Console with auth state.
- Updated Dashboard with auth state.
- Added frontend auth flow documentation.

Safety boundaries:

- Real identity service: no
- OAuth: no
- Password storage: no
- API key storage: no
- New trading functionality: no
- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Stripe live API calls: no
- AI API calls: no
- Production credentials committed: no

Validation:

```text
tests/test_v32_frontend_auth_flow_session_ux.py: 7 passed
pytest: 480 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm unavailable in shell; bundled pnpm install/build blocked by local dependency build approval for sharp
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V3.1 Real Frontend API Integration

V3.1 connects the polished Next.js frontend to backend health and admin APIs. It does not add trading functionality, change core strategy logic, connect to brokers, execute payments, call external AI services, or store plaintext credentials.

New files:

```text
web/frontend/app/lib/apiClient.ts
web/frontend/app/lib/sanitize.ts
web/frontend/app/components/LoadingState.tsx
web/frontend/app/components/ErrorState.tsx
docs/FRONTEND_API_INTEGRATION.md
tests/test_v31_real_frontend_api_integration.py
```

Updated files:

```text
web/frontend/app/admin/page.tsx
web/frontend/app/dashboard/page.tsx
web/frontend/app/styles.css
README.md
REVIEW_PACKAGE.md
```

Frontend API scope:

- Added frontend API client.
- Connected Admin Console to backend API with fallback data.
- Connected Dashboard to backend health APIs.
- Added frontend loading and error states.
- Added frontend sanitizer for API payloads.
- Added frontend API integration document.

Safety boundaries:

- New trading functionality: no
- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Stripe live API calls: no
- AI API calls: no
- Production credentials committed: no
- Plaintext password / session value / API key storage: no

Validation:

```text
tests/test_v31_real_frontend_api_integration.py: 6 passed
pytest: 473 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm unavailable in shell; bundled pnpm install/build blocked by local dependency build approval for sharp
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V3.0 UI / UX Polish & Product Experience Upgrade

V3.0 is a UI / UX and product experience polish release. It does not add trading functionality, change core strategy logic, connect to brokers, execute payments, call external AI services, or store plaintext credentials.

New files:

```text
web/frontend/app/components/StatusBadge.tsx
web/frontend/app/components/MetricCard.tsx
web/frontend/app/components/EmptyState.tsx
web/frontend/app/components/PageHeader.tsx
docs/UI_UX_REVIEW.md
tests/test_v30_ui_ux_product_polish.py
```

Updated files:

```text
web/frontend/app/components/ProductionShell.tsx
web/frontend/app/admin/page.tsx
web/frontend/app/dashboard/page.tsx
web/frontend/app/page.tsx
web/frontend/app/api-docs/page.tsx
web/frontend/app/login/page.tsx
web/frontend/app/reports/page.tsx
web/frontend/app/risk/page.tsx
web/frontend/app/settings/page.tsx
web/frontend/app/strategy/page.tsx
web/frontend/app/styles.css
README.md
REVIEW_PACKAGE.md
```

UI / UX scope:

- Polished Admin Console UI.
- Polished Dashboard / product shell.
- Added reusable UI components.
- Added unified status badge / card / empty state styles.
- Added active navigation state.
- Added product-level safety boundary messaging.
- Added UI UX review document.

Safety boundaries:

- New trading functionality: no
- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Stripe live API calls: no
- AI API calls: no
- Production credentials committed: no
- Plaintext password / session value / API key storage: no

Validation:

```text
tests/test_v30_ui_ux_product_polish.py: 6 passed
pytest: 467 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
npm build: npm unavailable in shell; bundled pnpm install/build blocked by local dependency build approval for sharp
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, after checks pass per user instruction
```

# V2.9 Architecture Review & Local Startup Verification

V2.9 is an architecture review and local startup verification release. It does not add business functionality, change core strategy logic, connect to brokers, place orders, execute payments, call external AI services, or store plaintext secrets.

New files:

```text
scripts/local_startup_verification.py
docs/V2_ARCHITECTURE_REVIEW.md
docs/LOCAL_DEMO_GUIDE.md
tests/test_v29_architecture_review_local_startup_verification.py
```

Updated files:

```text
README.md
REVIEW_PACKAGE.md
```

Verification scope:

- Local startup chain.
- API app import and creation.
- API health endpoint.
- Liveness endpoint.
- Readiness endpoint.
- Security health endpoint.
- Database health endpoint.
- Workspace health endpoint.
- Billing health endpoint.
- Admin Console in local mode.
- startup_check.
- v2_integration_check.
- system_doctor.
- Frontend Admin Console file.
- V2 release candidate document.
- Admin Console document.
- No committed `.env`.
- No obvious secret patterns.

Architecture review scope:

- API layer checked: yes
- Auth/session layer checked: yes
- Workspace layer checked: yes
- Quota/usage layer checked: yes
- Deployment layer checked: yes
- Admin Console checked: yes
- Local startup chain checked: yes

Safety boundaries:

- New business functionality: no
- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Stripe live API calls: no
- AI API calls: no
- Production secrets committed: no
- Plaintext password / session value / API key storage: no

Validation:

```text
py_compile: passed
startup_check: passed
v2_integration_check: passed
local_startup_verification: passed
tests/test_v29_architecture_review_local_startup_verification.py: 5 passed
pytest: 461 passed
system_doctor: OK
frontend structure check: passed via node scripts/verify-build.mjs
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V2.8 Admin Console / Product Control Center

V2.8 adds an Admin Console / Product Control Center for product operations visibility only. It does not add trading behavior, real payment execution, Stripe live integration, broker connectivity, external AI calls, frontend architecture changes, or strategy logic changes.

New files:

```text
src/api/v2/admin_console.py
web/frontend/app/admin/page.tsx
docs/ADMIN_CONSOLE.md
tests/test_v28_admin_console_product_control_center.py
```

Updated files:

```text
src/api/v2/server.py
web/frontend/app/components/ProductionShell.tsx
web/frontend/app/styles.css
README.md
REVIEW_PACKAGE.md
```

Admin Console coverage:

- System overview.
- API health and V2 service status.
- Database status.
- Auth and security policy status.
- Workspace status.
- Plan / quota status.
- Deployment readiness.
- Release candidate status.
- Sanitized aggregated output.
- Submodule failures degrade to warning instead of crashing the endpoint.

Safety boundaries:

- New core strategy functionality: no
- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Stripe live API calls: no
- AI API calls: no
- Production secrets committed: no
- Plaintext password / session value / API key storage: no

Validation:

```text
py_compile: passed
tests/test_v28_admin_console_product_control_center.py: 6 passed
pytest: 456 passed
system_doctor: OK
frontend build / structure check: structure check passed via node scripts/verify-build.mjs; npm unavailable in shell and bundled pnpm build was blocked by local dependency build approval for sharp
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, after checks pass per user instruction
```

# V2.7 Release Freeze & Integration QA

V2.7 is the first V2 release-freeze and total integration QA pass. It does not add business features, real payment execution, Stripe live integration, broker connectivity, trading behavior, AI calls, frontend UI changes, or strategy logic changes.

New files:

```text
scripts/v2_integration_check.py
tests/test_v27_release_freeze_integration_qa.py
docs/V2_RELEASE_CANDIDATE.md
```

Updated files:

```text
README.md
REVIEW_PACKAGE.md
```

Integration checks:

- Database initialization.
- Repeatable migrations.
- Default user creation.
- Default workspace creation.
- Local auth default-admin fallback.
- Production protected endpoint anonymous 401.
- Mock login session creation.
- Session access to protected report list.
- Viewer report-write denial.
- User admin denial.
- Workspace isolation denial.
- Usage event recording.
- Quota exceeded response.
- Readiness, liveness, security-health, billing-health, and workspace-health.
- Startup check.
- System doctor.
- Runtime obvious-risk scan.

Cleanup decision:

- `src/security/init.py`: retained intentionally.
- `src/workspace/init.py`: retained intentionally.
- `src/billing/init.py`: retained intentionally.
- `src/auth/init.py`: retained intentionally.
- No files deleted; each reviewed file contains functional initializer/export helpers.

Safety boundaries:

- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Stripe live API calls: no
- AI API calls: no
- Production secrets committed: no
- Plaintext password / session value / API key storage: no

Validation:

```text
py_compile: passed
startup_check: passed
v2_integration_check: passed
tests/test_v27_release_freeze_integration_qa.py: 6 passed
pytest: 450 passed
system_doctor: OK
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, after checks pass per user instruction
```

# V2.6 Deployment / Ops Readiness

V2.6 adds deployment and operations readiness only. It does not add business features, real payment execution, Stripe live integration, broker connectivity, trading behavior, AI calls, or strategy logic changes.

New files:

```text
.env.example
Dockerfile
docker-compose.yml
docker-compose.prod.example.yml
nginx/nginx.conf.example
scripts/startup_check.py
docs/DEPLOYMENT.md
docs/OPERATIONS_RUNBOOK.md
docs/SECURITY_CHECKLIST.md
.github/workflows/ci.yml
tests/test_v26_deployment_ops_readiness.py
```

Updated files:

```text
src/api/v2/server.py
src/system/health_check.py
README.md
REVIEW_PACKAGE.md
```

Deployment readiness:

- Added root `.env.example` with placeholders only.
- Added startup check.
- Added liveness endpoint.
- Added readiness endpoint.
- Added Dockerfile.
- Added local Docker Compose.
- Added production-like Docker Compose example.
- Added Nginx example config.
- Added deployment guide.
- Added operations runbook.
- Added security checklist.
- Added CI workflow.

Safety boundaries:

- Current status: research / SaaS foundation
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Stripe live API calls: no
- AI API calls: no
- Production secrets committed: no
- Plaintext password / session value / API key storage: no
- Core strategy logic changed: no

Validation:

```text
py_compile: passed
startup_check: passed
tests/test_v26_deployment_ops_readiness.py: 8 passed
pytest: 444 passed
system_doctor: OK
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, after checks pass per user instruction
```

# V2.5 Plan / Quota / Usage Limit

V2.5 adds local plan, quota, and usage-limit foundations only. It does not add real payment execution, Stripe live integration, broker connectivity, trading behavior, AI calls, or strategy logic changes.

New files:

```text
src/config/plan_config.py
src/db/usage_repository.py
src/billing/init.py
src/billing/plan_service.py
src/billing/quota_service.py
src/billing/usage_service.py
tests/test_v25_plan_quota_usage_limit.py
```

Updated files:

```text
src/db/models.py
src/api/v2/server.py
README.md
REVIEW_PACKAGE.md
```

Plan / quota layer:

- Added local `free`, `pro`, and `team` plan limits.
- Added environment override support with fallback to safe defaults.
- Added `usage_events` model.
- Added `quota_snapshots` model.
- Added usage repository with workspace-isolated queries.
- Added plan service for workspace-level mock plans.
- Added usage service for daily usage tracking.
- Added quota service with `QUOTA_EXCEEDED` standard API errors.
- Added quota enforcement for report generation and selected API calls.
- Added `/api/v2/billing/plan`.
- Added `/api/v2/billing/quota`.
- Added `/api/v2/system/billing-health`.

Safety boundaries:

- Billing mode: mock only
- Stripe live API calls: no
- Real payment execution: no
- Payment secrets stored: no
- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- AI API calls: no
- Secrets stored in plaintext: no

Validation:

```text
py_compile: passed
tests/test_v25_plan_quota_usage_limit.py: 7 passed
pytest: 436 passed
system_doctor: OK
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, after checks pass per user instruction
```

# V2.4 Workspace / Tenant Isolation

V2.4 adds workspace / tenant isolation only. It does not add real payments, broker connectivity, trading behavior, AI calls, or strategy logic changes.

New files:

```text
src/db/workspace_repository.py
src/workspace/__init__.py
src/workspace/init.py
src/workspace/workspace_context.py
src/workspace/workspace_service.py
tests/test_v24_workspace_tenant_isolation.py
```

Updated files:

```text
src/db/models.py
src/db/migrations.py
src/db/repository.py
src/auth/auth_context.py
src/api/v2/auth.py
src/api/v2/server.py
README.md
REVIEW_PACKAGE.md
```

Workspace isolation:

- Added `workspaces` and `workspace_members` tables.
- Added `workspace_id` compatibility columns to users, reports, API keys, billing plans, audit logs, sessions, and permissions.
- Existing and missing workspace data defaults to `default`.
- Added workspace repository methods for create, get, list, member add/remove/list, role lookup, and default workspace initialization.
- Added workspace service methods for active context, access checks, and role checks.
- AuthContext now includes workspace ID, workspace role, and workspace permissions.
- API v2 accepts `X-Workspace-ID` and `workspace_id` query parameters.
- Report listing is workspace-filtered.
- Production mode requires workspace membership for protected workspace access.
- Local mode keeps default workspace fallback for local development.
- Added `/api/v2/workspaces`.
- Added `/api/v2/system/workspace-health`.
- Workspace audit events are sanitized.

Safety boundaries:

- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Plaintext password / session value / API key storage: no
- AI API calls: no
- Secrets stored in plaintext: no

Validation:

```text
py_compile: passed
tests/test_v24_workspace_tenant_isolation.py: 9 passed
pytest: 429 passed
system_doctor: OK
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: yes, after checks pass per user instruction
```

# V2.3 Production Auth Mode & Security Policy

V2.3 hardens production auth mode and security policy only. It does not add real payment execution, real identity provider integration, broker connectivity, trading behavior, AI calls, or strategy logic changes.

New files:

```text
src/config/auth_config.py
src/security/__init__.py
src/security/init.py
src/security/policy.py
src/security/sanitizer.py
tests/test_v23_production_auth_security_policy.py
```

Updated files:

```text
src/api/v2/auth.py
src/api/v2/errors.py
src/api/v2/server.py
src/auth/session_service.py
README.md
REVIEW_PACKAGE.md
```

Production auth policy:

- Added explicit `local`, `dev`, and `production` auth modes.
- Local mode keeps default-admin fallback for local development compatibility.
- Dev mode supports mock sessions and API keys without anonymous admin promotion.
- Production mode requires a valid session or API key on protected endpoints.
- Production mode disables local default-admin fallback.
- Missing production credentials return `AUTH_REQUIRED`.
- Invalid sessions return `INVALID_SESSION`.
- Invalid API keys return `INVALID_API_KEY`.
- Permission failures return `PERMISSION_DENIED`.
- `/api/v2/system/security-health` reports the active security policy.
- Production mock login returns a `mock_auth_only` warning.

Security and audit hardening:

- Added central `SecurityPolicy`.
- Added sensitive data sanitizer.
- Audit metadata removes raw session IDs, raw API keys, authorization headers, passwords, tokens, database paths, and local absolute paths.
- Added auth audit actions for mode checks, required auth, invalid session, invalid API key, permission denial, and policy checks.

Safety boundaries:

- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Plaintext password / session value / API key storage: no
- AI API calls: no
- Secrets stored in plaintext: no

Validation:

```text
py_compile: passed
tests/test_v23_production_auth_security_policy.py: 11 passed
pytest: 420 passed
system_doctor: OK
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V2.2 Auth / User Session Hardening

V2.2 hardens the auth, session, API key, and permission structure only. It does not add real payments, real identity provider integration, trading behavior, or strategy logic changes.

New files:

```text
src/auth/init.py
src/auth/session_service.py
src/auth/permission_service.py
src/auth/api_key_service.py
src/auth/auth_context.py
src/api/v2/auth.py
tests/test_v22_auth_session_hardening.py
```

Updated files:

```text
src/db/models.py
src/db/repository.py
src/api/v2/server.py
src/system/health_check.py
README.md
REVIEW_PACKAGE.md
```

Auth hardening:

- Auth context added.
- Session service added.
- Permission service added.
- API key verification service added.
- Auth middleware helpers added.
- Mock login/logout/me endpoints added.
- RBAC permission checks added.
- Auth audit logs added.
- Sensitive data sanitization added.
- V2.0 database foundation preserved.
- V2.1 API hardening layer preserved.

Important limitation:

- Current login is local mock login only, not a real production login system.
- No real user passwords are stored.
- No plaintext session values are stored.
- No plaintext API keys are stored.

Safety boundaries:

- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Plaintext password / session value / API key storage: no
- AI API calls: no

Validation:

```text
py_compile: passed
tests/test_v22_auth_session_hardening.py: 9 passed
pytest: 409 passed
system_doctor: OK
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V2.1 API Production Hardening

V2.1 hardens the API layer only. It does not add business features, change core strategy logic, change trading behavior, or change payment behavior.

New files:

```text
src/api/v2/response.py
src/api/v2/errors.py
src/api/v2/schemas.py
src/api/v2/pagination.py
src/api/v2/middleware.py
src/api/v2/logging.py
tests/test_v21_api_production_hardening.py
```

Updated files:

```text
src/api/v2/server.py
README.md
REVIEW_PACKAGE.md
```

API hardening:

- Production API response standard added.
- Error handling layer added.
- Request validation schemas added.
- Pagination utilities added.
- CORS middleware added with local origins by default.
- Basic in-memory rate limit added.
- API logging added with sensitive data sanitization.
- DB health endpoint enhanced.
- V2.0 database foundation preserved.

Safety boundaries:

- Core strategy logic changed: no
- Broker connection: no
- Auto trading: no
- Real payment execution: no
- Plaintext secret / token / password storage: no
- AI API calls: no

Validation:

```text
py_compile: passed
tests/test_v21_api_production_hardening.py: 10 passed
pytest: 400 passed
system_doctor: OK
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# V2.0 Production Data Foundation

V2.0 adds the production data foundation layer only. It does not change core strategy logic, trading behavior, or payment behavior.

New files:

```text
src/config/database_config.py
src/db/__init__.py
src/db/base.py
src/db/models.py
src/db/session.py
src/db/repository.py
src/db/migrations.py
src/db/archive_importer.py
tests/test_v2_database_foundation.py
```

Updated files:

```text
src/api/v2/server.py
README.md
REVIEW_PACKAGE.md
```

Database:

- Default database location: `data/shandong_v2.db`
- Default database URL: `sqlite:///data/shandong_v2.db`
- SQLite is used for local development.
- PostgreSQL is reserved through configuration shape, but not required.

Compatibility:

- Supports old report archive compatibility: yes
- Existing `reports/strategy_research_reports/` files remain readable.
- `import_archived_reports_to_db(user_id="default")` imports legacy JSON files into the database.
- Broken archive files produce warnings instead of crashes.

Safety boundaries:

- Core strategy logic changed: no
- Broker connection: no
- Auto orders: no
- Real payment execution: no
- Plaintext API key / token / password storage: no
- AI API calls: no

Validation:

```text
tests/test_v2_database_foundation.py: 9 passed
pytest: 390 passed
system_doctor: OK
```

Review recommendation:

```text
Whether to create PR: yes
Whether to merge now: no, wait for human review
```

# REVIEW_PACKAGE.md

请帮我审查这个 GitHub Pull Request：

https://github.com/yvonnesun1992-lang/shandong/pull/1

## 审查目标

这是一个入门友好的 A股 + 美股趋势量化研究系统 V1。

请重点检查：

1. 项目结构是否合理。
2. 依赖是否合理，是否容易安装。
3. Python 文件是否有格式、缩进、SyntaxError 问题。
4. 趋势评分逻辑是否清晰、是否符合 AGENTS.md。
5. 简单回测逻辑是否有明显错误。
6. Streamlit dashboard 是否容易崩溃。
7. 是否存在真实交易、券商连接、自动下单、密钥泄露等危险逻辑。

## 当前分支和提交

- 分支：`codex/v1-quant-system`
- PR：`#1`
- 最新代码验证提交：`026d9a4 Restore raw Python files to valid multiline format`
- 上一个提交：`cbcd5b0 Make raw files visibly multiline`
- Raw 刷新提交：`70c1a84 Force raw files to refresh LF formatting`
- Raw 复查提交：`644b3c8 Reverify LF raw formatting`
- 格式规则提交：`ab5eb41 Enforce LF formatting and guard empty watchlists`
- 重要修复提交：`80636e2 Fix V1 install and runtime issues`

## 项目安全边界

V1 只做：

- 行情数据获取
- 技术指标计算
- 趋势评分
- 简单回测
- Streamlit 可视化
- 测试验证

V1 明确不做：

- 不连接真实券商
- 不自动下单
- 不做实盘交易
- 不使用 AI 预测股价
- 不保存或读取 API key、密码、券商凭证

## V1.16: strategy lab and presets

V1.16 目标：

- 增加“策略实验室”页面。
- 支持本地策略参数预设。
- 支持用策略预设运行组合回测。
- 页面保持简约、美观、大方、实用。
- 不改变已有核心策略逻辑，只做参数预设和调用。

新增文件：

```text
config/strategy_presets.json
src/strategies/presets.py
tests/test_strategy_presets.py
```

修改文件：

```text
app/main.py
src/ui/layout.py
README.md
REVIEW_PACKAGE.md
```

策略实验室功能说明：

- dashboard 新增“策略实验室”tab，位于首页和市场总览之后。
- 显示本地策略预设列表和关键参数。
- 支持查看所选策略预设详情。
- 支持保存现有或新增策略预设。
- 默认策略禁止在 dashboard 删除，避免误删基础配置。
- 非默认策略支持勾选确认后删除。
- 支持用当前 watchlist 和所选策略参数运行组合回测。
- 展示总收益、年化收益、最大回撤、最终资产和交易次数。
- 支持导出策略回测净值曲线和交易记录 CSV。

配置管理说明：

- `config/strategy_presets.json` 只保存研究参数，不保存账户、密码、API key 或券商凭证。
- `src/strategies/presets.py` 校验 preset 名称、参数范围、策略类型和调仓频率。
- JSON 损坏时抛出清晰 `ValueError`。
- 路径只允许 `config/strategy_presets.json`，拒绝路径穿越。

检查结果：

```text
py_compile: passed
pytest: 211 passed
system_doctor: passed
dashboard: passed
```

安全边界：

```text
是否改变核心策略逻辑：否
UI 是否保持简约、美观、大方、实用：是
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V5.39: Local Desktop Launcher

V5.39 新增本地桌面启动器，用于检查本地环境、生成 backend/frontend/browser 启动计划、输出本地启动日志，并提供 Mac / Windows 启动脚本。

新增内容：

- `config/v5_local_launcher_config.py`
- `local_launcher/`
- `scripts/run_v539_local_launcher.py`
- `scripts/start_shandong_mac.command`
- `scripts/start_shandong_windows.bat`
- `docs/V5_LOCAL_DESKTOP_LAUNCHER.md`
- `web/frontend/app/v5-local-launcher/page.tsx`
- `/api/v5/local-launcher/*` endpoints
- `tests/test_v539_local_launcher.py`

安全边界：

- 是否接真实券商：否
- 是否接 sandbox API：否
- 是否读取 secret / token / password / API key：否
- 是否读取账户 / 余额 / 持仓：否
- 是否提交订单：否
- 是否接真实资金：否
- 是否改变 alpha model / 因子逻辑 / 策略逻辑：否

验证结果：

- py_compile: passed
- CLI dry-run / check matrix: passed
- targeted pytest: 4 passed
- full pytest: 872 passed
- system_doctor: OK
- frontend structure check: passed
- local launcher dry-run verdict: WARNING only because current machine reported Node unavailable; Python checks and CLI completed successfully.

## V5.40: Product Home Dashboard

V5.40 新增产品化首页，让用户打开前端即可看到系统状态、Local Launcher、Paper Trading、Backtest、Risk Boundary、Recent Activity、主要功能入口和下一步建议。

新增内容：

- `config/v5_product_home_config.py`
- `product_home/`
- `scripts/run_v540_product_home_dashboard.py`
- `docs/V5_PRODUCT_HOME_DASHBOARD.md`
- `reports/v5_40_product_home_dashboard_report.md`
- `tests/test_v540_product_home_dashboard.py`
- `/api/v5/product-home/*` endpoints
- `web/frontend/app/page.tsx` 产品化首页

安全边界：

- 是否接真实券商：否
- 是否接 sandbox API：否
- 是否读取 secret / token / password / API key：否
- 是否读取真实账户 / 余额 / 持仓：否
- 是否提交订单：否
- 是否接真实资金：否
- 是否改变 alpha model / 因子逻辑 / 策略逻辑：否

验证结果：

- py_compile: passed
- CLI checks: passed
- targeted pytest: 4 passed
- full pytest: 876 passed
- system_doctor: OK
- frontend structure check: passed
- product home summary verdict: WARNING only because current machine reported Node unavailable through V5.39 launcher checks; Product Home remains usable and reports it as a warning.

## V1.31: platform layer

V1.31 目标：

- 增加插件系统。
- 增加 FastAPI API 层。
- 增加逻辑多用户隔离。
- 增加 Platform Launcher。
- 保持研究系统安全边界。

新增文件：

```text
PLATFORM_PACKAGE.md
app/platform.py
src/api/__init__.py
src/api/server.py
src/core/user_context.py
src/plugins/__init__.py
src/plugins/base.py
src/plugins/dashboard_plugin.py
src/plugins/registry.py
src/plugins/report_plugin.py
src/plugins/risk_plugin.py
src/plugins/strategy_plugin.py
tests/test_v131_platform.py
```

修改文件：

```text
README.md
REVIEW_PACKAGE.md
requirements.txt
```

平台层说明：

- 插件系统支持 report、strategy、risk 和 dashboard 插件动态注册。
- API 层提供标准 JSON 返回结构。
- UserContext 提供 report、cache 和 dashboard 逻辑隔离 key。
- Platform Launcher 按 INIT -> CONFIG -> CACHE -> PLUGINS -> API -> UI 初始化。

检查结果：

```text
py_compile: passed
pytest: 360 passed
system_doctor: passed
dashboard: returned 200
changed files: real UTF-8 + LF multiline files
local Unicode scan risk_count: 0
source boundary scan findings: 0
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否调用 AI API：否
是否调用 OpenAI API：否
是否预测股价：否
是否保存 API key/secret/password/token：否
是否新增支付或真实登录系统：否
是否改变核心策略逻辑：否
是否 merge PR：否
```

## V1.32: release and SaaS-ready layer

V1.32 目标：

- 增加 Docker 部署结构。
- 增加 API v2 产品化返回格式。
- 增加 account 级逻辑多用户隔离。
- 增加 System Admin Panel 数据层。
- 增加平台配置中心。
- 增加 release notes。

新增文件：

```text
RELEASE_NOTES_V1.32.md
deploy/.env.example
deploy/Dockerfile
deploy/docker-compose.yml
src/api/v2/__init__.py
src/api/v2/server.py
src/config/platform_config.py
src/core/account/__init__.py
src/dashboard/system_admin.py
tests/test_v132_release.py
```

修改文件：

```text
README.md
REVIEW_PACKAGE.md
```

发布层说明：

- Docker Compose 可启动 UI 和 API 两个服务。
- API v2 返回 `success/data/meta/warning`，meta 包含 V1.32 和 latency_ms。
- AccountContext 使用 `data/users/{user_id}/` 隔离 report、cache 和 dashboard。
- System Admin Panel 汇总 API latency、cache hit rate、system health score、plugin status 和 error logs。
- Platform config 集中管理 CACHE_ENABLED、API_ENABLED、MULTI_USER 和 LOG_LEVEL。

检查结果：

```text
py_compile: passed
pytest: 368 passed
system_doctor: passed
dashboard: returned 200
api_v2: smoke endpoints returned 200 / success / V1.32
docker_sanity: deploy files tested; docker CLI unavailable in local environment
changed files: real UTF-8 + LF multiline files
local Unicode scan risk_count: 0
source boundary scan findings: 0
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否调用 AI API：否
是否调用 OpenAI API：否
是否预测股价：否
是否保存 API key/secret/password/token：否
是否新增支付或真实登录系统：否
是否改变核心策略逻辑：否
是否 merge PR：否
```

## V1.33: SaaS product final architecture

V1.33 目标：

- 增加 mock 用户系统。
- 增加 RBAC 权限系统。
- 增加 mock API key 系统。
- 增加 Web 前端页面结构。
- 增加模拟 SaaS 计费结构。
- 增加 SaaS 平台文档。

新增文件：

```text
SAAS_PLATFORM.md
src/auth/__init__.py
src/auth/api_keys.py
src/billing/__init__.py
src/core/rbac.py
tests/test_v133_saas.py
web/api-docs.html
web/dashboard.html
web/login.html
web/report-viewer.html
web/strategy-center.html
web/trend.html
```

修改文件：

```text
README.md
REVIEW_PACKAGE.md
```

SaaS 层说明：

- Auth 仅为 mock login/logout 和内存 session，不是真实认证系统。
- RBAC 支持 admin、user、viewer 和 report/dashboard/api 权限控制。
- API Key 系统为 mock 本地 key，支持 revoke、rate limit 和 usage tracking。
- Billing 仅提供 free/pro/team plan 结构，不做真实支付。
- Web 目录提供静态页面结构，不包含真实登录或支付逻辑。

检查结果：

```text
py_compile: passed
pytest: 375 passed
system_doctor: passed
dashboard: returned 200
changed files: real UTF-8 + LF multiline files
local Unicode scan risk_count: 0
source boundary scan findings: 0
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否调用 AI API：否
是否调用 OpenAI API：否
是否预测股价：否
是否真实支付：否
是否真实认证系统：否
是否保存敏感信息：否
是否改变核心策略逻辑：否
是否 merge PR：否
```

## V1.34: production launch architecture

V1.34 目标：

- 增加 Next.js Web 前端结构。
- 增加 JWT 认证系统结构。
- 增加 Stripe 支付系统结构，支付保持 mock。
- 增加 Docker + Nginx + CI/CD 云部署结构。
- 增加生产级监控系统。
- 增加生产上线文档。

新增文件：

```text
PRODUCTION_LAUNCH.md
.github/workflows/production-launch.yml
deploy/Dockerfile.production
deploy/docker-compose.production.yml
deploy/nginx/nginx.conf
src/auth/jwt_auth.py
src/billing/stripe/__init__.py
src/monitoring/__init__.py
tests/test_v134_production.py
web/frontend/package.json
web/frontend/next.config.js
web/frontend/tsconfig.json
web/frontend/scripts/verify-build.mjs
web/frontend/app/layout.tsx
web/frontend/app/page.tsx
web/frontend/app/styles.css
web/frontend/app/components/ChartCard.tsx
web/frontend/app/components/ProductionShell.tsx
web/frontend/app/login/page.tsx
web/frontend/app/dashboard/page.tsx
web/frontend/app/strategy/page.tsx
web/frontend/app/reports/page.tsx
web/frontend/app/risk/page.tsx
web/frontend/app/settings/page.tsx
web/frontend/app/api-docs/page.tsx
```

修改文件：

```text
README.md
REVIEW_PACKAGE.md
```

生产层说明：

- Next.js 前端采用 responsive card layout 和 chart component。
- JWT auth 支持 signup/login、session validation 和 protected route checks。
- Stripe billing shell 支持 subscription、checkout、webhook 和 plan catalog，live payment 为 false。
- Production deploy 包含 Dockerfile、Compose、Nginx reverse proxy 和 GitHub Actions workflow。
- Monitoring 支持 API latency、logs、system health 和 usage metrics。

检查结果：

```text
py_compile: passed
pytest: 381 passed
system_doctor: passed
dashboard: returned 200
frontend_build: bundled node structure verification passed; Next dev smoke returned 200 for /login, /dashboard, /reports, /strategy, /risk, /settings, /api-docs
changed files: real UTF-8 + LF multiline files
local Unicode scan risk_count: 0
source boundary scan findings: 0
```

Freeze stability fixes:

- Upgraded frontend package metadata to Next 16.2.9 / React 19.2.7 / Recharts 3.8.1 after install warned that Next 15.3.0 had a security issue.
- Added frontend TypeScript type dependencies and Next-generated TypeScript config requirements.
- Added `pnpm-lock.yaml` for production dependency reproducibility.

安全边界：

```text
是否连接真实券商：否
是否自动交易：否
是否生成真实交易指令：否
是否调用 AI API：否
是否调用 OpenAI API：否
是否预测股价：否
是否保存敏感数据：否
是否真实支付：否
是否做实盘交易逻辑：否
是否改变核心策略逻辑：否
是否 merge PR：否
```

V1.18 raw 文件已再次强制刷新，用于确认远程 raw 是真实多行文本。
V1.18 文件格式已再次验证 6，用于确认 GitHub 远程分支刷新。

## V1.18: allocation lab

V1.18 目标：

- 增加组合配置实验室。
- 基于当前 watchlist、趋势分数、价格和风险参数生成研究用目标仓位。
- 对比当前持仓与目标持仓之间的差异。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/portfolio/__init__.py
src/portfolio/allocation.py
tests/test_allocation.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

组合配置实验室功能说明：

- `build_allocation_plan` 根据股票池、趋势分数、价格、当前持仓和风险参数生成目标配置。
- 分数低于最低分数的股票目标仓位为 0。
- 单只股票目标权重不超过 max_position_pct。
- 系统保留 cash_buffer_pct 对应的现金缓冲。
- 缺失价格或无效价格不会导致崩溃，会记录到 failed_symbols 和 warnings。
- 输出目标权重、目标金额、目标股数、当前金额和差异金额。
- 所有输出均标注“仅供投资研究，不构成投资建议，不代表未来收益。”

dashboard 更新：

- 新增“组合配置实验室”tab。
- 支持设置组合总金额、单股最大仓位、最低入选分数和现金缓冲。
- 支持手动输入当前持仓，格式为 `symbol,数量`。
- 展示组合总金额、可投资金额、现金缓冲、入选股票数和单股最大仓位。
- 展示目标仓位表、目标权重柱状图、当前 vs 目标金额对比图。
- 支持下载 allocation_plan.csv 和 allocation_summary.json。

检查结果：

```text
py_compile: passed
pytest: 228 passed
dashboard: passed
```

安全边界：

```text
是否改变核心策略逻辑：否
UI 是否保持简约、美观、大方、实用：是
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否建议创建 PR：是
```

## V1.19: risk control center

V1.19 目标：

- 增加“风险控制中心”页面。
- 基于当前 watchlist、组合配置方案、模拟持仓和本地行情数据，检查研究组合风险。
- 展示仓位风险、集中度风险、现金缓冲风险、数据质量风险和回撤风险提示。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/risk/control.py
tests/test_risk_control.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

风险控制中心功能说明：

- `build_risk_control_report` 根据目标仓位行生成研究用风险报告。
- 输出组合总金额、目标持仓金额、现金缓冲、投资比例、最大单股仓位、前三大持仓占比、持仓数量和风险等级。
- 检查单股最大仓位、前三大持仓集中度、持仓分散度、现金缓冲、数据质量和回撤风险提示。
- 支持 Low / Medium / High 风险等级。
- allocation_rows 为空、portfolio_value 无效、target_weight 或 target_value 缺失时不会崩溃，会返回 warnings 和 checks。
- dashboard 新增“风险控制中心”tab，位于“组合配置实验室”之后。
- 支持使用组合配置逻辑重新生成 allocation 后检查风险。
- 支持手动输入简化仓位，格式为 `AAPL,0.18,18000`。
- 展示风险指标、风险检查表、单股风险表和目标仓位权重柱状图。
- 支持下载 risk_control_report.json、position_risks.csv 和 risk_checks.csv。
- 所有输出均标注“仅供投资研究，不构成投资建议，不代表未来收益。”

检查结果：

```text
py_compile: passed
pytest: 237 passed
system_doctor: passed
dashboard: passed
```

安全边界：

```text
是否改变核心策略逻辑：否
UI 是否保持简约、美观、大方、实用：是
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.20: strategy stability center

V1.20 目标：

- 增加“策略稳定性评估中心”页面。
- 支持把当前 watchlist 的历史数据拆成多个时间窗口。
- 对每个窗口调用已有组合回测逻辑，并汇总多窗口表现。
- 检查收益稳定性、回撤稳定性、胜率稳定性、样本数量风险和数据质量风险。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/strategies/stability.py
tests/test_strategy_stability.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

策略稳定性评估中心功能说明：

- `split_backtest_windows` 支持按行数切分 DataFrame 或组合 price_data dict。
- `build_strategy_stability_report` 只分析已有多窗口回测结果，不重新实现核心回测逻辑。
- 支持部分窗口失败，不让整体页面崩溃。
- 输出窗口数量、成功窗口、失败窗口、正收益窗口、平均收益、最差收益、最差回撤、收益一致性分数、回撤一致性分数和稳定性等级。
- 支持 Low / Medium / High 稳定性等级。
- dashboard 新增“策略稳定性”tab，位于“风险控制中心”之后。
- 支持选择 market、watchlist、strategy preset、initial_cash、window_size、step_size 和 min_windows。
- 展示稳定性指标、窗口结果表、稳定性检查表、收益柱状图、回撤柱状图和最终资产折线图。
- 支持下载 strategy_stability_report.json、stability_windows.csv 和 stability_checks.csv。
- 所有输出均标注“仅供投资研究，不构成投资建议，不代表未来收益。”

检查结果：

```text
py_compile: passed
pytest: 247 passed
system_doctor: passed
dashboard: passed
hidden/bidi scan: passed, risk_count=0
```

安全边界：

```text
是否改变核心策略逻辑：否
UI 是否保持简约、美观、大方、实用：是
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.21: out-of-sample test center

V1.21 目标：

- 增加“样本外测试中心”页面。
- 支持把当前 watchlist 的历史数据按行数切分为训练区间和未知测试区间。
- 对训练区间和样本外测试区间调用已有组合回测逻辑。
- 汇总训练收益、样本外收益、收益衰减、最大回撤、回撤恶化和交易次数。
- 输出 Low / Medium / High 过拟合风险等级。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/strategies/out_of_sample.py
tests/test_out_of_sample.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

样本外测试中心功能说明：

- `split_train_test_data` 支持 DataFrame 和组合 price_data dict，按 train_ratio 切分训练和测试数据。
- `split_train_test_data` 会把 train_ratio 限制在 0.5 到 0.9 之间，并对数据不足情况返回 warnings。
- `build_out_of_sample_report` 只分析训练和样本外回测摘要，不重新实现核心回测。
- 支持训练区间或测试区间失败，不让页面崩溃。
- 支持训练为正收益、样本外为负收益时标记 High 风险。
- 支持收益明显衰减、样本外回撤恶化、样本外交易次数不足提示。
- dashboard 新增“样本外测试”tab，位于“策略稳定性”之后、“单股分析”之前。
- 支持选择 market、watchlist、strategy preset、initial_cash、train_ratio 和 min_test_trades。
- 展示过拟合风险、训练/样本外收益、收益衰减、训练/样本外最大回撤、回撤恶化和样本外交易数。
- 展示训练/样本外对比表、检查表、收益柱状图、回撤柱状图和最终资产柱状图。
- 支持下载 out_of_sample_report.json、out_of_sample_periods.csv 和 out_of_sample_checks.csv。
- 所有输出均标注“仅供投资研究，不构成投资建议，不代表未来收益。”

检查结果：

```text
py_compile: passed
pytest: 258 passed
system_doctor: passed
dashboard: returned 200
hidden/bidi scan: passed, risk_count=0
```

安全边界：

```text
是否改变核心策略逻辑：否
是否改变 allocation/risk 逻辑：否
UI 是否保持简约、美观、大方、实用：是
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.22: strategy stress test center

V1.22 目标：

- 增加“策略压力测试中心”页面。
- 基于当前 watchlist 和策略预设运行已有组合回测，生成基准情景。
- 对基准回测 summary 做轻度 / 中度 / 重度压力情景估算。
- 汇总收益下修、回撤放大、最终资产、估算损失和回撤超限情况。
- 输出 Low / Medium / High 总体压力等级。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/strategies/stress_test.py
tests/test_strategy_stress.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

策略压力测试中心功能说明：

- `build_strategy_stress_report` 只分析已有组合回测 summary，不重新实现核心回测逻辑。
- 默认支持轻度压力、中度压力、重度压力三种情景。
- 支持自定义 return_shock 和 drawdown_multiplier。
- 支持基准回测失败，不让页面崩溃，并标记 High 压力等级。
- 支持收益为负、回撤超过最大可接受回撤、交易次数不足等风险提示。
- dashboard 新增“压力测试”tab，位于“样本外测试”之后、“单股分析”之前。
- 支持选择 market、watchlist、strategy preset、initial_cash、max_acceptable_drawdown 和三档压力参数。
- 展示总体压力等级、基准收益、基准最大回撤、最差情景、最差压力收益、最差压力回撤和最大估算损失。
- 展示情景结果表、压力检查表、收益柱状图、回撤柱状图和最终资产柱状图。
- 支持下载 strategy_stress_report.json、stress_scenarios.csv 和 stress_checks.csv。
- 所有输出均标注“仅供投资研究，不构成投资建议，不代表未来收益。”

检查结果：

```text
py_compile: passed
pytest: 269 passed
system_doctor: passed
dashboard: returned 200
hidden/bidi scan: passed, risk_count=0
```

安全边界：

```text
是否改变核心策略逻辑：否
是否改变 allocation/risk 逻辑：否
UI 是否保持简约、美观、大方、实用：是
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.23: backtest quality score center

V1.23 目标：

- 增加“回测质量评分中心”页面。
- 基于当前 watchlist 和策略预设运行已有组合回测。
- 可选纳入策略稳定性、样本外测试和压力测试结果。
- 汇总收益质量、回撤质量、稳定性质量、样本外质量、压力测试质量和数据质量风险。
- 输出 0-100 综合质量分和 Excellent / Good / Watch / Weak 质量等级。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/strategies/quality_score.py
tests/test_quality_score.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

回测质量评分中心功能说明：

- `build_backtest_quality_score` 只汇总已有研究 summary，不重新实现核心回测逻辑。
- 支持缺少 stability / out_of_sample / stress 输入时继续生成报告。
- 缺少可选输入会降低 data_quality_score 并输出 warnings。
- 支持 total_return 为负、max_drawdown 较大、overfit_risk_level High、overall_stress_level High 时降低对应分项。
- dashboard 新增“质量评分”tab，位于“压力测试”之后、“单股分析”之前。
- 支持选择 market、watchlist、strategy preset、initial_cash 和是否纳入稳定性 / 样本外 / 压力测试评分。
- 展示综合质量分、质量等级、收益质量分、回撤质量分、稳定性质量分、样本外质量分、压力测试质量分和数据质量分。
- 展示分项评分表、质量检查表和分项评分柱状图。
- 支持下载 backtest_quality_score_report.json、quality_score_breakdown.csv 和 quality_score_checks.csv。
- 所有输出均标注“仅供投资研究，不构成投资建议，不代表未来收益。”

检查结果：

```text
py_compile: passed
pytest: 279 passed
system_doctor: passed
dashboard: returned 200
hidden/bidi scan: passed, risk_count=0
```

安全边界：

```text
是否改变核心策略逻辑：否
是否改变 allocation/risk 逻辑：否
UI 是否保持简约、美观、大方、实用：是
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.24: strategy research report center

V1.24 目标：

- 增加“策略研究报告中心”页面。
- 汇总组合回测、策略稳定性、样本外测试、压力测试、风险控制和质量评分结果。
- 输出 Positive / Neutral / Cautious 研究视图。
- 生成 dashboard 预览和 Markdown 报告。
- 支持 JSON / Markdown / CSV 下载。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/reports/strategy_research_report.py
tests/test_strategy_research_report.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

策略研究报告中心功能说明：

- `build_strategy_research_report` 只汇总已有研究结果，不重新实现核心回测逻辑。
- `strategy_report_to_markdown` 将研究报告渲染为 Markdown 文本。
- 支持缺少 stability / out_of_sample / stress / risk 输入时继续生成报告。
- 支持根据质量等级、样本外风险和压力测试等级生成 Positive / Neutral / Cautious 研究视图。
- dashboard 新增“研究报告”tab，位于“质量评分”之后、“单股分析”之前。
- 支持选择 market、watchlist、strategy preset、initial_cash 和是否纳入稳定性 / 样本外 / 压力测试 / 风险控制。
- 展示研究结论、综合质量分、质量等级、总收益、最大回撤、样本外风险、压力等级和数据质量分。
- 展示主要风险和 Markdown 报告预览。
- 支持下载 strategy_research_report.json、strategy_research_report.md 和 strategy_research_warnings.csv。
- 所有输出均标注“仅供投资研究，不构成投资建议，不代表未来收益。”

检查结果：

```text
py_compile: passed
pytest: 288 passed
system_doctor: passed
dashboard: returned 200
hidden/bidi scan: passed, risk_count=0
```

安全边界：

```text
是否改变核心策略逻辑：否
是否改变 allocation/risk 逻辑：否
UI 是否保持简约、美观、大方、实用：是
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.25: strategy report archive center

V1.25 目标：

- 增强“研究报告”页面，增加本地策略研究报告归档能力。
- 支持保存策略研究报告 JSON。
- 支持保存 Markdown 报告。
- 支持历史报告列表、加载历史报告、删除历史报告和导出报告列表 CSV。
- 所有文件操作限定在 `reports/strategy_research_reports/`。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
reports/strategy_research_reports/.gitkeep
src/reports/strategy_report_archive.py
tests/test_strategy_report_archive.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

策略研究报告归档中心功能说明：

- `save_strategy_research_report` 保存 JSON 报告，可选保存 Markdown 报告。
- `list_strategy_research_reports` 返回历史报告摘要列表，并跳过损坏 JSON。
- `load_strategy_research_report` 只能通过安全 report_id 加载归档目录内 JSON。
- `delete_strategy_research_report` 只能删除归档目录内对应 JSON / Markdown 文件。
- `export_strategy_report_summary_csv` 导出报告摘要 CSV bytes。
- dashboard “研究报告”tab 新增保存当前报告、历史报告列表、加载历史报告、删除历史报告和报告列表 CSV 下载。
- 历史报告列表展示 report_id、saved_at、strategy_name、research_view、quality_score、quality_level 和 symbol_count。
- 加载历史报告后展示研究结论、策略名称、质量分、质量等级、主要风险和 Markdown 预览。
- 所有输出均标注“仅供投资研究，不构成投资建议，不代表未来收益。”

文件保存目录：

```text
reports/strategy_research_reports/
```

检查结果：

```text
py_compile: passed
pytest: 299 passed
system_doctor: passed
dashboard: returned 200
hidden/bidi scan: passed, risk_count=0
```

安全边界：

```text
是否防路径穿越：是
是否改变核心策略逻辑：否
是否改变 allocation/risk 逻辑：否
UI 是否保持简约、美观、大方、实用：是
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.26: strategy report comparison center

V1.26 目标：

- 增强“研究报告”页面，增加策略报告对比中心。
- 支持从已归档策略研究报告中选择 2-5 份报告。
- 支持对比综合质量分、收益、回撤、样本外风险、压力等级和主要风险。
- 支持识别更值得进一步研究的报告。
- 只读取历史归档报告，不重新计算回测。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/reports/strategy_report_compare.py
tests/test_strategy_report_compare.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

策略报告对比中心功能说明：

- `compare_strategy_research_reports` 接收 2-5 份策略研究报告，字段缺失时不让整体崩溃。
- `compare_strategy_research_reports` 输出 comparison_summary、comparison_rows、risk_rows、best_report_id、best_strategy_name、best_quality_score、lowest_drawdown_report_id、highest_return_report_id、warnings 和 disclaimer。
- best_report_id 优先选择 quality_score 最高的报告；quality_score 相同时优先选择 max_drawdown 更小的报告。
- `export_strategy_report_comparison_csv` 导出 UTF-8-SIG CSV bytes，空输入也保留表头。
- dashboard “研究报告”tab 新增策略报告对比区。
- dashboard 支持选择 2-5 份历史报告，默认选择最新 2 份。
- dashboard 展示最值得进一步研究的报告、策略、最高质量分、最高收益报告、最低回撤报告和 Cautious 报告数量。
- dashboard 展示核心指标对比表、风险对比表、quality_score / total_return / max_drawdown 柱状图。
- dashboard 支持下载 strategy_report_comparison.csv 和 strategy_report_comparison.json。
- 所有输出均标注“仅供投资研究，不构成投资建议，不代表未来收益。”

检查结果：

```text
py_compile: passed
pytest: 311 passed
system_doctor: passed
dashboard: returned 200
hidden/bidi scan: passed, risk_count=0
```

安全边界：

```text
是否改变核心策略逻辑：否
是否只读取已归档报告：是
是否保持研究用途：是
UI 是否保持简约、美观、大方、实用：是
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.27: strategy research trend center

V1.27 目标：

- 增强“研究报告”页面，增加策略研究趋势中心。
- 支持按 strategy_name 聚合历史归档报告。
- 支持观察同一策略在不同生成时间下的质量分、收益、回撤、研究结论、样本外风险和压力等级变化。
- 支持 Improving / Stable / Deteriorating / Insufficient 趋势视图。
- 只读取历史归档报告，不重新计算回测。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/reports/strategy_report_trend.py
tests/test_strategy_report_trend.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

策略研究趋势中心功能说明：

- `build_strategy_report_trend` 接收已归档策略研究报告列表，可按 strategy_name 过滤。
- `build_strategy_report_trend` 支持字段缺失，不让整体崩溃。
- `build_strategy_report_trend` 按 generated_at 或 saved_at 正序排列报告。
- `build_strategy_report_trend` 输出 trend_summary、trend_rows、risk_trend_rows、warnings 和 disclaimer。
- trend_view 根据质量分变化和最大回撤变化输出 Improving / Stable / Deteriorating / Insufficient。
- `export_strategy_report_trend_csv` 导出 UTF-8-SIG CSV bytes，空输入也保留表头。
- dashboard “研究报告”tab 新增策略研究趋势区。
- dashboard 支持从历史报告中选择 strategy_name，默认选择最新报告对应策略。
- dashboard 展示趋势视图、报告数量、最新质量分、质量分变化、最新收益、收益变化、最新回撤和回撤变化。
- dashboard 展示趋势明细表、风险变化表、quality_score / total_return / max_drawdown 时间趋势图。
- dashboard 支持下载 strategy_report_trend.csv 和 strategy_report_trend.json。
- 所有输出均标注“仅供投资研究，不构成投资建议，不代表未来收益。”

检查结果：

```text
py_compile: passed
pytest: 324 passed
system_doctor: passed
dashboard: returned 200
hidden/bidi scan: passed, risk_count=0
```

安全边界：

```text
是否改变核心策略逻辑：否
是否只读取已归档报告：是
是否保持研究用途：是
UI 是否保持简约、美观、大方、实用：是
是否遵守项目 skill / AGENTS 规范：是
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.28: strategy research dashboard

V1.28 目标：

- 增强“研究报告”页面，增加策略研究看板。
- 支持按 strategy_name 汇总历史归档报告。
- 支持查看每个策略最新质量分、研究结论、趋势视图和风险状态。
- 支持 High / Medium / Watch / Low 研究优先级。
- 支持识别高风险策略。
- 只读取历史归档报告，不重新计算回测。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/reports/strategy_research_dashboard.py
tests/test_strategy_research_dashboard.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

策略研究看板功能说明：

- `build_strategy_research_dashboard` 接收已归档策略研究报告列表，按 strategy_name 分组。
- 每个策略使用最新报告作为 latest report。
- 复用 `build_strategy_report_trend` 生成每个策略的趋势视图。
- `build_strategy_research_dashboard` 输出 dashboard_summary、strategy_rows、priority_rows、risk_rows、warnings 和 disclaimer。
- research_priority 支持 High / Medium / Watch / Low。
- `export_strategy_dashboard_csv` 导出 UTF-8-SIG CSV bytes，空输入也保留表头。
- dashboard “研究报告”tab 新增策略研究看板区。
- dashboard 展示策略数量、报告总数、高优先级策略数量、Cautious 策略数量、Improving / Deteriorating 策略数量和最高质量分策略。
- dashboard 展示策略研究状态表、策略优先级区、风险策略区和 latest_quality_score / latest_total_return / latest_max_drawdown 柱状图。
- dashboard 支持下载 strategy_research_dashboard.csv 和 strategy_research_dashboard.json。
- 所有输出均标注“仅供投资研究，不构成投资建议，不代表未来收益。”

检查结果：

```text
py_compile: passed
pytest: 339 passed
system_doctor: passed
dashboard: returned 200
hidden/bidi scan: passed, risk_count=0
```

安全边界：

```text
是否改变核心策略逻辑：否
是否只读取已归档报告：是
是否保持研究用途：是
UI 是否保持简约、美观、大方、实用：是
是否遵守项目 skill / AGENTS 规范：是
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.29: strategy system productization

V1.29 目标：

- 将现有策略研究系统从多模块功能集合收口为统一策略控制中心产品。
- 首页新增 Strategy Control Center 作为默认统一入口。
- 增加本地 TTL 缓存系统。
- 增加 StandardReportV1 标准报告结构。
- 增加系统健康面板。
- 增加轻量目录结构：src/core、src/dashboard、src/cache、src/utils。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/core/__init__.py
src/core/cache_manager.py
src/core/standard_report.py
src/dashboard/.gitkeep
src/cache/.gitkeep
src/utils/.gitkeep
tests/test_v129_system.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

策略系统产品化收口功能说明：

- `StrategyCacheManager` 提供本地内存 TTL 缓存、命中率、过期计数和缓存大小统计。
- `build_cache_key` 使用 strategy + watchlist + preset + params 生成稳定缓存 key。
- `StandardReportV1` 定义统一报告结构，包含 strategy_name、generated_at、backtest_summary、quality_summary、risk_summary、stability_summary、out_of_sample_summary 和 stress_summary。
- `validate_standard_report` 用于检查标准报告必填字段和核心摘要类型。
- 首页新增 Strategy Control Center。
- Strategy Control Center 默认显示首页总览，其他模块通过折叠区按需加载。
- 控制中心包含生成策略研究报告、历史报告管理、策略对比分析、策略趋势分析、策略研究看板、风险总览和系统健康面板。
- 策略研究看板结果通过缓存系统缓存。
- 系统健康面板展示 cache hit rate、report generation time、system_doctor status、pytest status 和 last error logs。

检查结果：

```text
py_compile: passed
pytest: 346 passed
system_doctor: passed
dashboard: returned 200
hidden/bidi scan: passed, risk_count=0
```

安全边界：

```text
是否收口成功：是
UI 是否统一：是
是否可长期扩展：是
是否改变核心策略逻辑：否
是否只读取已归档报告：是
是否保持研究用途：是
UI 是否保持简约、美观、大方、实用：是
是否遵守项目 skill / AGENTS 规范：是
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.30: product stability and polish

V1.30 目标：

- 本版本不新增策略功能，只做产品级优化。
- 统一 Strategy Control Center 的 card-based UI 和 lazy load 模块入口。
- 增强 Cache 2.0。
- 固化 report pipeline。
- 增强 StandardReportV1。
- 增强 safe_render 错误处理。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/core/report_pipeline.py
tests/test_v130_stability.py
```

修改文件：

```text
app/main.py
src/core/cache_manager.py
src/core/standard_report.py
src/ui/layout.py
README.md
REVIEW_PACKAGE.md
```

产品稳定化说明：

- 是否功能新增：否。
- 是否优化版本：是。
- UI 是否统一：是，Strategy Control Center 使用 card-based overview 和折叠 lazy load 模块。
- 是否稳定性提升：是，safe_render 可对 report missing、invalid data、empty data 和 field missing 提供 fallback。
- Cache 2.0 支持 strategy / watchlist / preset 上下文变化自动失效。
- Cache 2.0 支持 report / dashboard / compare / trend 命名缓存入口。
- `generate_full_strategy_report` 固化 report generation、quality scoring、stress scoring、StandardReportV1 和 archive save 流程。
- StandardReportV1 新增 confidence_level、data_freshness_score 和 stability_index。
- 不改变核心策略逻辑，不重新定义交易规则。

检查结果：

```text
py_compile: passed
pytest: 353 passed
system_doctor: passed
dashboard: returned 200
hidden/bidi scan: passed, risk_count=0
```

安全边界：

```text
是否功能新增：否
是否优化版本：是
UI 是否统一：是
是否稳定性提升：是
是否改变核心策略逻辑：否
是否保持研究用途：是
是否连接真实券商：否
是否自动下单：否
是否生成真实交易指令：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.17: strategy comparison center

V1.17 目标：

- 增加“策略对比”页面。
- 支持多个本地策略预设批量运行组合回测。
- 支持对比收益、回撤、交易次数和最终资产。
- 支持净值曲线对比和结果导出。
- 不改变已有核心策略逻辑，只调用策略预设和组合回测模块。

新增文件：

```text
src/strategies/comparison.py
tests/test_strategy_comparison.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

策略对比中心功能说明：

- dashboard 新增“策略对比”tab，位于“策略实验室”和“单股分析”之间。
- 用户可以选择多个本地策略预设，并设置初始资金。
- 系统会对当前 market 和当前 watchlist 批量运行组合回测。
- 成功策略会进入 `results` 和 ranking 表。
- 失败策略会进入 `failed_presets`，不会导致整个对比页面崩溃。
- ranking 表包含 `preset_name`、`total_return`、`annualized_return`、`max_drawdown`、`number_of_trades`、`final_portfolio_value`。
- 页面展示成功策略数、失败策略数、最优总收益策略、最低回撤策略和最终资产最高策略。
- 支持导出 ranking CSV、单个策略 trades CSV 和对比结果 JSON。
- V1.17 相关文件已按 UTF-8 + LF 保存，并清理 hidden/bidi/zero-width/control characters。
- V1.17 文件已再次刷新，用于确认 GitHub PR 页面重新渲染为干净文本。
- V1.17 raw 文件已再次强制刷新，用于确认远程 raw 是真实多行文本。

检查结果：

```text
py_compile: passed
pytest: 220 passed
system_doctor: passed
dashboard: passed
```

安全边界：

```text
是否改变核心策略逻辑：否
UI 是否保持简约、美观、大方、实用：是
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.15: dashboard home overview

V1.15 目标：

- 增加首页 / 总览工作台。
- 用户打开 dashboard 后可以先看到系统状态、市场趋势概览、自选股概览、模拟账户概览、最近 workflow 和最近报告。
- 页面风格保持简约、美观、大方、实用。
- 不新增复杂业务功能。
- 不改变策略核心逻辑。

新增文件：

```text
src/ui/home.py
tests/test_home_summary.py
```

修改文件：

```text
app/main.py
src/ui/layout.py
README.md
REVIEW_PACKAGE.md
```

首页功能说明：

- 新增“首页”tab，并放在 dashboard tab 顺序第一位。
- 首页显示当前市场、watchlist、股票数量、系统健康状态、Strong trend、Watchlist、Weak 和模拟总资产。
- 首页显示平均趋势评分、Top 5 趋势股票和风险观察股票。
- 首页显示模拟账户现金、持仓市值、总资产和浮动盈亏。
- 首页显示最近 workflow 运行记录。
- 首页显示最近日报或回测报告。
- 首页提供常用功能入口说明。

UI 优化说明：

- 新增 `build_home_summary` 纯逻辑 helper，方便测试和复用。
- `src/ui/layout.py` 增加轻量指标行、空状态和紧凑表格 helper。
- 首页优先使用 Streamlit 原生组件，不新增 UI 依赖。

策略逻辑：

```text
是否改变策略逻辑：否
```

检查结果：

```text
py_compile: passed
pytest: 179 passed
system_doctor: passed
dashboard: passed
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## 最新格式修复说明

之前担心 GitHub raw 文件显示为一整行，导致 Python 代码不可运行。

当前已经完成以下修复和验证：

1. 强制把所有指定 `.py` 文件重新写成 UTF-8 + LF 多行格式。
2. 强制把 `requirements.txt`、`.gitattributes`、`.gitignore`、`README.md` 写成 LF 多行格式。
3. 新增 `.gitattributes`，固定文本文件换行：

```text
*.md text eol=lf
*.py text eol=lf
*.txt text eol=lf
.gitignore text eol=lf
```

4. 远程 GitHub raw 链接已经检查，不再是 `Total lines: 1`。

raw 检查结果：

```text
app/main.py lines=83
requirements.txt lines=7
.gitattributes lines=4
src/backtest/simple_backtest.py lines=70
simple_backtest bad multiline string=False
```

请使用这种 raw 路径检查分支，因为分支名里有 `/`：

```text
https://raw.githubusercontent.com/yvonnesun1992-lang/shandong/refs/heads/codex/v1-quant-system/app/main.py
https://raw.githubusercontent.com/yvonnesun1992-lang/shandong/refs/heads/codex/v1-quant-system/requirements.txt
https://raw.githubusercontent.com/yvonnesun1992-lang/shandong/refs/heads/codex/v1-quant-system/.gitattributes
```

## 项目结构

```text
shandong/
├── app/
│   └── main.py
├── data/
│   ├── .gitkeep
│   └── README.md
├── notebooks/
│   └── README.md
├── src/
│   ├── __init__.py
│   ├── backtest/
│   │   ├── __init__.py
│   │   └── simple_backtest.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── cn_data.py
│   │   └── us_data.py
│   ├── indicators/
│   │   ├── __init__.py
│   │   └── technical.py
│   ├── reports/
│   │   ├── __init__.py
│   │   └── daily_report.py
│   ├── risk/
│   │   ├── __init__.py
│   │   └── position.py
│   └── strategies/
│       ├── __init__.py
│       └── trend_score.py
├── tests/
│   ├── test_backtest.py
│   ├── test_indicators.py
│   └── test_trend_score.py
├── .gitignore
├── AGENTS.md
├── README.md
├── REVIEW_PACKAGE.md
└── requirements.txt
```

## requirements.txt

```text
pandas>=2.2
numpy>=1.26
matplotlib>=3.8
yfinance>=0.2
akshare>=1.14
streamlit>=1.36
pytest>=8.0
```

## 核心代码摘要

### app/main.py

Streamlit dashboard。

功能：

- 选择市场：`美股` 或 `A股`
- 编辑股票池
- 显示趋势评分排名
- 查看单只股票的收盘价、MA20、MA60、MA120、RSI14
- 运行单只股票简单回测

修复点：

- 单只股票图表区域加了 `try/except`
- 回测区域加了 `try/except`
- 如果 yfinance 或 akshare 数据源失败，页面显示错误提示，不让整个 dashboard 崩溃

### src/data/us_data.py

美股数据模块。

功能：

- 使用 `yfinance.download`
- 输入美股代码，例如 `NVDA`
- 输出标准 OHLCV：
  - `date`
  - `open`
  - `high`
  - `low`
  - `close`
  - `volume`

### src/data/cn_data.py

A股数据模块。

功能：

- 使用 `akshare.stock_zh_a_hist`
- 输入 A股代码，例如 `300308`
- 使用前复权：`adjust="qfq"`
- 输出标准 OHLCV：
  - `date`
  - `open`
  - `high`
  - `low`
  - `close`
  - `volume`

### src/indicators/technical.py

技术指标模块。

功能：

- `moving_average(series, window)`
- `rsi(series, window=14)`
- `add_technical_indicators(data)`

添加的指标：

- `ma20`
- `ma60`
- `ma120`
- `rsi14`
- `volume_ma20`

### src/strategies/trend_score.py

趋势评分策略。

默认股票池：

- 美股：`NVDA`, `AMD`, `PLTR`, `TSLA`, `MSFT`, `GOOGL`, `META`, `AVGO`, `CORZ`
- A股：`300308`, `300502`, `601138`, `002371`, `603986`, `000977`, `002463`, `300476`, `688256`

评分逻辑：

- 收盘价高于 MA20：+15
- 收盘价高于 MA60：+20
- 收盘价高于 MA120：+20
- MA20 高于 MA60：+15
- MA60 高于 MA120：+15
- RSI 在 50 到 75：+10
- 成交量高于成交量 MA20：+5

状态：

- 80 到 100：`Strong trend`
- 60 到 79：`Watchlist`
- 40 到 59：`Neutral`
- 40 以下：`Weak`

### src/backtest/simple_backtest.py

简单单只股票回测模块。

买入条件：

- 趋势分数 `>= 80`

卖出条件：

- 趋势分数 `< 60`
- 或收盘价跌破 MA60

输出：

- `total_return`
- `annualized_return`
- `max_drawdown`
- `win_rate`
- `number_of_trades`
- `final_portfolio_value`

重要修复：

- 原来买入时使用全部现金。
- 现在 V1 最多只使用 `15%` 初始资金买入单只股票。
- 这样避免了单只股票满仓，符合风险控制方向。
- 错误字符串已保持单行，不存在跨行未闭合字符串：

```python
raise ValueError("Not enough data for backtest. Need at least 120 rows.")
```

注意：

- V1 回测不包含手续费。
- V1 回测不包含滑点。
- V1 回测不处理涨跌停、停牌、分红、真实成交限制。

### src/risk/position.py

风险控制模块。

功能：

- `max_position_value(total_capital, max_position_pct=0.15)`
- `position_size_by_risk(total_capital, entry_price, stop_price, risk_pct=0.02)`
- `suggested_position_size(...)`

当前回测 V1 先直接使用 15% 初始资金上限，后续再逐步接入完整 risk 模块。

### src/reports/daily_report.py

报告模块。

功能：

- 输入多只股票的数据
- 输出按趋势分数排序的表格

## 测试结果

运行命令：

```bash
python -m pytest
```

结果：

```text
collected 7 items

tests/test_backtest.py .
tests/test_indicators.py ...
tests/test_trend_score.py ...

7 passed
```

## 最终本地检查结果

已运行：

```bash
git add --renormalize .
git diff --check
python -m py_compile app/main.py src/data/us_data.py src/data/cn_data.py src/indicators/technical.py src/strategies/trend_score.py src/backtest/simple_backtest.py src/risk/position.py src/reports/daily_report.py
python -m pytest
```

结果：

```text
git diff --check: passed
py_compile: passed
pytest: 7 passed
```

## Python 编译检查

运行命令：

```bash
python -m py_compile app/main.py src/data/us_data.py src/data/cn_data.py src/indicators/technical.py src/strategies/trend_score.py src/backtest/simple_backtest.py src/risk/position.py src/reports/daily_report.py
```

结果：

```text
passed
```

没有发现 `SyntaxError`。

## 最终远程 Raw 检查结果

检查命令使用 `curl` 直接读取 GitHub raw，不使用本地文件。

结果：

```text
app/main.py lines=83
first line='from __future__ import annotations'

requirements.txt lines=7
first line='pandas>=2.2'

.gitattributes lines=4
first line='*.md text eol=lf'

src/backtest/simple_backtest.py lines=70
first line='from __future__ import annotations'
bad multiline string=False
```

这些结果满足：

1. `app/main.py lines > 1`
2. `requirements.txt lines >= 7`
3. `.gitattributes lines >= 4`
4. `src/backtest/simple_backtest.py lines > 1`
5. `simple_backtest.py` 不存在跨行未闭合字符串

## Streamlit 空股票池保护

`app/main.py` 已经增加空股票池保护：

```python
if not symbols:
    st.warning("股票池为空，请在左侧输入至少一个股票代码。")
    st.stop()
```

## Dashboard 检查

运行命令：

```bash
streamlit run app/main.py
```

本地检查：

```text
http://localhost:8501 返回 200
```

## 已知限制

1. V1 数据依赖外部数据源，`yfinance` 或 `akshare` 网络失败时可能无法获取行情。
2. V1 回测是单只股票简单回测，不是完整投资组合回测。
3. V1 没有手续费、滑点、停牌、涨跌停、分红处理。
4. V1 没有交易日历和市场状态判断。
5. V1 dashboard 主要用于学习和查看结果，不是生产级投研系统。

## 请重点帮我检查的问题

1. GitHub raw 文件是否确实已经是多行，不是 `Total lines: 1`。
2. `app/main.py` 是否可以正常运行，空股票池保护是否合理。
3. 回测中 15% 仓位限制是否写得合理。
4. RSI 计算有没有明显问题。
5. A股和美股 OHLCV 标准化是否容易出错。
6. Streamlit 的错误处理是否足够避免页面崩溃。
7. 测试是否覆盖了最重要的计算。
8. 是否还有任何真实交易或券商连接风险。
9. README 是否已经把风险边界说清楚。
10. 这个 PR 是否可以 merge。

## 给 ChatGPT 的一句话请求

请帮我审查 PR #1，重点确认 GitHub raw 文件已经是正常多行代码、项目可安装可测试可运行、没有真实交易或券商连接风险。如果仍看到 `Total lines: 1`，请不要建议 merge。

## 最终状态

- 已 push 到 PR #1 的 `codex/v1-quant-system` 分支。
- 已确认没有 merge PR。
- 未发现真实交易、券商连接、自动下单、API key、secret、password 风险。
- 建议人工 reviewer 继续审查业务逻辑和可维护性；如 reviewer 也确认 raw 多行、测试通过、风险边界清楚，可以再考虑 merge。

## V1.1: sample data fallback and caching

V1.1 目标：

- 提高数据源稳定性。
- 当 `yfinance` 或 `akshare` 失败时，自动使用本地示例数据。
- 保证无网络或数据源失败时，dashboard 仍可以演示趋势评分、图表和回测。

新增文件：

```text
data/sample/us_NVDA.csv
data/sample/cn_300308.csv
src/data/sample_data.py
tests/test_sample_data.py
```

修改文件：

```text
app/main.py
src/data/us_data.py
src/data/cn_data.py
README.md
REVIEW_PACKAGE.md
```

实现内容：

- 示例 CSV 使用标准 OHLCV 字段：`date,open,high,low,close,volume`。
- 每个示例 CSV 有 180 行，日期递增，成交量为正数。
- `load_sample_ohlcv(market, symbol)` 支持：
  - `us + NVDA`
  - `cn + 300308`
- 美股数据优先走 `yfinance`，失败后 fallback 到 `data/sample/us_NVDA.csv`。
- A股数据优先走 `akshare`，失败后 fallback 到 `data/sample/cn_300308.csv`。
- fallback 数据通过 `DataFrame.attrs["is_sample_data"] = True` 标记。
- dashboard 使用 `st.cache_data(ttl=3600)` 缓存数据请求。
- dashboard 使用示例数据时显示 warning：

```text
当前真实数据源获取失败，正在使用本地示例数据。示例数据仅用于功能演示，不代表真实行情，不构成投资建议。
```

检查结果：

```text
py_compile: passed
pytest: 13 passed
dashboard: passed
```

py_compile 命令：

```bash
python -m py_compile app/main.py src/data/us_data.py src/data/cn_data.py src/data/sample_data.py src/indicators/technical.py src/strategies/trend_score.py src/backtest/simple_backtest.py src/risk/position.py src/reports/daily_report.py
```

pytest 结果：

```text
collected 13 items

tests/test_backtest.py .
tests/test_indicators.py ...
tests/test_sample_data.py ......
tests/test_trend_score.py ...

13 passed
```

dashboard 本地验证：

```text
http://localhost:8502 返回 200
趋势评分页：可显示示例数据评分和示例数据 warning
单只股票页：可显示 close、MA20、MA60、MA120、RSI14 图表
简单回测页：可使用示例数据跑通并显示回测结果
```

安全边界：

```text
是否使用真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.14: dashboard UI polish

V1.14 目标：

- 优化 Streamlit dashboard 的整体页面结构和视觉层级。
- 统一标题、说明、风险提示、状态展示和指标卡片。
- 增加轻量 UI helper，减少重复格式化逻辑。
- 不新增复杂业务功能。
- 不改变策略核心逻辑。

新增文件：

```text
src/ui/__init__.py
src/ui/layout.py
tests/test_ui_layout.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

UI 优化说明：

- 页面标题改为 `Shandong Quant Research`。
- 页面顶部增加英文副标题和统一研究风险提示。
- sidebar 增加研究配置分组、当前股票数量和系统状态入口说明。
- tabs 顺序优化为市场总览、单股分析、单股回测、组合回测、模拟交易、每日流程、报告、数据质量、运行记录、系统设置、系统健康和说明。
- 每个核心 tab 增加简短页面说明。
- 市场总览增加趋势评分数量、Strong trend、Watchlist 和 Weak 指标。
- 单股回测增加总收益、年化收益、最大回撤和最终资金指标卡片。
- 组合回测收益指标统一格式化。
- 系统健康状态使用统一状态文案。

策略逻辑：

```text
是否改变策略逻辑：否
```

检查结果：

```text
py_compile: passed
pytest: 174 passed
system_doctor: passed
dashboard: passed
hidden/bidi unicode cleanup: passed
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.13: local launcher and quick start guide

V1.13 目标：

- 增加本地一键启动能力。
- 增加启动前自检脚本。
- 增加 Windows bat / PowerShell 启动入口。
- 增加新手 Quick Start 文档。
- 启动失败时给出清晰错误提示和下一步建议。

新增文件：

```text
scripts/system_doctor.py
scripts/start_dashboard.py
start_shandong.bat
start_shandong.ps1
docs/QUICK_START.md
tests/test_system_doctor.py
tests/test_launcher_scripts.py
```

修改文件：

```text
README.md
REVIEW_PACKAGE.md
```

一键启动功能说明：

- `scripts/start_dashboard.py` 会先运行启动前检查。
- 如果存在阻塞错误，会提示安装依赖和运行测试，不直接崩溃。
- 检查通过后启动 `python -m streamlit run app/main.py`。
- `start_shandong.bat` 和 `start_shandong.ps1` 会优先使用 `.venv\Scripts\python.exe`。

system_doctor 功能说明：

- 检查 Python 版本。
- 检查 pandas、numpy、matplotlib、streamlit、yfinance、akshare、pytest 是否可 import。
- 检查 config、sample data、cache、reports 等关键目录。
- 检查 settings、watchlists、paper portfolio 和示例数据文件。
- 调用系统健康检查中心。
- 输出 OK / WARNING / ERROR 和下一步建议。

检查结果：

```text
py_compile: passed
pytest: 170 passed
system_doctor: passed
dashboard: passed
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.12: system health check center

V1.12 目标：

- 增加本地系统健康检查中心。
- 检查配置、缓存、报告、示例数据、workflow 日志和安全边界。
- dashboard 增加“系统健康”页面。
- 支持导出健康检查 JSON / CSV。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
src/system/__init__.py
src/system/health_check.py
tests/test_system_health_check.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

系统健康检查功能说明：

- `run_system_health_check` 汇总所有检查并返回 overall_status、checks、ok_count、warning_count、error_count 和 generated_at。
- `check_required_directories` 检查 config、sample、cache、reports 等关键目录。
- `check_required_files` 检查 settings、watchlists、paper portfolio 和示例 CSV。
- `check_settings_health` 复用 settings 管理模块验证配置。
- `check_watchlist_health` 检查默认 watchlist 和空列表。
- `check_sample_data_health` 复用 OHLCV 数据质量检查。
- `check_cache_health` 检查本地行情缓存目录和损坏 CSV。
- `check_reports_health` 检查报告目录和损坏 JSON。
- `check_workflow_logs_health` 检查 workflow 运行日志。
- `check_security_boundary` 扫描运行代码中的真实券商连接、自动下单、密钥保存和 AI API 风险。
- 单项检查失败时不会让整体 health check 崩溃，会记录为 error。

dashboard 更新：

- 新增“系统健康”tab。
- 支持点击“运行系统健康检查”。
- 显示 overall_status、OK / Warning / Error 数量。
- 用表格展示每个检查项的 name、status、message。
- 对 error / warning / ok 项分别显示状态提示。
- 支持下载健康检查 JSON。
- 支持下载健康检查 CSV。

检查结果：

```text
py_compile: passed
pytest: 155 passed
dashboard: passed
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.11: settings center and configuration management

V1.11 目标：

- 增加本地系统设置文件。
- 增加 settings 管理模块。
- dashboard 增加“系统设置”页面。
- 轻量集成默认市场、缓存启用状态、缓存 freshness 天数和模拟账户重置初始资金。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
config/settings.json
src/config/__init__.py
src/config/settings.py
tests/test_settings.py
```

修改文件：

```text
app/main.py
src/data/data_quality.py
README.md
REVIEW_PACKAGE.md
```

系统设置中心功能说明：

- `load_settings` 会在 `config/settings.json` 不存在时创建默认配置。
- `save_settings` 保存经过校验的配置。
- `reset_settings` 恢复默认配置。
- `validate_settings` 校验 cache、paper_trading、dashboard 和 workflow 的关键配置。
- `get_setting` 和 `update_setting` 提供简单读写接口。
- 路径只允许 `config/settings.json`，拒绝路径穿越和其他文件名。
- 设置文件拒绝 API key、secret、password、token 等敏感字段。

dashboard 更新：

- 新增“系统设置”tab。
- 显示当前 settings JSON。
- 支持修改 `cache.enabled`、`cache.max_age_days`、`paper_trading.initial_cash`、`dashboard.default_market`、`dashboard.show_disclaimer` 和 `workflow.min_success_symbols`。
- 支持保存设置。
- 支持勾选确认后重置为默认设置。
- 设置读取失败时显示错误，并使用本次运行的默认值，不让 dashboard 崩溃。

检查结果：

```text
py_compile: passed
pytest: 143 passed
dashboard: passed
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.10: price cache and data quality checks

V1.10 目标：

- 增加本地行情缓存，减少对 yfinance / akshare 的重复请求。
- 增加数据质量检查，识别缺字段、数据不足、日期异常、价格异常、缺失值和数据过旧。
- dashboard 增加“数据缓存与质量”页面。
- 每日 workflow 记录每只股票的数据来源。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
data/cache/.gitkeep
src/data/price_cache.py
src/data/data_quality.py
tests/test_price_cache.py
tests/test_data_quality.py
```

修改文件：

```text
app/main.py
src/data/us_data.py
src/data/cn_data.py
src/workflows/daily_workflow.py
tests/test_daily_workflow.py
tests/test_dashboard_helpers.py
README.md
REVIEW_PACKAGE.md
```

行情缓存功能说明：

- 缓存文件使用 CSV，保存到 `data/cache/`。
- 缓存字段固定为 `date, open, high, low, close, volume`。
- `get_us_ohlcv` 和 `get_cn_ohlcv` 默认优先读取本地缓存。
- 如果没有缓存或用户刷新缓存，则尝试真实数据源。
- 真实数据成功后会写入缓存。
- 真实数据失败时继续使用本地 sample fallback。
- 返回的 DataFrame 使用 `attrs["data_source"]` 标记 `cache` / `remote` / `sample`。

数据质量检查功能说明：

- `validate_ohlcv_data` 检查字段、行数、日期、价格、成交量和缺失值。
- `check_data_freshness` 检查最近数据是否过旧。
- `build_data_quality_report` 输出统一质量状态、warnings、errors、起止日期和最新收盘价。

dashboard 更新：

- 新增“数据缓存与质量”tab。
- 显示当前缓存列表。
- 支持更新当前 watchlist 缓存。
- 显示每只股票的数据源和质量状态。
- 支持勾选确认后删除单个缓存文件。
- 显示行情缓存风险提示。

检查结果：

```text
py_compile: passed
pytest: 128 passed
dashboard: passed
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.2: dashboard polish and CSV export

V1.2 目标：

- 把 Streamlit dashboard 优化成更适合演示的产品化界面。
- 保持核心策略不变。
- 继续禁止真实券商连接、自动下单、实盘交易和密钥保存。

新增文件：

```text
tests/test_dashboard_helpers.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

实现内容：

- 页面顶部增加全局免责声明。
- 趋势评分页、单只股票分析页、简单回测页显示数据源状态。
- 使用示例数据时显示 warning：

```text
当前真实数据源获取失败，正在使用本地示例数据。示例数据仅用于功能演示，不代表真实行情，不构成投资建议。
```

- 增加“趋势评分规则说明”可展开区域。
- 趋势评分排名支持导出 `trend_scores.csv`。
- sidebar 增加缓存说明：行情数据默认缓存 1 小时。
- 页面 tabs 调整为：
  - 趋势评分
  - 单只股票分析
  - 简单回测
  - 说明与风险提示
- 新增测试覆盖：
  - 趋势评分表可以转换为 CSV。
  - sample attrs 可以识别为示例数据。
  - 示例数据可以生成趋势评分结果。

检查结果：

```text
py_compile: passed
pytest: 16 passed
dashboard: passed
```

dashboard 本地验证：

```text
http://localhost:8503 返回 200
页面顶部免责声明：已显示
趋势评分页：已显示评分规则、数据源状态和 CSV 下载按钮
单只股票分析页：已显示数据源状态、收盘价/均线/RSI 图表
简单回测页：已显示数据源状态并可跑出回测结果
说明与风险提示页：已显示缓存说明和安全边界
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.3: local watchlist management

V1.3 目标：

- 让用户可以在 dashboard 中保存、加载、编辑自己的本地自选股列表。
- 避免每次运行 dashboard 都要手动输入股票池。
- 保持研究工具边界，不连接券商、不自动下单、不保存密钥。

新增文件：

```text
config/watchlists.json
src/data/watchlist_manager.py
tests/test_watchlist_manager.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
tests/test_dashboard_helpers.py
```

watchlist 功能说明：

- 默认配置文件：`config/watchlists.json`。
- 默认列表：
  - `us_default`
  - `cn_default`
- dashboard sidebar 支持：
  - 选择 watchlist
  - 编辑股票代码
  - 输入新 watchlist 名称
  - 保存自选股
- 股票代码会去空格、过滤空字符串、去重。
- 美股代码会转大写。
- A股数字代码会保留为 6 位字符串。
- watchlist 名称只允许字母、数字、下划线和短横线。
- 非法名称会被拒绝，不会被当作文件路径使用。
- 配置文件只保存股票代码列表，不保存账户、密码、API key 或券商凭证。

检查结果：

```text
py_compile: passed
pytest: 32 passed
dashboard: passed
```

dashboard 本地验证：

```text
http://localhost:8504 返回 200
sidebar：已显示自选股管理、watchlist 选择、新 watchlist 名称、股票池编辑框、保存自选股按钮
趋势评分页：可继续显示趋势评分和 CSV 下载按钮
数据源 fallback warning：可正常显示
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.4: local paper trading portfolio

V1.4 目标：

- 增加一个本地模拟交易 / 纸上交易基础版。
- 用户可以用虚拟资金模拟买入、卖出、查看持仓、查看现金、查看盈亏和交易记录。
- 继续禁止真实券商连接、自动下单、实盘交易和密钥保存。

新增文件：

```text
config/paper_portfolio.json
src/paper_trading/__init__.py
src/paper_trading/portfolio.py
tests/test_paper_portfolio.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

模拟交易功能说明：

- 默认虚拟资金：`100000.0`。
- 本地文件：`config/paper_portfolio.json`。
- 支持虚拟买入：
  - 检查价格大于 0。
  - 检查数量大于 0。
  - 检查现金足够。
  - 更新平均成本。
  - 写入交易记录。
- 支持虚拟卖出：
  - 检查持仓数量足够。
  - 卖完后删除持仓。
  - 写入交易记录。
- dashboard 新增“模拟交易”tab：
  - 显示当前现金、持仓市值、总资产、浮动盈亏、持仓数量。
  - 显示持仓表。
  - 支持手动输入价格和数量进行模拟买卖。
  - 显示最近 20 条交易记录。
  - 支持下载交易记录 CSV。
  - 支持确认后重置模拟账户。
- 交易价格由用户手动输入，不会产生真实订单。
- 文件只保存虚拟资金、持仓和交易记录，不保存真实账户或券商凭证。

检查结果：

```text
py_compile: passed
pytest: 49 passed
dashboard: passed
```

dashboard 本地验证：

```text
http://localhost:8505 返回 200
模拟交易 tab：已显示免责声明
账户概览：已显示当前现金、持仓市值、总资产、浮动盈亏、持仓数量
持仓表：无持仓时显示提示
模拟买入/卖出：表单已显示
交易记录：无记录时显示提示
重置模拟账户：已显示确认 checkbox 和重置按钮
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## Fresh Clone 验证

已按人工 review 要求，从远程仓库重新 clone：

```bash
git clone git@github.com:yvonnesun1992-lang/shandong.git fresh-check
cd fresh-check
git checkout codex/v1-quant-system
python -m py_compile app/main.py src/backtest/simple_backtest.py
python -m pytest
```

结果：

```text
py_compile: passed
pytest: 7 passed
app/main.py lines=83 first='from __future__ import annotations'
src/backtest/simple_backtest.py lines=70 first='from __future__ import annotations'
requirements.txt lines=7 first='pandas>=2.2'
.gitattributes lines=4 first='*.md text eol=lf'
bad multiline string=False
```

## Remote / Branch 排查

按人工 reviewer 要求，未改代码前执行 Git 排查命令。

### git remote -v

```text
origin  git@github.com:yvonnesun1992-lang/shandong.git (fetch)
origin  git@github.com:yvonnesun1992-lang/shandong.git (push)
```

### git branch --show-current

```text
codex/v1-quant-system
```

### git status

```text
On branch codex/v1-quant-system
Your branch is up to date with 'origin/codex/v1-quant-system'.

nothing to commit, working tree clean
```

### git log -5 --oneline

```text
ba7321d Record fresh clone verification
026d9a4 Restore raw Python files to valid multiline format
cbcd5b0 Make raw files visibly multiline
3d13932 Update review package with latest raw check
70c1a84 Force raw files to refresh LF formatting
```

### git rev-parse HEAD

```text
ba7321d193841dd8a9d5beb9580db236ce006af4
```

### git ls-remote origin refs/heads/codex/v1-quant-system

```text
ba7321d193841dd8a9d5beb9580db236ce006af4 refs/heads/codex/v1-quant-system
```

### git diff origin/codex/v1-quant-system..HEAD --stat

```text
No diff.
```

结论：

- 当前分支是 `codex/v1-quant-system`。
- `HEAD` 等于 `origin/codex/v1-quant-system`。
- 最新提交已经 push 到 `yvonnesun1992-lang/shandong` 的 `codex/v1-quant-system` 分支。

## Explicit Push 后的 Raw 检查

执行：

```bash
git push origin HEAD:codex/v1-quant-system
```

push 结果：

```text
ba7321d..934c566 HEAD -> codex/v1-quant-system
```

随后按要求用远程 raw 链接检查：

```text
app/main.py:
83
'from __future__ import annotations\n\nimport pandas as pd\nimport streamlit as st\n\nfrom src.backtest.simple_backtest import run_simple_backtest\nfrom src.data.cn_data import get_cn_ohlcv\nfrom src.data.us_'

requirements.txt:
7
'pandas>=2.2\nnumpy>=1.26\nmatplotlib>=3.8\nyfinance>=0.2\nakshare>=1.14\nstreamlit>=1.36\npytest>=8.0\n'

.gitattributes:
4
'*.md text eol=lf\n*.py text eol=lf\n*.txt text eol=lf\n.gitignore text eol=lf\n'

src/backtest/simple_backtest.py:
70
'from __future__ import annotations\n\nimport pandas as pd\n\nfrom src.strategies.trend_score import add_trend_scores\n\n\ndef calculate_max_drawdown(equity: pd.Series) -> float:\n    """Maximum fall from a previous high point."""\n    running_high = equity.cummax()\n    drawdown = equity / running_high - 1\n  '
bad=False
```

确认：

```text
HEAD=934c5661b2675af0f9e6b1ad6610b9d103e708ca
origin/codex/v1-quant-system=934c5661b2675af0f9e6b1ad6610b9d103e708ca
```

## PR #6 文档 Unicode 安全复查

本次只复查和更新文档，不修改模拟交易业务逻辑。

复查文件：

- README.md
- REVIEW_PACKAGE.md

清理与验证结果：

- 已使用 Python 扫描 RLO、LRO、RLE、LRE、PDF、LRI、RLI、FSI、PDI。
- 已扫描 zero-width space、zero-width joiner、zero-width non-joiner、BOM。
- 已扫描 Unicode category Cf 和异常 control characters。
- 未发现需要删除的隐藏 Unicode、双向文本控制字符或异常控制字符。
- 已确认两个文档按 UTF-8 和 LF 换行保存。
- 未修改 `src/paper_trading/portfolio.py` 业务逻辑。
- 未连接真实券商。
- 未自动下单。
- 未加入 API key、secret、password、token。

验证命令：

```bash
python -m py_compile app/main.py src/data/us_data.py src/data/cn_data.py src/data/sample_data.py src/data/watchlist_manager.py src/paper_trading/portfolio.py src/indicators/technical.py src/strategies/trend_score.py src/backtest/simple_backtest.py src/risk/position.py src/reports/daily_report.py
python -m pytest
```

结果：

```text
py_compile: passed
pytest: 49 passed
```

## PR #6 GitHub Files Hidden Unicode 定位结论

用户反馈 ChatGPT 在 GitHub PR / Files changed 页面仍然看到：

```text
This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below.
```

进一步定位结论：

- 已逐个检查 PR #6 相关文件：
  - README.md
  - REVIEW_PACKAGE.md
  - app/main.py
  - config/paper_portfolio.json
  - src/paper_trading/__init__.py
  - src/paper_trading/portfolio.py
  - tests/test_paper_portfolio.py
- 本地文件扫描未发现 hidden Unicode、bidi、zero-width、BOM、Unicode category Cf 或异常 control characters。
- 远程 raw 文件扫描也未发现上述风险字符。
- GitHub Files changed 页面的 HTML 源码中确实包含 hidden Unicode warning 文案，但它位于 GitHub 自带的 `<template>` 中。
- 该模板会被 GitHub 静态插入到 diff 页面中，不等于某个文件实际触发了警告。
- 实际可见页面检查结果：
  - `hasVisibleHiddenWarning=false`
  - `hasShowHiddenCharacters=false`
- 因此，如果审查工具直接搜索 GitHub HTML 源码，会误判；应以页面实际可见 warning 条、`Show hidden characters` 按钮或远程 raw 字符扫描为准。

最终验证：

```text
py_compile: passed
pytest: 49 passed
真实券商连接: 否
自动下单: 否
API key / secret / password / token: 否
PR merge: 否
```

## V1.5: portfolio backtesting and risk metrics

V1.5 目标：

- 增加组合回测功能。
- 基于当前 watchlist 对多个股票组成的组合做历史研究。
- 增加组合级风险指标。
- 继续禁止真实券商连接、自动下单、实盘交易和密钥保存。

新增文件：

```text
src/backtest/portfolio_backtest.py
src/risk/metrics.py
tests/test_portfolio_backtest.py
tests/test_risk_metrics.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

组合回测功能说明：

- 输入为多个股票的标准 OHLCV 数据。
- 使用现有趋势评分逻辑。
- 趋势分数大于等于买入阈值时进入候选池。
- 趋势分数低于持有阈值，或收盘价跌破 MA60 时卖出。
- 单只股票最大仓位默认 15%。
- 数据不足 120 行的股票会被跳过，并写入 `skipped_symbols`。
- 输出 `equity_curve`、`trades` 和 `summary`。
- `summary` 包含总收益、年化收益、最大回撤、交易次数、最终资产、现金和持仓市值。

dashboard 更新：

- 新增“组合回测”tab。
- 使用当前 watchlist 作为组合股票池。
- 支持设置初始资金、单只股票最大仓位、买入分数阈值和持有分数阈值。
- 展示总收益、年化收益、最大回撤、最终资产、交易次数和跳过股票。
- 展示组合净值曲线和交易记录表。
- 支持导出 `equity_curve.csv` 和 `portfolio_trades.csv`。
- 显示组合回测免责声明。

风险指标：

- `calculate_max_drawdown`
- `calculate_total_return`
- `calculate_annualized_return`

已知限制：

- 不包含手续费。
- 不包含滑点。
- 不处理停牌。
- 不处理涨跌停。
- 不处理分红。
- 不处理真实成交限制。
- 不做杠杆。
- 不做做空。

检查结果：

```text
py_compile: passed
pytest: 59 passed
dashboard: passed
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.6: backtest report center

V1.6 目标：

- 增加本地回测结果保存功能。
- 增加 dashboard 报告中心。
- 用户运行单票回测或组合回测后，可以保存报告并回看历史记录。
- 继续禁止真实券商连接、自动下单、实盘交易和密钥保存。

新增文件：

```text
reports/backtests/.gitkeep
src/reports/backtest_report.py
tests/test_backtest_report.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

回测报告保存功能说明：

- 默认报告目录：`reports/backtests/`。
- 每个报告保存为独立 JSON 文件。
- report_id 自动生成，包含时间戳和随机后缀。
- report_id 只允许字母、数字、下划线和短横线。
- 读取、删除报告时会校验 report_id，防止路径穿越。
- JSON 使用 UTF-8、`indent=2`、`ensure_ascii=False`。
- DataFrame 会转换为 records。
- 日期和 timestamp 会转换为字符串，避免 JSON 序列化失败。
- 如果 JSON 损坏，读取时会抛出清晰 `ValueError`。
- 如果报告不存在，读取或删除时会抛出清晰 `FileNotFoundError`。

报告内容结构：

```text
report_id
created_at
report_type
parameters
summary
equity_curve
trades
```

报告中心功能说明：

- dashboard 新增“报告中心”tab。
- 显示历史报告列表。
- 支持选择一个 report_id 查看详情。
- 展示报告 metadata。
- 展示 summary。
- 如果有 equity_curve，展示净值曲线和表格。
- 如果有 trades，展示交易记录表。
- 支持下载当前报告 JSON。
- 支持下载当前报告 trades CSV。
- 支持下载全部报告 summary CSV。
- 支持勾选确认后删除报告。
- 删除失败会显示 error，不会让 dashboard 崩溃。

单票回测保存：

- 保存 `symbol`、`market`、`initial_cash` 和回测 summary。
- 当前单票 V1 回测函数只返回 summary，因此报告保存为 summary-only。

组合回测保存：

- 保存 `watchlist`、`market`、`initial_cash`、`max_position_pct`、`min_score_to_buy`、`min_score_to_hold`。
- 保存 summary、equity_curve 和 trades。

检查结果：

```text
py_compile: passed
pytest: 72 passed
dashboard: passed
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.7: daily research report center

V1.7 目标：

- 增加每日量化研究报告功能。
- 基于当前 watchlist、趋势评分、数据源状态、模拟持仓和最近回测报告生成本地研究日报。
- dashboard 增加“每日研究报告”页面。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
reports/daily/.gitkeep
src/reports/daily_research_report.py
tests/test_daily_research_report.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

每日研究报告功能说明：

- `generate_daily_report_id` 生成路径安全的日报 ID。
- `build_daily_research_report` 基于已计算的趋势评分表生成日报。
- `daily_report_to_markdown` 将日报转换为可读 Markdown。
- `save_daily_research_report` 将日报保存为本地 JSON。
- `list_daily_research_reports` 返回历史日报摘要表。
- `load_daily_research_report` 读取指定日报。
- `delete_daily_research_report` 删除指定日报。
- `export_daily_report_summary_csv` 导出日报摘要 CSV。

日报内容：

- report_id
- created_at
- market
- watchlist_name
- disclaimer
- market_summary
- top_symbols
- risk_symbols
- data_source_summary
- paper_portfolio_summary
- recent_backtest_summary
- notes

dashboard 更新：

- 新增“每日研究报告”tab。
- 可以生成今日研究报告。
- 可以预览 Markdown。
- 可以保存日报到 `reports/daily/`。
- 可以下载当前日报 JSON。
- 可以下载当前日报 Markdown。
- 可以查看历史日报列表。
- 可以下载历史日报 summary CSV。
- 可以选择历史日报查看详情。
- 可以勾选确认后删除历史日报。

检查结果：

```text
py_compile: passed
pytest: 88 passed
dashboard: passed
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.9: workflow run logs

V1.9 目标：

- 为每日 workflow 增加本地运行日志。
- 每次运行保存 run_id、时间、成功/失败股票、失败原因、report_id 和运行耗时。
- dashboard 增加“运行记录”页面。
- CLI 运行每日 workflow 后也保存日志。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
reports/workflow_runs/.gitkeep
src/workflows/run_log.py
tests/test_workflow_run_log.py
```

修改文件：

```text
app/main.py
scripts/run_daily_workflow.py
src/workflows/daily_workflow.py
tests/test_daily_workflow.py
README.md
REVIEW_PACKAGE.md
```

workflow run log 功能说明：

- `generate_run_id` 生成路径安全的运行 ID。
- `save_workflow_run_log` 将 workflow_result 保存为本地 JSON。
- `list_workflow_run_logs` 返回历史运行记录摘要表。
- `load_workflow_run_log` 读取指定运行记录。
- `delete_workflow_run_log` 删除指定运行记录。
- `export_workflow_run_summary_csv` 导出运行记录摘要 CSV。

运行记录内容：

- run_id
- created_at
- started_at
- finished_at
- elapsed_seconds
- success
- market
- watchlist_name
- total_symbols
- success_count
- failed_count
- success_symbols
- failed_symbols
- report_id
- error_message
- summary

dashboard 更新：

- 每次点击“运行每日研究流程”后自动保存一条 workflow run log。
- 新增“运行记录”tab。
- 显示历史运行记录列表。
- 支持选择 run_id 查看详情。
- 展示 success_symbols、failed_symbols、error_message、report_id 和 summary。
- 支持下载当前运行日志 JSON。
- 支持下载运行记录 summary CSV。
- 支持勾选确认后删除运行记录。

CLI 更新：

- CLI 运行每日 workflow 后自动保存运行日志。
- 打印 run_id、report_id、success_count、failed_count 和 elapsed_seconds。

检查结果：

```text
py_compile: passed
pytest: 110 passed
dashboard: passed
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.8: daily workflow runner

V1.8 目标：

- 增加本地一键每日研究流程。
- 基于当前市场、watchlist 和股票池自动获取行情、计算趋势评分、生成并保存每日研究报告。
- dashboard 增加“每日流程”页面。
- 增加 CLI 脚本，支持本地命令行运行。
- 继续禁止真实券商连接、自动下单、实盘交易、密钥保存和 AI API 调用。

新增文件：

```text
scripts/run_daily_workflow.py
src/workflows/__init__.py
src/workflows/daily_workflow.py
tests/test_daily_workflow.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

每日 workflow 功能说明：

- `run_daily_research_workflow` 接收 market、watchlist_name、symbols 和可注入的数据获取函数。
- 自动清洗股票池，过滤空值并去重。
- 单只股票数据失败时记录到 failed_symbols，不让整个流程崩溃。
- 至少一个股票成功时生成 trend_scores，并保存每日研究报告。
- 全部股票失败时返回失败结果，不保存空报告。
- 返回 report_id、report_path、trend_scores、summary、success_symbols 和 failed_symbols。

dashboard 更新：

- 新增“每日流程”tab。
- 显示当前市场、watchlist 和股票数量。
- 支持点击“运行每日研究流程”。
- 显示成功处理股票数、失败股票列表、report_id 和趋势评分摘要。
- 显示 Top 趋势股票和风险观察股票。
- 支持下载本次生成日报 JSON。
- 支持下载本次趋势评分 CSV。

CLI 更新：

```bash
python scripts/run_daily_workflow.py --market us --watchlist us_default
python scripts/run_daily_workflow.py --market cn --watchlist cn_default
```

检查结果：

```text
py_compile: passed
pytest: 96 passed
dashboard: passed
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否调用 AI API：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```
# V5.41 Local End-to-End Run Verification

V5.41 adds a local end-to-end verification layer for confirming the local-only product path after V5.40.

新增内容：

- `config/v5_local_e2e_config.py`
- `local_e2e_verification/`
- `scripts/run_v541_local_e2e_verification.py`
- `/api/v5/local-e2e/*` endpoints
- `web/frontend/app/v5-local-e2e/page.tsx`
- `docs/V5_LOCAL_E2E_VERIFICATION.md`
- `reports/v5_41_local_e2e_verification_report.md`
- `tests/test_v541_local_e2e_verification.py`

验证范围：

- Local launcher plan verification
- Backend smoke test
- Frontend smoke test
- API smoke test matrix
- Log write/read verification
- Local verification report generation
- Safety boundary verification

安全边界：

- 是否连接真实券商：否
- 是否连接 sandbox API：否
- 是否读取 secret/token/password/API key：否
- 是否读取真实 account/balance/position：否
- 是否提交订单：否
- 是否接真实资金：否
- 是否修改 alpha/factor/strategy：否

检查结果：

```text
py_compile: passed
V5.41 targeted pytest: 4 passed
V5.41 CLI checks: passed, full summary WARNING because node was unavailable in PATH during local environment probe
frontend structure check: passed via bundled Node, V3.9 frontend structure verified
pytest: 880 passed
system_doctor: OK
```

是否建议创建 PR：是

---

# V5.43 Guided Local Setup Wizard

V5.43 adds a guided local setup wizard for non-programmer users who cannot open `http://127.0.0.1:3000`.

新增内容：

- `config/v5_guided_setup_config.py`
- `guided_setup/`
- `scripts/run_v543_guided_setup_wizard.py`
- `/api/v5/guided-setup/*` endpoints
- `web/frontend/app/v5-guided-setup/page.tsx`
- `docs/V5_GUIDED_SETUP.md`
- `reports/v5_43_guided_setup_wizard_report.md`
- `tests/test_v543_guided_setup_wizard.py`

验证范围：

- Setup requirement detector
- Mac / Windows setup steps
- Copy command blocks
- Plain language explanation
- Guided setup wizard orchestrator
- Safety boundary validation
- API endpoints
- Frontend page / navigation / API client helpers

安全边界：

- 是否自动安装依赖：否
- 是否自动访问外部网络：否
- 是否修改 PATH：否
- 是否请求管理员权限：否
- 是否启动长期进程：否
- 是否连接真实券商：否
- 是否连接 sandbox API：否
- 是否读取 secret/token/password/API key：否
- 是否读取真实 account/balance/position：否
- 是否提交订单：否
- 是否接真实资金：否
- 是否修改 alpha/factor/strategy：否

检查结果：

```text
py_compile: passed
V5.43 targeted pytest: 4 passed
V5.43 CLI checks: passed, full summary WARNING because Node.js is unavailable in PATH
frontend structure check: passed via bundled Node, V3.9 frontend structure verified
pytest: 888 passed
system_doctor: OK
```

是否建议创建 PR：是

---

# V5.42 Local Run Doctor & One-Click Fix Guide

V5.42 adds a local run doctor for diagnosing why `http://127.0.0.1:3000` may not open.

新增内容：

- `config/v5_local_run_doctor_config.py`
- `local_run_doctor/`
- `scripts/run_v542_local_run_doctor.py`
- `/api/v5/local-run-doctor/*` endpoints
- `web/frontend/app/v5-local-run-doctor/page.tsx`
- `docs/V5_LOCAL_RUN_DOCTOR.md`
- `reports/v5_42_local_run_doctor_report.md`
- `tests/test_v542_local_run_doctor.py`

验证范围：

- Command availability diagnosis
- Localhost-only port diagnosis
- Backend TestClient diagnosis
- Frontend file/dependency diagnosis
- Browser target diagnosis
- Human-friendly Mac and Windows fix guide
- Local run doctor report generation
- Safety boundary validation

安全边界：

- 是否自动安装依赖：否
- 是否启动长期进程：否
- 是否访问外部网络：否
- 是否连接真实券商：否
- 是否连接 sandbox API：否
- 是否读取 secret/token/password/API key：否
- 是否读取真实 account/balance/position：否
- 是否提交订单：否
- 是否接真实资金：否
- 是否修改 alpha/factor/strategy：否

检查结果：

```text
py_compile: passed
V5.42 targeted pytest: 4 passed
V5.42 CLI checks: passed, full summary WARNING because Node.js is unavailable in PATH and 127.0.0.1:3000 is not running
frontend structure check: passed via bundled Node, V3.9 frontend structure verified
pytest: 884 passed
system_doctor: OK
```

是否建议创建 PR：是

---
