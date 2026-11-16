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

title = "data(base): list official Artemis fundamental analytics dashboard for Base"

body = """## Summary

Add the canonical `artemis` analytics entry to `listings/specific-networks/base/analytics.csv`.

Artemis ([classic.artemis.ai/asset/base](https://classic.artemis.ai/asset/base)) is the premier institutional crypto fundamentals, developer activity, and onchain metrics dashboard for Base, tracking DEX volume, active addresses, stablecoin flows, and fee metrics.

## Type of change

- [x] Add data rows
- [ ] Update data rows
- [ ] Remove data rows
- [ ] Schema change
- [ ] Documentation/metadata only

## Scope

- Networks affected: Base
- Categories affected: analytics
- Rows: 1 Base listing (`artemis-mainnet` referencing canonical `!offer:artemis`)

## Sources

- Artemis Base Overview: https://classic.artemis.ai/asset/base

URL returned HTTP 200 during verification.

## Links

- Data Population Program: https://github.com/Chain-Love/chain-love/discussions/41

## Validation

- [x] Followed the Style Guide and column definitions, including canonical `!offer:artemis` reference matching other networks (`algorand`, `arbitrum`, `avalanche`, `ethereum`, `polygon`, `solana`).
- [x] Verified URLs during contribution.
- [x] Confirmed current Base analytics status.
- [x] Validated with pre-commit suite (`validate_csv.py`, `csv_to_json.py`, `validate.py`: Pre-commit checks passed).
- [x] Verified `git diff --check` (no whitespace or formatting warnings).

## Reward

- Rewards address (Base / Ethereum mainnet USDC):
`0x8366bCe3a2D379De7656D7A67015789FaF999f20`
- Contributor: `@dextermos-dev`
"""

payload = {
    "title": title,
    "head": "dextermos-dev:data/base-artemis-analytics",
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
