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

print("=== 1. CHECKING GITHUB NOTIFICATIONS ===")
req = urllib.request.Request("https://api.github.com/notifications?all=true", headers=headers)
try:
    with urllib.request.urlopen(req) as r:
        notifs = json.loads(r.read().decode())
        print(f"Total notifications: {len(notifs)}")
        for n in notifs[:15]:
            repo = n.get("repository", {}).get("full_name")
            subj = n.get("subject", {})
            print(f"- [{n.get('reason')}] {subj.get('type')}: {subj.get('title')} ({repo}) - unread: {n.get('unread')}")
except Exception as e:
    print("Notifications error:", e)

print("\n=== 2. CHECKING CI RUNS FOR PARABOLA PRs #99, #100, #101 ===")
for pr_num in [99, 100, 101]:
    req = urllib.request.Request(f"https://api.github.com/repos/Parabola-org/parabola/pulls/{pr_num}", headers=headers)
    with urllib.request.urlopen(req) as r:
        pr_data = json.loads(r.read().decode())
        head_sha = pr_data["head"]["sha"]
        state = pr_data["state"]
        merged = pr_data["merged"]
        print(f"PR #{pr_num} ({state}, merged={merged}): head_sha={head_sha[:8]}")

    req_status = urllib.request.Request(f"https://api.github.com/repos/Parabola-org/parabola/commits/{head_sha}/check-runs", headers=headers)
    try:
        with urllib.request.urlopen(req_status) as r:
            check_data = json.loads(r.read().decode())
            runs = check_data.get("check_runs", [])
            print(f"  Check runs ({len(runs)}):")
            for run in runs:
                print(f"    - {run['name']}: {run['status']}, conclusion={run['conclusion']}")
    except Exception as e:
        print(f"  Check runs error: {e}")

print("\n=== 3. CHECKING COMMENTS ON RECENT PRs ===")
for pr_num in [99, 100, 101]:
    req = urllib.request.Request(f"https://api.github.com/repos/Parabola-org/parabola/issues/{pr_num}/comments", headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            comments = json.loads(r.read().decode())
            print(f"PR #{pr_num} comments count: {len(comments)}")
            for c in comments:
                user = c.get("user", {}).get("login")
                body = c.get("body", "").strip()[:100].replace("\n", " ")
                print(f"  - @{user}: {body}...")
    except Exception as e:
        print(f"  Error reading PR #{pr_num} comments: {e}")
