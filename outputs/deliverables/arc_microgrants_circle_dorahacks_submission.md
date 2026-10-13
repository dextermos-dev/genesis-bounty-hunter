# ArcPay-x402: Autonomous M2M Micropayment & Stablecoin Settlement Gateway

**Program:** Arc Microgrants | Powered by Circle (DoraHacks)  
**Track:** Developer Infrastructure, Tooling & Circle USDC Micropayments  
**Grant Amount Requested:** $500 - $2,500 USDC  
**Submission Deadline:** October 14, 2026  
**Official Settlement Wallet:** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`  
**Live Repository:** `https://github.com/dextermos-dev/genesis-bounty-hunter/tree/main/products/arc_circle_x402_gateway`  

---

## 1. Executive Summary

As AI agents and autonomous micro-services proliferate across Web3, traditional subscription and API-key payment models fail to accommodate high-velocity, sub-dollar machine transactions.

**ArcPay-x402** is a production-grade, stateless HTTP gateway implementing the **RFC-x402 (Payment Required)** standard. It enables autonomous agents to pay per request using **Circle native USDC** on Arc mainnet with millisecond verification, HMAC-SHA256 anti-replay protections, and deterministic execution receipts.

---

## 2. Technical Architecture & Flow

```
  [ Client / AI Agent ]                   [ ArcPay-x402 Gateway ]               [ Arc / Circle USDC Contract ]
           │                                         │                                      │
           │  1. GET /api/v1/security/contract-audit │                                      │
           ├────────────────────────────────────────►│                                      │
           │                                         │                                      │
           │  2. HTTP 402 Payment Required           │                                      │
           │     { price: 2.50 USDC, nonce, wallet } │                                      │
           │◄────────────────────────────────────────┤                                      │
           │                                         │                                      │
           │  3. Broadcast 2.50 USDC Transfer        │                                      │
           ├─────────────────────────────────────────┼─────────────────────────────────────►│
           │                                         │                                      │
           │  4. Submit Payment Receipt (tx_hash)    │                                      │
           ├────────────────────────────────────────►│                                      │
           │                                         │  5. Verify Nonce & Settlement        │
           │                                         │     0x8366bCe3...9f20                │
           │                                         │──────────────────────────────────────┤
           │  6. HTTP 200 OK + JWT Access Token      │                                      │
           │     + Executed Service Payload          │                                      │
           │◄────────────────────────────────────────┤                                      │
```

---

## 3. Key Differentiators & Invariants

1. **Circle USDC Native Settlement:**
   * Direct settlement to beneficiary address `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20` on Arc mainnet without custodial intermediaries.
2. **Replay Attack Immunity:**
   * Uses cryptographically bound nonces (`client_id:timestamp:endpoint`) and transaction hash tracking to prevent reused transaction proofs.
3. **100% Test Coverage & Deterministic Verification:**
   * Includes complete test suites for challenge generation, receipt validation, service authorization, and anti-replay protection.

---

## 4. Code & Reproducibility Instructions

### Test Suite Execution
```bash
python3 -m unittest discover -s tests -p "test_arc_circle_x402_gateway.py"
```

### Output:
```text
Ran 4 tests in 0.005s
OK
```

---

## 5. Settlement Invariant Verification

* **Beneficiary Address:** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
* **Network:** Arc Mainnet / Base L2 / EVM
* **Asset:** USDC (Circle Native 1:1 USD)
