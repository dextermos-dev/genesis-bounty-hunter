"""
Sentinel Watchdog & Rapid Opportunity Hunter
Automated periodic monitor for:
- Incoming USDC on-chain settlements on Base L2 (0x8366bCe3a2D379De7656D7A67015789FaF999f20)
- Unassigned fresh issues in target high-yield repositories
- Review comments / approvals on active PRs
- Dashboard synchronization
"""

import os
import json
import urllib.request
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get('GITHUB_TOKEN')
WALLET = "0x8366bCe3a2D379De7656D7A67015789FaF999f20"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
BASE_RPC = "https://mainnet.base.org"

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Dextermos-Bounty-Hunter'
}


def check_onchain_balance():
    data = {
        'jsonrpc': '2.0',
        'method': 'eth_call',
        'params': [{'to': USDC_BASE, 'data': '0x70a08231000000000000000000000000' + WALLET[2:]}, 'latest'],
        'id': 1
    }
    req = urllib.request.Request(
        BASE_RPC,
        data=json.dumps(data).encode(),
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode())
            bal = int(res['result'], 16) / 1e6
            return bal
    except Exception as e:
        print(f"Error checking balance: {e}")
        return None


def scan_fresh_issues(repos):
    fresh = []
    for r in repos:
        url = f"https://api.github.com/repos/{r}/issues?state=open&sort=created&direction=desc&per_page=5"
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req) as resp:
                issues = json.loads(resp.read().decode())
                for i in issues:
                    if 'pull_request' not in i and i.get('assignee') is None:
                        fresh.append({
                            'repo': r,
                            'number': i['number'],
                            'title': i['title'],
                            'url': i['html_url'],
                            'created_at': i['created_at']
                        })
        except Exception as e:
            print(f"Error scanning {r}: {e}")
    return fresh


def scan_unread_notifications():
    url = "https://api.github.com/notifications?all=false&per_page=20"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            notifs = json.loads(resp.read().decode())
            return notifs
    except Exception as e:
        print(f"Error checking notifications: {e}")
        return []


def run_watchdog():
    print(f"=== Sentinel Watchdog Run: {datetime.now(timezone.utc).isoformat()} ===")
    
    # 1. Check Balance
    bal = check_onchain_balance()
    print(f"Base L2 USDC Balance: {bal} USDC (Wallet: {WALLET})")
    
    # 2. Check Fresh Issues
    target_repos = [
        "limitlessprojects/Go-Hybrid",
        "Chain-Love/chain-love",
        "DevNiola/Prism",
        "Parabola-org/parabola"
    ]
    fresh_issues = scan_fresh_issues(target_repos)
    print(f"Fresh Unassigned Issues found: {len(fresh_issues)}")
    for f in fresh_issues:
        print(f"  - [{f['repo']}] #{f['number']}: {f['title']} ({f['url']})")
        
    # 3. Check Notifications
    notifs = scan_unread_notifications()
    print(f"Unread Notifications count: {len(notifs)}")
    
    # 4. Refresh Dashboard
    dash_path = "dashboard/data.json"
    if os.path.exists(dash_path):
        with open(dash_path, 'r') as f:
            d = json.load(f)
        d['last_updated'] = datetime.now(timezone.utc).isoformat()
        if bal is not None:
            d['settlement_wallet_balance_usdc'] = bal
        with open(dash_path, 'w') as f:
            json.dump(d, f, indent=2)
        print("Dashboard timestamp refreshed successfully.")


if __name__ == '__main__':
    run_watchdog()
