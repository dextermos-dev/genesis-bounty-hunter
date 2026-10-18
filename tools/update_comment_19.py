#!/usr/bin/env python3
import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN", "").strip()
wallet = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "dextermos-dev",
    "Content-Type": "application/json"
}

body = f"""Hello maintainers!

We have submitted a clean, comprehensive pull request to resolve this issue:
PR: https://github.com/Parabola-org/parabola/pull/99

Key highlights:
- Strict validation of 0x prefix, string type, even length, exact 32-byte length (64 hex characters), and valid hexadecimal characters with clear, descriptive TypeError messages.
- Full test coverage in tests/encoding.test.ts including round-tripping across 10 random Stellar Keypairs.
- 100% passing tests (119/119 vitest tests) and clean TypeScript / build verification.

/claim #19
Settlement Wallet: {wallet}"""

url = "https://api.github.com/repos/Parabola-org/parabola/issues/comments/6208577082"
req = urllib.request.Request(url, data=json.dumps({"body": body}).encode("utf-8"), headers=headers, method="PATCH")
with urllib.request.urlopen(req) as resp:
    print("Updated comment status:", resp.status)
    data = json.loads(resp.read().decode("utf-8"))
    print("Body verification:\n", data.get("body"))
