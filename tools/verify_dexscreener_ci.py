import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "BountyHunterAI/2.0"
}

time.sleep(15)  # Wait for CI to run

for pr in [5738, 5739, 5740, 5741]:
    r = requests.get(f"https://api.github.com/repos/Chain-Love/chain-love/pulls/{pr}", headers=headers).json()
    head = r["head"]["sha"]
    cs = requests.get(f"https://api.github.com/repos/Chain-Love/chain-love/commits/{head}/check-runs", headers=headers).json()
    print(f"\nPR #{pr} ({r['title'][:40]}...): Head={head[:7]}")
    for c in cs.get("check_runs", []):
        print(f"  Check: {c['name']} | Status: {c['status']} | Conclusion: {c['conclusion']}")

