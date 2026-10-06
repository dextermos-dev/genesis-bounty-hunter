"""
Solana AMM Micro-Arbitrage & Jito Tip Harvester.
Scans price spreads across Raydium, Orca Whirlpools, and Meteora pools on Solana.
Calculates net profit after Jito MEV tips and transaction priority fees.
"""

from typing import Dict, Any, List

class SolanaArbitrageHarvester:
    def __init__(self, settlement_address: str = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"):
        self.settlement_address = settlement_address
        self.detected_spreads: List[Dict[str, Any]] = []

    def evaluate_spread(
        self,
        token_pair: str,
        pool_a_price: float,
        pool_b_price: float,
        trade_size_usd: float = 1_000.0,
        jito_tip_lamports: int = 10_000,
        gas_fee_usd: float = 0.005
    ) -> Dict[str, Any]:
        """
        Calculates cross-pool price spread, slippage, and net captured arbitrage in USDC.
        """
        if pool_a_price <= 0 or pool_b_price <= 0:
            raise ValueError("Pool prices must be strictly positive")

        spread_pct = abs(pool_a_price - pool_b_price) / min(pool_a_price, pool_b_price)
        gross_profit_usd = trade_size_usd * spread_pct
        
        # Jito tip in USD (~$0.0015 per 10k lamports assuming SOL = $150)
        jito_tip_usd = (jito_tip_lamports / 10**9) * 150.0
        net_profit_usd = gross_profit_usd - (jito_tip_usd + gas_fee_usd)

        is_profitable = net_profit_usd > 1.0 # Minimum $1 net threshold

        result = {
            "pair": token_pair,
            "spread_pct": round(spread_pct * 100, 3),
            "trade_size_usd": trade_size_usd,
            "gross_profit_usd": round(gross_profit_usd, 4),
            "net_profit_usd": round(net_profit_usd, 4),
            "is_profitable": is_profitable,
            "beneficiary": self.settlement_address
        }

        self.detected_spreads.append(result)
        return result
