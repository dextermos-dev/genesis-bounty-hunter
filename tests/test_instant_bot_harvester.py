"""
Unit Tests for InstantBotHarvester
"""

import unittest
from tools.instant_bot_harvester import InstantBotHarvester


class TestInstantBotHarvester(unittest.TestCase):
    def setUp(self):
        self.harvester = InstantBotHarvester()

    def test_01_detect_algora_bot(self):
        issue_data = {
            "url": "https://github.com/example/repo/issues/42",
            "title": "Fix memory leak in Rust worker",
            "body": "Bounty of $150 USDC available via Algora. Use /claim to apply.",
            "comments": ["algora-bot has added $150 USDC reward to this issue"],
            "reward_amount": 150.0,
            "currency": "USDC"
        }
        res = self.harvester.evaluate_issue_bot_compatibility(issue_data)
        self.assertTrue(res["is_instant_payout"])
        self.assertEqual(res["bot_detected"], "algora-bot")
        self.assertEqual(res["settlement_wallet"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")

    def test_02_generate_claim_comment(self):
        comment = self.harvester.prepare_instant_claim_comment("algora-bot", "https://github.com/example/repo/pull/43")
        self.assertIn("/claim", comment)
        self.assertIn("0x8366bCe3a2D379Dec7656D7A67015789FaF999f20", comment)

    def test_03_non_instant_issue(self):
        issue_data = {
            "url": "https://github.com/example/repo/issues/100",
            "title": "Discussion on tokenomics",
            "body": "No bot here, just an idea.",
            "comments": [],
            "reward_amount": 0.0
        }
        res = self.harvester.evaluate_issue_bot_compatibility(issue_data)
        self.assertFalse(res["is_instant_payout"])


if __name__ == "__main__":
    unittest.main()
