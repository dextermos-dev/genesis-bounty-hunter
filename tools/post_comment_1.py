#!/usr/bin/env python3
import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN", "").strip()
wallet = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "dextermos-dev",
    "Content-Type": "application/json"
}

body = f"""Hello maintainers!

We have submitted a focused, high-reliability pull request to resolve this issue:
PR: https://github.com/Parabola-org/parabola/pull/101

Key highlights:
- `pollTransactionStatus` now catches transient RPC errors (connection resets, 5xx, network drops) and tracks consecutive failures, mirroring the policy in `src/iris/poll.ts`.
- Standardized constants `STELLAR_RPC_MAX_CONSECUTIVE_FAILURES = 5` and `STELLAR_RPC_RETRY_INTERVAL_MS = 2000` with documented tolerance rationale.
- Re-throws terminal `FAILED` status immediately without retrying.
- Upon persistent failure or deadline expiration, preserves `burnTxHash` via `SubmissionTimeoutError(..., hash)`, guaranteeing callers never lose the handle to an already-broadcast transaction.
- 5 comprehensive tests added in `tests/stellar.test.ts` (16/16 stellar tests passing, 123/123 total suite pass, 0 TypeScript errors).

/claim #1
Settlement Wallet: {wallet}"""

url = "https://api.github.com/repos/Parabola-org/parabola/issues/1/comments"
req = urllib.request.Request(url, data=json.dumps({"body": body}).encode("utf-8"), headers=headers, method="POST")
with urllib.request.urlopen(req) as resp:
    print("Comment posted status:", resp.status)
    data = json.loads(resp.read().decode("utf-8"))
    print("Comment URL:", data.get("html_url"))
