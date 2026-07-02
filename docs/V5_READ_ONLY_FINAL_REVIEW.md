# V5.38 Sandbox Read-Only Connector Final Review Board

V5.38 adds a read-only connector final review board. It reviews local evidence from V5.34 mock replay, V5.35 fault injection, V5.36 stability gate, and V5.37 evidence pack.

This is a final review board only. It cannot approve real broker access, sandbox API access, credential reads, account reads, balance reads, position reads, order preview, order submission, or real funds.

## Review Scope

- Final review charter
- Reviewer role matrix
- Evidence review matrix
- Risk acceptance matrix
- Missing requirement register
- Final review decision
- Final review audit trail
- Final review safety validation

## Decision

The V5.38 decision is always `READ_ONLY_FINAL_REVIEW_ONLY`.

Even if evidence review is ready, risk acceptance is simulated, or a simulated approval is present, V5.38 cannot set `final_review_passed` to true and cannot set `read_only_connector_allowed` to true.

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
python scripts/run_v538_read_only_final_review.py
```

The generated report is:

```text
reports/v5_38_sandbox_read_only_final_review_report.md
```

