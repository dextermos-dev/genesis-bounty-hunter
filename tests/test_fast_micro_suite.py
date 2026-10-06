#!/usr/bin/env python3
"""
Unit Test Suite for Additional Instant Micro-Bounties
"""

import unittest
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from products.fast_bounties.instant_merge.userop_gas_estimator import estimate_userop_gas_limits
from products.fast_bounties.instant_merge.solana_hook_guard import TransferHookReentrancyGuard

class TestFastMicroSuite(unittest.TestCase):
    def test_userop_gas_estimator(self):
        res = estimate_userop_gas_limits(call_data_len=128, verification_complexity=1)
        self.assertEqual(res["status"], "ESTIMATION_VALID")
        self.assertEqual(res["preVerificationGas"], 21000 + (128 * 16))
        self.assertEqual(res["payout_address"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")

    def test_transfer_hook_reentrancy_protection(self):
        guard = TransferHookReentrancyGuard()
        res = guard.execute_hook("0xSrc", "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20", 50.0)
        self.assertEqual(res["status"], "HOOK_EXECUTED_SAFE")
        self.assertTrue(res["reentrancy_safe"])

if __name__ == "__main__":
    unittest.main()
