import unittest
from products.solana_seeker_mobile_pay.seeker_mobile_pay import SolanaSeekerMobilePay

class TestSolanaSeekerMobilePay(unittest.TestCase):
    def setUp(self):
        self.engine = SolanaSeekerMobilePay()

    def test_mwa_session_connection(self):
        resp = self.engine.connect_mwa_session({
            "name": "GenesisSeekerApp",
            "uri": "https://github.com/dextermos/genesis-bounty-hunter"
        })
        self.assertEqual(resp["status"], "CONNECTED")
        self.assertTrue(self.engine.session_active)
        self.assertIsNotNone(self.engine.authorized_wallet)

    def test_build_token2022_micropayment_tx(self):
        self.engine.connect_mwa_session({
            "name": "GenesisSeekerApp",
            "uri": "https://github.com/dextermos/genesis-bounty-hunter"
        })
        tx = self.engine.build_token2022_micropayment_tx(
            recipient_pubkey="Recv8366bCe3a2D379Dec7656D7A67015789FaF999f20",
            amount_tokens=25.5,
            mint_pubkey="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", # USDC
            compute_unit_price_micro_lamports=75_000
        )
        self.assertEqual(tx["type"], "SPL_TOKEN_2022_TRANSFER_CHECKED")
        self.assertTrue(tx["is_mtu_safe"])
        self.assertLess(tx["estimated_serialized_size_bytes"], 1232)
        self.assertEqual(len(tx["instructions"]), 2)
        self.assertEqual(len(self.engine.get_transaction_history()), 1)

    def test_unconnected_session_rejection(self):
        with self.assertRaises(PermissionError):
            self.engine.build_token2022_micropayment_tx(
                recipient_pubkey="Recv8366bCe3a2D379Dec7656D7A67015789FaF999f20",
                amount_tokens=10.0,
                mint_pubkey="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            )

if __name__ == '__main__':
    unittest.main()
