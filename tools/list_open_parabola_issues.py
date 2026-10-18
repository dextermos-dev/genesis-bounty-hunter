#!/usr/bin/env python3
"""
List all currently OPEN issues in Parabola-org/parabola.
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

req = urllib.request.Request("https://api.github.com/repos/Parabola-org/parabola/issues?state=open&per_page=100", headers=headers)
with urllib.request.urlopen(req) as r:
    items = json.loads(r.read().decode())

open_issues = [i for i in items if "pull_request" not in i]
print(f"Total OPEN issues: {len(open_issues)}")

for i in sorted(open_issues, key=lambda x: x["number"]):
    num = i["number"]
    title = i["title"]
    comments = i.get("comments", 0)
    print(f"Issue #{num:2d} ({comments:2d} comments): {title}")
