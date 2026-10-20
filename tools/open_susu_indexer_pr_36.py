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

title = "fix(reliability): stop retrying deterministic non-transient RPC and DB errors (Fixes #36)"
body = """## Summary

Fixes #36 by adding and applying an `isRetryableError` predicate across RPC and database operations, preventing wasteful retries and quota exhaustion on deterministic errors (such as JSON-RPC `-32600: startLedger must be within the ledger range`, HTTP 4xx client errors, and Postgres constraint violations).

### Problem
Previously, `withRetry` defaulted `isRetryable` to `true`, and neither `scan.ts` nor `indexer/index.ts` supplied a predicate. Non-transient errors like Soroban `-32600` or database integrity violations were retried four times with backoff (~4 seconds of unnecessary latency), wasting RPC quota and obscuring the root cause in logs and health checks.

### Solution
1. **Predicate Definition (`supabase/functions/_shared/retry.ts`)**:
   - Implemented `isRetryableError(error: unknown): boolean` and exported `DEFAULT_RETRY_POLICY`.
   - **Non-retryable (attempted once)**:
     * HTTP 4xx client errors (400, 401, 403, 404, 422).
     * Deterministic JSON-RPC validation codes (`-32600`, `-32601`, `-32602`, `-32700`).
     * Documented out-of-bounds startLedger errors (`startLedger must be within the ledger range`).
     * Postgres integrity constraint violations (Class 23: not-null, unique, foreign key, check violations).
   - **Retryable (retried with backoff)**:
     * HTTP 408 (Request Timeout) and 429 (Too Many Requests).
     * HTTP 5xx server errors (500, 502, 503, 504).
     * Network transport errors (`fetch failed`, `ECONNRESET`, `ECONNREFUSED`, `ETIMEDOUT`).
     * Transient database transport and timeout errors.
2. **RPC Client & Consumers**:
   - Extended `RpcError` in `supabase/functions/_shared/stellar.ts` to capture the JSON-RPC error `code`.
   - Passed `isRetryableError` in `scan.ts` and `indexer/index.ts`.
3. **Automated Verification (`tests/retry_test.ts`)**:
   - Added unit tests asserting exact classifications for all 4xx, 5xx, JSON-RPC, network, and Postgres constraint scenarios.
   - Asserted that 4xx and validation `RpcError` are attempted exactly once.
   - Asserted that Postgres constraint violations (`not-null`, `unique`) are attempted exactly once.
   - Asserted that 5xx and network errors retry across all 4 configured attempts.

### Verification
- `deno task lint`: Clean (0 problems across 41 files).
- `deno task check`: Clean.
- `deno task test`: 231 passed (0 failed).

---
**Settlement Wallet (USDC / Base L2 / EVM):**
`0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:bounty-36-classify-retryable-errors",
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

        # Post courteous comment on Issue #36
        comment_body = f"""Hello @SUSU-LABS maintainers,

We have resolved issue #36 in PR #{pr_number}: {pr_url}

### Summary of Resolution:
- Implemented `isRetryableError` predicate and `DEFAULT_RETRY_POLICY` in `supabase/functions/_shared/retry.ts`.
- Classified HTTP 4xx, JSON-RPC `-32600`/validation errors, and Postgres constraint violations (Class 23) as non-retryable (attempted exactly once).
- Preserved retries with exponential backoff for transient failures (HTTP 5xx, 408, 429, fetch/network errors, and DB transport timeouts).
- Applied the predicate in `scan.ts` and `indexer/index.ts`.
- Added automated test cases in `tests/retry_test.ts` asserting exact attempt counts for both classifications.

**Settlement Wallet (USDC / Base L2 / EVM):**
`0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`

We are delighted to make any further adjustments or address any questions you might have. Thank you! 🙌"""

        comment_req = urllib.request.Request(
            "https://api.github.com/repos/SUSU-LABS/susu-indexer/issues/36/comments",
            data=json.dumps({"body": comment_body}).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(comment_req) as c_resp:
            c_res = json.loads(c_resp.read().decode("utf-8"))
            print(f"Posted comment on Issue #36: {c_res.get('html_url')}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
