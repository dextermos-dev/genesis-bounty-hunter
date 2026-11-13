import urllib.request, json

import os; TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO = 'Chain-Love/chain-love'
TITLE = 'data(base): add Coinbase OnchainKit React and TypeScript SDK'
HEAD = 'dextermos-dev:data/base-onchainkit-sdk'
BASE = 'main'

BODY = """## Summary

Add Coinbase OnchainKit as a canonical SDK offer and list it for Base.

OnchainKit is Coinbase's official open-source React component toolkit and TypeScript SDK for building onchain applications, providing ready-to-use wallet, identity, swap, checkout, and minting UI components directly on Base.

## Type of change

- [x] Add data rows
- [ ] Update data rows
- [ ] Remove data rows
- [ ] Schema change
- [ ] Documentation/metadata only

## Scope

- Networks affected: Base
- Categories affected: sdks
- Rows: 1 canonical offer and 1 Base listing

## Sources

- OnchainKit Docs: https://docs.base.org/builderkits/onchainkit/overview
- OnchainKit GitHub: https://github.com/coinbase/onchainkit

Both first-party URLs returned HTTP 200 during verification.

## Links

- Data Population Program: https://github.com/Chain-Love/chain-love/discussions/41

## Validation

- [x] Followed the Style Guide and column definitions, including canonical `!offer:` references.
- [x] Verified every new link during this contribution.
- [x] Confirmed current Base support using first-party Base documentation.
- [x] Validated with `validate_csv.py` (All checks passed, zero slug ordering violations).
- [x] Verified `git diff --check` (no whitespace or formatting warnings).

## Reward

- Rewards address (Base / Ethereum mainnet USDC):
`0x8366bCe3a2D379De7656D7A67015789FaF999f20`
- Contributor: `@dextermos-dev`
"""

payload = {
    'title': TITLE,
    'head': HEAD,
    'base': BASE,
    'body': BODY
}

req = urllib.request.Request(
    f'https://api.github.com/repos/{REPO}/pulls',
    data=json.dumps(payload).encode('utf-8'),
    headers={
        'Authorization': f'Bearer {TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Dextermos-Bounty-Hunter'
    }
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print('SUCCESS! Created PR #' + str(res.get('number')) + ' at ' + res.get('html_url'))
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code, e.read().decode())
except Exception as e:
    print('Error:', e)
