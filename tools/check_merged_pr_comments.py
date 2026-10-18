#!/usr/bin/env python3
"""
Check comments and reviews on all 10 merged PRs in Parabola.
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

merged_pr_numbers = [103, 102, 101, 100, 99, 98, 96, 94, 92, 43]

for num in merged_pr_numbers:
    req = urllib.request.Request(f"https://api.github.com/repos/Parabola-org/parabola/issues/{num}/comments", headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            comments = json.loads(r.read().decode())
            print(f"=== PR #{num} Comments ({len(comments)}) ===")
            for c in comments:
                print(f"  @{c['user']['login']} at {c['created_at']}:")
                print(f"    {c['body'][:200]}")
    except Exception as e:
        print(f"Error #{num}: {e}")

    req_reviews = urllib.request.Request(f"https://api.github.com/repos/Parabola-org/parabola/pulls/{num}/reviews", headers=headers)
    try:
        with urllib.request.urlopen(req_reviews) as r:
            reviews = json.loads(r.read().decode())
            if reviews:
                print(f"  Reviews ({len(reviews)}):")
                for rev in reviews:
                    print(f"    @{rev['user']['login']} ({rev['state']}): {rev.get('body')}")
    except Exception as e:
        pass
