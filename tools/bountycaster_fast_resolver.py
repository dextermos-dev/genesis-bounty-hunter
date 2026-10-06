"""
Bountycaster & Farcaster Base L2 P2P Micro-Bounty Resolver.
Monitors Farcaster @bountybot tasks, matches requirements against our open-source codebase,
and prepares instant automated submission casts with verified Base settlement address.
"""

import json
from typing import Dict, Any, List

class BountycasterFastResolver:
    def __init__(self, settlement_wallet: str = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"):
        self.settlement_wallet = settlement_wallet
        self.active_submissions: List[Dict[str, Any]] = []

    def format_submission_cast(
        self,
        bounty_id: str,
        poster_username: str,
        reward_amount_usd: float,
        solution_repo_url: str,
        summary_text: str
    ) -> Dict[str, Any]:
        """
        Builds a compliant Farcaster cast payload tagging the poster and providing proof of work.
        """
        cast_text = (
            f"@{poster_username} Solution ready for bounty #{bounty_id} (${reward_amount_usd} USDC)!\n\n"
            f"⚡ {summary_text}\n"
            f"📦 Code: {solution_repo_url}\n\n"
            f"Settlement (Base L2): {self.settlement_wallet}"
        )

        payload = {
            "bounty_id": bounty_id,
            "target_poster": poster_username,
            "reward_amount_usd": reward_amount_usd,
            "cast_text": cast_text,
            "char_count": len(cast_text),
            "is_valid_length": len(cast_text) <= 320, # Farcaster limit is 320 chars
            "settlement_wallet": self.settlement_wallet
        }

        self.active_submissions.append(payload)
        return payload

    def get_submissions(self) -> List[Dict[str, Any]]:
        return self.active_submissions
