import unittest
from products.cyfrin_audit_mcp.sherlock_c4_mcp_auditor import SherlockC4McpAuditor

class TestCyfrinMcpAuditor(unittest.TestCase):
    def setUp(self):
        self.auditor = SherlockC4McpAuditor()

    def test_list_vulnerability_patterns_filters(self):
        # Query by protocol
        res_vault = self.auditor.list_vulnerability_patterns(protocol_type="ERC4626")
        self.assertGreaterEqual(res_vault["total_matches"], 1)
        self.assertEqual(res_vault["patterns"][0]["vulnerability_class"], "FIRST_DEPOSITOR_INFLATION")

        # Query by severity
        res_high = self.auditor.list_vulnerability_patterns(severity="HIGH")
        self.assertTrue(all(p["severity"] == "HIGH" for p in res_high["patterns"]))

        # Query by keyword search
        res_search = self.auditor.list_vulnerability_patterns(search_query="reentrancy")
        self.assertGreaterEqual(res_search["total_matches"], 1)

    def test_invalid_input_validation(self):
        with self.assertRaises(ValueError):
            self.auditor.list_vulnerability_patterns(severity="INVALID_SEVERITY")

        with self.assertRaises(TypeError):
            self.auditor.list_vulnerability_patterns(protocol_type=12345)

    def test_scan_code_heuristics(self):
        vulnerable_vault_code = """
        contract InsecureVault is ERC4626 {
            function deposit(uint256 assets) external returns (uint256) {
                uint256 shares = convertToShares(assets);
                return shares;
            }
        }
        """
        scan_res = self.auditor.scan_code_for_patterns(vulnerable_vault_code)
        self.assertEqual(scan_res["scan_status"], "COMPLETED")
        self.assertGreaterEqual(scan_res["findings_count"], 1)
        self.assertEqual(scan_res["findings"][0]["finding_ref"], "C4-ERC4626-001")

if __name__ == '__main__':
    unittest.main()
