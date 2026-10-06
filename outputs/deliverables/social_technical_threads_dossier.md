# 📢 Dossier de Hilos Técnicos para X / Twitter — `@dextermostard`
*(Versiones optimizadas y compactas: todos los tweets tienen entre 150 y 217 caracteres, muy por debajo del límite de 280 caracteres de X)*

---

## 🧵 HILO 1: Solana Token-2022 — Fee Harvester & MTU

### Tweet 1 (Principal):
```text
Most devs using SPL Token-2022 hit the 1,232-byte MTU limit or reentrancy loops in Transfer Hooks.

Here is how to architect an atomic fee harvester with dynamic compute prioritization 🧵👇

#Solana #Rust #Token2022
```

### Tweet 2:
```text
1/ The Challenge:
Harvesting fees across 100s of accounts exceeds Solana's 1,232-byte MTU limit.

Each pubkey is 32B + signatures. The fix: deterministic batching of max 28 accounts per atomic CPI.
```

### Tweet 3:
```text
2/ Dynamic Priority Fees:
Static compute units cause dropped packets.

We query getRecentPrioritizationFees, get the 75th percentile micro-lamports/CU, and prepend setComputeUnitPrice dynamically.
```

### Tweet 4:
```text
3/ Invariant Safety:
Transfer Hooks must NEVER CPI back into the mint without strict reentrancy guards.

State transition checks ensure harvesting cannot be sandwiched mid-flight.
```

### Tweet 5:
```text
4/ Full open-source code & tests are live:
📦 GitHub: https://github.com/dextermos/genesis-bounty-hunter/blob/main/tools/solana_fee_harvester.py

By @dextermostard (@dextermos on GH). Feedback welcome! 🚀
```

---

## 🧵 HILO 2: AI Agents en Base L2 — Session Keys (ERC-7579 / ERC-4337)

### Tweet 1 (Principal):
```text
Giving an AI agent your master private key is dangerous. Manual confirmations kill autonomy.

The fix on Base L2? Modular Session Keys (ERC-7579 / ERC-4337).

Quick architecture breakdown 🧵👇

#Base #Ethereum #AIAgents
```

### Tweet 2:
```text
1/ Session Key Primitive:
Master signs a temporary session with 4 strict bounds:
• validUntil timestamp
• dailySpendLimit (USDC/ETH)
• allowedTarget contract
• allowedSelector (4-byte function)
```

### Tweet 3:
```text
2/ On-Chain Guard:
When the agent executes:
✅ Checks signature against session
✅ Verifies target whitelist
✅ Enforces daily spend budget

Fails immediately if any bound is breached!
```

### Tweet 4:
```text
3/ Gas Efficiency:
• Custom errors save ~2,100 gas vs strings
• Pull accounting prevents balance griefing
• Total execution on Base L2 stays < 45k gas
```

### Tweet 5:
```text
4/ Smart contract & Foundry test suite:
📦 GitHub: https://github.com/dextermos/genesis-bounty-hunter/tree/main/products/fast_bounties/session_key_manager

By @dextermostard (@dextermos on GH) ⚡
```

---

## 🧵 HILO 3: Uniswap v4 Dynamic Fee Hooks — MEV & Tick Desync

### Tweet 1 (Principal):
```text
Dynamic fee hooks in Uniswap v4 are powerful, but naive implementations cause a critical flaw: Tick Desync & Sandwich MEV.

Here is a short security breakdown 🧵👇

#DeFi #Uniswap #SmartContractSecurity
```

### Tweet 2:
```text
1/ The Exploit Vector:
If swap fees update dynamically inside beforeSwap based on single-block volume spikes:
MEV bots inflate the dynamic fee to max pre-swap, forcing victims into severe price degradation.
```

### Tweet 3:
```text
2/ The Core Math:
Arbitrageurs capture the fee delta and restore equilibrium in afterSwap:
Profit = ΔP * V_victim - 2*Gas

LPs suffer impermanent loss without fee benefits.
```

### Tweet 4:
```text
3/ Defense & Mitigations:
🛡️ Multi-block EMA dampening (no single-block spikes)
🛡️ Strict rate limits (Δfee <= 0.05%/block)
🛡️ Caller validation for oracle updates
```

### Tweet 5:
```text
4/ Full audit paper & Foundry exploit PoC:
📄 Audit: https://github.com/dextermos/genesis-bounty-hunter/blob/main/outputs/deliverables/cantina_uniswap_v4_hook_audit.md

By @dextermostard (@dextermos on GH) 🛡️
```


---
### 📬 Verified Settlement Address
- **Settlement Wallet (EVM / Base / Solana):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
