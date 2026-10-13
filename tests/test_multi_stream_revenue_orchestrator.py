"""
Unit Tests for MultiStreamRevenueOrchestrator
"""

import unittest
from tools.multi_stream_revenue_orchestrator import MultiStreamRevenueOrchestrator


class TestMultiStreamRevenueOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = MultiStreamRevenueOrchestrator()

    def test_01_summary_structure(self):
        summary = self.orchestrator.get_orchestrator_summary()
        self.assertEqual(summary["total_streams_active"], 5)
        self.assertEqual(summary["settlement_wallet"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")
        self.assertIn("Base L2", summary["supported_settlement_chains"])

    def test_02_stream_readiness(self):
        streams = self.orchestrator.streams_status
        self.assertIn("stream_1_grants_hackathons", streams)
        self.assertIn("stream_2_instant_bot_bounties", streams)
        self.assertIn("stream_3_escrow_services", streams)
        self.assertIn("stream_4_m2m_x402_api", streams)
        self.assertIn("stream_5_fee_relaying", streams)

    def test_03_competitive_benchmarking_audit(self):
        rivals = [{"competitor_id": "rival_alpha", "has_tests": False}]
        audit = self.orchestrator.execute_competitive_audit("bounty_october", rivals)
        self.assertEqual(audit["bounty_id"], "bounty_october")
        self.assertEqual(audit["competitors_evaluated"], 1)
        self.assertIn("our_standards", audit)


if __name__ == "__main__":
    unittest.main()

