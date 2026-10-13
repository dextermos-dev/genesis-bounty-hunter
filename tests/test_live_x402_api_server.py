"""
Unit Tests for LiveX402MicroServiceServer (RFC-x402 M2M Monetization)
"""

import unittest
from tools.live_x402_api_server import LiveX402MicroServiceServer


class TestLiveX402MicroServiceServer(unittest.TestCase):
    def setUp(self):
        self.server = LiveX402MicroServiceServer()

    def test_01_http_402_challenge(self):
        res = self.server.handle_request("/api/v1/shield/url", {"url": "https://example.com"})
        self.assertEqual(res["status"], 402)
        self.assertIn("x402_quote", res)
        self.assertEqual(res["x402_quote"]["recipient_wallet"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")
        self.assertEqual(res["x402_quote"]["cost_usdc"], 0.50)

    def test_02_paid_request_execution(self):
        valid_tx = "0x" + "b" * 64
        res = self.server.handle_request(
            endpoint="/api/v1/shield/url",
            payload={"url": "https://github.com/dextermos-dev/genesis-bounty-hunter"},
            auth_payment_header=f"Base-x402 {valid_tx}"
        )
        self.assertEqual(res["status"], 200)
        self.assertTrue(res["data"]["is_safe"])
        self.assertEqual(res["receipt"]["beneficiary"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")
        self.assertEqual(res["receipt"]["cost_usdc"], 0.50)
        self.assertEqual(self.server.total_revenue_collected, 0.50)


if __name__ == "__main__":
    unittest.main()
