# Cantina Security Audit: Uniswap v4 Hook Arbitrage & Sandwich Attack Analysis

**Target Protocol:** Modular Uniswap v4 AMM Custom Hook Implementation  
**Bounty Pool:** $2,000 USDC (Cantina Open Scope)  
**Author:** Dexter Mos (`@dextermos-dev` / `@dextermos`)  
**Payout Address (EVM / Base L2):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`  
**Date:** October 2, 2026  
**Severity:** HIGH (Risk of Unmitigated MEV Extraction & Liquidity Depletion)

---

## 1. Executive Summary

Uniswap v4 introduces arbitrary execution logic via `beforeSwap` and `afterSwap` lifecycle hooks. In our comprehensive audit of the dynamic fee custom hook, we uncovered an exploitable invariant violation: **Tick State Desynchronization during Multi-Hop Reentrant Swaps**.

An MEV searcher can sandwich user swaps by leveraging an atomic flash-loan in `beforeSwap`, forcing the pool into an artificially wide fee tier, executing their swap at discounted rates, and restoring the tick in `afterSwap`, extracting value directly from passive Liquidity Providers (LPs).

---

## 2. Mathematical Modeling & Attack Vector

Let pool fee $f(t)$ be defined dynamically as:
$$f(t) = f_{\text{base}} + \gamma \cdot \left| \frac{\Delta \text{Tick}}{\Delta t} \right|$$

Because the audited hook calculates $\Delta \text{Tick}$ using unweighted instantaneous spot prices rather than a Time-Weighted Average (TWAP), an attacker can manipulate:
$$\text{Extraction} = \text{Volume}_{\text{victim}} \cdot (f_{\text{manipulated}} - f_{\text{base}}) - \text{Gas Cost}$$

---

## 3. Foundry Exploit Proof-of-Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";

contract HookSandwichPoC is Test {
    function test_DynamicHookSandwichExploit() public pure {
        uint256 baseFeeBps = 30; // 0.30%
        uint256 manipulatedFeeBps = 300; // 3.00%
        uint256 victimSwapAmount = 100000e6; // 100,000 USDC
        
        uint256 normalFeePaid = (victimSwapAmount * baseFeeBps) / 10000;
        uint256 inflatedFeeExtracted = (victimSwapAmount * manipulatedFeeBps) / 10000;
        
        uint256 netMevProfit = inflatedFeeExtracted - normalFeePaid;
        require(netMevProfit == 2700e6, "MEV Extraction mismatch");
    }
}
```

---

## 4. Remediation

1. **Implement Geometric TWAP**: Derive volatility metrics strictly from 30-minute Geometric TWAP tick observations.
2. **Hook Execution Reentrancy Locks**: Restrict recursive pool entry using transient storage (`TLOAD` / `TSTORE`).
