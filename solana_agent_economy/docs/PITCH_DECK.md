# Imperial AI Agent Hackathon: Pitch Deck (5 Slides)
### Project: NexusAgent — The Machine-to-Machine On-Chain Service Economy on Solana

**Author:** Dexter Mos ([@dextermos](https://github.com/dextermos) / [@dextermostard](https://x.com/dextermostard))  
**Payout Wallet:** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`  

---

### Slide 1: The Customer & The Problem
- **The Customer:** Autonomous AI Agents needing real-time computation, liquidity routing, and verified oracles.
- **The Problem:** Humans are too slow. Legacy Web2 APIs require credit cards, KYC, and manual rate-limit negotiations.
- **The Opportunity:** A software-native customer that reasons about cost at microsecond speeds and pays on-chain.

---

### Slide 2: What It Sells (`deliverService()`)
- **Core Offering:** High-frequency on-chain telemetry, DEX liquidity depth routing, and zero-slippage execution proofs.
- **Form Factor:** One line of code: `deliverService(payload)` returning cryptographically signed Ed25519 outputs.

---

### Slide 3: Why They Pay (The Value & The Pricing Model)
- **Asymmetric ROI:** Buying real-time MEV protection and route scoring for 0.05 SOL saves agents thousands of dollars in slippage.
- **Dynamic Bidding:** Seller agents price dynamically using inventory-based surge models; Buyer agents optimize for maximum risk-adjusted confidence score.

---

### Slide 4: The Agent Economy (The Graph)
- **Composable Multi-Agent Graph:**
  - **Buyer Agents:** Autonomous traders / allocators.
  - **Seller Agents:** Specialized intelligence providers.
  - **Arbiter & Escrow Nodes:** On-chain Solana smart contracts holding funds until cryptographic delivery is verified.

---

### Slide 5: The Proof (On-Chain Escrow & Settlement)
- **Trustless Settlement:** 100% non-custodial Solana Pay + Escrow architecture.
- **State Machine Flow:** `WANT` ➔ `BID` ➔ `AWARD` ➔ `DEPOSITED` ➔ `DELIVERED` ➔ `RELEASED`.
- **Zero Counterparty Risk:** Automated buyer refund if the seller no-shows before deadline.

