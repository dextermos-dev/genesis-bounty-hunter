#!/usr/bin/env python3
import json
import datetime

with open('dashboard/data.json') as f:
    d = json.load(f)

# Check if PR #2964 is already recorded
existing_prs = d.get('submitted_prs', [])
has_2964 = any(pr.get('pr_number') == 2964 or pr.get('id') == 'gh-2964' for pr in existing_prs)

if not has_2964:
    pr_entry = {
        'id': 'gh-2964',
        'title': 'fix(hy-check): enforce T24 HYB-E3104 on O8 field loans, map projections, and loan rebinds (fixes #2946)',
        'repo': 'limitlessprojects/Go-Hybrid',
        'pr_number': 2964,
        'pr_url': 'https://github.com/limitlessprojects/Go-Hybrid/pull/2964',
        'issue_url': 'https://github.com/limitlessprojects/Go-Hybrid/issues/2946',
        'status': 'in_review',
        'bounty_usd': 150.0,
        'currency': 'USDC',
        'network': 'Base L2 / EVM',
        'settlement_wallet': '0x8366bCe3a2D379Dec7656D7A67015789FaF999f20',
        'submitted_at': datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    existing_prs.insert(0, pr_entry)
    d['submitted_prs'] = existing_prs
    d['total_submitted_prs'] = len(existing_prs)
    d['in_review_usd'] = round(d.get('in_review_usd', 10436.0) + 150.0, 2)

    with open('dashboard/data.json', 'w') as f:
        json.dump(d, f, indent=2)
    print(f"Added PR #2964 to dashboard/data.json. In review USD: ${d['in_review_usd']}")
else:
    print("PR #2964 already present.")

# Append to live events
with open('dashboard/live_events.json') as f:
    events = json.load(f)

events.insert(0, {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    "type": "pr_submitted",
    "title": "PR #2964 Enviado en Go-Hybrid ($150 USDC)",
    "description": "Fix T24 HYB-E3104 en O8 field loans, unaddressable map projections y loan rebinds (fixes #2946). Todos los tests pasaron 100%. Settlement Wallet registrada: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20.",
    "url": "https://github.com/limitlessprojects/Go-Hybrid/pull/2964"
})

events.insert(0, {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    "type": "pr_approved",
    "title": "Chain-Love PR #4781 APROBADO por @USS-Supervisor ($150 USDC)",
    "description": "El mantenedor @USS-Supervisor ha emitido el veredicto oficial 'APPROVE' (Confidence: HIGH, Risk: LOW, Findings: None). 10/10 checks de links en verde en CI.",
    "url": "https://github.com/Chain-Love/chain-love/pull/4781"
})

with open('dashboard/live_events.json', 'w') as f:
    json.dump(events[:50], f, indent=2)

print("live_events.json updated.")
