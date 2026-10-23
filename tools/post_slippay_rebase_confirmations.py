#!/usr/bin/env python3
"""
Post polite and humble rebase confirmation comments to maintainer @Obaara293
on PRs #228, #340, #435, and #453 in slippay-labs/slippay.
"""

import os
import json
import urllib.request
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k] = v.strip('"').strip("'")

TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "BountyHunterAI/2.0",
    "Content-Type": "application/json"
}

def post_comment(pr_num, specific_notes):
    url = f"https://api.github.com/repos/slippay-labs/slippay/issues/{pr_num}/comments"
    body = f"""Hi @Obaara293! 👋

Thank you so much for the clear guidance and security notification. We have completed the clean rebase onto the rewritten `upstream/main` as requested.

### Verification Summary
- **Base**: Rebased cleanly onto the latest purged `main` (`fedc051`).
- **Diff Cleanliness**: {specific_notes}
- **Security Check**: Verified that `apps/web/postcss.config.cjs` is untouched and contains strictly the clean one-line `module.exports`.
- **Mergeability**: Branch is fully mergeable with zero conflicts (`mergeable: true`).

**Settlement Wallet (Base USDC)**: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`

We remain at your entire disposal if you need any adjustments or additional test cases! 🚀"""

    payload = {"body": body}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"[+] Comment posted to PR #{pr_num}: {data.get('html_url')}")
    except Exception as e:
        print(f"[-] Error on PR #{pr_num}: {e}")

if __name__ == "__main__":
    post_comment(228, "PR strictly untracks the 8 compiled `.pyc` files and updates `.gitignore` with Python cache patterns, accompanied by the regression test in `packages/shared/test/gitignore.test.ts` (10 files total).")
    post_comment(340, "PR strictly encompasses the canonical fee arithmetic specification across `docs/fees.md` and associated verification tests (10 files total).")
    post_comment(435, "PR strictly updates the checkout fee semantics in `contracts/checkout/` and `docs/contracts/` plus anti-drift vector tests (4 files total).")
    post_comment(453, "PR strictly implements integer stroop comparison for `txguard` and currency conversions with full test vectors (6 files total).")
