from __future__ import annotations

import json


def test_synthetic_market_generator_is_deterministic():
    from runtime.synthetic_market import SyntheticMarketGenerator

    first = SyntheticMarketGenerator(seed=123).generate(mode="trend", ticks=20, symbols=["AAPL", "MSFT"])
    second = SyntheticMarketGenerator(seed=123).generate(mode="trend", ticks=20, symbols=["AAPL", "MSFT"])

    assert first.equals(second)
    assert set(["datetime", "symbol", "open", "high", "low", "close", "volume"]).issubset(first.columns)
    assert set(first["symbol"]) == {"AAPL", "MSFT"}


def test_soak_test_runner_completes_500_ticks(tmp_path):
    from runtime.soak_test_runner import run_synthetic_soak_test

    result = run_synthetic_soak_test(ticks=500, output_dir=tmp_path, seed=7)

    assert result["success"] is True
    assert result["ticks_processed"] == 500
    assert result["final_equity"] > 0
    assert result["checkpoint_count"] >= 1
    assert result["health_status"] in {"HEALTHY", "DEGRADED", "FAILED"}
    assert result["errors"] == []


def test_checkpoint_and_recovery_from_soak_test(tmp_path):
    from runtime.recovery_engine import RecoveryEngine
    from runtime.soak_test_runner import run_synthetic_soak_test
    from runtime.state_checkpoint import StateCheckpoint
    from trading.paper_account import PaperAccount

    result = run_synthetic_soak_test(ticks=120, output_dir=tmp_path, seed=8)
    checkpoint = StateCheckpoint(tmp_path / "data" / "runtime_state_checkpoint.json")
    account = PaperAccount(initial_cash=100_000)
    restored = RecoveryEngine(checkpoint).restore_account(account)

    assert result["checkpoint_count"] >= 1
    assert restored["restored"] is True
    assert account.cash >= 0


def test_fault_injection_does_not_crash_and_records_errors(tmp_path):
    from runtime.soak_test_runner import run_synthetic_soak_test

    result = run_synthetic_soak_test(ticks=180, output_dir=tmp_path, seed=9, faults=True)

    assert result["success"] is True
    assert result["error_count"] >= 1
    assert result["mode"] in {"DEGRADED", "SAFE_MODE"}
    assert (tmp_path / "logs" / "runtime.jsonl").exists()


def test_consistency_validator_passes_after_soak(tmp_path):
    from runtime.consistency_validator import ConsistencyValidator
    from runtime.soak_test_runner import run_synthetic_soak_test

    result = run_synthetic_soak_test(ticks=160, output_dir=tmp_path, seed=10)
    validation = ConsistencyValidator().validate(result["final_state"], result["checkpoint_state"])

    assert validation["consistent"] is True
    assert validation["errors"] == []


def test_security_scan_finds_no_sensitive_data(tmp_path):
    from runtime.security_scan import scan_runtime_outputs
    from runtime.soak_test_runner import run_synthetic_soak_test

    run_synthetic_soak_test(ticks=80, output_dir=tmp_path, seed=11, faults=True)
    scan = scan_runtime_outputs([tmp_path / "logs", tmp_path / "data", tmp_path / "reports"])

    assert scan["safe"] is True
    assert scan["findings"] == []


def test_soak_report_is_generated(tmp_path):
    from runtime.soak_test_runner import run_synthetic_soak_test

    result = run_synthetic_soak_test(ticks=100, output_dir=tmp_path, seed=12)
    report_path = tmp_path / "reports" / "v5_3_soak_test_report.md"

    assert report_path.exists()
    text = report_path.read_text(encoding="utf-8")
    assert "V5.3 Long-Run Paper Trading Soak Test Report" in text
    assert "Final verdict" in text
    assert result["final_verdict"] in {"PASS", "WARNING", "FAIL"}


def test_risk_kill_switch_can_trigger_in_crash_market(tmp_path):
    from runtime.soak_test_runner import run_synthetic_soak_test

    result = run_synthetic_soak_test(ticks=220, output_dir=tmp_path, seed=13, market_mode="crash")

    assert result["risk_kill_switch_triggered"] is True
    assert result["final_verdict"] in {"WARNING", "FAIL"}


def test_soak_test_cli_outputs_json_summary(tmp_path):
    import subprocess
    import sys

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_v53_soak_test.py",
            "--mode",
            "synthetic",
            "--ticks",
            "120",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(completed.stdout)

    assert summary["success"] is True
    assert summary["ticks_processed"] == 120
    assert (tmp_path / "reports" / "v5_3_soak_test_report.md").exists()
