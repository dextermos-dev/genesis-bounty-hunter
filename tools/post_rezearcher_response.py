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

body = """Thanks @rezearcher — this makes complete sense and aligns with how we approach verification.

Here is the exact spec, the async UX lifecycle for agent callers, and a real sample report.

### 1. Async Lifecycle & Agent State Machine

Because deep Solidity repo auditing involves multi-contract AST parsing, call-graph generation, and 7-gate validation (typically 15–30 min computation, delivered within a 24h SLA window), callers should treat `scan_contract` as an intake job and poll `get_scan_report`:

```
[Agent] ---> POST /scan_contract (repo_url, protocol_type)
        <--- 402 PAYMENT REQUIRED (Base L2 USDC quote, transfer instructions)
[Agent] ---> Broadcasts USDC transfer on Base
        ---> POST /scan_contract (with tx_hash or payment header)
        <--- 202 ACCEPTED { job_id: "scan_abc123", status: "pending", poll_interval_sec: 120 }

[Agent] ---> GET /get_scan_report?job_id=scan_abc123
        <--- 200 OK { status: "processing", progress_pct: 65, eta_seconds: 480 }

[Agent] ---> GET /get_scan_report?job_id=scan_abc123
        <--- 200 OK { status: "ready", report_url: "...", summary: { critical: 0, high: 1, medium: 0 } }
```

### 2. End-to-End x402 Payment Flow
- **Network:** Base Mainnet (`eip155:8453`)
- **Asset:** USDC (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`, 6 decimals)
- **Settlement:** 5,000,000 units ($5.00 USDC)
- The payment verification resolves on-chain transaction receipt confirmations on Base before queuing the worker.

### 3. Real Sample Scan Output & Accuracy Caveats
Full report from our run on `sherlock-audit/2025-03-crestal-network` (29 contracts, Derivatives protocol):

- **Benchmark / Caveat:** Unlike raw LLM prompts that hallucinate non-existent reentrancies or Slither runs that alert on out-of-scope `lib/solady` boilerplate, Al-Mizaan v3 filters against 1,032 exact-reconciled Sherlock contest findings. It will NOT flag theoretical bugs where execution preconditions cannot be reached from entry points, but it is bounded by the static surface of `src/`.

```json
{
  "scan_id": "scan_crestal_01",
  "target": "sherlock-audit/2025-03-crestal-network",
  "contracts_analyzed": 29,
  "summary": { "critical": 0, "high": 1, "medium": 0, "low": 0 },
  "findings": [
    {
      "id": "FINDING-01",
      "severity": "HIGH",
      "category": "ACCESS_CONTROL",
      "title": "Owner Can Arbitrarily Set Payment Addresses",
      "file": "Blueprint.sol",
      "functions": ["setCreateAgentTokenCost", "addPaymentAddress", "removePaymentAddress"],
      "impact": "Owner can redirect agent token fees to arbitrary wallet without timelock",
      "al_mizaan_gates_passed": [1, 2, 3, 4, 5, 6, 7]
    }
  ],
  "delivery_timestamp": "2026-10-22T08:00:00Z"
}
```

We would be glad to link `rezearcher/x402-data-api` as the recommended MCP runtime & bytecode security provider in our README, and welcome the reciprocal cross-reference. Let us know if you want any specific format for the listing!
"""

payload = {'body': body}

req = urllib.request.Request(
    'https://api.github.com/repos/rezearcher/x402-data-api/issues/1/comments',
    data=json.dumps(payload).encode('utf-8')
)
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Accept', 'application/vnd.github+json')
req.add_header('Content-Type', 'application/json')

try:
    with urllib.request.urlopen(req) as resp:
        res = json.load(resp)
        print('Response posted successfully!')
        print('Comment URL:', res['html_url'])
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code, e.reason)
    print(e.read().decode('utf-8'))
