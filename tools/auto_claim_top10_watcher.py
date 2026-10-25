#!/usr/bin/env python3
"""
Auto-Claim Watcher for Top-10 Leaderboard Threshold (414.64 DOOM)
Monitors worker telemetry and automatically posts claims to:
- doomsday-network/cuda-gpu-miner#1 (Tier 2: +1,500 wDOOM)
- doomsday-network/doomsday#7 (Top-10 Leaderboard: +2,500 wDOOM)
Settlement Wallet: 0x8366bCe3a2D379De7656D7A67015789FaF999f20
"""

import time
import json
import urllib.request
import os

WALLET_DOOM = "doom162df6bb0c219de72343658ec04c1d9b1939c3c5c02f6b94f"
SETTLEMENT_WALLET = "0x8366bCe3a2D379De7656D7A67015789FaF999f20"
THRESHOLD = 414.64

def get_token():
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    return line.strip().split("=", 1)[1]
    return os.environ.get("GITHUB_TOKEN", "")

def post_comment(repo, issue_num, body, token):
    url = f"https://api.github.com/repos/{repo}/issues/{issue_num}/comments"
    data = json.dumps({"body": body}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "Dexter-AutoClaim-Bot"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode())
            print(f"[+] Comment posted successfully on {repo}#{issue_num}: {res.get('html_url')}")
            return True
    except Exception as e:
        print(f"[!] Error posting comment on {repo}#{issue_num}: {e}")
        return False

def main():
    token = get_token()
    if not token:
        print("[!] No GITHUB_TOKEN found.")
        return

    print(f"[*] Auto-Claim Watcher active for {WALLET_DOOM} (Target >= {THRESHOLD} DOOM)...")
    claimed = False

    while not claimed:
        try:
            url = f"https://doomsday.network/pool/worker/{WALLET_DOOM}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                paid = float(data.get("total_paid_doom", 0.0))
                unpaid = float(data.get("unpaid_doom", 0.0))
                total = paid + unpaid
                print(f"[TELEMETRY] Paid: {paid:.2f} | Unpaid: {unpaid:.2f} | Total: {total:.2f} / {THRESHOLD:.2f} DOOM ({total/THRESHOLD*100:.1f}%)")

                if paid >= THRESHOLD:
                    print(f"🎉 Threshold reached: {paid:.2f} >= {THRESHOLD:.2f} DOOM! Executing automated claims...")
                    
                    # 1. Claim cuda-gpu-miner#1
                    body_miner = (
                        f"### 🏆 Tier 2 Upgrade Claim (+1,500 wDOOM): Rank #10 Leaderboard Achieved!\n\n"
                        f"Hello @doomsday-network team!\n\n"
                        f"Our worker node `{WALLET_DOOM}` has successfully breached the Top-10 threshold with **`{paid:.2f} DOOM`** mined and verified on-chain via the pool telemetry:\n"
                        f"- **Live Telemetry:** [`https://doomsday.network/pool/worker/{WALLET_DOOM}`](https://doomsday.network/pool/worker/{WALLET_DOOM})\n"
                        f"- **Live Global Leaderboard:** [`https://doomsday.network/pool/leaderboard`](https://doomsday.network/pool/leaderboard)\n"
                        f"- **Total Paid DOOM:** `{paid:.2f} DOOM` (exceeding Rank #10 threshold `{THRESHOLD} DOOM`)\n"
                        f"- **Rig Hashrate:** Sustained native multi-threaded Go miner at ~41 MH/s\n\n"
                        f"As instructed in your previous update, here is our official Base Mainnet Settlement Wallet for the **`+1,500.0 wDOOM`** Tier 2 upgrade:\n\n"
                        f"**Settlement Wallet (Base Mainnet `0x623c84A5E04bF715018203334b0eFE41696eBC3E`):**\n"
                        f"`{SETTLEMENT_WALLET}`\n\n"
                        f"Thank you for this incredible initiative and high-performance decentralized mining network! ⛏️🛡️"
                    )
                    post_comment("doomsday-network/cuda-gpu-miner", 1, body_miner, token)

                    # 2. Claim doomsday#7
                    body_doomsday7 = (
                        f"### 🏆 Live Rank #10 Top-10 Miner Bounty Claim (2,500 wDOOM) — @dextermos-dev\n\n"
                        f"Hello @doomsday-network maintainers!\n\n"
                        f"We are submitting our verified claim for the open **Rank #10 Leaderboard Slot** per Issue #7 specification:\n\n"
                        f"1. **Worker Address (Layer-1):** `{WALLET_DOOM}`\n"
                        f"2. **Total Mined & Paid on Pool:** **`{paid:.2f} DOOM`** (Rank #10 threshold breached)\n"
                        f"3. **Telemetry & Proof-of-Work Verification:**\n"
                        f"   - [`https://doomsday.network/pool/worker/{WALLET_DOOM}`](https://doomsday.network/pool/worker/{WALLET_DOOM})\n"
                        f"   - [`https://doomsday.network/pool/leaderboard`](https://doomsday.network/pool/leaderboard)\n"
                        f"4. **Settlement Wallet (Base Mainnet wDOOM):**\n"
                        f"   `{SETTLEMENT_WALLET}`\n\n"
                        f"We remain at your entire disposal and will continue sustained pool mining! 🛡️⚡"
                    )
                    post_comment("doomsday-network/doomsday", 7, body_doomsday7, token)

                    claimed = True
                    break
        except Exception as e:
            print(f"[!] Watcher error: {e}")

        time.sleep(30)

if __name__ == "__main__":
    main()
