import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get('GITHUB_TOKEN')

headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Dextermos-Bounty-Hunter'
}

title = "data(base): add official BaseScan Etherscan explorer for Base mainnet"

body = """## Summary

Add official BaseScan (`https://basescan.org/`) explorer entry for Base mainnet under `listings/specific-networks/base/explorers.csv`.

BaseScan is the primary Etherscan-powered block explorer and analytics platform for Base mainnet, complementing the existing `etherscan-sepolia` entry.

## Type of change

- [x] Add data rows
- [ ] Update data rows
- [ ] Remove data rows
- [ ] Schema change
- [ ] Documentation/metadata only

## Scope

- Networks affected: Base
- Categories affected: explorers
- Rows: 1 Base listing (`etherscan-mainnet` referencing canonical `!offer:etherscan`)

## Sources

- BaseScan: https://basescan.org/
- Etherscan Supported Chains: https://docs.etherscan.io/supported-chains

## Links

- Data Population Program: https://github.com/Chain-Love/chain-love/discussions/41

## Validation

- [x] Followed the Style Guide and column definitions, including canonical `!offer:etherscan` reference matching other networks (`snowscan-mainnet`, `bobascan-mainnet`, `celoscan-mainnet`, `etherscan-sepolia`).
- [x] Verified URLs during contribution.
- [x] Confirmed current Base mainnet explorer status.
- [x] Validated with pre-commit suite (`validate_csv.py`, `csv_to_json.py`, `validate.py`: Pre-commit checks passed).
- [x] Verified `git diff --check` (no whitespace or formatting warnings).

## Reward

- Rewards address (Base / Ethereum mainnet USDC):
`0x8366bCe3a2D379De7656D7A67015789FaF999f20`
- Contributor: `@dextermos-dev`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:data/base-basescan-explorer",
    "base": "main",
    "body": body
}

req = urllib.request.Request(
    'https://api.github.com/repos/Chain-Love/chain-love/pulls',
    data=json.dumps(payload).encode('utf-8'),
    headers=headers
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print(f"PR Successfully created! #{res['number']}: {res['html_url']}")
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code} - {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
