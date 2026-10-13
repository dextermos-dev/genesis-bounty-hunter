"""
Unit Tests for WebacyAgentShield Due Diligence Engine (100% Coverage)
"""

import unittest
from products.webacy_integration.webacy_agent_shield import WebacyAgentShield


class TestWebacyAgentShield(unittest.TestCase):
    def setUp(self):
        self.shield = WebacyAgentShield()

    def test_01_url_risk_evaluation(self):
        safe_url = "https://github.com/dextermos-dev/genesis-bounty-hunter"
        res_safe = self.shield.evaluate_url_safety(safe_url)
        self.assertTrue(res_safe["is_safe"])
        self.assertEqual(res_safe["category"], "CLEAN_LEGITIMATE")

        malicious_url = "https://wallet-connect-fake.xyz/drainer"
        res_bad = self.shield.evaluate_url_safety(malicious_url)
        self.assertFalse(res_bad["is_safe"])
        self.assertEqual(res_bad["category"], "MALICIOUS_DRAINER")

    def test_02_address_threat_evaluation(self):
        safe_wallet = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"
        res = self.shield.evaluate_address_threat(safe_wallet, chain="base")
        self.assertEqual(res["action"], "ALLOW")
        self.assertEqual(res["exposure_level"], "LOW_RISK_SAFE")

    def test_03_contract_and_holder_analysis(self):
        contract_res = self.shield.evaluate_smart_contract_risk("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", chain="solana")
        self.assertEqual(contract_res["status"], "APPROVED_FOR_AGENT_INTERACTION")

        holder_res = self.shield.evaluate_token_holder_distribution("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", chain="solana")
        self.assertFalse(holder_res["is_concentrated_sniper_risk"])
        self.assertEqual(holder_res["status"], "SAFE_FOR_SWAP_OR_SETTLEMENT")


if __name__ == "__main__":
    unittest.main()
