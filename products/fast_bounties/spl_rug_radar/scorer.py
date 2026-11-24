"""
Real-Time Solana SPL Mint Anomaly & Rug-Pull Radar Scorer (<=8KB)
Autonomous heuristic scoring engine for new SPL tokens & DEX pools.
Evaluates early-momentum vs rug-pull risk within 15 blocks of launch.

Invariants Scored:
1. Mint & Freeze Authority state (unrevoked = severe penalty).
2. Top-10 Holder Concentration (Gini coefficient calculation).
3. LP Token Lock & Burn Verification (Raydium / Orca / Meteora pools).
4. Slot-Bundler Jito Detection (atomic multi-buy in same block/slot).
"""

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class TokenLaunchEvent:
    mint: str
    mint_authority: str | None
    freeze_authority: str | None
    total_supply: int
    top_10_balances: List[int]
    lp_mint: str
    lp_burned_percent: float # 0.0 to 100.0
    lp_locked_until: int # unix timestamp
    block_slot: int
    first_15_txs_slots: List[int]


class SPLRugRadarScorer:
    def __init__(self, current_timestamp: int = 1795553700):
        self.now = current_timestamp

    def calculate_gini(self, balances: List[int]) -> float:
        if not balances or len(balances) <= 1:
            return 1.0
        sorted_b = sorted(balances)
        n = len(sorted_b)
        total = sum(sorted_b)
        if total == 0:
            return 1.0
        # Gini = (2 * sum(i * y_i) - (n + 1) * sum(y_i)) / (n * sum(y_i))
        weighted_sum = sum((i + 1) * val for i, val in enumerate(sorted_b))
        return (2 * weighted_sum - (n + 1) * total) / (n * total)

    def score(self, event: TokenLaunchEvent) -> Dict[str, Any]:
        """
        Returns a calibrated score in [0.0, 1.0] where:
        1.0 = Guaranteed Rug-Pull / Malicious
        0.0 = Safe / Legitimate Early Momentum
        """
        penalties = 0.0
        details = {}

        # 1. Authority Risk (Weight: 0.35)
        # Having unrevoked freeze authority allows freezing user balances instantly.
        auth_penalty = 0.0
        if event.freeze_authority is not None:
            auth_penalty += 0.25
            details["freeze_authority_active"] = True
        else:
            details["freeze_authority_active"] = False

        if event.mint_authority is not None:
            auth_penalty += 0.10
            details["mint_authority_active"] = True
        else:
            details["mint_authority_active"] = False
        penalties += auth_penalty

        # 2. Top-10 Concentration / Gini Risk (Weight: 0.25)
        gini = self.calculate_gini(event.top_10_balances)
        details["gini_coefficient"] = round(gini, 4)
        top10_share = sum(event.top_10_balances) / max(event.total_supply, 1)
        details["top10_supply_share"] = round(top10_share, 4)

        if top10_share > 0.60 or gini > 0.80:
            penalties += 0.25
        elif top10_share > 0.40 or gini > 0.65:
            penalties += 0.15
        elif top10_share > 0.25:
            penalties += 0.05

        # 3. Liquidity Pool Lock / Burn Verification (Weight: 0.25)
        lp_penalty = 0.0
        if event.lp_burned_percent >= 99.0:
            details["lp_burned"] = True
            details["lp_locked"] = True
        elif event.lp_locked_until > self.now + (30 * 86400): # locked >= 30 days
            details["lp_burned"] = False
            details["lp_locked"] = True
        elif event.lp_locked_until > self.now:
            details["lp_burned"] = False
            details["lp_locked"] = True
            lp_penalty += 0.10
        else:
            details["lp_burned"] = False
            details["lp_locked"] = False
            lp_penalty += 0.25
        penalties += lp_penalty

        # 4. Slot-Bundler / Jito Sniper Detection (Weight: 0.15)
        # If > 5 of first 15 txs happened in the exact launch slot, it indicates automated sniper bundling.
        slot_counts: Dict[int, int] = {}
        for s in event.first_15_txs_slots:
            slot_counts[s] = slot_counts.get(s, 0) + 1

        bundled_snipes = slot_counts.get(event.block_slot, 0)
        details["bundled_initial_txs"] = bundled_snipes
        if bundled_snipes >= 6:
            penalties += 0.15
            details["bundler_detected"] = True
        elif bundled_snipes >= 3:
            penalties += 0.08
            details["bundler_detected"] = False
        else:
            details["bundler_detected"] = False

        final_risk = min(1.0, max(0.0, penalties))
        verdict = "HIGH_RISK_RUG" if final_risk >= 0.70 else "SUSPICIOUS" if final_risk >= 0.40 else "SAFE_MOMENTUM"

        return {
            "mint": event.mint,
            "rug_probability": round(final_risk, 4),
            "momentum_score": round(1.0 - final_risk, 4),
            "verdict": verdict,
            "details": details
        }


# Self-test benchmark
if __name__ == "__main__":
    scorer = SPLRugRadarScorer()
    
    # Test A: Classic HoneyPot/Rug-pull (Active freeze, 0% burned LP, bundled snipe)
    bad_token = TokenLaunchEvent(
        mint="BadMint1111111111111111111111111111111111111",
        mint_authority="Dev1111111111111111111111111111111111111111",
        freeze_authority="Dev1111111111111111111111111111111111111111",
        total_supply=1_000_000_000,
        top_10_balances=[500_000_000, 200_000_000, 100_000_000, 50_000_000],
        lp_mint="LPMint1111111111111111111111111111111111111",
        lp_burned_percent=0.0,
        lp_locked_until=0,
        block_slot=300000000,
        first_15_txs_slots=[300000000]*8 + [300000001]*7
    )
    res_a = scorer.score(bad_token)
    print("Test A (Bad Token):", res_a)
    assert res_a["rug_probability"] >= 0.85, "Should flag bad token as severe rug"

    # Test B: Fair Launch (Revoked authorities, 100% burned LP, distributed holders)
    good_token = TokenLaunchEvent(
        mint="GoodMint111111111111111111111111111111111111",
        mint_authority=None,
        freeze_authority=None,
        total_supply=1_000_000_000,
        top_10_balances=[20_000_000, 18_000_000, 15_000_000, 12_000_000, 10_000_000],
        lp_mint="LPMint2222222222222222222222222222222222222",
        lp_burned_percent=100.0,
        lp_locked_until=0,
        block_slot=300000000,
        first_15_txs_slots=list(range(300000000, 300000015))
    )
    res_b = scorer.score(good_token)
    print("Test B (Good Token):", res_b)
    assert res_b["rug_probability"] <= 0.15, "Should flag good token as safe"
    print("All radar benchmarks PASSED successfully!")
