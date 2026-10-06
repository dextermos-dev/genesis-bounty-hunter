import unittest
from tools.base_l2_liquidator_bot import BaseL2LiquidatorBot
from tools.bountycaster_fast_resolver import BountycasterFastResolver
from tools.solana_arbitrage_harvester import SolanaArbitrageHarvester

class TestFastMonetizationEngines(unittest.TestCase):
    def test_base_l2_liquidator_bot(self):
        bot = BaseL2LiquidatorBot()
        # Healthy position: $10k collateral, $5k debt -> HF = (10k * 0.8) / 5k = 1.6
        res_healthy = bot.scan_position("0x1111", "cbETH", 10_000, "USDC", 5_000)
        self.assertFalse(res_healthy["is_liquidatable"])
        self.assertEqual(res_healthy["health_factor"], 1.6)

        # Unhealthy position: $5k collateral, $5k debt -> HF = (5k * 0.8) / 5k = 0.8 (< 1.0)
        res_unhealthy = bot.scan_position("0x2222", "cbETH", 5_000, "USDC", 5_000, bonus_pct=0.08)
        self.assertTrue(res_unhealthy["is_liquidatable"])
        self.assertEqual(res_unhealthy["health_factor"], 0.8)
        self.assertEqual(res_unhealthy["repay_amount_usd"], 2500.0) # 50% close factor
        self.assertEqual(res_unhealthy["estimated_profit_usdc"], 200.0) # 8% bonus on $2,500 = $200

        # Build tx payload
        tx = bot.build_liquidation_tx(res_unhealthy)
        self.assertTrue(tx["is_ready_to_broadcast"])
        self.assertEqual(tx["expected_usdc_reward"], 200.0)

    def test_bountycaster_fast_resolver(self):
        resolver = BountycasterFastResolver()
        cast = resolver.format_submission_cast(
            bounty_id="942",
            poster_username="vitalik",
            reward_amount_usd=50.0,
            solution_repo_url="https://github.com/dextermos/genesis-bounty-hunter",
            summary_text="Implemented ERC-7579 Session Key Module."
        )
        self.assertTrue(cast["is_valid_length"])
        self.assertIn("0x8366bCe3a2D379Dec7656D7A67015789FaF999f20", cast["cast_text"])

    def test_solana_arbitrage_harvester(self):
        harvester = SolanaArbitrageHarvester()
        # Pool A = $150.00, Pool B = $151.50 -> 1% spread on $1,000 = $10 gross profit
        spread = harvester.evaluate_spread("SOL/USDC", 150.0, 151.5, trade_size_usd=1000.0)
        self.assertTrue(spread["is_profitable"])
        self.assertGreater(spread["net_profit_usd"], 9.0)

if __name__ == '__main__':
    unittest.main()
