#!/usr/bin/env python3
"""
Courteous Follow-Up Dispatcher (tools/send_courteous_followups.py)
Posts respectful, polite, and professional inquiries on mature PRs and issues.
Mandatory Invariant: Settlement Wallet 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20 included in all payloads.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
WALLET = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"

if not TOKEN:
    print("[!] Error: GITHUB_TOKEN not found in environment.")
    sys.exit(1)

def post_comment(repo: str, issue_number: int, body: str, label: str):
    # Rule 4: Mandatory check
    if WALLET not in body:
        raise ValueError(f"CRITICAL: Settlement Wallet {WALLET} is missing from comment for {repo}#{issue_number}!")

    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"token {TOKEN}",
        "User-Agent": "BountyHunterAI-CourteousFollowup/2.0 (@dextermos-dev)",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    payload = json.dumps({"body": body}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    print(f"[*] Enviando recordatorio cortés a {repo}#{issue_number} ({label})...")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            comment_url = data.get("html_url")
            print(f"  [+] Éxito ({resp.status}): {comment_url}")
            return comment_url
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")[:250]
        print(f"  [-] Error HTTP {e.code} en {repo}#{issue_number}: {err_msg}")
        return None
    except Exception as e:
        print(f"  [-] Error inesperado en {repo}#{issue_number}: {e}")
        return None

def main():
    results = {}

    # 1. MallonePay PR #127 ($800 USDC - Merged)
    mallone_body = f"""Hi @scarface-dev1! Hope you are having a wonderful week.

Following up gently on PR #127 (*"Integrate Soroban credit-escrow contract for token gateway"*), which was merged into main and resolved Issue #5. We're very happy to see the Soroban credit-escrow contract active in the project!

Whenever you have a moment to process the $800 USDC bounty disbursement, could you please let us know the status or if you need any additional information from our side?

- **Settlement Wallet (EVM / Base / Ethereum / Arbitrum):** `{WALLET}`
- **Preferred Asset:** USDC

*(Note: If your escrow or treasury prefers a native Stellar G-address instead of Base/EVM, please just let us know and we will be delighted to provide it).*

Thank you again for the opportunity to contribute to MallonePay!
"""
    results["mallonepay_pr127"] = post_comment("mallonepay/pay-per-token-llm-gateway", 127, mallone_body, "MallonePay $800 USDC PR #127")
    time.sleep(2)

    # 2. Spectral-Finance/lux PR #969 (Hyperliquid - $900 USD)
    spectral_969_body = f"""Hi @Spectral-Finance team! 👋

Hope all is going well. Just checking in politely to see if there is any feedback or additional test cases you'd like us to run on this PR (#969 - Hyperliquid Integration and Perpetual Trading).

The implementation covers the full perpetual trading flow with complete unit tests and mock verifications. We remain fully available to address any questions or adjustments needed to get this merged.

- **Settlement Wallet:** `{WALLET}`
- **Preferred Asset:** USDC

Thank you very much for your time and review!
"""
    results["spectral_pr969"] = post_comment("Spectral-Finance/lux", 969, spectral_969_body, "Spectral Hyperliquid $900 PR #969")
    time.sleep(2)

    # 3. Spectral-Finance/lux PR #966 (Auth Multi-session - $1,000 USD)
    spectral_966_body = f"""Hi @Spectral-Finance team! 👋

Checking in respectfully to see if the team has had a chance to review PR #966 (Auth & Multi-session management).

All components and session lifecycle handlers are fully implemented and verified. Please let us know if any tweaks or further refinements are needed.

- **Settlement Wallet:** `{WALLET}`
- **Preferred Asset:** USDC

Thank you for your continuous guidance and review!
"""
    results["spectral_pr966"] = post_comment("Spectral-Finance/lux", 966, spectral_966_body, "Spectral Auth $1,000 PR #966")
    time.sleep(2)

    # 4. Gibwork Website PR #208 ($300 USDC)
    gibwork_body = f"""Hi @gibwork team! 👋

Hope you're doing great. Friendly check-in regarding PR #208 (*"Modernize landing page with mobile app badges and delivery status"*).

Everything is ready and tested; whenever a team member has a moment to authorize the Vercel deployment preview, we'd appreciate any feedback or suggestions.

- **Settlement Wallet:** `{WALLET}`
- **Preferred Asset:** USDC

Thanks so much for building Gibwork!
"""
    results["gibwork_pr208"] = post_comment("gibwork/gibwork-website", 208, gibwork_body, "Gibwork $300 USDC PR #208")

    print("\n=== RESUMEN DE PUBLICACIONES ===")
    for k, v in results.items():
        print(f"  {k}: {v or 'FALLÓ'}")

if __name__ == "__main__":
    main()
