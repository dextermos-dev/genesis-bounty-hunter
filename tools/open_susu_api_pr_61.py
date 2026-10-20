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

title = "fix(invites): add per-account rate limiting to invite creation (Fixes #61)"
body = """## Summary

Fixes #61 by adding per-account rate limiting to the invite-creation route (`POST /groups/:contractId/invites`), preventing unbounded growth of `invite_links` rows and uncontrolled code generation by authenticated accounts.

### Problem
Previously, `POST /groups/:contractId/invites` lacked any route-specific or per-user rate limit, relying solely on the broad 100/minute global IP budget. Authenticated users could mint unlimited invite codes across multiple sessions or rotating IP addresses, accumulating rows in the database as noted in `src/db/schema.ts:415-423` and `README.md:296-300`.

### Solution
1. **Per-Account Rate Limiter (`src/routes/invites.ts`)**:
   - Initialised `app.createRateLimit` with `max: 20` and `timeWindow: '1 minute'`, mirroring `verifiedUserLimiter` in `src/routes/transactions.ts:92-100`.
   - Keyed on `user ? `user:${user.id}` : `ip:${request.ip}``.
   - Enforced in `preHandler` right after `requireAuth`, evaluating `verifiedUserLimiter(request)` and throwing a standard 429 error (`Rate limit exceeded, retry in 1 minute`) when the limit is exceeded.
2. **Documentation & Schema Synchronization**:
   - Updated comments in `src/db/schema.ts` and `README.md` to document that rate limiting for invitation abuse is now actively enforced per account.
3. **Route Integration Tests (`tests/invites.test.ts`)**:
   - Verified that exceeding the 20-creations-per-minute limit returns HTTP 429 and stops calls to `store.create`.
   - Verified that rotating IP addresses does not allow a single user to bypass their rate limit budget.
   - Verified that invite creation budgets are strictly isolated between distinct authenticated users.

### Verification
- `npm run lint`: Clean (0 errors, 0 warnings).
- `npx tsc --noEmit`: Clean (0 errors).
- `npx vitest run tests/invites.test.ts`: 36 passed across all test suites (0 failed).

---
**Settlement Wallet (USDC / Base L2 / EVM):**
`0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:bounty-61-invite-creation-rate-limit",
    "base": "main",
    "body": body
}

req = urllib.request.Request(
    "https://api.github.com/repos/SUSU-LABS/susu-api/pulls",
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

        # Post courteous comment on Issue #61
        comment_body = f"""Hello @SUSU-LABS maintainers,

We have resolved issue #61 in PR #{pr_number}: {pr_url}

### Summary of Resolution:
- Added per-account rate limiting via `app.createRateLimit` (`max: 20`, `timeWindow: '1 minute'`) keyed on `user:${{user.id}}` in `preHandler` after `requireAuth`, mirroring `src/routes/transactions.ts`.
- Refuses excess creations with HTTP 429 (`Rate limit exceeded, retry in 1 minute`) and stops store writes.
- Updated `src/db/schema.ts` and `README.md` to align with the implemented mitigation.
- Added 3 comprehensive route tests in `tests/invites.test.ts` verifying the 429 refusal, IP decoupling / anti-evasion, and multi-user budget isolation.

**Settlement Wallet (USDC / Base L2 / EVM):**
`0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`

We remain fully at your service if you would like any parameter adjustments or additional test cases. Thank you! 🙌"""

        comment_req = urllib.request.Request(
            "https://api.github.com/repos/SUSU-LABS/susu-api/issues/61/comments",
            data=json.dumps({"body": comment_body}).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(comment_req) as c_resp:
            c_res = json.loads(c_resp.read().decode("utf-8"))
            print(f"Posted comment on Issue #61: {c_res.get('html_url')}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
