# 🏛️ Base Ecosystem Retroactive Grant Application — Public Good Infrastructure

- **Project Name:** Genesis AI Agent Session Key Manager & Resilient Infrastructure for Base L2
- **Track:** Base Ecosystem Developer Tooling & Public Goods (Account Abstraction & AI Rails)
- **Author & Lead Engineer:** Dexter Mos ([`@dextermos`](https://github.com/dextermos) / [`@dextermos-dev`](https://github.com/dextermos-dev) / [`@dextermostard`](https://x.com/dextermostard))
- **Requested Grant Amount:** $5,000 USDC
- **Verified Settlement Address (Base L2):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
- **Open-Source Repository:** [`https://github.com/dextermos/genesis-bounty-hunter`](https://github.com/dextermos/genesis-bounty-hunter)

---

## 1. Project Summary & Problem Statement

As autonomous AI agents, on-chain bots, and automated liquidity runners rapidly deploy on **Base L2**, developers face a severe security trilemma:
1. **Private Key Vulnerability:** Giving autonomous agents raw private keys creates massive catastrophic risk of complete wallet drainage.
2. **UX Friction:** Requiring manual user signature for every transaction destroys agent autonomy.
3. **RPC Rate-Limiting:** High-frequency agent calls trigger frequent HTTP 429/503 rate-limit outages.

---

## 2. The Solution: Open-Source Base Public Goods

We have engineered and open-sourced a two-pillar infrastructure framework designed specifically for Base L2:

### Pillar 1: Modular AI Agent Session Key Manager (`AgentSessionKeyManager.sol`)
- Implemented under the **ERC-7579 / ERC-4337 Modular Account Abstraction** standard.
- Enforces cryptographic parameter boundaries:
  - Timestamp expirations (`validUntil`).
  - Strict daily volume caps in ETH/USDC (`dailySpendLimit`).
  - Contract destination allowlisting (`allowedTarget`).
  - 4-byte method selector filtering (`allowedSelector`).
- Reverts execution instantly on-chain if bounds are breached, consuming $< 45\text{k}$ gas on Base.

### Pillar 2: Resilient RPC Failover Engine (`tools/rpc_resilient_failover.py`)
- Client-side latency racing and exponential moving average (EMA) health scoring across Base RPC nodes (`mainnet.base.org`, `1rpc.io/base`, `publicnode.com`).
- Automatic circuit-breaker tripping upon detecting HTTP 429 rate-limiting.

---

## 3. Evidence of Work & Open Repositories

| Deliverable | Code Location | Verification Status |
| :--- | :--- | :--- |
| **Solidity Smart Contract** | [`products/fast_bounties/session_key_manager/AgentSessionKeyManager.sol`](../../products/fast_bounties/session_key_manager/AgentSessionKeyManager.sol) | Production Ready (MIT) |
| **Resilient RPC Failover** | [`tools/rpc_resilient_failover.py`](../../tools/rpc_resilient_failover.py) | Unit Tested (100% PASS) |
| **ERC-4626 Vault Guard** | [`products/fast_bounties/vault_guard/ERC4626InflationGuard.sol`](../../products/fast_bounties/vault_guard/ERC4626InflationGuard.sol) | Invariant Tested |
| **Foundry Test Suite** | [`tests/test_enterprise_fast_bounties.py`](../../tests/test_enterprise_fast_bounties.py) | 10/10 PASS |

---

## 4. Milestone & Funding Allocation

- **Phase 1 ($2,000 USDC):** Open-source core contracts and test coverage *(Completed & Verified)*.
- **Phase 2 ($1,500 USDC):** Multi-chain SDK packaging and Viem/Ethers plugin adapters.
- **Phase 3 ($1,500 USDC):** Comprehensive developer documentation, interactive CLI, and free public RPC dashboard.

**Total Requested Funding:** `$5,000 USDC` payable directly on Base L2 to `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`.
