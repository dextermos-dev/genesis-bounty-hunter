# 🛡️ Hats Finance Security Vulnerability Disclosure: Eurodollar Protocol

- **Protocol Name:** Eurodollar (Rhinefield Technologies Limited)
- **Target Repository / Vault:** `hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd`
- **Target Contracts:**
  - `InvestToken.sol` (Commit / Tag: Rhinefield v1.0)
  - `YieldOracle.sol` (Commit / Tag: Rhinefield v1.0)
- **Author & Security Researcher:** Dexter Mos ([`@dextermos`](https://github.com/dextermos))
- **Settlement Wallet (USDC / ETH on Base L2 & Mainnet):** `0x8366bCe3a2D379De7656D7A67015789FaF999f20`
- **Date:** November 18, 2026

---

## Executive Summary

During our formal security analysis of the Eurodollar protocol's yield-bearing investment token (`InvestToken.sol`) and its pricing oracle (`YieldOracle.sol`), multiple severe vulnerabilities were identified:

1. **[CRITICAL] ERC-4626 Price Asymmetry & Unbacked Asset Extraction:**
   An asymmetry between `convertToShares()` (which queries `currentPrice`) and `convertToAssets()` (which queries `previousPrice`) allows an attacker to purchase shares cheaply via `mint()` and immediately redeem them for inflated assets via `withdraw()`, generating risk-free arbitrage and minting unbacked USDE.
2. **[HIGH] Arithmetic Underflow Panics in `commitPrice()` and `updatePrice()` (Denial of Service):**
   In Solidity `^0.8.21`, unchecked arithmetic checks `require(nextPrice - currentPrice >= 0)` and `require(price - currentPrice <= maxPriceIncrease)` cause immediate opcode `0x11` reverts (underflow panic) whenever `nextPrice < currentPrice` or during negative yields, permanently freezing the oracle.
3. **[MEDIUM] ERC-4626 Specification Invariant Violation:**
   `maxWithdraw()` computes maximum assets using `previousPrice` while `withdraw()` computes burned shares using `currentPrice`, causing inconsistency between the preview/limit APIs and actual execution logic.

---

## Finding 1: [CRITICAL] ERC-4626 Price Asymmetry Enables Infinite Unbacked USDE Extraction via `mint()` & `withdraw()`

### 1. Vulnerability Details

In `YieldOracle.sol`, conversion functions are defined as follows:

```solidity
// YieldOracle.sol lines 174-185
function assetsToShares(uint256 assets) external view returns (uint256) {
    return Math.mulDiv(assets, 10 ** 18, currentPrice);
}

function sharesToAssets(uint256 shares) external view returns (uint256) {
    return Math.mulDiv(shares, previousPrice, 10 ** 18);
}
```

Notice that `assetsToShares` uses **`currentPrice`**, whereas `sharesToAssets` uses **`previousPrice`**.

In `InvestToken.sol`, the standard ERC-4626 functions are implemented:

```solidity
// InvestToken.sol lines 278-284
function mint(uint256 shares, address receiver) public returns (uint256 assets) {
    assets = convertToAssets(shares); // <-- Uses sharesToAssets() -> PREVIOUS PRICE
    usde.burn(msg.sender, assets);
    _mint(receiver, shares);
    emit Deposit(msg.sender, receiver, assets, shares);
}

// InvestToken.sol lines 315-322
function withdraw(uint256 assets, address receiver, address owner) public returns (uint256 shares) {
    shares = convertToShares(assets); // <-- Uses assetsToShares() -> CURRENT PRICE
    if (owner != msg.sender) _spendAllowance(owner, msg.sender, shares);
    _burn(owner, shares);
    usde.mint(receiver, assets);      // <-- Mints newly created USDE to receiver!
    emit Withdraw(msg.sender, receiver, owner, assets, shares);
}
```

### 2. Attack Vector & Economic Impact

Whenever the oracle commits a price increase reflecting accrued yield (`currentPrice > previousPrice`):
1. The user acquires shares through `mint(shares, receiver)`. The required USDE cost is calculated using `convertToAssets(shares)`, which values each share at the outdated, cheaper `previousPrice`.
2. The user immediately calls `withdraw(assets, receiver, owner)` for an equivalent number of shares. In `withdraw`, the shares required to receive `assets` are calculated via `convertToShares(assets)`, which values each share at the higher `currentPrice`.
3. Because `usde.mint(receiver, assets)` issues fresh USDE on withdrawal, the attacker immediately extracts more USDE than the burned principal, extracting pure unbacked profit in a single atomic transaction.

### 3. Concrete Numerical Proof of Concept (PoC)

Assume the protocol state after an oracle price update:
- `previousPrice = 1.00e18` (1.00 USDE per share)
- `currentPrice = 1.10e18` (1.10 USDE per share, 10% accrued yield)
- Attacker holds $100,000\text{ USDE}$.

**Step 1: Exploit `mint()`**
- Attacker calls `InvestToken.mint(100_000e18, attacker)`.
- `assets = convertToAssets(100_000e18) = 100,000e18 * 1.00e18 / 1e18 = 100,000e18 USDE`.
- `usde.burn(attacker, 100,000e18)` burns $100,000\text{ USDE}$.
- Attacker receives $100,000\text{ EUI}$ shares.

**Step 2: Exploit `withdraw()`**
- Attacker immediately calls `InvestToken.withdraw(110_000e18, attacker, attacker)`.
- `shares = convertToShares(110_000e18) = 110,000e18 * 1e18 / 1.10e18 = 100,000e18 EUI`.
- `_burn(attacker, 100_000e18)` burns the $100,000\text{ EUI}$ shares.
- `usde.mint(attacker, 110_000e18)` mints $110,000\text{ USDE}$ to attacker.

**Result:**
- Attacker deposited $100,000\text{ USDE}$ and withdrew $110,000\text{ USDE}$.
- **Net Unbacked USDE Extracted:** $+10,000\text{ USDE}$ ($+10\%$ profit) in 0 blocks.
- This can be repeated or flash-loan leveraged to inflate USDE supply without backing assets.

---

## Finding 2: [HIGH] Arithmetic Underflow Panics in `commitPrice()` & `updatePrice()` (Denial of Service)

### 1. Vulnerability Details

Solidity `0.8.x` features built-in overflow/underflow checks that revert with panic code `0x11` upon underflow.

In `YieldOracle.sol`:

```solidity
// YieldOracle.sol line 91-92
function commitPrice() public {
    require(nextPrice - currentPrice >= 0, "Price out of bounds");
```

And:

```solidity
// YieldOracle.sol line 80
function updatePrice(uint256 price) external onlyOracle {
    ...
    require(price - currentPrice <= maxPriceIncrease, "Price out of bounds");
```

### 2. Flaws Identified

1. **Underflow in `commitPrice()`:**
   - If `commitPrice()` is invoked when `nextPrice < currentPrice` (or when `nextPrice == NO_PRICE` which is initialized to 0), `nextPrice - currentPrice` underflows and panics with `0x11` rather than reverting gracefully with `"Price out of bounds"`.
   - Furthermore, in unsigned arithmetic, any valid subtraction result is always `>= 0`, rendering the `>= 0` condition completely redundant.
2. **Inability to Lower Price on Market Loss / Negative Yield:**
   - If the protocol experiences negative yield, bad debt, or collateral devaluation and the oracle attempts to publish a lower price (`price < currentPrice`), `price - currentPrice` panics with underflow (`0x11`).
   - The contract cannot accept a decreased price via `updatePrice()`, causing an unrecoverable DoS to the oracle pricing pipeline.

---

## Finding 3: [MEDIUM] ERC-4626 Specification Invariant Violation in `maxWithdraw()`

In `InvestToken.sol`:
```solidity
function maxWithdraw(address owner) public view returns (uint256) {
    if (paused()) return 0;
    return convertToAssets(this.balanceOf(owner));
}
```
`maxWithdraw` uses `convertToAssets` (which computes based on `previousPrice`), whereas `withdraw` calculates required shares via `convertToShares` (which computes based on `currentPrice`). Consequently:
- A user holding $100\text{ shares}$ is told by `maxWithdraw` that their maximum withdrawal is $100\text{ USDE}$.
- However, calling `withdraw(110e18)` succeeds because it consumes $100\text{ shares}$.
- This breaks ERC-4626 conformance and breaks automated integrations (aggregators, routers, and yield vaults) that rely on `maxWithdraw` to size transactions.

---

## Recommended Remediation

### 1. Fix `YieldOracle.sol` Pricing Consistency
Ensure both `assetsToShares` and `sharesToAssets` operate consistently on `currentPrice`:

```solidity
function assetsToShares(uint256 assets) external view returns (uint256) {
    return Math.mulDiv(assets, 10 ** 18, currentPrice);
}

function sharesToAssets(uint256 shares) external view returns (uint256) {
    return Math.mulDiv(shares, currentPrice, 10 ** 18);
}
```

### 2. Fix Underflow Checks in `YieldOracle.sol`

Replace unchecked subtractions with explicit comparisons:

```solidity
function commitPrice() public {
    require(nextPrice != NO_PRICE, "No pending price update");
    require(nextPrice >= currentPrice, "Price out of bounds");
    require(lastUpdate + commitDelay < block.timestamp, "Insufficient commit delay");

    previousPrice = currentPrice;
    currentPrice = nextPrice;
    nextPrice = NO_PRICE;

    emit PriceCommitted(currentPrice);
}

function updatePrice(uint256 price) external onlyOracle {
    require(lastUpdate + updateDelay < block.timestamp, "Insufficient update delay");

    if (nextPrice != NO_PRICE) {
        previousPrice = currentPrice;
        currentPrice = nextPrice;
        emit PriceCommitted(currentPrice);
    }

    if (price >= currentPrice) {
        require(price - currentPrice <= maxPriceIncrease, "Price increase exceeds maximum");
    } else {
        // Handle negative yield / price decrease according to protocol bounds
        require(currentPrice - price <= maxPriceDecrease, "Price decrease exceeds maximum");
    }

    nextPrice = price;
    lastUpdate = block.timestamp;
    emit PriceUpdated(price);
}
```

---

## Disclosure Metadata & Settlement Details

- **Reporting Researcher:** Dexter Mos ([`@dextermos`](https://github.com/dextermos))
- **Settlement Wallet:** `0x8366bCe3a2D379De7656D7A67015789FaF999f20`
- **Supported Settlement Chains:** Base L2 / Ethereum Mainnet (USDC / ETH)
- **Status:** Complete & Ready for Hats Finance Submission
