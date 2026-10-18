#!/usr/bin/env python3
"""
Inspect closed PRs and issues to see what was merged, who merged it, and which PRs won the bounties!
"""

import os
import sys
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN", "").strip()
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "dextermos-dev"
}

def get_json(url):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

print("=== 1. CHECKING OUR PRs (#99, #100, #101) ===")
for num in [99, 100, 101]:
    pr = get_json(f"https://api.github.com/repos/Parabola-org/parabola/pulls/{num}")
    if pr:
        print(f"PR #{num}: state={pr.get('state')}, merged={pr.get('merged')}, merged_at={pr.get('merged_at')}")
        if pr.get('merged'):
            print(f"  🎉 MERGED! By: {pr.get('merged_by', {}).get('login')}")
        elif pr.get('state') == 'closed':
            print(f"  CLOSED WITHOUT MERGE. Closed at: {pr.get('closed_at')}")

print("\n=== 2. RECENT MERGED PRs IN PARABOLA ===")
closed_prs = get_json("https://api.github.com/repos/Parabola-org/parabola/pulls?state=closed&per_page=30")
if closed_prs:
    print(f"Total closed PRs returned: {len(closed_prs)}")
    for p in closed_prs:
        merged = p.get('merged_at') is not None
        title = p.get('title')
        num = p.get('number')
        user = p.get('user', {}).get('login')
        merged_by = p.get('merged_by', {}).get('login') if merged else "N/A"
        print(f"PR #{num:3d} | merged={merged} | by @{user} (merged_by @{merged_by}) | {title}")

print("\n=== 3. CHECKING CLOSED ISSUES DETAILS (#1, #19, #20, #4, etc.) ===")
for num in [1, 19, 20, 4]:
    iss = get_json(f"https://api.github.com/repos/Parabola-org/parabola/issues/{num}")
    if iss:
        print(f"\nIssue #{num}: {iss.get('title')}")
        print(f"State: {iss.get('state')} | Closed at: {iss.get('closed_at')}")
        # Check timeline/events
        events = get_json(f"https://api.github.com/repos/Parabola-org/parabola/issues/{num}/events")
        if events:
            for ev in events:
                event_name = ev.get('event')
                actor = ev.get('actor', {}).get('login')
                created = ev.get('created_at')
                commit_id = ev.get('commit_id')
                print(f"  Event: {event_name} by @{actor} at {created} (commit: {commit_id[:8] if commit_id else 'None'})")

print("\n=== 4. RECENT COMMITS ON MAIN IN PARABOLA ===")
commits = get_json("https://api.github.com/repos/Parabola-org/parabola/commits?per_page=15")
if commits:
    for c in commits:
        sha = c.get('sha')[:8]
        msg = c.get('commit', {}).get('message', '').split('\n')[0]
        author = c.get('author', {}).get('login')
        date = c.get('commit', {}).get('author', {}).get('date')
        print(f"Commit {sha} by @{author} at {date}: {msg}")
