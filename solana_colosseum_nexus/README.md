# Nexus Protocol: Autonomous AI Settlement Spine on Solana
### Colosseum World's Fair Hackathon Track ($10,000 USDC)

**Author:** Dexter Mos ([@dextermos](https://github.com/dextermos) / [@dextermostard](https://x.com/dextermostard))  
**Target Submission:** Colosseum Crypto World's Fair Hackathon — Superteam Vietnam Track ($10,000 USDC)  
**Payout Address (Solana / EVM):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`  

---

## 1. Executive Summary

Nexus Protocol is a high-speed, non-custodial smart contract infrastructure on Solana designed to allow autonomous AI agents to bid, deliver micro-services, and settle payments in sub-second transaction slots.

## 2. Technical Deliverables
1. **On-Chain Anchor Smart Contracts:** Located in [`programs/nexus_protocol/`](programs/nexus_protocol/).
2. **Technical Whitepaper:** Available in [`docs/WHITEPAPER.md`](docs/WHITEPAPER.md).
3. **Automated Test Suite:** In [`tests/nexus_protocol.spec.ts`](tests/nexus_protocol.spec.ts).
4. **React & Glassmorphism Dashboard:** In [`app/src/NexusDashboard.tsx`](app/src/NexusDashboard.tsx).

---

## 3. How to Build & Test

```bash
cd solana_colosseum_nexus
anchor test
```
