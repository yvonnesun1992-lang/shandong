from __future__ import annotations

import re
from pathlib import Path
import json


SENSITIVE_PATTERN = re.compile(r"(api_key|secret|token|password|authorization|sk-[A-Za-z0-9])", re.IGNORECASE)


def scan_runtime_outputs(paths: list[str | Path]) -> dict:
    findings = []
    for path in paths:
        root = Path(path)
        if not root.exists():
            continue
        files = [root] if root.is_file() else [item for item in root.rglob("*") if item.is_file()]
        for file_path in files:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if SENSITIVE_PATTERN.search(line):
                    findings.append({"path": file_path.as_posix(), "line": line_no, "kind": "sensitive-pattern"})
                    break
    return {"safe": not findings, "findings": findings}


def scan_payload(payload: dict | list | str) -> dict:
    text = json.dumps(payload, default=str) if not isinstance(payload, str) else payload
    findings = []
    for match in SENSITIVE_PATTERN.finditer(text):
        findings.append({"kind": "sensitive-pattern", "match": match.group(0)})
    return {"safe": not findings, "findings": findings}

