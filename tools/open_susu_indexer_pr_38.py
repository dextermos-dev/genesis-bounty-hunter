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

title = "feat(reliability): batch event, group and plan writes instead of unbounded upserts (Fixes #38)"
body = """## Summary

Fixes #38 by chunking database writes into bounded batches across `upsertEvents`, `upsertGroups`, `recordRejectedEvents`, and `persistPlan` (fact tables: `decoded_events`, `group_members`, `contributions`, `payouts`, `protocol_fees`), preventing large ledger ranges from exceeding PostgREST request-body and statement limits.

### Problem
Previously in `supabase/functions/indexer/index.ts` and `_shared/db.ts:109-119,206-251`, an entire ledger range was handed to single unbounded upsert calls. On busy ranges (with up to `INDEXER_MAX_LEDGER_RANGE` ledgers), tens of thousands of rows could be produced at once, exceeding statement/payload limits and failing the run repeatedly.

### Solution
1. **Configurable Batch Size (`DEFAULT_WRITE_BATCH_SIZE = 500`)**:
   - Added `DEFAULT_WRITE_BATCH_SIZE = 500` constant in `supabase/functions/_shared/db.ts`.
   - Added optional `writeBatchSize` configuration parameter in `IndexerConfig` (defaults to 500, configurable via `INDEXER_WRITE_BATCH_SIZE` up to 10,000).
2. **Chunked Writes**:
   - `upsertEvents`: Slices row batches bounded by `batchSize`.
   - `upsertGroups`: Slices new group discoveries bounded by `batchSize`.
   - `recordRejectedEvents`: Slices rejected events bounded by `batchSize`.
   - `persistPlan` & `#insertIgnoringDuplicates`: Slices all fact table rows (`decoded_events`, `group_members`, `contributions`, `payouts`, `protocol_fees`) bounded by `batchSize`.
3. **Fail-Fast Semantics**:
   - Sequential batch iteration guarantees that a failure on any middle batch throws immediately, failing the run and leaving the checkpoint completely untouched.
4. **Comprehensive Automated Verification (`tests/batch_writes_test.ts`)**:
   - Verified that no single PostgREST request carries more than the configured batch size across 1250 events, 750 groups, and 600+ plan fact rows.
   - Verified that all rows are written exactly once across batch boundaries without truncation or duplication.
   - Verified that a middle batch failure immediately throws and leaves subsequent batches unattempted and checkpoint untouched.

### Verification
- `deno task lint`: Clean (0 problems across 42 files).
- `deno task check`: Clean.
- `deno task test`: 230 passed (0 failed).

---
**Settlement Wallet (USDC / Base L2 / EVM):**
`0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:bounty-38-batch-writes",
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
        pr_url = res.get("html_url")
        pr_number = res.get("number")
        print(f"Created PR #{pr_number}: {pr_url}")

        # Post courteous comment on Issue #38
        comment_body = f"""Hello @SUSU-LABS maintainers,

We have resolved issue #38 in PR #{pr_number}: {pr_url}

### Summary of Resolution:
- Introduced `DEFAULT_WRITE_BATCH_SIZE = 500` (configurable via `INDEXER_WRITE_BATCH_SIZE` in `IndexerConfig`).
- Chunked writes into bounded batches across `upsertEvents`, `upsertGroups`, `recordRejectedEvents`, and all fact tables in `persistPlan`.
- Guaranteed that no single PostgREST request exceeds the batch threshold, while preserving exact rows and fail-fast checkpoint protection if any middle batch fails.
- Added comprehensive unit tests in `tests/batch_writes_test.ts` verifying chunk boundaries, row identity preservation, and middle-batch failure handling.

**Settlement Wallet (USDC / Base L2 / EVM):**
`0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`

We remain gladly at your disposal for any further reviews or tweaks you may need. Thank you! 🙌"""

        comment_req = urllib.request.Request(
            "https://api.github.com/repos/SUSU-LABS/susu-indexer/issues/38/comments",
            data=json.dumps({"body": comment_body}).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(comment_req) as c_resp:
            c_res = json.loads(c_resp.read().decode("utf-8"))
            print(f"Posted comment on Issue #38: {c_res.get('html_url')}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
