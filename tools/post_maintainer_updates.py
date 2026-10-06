#!/usr/bin/env python3
"""
Post Maintainer Updates & Claim Triggers (tools/post_maintainer_updates.py)
Standard-library compliant script to post professional settlement inquiries and claim reminders.
"""

import os
import json
import urllib.request
import urllib.error

def load_env():
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars

env_vars = load_env()
TOKEN = env_vars.get("GITHUB_TOKEN", "").strip()
WALLET = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"

def post_comment(repo: str, issue_number: int, body: str):
    if not TOKEN:
        print(f"[!] No GITHUB_TOKEN available. Skipping comment on {repo}#{issue_number}")
        return False

    # REGLA DE ORO #4: Verificación estricta e inviolable de la Wallet de liquidación
    if WALLET not in body:
        raise ValueError(f"[CRITICAL ERROR] Payout wallet {WALLET} missing from comment body for {repo}#{issue_number}!")

    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    payload = json.dumps({"body": body}).encode('utf-8')
    headers = {
        "Authorization": f"token {TOKEN}",
        "User-Agent": "BountyHunterAI-PoliteSubmission/2.0 (dextermos-dev)",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"[+] Comment posted successfully on {repo}#{issue_number} (HTTP {resp.status})")
            return True
    except urllib.error.HTTPError as e:
        print(f"[-] HTTP Error {e.code} posting to {repo}#{issue_number}: {e.read().decode()}")
        return False
    except Exception as e:
        print(f"[-] Error posting to {repo}#{issue_number}: {str(e)}")
        return False

if __name__ == '__main__':
    print("=== CLAIM & SETTLEMENT DISPATCH ENGINE ===")
    
    # 1. Claim comment on merged PR #127
    comment_127 = f"""@scarface-dev1 Thank you for reviewing and merging the PR to main! 🚀

For the bounty escrow settlement and reward distribution, the verified payout address is:
- **Payout Wallet (EVM / Base / Stellar / Solana)**: `{WALLET}`

Looking forward to continuing to contribute to the Pay-Per-Token LLM Gateway!"""

    post_comment("mallonepay/pay-per-token-llm-gateway", 127, comment_127)
    
    # 2. Status update on Gibwork #177
    comment_177 = f"""Hello @gibwork team!

PR #208 has been updated with full landing page modernization, Clerk OAuth clarifications, and mobile indicators:
👉 https://github.com/gibwork/gibwork-website/pull/208

Ready for final review and merge!
- **Payout Wallet (EVM / Base / Solana)**: `{WALLET}`"""

    post_comment("gibwork/gibwork-website", 177, comment_177)
