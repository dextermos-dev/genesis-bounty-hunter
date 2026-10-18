#!/usr/bin/env python3
"""
Audit all recent activity, comments, reviews, and events in Parabola-org/parabola.
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

print("=== 1. CHECKING NOTIFICATIONS ===")
notifs = get_json("https://api.github.com/notifications?all=true")
if notifs:
    parabola_notifs = [n for n in notifs if "parabola" in n.get("repository", {}).get("full_name", "").lower()]
    print(f"Total Parabola notifications: {len(parabola_notifs)}")
    for n in parabola_notifs:
        subj = n.get("subject", {})
        print(f"- [{n.get('reason')}] {subj.get('type')}: {subj.get('title')} (unread: {n.get('unread')})")
        print(f"  URL: {subj.get('url')}")
        print(f"  Latest comment: {subj.get('latest_comment_url')}")

print("\n=== 2. CHECKING OUR PRs (#99, #100, #101) ===")
for num in [99, 100, 101]:
    pr = get_json(f"https://api.github.com/repos/Parabola-org/parabola/pulls/{num}")
    if pr:
        print(f"\n--- PR #{num}: {pr.get('title')} ---")
        print(f"State: {pr.get('state')} | Merged: {pr.get('merged')}")
        print(f"Assignees: {[a.get('login') for a in pr.get('assignees', [])]}")
        print(f"Requested Reviewers: {[r.get('login') for r in pr.get('requested_reviewers', [])]}")
        
        # Check PR reviews
        reviews = get_json(f"https://api.github.com/repos/Parabola-org/parabola/pulls/{num}/reviews")
        if reviews:
            print(f"Reviews ({len(reviews)}):")
            for r in reviews:
                print(f"  Review from @{r.get('user', {}).get('login')} (state: {r.get('state')}):")
                print(f"    Body: {r.get('body')}")
        
        # Check PR comments (issue comments on PR)
        comments = get_json(f"https://api.github.com/repos/Parabola-org/parabola/issues/{num}/comments")
        if comments:
            print(f"PR comments ({len(comments)}):")
            for c in comments:
                print(f"  Comment by @{c.get('user', {}).get('login')} at {c.get('created_at')}:")
                print(f"    {c.get('body')}")

print("\n=== 3. CHECKING CORRESPONDING ISSUES (#19, #20, #1) ===")
for num in [19, 20, 1]:
    iss = get_json(f"https://api.github.com/repos/Parabola-org/parabola/issues/{num}")
    if iss:
        print(f"\n--- ISSUE #{num}: {iss.get('title')} ---")
        print(f"State: {iss.get('state')} | Assignees: {[a.get('login') for a in iss.get('assignees', [])]}")
        comments = get_json(f"https://api.github.com/repos/Parabola-org/parabola/issues/{num}/comments")
        if comments:
            print(f"Total comments: {len(comments)}")
            # Show last 5 comments
            for c in comments[-5:]:
                print(f"  [{c.get('created_at')}] @{c.get('user', {}).get('login')}:")
                body = c.get('body', '').strip()
                print(f"    {body[:250]}...")

print("\n=== 4. RECENT COMMENTS REPO-WIDE (LAST 30 COMMENTS IN PARABOLA) ===")
recent_comments = get_json("https://api.github.com/repos/Parabola-org/parabola/issues/comments?sort=updated&direction=desc&per_page=30")
if recent_comments:
    print(f"Retrieved {len(recent_comments)} recent comments:")
    for c in recent_comments[:20]:
        issue_url = c.get("issue_url", "")
        issue_num = issue_url.split("/")[-1] if "/" in issue_url else "?"
        user = c.get("user", {}).get("login")
        created = c.get("created_at")
        body = c.get("body", "").replace("\n", " ").strip()
        print(f"- Issue/PR #{issue_num} | @{user} at {created}:")
        print(f"    {body[:150]}")
