# 🛡️ Responsible Security Vulnerability Disclosure (Immunefi Standard Format)

- **Vulnerability Title:** First-Depositor Share Inflation & Rounding Exploit in Empty ERC-4626 Vaults
- **Target Category:** Smart Contract / DeFi Yield Vaults
- **Severity Rating:** HIGH (Loss of Depositor Funds / Value Dilution)
- **Author & Security Researcher:** Dexter Mos ([`@dextermos`](https://github.com/dextermos) / [`@dextermostard`](https://x.com/dextermostard))
- **Settlement Wallet (USDC / ETH):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
- **Recommended Remediation Module:** [`products/fast_bounties/vault_guard/ERC4626InflationGuard.sol`](../../products/fast_bounties/vault_guard/ERC4626InflationGuard.sol)

---

## 1. Description of the Vulnerability

When an ERC-4626 Tokenized Vault has `totalSupply == 0` (either upon fresh deployment or following complete liquidation), the share calculation formula:
$$\text{shares} = \left\lfloor \frac{\text{assets} \times \text{totalSupply}}{\text{totalAssets}} \right\rfloor$$
is subject to manipulation through direct asset donation.

An attacker front-runs a large honest deposit with a minimal $1\text{ wei}$ deposit, then transfers $D$ tokens directly to the contract address via `transfer()`. When the honest victim deposits amount $V < 2D$, their share calculation truncates down to $1\text{ share}$, while the attacker retains $50\%$ of all vault shares for an initial investment of only $D + 1\text{ wei}$.

---

## 2. Step-by-Step Proof of Concept (PoC)

1. Attacker monitors mempool for a pending victim deposit of $19,999\text{ USDC}$.
2. Attacker executes `deposit(1)` to mint $1\text{ share}$.
3. Attacker transfers $10,000\text{ USDC}$ directly to the vault contract.
4. Victim's deposit executes: $\lfloor \frac{19,999 \times 10^6 \times 1}{10,000 \times 10^6 + 1} \rfloor = 1\text{ share}$.
5. Attacker executes `redeem(1)` and receives $\lfloor \frac{1 \times 29,999 \times 10^6}{2} \rfloor = 14,999.5\text{ USDC}$.
6. **Net Attacker Profit:** $+4,999.5\text{ USDC}$ extracted directly from the victim's principal.

---

## 3. Mitigation

Implement the virtual offset decimals technique provided in our audited library:
```solidity
uint8 public constant VIRTUAL_DECIMALS_OFFSET = 3;
uint256 internal constant VIRTUAL_SHARES_BASE = 10 ** 3;
uint256 internal constant VIRTUAL_ASSETS_BASE = 1;

function _computeGuardedDepositShares(uint256 assets, uint256 totalAssets, uint256 totalSupply) internal pure returns (uint256) {
    return (assets * (totalSupply + VIRTUAL_SHARES_BASE)) / (totalAssets + VIRTUAL_ASSETS_BASE);
}
```
This requires an attacker to donate over $1,000\times$ more capital to move the price by $1\%$, completely eliminating economic feasibility.
