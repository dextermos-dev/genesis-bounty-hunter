"""
Instant Bot Payout Harvester (Algora, Polar.sh, Bountycaster, Opire)
Discovers, filters, and prioritizes GitHub issues with automated smart contract payout bots.
Settlement Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
"""

import json
import time
from typing import Dict, Any, List, Optional


class InstantBotHarvester:
    """
    Scans and filters open source issues where rewards are disbursed instantly
    by automated bots upon PR merge (no waiting for human grant committees).
    """

    OFFICIAL_SETTLEMENT_WALLET = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"
    SUPPORTED_BOTS = ["algora-bot", "bountycaster", "polar-sh", "opire", "frantic-board"]

    def __init__(self):
        self.active_targets: List[Dict[str, Any]] = []

    def evaluate_issue_bot_compatibility(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates whether an issue has an active automated payout bot attached.
        """
        body = issue_data.get("body", "").lower()
        comments = [c.lower() for c in issue_data.get("comments", [])]
        all_text = body + " " + " ".join(comments)

        detected_bot = None
        for bot in self.SUPPORTED_BOTS:
            if bot in all_text or bot.replace("-", "") in all_text:
                detected_bot = bot
                break

        reward = float(issue_data.get("reward_amount", 0))
        is_instant = detected_bot is not None and reward > 0

        result = {
            "issue_url": issue_data.get("url", ""),
            "title": issue_data.get("title", ""),
            "reward_amount": reward,
            "currency": issue_data.get("currency", "USDC"),
            "bot_detected": detected_bot or "NONE",
            "is_instant_payout": is_instant,
            "required_command": f"/claim {self.OFFICIAL_SETTLEMENT_WALLET}" if detected_bot == "algora-bot" else None,
            "settlement_wallet": self.OFFICIAL_SETTLEMENT_WALLET,
            "estimated_payout_latency": "1-15 minutes post-merge" if is_instant else "manual evaluation required"
        }
        return result

    def prepare_instant_claim_comment(self, bot_type: str, pr_url: str) -> str:
        """
        Generates the formal claim message required by the specific bot to release USDC on-chain.
        """
        if bot_type == "algora-bot":
            return f"/claim\n\nSolution delivered in PR: {pr_url}\nSettlement Wallet: {self.OFFICIAL_SETTLEMENT_WALLET}"
        elif bot_type == "bountycaster":
            return f"@bountycaster claim\nDeliverable: {pr_url}\nWallet: {self.OFFICIAL_SETTLEMENT_WALLET}"
        elif bot_type == "polar-sh":
            return f"Resolves issue via {pr_url}. Settlement address: {self.OFFICIAL_SETTLEMENT_WALLET}"
        else:
            return f"Claiming reward for PR {pr_url}. Settlement address: {self.OFFICIAL_SETTLEMENT_WALLET}"


if __name__ == "__main__":
    harvester = InstantBotHarvester()
    sample_issue = {
        "url": "https://github.com/algora-io/bounties/issues/42",
        "title": "Fix memory leak in webhook dispatcher",
        "body": "Reward 150 USDC via algora-bot on merge.",
        "comments": ["algora-bot bounty 150"],
        "reward_amount": 150.0
    }
    evaluated = harvester.evaluate_issue_bot_compatibility(sample_issue)
    print(json.dumps(evaluated, indent=2))

