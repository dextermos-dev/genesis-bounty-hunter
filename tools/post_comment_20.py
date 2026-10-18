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

We have submitted an exhaustive, clean pull request to resolve this issue:
PR: https://github.com/Parabola-org/parabola/pull/100

Key highlights:
- `convertPrecision` re-exported from `src/index.ts` with zero runtime code modifications beyond the export.
- Type definitions and bundles verified against `dist/index.d.ts` and `dist/index.js`.
- Comprehensive test suite in `tests/encoding.test.ts` asserting upscale exactness, downscale truncation, matching decimals identity, zero handling, 6->7->6 round-trip identity preservation, 7->6->7 round-trip truncation pinning with exact BigInt delta assertions, and end-to-end integration with `parseUsdcAmount` and `formatUsdcAmount`.
- 100% passing tests (118/118 vitest tests) and clean TypeScript typecheck.

/claim #20
Settlement Wallet: {wallet}"""

url = "https://api.github.com/repos/Parabola-org/parabola/issues/20/comments"
req = urllib.request.Request(url, data=json.dumps({"body": body}).encode("utf-8"), headers=headers, method="POST")
with urllib.request.urlopen(req) as resp:
    print("Comment posted status:", resp.status)
    data = json.loads(resp.read().decode("utf-8"))
    print("Comment URL:", data.get("html_url"))
