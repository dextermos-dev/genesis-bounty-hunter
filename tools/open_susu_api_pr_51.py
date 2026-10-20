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

title = "fix(server): close PostgreSQL pool during server shutdown (Fixes #51)"
body = """## Summary

Fixes #51 by registering a Fastify `onClose` hook in `buildServer` that invokes `closeDb()`, ensuring the PostgreSQL connection pool drains in-flight queries and closes gracefully during server shutdown rather than leaking connections.

### Problem
Previously, `closeDb()` in `src/db/client.ts` was exported but never imported or invoked by the application or server. `src/index.ts` called `app.close()` and exited immediately without closing the database pool, leaving connections un-drained and leaking the pool whenever the process did not hard-exit.

### Solution
1. **Server Lifecycle Hook (`src/server.ts`)**:
   - Imported `closeDb` from `./db/client`.
   - Supported dependency injection via `BuildServerOptions.closeDatabase?: () => Promise<void>` (defaulting to `closeDb`).
   - Registered an `onClose` hook: `app.addHook('onClose', async () => closeDatabase())`.
2. **Process Shutdown Drainage (`src/index.ts`)**:
   - Explicitly invoked `await closeDb()` in the signal shutdown handler after `await app.close()` as defensive cleanup.
3. **Lifecycle Test Coverage (`tests/server.test.ts`)**:
   - Added unit tests verifying:
     * `app.close()` invokes `closeDatabase` hook.
     * Default hook invokes `closeDb()`, closing the real pool and setting `pool.ended === true`.
     * Calling `closeDb()` again is idempotent.

### Verification
- `npm run lint`: Clean (0 errors, 0 warnings).
- `npx tsc --noEmit`: Clean (0 errors).
- `npx vitest run tests/server.test.ts`: 16 tests passed (0 failed).

---
Settlement Wallet: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:bounty-51-close-pool-on-shutdown",
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

        # Post comment on issue #51
        issue_comment = f"""Hello @SUSU-LABS maintainers,

We have resolved issue #51 in PR #{pr_number}: {pr_url}

### Summary of Resolution:
- Registered a Fastify `onClose` hook in `buildServer` that invokes `closeDb()`, draining in-flight queries and gracefully ending the PostgreSQL pool.
- Added optional `closeDatabase` injection to `BuildServerOptions` for seamless test mocking.
- Added comprehensive lifecycle tests in `tests/server.test.ts` verifying that `app.close()` triggers the hook and leaves `pool.ended === true`.
- All tests pass, TypeScript compiler is clean, and ESLint is clean.

We remain at your service if you would like any adjustments to the lifecycle hook or tests!

Settlement Wallet: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`"""

        comment_payload = {"body": issue_comment}
        comment_req = urllib.request.Request(
            "https://api.github.com/repos/SUSU-LABS/susu-api/issues/51/comments",
            data=json.dumps(comment_payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(comment_req) as c_resp:
            print("Comment posted on Issue #51 successfully!")

except Exception as e:
    if hasattr(e, "read"):
        print("Error:", e.read().decode("utf-8"))
    else:
        print("Error:", e)
