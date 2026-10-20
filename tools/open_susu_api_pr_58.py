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

title = "fix(registrations): compute registration expiry from database clock (Fixes #58)"
body = """## Summary

Fixes #58 by deriving registration expiry strictly from the PostgreSQL database clock (`now() + (REGISTRATION_TTL_MS * interval '1 millisecond')`) rather than the host application clock (`Date.now() + TTL`).

### Problem
Previously, `src/db/registrations.ts` computed `expires_at` using the host's `Date.now() + REGISTRATION_TTL_MS`, while `isRegistered`, cleanup deletes, and default `created_at` all relied on the PostgreSQL database clock (`sql\`now()\``). Host clock skew (specifically if the host clock ran behind the database clock) could cause `expires_at <= created_at`, violating the `group_registrations_window_positive` check constraint (`expires_at > created_at`) and returning 500 errors to callers during registration.

### Solution
1. **Single Database Clock Authority (`src/db/registrations.ts`)**:
   - Replaced host `Date.now()` arithmetic with SQL database clock expression:
     `sql\`now() + (${REGISTRATION_TTL_MS} * interval '1 millisecond')\``
   - Applied this consistently across both `insert` (`.values(...)`) and re-registration `update` (`.set(...)`).
   - Derived returned `expiresAt` directly from the PostgreSQL `returning({ expiresAt: groupRegistrations.expiresAt })` row, ensuring the application always reports the database's authoritative timestamp.
2. **Postgres Integration Tests (`tests/registrations.test.ts`)**:
   - Added tests with synthetic host clock skew via `vi.useFakeTimers()` / `vi.setSystemTime()`:
     * When host clock is skewed 2 hours in the past, registration succeeds without check constraint violation, maintaining `positive_window = true` and `window_seconds = 1800`.
     * When host clock is skewed 24 hours in the future, registration window duration remains exactly 30 minutes, completely unaffected by application clock skew.

### Verification
- `npm run lint`: Clean (0 errors, 0 warnings).
- `npx tsc --noEmit`: Clean (0 errors).
- `npx vitest run tests/registrations.test.ts`: 12 tests passed (0 failed).

---
Settlement Wallet: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:bounty-58-single-clock-registration",
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

        # Post courteous comment on issue #58
        issue_comment = f"""Hello @SUSU-LABS maintainers,

We have resolved issue #58 in PR #{pr_number}: {pr_url}

### Summary of Resolution:
- Derived `expiresAt` strictly from the database clock via `sql`now() + (${{REGISTRATION_TTL_MS}} * interval '1 millisecond')`` in both insert and update queries.
- Ensured `created_at` and `expires_at` share the single database transaction clock authority, making check constraint `group_registrations_window_positive` immune to host clock skew.
- Verified with integration tests in `tests/registrations.test.ts` showing that skewing application clock hours into the past or future leaves the 30-minute window unaffected and passes constraint checks.
- All tests pass, TypeScript compiler is clean, and ESLint is clean.

We remain at your service if you would like any adjustments to the SQL expression, types, or tests!

Settlement Wallet: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`"""

        comment_payload = {"body": issue_comment}
        comment_req = urllib.request.Request(
            "https://api.github.com/repos/SUSU-LABS/susu-api/issues/58/comments",
            data=json.dumps(comment_payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(comment_req) as c_resp:
            print("Comment posted on Issue #58 successfully!")

except Exception as e:
    if hasattr(e, "read"):
        print("Error:", e.read().decode("utf-8"))
    else:
        print("Error:", e)
