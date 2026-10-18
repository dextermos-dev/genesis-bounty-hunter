#!/usr/bin/env python3
import json

with open("dashboard/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

new_entries = [
    {
        "bounty_id": "parabola_issue_1",
        "title": "[Parabola $105 USDC] Preserve burnTxHash when Stellar confirmation polling hits transient RPC errors",
        "url": "https://github.com/Parabola-org/parabola/issues/1",
        "platform": "GitHub Micro-Bounties (Circle CCTP Arc<->Stellar)",
        "reward_amount": 105.0,
        "reward_currency": "USDC",
        "payment_network": "Base L2 / EVM",
        "final_score": 9.9,
        "expected_value": 105.0,
        "status": "SUBMITTED",
        "payout_status": "EN_EVALUACION_ACTIVA",
        "payout_text": "⚡ PR #101 SUBMITTED - RETRY TOLERANCE & HASH PRESERVATION (ONLY OPEN PR)",
        "pull_request_url": "https://github.com/Parabola-org/parabola/pull/101",
        "pr_number": 101,
        "web3_wallet_address": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
        "red_team_score": 9.9,
        "sandbox_status": "SUCCESS",
        "is_complete": True,
        "is_new": True,
        "cycle": "OCTUBRE_2026_ACTIVO",
        "in_review": True
    },
    {
        "bounty_id": "parabola_issue_19",
        "title": "[Parabola $45 USDC] Validate input to bytes32ToStellarAddress",
        "url": "https://github.com/Parabola-org/parabola/issues/19",
        "platform": "GitHub Micro-Bounties (Circle CCTP Arc<->Stellar)",
        "reward_amount": 45.0,
        "reward_currency": "USDC",
        "payment_network": "Base L2 / EVM",
        "final_score": 9.8,
        "expected_value": 45.0,
        "status": "SUBMITTED",
        "payout_status": "EN_EVALUACION_ACTIVA",
        "payout_text": "⚡ PR #99 SUBMITTED - STRICT 32-BYTE VALIDATION & 100% UNIT TESTS",
        "pull_request_url": "https://github.com/Parabola-org/parabola/pull/99",
        "pr_number": 99,
        "web3_wallet_address": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
        "red_team_score": 9.8,
        "sandbox_status": "SUCCESS",
        "is_complete": True,
        "is_new": True,
        "cycle": "OCTUBRE_2026_ACTIVO",
        "in_review": True
    },
    {
        "bounty_id": "parabola_issue_20",
        "title": "[Parabola $45 USDC] Export convertPrecision and add 6<->7 decimal round-trip tests",
        "url": "https://github.com/Parabola-org/parabola/issues/20",
        "platform": "GitHub Micro-Bounties (Circle CCTP Arc<->Stellar)",
        "reward_amount": 45.0,
        "reward_currency": "USDC",
        "payment_network": "Base L2 / EVM",
        "final_score": 9.8,
        "expected_value": 45.0,
        "status": "SUBMITTED",
        "payout_status": "EN_EVALUACION_ACTIVA",
        "payout_text": "⚡ PR #100 SUBMITTED - RE-EXPORT & COMPREHENSIVE ROUND-TRIP TESTS",
        "pull_request_url": "https://github.com/Parabola-org/parabola/pull/100",
        "pr_number": 100,
        "web3_wallet_address": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
        "red_team_score": 9.8,
        "sandbox_status": "SUCCESS",
        "is_complete": True,
        "is_new": True,
        "cycle": "OCTUBRE_2026_ACTIVO",
        "in_review": True
    }
]

existing_ids = {b["bounty_id"] for b in data["bounties"]}
filtered_new = [e for e in new_entries if e["bounty_id"] not in existing_ids]

data["bounties"] = filtered_new + data["bounties"]
data["total_bounties_count"] = len(data["bounties"])
data["in_review_usd"] += sum(e["reward_amount"] for e in filtered_new)
data["total_pipeline_value_usd"] += sum(e["reward_amount"] for e in filtered_new)
data["total_claimed_usd"] += sum(e["reward_amount"] for e in filtered_new)
data["submitted_prs_count"] += len(filtered_new)

with open("dashboard/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Dashboard updated successfully.")
print(f"In review USD: ${data['in_review_usd']:.2f}")
print(f"Total pipeline USD: ${data['total_pipeline_value_usd']:.2f}")
print(f"Total submitted PRs: {data['submitted_prs_count']}")
