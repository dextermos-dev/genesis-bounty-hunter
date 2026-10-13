"""
Unit Tests for Solana Anchor Guard Auditor & LiteSVM Generator
"""

import unittest
from products.solana_anchor_guard.anchor_guard import AnchorGuardAuditor


class TestAnchorGuardAuditor(unittest.TestCase):
    def setUp(self):
        self.auditor = AnchorGuardAuditor()

    def test_01_detect_vulnerabilities(self):
        vulnerable_code = """
        use anchor_lang::prelude::*;

        #[derive(Accounts)]
        pub struct Withdraw<'info> {
            pub authority: AccountInfo<'info>, // Missing signer
            pub vault: Account<'info, TokenAccount>,
            pub target: AccountInfo<'info>, // Unchecked AccountInfo
        }
        """
        audit_res = self.auditor.audit_source_code(vulnerable_code)
        self.assertFalse(audit_res["is_secure"])
        self.assertTrue(audit_res["total_findings"] >= 2)
        self.assertEqual(audit_res["settlement_wallet"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")

    def test_02_secure_code_passes(self):
        secure_code = """
        use anchor_lang::prelude::*;

        #[derive(Accounts)]
        pub struct Withdraw<'info> {
            pub authority: Signer<'info>,
            #[account(has_one = authority)]
            pub vault: Account<'info, TokenAccount>, // validated
        }
        """
        audit_res = self.auditor.audit_source_code(secure_code)
        self.assertTrue(audit_res["is_secure"])
        self.assertEqual(audit_res["total_findings"], 0)
        self.assertEqual(audit_res["score"], 100)

    def test_03_litesvm_generation(self):
        test_code = self.auditor.generate_litesvm_test("EscrowProgram", ["Maker", "Taker", "Vault"])
        self.assertIn("EscrowProgram", test_code)
        self.assertIn("0x8366bCe3a2D379Dec7656D7A67015789FaF999f20", test_code)
        self.assertIn("LiteSVM", test_code)


if __name__ == "__main__":
    unittest.main()
