#!/usr/bin/env python3
"""
Unit Test Suite for October 3 Bounties
"""

import unittest
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.solana_priority_estimator import estimate_priority_fee

class TestOctober3Bounties(unittest.TestCase):
    def test_priority_fee_percentile_calculation(self):
        fees = [1000, 2000, 3000, 4000, 5000]
        res = estimate_priority_fee(fees, percentile=80)
        self.assertEqual(res["status"], "ESTIMATED_SUCCESS")
        self.assertEqual(res["recommended_micro_lamports"], 4200)
        self.assertEqual(res["median_fee"], 3000)

    def test_empty_fallback(self):
        res = estimate_priority_fee([], percentile=75)
        self.assertEqual(res["status"], "FALLBACK")
        self.assertEqual(res["recommended_micro_lamports"], 50000)

if __name__ == "__main__":
    unittest.main()
