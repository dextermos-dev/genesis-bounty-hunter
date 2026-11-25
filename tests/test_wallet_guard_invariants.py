#!/usr/bin/env python3
"""
Unit Test Suite for Wallet Guard Invariants (tests/test_wallet_guard_invariants.py)
Guarantees zero tolerance against wallet typos, mutations, or truncated addresses.
"""

import unittest
from constants.wallets import (
    BASE_SETTLEMENT_WALLET,
    SOLANA_SETTLEMENT_WALLET,
    METAMASK_GAS_WALLET,
    validate_evm_address,
    validate_solana_address,
    assert_official_wallet,
    scan_text_for_corrupt_wallets
)
from tools.wallet_guard import audit_repository

class TestWalletGuardInvariants(unittest.TestCase):
    def test_canonical_constants_invariants(self):
        """Asegura que las constantes canónicas cumplen estrictamente las longitudes oficiales."""
        self.assertEqual(len(BASE_SETTLEMENT_WALLET), 42)
        self.assertTrue(BASE_SETTLEMENT_WALLET.startswith("0x"))
        self.assertTrue(validate_evm_address(BASE_SETTLEMENT_WALLET))

        self.assertEqual(len(METAMASK_GAS_WALLET), 42)
        self.assertTrue(METAMASK_GAS_WALLET.startswith("0x"))
        self.assertTrue(validate_evm_address(METAMASK_GAS_WALLET))

        self.assertEqual(len(SOLANA_SETTLEMENT_WALLET), 44)
        self.assertTrue(validate_solana_address(SOLANA_SETTLEMENT_WALLET))

    def test_rejection_of_blacklisted_typo(self):
        """Asegura que el error histórico 'Dec' sea detectado y rechazado con excepción crítica."""
        typo_wallet = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"
        self.assertEqual(len(typo_wallet), 43)
        self.assertFalse(validate_evm_address(typo_wallet))

        with self.assertRaises(ValueError):
            assert_official_wallet(typo_wallet, chain="base")

    def test_scan_text_catches_mutations(self):
        """Asegura que el escáner de texto intercepte mutaciones en comentarios o payloads."""
        bad_comment = "/claim 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20 for bounty"
        findings = scan_text_for_corrupt_wallets(bad_comment)
        self.assertTrue(len(findings) > 0)

        clean_comment = f"/claim {BASE_SETTLEMENT_WALLET} for bounty"
        self.assertEqual(len(scan_text_for_corrupt_wallets(clean_comment)), 0)

    def test_entire_codebase_clean(self):
        """Verifica que el repositorio completo no contiene violaciones activas de wallet."""
        exit_code = audit_repository(".")
        self.assertEqual(exit_code, 0)

if __name__ == "__main__":
    unittest.main()
