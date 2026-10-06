import unittest
from tools.x402_micropayment_gateway import X402MicropaymentGateway
from tools.ci_binary_proof_verifier import CiBinaryProofVerifier

class TestInstantPayoutTools(unittest.TestCase):
    def test_x402_micropayment_gateway(self):
        gateway = X402MicropaymentGateway()
        challenge = gateway.generate_402_challenge("/api/v1/smart-audit", custom_price_usdc=0.10)
        self.assertEqual(challenge["status_code"], 402)
        self.assertEqual(challenge["headers"]["X-402-Network"], "base")
        self.assertEqual(challenge["headers"]["X-402-Amount"], "0.1")

        settlement = gateway.verify_and_settle_x402_payment(
            payment_tx_hash="0xabcdef1234567890",
            payer_address="0xPayer1234",
            amount_paid_usdc=0.10,
            nonce=challenge["headers"]["X-402-Nonce"]
        )
        self.assertEqual(settlement["status"], "SETTLED_INSTANT")
        self.assertTrue(settlement["is_authorized"])

    def test_ci_binary_proof_verifier(self):
        verifier = CiBinaryProofVerifier()
        # Passing binary criteria
        proof = verifier.generate_binary_proof(
            bounty_id="frantic_agent_08",
            test_results={"passed": 24, "failed": 0},
            commit_sha="9f8e7d6c5b4a"
        )
        self.assertEqual(proof["binary_status"], "PASS")
        self.assertTrue(proof["is_claimable_instant"])
        self.assertTrue(proof["proof_hash"].startswith("0x"))

        # Failing binary criteria
        fail_proof = verifier.generate_binary_proof(
            bounty_id="frantic_agent_08",
            test_results={"passed": 20, "failed": 2},
            commit_sha="9f8e7d6c5b4a"
        )
        self.assertEqual(fail_proof["binary_status"], "FAIL")
        self.assertFalse(fail_proof["is_claimable_instant"])

if __name__ == '__main__':
    unittest.main()
