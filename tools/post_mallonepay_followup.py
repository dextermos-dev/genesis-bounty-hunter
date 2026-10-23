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

body = """Hi @scarface-dev1! 👋 Hope you are having a wonderful and productive week.

We wanted to touch base gently regarding PR #127 (*"Integrate Soroban credit-escrow contract for token gateway"*), which was reviewed and merged into main to resolve Issue #5 ($1,000.00 USDC).

We are re-verifying our official settlement details to make disbursement as straightforward and seamless as possible for your team:

- **Settlement Wallet (USDC / Base L2 / EVM / Stellar):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
- **Resolved Delivery:** Issue #5 / PR #127 ($1,000.00 USDC)

Please let us know if you require any additional information, testing, or verification steps from our side. We greatly appreciate your time and dedication to the gateway, and remain at your disposal for upcoming features and integrations! 🙏✨"""

payload = json.dumps({"body": body}).encode("utf-8")
url = "https://api.github.com/repos/mallonepay/pay-per-token-llm-gateway/issues/127/comments"

req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
with urllib.request.urlopen(req) as resp:
    data = json.load(resp)
    print("MALLONEPAY POST SUCCESS! Comment URL:", data.get("html_url"))
