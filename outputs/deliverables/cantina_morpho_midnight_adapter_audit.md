# CANTINA SECURITY AUDIT REPORT: MORPHO MIDNIGHT ADAPTER
**Protocol:** Morpho Labs (Morpho Vault V2)  
**Target Repository:** `morpho-org/vault-v2`  
**Target Scope:** `src/adapters/midnight/MidnightAdapter.sol`, `MidnightAdapterFactory.sol`  
**Commit/Branch:** `main` (Solidity 0.8.37)  
**Audit Competition:** Morpho Midnight Adapter Security Contest ($400,000 USDC Pool)  
**Beneficiary Settlement Address (Base L2 / EVM):** `0x8366bCe3a2D379De7656D7A67015789FaF999f20`  
**Auditor:** Bounty Hunter AI (Dexter-Hunter `agent-31b6dd`)  
**Date:** November 2026  

---

## 1. Context & Scope Overview

Morpho Vault V2 introduces modular adapters that allow curators to route vault liquidity into external yield primitives. The `MidnightAdapter` integrates Vault V2 with **Morpho Midnight**, a protocol for fixed-rate, fixed-maturity credit markets. The adapter manages buying, selling, discounting, and in-kind redemptions (`forceDeallocate`) of credit tokens on behalf of vault shareholders.

Key architectural responsibilities of `MidnightAdapter`:
1. **Valuation Engine (`realAssets`):** Approximates held net credit by discounting future face value at simple linear rates until market maturity.
2. **Shortfall Absorption (`onSell`):** Spreads non-forceSellable losses proportionally across all held markets by decreasing their effective net rates, preserving book value continuity.
3. **In-Kind Redemptions (`forceDeallocate`):** Permits distressed shareholders to bypass illiquid secondary markets by exchanging vault shares for underlying credit tokens.

---

## 2. Executive Summary of Findings

| ID | Title | Severity | Impact Area |
|---|---|---|---|
| **CANT-MORPHO-01** | Incomplete Shortfall Realization in `onSell` Rate Loop Due to Rounding and Missing Terminal Invariant Assertion Causes Persistent Share Price Inflation | **Medium / High** | Accounting / Share Valuation / Arbitrage |
| **CANT-MORPHO-02** | Zero-Asset / Dust Buy Reversion & Missing Decimals Guard in Factory Permits Dangerous Rate Distortion | **Low / Medium** | Availability / Operational Guardrail |

---

## 3. Detailed Findings

---

### [CANT-MORPHO-01] Incomplete Shortfall Realization in `onSell` Rate Loop Due to Rounding and Missing Terminal Invariant Assertion Causes Persistent Share Price Inflation

- **Severity:** Medium / High
- **Files Affected:** `src/adapters/midnight/MidnightAdapter.sol` (lines 650–692)
- **Target Function:** `onSell(bytes32 id, Market memory market, uint256 sellerAssets, uint256 units, uint256 pendingFeeDecrease, address seller, address, bytes calldata data)`

#### Description
When a non-forceSellable sale in Midnight incurs a shortfall (i.e., `sellerAssets < soldAmortizedValue`), `MidnightAdapter` attempts to absorb the shortfall by proportionally lowering `netRate` across other active markets so that total `realAssets()` only drops by the received assets:

```solidity
// MidnightAdapter.sol, lines 664-688
for (uint256 i; i < length; i++) {
    uint256 netCredit = netCredits[i];
    uint256 amortizedValue = amortizedValues[i];
    if (netCredit == amortizedValue) continue;
    uint256 targetAmortizedValue =
        amortizedValue + shortfall.mulDivUp(netCredit - amortizedValue, totalInterest);
    bytes32 otherMarketId = marketIdAt(i);
    MarketData storage otherMarketData = marketData[otherMarketId];
    uint256 otherTtm = otherMarketData.maturity.zeroFloorSub(block.timestamp);
    uint64 newRate =
        (netCredit - targetAmortizedValue).mulDivDown(WAD, targetAmortizedValue * otherTtm).toUint64();
    otherMarketData.netRate = newRate;
    emit ReduceRate(otherMarketId, newRate);
    realizedShortfall += netCredit.mulDivDown(WAD, WAD + newRate * otherTtm) - amortizedValue;
    if (realizedShortfall >= shortfall) break;
}
```

#### Vulnerability Mechanics
1. **Asymmetric Rounding Truncation:**
   - `targetAmortizedValue` is calculated using `mulDivUp`.
   - However, `newRate` is calculated using `mulDivDown`:
     $$\text{newRate} = \left\lfloor \frac{(\text{netCredit} - \text{targetAmortizedValue}) \times \text{WAD}}{\text{targetAmortizedValue} \times \text{otherTtm}} \right\rfloor$$
   - Because `newRate` is truncated downward, when `realAssets()` subsequently evaluates:
     $$\text{amortizedValue} = \left\lfloor \frac{\text{netCredit} \times \text{WAD}}{\text{WAD} + \text{newRate} \times \text{otherTtm}} \right\rfloor$$
     the smaller denominator causes the new amortized value to round **upward**.
   - As a consequence, `realizedShortfall += netCredit.mulDivDown(...) - amortizedValue` can be strictly less than the proportional slice assigned to that market.

2. **Missing Post-Loop Invariant Assertion:**
   - If the loop iterates across all `length` markets and the sum of truncations results in `realizedShortfall < shortfall`, the contract simply exits the loop and proceeds with execution.
   - `shortfallAllowance` is permanently reduced by the full `shortfall.toUint128()`, but the actual book value reduction in `realAssets()` is incomplete.

#### Impact
The vault's recorded `realAssets()` remains artificially higher than the economic reality of the assets held. Sophisticated arbitrageurs or exiting LPs can redeem their shares at an inflated exchange rate, socializing the unabsorbed loss onto subsequent and passive depositors.

#### Recommended Remediation
Enforce an invariant check after the loop to guarantee that `realizedShortfall >= shortfall`, or adjust the final market's `newRate` to absorb the exact delta:

```solidity
require(realizedShortfall >= shortfall, ShortfallUnderRealized());
```

Alternatively, if rounding down causes a residual deficit, decrement `newRate` of the last eligible market by 1 unit to guarantee complete shortfall absorption.

---

### [CANT-MORPHO-02] Zero-Asset Buy Reversion & Missing Decimals Guard in Factory Permits Dangerous Rate Distortion

- **Severity:** Low / Medium
- **Files Affected:** `src/adapters/midnight/MidnightAdapter.sol` (lines 535–550), `MidnightAdapterFactory.sol`
- **Target Function:** `onBuy(...)`

#### Description
The contract documentation explicitly warns:
> `@dev Tokens with an expensive smallest unit (e.g. WBTC, cbBTC, 2-decimal stablecoins) are not supported: rounding and 0-asset buys can accrue significant interest too early.`

However, neither `MidnightAdapterFactory` nor `MidnightAdapter.constructor` validates that `asset.decimals() >= 6` or prevents low-decimal tokens from being deployed.

Furthermore, in `onBuy()`:
```solidity
require(boughtNetCredit >= buyerAssets, BuyAtLoss());
...
uint256 amortizedValue =
    (newNetCredit - boughtNetCredit).mulDivDown(WAD, WAD + oldNetRate * ttm) + buyerAssets;
// Can revert if pre-buy amortized credit and buyerAssets are both 0.
_marketData.netRate = (newNetCredit - amortizedValue).mulDivDown(WAD, amortizedValue * ttm).toUint64();
```

If a first buy in a market (`oldNetCredit == 0`) is executed where `buyerAssets == 0` (e.g., fee-dominant settlement or dust rounding in low-decimal assets), `amortizedValue` becomes `0`.
The subsequent calculation:
$$\text{mulDivDown}(\text{WAD}, \text{amortizedValue} \times \text{ttm})$$
reverts with a division by zero error (`Panic(0x12)`), bricking legitimate execution paths for dust or zero-asset fills.

#### Recommended Remediation
1. Add an explicit check in `MidnightAdapterFactory.createAdapter` or `constructor`:
   ```solidity
   require(IERC20(asset).decimals() >= 6, UnsupportedAssetDecimals());
   ```
2. In `onBuy()`, require `amortizedValue > 0` before calculating `netRate`:
   ```solidity
   require(amortizedValue > 0, ZeroAmortizedValue());
   ```

---

## 4. Conclusion & Settlement Information

The `MidnightAdapter` architecture provides elegant linear discounting and fair in-kind redemption mechanics. Incorporating the terminal shortfall invariant check and asset decimal verification guarantees that vault accounting remains strictly conservative under all adverse market conditions.

- **Beneficiary Settlement Address (Base L2 / EVM):** `0x8366bCe3a2D379De7656D7A67015789FaF999f20`
- **Target Competition:** Cantina Morpho Midnight Adapter Audit Contest ($400,000 USDC)
