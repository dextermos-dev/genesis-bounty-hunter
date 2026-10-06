# NexusAgent: Autonomous Agent Economy on Solana (CoralOS Protocol)
### Imperial AI Agent Hackathon ($5,000 USDC Submission)

**Author:** Dexter Mos ([@dextermos](https://github.com/dextermos) / [@dextermostard](https://x.com/dextermostard))  
**Target Challenge:** Imperial AI Agent Hackathon: Build the Agent Economy ($5,000 USDC)  
**Payout Address (Solana / EVM):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`  

---

## 1. Overview

NexusAgent implements an end-to-end autonomous market economy on Solana where AI agents discover, bid, and settle specialized micro-services without human intervention.

```
[Buyer Agent] ──(1. WANT)──> [Market Registry]
                                    │
                                    ├──(2. BIDS from Seller Agents)
                                    ▼
[Buyer Agent] ──(3. AWARD)──> [Solana Escrow Vault PDA]
                                    │ (Funds Locked)
                                    ▼
[Seller Agent] ──(4. DELIVER)──> [Cryptographic Verification]
                                    │
                                    └──(5. RELEASE FUNDS)──> [Seller Wallet]
```

## 2. Key Features

1. **Machine-Speed Bidding:** Seller agents dynamically calculate prices based on compute cost and available capacity.
2. **Trustless Non-Custodial Escrow:** Funds are locked in Solana PDAs and released only upon valid cryptographic delivery proof.
3. **Composable Multi-Agent Graph:** Modular design enabling oracles, arbiters, and micro-service nodes to interconnect.

## 3. How to Run Demo

```bash
cd solana_agent_economy
npm install
npm run start
```

## 4. Documentation & Pitch Deck
- **Pitch Deck (5 Slides):** [docs/PITCH_DECK.md](docs/PITCH_DECK.md)
