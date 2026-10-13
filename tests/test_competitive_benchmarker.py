import unittest
from tools.competitive_benchmarker import CompetitiveBenchmarker


class TestCompetitiveBenchmarker(unittest.TestCase):
    def setUp(self):
        self.benchmarker = CompetitiveBenchmarker()

    def test_initialization(self):
        self.assertEqual(self.benchmarker.OFFICIAL_SETTLEMENT_WALLET, "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")
        self.assertTrue(self.benchmarker.benchmark_metrics["zero_flaky_tests"])

    def test_analyze_flawed_competitor(self):
        competitor = {
            "competitor_id": "weak_coder",
            "has_tests": False,
            "test_coverage": 0.0,
            "has_security_guards": False,
            "has_math_formulation": False
        }
        res = self.benchmarker.analyze_competitor_flaws(competitor)
        self.assertIn("INSUFFICIENT_OR_MISSING_TEST_SUITE", res["flaws_detected"])
        self.assertIn("MISSING_NONCE_OR_REPLAY_PROTECTION", res["flaws_detected"])
        self.assertIn("LACKS_FORMAL_MATHEMATICAL_MODEL", res["flaws_detected"])
        self.assertGreater(res["win_probability_boost"], 0.8)

    def test_superiority_matrix_generation(self):
        rivals = [
            {"competitor_id": "rival_1", "has_tests": False, "test_coverage": 0.0},
            {"competitor_id": "rival_2", "has_tests": True, "test_coverage": 0.4}
        ]
        matrix = self.benchmarker.generate_superiority_matrix("bounty_test_1", rivals)
        self.assertEqual(matrix["competitors_evaluated"], 2)
        self.assertGreaterEqual(matrix["total_competitor_flaws_exploited"], 2)
        self.assertEqual(matrix["our_standards"]["settlement_wallet"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")


if __name__ == "__main__":
    unittest.main()
