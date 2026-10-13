"""
Unit Tests for Base L2 Agent Micropayment Gateway (100% Coverage)
"""

import unittest
import time
from products.base_agent_gateway.base_agent_settler import BaseAgentGateway


class TestBaseAgentGateway(unittest.TestCase):
    def setUp(self):
        self.gateway = BaseAgentGateway()

    def test_01_quote_generation(self):
        quote = self.gateway.generate_x402_quote(task_id="task-bounty-88", cost_usdc=250.0)
        self.assertEqual(quote["status_code"], 402)
        self.assertEqual(quote["recipient_wallet"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")
        self.assertEqual(quote["cost_usdc"], 250.0)
        self.assertTrue(len(quote["quote_signature"]) > 10)

    def test_02_payment_verification_and_settlement(self):
        quote = self.gateway.generate_x402_quote(task_id="task-bounty-88", cost_usdc=250.0)
        valid_tx = "0x" + "a" * 64
        verif = self.gateway.verify_payment_and_open_channel(
            quote=quote,
            tx_hash=valid_tx,
            sender_address="0x1111111111111111111111111111111111111111"
        )
        self.assertTrue(verif["success"])
        channel_id = verif["channel_id"]

        # Settle subtask
        subtask_data = {"status": "SUCCESS", "lines_audited": 1500, "bounty_id": "88"}
        settle_res = self.gateway.execute_subtask_settlement(channel_id, subtask_data)
        self.assertTrue(settle_res["success"])
        self.assertEqual(settle_res["beneficiary"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")
        self.assertEqual(settle_res["payout_amount_usdc"], 250.0)

    def test_03_invalid_tx_rejection(self):
        quote = self.gateway.generate_x402_quote(task_id="task-invalid", cost_usdc=10.0)
        invalid_verif = self.gateway.verify_payment_and_open_channel(
            quote=quote,
            tx_hash="invalid_tx_hash",
            sender_address="0x1111111111111111111111111111111111111111"
        )
        self.assertFalse(invalid_verif["success"])


if __name__ == "__main__":
    unittest.main()
