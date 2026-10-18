import json
import os
import requests
from datetime import datetime, timezone
from dotenv import dotenv_values

# 1. Update data.json
data_path = 'dashboard/data.json'
with open(data_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

existing_ids = [b.get('id') for b in d.get('bounties', [])]
if 'prism-issue-136' not in existing_ids:
    new_bounty = {
        'id': 'prism-issue-136',
        'title': 'feat(devops): add automated release workflow with semantic versioning (closes #136)',
        'repository': 'DevNiola/Prism',
        'maintainer': '@DevNiola',
        'platform': 'GitHub / Stellar Wave',
        'bounty_type': 'DevOps & Automation',
        'reward': '70 USDC',
        'reward_amount': 70.0,
        'status': 'In Review',
        'pr_url': 'https://github.com/DevNiola/Prism/pull/155',
        'issue_url': 'https://github.com/DevNiola/Prism/issues/136',
        'settlement_wallet': '0x8366bCe3a2D379Dec7656D7A67015789FaF999f20',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'notes': 'PR #155 opened. Monopolio absoluto en DevNiola/Prism (6/6 PRs del repo). Semantic versioning con conventional commits, changelog generation (.releaserc.json), vX.Y.Z tags y automated GitHub Actions release workflow (.github/workflows/release.yml).'
    }
    d['bounties'].insert(0, new_bounty)
    print('Added prism-issue-136 to bounties list!')

won_bounties = [b for b in d['bounties'] if b.get('status') in ['MERGED', 'MERGED (Won)']]
in_review_bounties = [b for b in d['bounties'] if b.get('status') == 'In Review']

won_sum = sum(float(b.get('reward_amount', 0)) for b in won_bounties)
in_review_sum = sum(float(b.get('reward_amount', 0)) for b in in_review_bounties)

d['earned_onchain_usd'] = won_sum
d['in_review_usd'] = in_review_sum
d['total_pipeline_value_usd'] = won_sum + in_review_sum
d['submitted_prs_count'] = len(won_bounties) + len(in_review_bounties)
d['total_bounties_count'] = len(d['bounties'])

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f'Updated data.json: Won=${won_sum} ({len(won_bounties)} PRs), In Review=${in_review_sum} ({len(in_review_bounties)} PRs), Total=${won_sum + in_review_sum} ({d["submitted_prs_count"]} PRs)')

# 2. Update live_events.json
events_path = 'dashboard/live_events.json'
with open(events_path, 'r', encoding='utf-8') as f:
    events = json.load(f)

new_event = {
    'timestamp': datetime.now().strftime('%H:%M:%S'),
    'type': 'GITHUB_PR',
    'title': 'PR #155 Abierto en DevNiola/Prism (Issue #136)',
    'details': 'Workflow de releases automatizadas y versionado semántico implementado (.github/workflows/release.yml, .releaserc.json, CHANGELOG.md). Monopolio total 6/6 PRs en Prism. Settlement Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20.',
    'severity': 'success'
}

events.insert(0, new_event)
with open(events_path, 'w', encoding='utf-8') as f:
    json.dump(events[:50], f, indent=2, ensure_ascii=False)

print('Updated live_events.json with PR #155 event!')

# 3. Telegram notification
config = dotenv_values('.env')
tg_token = config.get('TELEGRAM_BOT_TOKEN')
tg_chat_id = config.get('TELEGRAM_CHAT_ID')
if tg_token and tg_chat_id:
    msg = (
        "🚀 *NUEVO PR ENTREGADO — DEVNIOLA/PRISM #136*\n\n"
        "🎯 *Issue:* #136 (Automated release workflow & semantic versioning)\n"
        "📦 *PR:* #155 (https://github.com/DevNiola/Prism/pull/155)\n"
        "💰 *Recompensa:* $70.00 USDC\n"
        "👑 *Dominio:* 6/6 PRs en DevNiola/Prism (100% monopolio)\n"
        "📊 *Cartera Total:* $1,400.00 USDC (18 Soluciones)\n"
        "   • Ganado On-Chain: $685.00 USDC (8 PRs)\n"
        "   • En Revisión: $715.00 USDC (10 PRs)\n"
        "💳 *Wallet:* `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`"
    )
    try:
        res = requests.post(
            f'https://api.telegram.org/bot{tg_token}/sendMessage',
            json={'chat_id': tg_chat_id, 'text': msg, 'parse_mode': 'Markdown'}
        )
        print('Telegram notification status:', res.status_code)
    except Exception as e:
        print('Telegram error:', e)
