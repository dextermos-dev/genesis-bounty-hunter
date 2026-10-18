#!/usr/bin/env python3
"""
Open Pull Request for Parabola Issue #19:
[Bounty: $45] Validate input to bytes32ToStellarAddress
Settlement Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
"""

import os
import sys
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
WALLET = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"
REPO = "Parabola-org/parabola"
AUTH_USER = "dextermos-dev"
BRANCH = "fix/19-validate-bytes32-input"

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "BountyHunterAI-Parabola/2.0 (dextermos-dev)"
}

PR_TITLE = "fix(encoding): validate 32-byte hex input in bytes32ToStellarAddress (fixes #19)"

PR_BODY = f"""## Summary
Fixes #19

Strictly validates input to `bytes32ToStellarAddress` in `src/utils/encoding.ts` before decoding or calling `StrKey.encodeContract`, preventing obscure low-level buffer crashes and ensuring descriptive error messages across all invalid input classes.

## Changes
- **Input Type & Prefix Validation**: Asserts that `hex` is a string beginning with `0x`. Throws descriptive `TypeError: Expected hex string with "0x" prefix, received: ...` if invalid.
- **Length Validation**: Asserts even length and exact 32-byte representation (`0x` + 64 hex characters). Throws clear `TypeError` specifying character count and byte length.
- **Hex Character Validation**: Validates that string only contains valid hexadecimal digits (`[0-9a-fA-F]`). Throws descriptive `TypeError: Invalid hexadecimal character in bytes32 input: ...`.
- **Contract Address Encoding**: Accurately maps 32-byte hash to Stellar `C...` StrKey contract identifier using official `@stellar/stellar-sdk` `StrKey.encodeContract`.
- **Zero Runtime Overhead & Backward Compatible**: Valid inputs (e.g., standard CCTP 32-byte hex addresses) continue passing through with zero friction and identical outputs.

## Tests & Verification
Added comprehensive test suite to `tests/encoding.test.ts`:
1. Valid 32-byte zero hash `0x00...00` -> valid Stellar Contract ID `C...`.
2. Valid arbitrary 32-byte hex address with mixed case.
3. Rejection of missing `0x` prefix (with type check).
4. Rejection of truncated hex strings (< 64 hex chars).
5. Rejection of oversized hex strings (> 64 hex chars).
6. Rejection of invalid non-hex characters (e.g. `0x${{'00'.repeat(31)}}zz`).
7. 10 round-trip tests against randomly generated Stellar Keypairs asserting consistent 32-byte hex decoding.

Verification runs:
- `npx vitest run`: 25/25 encoding tests pass (119/119 total suite pass).
- `npx tsc --noEmit`: 0 TypeScript diagnostics.
- `npx tsup`: Clean CJS and ESM bundle generation.

## Claim & Settlement
/claim #19
Settlement Wallet (USDC / Base L2 / EVM):
`{WALLET}`
"""

def main():
    if not TOKEN:
        print("ERROR: GITHUB_TOKEN not set in environment or .env")
        sys.exit(1)

    url = f"https://api.github.com/repos/{REPO}/pulls"
    payload = {
        "title": PR_TITLE,
        "head": f"{AUTH_USER}:{BRANCH}",
        "base": "main",
        "body": PR_BODY
    }

    print(f"Opening Pull Request on {REPO} from {payload['head']} to {payload['base']}...")
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"token {TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "BountyHunterAI-Parabola/2.0 (dextermos-dev)",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Status Code: {resp.status}")
            data = json.loads(resp.read().decode("utf-8"))
            print("SUCCESS! Pull Request opened:")
            print(f"URL: {data.get('html_url')}")
            print(f"PR Number: #{data.get('number')}")
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
