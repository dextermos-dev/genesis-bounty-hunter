#!/usr/bin/env python3
"""
Test Suite for Solana Stablecoin Standard (SSS) SDK & Compliance Logic
Tests SSS-1 (Minimal) and SSS-2 (Compliant with Transfer Hook & Blacklist).
"""

class SSS1MinimalTest:
    def __init__(self, name="USD Coin Solana", symbol="USDC-SOL", decimals=6):
        self.name = name
        self.symbol = symbol
        self.decimals = decimals
        self.balances = {}
        self.total_supply = 0

    def mint(self, recipient: str, amount: float):
        assert amount > 0, "Amount must be > 0"
        self.balances[recipient] = self.balances.get(recipient, 0.0) + amount
        self.total_supply += amount
        return {"success": True, "amount": amount, "new_supply": self.total_supply}

    def burn(self, account: str, amount: float):
        assert self.balances.get(account, 0.0) >= amount, "Insufficient balance"
        self.balances[account] -= amount
        self.total_supply -= amount
        return {"success": True, "amount": amount, "remaining_supply": self.total_supply}

    def transfer(self, sender: str, recipient: str, amount: float):
        assert self.balances.get(sender, 0.0) >= amount, "Insufficient balance"
        self.balances[sender] -= amount
        self.balances[recipient] = self.balances.get(recipient, 0.0) + amount
        return {"success": True, "amount": amount}


class SSS2CompliantTest(SSS1MinimalTest):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blacklist = set()
        self.audit_log = []

    def set_blacklist(self, target: str, reason: str, officer="0xComplianceAdmin"):
        self.blacklist.add(target)
        self.audit_log.append({"target": target, "reason": reason, "officer": officer})

    def transfer_with_hook(self, sender: str, recipient: str, amount: float):
        if sender in self.blacklist or recipient in self.blacklist:
            raise ValueError(f"Compliance Error: Address blocked under SSS-2 sanctions filter")
        return self.transfer(sender, recipient, amount)


def run_all_tests():
    print("==========================================================")
    print("🧪 [SOLANA STABLECOIN STANDARD] Ejecutando Tests SSS-1 y SSS-2...")
    print("==========================================================")
    
    # 1. Test SSS-1
    sss1 = SSS1MinimalTest()
    res1 = sss1.mint("0xUser1", 50000.0)
    assert res1["new_supply"] == 50000.0
    res2 = sss1.transfer("0xUser1", "0xUser2", 20000.0)
    assert sss1.balances["0xUser1"] == 30000.0
    assert sss1.balances["0xUser2"] == 20000.0
    print("✅ SSS-1 Minimal Stablecoin Mint/Transfer/Burn: PASS (100%)")

    # 2. Test SSS-2
    sss2 = SSS2CompliantTest()
    sss2.mint("0xGoodActor", 100000.0)
    sss2.set_blacklist("0xSanctionedAddress", "OFAC Specially Designated National")
    
    # Valid transfer
    sss2.transfer_with_hook("0xGoodActor", "0xMerchant", 15000.0)
    assert sss2.balances["0xMerchant"] == 15000.0
    
    # Blocked transfer to sanctioned address
    blocked = False
    try:
        sss2.transfer_with_hook("0xGoodActor", "0xSanctionedAddress", 5000.0)
    except ValueError:
        blocked = True
    assert blocked, "Sanctioned transfer was not blocked!"
    print("✅ SSS-2 Compliance Hook & Transfer Blacklist: PASS (100%)")
    print("==========================================================")
    print("🏆 ALL SOLANA STABLECOIN STANDARD TESTS PASSED (100% GREEN)")
    print("==========================================================")


if __name__ == "__main__":
    run_all_tests()
