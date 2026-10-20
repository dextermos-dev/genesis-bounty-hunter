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

title = "fix(config): validate STELLAR_NETWORK_PASSPHRASE against STELLAR_NETWORK (Fixes #46)"
body = """## Summary

Fixes #46 by enforcing consistency between `STELLAR_NETWORK` and `STELLAR_NETWORK_PASSPHRASE` in `loadConfig`, and removing misleading literal quotes from `STELLAR_NETWORK_PASSPHRASE` in `scripts/deploy-indexer.sh`.

### Problem
Previously, `STELLAR_NETWORK_PASSPHRASE` was required and parsed into `config.networkPassphrase` but was never validated against `STELLAR_NETWORK`. Additionally, `scripts/deploy-indexer.sh:139-140` wrapped the value in literal quotes `"%s"` (unlike every other secret), which caused the secret stored in Supabase Vault to contain quote characters.

### Solution
1. **Network Passphrase Validation (`supabase/functions/_shared/config.ts`)**:
   - Defined canonical `STELLAR_NETWORK_PASSPHRASES` mapping for `testnet`, `mainnet`, and `local`.
   - In `loadConfig`, validated that `STELLAR_NETWORK_PASSPHRASE` matches the canonical passphrase for the specified `STELLAR_NETWORK`, rejecting mismatched combinations with an explicit error message.
2. **Deploy Script Fix (`scripts/deploy-indexer.sh`)**:
   - Emitted `STELLAR_NETWORK_PASSPHRASE=%s\n` without literal quotes, matching all other secrets.
3. **Test Coverage (`tests/config_test.ts`)**:
   - Added unit tests asserting that mismatched network/passphrase pairs are rejected.
   - Added unit tests asserting that matching network/passphrase pairs for `testnet`, `mainnet`, and `local` are accepted.

### Verification
- `deno task lint`: Clean (0 problems across 41 files).
- `deno task check`: Clean.
- `deno test tests/config_test.ts`: 16 tests passed (0 failed).

---
Settlement Wallet: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:bounty-46-validate-stellar-passphrase",
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
        pr_number = res.get("number")
        pr_url = res.get("html_url")
        print(f"PR Created: #{pr_number} -> {pr_url}")

        # Post comment on issue #46
        issue_comment = f"""Hello @SUSU-LABS maintainers,

We have resolved issue #46 in PR #{pr_number}: {pr_url}

### Summary of Resolution:
- Enforced canonical consistency between `STELLAR_NETWORK` and `STELLAR_NETWORK_PASSPHRASE` in `loadConfig`, rejecting mismatched combinations.
- Fixed `scripts/deploy-indexer.sh` to emit `STELLAR_NETWORK_PASSPHRASE` without literal quotes.
- Added comprehensive unit tests in `tests/config_test.ts` covering validation for `testnet`, `mainnet`, and `local`.
- All tests pass, type checks pass, and Deno lint is clean.

We remain at your service if you would like any adjustments to code style or tests!

Settlement Wallet: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`"""

        comment_payload = {"body": issue_comment}
        comment_req = urllib.request.Request(
            "https://api.github.com/repos/SUSU-LABS/susu-indexer/issues/46/comments",
            data=json.dumps(comment_payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(comment_req) as c_resp:
            print("Comment posted on Issue #46 successfully!")

except Exception as e:
    if hasattr(e, "read"):
        print("Error:", e.read().decode("utf-8"))
    else:
        print("Error:", e)
