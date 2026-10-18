#!/usr/bin/env python3
"""
List all merged PRs in Parabola, their authors, issues they closed, and timestamps.
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

req = urllib.request.Request("https://api.github.com/repos/Parabola-org/parabola/pulls?state=closed&per_page=50", headers=headers)
with urllib.request.urlopen(req) as r:
    prs = json.loads(r.read().decode())

merged_prs = [p for p in prs if p.get("merged_at")]
print(f"Total merged PRs: {len(merged_prs)}")

for p in merged_prs:
    num = p["number"]
    title = p["title"]
    author = p["user"]["login"]
    merged_at = p["merged_at"]
    merged_by = p.get("merged_by", {}).get("login")
    print(f"PR #{num:3d} by @{author:20s} at {merged_at} (merged by @{merged_by})")
    print(f"       Title: {title}")
