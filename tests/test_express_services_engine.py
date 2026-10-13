"""
Unit Tests for ExpressServicesEngine
"""

import unittest
from tools.express_services_engine import ExpressServicesEngine


class TestExpressServicesEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ExpressServicesEngine()

    def test_01_catalog_and_order_creation(self):
        self.assertTrue(len(self.engine.SERVICES_CATALOG) >= 3)
        res = self.engine.create_escrow_service_order(
            service_id="SVC-AUDIT-24H",
            client_id="defi_protocol_alpha",
            repo_url="https://github.com/defi/contracts"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["order"]["settlement_wallet"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")
        self.assertEqual(res["order"]["price_usdc"], 500.0)

    def test_02_order_fulfillment(self):
        res = self.engine.create_escrow_service_order(
            service_id="SVC-AGENT-PLUGIN",
            client_id="ai_agent_dao",
            repo_url="https://github.com/ai/agents"
        )
        order_id = res["order"]["order_id"]
        fulfill = self.engine.fulfill_service_order(order_id, "outputs/deliverables/sample_audit.md")
        self.assertTrue(fulfill["success"])
        self.assertEqual(fulfill["beneficiary"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")
        self.assertEqual(fulfill["status"], "DELIVERED_RELEASE_ESCROW")


if __name__ == "__main__":
    unittest.main()
