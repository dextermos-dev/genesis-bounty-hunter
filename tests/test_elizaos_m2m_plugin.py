#!/usr/bin/env python3
"""
Unit tests for ElizaOS Zero-Gas M2M Micropayment Plugin
Author: @dextermos / @dextermos-dev
Settlement Address: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
"""

import unittest
from products.elizaos_m2m_plugin.eliza_zero_gas_m2m import ElizaZeroGasM2MPayments, MANDATORY_WALLET

class TestElizaOSM2MPlugin(unittest.TestCase):
    def setUp(self):
        self.engine = ElizaZeroGasM2MPayments()

    def test_create_invoice_success(self):
        inv = self.engine.create_m2m_invoice(
            payer_agent="0x1111111111111111111111111111111111111111",
            amount_usdc=25.0,
            service_desc="Agent Subtask Computation"
        )
        self.assertEqual(inv["status"], "PAYMENT_REQUIRED")
        self.assertEqual(inv["status_code"], 402)
        self.assertEqual(inv["amount_usdc"], 25.0)
        self.assertEqual(inv["recipient_agent"], MANDATORY_WALLET)
        self.assertEqual(inv["settlement_wallet"], MANDATORY_WALLET)

    def test_execute_settlement_success(self):
        inv = self.engine.create_m2m_invoice(
            payer_agent="0x2222222222222222222222222222222222222222",
            amount_usdc=100.0,
            service_desc="Dataset Vector Query"
        )
        res = self.engine.execute_gasless_settlement(inv, "0xvalid_signature")
        self.assertEqual(res["status"], "SETTLED")
        self.assertEqual(res["gas_cost_usd"], 0.0)
        self.assertEqual(res["paymaster_sponsored"], True)
        self.assertEqual(res["settlement_wallet"], MANDATORY_WALLET)
        self.assertTrue(res["transaction_hash"].startswith("0x"))

    def test_invalid_payer_rejection(self):
        with self.assertRaises(ValueError):
            self.engine.create_m2m_invoice(
                payer_agent="invalid_address",
                amount_usdc=10.0,
                service_desc="Invalid"
            )

    def test_negative_amount_rejection(self):
        with self.assertRaises(ValueError):
            self.engine.create_m2m_invoice(
                payer_agent="0x1111111111111111111111111111111111111111",
                amount_usdc=-10.0,
                service_desc="Negative Amount"
            )

if __name__ == '__main__':
    unittest.main()
