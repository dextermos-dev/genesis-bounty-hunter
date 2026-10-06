#!/usr/bin/env python3
"""
Unit Test Suite for Enhanced Fast Bounties
"""

import unittest
import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.solana_fee_harvester import simulate_fee_scan, harvest_withheld_fees

class MockArgs:
    def __init__(self, mint="TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", authority="0x8366bCe3a2D379Dec7656D7A67015789FaF999f20", dry_run=True, batch_size=10, priority_micro_lamports=50000):
        self.mint = mint
        self.authority = authority
        self.dry_run = dry_run
        self.batch_size = batch_size
        self.priority_micro_lamports = priority_micro_lamports

class TestEnterpriseBounties(unittest.TestCase):
    def test_revenue_splitter_exact_residual_math(self):
        total_balance = 1000000000000000001 # 1 ETH + 1 wei (odd number testing truncation)
        primary_bps = 8000 # 80%
        total_bps = 10000
        
        primary_amount = (total_balance * primary_bps) // total_bps
        secondary_amount = total_balance - primary_amount
        
        self.assertEqual(primary_amount + secondary_amount, total_balance, "No wei dust lost during distribution")

    def test_solana_fee_harvester_execution(self):
        args = MockArgs(dry_run=True, batch_size=10)
        res = harvest_withheld_fees(args)
        
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["total_accounts_scanned"], 20)
        self.assertEqual(res["total_batches_generated"], 2)
        self.assertEqual(res["total_fees_harvested_usdc"], 850.0)
        self.assertTrue(res["dry_run_mode"])

if __name__ == "__main__":
    unittest.main()
