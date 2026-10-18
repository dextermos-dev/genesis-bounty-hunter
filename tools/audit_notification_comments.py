#!/usr/bin/env python3
import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN", "").strip()
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "dextermos-dev"
}

threads = [
    ("Spectral Lux Hyperliquid", "https://api.github.com/repos/Spectral-Finance/lux/issues/131/comments"),
    ("Spectral Lux Web3 Auth", "https://api.github.com/repos/Spectral-Finance/lux/issues/130/comments"),
    ("Superteam Earn Issue", "https://api.github.com/repos/SuperteamDAO/earn/issues/1739/comments"),
    ("Superteam Earn PR", "https://api.github.com/repos/SuperteamDAO/earn/pulls/1740/comments"),
    ("Superteam Earn PR Issue Comments", "https://api.github.com/repos/SuperteamDAO/earn/issues/1740/comments"),
]

for label, url in threads:
    print(f"\n=== {label} ===")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as r:
            comments = json.loads(r.read().decode())
            print(f"Total comments: {len(comments)}")
            for c in comments[-3:]:
                user = c.get("user", {}).get("login")
                body = c.get("body", "").replace("\r\n", "\n").strip()
                date = c.get("created_at")
                print(f"[{date}] @{user}:\n{body[:300]}\n---")
    except Exception as e:
        print(f"Error {label}: {e}")
