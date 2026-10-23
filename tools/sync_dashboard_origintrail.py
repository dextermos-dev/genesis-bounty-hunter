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

# Check if already present
bounties = data.get("bounties", [])
exists = any(b.get("id") == "origintrail-dkgv10-audit-ledger" or b.get("pr_number") == 37 for b in bounties)

new_entry = {
    "id": "origintrail-dkgv10-audit-ledger",
    "title": "DKG Audit Ledger — Autonomous Code Audit & Security Verification Memory [cfi-dkgv10-r1]",
    "repository": "OriginTrail/dkg-integrations",
    "pr_url": "https://github.com/OriginTrail/dkg-integrations/pull/37",
    "pr_number": 37,
    "integration_repo": "https://github.com/dextermos-dev/dkg-audit-ledger",
    "commit_sha": "751d33597b12e1265e907c48d945507e989ac185",
    "platform": "OriginTrail DKG",
    "category": "SDK / Tooling / MCP",
    "memory_layers": ["WM", "SWM"],
    "reward_amount": 7000.0,
    "reward_asset": "TRAC / USDC",
    "reward_usd": 7000.0,
    "status": "IN_REVIEW",
    "settlement_wallet": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
    "submitted_at": now_iso,
    "updated_at": now_iso,
    "description": "Autonomous code audit and security verification memory for AI agents in OriginTrail DKG V10. Tested with 5/5 passing unit tests, zero external egress, zero-dependency Node.js standard libraries, and stdio MCP server for Cursor and Claude Code."
}

if not exists:
    bounties.insert(0, new_entry)
    data["bounties"] = bounties
    data["in_review_usd"] = round(data.get("in_review_usd", 0) + 7000.0, 2)
    data["grand_total_pipeline_usd"] = round(data.get("grand_total_pipeline_usd", 0) + 7000.0, 2)
    data["total_pipeline_value_usd"] = round(data.get("total_pipeline_value_usd", 0) + 7000.0, 2)
    data["submitted_prs_count"] = data.get("submitted_prs_count", 0) + 1
    data["total_bounties_count"] = len(bounties)

with open(DATA_FILE, "w") as f:
    json.dump(data, f, indent=2)

print(f"[+] Updated {DATA_FILE}")
print(f"    In Review USD: ${data['in_review_usd']:,.2f}")
print(f"    Grand Total Pipeline USD: ${data['grand_total_pipeline_usd']:,.2f}")
print(f"    Submitted PRs Count: {data['submitted_prs_count']}")

# Update live_events.json
if os.path.exists(EVENTS_FILE):
    with open(EVENTS_FILE, "r") as f:
        events_data = json.load(f)
else:
    events_data = []

event = {
    "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    "type": "NEW_SUBMISSION",
    "title": "OriginTrail DKG V10: PR #37 Enviada",
    "details": "Integration dkg-audit-ledger submitted to OriginTrail/dkg-integrations (PR #37). 5/5 tests passing, zero-dependency Node.js, Apache-2.0. Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
    "severity": "success"
}

if isinstance(events_data, list):
    events_data.insert(0, event)
    events_data = events_data[:100]
elif isinstance(events_data, dict):
    events = events_data.get("events", [])
    events.insert(0, event)
    events_data["events"] = events[:100]

with open(EVENTS_FILE, "w") as f:
    json.dump(events_data, f, indent=2)

print(f"[+] Added live event to {EVENTS_FILE}")
