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

title = "fix(alerts): do not treat in-flight pg_cron runs as failures (Fixes #42)"
body = """## Summary

Fixes #42 by updating `check_indexer_health` to match only terminal failures (`status = 'failed'`) in `cron.job_run_details`, preventing healthy in-flight executions (`status = 'running'`) from triggering spurious `failed_schedule` alerts.

### Problem
Previously in `supabase/migrations/20260914000000_indexer_alerts.sql:200` and `20261009000001_ledger_lag_alert.sql:150`, `check_indexer_health` queried `cron.job_run_details` with `where d.status <> 'succeeded' and d.start_time > v_now - failure_window`. Because `pg_cron` records `status = 'running'` for any job actively in progress, any scheduled task executing at check time (including long-running indexing sweeps and the health check itself) was recorded as a failure and opened a false-positive `failed_schedule` alert.

### Solution
1. **Migration (`supabase/migrations/20261020000000_inflight_cron_runs_not_failed.sql`)**:
   - Updated `public.check_indexer_health` condition 3 query to select strictly `where d.status = 'failed' and d.start_time > v_now - failure_window`.
   - Excluded in-flight (`running`) and completed (`succeeded`) executions.
2. **Automated Integration Tests (`tests/inflight_cron_test.ts`)**:
   - Verified against PGlite that:
     * An in-flight job with `status = 'running'` does not open a `failed_schedule` alert.
     * A succeeded job with `status = 'succeeded'` does not open a `failed_schedule` alert.
     * A job with terminal failure `status = 'failed'` does open a `failed_schedule` alert, preserving the failure count and newest error message.

### Verification
- `deno task lint`: Clean (0 problems across 42 files).
- `deno task check`: Clean.
- `deno task test`: 227 passed (0 failed).

---
**Settlement Wallet (USDC / Base L2 / EVM):**
`0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:bounty-42-exclude-inflight-cron-runs",
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

        # Post courteous comment on Issue #42
        comment_body = f"""Hello @SUSU-LABS maintainers,

We have resolved issue #42 in PR #{pr_number}: {pr_url}

### Summary of Resolution:
- Updated `check_indexer_health` via migration `supabase/migrations/20261020000000_inflight_cron_runs_not_failed.sql` to select strictly `where d.status = 'failed'`, filtering out in-flight `running` and `succeeded` runs.
- Added comprehensive PGlite integration tests in `tests/inflight_cron_test.ts` verifying that `running` jobs do not open false-positive `failed_schedule` alerts, while terminal `failed` runs open alerts with their return message.

**Settlement Wallet (USDC / Base L2 / EVM):**
`0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`

We remain fully at your service for any adjustments or additional test cases you may desire. Thank you! 🙌"""

        comment_req = urllib.request.Request(
            "https://api.github.com/repos/SUSU-LABS/susu-indexer/issues/42/comments",
            data=json.dumps({"body": comment_body}).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(comment_req) as c_resp:
            c_res = json.loads(c_resp.read().decode("utf-8"))
            print(f"Posted comment on Issue #42: {c_res.get('html_url')}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
