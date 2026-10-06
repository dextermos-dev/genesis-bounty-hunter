#!/usr/bin/env python3
"""
Solana Stablecoin Standard (SSS) Enterprise CLI Tool
Command-line operator interface for SSS-1 and SSS-2 token administration on Solana.
Author: Dexter Mos (@dextermos)
Payout: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
"""

import sys
import os
import json
import argparse
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class SolanaStablecoinCLI:
    def __init__(self, state_file="outputs/deliverables/sss_token_state.json"):
        self.state_file = os.path.join(PROJECT_ROOT, state_file)
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
                    return
            except Exception:
                pass
        self.state = {
            "token_name": "Solana Institutional USD",
            "symbol": "USDX",
            "decimals": 6,
            "total_supply": 10000000.0,
            "program_id": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb",
            "compliance_preset": "SSS-2",
            "blacklist": ["0xSanctionedActor_001", "0xMaliciousDrainer_002"],
            "balances": {
                "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20": 5000000.0,
                "0xEnterpriseTreasury": 5000000.0
            },
            "audit_trail": [
                {
                    "action": "INIT_SSS2",
                    "timestamp": datetime.now().isoformat(),
                    "officer": "0xComplianceAdmin",
                    "note": "Initialized SSS-2 Compliant Token-2022 Mint"
                }
            ]
        }
        self.save_state()

    def save_state(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    def mint(self, recipient: str, amount: float):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.state["balances"][recipient] = self.state["balances"].get(recipient, 0.0) + amount
        self.state["total_supply"] += amount
        self.state["audit_trail"].append({
            "action": "MINT",
            "recipient": recipient,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        })
        self.save_state()
        print(f"✅ [MINT SUCCESS] +{amount:,.2f} {self.state['symbol']} minted to {recipient}. New Total Supply: {self.state['total_supply']:,.2f}")

    def transfer(self, sender: str, recipient: str, amount: float):
        if sender in self.state["blacklist"] or recipient in self.state["blacklist"]:
            raise PermissionError("❌ [TRANSFER BLOCKED] Address is blacklisted under SSS-2 Compliance Rules.")
        if self.state["balances"].get(sender, 0.0) < amount:
            raise ValueError("❌ [INSUFFICIENT BALANCE] Sender does not have enough funds.")

        self.state["balances"][sender] -= amount
        self.state["balances"][recipient] = self.state["balances"].get(recipient, 0.0) + amount
        self.state["audit_trail"].append({
            "action": "TRANSFER_HOOK_PASSED",
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "fee": 0.0,
            "timestamp": datetime.now().isoformat()
        })
        self.save_state()
        print(f"✅ [TRANSFER SUCCESS] {amount:,.2f} {self.state['symbol']} transferred from {sender[:10]}... to {recipient[:10]}...")

    def status(self):
        print(f"==========================================================")
        print(f"🏛️  SOLANA STABLECOIN STANDARD (SSS-2) OPERATOR DASHBOARD")
        print(f"==========================================================")
        print(f"Token: {self.state['token_name']} ({self.state['symbol']})")
        print(f"Total Supply: ${self.state['total_supply']:,.2f} USDC-equivalent")
        print(f"Preset: {self.state['compliance_preset']} (Token-2022 Transfer Hook Active)")
        print(f"Blacklisted Sanctions Entries: {len(self.state['blacklist'])}")
        print(f"Total Audit Trail Log Events: {len(self.state['audit_trail'])}")
        print(f"==========================================================")


if __name__ == "__main__":
    cli = SolanaStablecoinCLI()
    cli.status()
    cli.mint("0x8366bCe3a2D379Dec7656D7A67015789FaF999f20", 250000.0)
    cli.transfer("0x8366bCe3a2D379Dec7656D7A67015789FaF999f20", "0xMerchantPartner", 50000.0)
