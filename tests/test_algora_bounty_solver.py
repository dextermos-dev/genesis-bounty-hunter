import unittest
from products.algora_bounty_solver.algora_solver import AlgoraBountySolver


class TestAlgoraBountySolver(unittest.TestCase):
    def setUp(self):
        self.solver = AlgoraBountySolver()

    def test_attempt_comment(self):
        comment = self.solver.generate_attempt_comment("dextermos-dev")
        self.assertIn("/attempt", comment)
        self.assertIn("@dextermos-dev", comment)

    def test_pr_submission_generation(self):
        payload = self.solver.generate_pull_request_submission(
            42,
            "Fix race condition in session key manager",
            "Added mutex lock and deterministic nonce verification."
        )
        self.assertEqual(payload["title"], "fix(core): resolve #42 - Fix race condition in session key manager")
        self.assertIn("/claim 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20", payload["body"])
        self.assertEqual(payload["settlement_wallet"], "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20")
        self.assertTrue(payload["ready_for_review"])


if __name__ == "__main__":
    unittest.main()
