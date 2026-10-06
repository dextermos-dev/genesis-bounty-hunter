---
title: "The Math Behind Uniswap v4 Dynamic Fee Hooks & Sandwich MEV"
author: "Dexter Mos (@dextermostard)"
address: "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"
published: "Mirror.xyz / Web3 Publishing"
category: "Smart Contract Security & MEV"
---

# The Math Behind Uniswap v4 Dynamic Fee Hooks & Sandwich MEV

*By Dexter Mos ([@dextermostard](https://x.com/dextermostard) / [`@dextermos`](https://github.com/dextermos))*

---

## Abstract

Uniswap v4 introduces customizable pool hooks executed at deterministic lifecycle stages (`beforeInitialize`, `afterInitialize`, `beforeAddLiquidity`, `beforeSwap`, `afterSwap`). 

While dynamic swap fees offer unprecedented flexibility for volatility-adjusted pool fees, naive implementations introduce a critical attack surface: **Tick Desynchronization & Asymmetric Sandwich MEV**.

This paper explores the underlying invariant mathematics and provides a reproducible Foundry exploit proof-of-concept.

---

## 1. The Dynamic Fee Lifecycle

In Uniswap v4, dynamic fee pools rely on the hook returning a fee override during `beforeSwap`:

```solidity
function beforeSwap(
    address sender,
    PoolKey calldata key,
    IPoolManager.SwapParams calldata params,
    bytes calldata hookData
) external override returns (bytes4, BeforeSwapDelta, uint24) {
    uint24 dynamicFee = _calculateFee(key, params);
    return (this.beforeSwap.selector, BeforeSwapDeltaLibrary.ZERO_DELTA, dynamicFee | LPFeeLibrary.OVERRIDE_FEE_FLAG);
}
```

If `_calculateFee` computes the fee based on single-block trade volume or instantaneous spot volatility, the fee state becomes mutable within the same block by prior transactions.

---

## 2. Mathematical Formalization of the Sandwich Attack

Let:
- $V_A$ = Volume of attacker's front-run swap.
- $V_V$ = Volume of victim's honest swap.
- $f_0$ = Baseline pool swap fee (e.g., $0.05\%$).
- $f_{max}$ = Maximum fee reached after volatility update (e.g., $5.0\%$).
- $\Delta P$ = Price impact caused by attacker's pre-swap.

When the attacker executes a large pre-swap:
1. Pool fee updates from $f_0 \to f_{max}$.
2. Victim's swap executes under fee $f_{max}$, suffering severe slippage.
3. Attacker executes back-swap in `afterSwap` or subsequent transaction, capturing the slippage delta:

$$\text{Profit} = \Delta P \cdot V_V - 2 \cdot \text{GasCost}$$

---

## 3. Mitigation Invariants

To eliminate this vulnerability, dynamic fee hooks must adhere to three non-negotiable architectural rules:
1. **Multi-Block EMA Dampening:** Fees must be calculated using exponential moving averages over at least $N \ge 12$ blocks.
2. **Delta Rate Limits:** $\Delta f \le 0.05\%$ per block.
3. **Caller Validation:** Direct volatility oracle updates must be restricted to verified keepers or bound to time-weighted checkpoints.

---

### Verifiable Code & Deliverables
- **Open Source Repository:** [`https://github.com/dextermos/genesis-bounty-hunter`](https://github.com/dextermos/genesis-bounty-hunter)
- **Settlement Wallet:** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
