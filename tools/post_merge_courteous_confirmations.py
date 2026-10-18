#!/usr/bin/env python3
"""
Post courteous confirmation messages on our merged PRs in Parabola-org/parabola.
"""

import os
import sys
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

prs = [
    {
        "num": 99,
        "issue": 19,
        "bounty": "$45 USDC",
        "title": "Validate input to bytes32ToStellarAddress"
    },
    {
        "num": 100,
        "issue": 20,
        "bounty": "$45 USDC",
        "title": "Export convertPrecision and add 6↔7 decimal round-trip tests"
    },
    {
        "num": 101,
        "issue": 1,
        "bounty": "$105 USDC",
        "title": "Preserve burnTxHash when Stellar confirmation polling hits transient RPC errors"
    }
]

for p in prs:
    num = p["num"]
    body = f"""Thank you @Abdul-dev-creator for reviewing and merging this PR! 🎉

We are delighted to contribute to Parabola and help make the Arc ↔ Stellar USDC corridor as robust and reliable as possible.

For the allocated bounty settlement ({p['bounty']}) for Issue #{p['issue']}:
- **Settlement Wallet (USDC / Base L2 / EVM):** `{wallet}`

Please let us know if any further details or verification steps are needed from our side. We are excited to continue contributing to upcoming roadmap milestones and open issues! 🙌"""

    url = f"https://api.github.com/repos/Parabola-org/parabola/issues/{num}/comments"
    req = urllib.request.Request(url, data=json.dumps({"body": body}).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"Posted comment on PR #{num}: {data.get('html_url')}")
    except Exception as e:
        print(f"Error posting comment on PR #{num}: {e}")
