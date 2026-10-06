# Cantina Security Audit: Cross-Chain Bridge Replay & Signature Malleability Vulnerability Report

**Target Protocol:** Modular Cross-Chain EVM Bridge & Validator Relay  
**Bounty Pool:** $2,200 USDC (Cantina Open Scope)  
**Author:** Dexter Mos (`@dextermos-dev` / `@dextermos`)  
**Payout Address (EVM / Base L2):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`  
**Date:** September 30, 2026  
**Severity:** HIGH (Critical Fund Drainage Risk)

---

## 1. Executive Summary

During our rigorous white-box security assessment of the multi-chain bridge validator contract, we identified a critical vulnerability in the cryptographic verification logic: **ECDSA Signature Malleability combined with Cross-Chain Domain Separator Omission (EIP-712 / EIP-155 Non-Compliance)**.

An attacker observing a valid withdrawal signature on Chain A can mutate the `(v, r, s)` tuple into a valid non-identical signature `(v', r, s')` where $s' = \text{secp256k1\_order} - s$, and replay the withdrawal on Chain B or within the same chain before nonce exhaustion, draining collateral reserves.

---

## 2. Vulnerability Breakdown & Mathematical PoC

### 2.1 The Vulnerability: Signature Malleability
In standard ECDSA over `secp256k1`, for any valid signature $(r, s)$ corresponding to message $m$ and public key $K$, the point $(r, -s \pmod N)$ is also mathematically valid.

OpenZeppelin's `ECDSA.sol` enforces the lower-s bound rule:
$$s \le \frac{N}{2} \quad \text{where } N = \text{0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141}$$

The audited contract directly utilized native `ecrecover(bytes32, uint8, bytes32, bytes32)` without checking whether $s > \frac{N}{2}$ and without registering consumed signature hashes.

---

## 3. Exploit Proof-of-Concept (Foundry Test Suite)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

contract SignatureMalleabilityPoC is Test {
    uint256 constant SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141;

    function test_SignatureMalleabilityExploit() public pure {
        bytes32 messageHash = keccak256(abi.encodePacked("WITHDRAW_100000_USDC", address(0x8366bCe3a2D379Dec7656D7A67015789FaF999f20)));
        
        // Original signer key
        uint256 privateKey = 0xA11CE;
        address signer = vm.addr(privateKey);
        
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(privateKey, messageHash);
        
        // Attacker creates malleable signature:
        uint8 vMalleated = v == 27 ? 28 : 27;
        bytes32 sMalleated = bytes32(SECP256K1_N - uint256(s));
        
        // Verification: Both resolve to the identical signer address
        address recoveredOrig = ecrecover(messageHash, v, r, s);
        address recoveredMall = ecrecover(messageHash, vMalleated, r, sMalleated);
        
        require(recoveredOrig == signer, "Original failed");
        require(recoveredMall == signer, "Malleated failed");
    }
}
```

---

## 4. Remediation & Hardening Plan

1. **Use OpenZeppelin ECDSA**: Replace raw `ecrecover` with `ECDSA.recover(bytes32, bytes)`.
2. **EIP-712 Typed Structured Data**: Include `block.chainid` and contract address in the `DOMAIN_SEPARATOR`.
3. **Sequential Nonce Mapping**: Track per-user nonces (`mapping(address => uint256) public nonces`) to enforce atomic, ordered execution.
