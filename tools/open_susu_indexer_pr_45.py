#!/usr/bin/env python3
import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN", "").strip()
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "dextermos-dev"
}

title = "fix(indexer): stop silently skipping ledgers when start ledger is raised (Fixes #45)"
body = """## Summary

Fixes #45 by ensuring that once a checkpoint exists, `computeLedgerRange` always resumes strictly from `lastProcessedLedger + 1` rather than advancing to a raised `startLedger`, eliminating silent ledger skipping and alerting operators when a configured start ledger is ahead of the checkpoint.

### Problem
Previously, `computeLedgerRange` in `supabase/functions/_shared/checkpoint.ts` computed `from = lastProcessedLedger === null ? startLedger : Math.max(lastProcessedLedger + 1, startLedger)`. When an operator raised `INDEXER_START_LEDGER` in the environment (or `indexer_checkpoints.start_ledger`), `Math.max` jumped `from` forward across the gap, silently skipping all intervening ledgers without any warning or notification.

### Solution
1. **Range Calculation Safety (`supabase/functions/_shared/checkpoint.ts`)**:
   - Updated `computeLedgerRange` so that when `lastProcessedLedger !== null`, `from` is strictly `lastProcessedLedger + 1`.
   - `startLedger` is used solely on the initial run when `lastProcessedLedger === null`.
   - Exported `isStartLedgerAheadOfCheckpoint(lastProcessedLedger, startLedger)` helper to detect configuration discrepancies.
2. **Operator Alerting & Rebuild Guidance (`supabase/functions/indexer/index.ts`)**:
   - In `handleRequest`, if a checkpoint exists and `configuredStart > checkpoint.lastProcessedLedger + 1`, emits a structured `logger.warn` explaining that indexing continues from the checkpoint to prevent silent ledger skipping, and directs the operator to follow the documented rebuild procedure in `docs/RUNBOOK.md` to reset the checkpoint if a full re-index is intended.
3. **Rebuild Procedure Compatibility**:
   - Fully compatible with the documented rebuild procedure (`last_processed_ledger = :start_ledger - 1`), since `:start_ledger - 1 + 1 == :start_ledger`.
4. **Test Coverage**:
   - Added unit tests in `tests/checkpoint_test.ts` asserting:
     * A raised `startLedger` does not advance `computeLedgerRange` past `lastProcessedLedger + 1`.
     * The documented rebuild procedure reset takes effect cleanly.
     * `isStartLedgerAheadOfCheckpoint` accurately detects discrepancies.
   - Added orchestration integration test in `tests/indexer_orchestration_test.ts` verifying that `handleRequest` with a raised `INDEXER_START_LEDGER` ignores the jump, emits warning, and resumes cleanly from the checkpoint.

### Verification
- `deno task lint`: Clean (0 problems across 41 files).
- `deno task check`: Clean.
- `deno task test`: 228 tests passed (0 failed).

---
Settlement Wallet: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:bounty-45-prevent-start-ledger-skip",
    "base": "main",
    "body": body
}

req = urllib.request.Request(
    "https://api.github.com/repos/SUSU-LABS/susu-indexer/pulls",
    data=json.dumps(payload).encode("utf-8"),
    headers=headers,
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        pr_number = res.get("number")
        pr_url = res.get("html_url")
        print(f"PR Created: #{pr_number} -> {pr_url}")

        # Post comment on issue #45
        issue_comment = f"""Hello @SUSU-LABS maintainers,

We have resolved issue #45 in PR #{pr_number}: {pr_url}

### Summary of Resolution:
- Ensured `computeLedgerRange` always resumes from `lastProcessedLedger + 1` when a checkpoint is present, eliminating silent ledger skipping when `startLedger` is raised.
- Emits a structured `logger.warn` alert when `startLedger > checkpoint + 1`, explaining that the jump is ignored to preserve ledger continuity and referencing the documented rebuild procedure in `docs/RUNBOOK.md`.
- Fully preserves compatibility with the documented rebuild procedure (`last_processed_ledger = start_ledger - 1`).
- Added unit and orchestration tests covering raised `startLedger` and rebuild compatibility; all 228 Deno tests pass and linter/typecheck are clean.

We remain at your service if you would like any adjustments to code style, typing, or additional test coverage!

Settlement Wallet: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`"""

        comment_payload = {"body": issue_comment}
        comment_req = urllib.request.Request(
            "https://api.github.com/repos/SUSU-LABS/susu-indexer/issues/45/comments",
            data=json.dumps(comment_payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(comment_req) as c_resp:
            print("Comment posted on Issue #45 successfully!")

except Exception as e:
    if hasattr(e, "read"):
        print("Error:", e.read().decode("utf-8"))
    else:
        print("Error:", e)
