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

title = "fix(server): run notification sweeper on lifecycle-managed interval when pg_cron is unavailable (Fixes #57)"
body = """## Summary

Fixes #57 by wiring `createNotificationSweeper(getDb()).sweep()` to a lifecycle-managed periodic interval in `src/server.ts`, ensuring that notification derivation runs reliably as an in-process housekeeping fallback on databases where `pg_cron` is absent or untrusted.

### Problem
Previously, notification derivation depended entirely on `pg_cron` scheduling (`drizzle/0006_notification_schedule.sql:208-231`). When `pg_cron` is absent (which the migration deliberately tolerates via `to_regclass('cron.job') is null`), the `derive_notifications` function was created but never scheduled, leaving users without any notifications and the service without an application fallback.

### Solution
1. **Server Lifecycle Management (`src/server.ts`)**:
   - Added `notificationSweeper?: NotificationSweeper`, `enableNotificationSweep?: boolean`, and `notificationSweepIntervalMs?: number` to `BuildServerOptions`.
   - Implemented `startNotificationSweep(sweeper, log, intervalMs)` defaulting to 60 seconds (`DEFAULT_NOTIFICATION_SWEEP_INTERVAL_MS`), using `unref()` so housekeeping never keeps the node process artificially alive.
   - Tied to Fastify server lifecycle: registered an `onClose` hook to clear the interval timer via `clearInterval(sweepTimer)`.
2. **Production Startup (`src/index.ts`)**:
   - Enabled the fallback sweeper for production deployment: `buildServer({ enableNotificationSweep: true })`.
3. **Comprehensive Unit & Lifecycle Testing (`tests/server.test.ts`)**:
   - Proved that `startNotificationSweep` runs sweeps periodically on fake timer intervals.
   - Verified that errors from unreachable database connections are caught, logged as warnings (`notification_sweep_failed`), and do not crash or abort subsequent scheduled ticks.
   - Verified that successful sweeps with derived notifications or examined events are logged with details (`notification_sweep`).
   - Verified that `app.close()` clears the interval timer and stops all subsequent sweep ticks.

### Verification
- `npm run lint`: Clean (0 errors, 0 warnings).
- `npx tsc --noEmit`: Clean (0 errors).
- `npx vitest run tests/server.test.ts`: 18 tests passed across all suites (0 failed).

---
**Settlement Wallet (USDC / Base L2 / EVM):**
`0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:bounty-57-notification-sweeper-fallback",
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

        # Post courteous comment on Issue #57
        comment_body = f"""Hello @SUSU-LABS maintainers,

We have resolved issue #57 in PR #{pr_number}: {pr_url}

### Summary of Resolution:
- Wired `createNotificationSweeper(getDb()).sweep()` to a lifecycle-managed timer (`startNotificationSweep`) running every 60s in `src/server.ts` when enabled or in production (`src/index.ts`).
- Added Fastify `onClose` hook to cleanly clear the interval (`clearInterval(sweepTimer)`).
- Logged structured events (`notification_sweep` / `notification_sweep_failed`) without crashing on transient failures.
- Added 4 comprehensive unit and lifecycle tests in `tests/server.test.ts` verifying scheduling, resilience, logging, and timer cleanup on `app.close()`.

**Settlement Wallet (USDC / Base L2 / EVM):**
`0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`

We remain fully at your disposal for any adjustments or additional test cases you may need. Thank you! 🙌"""

        comment_req = urllib.request.Request(
            "https://api.github.com/repos/SUSU-LABS/susu-api/issues/57/comments",
            data=json.dumps({"body": comment_body}).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(comment_req) as c_resp:
            c_res = json.loads(c_resp.read().decode("utf-8"))
            print(f"Posted comment on Issue #57: {c_res.get('html_url')}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
