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

title = "fix(server): tie nonce-reaper timer to server lifecycle and require opt-in (Fixes #52)"
body = """## Summary

Fixes #52 by tying the nonce reaper interval timer directly to the Fastify server lifecycle via an `onClose` hook, and making background reaping require explicit opt-in (`enableNonceReaping: true`) so that test servers do not spawn background timers.

### Problem
Previously, `src/server.ts` started a 15-minute `setInterval` whenever `walletLinkStore === undefined` and discarded the timer handle. Calling `app.close()` never cleared the interval, causing closed test servers to leak live background timers that could lazily create real database pools and run queries long after server shutdown.

### Solution
1. **Explicit Opt-in & Lifecycle Management (`src/server.ts`)**:
   - Added `enableNonceReaping?: boolean` and `reapNonces?: boolean` to `BuildServerOptions`.
   - Started the background timer only when explicitly enabled (defaults to `false`), preventing background timer leaks in tests.
   - Tied the interval to the server lifecycle: registered an `onClose` hook (`app.addHook('onClose', async () => clearInterval(timer))`).
2. **Production Startup (`src/index.ts`)**:
   - Enabled background nonce reaping in production main entrypoint: `buildServer({ enableNonceReaping: true })`.
3. **Lifecycle Test Coverage (`tests/server.test.ts`)**:
   - Verified no interval is started when `enableNonceReaping` is not opted into.
   - Verified that when opted into, `app.close()` clears the interval (`clearInterval` called) and advancing fake timers generates zero subsequent ticks after close.

### Verification
- `npm run lint`: Clean (0 errors, 0 warnings).
- `npx tsc --noEmit`: Clean (0 errors).
- `npx vitest run tests/server.test.ts`: 16 tests passed (0 failed).

---
Settlement Wallet: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:bounty-52-nonce-reaper-lifecycle",
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

        # Post comment on issue #52
        issue_comment = f"""Hello @SUSU-LABS maintainers,

We have resolved issue #52 in PR #{pr_number}: {pr_url}

### Summary of Resolution:
- Added explicit opt-in for background nonce reaping (`enableNonceReaping: true` / `reapNonces: true`) in `BuildServerOptions`, enabled in `src/index.ts` for production, ensuring tests never spawn background timers by default.
- Tied the reaper interval timer to the Fastify server lifecycle via an `onClose` hook that clears the interval with `clearInterval`.
- Added lifecycle tests in `tests/server.test.ts` asserting no interval runs without opt-in and that closing the server cancels the interval and stops subsequent ticks.
- All tests pass, TypeScript compiler is clean, and ESLint is clean.

We remain at your service if you would like any adjustments to naming or tests!

Settlement Wallet: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`"""

        comment_payload = {"body": issue_comment}
        comment_req = urllib.request.Request(
            "https://api.github.com/repos/SUSU-LABS/susu-api/issues/52/comments",
            data=json.dumps(comment_payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(comment_req) as c_resp:
            print("Comment posted on Issue #52 successfully!")

except Exception as e:
    if hasattr(e, "read"):
        print("Error:", e.read().decode("utf-8"))
    else:
        print("Error:", e)
