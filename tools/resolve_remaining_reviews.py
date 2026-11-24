import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "BountyHunterAI/2.0"
}

def update_file(repo, path, branch, message, transform_fn):
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"Error fetching {path} from {repo}@{branch}: {res.status_code} {res.text}")
        return False
    data = res.json()
    sha = data["sha"]
    content = base64.b64decode(data["content"]).decode("utf-8")
    
    new_content = transform_fn(content)
    if new_content == content:
        print(f"No changes needed for {path}")
        return True
        
    payload = {
        "message": message,
        "content": base64.b64encode(new_content.encode("utf-8")).decode("utf-8"),
        "sha": sha,
        "branch": branch
    }
    put_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    put_res = requests.put(put_url, headers=headers, json=payload)
    if put_res.status_code in [200, 201]:
        print(f"Successfully updated {path} on {branch} in {repo}!")
        return True
    else:
        print(f"Error pushing update to {path}: {put_res.status_code} {put_res.text}")
        return False

def post_comment(repo, pr_num, comment):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_num}/comments"
    res = requests.post(url, headers=headers, json={"body": comment})
    if res.status_code in [200, 201]:
        print(f"Comment posted on {repo}#{pr_num}")
    else:
        print(f"Error posting comment on {repo}#{pr_num}: {res.status_code} {res.text}")

print("--- 1. Resolving PR #5555 (Bubblemaps Arbitrum) ---")
# Bubblemaps requires availableApis="[]" override
def transform_arbitrum_bubblemaps(c):
    lines = c.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("bubblemaps-one,"):
            # Format: bubblemaps-one,,!offer:bubblemaps,"[""[Dashboard](https://v2.bubblemaps.io/arbitrum)""]",one,,,,"[]",,,,,
            # Let's ensure availableApis column has "[]"
            # Original: bubblemaps-one,,!offer:bubblemaps,"[""[Dashboard](https://v2.bubblemaps.io/arbitrum)""]",one,,,,,,,,,,
            # In Chain-Love CSV headers:
            # name,aliases,offers,documentationUrls,networkRelationship,supportedChainIds,contracts,languages,availableApis,...
            # Let's check headers
            pass
        new_lines.append(line)
    return "\n".join(new_lines)

# Let's inspect current content of PR #5555 and PR #5573 first
r5555 = requests.get("https://api.github.com/repos/dextermos-dev/chain-love/contents/listings/specific-networks/arbitrum/analytics.csv?ref=data/arbitrum-bubblemaps-analytics", headers=headers).json()
raw5555 = base64.b64decode(r5555["content"]).decode("utf-8")
print("Current 5555 content:\n", raw5555)

r5573 = requests.get("https://api.github.com/repos/dextermos-dev/chain-love/contents/listings/specific-networks/polygon/analytics.csv?ref=data/polygon-bubblemaps-analytics", headers=headers).json()
raw5573 = base64.b64decode(r5573["content"]).decode("utf-8")
print("Current 5573 content:\n", raw5573)

