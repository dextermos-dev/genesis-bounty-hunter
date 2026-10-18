#!/usr/bin/env python3
"""
Inspect maintainer comments, payout instructions, and repository announcements.
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

# Check Abdul-dev-creator's recent comments in the repo
print("=== 1. ABDUL-DEV-CREATOR'S COMMENTS IN THE REPO ===")
recent_comments = get_json("https://api.github.com/repos/Parabola-org/parabola/issues/comments?sort=updated&direction=desc&per_page=100")
if recent_comments:
    abdul_comments = [c for c in recent_comments if c.get("user", {}).get("login") == "Abdul-dev-creator"]
    print(f"Found {len(abdul_comments)} comments by @Abdul-dev-creator:")
    for c in abdul_comments:
        issue_url = c.get("issue_url", "")
        print(f"On {issue_url} at {c.get('created_at')}:")
        print(c.get("body"))
        print("-" * 50)

# Check all comments on PR #99, #100, #101
print("\n=== 2. COMMENTS ON OUR MERGED PRs (#99, #100, #101) ===")
for num in [99, 100, 101]:
    comments = get_json(f"https://api.github.com/repos/Parabola-org/parabola/issues/{num}/comments")
    print(f"PR #{num} comments ({len(comments) if comments else 0}):")
    if comments:
        for c in comments:
            print(f"  @{c.get('user', {}).get('login')} at {c.get('created_at')}: {c.get('body')}")

# Check comments on Issues #19, #20, #1
print("\n=== 3. COMMENTS ON ISSUES #19, #20, #1 ===")
for num in [19, 20, 1]:
    comments = get_json(f"https://api.github.com/repos/Parabola-org/parabola/issues/{num}/comments")
    print(f"Issue #{num} comments ({len(comments) if comments else 0}):")
    if comments:
        for c in comments:
            print(f"  @{c.get('user', {}).get('login')} at {c.get('created_at')}: {c.get('body')}")

# Check README or CONTRIBUTING for payout details
print("\n=== 4. CHECKING README / CONTRIBUTING FOR BOUNTY PAYOUT DETAILS ===")
readme = get_json("https://api.github.com/repos/Parabola-org/parabola/contents/README.md")
if readme and "content" in readme:
    import base64
    content = base64.b64decode(readme["content"]).decode("utf-8")
    for line in content.split("\n"):
        if any(w in line.lower() for w in ["bounty", "payout", "reward", "claim", "usdc", "payment"]):
            print(f"README: {line}")
