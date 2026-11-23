import urllib.request
import json
from dotenv import dotenv_values

token = dotenv_values('.env').get('GITHUB_TOKEN')
headers = {
    'Authorization': f'token {token}',
    'User-Agent': 'BountyHunter',
    'Content-Type': 'application/json'
}

title = "data(polygon): add Chainspect real-time network and TPS analytics for Polygon"
body = """### Summary

This PR adds **Chainspect** (`chainspect-polygon`) to `listings/specific-networks/polygon/analytics.csv`, inheriting canonical offer metadata from `!offer:chainspect`:

- **Chainspect**: Real-time blockchain telemetry and analytics engine tracking live TPS, Max TPS recorded, 30-day/90-day transaction volume, block time, time to finality, and network metrics for Polygon PoS mainnet.
- **Official Dashboard**: [`https://chainspect.app/chain/polygon`](https://chainspect.app/chain/polygon) (verified HTTP 200).

### Verification & Compliance
- **Sparse Row Inheritance**: Inherits canonical metadata (`provider`, `dataSources`, `hasDashboard`, `historicalData`, `price=$0`, `planType=Public`, `starred=FALSE`) from `references/offers/analytics.csv`.
- **Alphabetical Sorting**: Inserted in exact alphabetical order by slug (`artemis-polygon` -> `chainspect-polygon` -> `coingecko-api-analyst`).
- **Validation**: Passed local pre-commit suite (`validate_csv`, full JSON generation across 138 exports, and JSON schema validation).

### Settlement
Settlement Wallet (USDC on Base):
`0x8366bCe3a2D379De7656D7A67015789FaF999f20`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:data/polygon-chainspect-analytics",
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
