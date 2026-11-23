import urllib.request
import json
from dotenv import dotenv_values

token = dotenv_values('.env').get('GITHUB_TOKEN')
headers = {
    'Authorization': f'token {token}',
    'User-Agent': 'BountyHunter',
    'Content-Type': 'application/json'
}

title = "data(optimism): add Bungee Exchange cross-chain bridge aggregator for Optimism"
body = """### Summary

This PR adds **Bungee Exchange** (`bungee-exchange-mainnet`) by **Socket** to `listings/specific-networks/optimism/bridges.csv`, inheriting canonical offer metadata from `!offer:bungee-exchange`:

- **Bungee Exchange**: High-speed multichain bridge aggregator and DEX routing infrastructure powered by Socket protocol, enabling seamless cross-chain swaps and native/ERC-20 transfers to and from OP Mainnet.
- **Official Bridge**: [`https://www.bungee.exchange/`](https://www.bungee.exchange/) (verified HTTP 200).
- **Official Documentation**: [`https://docs.socket.tech/`](https://docs.socket.tech/) (verified HTTP 200).

### Verification & Compliance
- **Sparse Row Inheritance**: Inherits canonical metadata (`provider`, `technology`, `assetTypes`, `availableApis`, `monitoringAndAnalytics`, `additionalFeatures`, `price=$0`, `decentralizationModel=Hybrid`, `tag`) from `references/offers/bridges.csv`.
- **Alphabetical Sorting**: Inserted in exact alphabetical order by slug (`axelar-optimism` -> `bungee-exchange-mainnet` -> `celer-cbridge`).
- **Validation**: Passed local pre-commit suite (`validate_csv`, full JSON generation across 138 exports, and JSON schema validation).

### Settlement
Settlement Wallet (USDC on Base):
`0x8366bCe3a2D379De7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:data/optimism-bungee-bridge",
    "base": "main",
    "body": body
}

url = "https://api.github.com/repos/Chain-Love/chain-love/pulls"
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print(f"PR created successfully: #{res['number']} - {res['html_url']}")
except urllib.error.HTTPError as e:
    print(f"HTTPError {e.code}: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
