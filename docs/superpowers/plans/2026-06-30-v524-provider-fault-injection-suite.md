# V5.24 Provider Fault Injection Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build V5.24 Provider Sandbox Connector Fault Injection Suite to validate offline connector fault detection, recovery, kill switch simulation, audit consistency, and safety boundaries.

**Architecture:** Follow V5.23's offline namespace pattern with a new `provider_fault_injection/` package. V5.24 consumes only generated local placeholder fault scenarios and returns report/API/frontend evidence without broker, sandbox API, account, order, network, or credential paths.

**Tech Stack:** Python 3.12+, FastAPI TestClient, pytest, existing Next.js frontend files.

## Global Constraints

- Build only V5.24 in this branch.
- Do not implement V5.25, V5.26, V5.27, or V5.28.
- 不接真实 broker.
- 不接 sandbox API.
- 不访问 provider portal.
- 不创建 API key.
- 不导入 broker SDK.
- 不读取真实账户.
- 不读取 sandbox 账户.
- 不下真实订单.
- 不下 sandbox 订单.
- 不接真实资金.
- 不访问外部网络.
- 不保存 raw provider payload.
- 不返回真实 account id / order id / provider endpoint URL.
- 不改 alpha/factor/strategy.

---

### Task 1: Red Tests For V5.24 Contract

**Files:**
- Create: `tests/test_v524_provider_fault_injection.py`

**Interfaces:**
- Produces expected import and behavior contracts for config, fault catalog, injector, runner, validators, kill switch simulation, audit trail, orchestrator, API, CLI, frontend, report, and security scan.

- [x] **Step 1: Write failing tests for V5.24 behavior.**
- [x] **Step 2: Run `./.venv312/bin/python -m pytest tests/test_v524_provider_fault_injection.py -q` and confirm missing V5.24 modules/routes fail.**

### Task 2: Fault Injection Core

**Files:**
- Create: `config/v5_provider_fault_injection_config.py`
- Create: `provider_fault_injection/__init__.py`
- Create: `provider_fault_injection/fault_scenario_catalog.py`
- Create: `provider_fault_injection/fault_injector.py`
- Create: `provider_fault_injection/fault_replay_runner.py`

**Interfaces:**
- Produces `get_fault_injection_mode() -> str`
- Produces `get_fault_injection_provider() -> str`
- Produces `get_fault_injection_status() -> dict`
- Produces `boundary() -> dict`
- Produces `build_fault_scenario_catalog(provider: str) -> dict`
- Produces `inject_fault(provider: str, scenario: str) -> dict`
- Produces `inject_all_faults(provider: str) -> dict`
- Produces `run_fault_scenario(provider: str, scenario: str) -> dict`
- Produces `run_all_fault_scenarios(provider: str) -> dict`

- [x] **Step 1: Implement config and boundary flags with all real paths false.**
- [x] **Step 2: Implement local placeholder fault scenario catalog.**
- [x] **Step 3: Implement fault injector and replay runner using only local placeholders.**

### Task 3: Validators, Kill Switch, Audit, Orchestrator, Report, CLI

**Files:**
- Create: `provider_fault_injection/fault_detection_validator.py`
- Create: `provider_fault_injection/fault_recovery_validator.py`
- Create: `provider_fault_injection/kill_switch_simulation.py`
- Create: `provider_fault_injection/fault_audit_trail.py`
- Create: `provider_fault_injection/fault_safety_validator.py`
- Create: `provider_fault_injection/fault_injection_orchestrator.py`
- Create: `provider_fault_injection/provider_fault_injection_report.py`
- Create: `scripts/run_v524_provider_fault_injection.py`

**Interfaces:**
- Produces `validate_fault_detection(result: dict) -> dict`
- Produces `validate_all_fault_detections(provider: str) -> dict`
- Produces `validate_fault_recovery(result: dict) -> dict`
- Produces `validate_all_fault_recovery(provider: str) -> dict`
- Produces `simulate_kill_switch_trigger(provider: str, scenario: str) -> dict`
- Produces `validate_kill_switch_effect(result: dict) -> dict`
- Produces `build_fault_audit_trail(result: dict) -> dict`
- Produces `build_all_fault_audit_trails(provider: str) -> dict`
- Produces `validate_fault_safety(payload: dict | str) -> dict`
- Produces `build_fault_safety_summary() -> dict`
- Produces `run_fault_injection_suite(provider: str) -> dict`
- Produces `generate_provider_fault_injection_report(provider: str | None = None, scenario: str | None = None, check: str = "all") -> dict`

- [x] **Step 1: Implement validators and kill switch simulation.**
- [x] **Step 2: Implement audit trail, orchestrator, report, and CLI.**
- [x] **Step 3: Run targeted tests and fix failures.**

### Task 4: API, Frontend, Docs, And Security Scan

**Files:**
- Modify: `src/api/v2/server.py`
- Modify: `web/frontend/app/lib/apiClient.ts`
- Modify: `web/frontend/app/components/ProductionShell.tsx`
- Create: `web/frontend/app/v5-provider-fault-injection/page.tsx`
- Modify: `runtime/security_scan.py`
- Modify: `README.md`
- Modify: `REVIEW_PACKAGE.md`
- Create: `docs/V5_PROVIDER_FAULT_INJECTION.md`
- Create: `reports/v5_24_provider_fault_injection_report.md`

**Interfaces:**
- Produces ten `/api/v5/provider-fault-injection/*` endpoints.
- Produces frontend fetch helpers and V5 Fault Injection page.
- Produces V5.24 docs, report, and review package evidence.

- [x] **Step 1: Add API imports, boundary helper, and endpoints.**
- [x] **Step 2: Add frontend client helpers, route page, and navigation item.**
- [x] **Step 3: Add security scan hook and documentation.**

### Task 5: Final Verification And PR

**Files:**
- All V5.24 files.

**Interfaces:**
- Produces clean branch ready for PR review.

- [x] **Step 1: Run V5.24 targeted tests.**
- [x] **Step 2: Run V5.23 + V5.24 regression tests.**
- [x] **Step 3: Run py_compile and CLI checks.**
- [x] **Step 4: Run full pytest and system doctor.**
- [x] **Step 5: Clean generated runtime artifacts and confirm git status.**
- [x] **Step 6: Commit, push, and create PR without merging.**
