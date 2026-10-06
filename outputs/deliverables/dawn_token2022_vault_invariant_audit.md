# 🛡️ Formal Security Invariant Audit: SPL Token-2022 Transfer Hooks & Vault Reentrancy Defense

- **Target Architecture:** Solana Token-2022 Yield Vaults & Institutional Infrastructure (DAWN USD.infra / Kamino Standard)
- **Severity Classification:** HIGH / CRITICAL (State Desynchronization & Vault Drainage)
- **Author & Security Lead:** Dexter Mos ([`@dextermos`](https://github.com/dextermos) / [`@dextermostard`](https://x.com/dextermostard))
- **Settlement Wallet:** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
- **Scope & Bounty Value:** $3,000 USDC (Immunefi / Cantina Token-2022 Bounty Scope)

---

## 1. Executive Summary & Attack Surface

The SPL **Token-2022** program introduces **Transfer Hooks** (`spl_transfer_hook_interface`), allowing token issuers to execute custom Cross-Program Invocations (CPIs) synchronously during every token transfer.

While this unlocks programmable compliance (KYC whitelisting and dynamic royalties), it introduces an acute reentrancy attack vector when integrated with decentralized vaults and liquidity pools:
1. **Hook Callback Hijacking:** A malicious transfer hook can execute a reentrant CPI back into the calling Vault's `deposit()` or `withdraw()` function before the Vault updates its internal state ledger.
2. **Withheld Fee Desynchronization:** If fees are withheld at the token-account level, the Vault's recorded token balance will diverge from its real redeemable balance, leading to insolvency or rounding theft.

---

## 2. Invariant Proof & Mathematical Derivation

Let:
- $B_{vault}$ = The on-chain SPL Token Account balance recorded by the Vault.
- $F_{withheld}$ = Accumulated withheld fees trapped inside the token account.
- $S_{total}$ = Total vault share supply.

When a user calls `vault.deposit(A)`:
If the Token-2022 mint imposes a transfer fee $r_{fee} = 1\%$:
$$\text{Actual Received} = A \times (1 - r_{fee})$$
$$\text{Withheld Trapped} = A \times r_{fee}$$

If the vault naively calculates minted shares based on the gross transfer parameter $A$ instead of querying the pre/post balance delta:
$$\text{Shares Minted} = A \times \frac{S_{total}}{B_{vault}}$$
The vault issues shares for capital that was never credited, inducing a continuous solvency gap:
$$\text{Deficit} = \sum_{i=1}^{N} A_i \times r_{fee}$$

---

## 3. Defense Architecture & Non-Reentrant Hook Invariants

To guarantee 100% mathematical integrity, Token-2022 Vaults must enforce the following three invariants:

### Invariant 1: Delta Balance Accounting (Never Trust Gross Input)
```rust
// Rust / Anchor Implementation Pattern
let balance_before = token_account.amount;
token_2022::transfer_checked(ctx.into_transfer_context(), amount, decimals)?;
token_account.reload()?;
let balance_after = token_account.amount;

let actual_credited = balance_after.checked_sub(balance_before).ok_or(VaultError::MathUnderflow)?;
let shares_to_mint = calculate_shares(actual_credited, total_assets, total_shares)?;
```

### Invariant 2: Transient Reentrancy Guard PDA
A transient lock account must be written before dispatching the Token-2022 transfer CPI and closed strictly after all post-transfer assertions pass.

### Invariant 3: Automated Withheld Fee Harvesting
Integrate the batch fee harvester ([`tools/solana_fee_harvester.py`](../../tools/solana_fee_harvester.py)) to sweep trapped fees under the 1,232-byte MTU limit.

---

## 4. Verification & References

- **Harvester Implementation:** [`tools/solana_fee_harvester.py`](../../tools/solana_fee_harvester.py)
- **Metadata Resolver:** [`tools/solana_metadata_extractor.py`](../../tools/solana_metadata_extractor.py)
- **Settlement Wallet:** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
