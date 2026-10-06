#!/usr/bin/env python3
"""
Unit test to enforce Golden Rule #4: Mandatory Settlement Wallet Verification.
Asserts that every deliverable, reinforcement script, and submission payload contains
the valid settlement address: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
"""

import os
import unittest

WALLET = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"

class TestMandatoryWalletRule(unittest.TestCase):
    def test_wallet_present_in_agents_md(self):
        with open("AGENTS.md", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("1.1. CINCO REGLAS DE ORO OBLIGATORIAS", content)
        self.assertIn("GESTIÓN ESTRATÉGICA DE CRÉDITOS Y FILTRADO RIGUROSO DIARIO", content)
        self.assertIn(WALLET, content)

    def test_wallet_present_in_deploy_script(self):
        with open("tools/deploy_reinforcement_comments.py", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn(WALLET, content)
        self.assertIn("WALLET not in body", content)

    def test_wallet_present_in_recent_deliverables(self):
        deliverables_dir = "outputs/deliverables"
        if os.path.exists(deliverables_dir):
            for fname in os.listdir(deliverables_dir):
                if fname.endswith(".md"):
                    path = os.path.join(deliverables_dir, fname)
                    with open(path, "r", encoding="utf-8") as f:
                        text = f.read()
                    self.assertIn(WALLET, text, f"Missing settlement wallet in {fname}")

if __name__ == "__main__":
    unittest.main()
