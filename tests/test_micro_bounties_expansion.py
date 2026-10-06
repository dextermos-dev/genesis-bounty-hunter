import unittest
from tools.solana_metadata_extractor import SolanaMetadataExtractor
from tools.rpc_resilient_failover import ResilientRpcFailover

class TestMicroBountiesExpansion(unittest.TestCase):
    def test_solana_metadata_extractor(self):
        extractor = SolanaMetadataExtractor(cache_enabled=True)
        # Test mock extraction
        res = extractor.extract_metadata("So11111111111111111111111111111111111111112", {
            "name": "Wrapped SOL",
            "symbol": "SOL",
            "uri": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png"
        })
        self.assertEqual(res["name"], "Wrapped SOL")
        self.assertEqual(res["symbol"], "SOL")
        
        # Test cache hit
        cached_res = extractor.extract_metadata("So11111111111111111111111111111111111111112")
        self.assertEqual(cached_res["name"], "Wrapped SOL")

    def test_rpc_resilient_failover(self):
        endpoints = [
            "https://mainnet.base.org",
            "https://base-rpc.publicnode.com",
            "https://1rpc.io/base"
        ]
        failover = ResilientRpcFailover("base", endpoints)
        pref = failover.get_preferred_endpoint()
        self.assertIn(pref, endpoints)

        # Simulate latency change
        failover.record_rpc_call("https://1rpc.io/base", success=True, latency_ms=10.0)
        failover.record_rpc_call("https://mainnet.base.org", success=True, latency_ms=150.0)
        
        # 1rpc should now be preferred due to lower latency
        self.assertEqual(failover.get_preferred_endpoint(), "https://1rpc.io/base")

        # Simulate failure and circuit breaker
        failover.record_rpc_call("https://1rpc.io/base", success=False, latency_ms=10.0, error_code=429)
        self.assertNotEqual(failover.get_preferred_endpoint(), "https://1rpc.io/base")

if __name__ == '__main__':
    unittest.main()
