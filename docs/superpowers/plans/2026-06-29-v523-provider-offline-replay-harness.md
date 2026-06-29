# V5.23 Provider Offline Replay Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build V5.23 Provider Sandbox Connector Offline Replay Harness to validate mock connector sequencing, lifecycle replay, failure recovery, idempotency, audit consistency, and safety boundaries using local placeholder events only.

**Architecture:** Follow the V5.22 mock-contract pattern with a new `provider_offline_replay/` namespace. V5.23 owns generated local replay catalogs, offline-only loaders/runners/state machines, validators, audit trails, orchestrated summaries, report/CLI/API/frontend surfaces, and security-scan extensions.

**Tech Stack:** Python 3.12+, FastAPI TestClient, pytest, existing Next.js frontend files.

## Global Constraints

- 本阶段只做 offline replay harness.
- 不接真实券商 API.
- 不接 broker sandbox API.
- 不访问券商官网或 portal.
- 不创建真实账户.
- 不创建 sandbox account.
- 不申请 API key.
- 不导入 IBKR / Alpaca / 富途 / 老虎 / 嘉信 / Robinhood SDK.
- 不读取真实账户.
- 不读取 sandbox account.
- 不读取真实余额.
- 不读取真实持仓.
- 不下真实订单.
- 不下 sandbox 订单.
- 不接真实资金.
- 不保存 API key / secret / token / password.
- 不提交 .env.
- 不做 OAuth 登录.
- 不做 production trading.
- 不发送任何外部网络请求.
- 不上传日志到外部系统.
- 不保存 raw provider payload.
- 不返回真实 account id.
- 不返回真实 order id.
- 不返回 provider endpoint URL.
- 不改 alpha model.
- 不改因子逻辑.
- 不新增交易策略.

---

### Task 1: Red Tests For V5.23 Contract

**Files:**
- Create: `tests/test_v523_provider_offline_replay.py`

**Interfaces:**
- Produces expected import and behavior contracts for all V5.23 modules, API routes, CLI, frontend, report, and safety scan.

- [x] **Step 1: Write tests for config, catalog, loader, state machine, runner, validators, audit trail, orchestrator, API, CLI, frontend, and safety scan.**
- [x] **Step 2: Run `./.venv312/bin/python -m pytest tests/test_v523_provider_offline_replay.py -q` and verify it fails because V5.23 modules are missing.**

### Task 2: Offline Replay Core

**Files:**
- Create: `config/v5_provider_offline_replay_config.py`
- Create: `provider_offline_replay/__init__.py`
- Create: `provider_offline_replay/replay_event_catalog.py`
- Create: `provider_offline_replay/replay_event_loader.py`
- Create: `provider_offline_replay/replay_state_machine.py`
- Create: `provider_offline_replay/replay_runner.py`

**Interfaces:**
- Produces `get_offline_replay_mode() -> str`
- Produces `get_offline_replay_provider() -> str`
- Produces `get_offline_replay_status() -> dict`
- Produces `boundary() -> dict`
- Produces `build_replay_event_catalog(provider: str) -> dict`
- Produces `load_replay_scenario(provider: str, scenario: str) -> dict`
- Produces `load_all_replay_scenarios(provider: str) -> dict`
- Produces `transition(current_state: str, event_type: str) -> dict`
- Produces `run_replay_scenario(provider: str, scenario: str) -> dict`
- Produces `run_all_replay_scenarios(provider: str) -> dict`

- [x] **Step 1: Implement config and boundary flags with all runtime/sandbox/account/order/real-money paths false.**
- [x] **Step 2: Implement generated placeholder event catalog without provider endpoint URL fields.**
- [x] **Step 3: Implement loader, state machine, and runner as offline-only state advancement.**
- [x] **Step 4: Run targeted tests and keep the red test moving toward green.**

### Task 3: Validators, Audit, Orchestrator, And Report

**Files:**
- Create: `provider_offline_replay/replay_consistency_validator.py`
- Create: `provider_offline_replay/replay_failure_recovery_validator.py`
- Create: `provider_offline_replay/replay_audit_trail.py`
- Create: `provider_offline_replay/replay_safety_validator.py`
- Create: `provider_offline_replay/offline_replay_orchestrator.py`
- Create: `provider_offline_replay/provider_offline_replay_report.py`
- Create: `scripts/run_v523_provider_offline_replay.py`

**Interfaces:**
- Produces `validate_replay_consistency(replay_result: dict) -> dict`
- Produces `validate_all_replay_consistency(provider: str) -> dict`
- Produces `validate_failure_recovery(provider: str) -> dict`
- Produces `build_replay_audit_trail(replay_result: dict) -> dict`
- Produces `build_all_replay_audit_trails(provider: str) -> dict`
- Produces `validate_replay_safety(payload: dict | str) -> dict`
- Produces `build_replay_safety_summary() -> dict`
- Produces `run_offline_replay(provider: str) -> dict`
- Produces `summarize_offline_replay_results(results: dict) -> dict`
- Produces `generate_provider_offline_replay_report(provider: str, scenario: str | None = None, check: str = "all") -> dict`

- [x] **Step 1: Implement consistency, recovery, audit, and safety validators.**
- [x] **Step 2: Implement orchestrator summary with PASS/WARNING/FAIL verdicts.**
- [x] **Step 3: Implement markdown report and CLI JSON output.**
- [x] **Step 4: Run targeted tests and fix issues.**

### Task 4: API, Frontend, Docs, And Security Scan

**Files:**
- Modify: `src/api/v2/server.py`
- Modify: `web/frontend/app/lib/apiClient.ts`
- Create: `web/frontend/app/v5-provider-offline-replay/page.tsx`
- Modify: `web/frontend/app/components/ProductionShell.tsx`
- Modify: `runtime/security_scan.py`
- Modify: `README.md`
- Create: `docs/V5_PROVIDER_OFFLINE_REPLAY.md`

**Interfaces:**
- Produces nine `/api/v5/provider-offline-replay/*` endpoints.
- Produces frontend fetch helpers and page route.
- Produces security scan helper for offline replay outputs.

- [x] **Step 1: Add API imports, boundary helper, and endpoints matching the V5.22 style.**
- [x] **Step 2: Add frontend API helpers, page, and nav item.**
- [x] **Step 3: Add docs and README section.**
- [x] **Step 4: Enhance security scan for offline replay.**

### Task 5: Final Verification And Review Package

**Files:**
- Create: `reports/v5_23_provider_offline_replay_report.md`
- Modify: `REVIEW_PACKAGE.md`

**Interfaces:**
- Produces final reviewer evidence for V5.23.

- [x] **Step 1: Run `./.venv312/bin/python -m pytest tests/test_v523_provider_offline_replay.py -q`.**
- [x] **Step 2: Run `./.venv312/bin/python -m py_compile ...` for V5.23 files.**
- [x] **Step 3: Run `./.venv312/bin/python scripts/run_v523_provider_offline_replay.py`.**
- [x] **Step 4: Run full pytest and system doctor.**
- [x] **Step 5: Clean generated runtime artifacts and confirm `git status`.**
