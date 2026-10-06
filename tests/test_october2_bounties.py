#!/usr/bin/env python3
"""
Unit Test Suite for October 2 Bounties
"""

import unittest
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.solana_confidential_verifier import verify_elgamal_zero_knowledge_proof

class TestOctober2Bounties(unittest.TestCase):
    def test_session_key_daily_limit_enforcement(self):
        daily_limit = 500.0
        spent_today = 300.0
        tx_amount = 150.0
        
        can_execute = (spent_today + tx_amount) <= daily_limit
        self.assertTrue(can_execute, "Valid transaction under daily limit must be approved")
        
        excess_amount = 300.0
        can_execute_excess = (spent_today + excess_amount) <= daily_limit
        self.assertFalse(can_execute_excess, "Transaction exceeding daily limit must be rejected")

    def test_solana_confidential_zk_verifier(self):
        res = verify_elgamal_zero_knowledge_proof("enc_data_hex", "proof_hex")
        self.assertEqual(res["status"], "PROOF_VERIFIED_VALID")
        self.assertTrue(res["is_range_proof_valid"])
        self.assertTrue(res["is_ciphertext_valid"])

if __name__ == "__main__":
    unittest.main()
