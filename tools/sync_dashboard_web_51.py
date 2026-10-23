#!/usr/bin/env python3
import json

with open("dashboard/data.json", "r") as f:
    data = json.load(f)

data["bounties"] = [b for b in data.get("bounties", []) if b.get("bounty_id") != "susu-web-51"]

new_item = {
    "bounty_id": "susu-web-51",
    "title": "SUSU-LABS/susu-web #51: [Bounty: $50] Validate the extra body fields returned by apiRequestPageBody",
    "url": "https://github.com/SUSU-LABS/susu-web/issues/51",
    "platform": "GitHub / Direct PR",
    "reward_amount": 50.0,
    "reward_currency": "USDC",
    "payment_network": "Base L2 / EVM",
    "final_score": 9.9,
    "expected_value": 50.0,
    "status": "IN_REVIEW",
    "payout_status": "EN_REVISION",
    "payout_text": "🟡 EN REVISIÓN EN GITHUB (PR #165)",
    "pull_request_url": "https://github.com/SUSU-LABS/susu-web/pull/165",
    "pr_url": "https://github.com/SUSU-LABS/susu-web/pull/165",
    "pr_number": 165,
    "web3_wallet_address": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
    "settlement_wallet": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
    "red_team_score": 9.9,
    "sandbox_status": "SUCCESS",
    "is_complete": True,
    "sprint": True,
    "in_review": True,
    "repo": "SUSU-LABS/susu-web",
    "is_new": True
}
data["bounties"].insert(0, new_item)

# Recompute metrics
data["total_bounties_count"] = len(data["bounties"])
sprint_in_review = sum(b.get("reward_amount", 0) for b in data["bounties"] if b.get("sprint") and b.get("in_review"))
data["sprint_in_review_usd"] = round(sprint_in_review, 2)
data["in_review_usd"] = round(sprint_in_review, 2)
data["sprint_total_usd"] = round(sprint_in_review + data.get("earned_onchain_usd", 1485.0), 2)
data["total_pipeline_value_usd"] = round(sum(b.get("reward_amount", 0) for b in data["bounties"]), 2)
data["submitted_prs_count"] = sum(1 for b in data["bounties"] if b.get("pull_request_url"))

with open("dashboard/data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated dashboard/data.json successfully!")
print(f"Total bounties: {data['total_bounties_count']}")
print(f"Sprint In Review: ${data['sprint_in_review_usd']} USDC")
print(f"Submitted PRs count: {data['submitted_prs_count']}")
