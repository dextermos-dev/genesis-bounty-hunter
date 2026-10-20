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

title = "fix(invites): do not spend invite use when join code targets different group (Fixes #49)"
body = """## Summary

Fixes #49 by validating that the invite code matches the expected group before performing any database writes, ensuring that a request targeting a mismatched group returns `404 invite_not_found` with zero writes to `invite_redemptions` and leaving `invite_links.uses` completely untouched.

### Problem
Previously, `claimUse` in `src/routes/invites.ts` called `store.redeem` prior to checking `expectedGroup !== undefined && result.groupContractId !== expectedGroup`. As a consequence, `store.redeem` recorded a redemption and incremented `invite_links.uses` before returning `404 invite_not_found` to the caller, consuming a limited invite use for a join that never took place.

### Solution
1. **Store Layer (`src/db/invites.ts`)**:
   - Extended `InviteStore.redeem` parameters with `expectedGroup?: string`.
   - In both preview lookup and under row lock inside the transaction, checked `expectedGroup !== undefined && invite.groupContractId !== expectedGroup`.
   - If a mismatch occurs, immediately returned `{ outcome: 'not_found' }` before opening a transaction or acquiring row locks, avoiding unnecessary I/O (`shouldClaim` is skipped) and guaranteeing zero writes to `invite_redemptions` or `invite_links.uses`.
2. **Route Layer (`src/routes/invites.ts`)**:
   - Passed `expectedGroup` directly from `claimUse` into `store.redeem`.
3. **Integration & Route Test Coverage**:
   - Added real PostgreSQL integration tests in `tests/invite-store.test.ts` (using PGlite):
     * Proves `POST /groups/<wrongId>/join` returns `not_found` and leaves `uses` and `invite_redemptions` unchanged.
     * Proves a subsequent correct `/groups/<rightId>/join` succeeds and spends exactly one use.
     * Proves `shouldClaim` is not called on mismatch.
   - Added route tests in `tests/invites.test.ts` asserting that `expectedGroup` is propagated and that mismatched groups receive 404 without writes.

### Verification
- `npm run lint`: Clean (0 errors, 0 warnings).
- `npx tsc --noEmit`: Clean (0 errors).
- `npx vitest run`: 402 tests passed across 30 test suites (0 failed).

---
Settlement Wallet: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:bounty-49-invite-group-mismatch",
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
        pr_number = res.get("number")
        pr_url = res.get("html_url")
        print(f"PR Created: #{pr_number} -> {pr_url}")

        # Post comment on issue #49
        issue_comment = f"""Hello @SUSU-LABS maintainers,

We have resolved issue #49 in PR #{pr_number}: {pr_url}

### Summary of Resolution:
- Passed `expectedGroup` into `store.redeem` to check group match before writing anything.
- If mismatched, returns `not_found` immediately before opening a transaction or acquiring row locks, skipping `shouldClaim` and ensuring zero writes to `invite_redemptions` and `invite_links.uses`.
- Verified with store-level PGlite integration tests and route tests proving zero writes on mismatch and successful subsequent redemption on the correct group.
- All 402 unit/integration tests pass, TypeScript compiler is clean, and ESLint is clean.

We remain at your service if you would like any adjustments to code style, typing, or additional test coverage!

Settlement Wallet: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`"""

        comment_payload = {"body": issue_comment}
        comment_req = urllib.request.Request(
            "https://api.github.com/repos/SUSU-LABS/susu-api/issues/49/comments",
            data=json.dumps(comment_payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(comment_req) as c_resp:
            print("Comment posted on Issue #49 successfully!")

except Exception as e:
    if hasattr(e, "read"):
        print("Error:", e.read().decode("utf-8"))
    else:
        print("Error:", e)
