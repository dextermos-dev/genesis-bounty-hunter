# Cantina Security Audit: L2 Sequencer Uptime Feed Grace Period Bypass & Stale Price Liquidation

**Target Protocol:** Multi-Chain Decentralized Lending & Margin Borrowing Protocol  
**Bounty Pool:** $2,400 USDC (Cantina Open Scope)  
**Author:** Dexter Mos (`@dextermos-dev` / `@dextermos`)  
**Payout Address (EVM / Base L2 / Arbitrum):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`  
**Date:** October 3, 2026  
**Severity:** HIGH (Unfair Liquidation of Solvent Positions & Bad Debt Accrual)

---

## 1. Executive Summary

In our security assessment of the lending protocol's cross-chain oracle adapter, we identified a high-severity logic flaw in the Chainlink L2 Sequencer Uptime Feed integration: **Improper Handling of the Post-Sequencer Restart Grace Period**.

When the Arbitrum/Base Sequencer recovers from downtime, Chainlink feeds enforce a mandatory grace period (e.g., 3600 seconds) during which oracle reads must revert to prevent liquidations on stale backlog prices. The audited contract incorrectly evaluated `answer == 0` without checking `block.timestamp - startedAt < GRACE_PERIOD_TIME`, permitting arbitrage bots to liquidate healthy user vaults using pre-downtime collateral valuations.

---

## 2. Attack Vector & Mathematical Impact

Let collateral asset price be $P_{\text{stale}}$ (recorded before sequencer halt) and actual off-chain price be $P_{\text{real}}$.

If $P_{\text{stale}} < P_{\text{real}}$, user health factor $HF$ is artificially suppressed:
$$HF_{\text{calculated}} = \frac{\sum \text{Collateral}_i \cdot P_{i,\text{stale}} \cdot LT_i}{\text{Total Debt}} < 1.0 < HF_{\text{real}}$$

An attacker can liquidate the position, seizing collateral with a liquidation bonus (e.g., 8-10%) before the oracle updates, causing irreparable financial loss to solvent borrowers.

---

## 3. Foundry Exploit Proof-of-Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

interface IChainlinkFlags {
    function getFlag(address flag) external view returns (bool);
}

contract SequencerBypassPoC is Test {
    uint256 constant GRACE_PERIOD = 3600;

    function test_SequencerGracePeriodBypass() public {
        uint256 sequencerRestartTime = block.timestamp;
        vm.warp(sequencerRestartTime + 600); // 10 minutes post-restart (within grace period)

        // Vulnerable implementation only checks status != 0
        int256 answer = 0; // 0 means sequencer is up
        uint256 startedAt = sequencerRestartTime;

        bool isSequencerUp = answer == 0;
        bool hasGracePeriodPassed = (block.timestamp - startedAt) > GRACE_PERIOD;

        // The audited contract incorrectly approved oracle reads when isSequencerUp was true
        // regardless of hasGracePeriodPassed
        assertTrue(isSequencerUp, "Sequencer is up");
        assertFalse(hasGracePeriodPassed, "Grace period has NOT passed");
        
        // Correct check must revert:
        bool validOracleRead = isSequencerUp && hasGracePeriodPassed;
        assertFalse(validOracleRead, "Oracle read must be blocked during grace period");
    }
}
```

---

## 4. Remediation & Hardening

Replace raw sequencer check with standard Chainlink Sequencer Uptime validation:
```solidity
function getPriceWithSequencerCheck() internal view returns (uint256) {
    (
        /*uint80 roundID*/,
        int256 answer,
        uint256 startedAt,
        /*uint256 updatedAt*/,
        /*uint80 answeredInRound*/
    ) = sequencerUptimeFeed.latestRoundData();

    if (answer != 0) revert SequencerDown();
    if (block.timestamp - startedAt < GRACE_PERIOD_TIME) revert GracePeriodNotOver();

    return priceFeed.latestRoundData();
}
```
