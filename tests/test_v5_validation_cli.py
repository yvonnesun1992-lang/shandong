from __future__ import annotations

import subprocess
import sys


def test_v5_validation_cli_help_imports_project_modules():
    result = subprocess.run(
        [sys.executable, "scripts/run_v5_validation.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Run V5 alpha validation" in result.stdout


def test_v5_validation_batch_cli_help_imports_project_modules():
    result = subprocess.run(
        [sys.executable, "scripts/run_v5_validation_batch.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Run V5 multi-universe validation" in result.stdout
