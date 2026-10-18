#!/usr/bin/env python3
"""
Update dashboard/data.json to mark Parabola PRs #99, #100, #101 as MERGED / GANADO!
"""

import json

with open("dashboard/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for b in data["bounties"]:
    if b["bounty_id"] in ["parabola_issue_1", "parabola_issue_19", "parabola_issue_20"]:
        b["status"] = "MERGED"
        b["payout_status"] = "MERGED_CONFIRMADO_EN_DISPERSION"
        b["in_review"] = False
        if b["bounty_id"] == "parabola_issue_1":
            b["payout_text"] = "🎉 PR #101 MERGED POR MAINTAINER @Abdul-dev-creator ($105 USDC)"
        elif b["bounty_id"] == "parabola_issue_19":
            b["payout_text"] = "🎉 PR #99 MERGED POR MAINTAINER @Abdul-dev-creator ($45 USDC)"
        elif b["bounty_id"] == "parabola_issue_20":
            b["payout_text"] = "🎉 PR #100 MERGED POR MAINTAINER @Abdul-dev-creator ($45 USDC)"

# Calculate amounts
merged_parabola = 105.0 + 45.0 + 45.0
data["in_review_usd"] -= merged_parabola
data["earned_onchain_usd"] += merged_parabola

with open("dashboard/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated dashboard data.json:")
print(f"Earned / Merged USD: ${data['earned_onchain_usd']:.2f}")
print(f"In review USD: ${data['in_review_usd']:.2f}")
