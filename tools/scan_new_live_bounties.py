import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "BountyHunterAI/2.0"
}

# Search recent open issues labeled bounty, algora, or bountycaster created/updated in the last 7 days
queries = [
    'is:issue is:open label:bounty "USDC" in:body',
    'is:issue is:open "algora.io" "funded" in:body',
    'is:issue is:open "bountycaster" in:body',
    'is:issue is:open label:"good first issue" label:bounty'
]

found = []
for q in queries:
    url = f"https://api.github.com/search/issues?q={q}&sort=updated&order=desc&per_page=5"
    r = requests.get(url, headers=headers).json()
    items = r.get("items", [])
    print(f"Query '{q}': {len(items)} results")
    for it in items:
        repo = it.get("repository_url", "").replace("https://api.github.com/repos/", "")
        found.append({
            "repo": repo,
            "title": it.get("title"),
            "url": it.get("html_url"),
            "labels": [l.get("name") for l in it.get("labels", [])],
            "body_snippet": (it.get("body") or "")[:200].replace("\n", " ")
        })

print(f"\nTotal collected: {len(found)}")
seen = set()
for f in found:
    if f["url"] not in seen:
        seen.add(f["url"])
        print(f"\n[{f['repo']}] {f['title']}")
        print(f"URL: {f['url']}")
        print(f"Snippet: {f['body_snippet'][:140]}...")

