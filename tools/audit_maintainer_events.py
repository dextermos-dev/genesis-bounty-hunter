#!/usr/bin/env python3
"""
Check all discussions, issues created by maintainers, and organization profile.
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

# Check organization details
print("=== 1. PARABOLA-ORG DETAILS ===")
org = get_json("https://api.github.com/orgs/Parabola-org")
if org:
    print("Org:", org.get("name"), "| Blog:", org.get("blog"), "| Email:", org.get("email"), "| Description:", org.get("description"))

# Check all repos in Parabola-org
print("\n=== 2. PARABOLA-ORG REPOSITORIES ===")
repos = get_json("https://api.github.com/orgs/Parabola-org/repos")
if repos:
    for r in repos:
        print(f"- {r.get('name')}: {r.get('description')} (stars: {r.get('stargazers_count')}, forks: {r.get('forks_count')})")

# Check all open and closed issues in Parabola
print("\n=== 3. ALL ISSUES CREATED OR UPDATED IN PARABOLA ===")
issues = get_json("https://api.github.com/repos/Parabola-org/parabola/issues?state=all&per_page=100")
if issues:
    print(f"Total issues/PRs: {len(issues)}")
    # Look for any issue that is NOT a bounty listing (e.g. payout, discussion, announcement)
    for i in issues:
        title = i.get("title", "")
        if not title.startswith("[Bounty:"):
            print(f"#{i.get('number')}: {title} (state: {i.get('state')}, user: {i.get('user', {}).get('login')})")

# Check if there are any comments by Abdul-dev-creator on merged PRs #99, #100, #101 or anywhere
print("\n=== 4. ABDUL-DEV-CREATOR EVENTS ===")
events = get_json("https://api.github.com/users/Abdul-dev-creator/events/public")
if events:
    print(f"Total public events for Abdul-dev-creator: {len(events)}")
    for ev in events[:15]:
        ev_type = ev.get("type")
        repo_name = ev.get("repo", {}).get("name")
        created = ev.get("created_at")
        payload = ev.get("payload", {})
        action = payload.get("action")
        print(f"- [{created}] {ev_type} ({action}) on {repo_name}")
        if ev_type == "IssueCommentEvent":
            print(f"  Comment: {payload.get('comment', {}).get('body')[:150]}")
        elif ev_type == "PullRequestReviewCommentEvent":
            print(f"  Review comment: {payload.get('comment', {}).get('body')[:150]}")
        elif ev_type == "PullRequestEvent":
            pr = payload.get("pull_request", {})
            print(f"  PR #{pr.get('number')}: {pr.get('title')} (merged: {pr.get('merged')})")
