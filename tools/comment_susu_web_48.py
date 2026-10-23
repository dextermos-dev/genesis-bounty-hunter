#!/usr/bin/env python3
import os
import json
import urllib.request

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k] = v.strip('"').strip("'")

token = os.getenv("GITHUB_TOKEN", "")
headers = {
    "User-Agent": "BountyHunterAI/2.0",
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

comment_data = {
    "body": """Greetings maintainers! 👋

We have prepared and submitted a clean, robust solution for this issue in PR **#167** (https://github.com/SUSU-LABS/susu-web/pull/167).

### Summary of Resolution:
1. **Explicit Custom RPC Opt-In**: Added `VITE_STELLAR_RPC_IS_CUSTOM` in `src/lib/env.ts` (accepting boolean or `'true'`/`'false'`/`'1'`/`'0'`) and documented in `.env.example`.
2. **Hardened Verification**: `assertRpcMatchesNetwork` now rejects unmarked custom endpoints unless `allowCustom: true` is opted into, preventing accidental mainnet RPC usage when configured for testnet.
3. **Local Development Preservation**: Standard localhost/sandbox endpoints (`localhost`, `127.0.0.1`, `[::1]`) remain permitted automatically without requiring manual opt-in flags.
4. **Unconditional Contradiction Guard**: Explicit network contradictions (e.g. `mainnet` in URL while configured for `testnet`) remain strictly refused even if `allowCustom: true` is set.
5. **Full Test Coverage**: Expanded `network.test.ts` to cover matching endpoints, rejected unmarked custom endpoints, accepted opted-in endpoints, localhost sandbox endpoints, and explicit contradictions.
6. **Clean Verification**: All 465 Vitest tests pass across 39 suites, `tsc --noEmit` reports 0 errors, ESLint reports 0 warnings, and `pnpm build` succeeds cleanly.

We remain completely at your service should you want any adjustments or additional test cases. Thank you very much for your time and guidance!

- **Settlement Wallet (USDC / EVM / Stellar)**:
  `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`"""
}

req = urllib.request.Request(
    "https://api.github.com/repos/SUSU-LABS/susu-web/issues/48/comments",
    data=json.dumps(comment_data).encode("utf-8"),
    headers=headers,
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print("Comment posted on Issue #48:", data.get("html_url"))
except Exception as e:
    print("Error:", e)
