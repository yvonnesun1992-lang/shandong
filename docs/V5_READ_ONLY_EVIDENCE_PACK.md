# V5.37 Sandbox Read-Only Connector Evidence Pack

V5.37 builds a read-only connector evidence pack from local V5.34 mock replay evidence, V5.35 fault injection evidence, and V5.36 stability gate evidence.

This is an evidence packaging layer only. It does not connect to any real broker, broker sandbox API, provider portal, account, balance, position, order, or funding path.

## Included Evidence

- Evidence source inventory
- Evidence completeness check
- Redaction evidence pack
- Schema evidence pack
- Audit evidence pack
- Order blocking evidence pack
- Safety boundary evidence pack
- Evidence pack decision
- Evidence pack safety validation

## Decision

The V5.37 decision is always `READ_ONLY_EVIDENCE_ONLY`.

Even if evidence is complete, the evidence pack cannot set `evidence_pack_passed` to true and cannot set `read_only_connector_allowed` to true.

## Safety Boundary

- No real broker API
- No broker sandbox API
- No provider portal access
- No real or sandbox account creation
- No credential, API key, token, secret, or password read
- No real or sandbox account read
- No balance or position read
- No order preview
- No order submission
- No raw provider payload storage
- No real account id or order id
- No provider endpoint URL
- No unredacted balance, position, buying power, quantity, or market value
- No real money
- No alpha model changes
- No factor logic changes
- No new strategy

## Report

Run:

```bash
python scripts/run_v537_read_only_evidence_pack.py
```

The generated report is:

```text
reports/v5_37_sandbox_read_only_evidence_pack_report.md
```

