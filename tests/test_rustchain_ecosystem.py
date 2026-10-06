#!/usr/bin/env python3
import unittest
from products.rustchain_ecosystem.mining_calculator_and_status import RustChainMiningCalculator, RustChainNetworkStatus

class TestRustChainEcosystem(unittest.TestCase):
    def test_mining_calculator(self):
        calc = RustChainMiningCalculator(current_difficulty=1.0, network_hashrate_khs=1000.0)
        res = calc.calculate_daily_earnings(100.0)
        self.assertGreater(res["daily_rtc"], 0)
        self.assertGreater(res["daily_usd"], 0)
        self.assertEqual(res["settlement_wallet"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")

    def test_network_telemetry(self):
        telemetry = RustChainNetworkStatus()
        telemetry.register_peer("node_1", "192.168.1.10", 45.2, 10240)
        telemetry.register_peer("node_2", "192.168.1.11", 120.5, 10242)
        summary = telemetry.get_telemetry_summary()
        self.assertEqual(summary["total_nodes"], 2)
        self.assertEqual(summary["healthy_nodes"], 2)
        self.assertEqual(summary["max_block_height"], 10242)
        self.assertEqual(summary["settlement_wallet"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")

if __name__ == "__main__":
    unittest.main()
