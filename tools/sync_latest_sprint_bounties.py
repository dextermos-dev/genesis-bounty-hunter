#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_ROOT, "dashboard", "data.json")
EVENTS_FILE = os.path.join(PROJECT_ROOT, "dashboard", "live_events.json")

now_iso = datetime.now(timezone.utc).isoformat()

with open(DATA_FILE, "r") as f:
    data = json.load(f)

bounties = data.get("bounties", [])

new_items = [
    {
        "id": "slippay-issue-512",
        "title": "fix(billing): validate billing window parameters before database execution (closes #512)",
        "repository": "slippay-labs/slippay",
        "pr_url": "https://github.com/slippay-labs/slippay/pull/661",
        "pr_number": 661,
        "issue_url": "https://github.com/slippay-labs/slippay/issues/512",
        "platform": "SlipPay Labs",
        "category": "Backend / API / TypeScript",
        "reward_amount": 150.0,
        "reward_asset": "USDC",
        "reward_usd": 150.0,
        "status": "IN_REVIEW",
        "payout_status": "EN_EVALUACION_ACTIVA",
        "settlement_wallet": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
        "submitted_at": now_iso,
        "updated_at": now_iso,
        "description": "Introduced validateBillingWindow before DB execution: enforces date syntax, prevents reversed windows, restricts span to 366 days max, and verified with 10 passing unit tests."
    },
    {
        "id": "paraloom-wallet-issue-89",
        "title": "fix(wallet): RPC resilience, stale swap polling filter, event bounds, and v0 LUT recovery (closes #89)",
        "repository": "paraloom-labs/paraloom-wallet",
        "pr_url": "https://github.com/paraloom-labs/paraloom-wallet/pull/103",
        "pr_number": 103,
        "issue_url": "https://github.com/paraloom-labs/paraloom-wallet/issues/89",
        "platform": "Paraloom Labs",
        "category": "Web3 Wallet / TypeScript",
        "reward_amount": 150.0,
        "reward_asset": "USDC",
        "reward_usd": 150.0,
        "status": "IN_REVIEW",
        "payout_status": "EN_EVALUACION_ACTIVA",
        "settlement_wallet": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
        "submitted_at": now_iso,
        "updated_at": now_iso,
        "description": "Hardened private swap flow against transient RPC drops, isolated stale swap resolutions with startedAt filtering, added bounds checks to fetchV3Leaves, and fixed v0 LUT note recovery."
    },
    {
        "id": "paraloom-core-issue-1160",
        "title": "fix(privacy): verify commitment openings, enforce strict proof wire framing, and coordinator failover resilience (closes #1160)",
        "repository": "paraloom-labs/paraloom-core",
        "pr_url": "https://github.com/paraloom-labs/paraloom-core/pull/1167",
        "pr_number": 1167,
        "issue_url": "https://github.com/paraloom-labs/paraloom-core/issues/1160",
        "platform": "Paraloom Labs",
        "category": "Smart Contracts / Rust / ZK",
        "reward_amount": 150.0,
        "reward_asset": "USDC",
        "reward_usd": 150.0,
        "status": "IN_REVIEW",
        "payout_status": "EN_EVALUACION_ACTIVA",
        "settlement_wallet": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
        "submitted_at": now_iso,
        "updated_at": now_iso,
        "description": "Unified commitment schemes, enforced zero-trailing bytes in proof deserialization, fixed big-endian field encoding, added non-zero nullifier validation, and unstranded coordinator failover tasks."
    },
    {
        "id": "chain-love-dbip-4724",
        "title": "feat(schema): add possessionProofMechanisms storage category & validation (DBIP-4724)",
        "repository": "Chain-Love/chain-love",
        "pr_url": "https://github.com/Chain-Love/chain-love/pull/4735",
        "pr_number": 4735,
        "issue_url": "https://github.com/Chain-Love/chain-love/issues/4724",
        "platform": "Chain-Love DBIP",
        "category": "Schema / Open Source",
        "reward_amount": 20.0,
        "reward_asset": "USDC",
        "reward_usd": 20.0,
        "status": "IN_REVIEW",
        "payout_status": "EN_EVALUACION_ACTIVA",
        "settlement_wallet": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
        "submitted_at": now_iso,
        "updated_at": now_iso,
        "description": "Added possessionProofMechanisms (PDP, PoRep, PoSt) column definitions, JSON schema definitions, CSV validation, and test suite with 7 passing tests."
    }
]

added_usd = 0.0
added_prs = 0

for item in new_items:
    if not any(b.get("id") == item["id"] or (item.get("pr_number") and b.get("pr_number") == item["pr_number"] and b.get("repository") == item["repository"]) for b in bounties):
        bounties.insert(0, item)
        added_usd += item["reward_usd"]
        added_prs += 1
        print(f"[+] Added {item['id']} ({item['pr_url']}) - ${item['reward_usd']}")

if added_prs > 0:
    data["bounties"] = bounties
    data["in_review_usd"] = round(data.get("in_review_usd", 0) + added_usd, 2)
    data["sprint_in_review_usd"] = round(data.get("sprint_in_review_usd", 0) + added_usd, 2)
    data["sprint_total_usd"] = round(data.get("sprint_total_usd", 0) + added_usd, 2)
    data["grand_total_pipeline_usd"] = round(data.get("grand_total_pipeline_usd", 0) + added_usd, 2)
    data["total_pipeline_value_usd"] = round(data.get("total_pipeline_value_usd", 0) + added_usd, 2)
    data["submitted_prs_count"] = data.get("submitted_prs_count", 0) + added_prs
    data["total_bounties_count"] = len(bounties)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n[OK] Dashboard data updated successfully!")
    print(f"     New PRs added: {added_prs}")
    print(f"     Added Value: ${added_usd:,.2f} USDC")
    print(f"     In Review Total: ${data['in_review_usd']:,.2f} USDC")
    print(f"     Grand Total Pipeline: ${data['grand_total_pipeline_usd']:,.2f} USDC")
else:
    print("[i] All items already present in data.json.")

# Update live_events.json
if os.path.exists(EVENTS_FILE):
    try:
        with open(EVENTS_FILE, "r") as f:
            events_data = json.load(f)
        events_list = events_data if isinstance(events_data, list) else events_data.get("events", [])
        time_str = datetime.now(timezone.utc).strftime("%H:%M:%S")
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        for item in new_items:
            events_list.insert(0, {
                "timestamp": time_str,
                "date": date_str,
                "type": "PR_SUBMITTED",
                "title": f"PR #{item['pr_number']} enviado a {item['repository']}",
                "details": f"{item['title']} - Recompensa esperada: ${item['reward_usd']} USDC",
                "severity": "success"
            })
        events_data = events_list[:100]
        with open(EVENTS_FILE, "w") as f:
            json.dump(events_data, f, indent=2)
        print("[OK] live_events.json updated.")
    except Exception as e:
        print("[!] Error updating live_events.json:", e)
