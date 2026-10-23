import os
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN", "").strip()
headers = {
    "Authorization": f"token {token}",
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
    "Accept": "application/vnd.github.v3+json"
}

body = """Hi @Abdul-dev-creator! 👋 Hope you are having a productive week.

First of all, thank you once again for your review and for merging our contributions across Parabola (PRs #99, #100, #101, #104, #109, #115, and #116). We loved working on the Arc ↔ Stellar USDC corridor and ensuring the test suites and edge cases were rock solid.

We noticed the community follow-ups on the upcoming batch settlement, so we wanted to gently consolidate our settlement information to make disbursement as easy and frictionless as possible on your end:

- **Settlement Wallet (USDC / Base L2 / EVM):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
- **Consolidated PR Batch:**
  - #99 ($45 USDC) — Validate 32-byte hex input
  - #100 ($45 USDC) — Decimal precision conversion
  - #101 ($105 USDC) — Transient RPC timeout preservation
  - #104 ($105 USDC) — Iris transient attestation tolerance
  - #109 ($125 USDC) — Structured progress callbacks
  - #115 ($60 USDC) — Testnet smoke hardening
  - #116 ($125 USDC) — AbortSignal support across transfer & burn
  - **Batch Total:** $710.00 USDC

Please let us know if you need any additional receipts, verification, or tests from our side. We remain at your full disposal whenever you need further improvements or maintenance on the SDK! 🙏✨"""

payload = json.dumps({"body": body}).encode("utf-8")
url = "https://api.github.com/repos/Parabola-org/parabola/issues/comments/6333083322"

req = urllib.request.Request(url, data=payload, headers=headers, method="PATCH")
with urllib.request.urlopen(req) as resp:
    data = json.load(resp)
    print("PATCH SUCCESS! Updated body:")
    print(data.get("body"))
