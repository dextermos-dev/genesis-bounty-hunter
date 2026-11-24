import os
import requests
import base64
import csv
import io
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "BountyHunterAI/2.0"
}

def fix_wallet_csv(network, branch):
    # Fetch file
    url = f"https://api.github.com/repos/dextermos-dev/chain-love/contents/listings/specific-networks/{network}/wallets.csv?ref={branch}"
    res = requests.get(url, headers=headers).json()
    sha = res["sha"]
    content = base64.b64decode(res["content"]).decode("utf-8")
    
    # Read rows using csv reader
    f = io.StringIO(content)
    reader = csv.reader(f)
    rows = list(reader)
    header = rows[0]
    
    native_idx = header.index("native")
    tokens_idx = header.index("tokensSupport")
    key_export_idx = header.index("keyExport")
    tendermint_idx = header.index("tendermint")
    
    print(f"\nFixing {network}: native is col {native_idx}, tokensSupport is col {tokens_idx}")
    
    new_rows = []
    for row in rows:
        if row and row[0] == "backpack":
            # ensure row has exact length of header
            while len(row) < len(header):
                row.append("")
            # Clear any accidental values
            row[key_export_idx] = ""
            row[tendermint_idx] = ""
            # Set correct values
            row[native_idx] = "FALSE"
            row[tokens_idx] = '["ERC-20","ERC-721"]'
        new_rows.append(row)
        
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    for r in new_rows:
        writer.writerow(r)
    
    new_csv = out.getvalue()
    
    payload = {
        "message": f"fix({network}): align CSV columns for Backpack native=FALSE and tokensSupport",
        "content": base64.b64encode(new_csv.encode("utf-8")).decode("utf-8"),
        "sha": sha,
        "branch": branch
    }
    put_url = f"https://api.github.com/repos/dextermos-dev/chain-love/contents/listings/specific-networks/{network}/wallets.csv"
    put_res = requests.put(put_url, headers=headers, json=payload)
    if put_res.status_code in [200, 201]:
        print(f"✅ Successfully pushed fix for {network} on {branch}!")
    else:
        print(f"❌ Error pushing to {network}: {put_res.status_code} {put_res.text}")

fix_wallet_csv("base", "data/base-backpack-wallet")
fix_wallet_csv("polygon", "data/polygon-backpack-wallet")

