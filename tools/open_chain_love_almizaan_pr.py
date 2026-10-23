import urllib.request
import urllib.error
import json
import os

token = ""
with open('.env') as f:
    for line in f:
        if line.startswith('GITHUB_TOKEN='):
            token = line.strip().split('=', 1)[1]
            break

title = "Add Bug Bounty Intelligence — Al-Mizaan v3 Solidity security scanner + MCP server (Base)"

body = """Adds **Bug Bounty Intelligence** as a provider with two Base-network listings.

**Provider:** Bug Bounty Intelligence — AI-powered smart contract security analysis for developers and autonomous agents (Al-Mizaan v3 framework, settled in USDC on Base via x402). Repository https://github.com/holistis/bug-bounty-intelligence-mcp · Docs https://github.com/holistis/bug-bounty-intelligence-mcp#readme

**Listings**
- `security` — `al-mizaan-solidity-scan`: AI-powered smart contract security scanner utilizing the 7-gate Al-Mizaan v3 verification framework. Evaluates Solidity codebases against 1,032 exact-reconciled findings from Sherlock and Code4rena audit contests, pruning false positives before generating actionable reports. Pay-as-you-go via x402 ($5.00 USDC full repo scan on Base).
- `mcpservers` — `bug-bounty-intelligence-mcp`: MCP server that scans Solidity repositories through the 7-gate Al-Mizaan verification framework to cut LLM false positives. Free pattern search from 1,032 reconciled Sherlock contest findings; paid full-repo AST scan via x402 micropayments in USDC on Base.

**Sources**
- MCP Server Repository & Docs: https://github.com/holistis/bug-bounty-intelligence-mcp
- Methodology: https://github.com/holistis/bug-bounty-intelligence-mcp/blob/main/METHODOLOGY.md
- Benchmark (vs Slither): https://github.com/holistis/bug-bounty-intelligence-mcp/blob/main/BENCHMARK.md

**Validation:** ran `git-hooks/pre-commit.py` locally against `json-tools` — `validate_csv.py`, `csv_to_json.py` and `validate.py` all pass cleanly with zero errors. Slug ordering preserved; 256×256 transparent PNG logo included. Repo starred per CONTRIBUTING.
"""

payload = {
    'title': title,
    'head': 'dextermos-dev:add/al-mizaan-security-base',
    'base': 'main',
    'body': body
}

req = urllib.request.Request(
    'https://api.github.com/repos/Chain-Love/chain-love/pulls',
    data=json.dumps(payload).encode('utf-8')
)
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Accept', 'application/vnd.github+json')
req.add_header('Content-Type', 'application/json')

try:
    with urllib.request.urlopen(req) as resp:
        res = json.load(resp)
        print('PR created successfully!')
        print('PR URL:', res['html_url'])
        print('PR Number:', res['number'])
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code, e.reason)
    print(e.read().decode('utf-8'))
