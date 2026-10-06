#!/usr/bin/env python3
"""
Unit Test Suite for Instant-Merge Micro Bounties
"""

import unittest
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from products.fast_bounties.instant_merge.metadata_guard import serialize_token2022_metadata, deserialize_and_verify

class TestInstantMergeBounties(unittest.TestCase):
    def test_metadata_serialization_roundtrip(self):
        name = "Instant USDC Vault"
        symbol = "iUSDC"
        uri = "https://base.org/meta.json"
        
        raw_bytes = serialize_token2022_metadata(name, symbol, uri)
        res = deserialize_and_verify(raw_bytes)
        
        self.assertEqual(res["status"], "VALID_METADATA")
        self.assertEqual(res["name"], name)
        self.assertEqual(res["symbol"], symbol)
        self.assertEqual(res["payout_address"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")

if __name__ == "__main__":
    unittest.main()
