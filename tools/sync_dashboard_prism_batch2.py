import json
from datetime import datetime, timezone
import requests
from dotenv import dotenv_values

data_path = 'dashboard/data.json'
with open(data_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

existing_ids = [b.get('id') for b in d.get('bounties', [])]

# Add prism-issue-137 if not present
if 'prism-issue-137' not in existing_ids:
    d['bounties'].insert(0, {
        'id': 'prism-issue-137',
        'title': 'feat(devops): add Cargo publish workflow for crates.io (closes #137)',
        'repository': 'DevNiola/Prism',
        'maintainer': '@DevNiola',
        'platform': 'GitHub / Stellar Wave',
        'bounty_type': 'CI/CD & Packaging',
        'reward': '70 USDC',
        'reward_amount': 70.0,
        'status': 'In Review',
        'pr_url': 'https://github.com/DevNiola/Prism/pull/158',
        'issue_url': 'https://github.com/DevNiola/Prism/issues/137',
        'settlement_wallet': '0x8366bCe3a2D379Dec7656D7A67015789FaF999f20',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'notes': 'PR #158 opened. Automated publishing to crates.io for grat-core, grat-wasm, and grat CLI with topological dependency order and crates.io API verification.'
    })
    print('Added prism-issue-137 to bounties!')

# Add prism-issue-138 if not present
if 'prism-issue-138' not in existing_ids:
    d['bounties'].insert(0, {
        'id': 'prism-issue-138',
        'title': 'feat(devops): add npm publish workflow for web app and server (closes #138)',
        'repository': 'DevNiola/Prism',
        'maintainer': '@DevNiola',
        'platform': 'GitHub / Stellar Wave',
        'bounty_type': 'CI/CD & Packaging',
        'reward': '70 USDC',
        'reward_amount': 70.0,
        'status': 'In Review',
        'pr_url': 'https://github.com/DevNiola/Prism/pull/159',
        'issue_url': 'https://github.com/DevNiola/Prism/issues/138',
        'settlement_wallet': '0x8366bCe3a2D379Dec7656D7A67015789FaF999f20',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'notes': 'PR #159 opened. Automated packaging and publication to npm registry for grat-server on release with provenance and NPM_TOKEN.'
    })
    print('Added prism-issue-138 to bounties!')

won_bounties = [b for b in d['bounties'] if b.get('status') in ['MERGED', 'MERGED (Won)']]
in_review_bounties = [b for b in d['bounties'] if b.get('status') == 'In Review']
submitted_bounties = [b for b in d['bounties'] if b.get('status') == 'SUBMITTED']

won_sum = sum(float(b.get('reward_amount', 0)) for b in won_bounties)
in_review_sum = sum(float(b.get('reward_amount', 0)) for b in in_review_bounties)
submitted_sum = sum(float(b.get('reward_amount', 0)) for b in submitted_bounties)

d['earned_onchain_usd'] = won_sum
d['in_review_usd'] = in_review_sum
d['sprint_won_usd'] = won_sum
d['sprint_in_review_usd'] = in_review_sum
d['sprint_total_usd'] = won_sum + in_review_sum
d['sprint_prs_count'] = len(won_bounties) + len(in_review_bounties)
d['submitted_prs_count'] = d['sprint_prs_count']
d['submitted_grants_usd'] = submitted_sum
d['submitted_grants_count'] = len(submitted_bounties)
d['grand_total_pipeline_usd'] = d['sprint_total_usd'] + 3000.0 + submitted_sum
d['total_pipeline_value_usd'] = d['sprint_total_usd']
d['total_bounties_count'] = len(d['bounties'])

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f'Updated data.json: Won=${won_sum}, In Review=${in_review_sum}, Sprint Total=${d["sprint_total_usd"]} ({d["sprint_prs_count"]} PRs), Grand Total=${d["grand_total_pipeline_usd"]}')

# Update live_events.json
events_path = 'dashboard/live_events.json'
with open(events_path, 'r', encoding='utf-8') as f:
    events = json.load(f)

events.insert(0, {
    'timestamp': datetime.now().strftime('%H:%M:%S'),
    'type': 'GITHUB_PR',
    'title': 'PR #159 Abierto en DevNiola/Prism (Issue #138 - $70 USDC)',
    'details': 'Workflow de publicación en NPM automatizado (.github/workflows/publish-npm.yml) para grat-server con provenance. 10/10 PRs en Prism. Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20.',
    'severity': 'success'
})

events.insert(0, {
    'timestamp': datetime.now().strftime('%H:%M:%S'),
    'type': 'GITHUB_PR',
    'title': 'PR #158 Abierto en DevNiola/Prism (Issue #137 - $70 USDC)',
    'details': 'Workflow de publicación en crates.io (.github/workflows/publish-crates.yml) para grat-core, grat-wasm y grat CLI con verificación API. Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20.',
    'severity': 'success'
})

with open(events_path, 'w', encoding='utf-8') as f:
    json.dump(events[:50], f, indent=2, ensure_ascii=False)

print('Updated live_events.json!')

# Telegram alert
config = dotenv_values('.env')
tg_token = config.get('TELEGRAM_BOT_TOKEN')
tg_chat_id = config.get('TELEGRAM_CHAT_ID')
if tg_token and tg_chat_id:
    msg = (
        "👑 *HIT HISTÓRICO: 10/10 PRS EN DEVNIOLA/PRISM*\n\n"
        "📦 *PR #158:* Cargo Crates Publish (Issue #137 — $70 USDC)\n"
        "📦 *PR #159:* NPM Packages Publish (Issue #138 — $70 USDC)\n"
        "🎯 *Dominio Total:* $710.00 USDC bajo control (100% monopolio del repo)\n\n"
        "📊 *Métricas Actualizadas:*\n"
        "   • Sprint Micro-Bounties: $1,695.00 USDC (22 PRs)\n"
        "     - Ganado Oficial: $685.00 USDC (8 PRs)\n"
        "     - En Revisión: $1,010.00 USDC (14 PRs)\n"
        "   • Grants & Hackathons: $30,400.00 USDC (19 submissions)\n"
        "   • Gran Total Presentado: $35,095.00 USDC\n"
        "💳 *Settlement Wallet:* `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`"
    )
    try:
        requests.post(
            f'https://api.telegram.org/bot{tg_token}/sendMessage',
            json={'chat_id': tg_chat_id, 'text': msg, 'parse_mode': 'Markdown'}
        )
        print('Telegram notification sent!')
    except Exception as e:
        print('Telegram error:', e)
