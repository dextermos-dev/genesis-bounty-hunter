import urllib.request, json

import os; TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO = 'Chain-Love/chain-love'
TITLE = 'data(base): add Coinbase Wallet SDK for Base'
HEAD = 'dextermos-dev:data/base-coinbase-wallet-sdk'
BASE = 'main'

BODY = """## Summary

Add Coinbase Wallet SDK (`@coinbase/wallet-sdk`) as a canonical SDK offer and list it for Base.

Coinbase Wallet SDK is the official open-source SDK that allows developers to connect their decentralized applications to Coinbase Wallet and Smart Wallet on Base and EVM networks, supporting seamless user onboarding, passkeys, and multi-chain wallet connectivity.

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

- Coinbase Wallet SDK Documentation: https://docs.cdp.coinbase.com/wallet-sdk/docs/welcome
- Coinbase Wallet SDK GitHub: https://github.com/coinbase/coinbase-wallet-sdk

Both first-party URLs returned HTTP 200 during verification.

## Links

- Data Population Program: https://github.com/Chain-Love/chain-love/discussions/41

## Validation

- [x] Followed the Style Guide and column definitions, including canonical `!offer:` references.
- [x] Verified every new link during this contribution.
- [x] Confirmed current Base support using first-party documentation.
- [x] Validated with `validate_csv.py` (All checks passed, exact 18 columns, strict slug alphabetical ordering).
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
