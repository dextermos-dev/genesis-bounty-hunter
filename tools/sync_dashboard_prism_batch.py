import json
from datetime import datetime, timezone
import requests
from dotenv import dotenv_values

data_path = 'dashboard/data.json'
with open(data_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

existing_ids = [b.get('id') for b in d.get('bounties', [])]

# Add prism-issue-146 if not present
if 'prism-issue-146' not in existing_ids:
    d['bounties'].insert(0, {
        'id': 'prism-issue-146',
        'title': 'feat(devops): add GitHub Actions workflow for security scanning (closes #146)',
        'repository': 'DevNiola/Prism',
        'maintainer': '@DevNiola',
        'platform': 'GitHub / Stellar Wave',
        'bounty_type': 'Security & Compliance',
        'reward': '70 USDC',
        'reward_amount': 70.0,
        'status': 'In Review',
        'pr_url': 'https://github.com/DevNiola/Prism/pull/156',
        'issue_url': 'https://github.com/DevNiola/Prism/issues/146',
        'settlement_wallet': '0x8366bCe3a2D379Dec7656D7A67015789FaF999f20',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'notes': 'PR #156 opened. Automated security scanning with cargo-audit, pnpm audit, CodeQL SAST, and Trivy container/filesystem scanner. Monopolio en Prism.'
    })
    print('Added prism-issue-146 to bounties!')

# Add prism-issue-148 if not present
if 'prism-issue-148' not in existing_ids:
    d['bounties'].insert(0, {
        'id': 'prism-issue-148',
        'title': 'feat(devops): add benchmark workflow for performance regression detection (closes #148)',
        'repository': 'DevNiola/Prism',
        'maintainer': '@DevNiola',
        'platform': 'GitHub / Stellar Wave',
        'bounty_type': 'Performance & Benchmarking',
        'reward': '75 USDC',
        'reward_amount': 75.0,
        'status': 'In Review',
        'pr_url': 'https://github.com/DevNiola/Prism/pull/157',
        'issue_url': 'https://github.com/DevNiola/Prism/issues/148',
        'settlement_wallet': '0x8366bCe3a2D379Dec7656D7A67015789FaF999f20',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'notes': 'PR #157 opened. Criterion benchmark suite for decode pipeline (crates/core/benches/decode_benchmarks.rs) with github-action-benchmark comparison against main and 10% regression failure gate.'
    })
    print('Added prism-issue-148 to bounties!')

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
    'title': 'PR #157 Abierto en DevNiola/Prism (Issue #148 - $75 USDC)',
    'details': 'Workflow de benchmark con Criterion y detección de regresiones de rendimiento implementado (.github/workflows/benchmark.yml, decode_benchmarks.rs). Monopolio total 8/8 PRs en Prism. Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20.',
    'severity': 'success'
})

events.insert(0, {
    'timestamp': datetime.now().strftime('%H:%M:%S'),
    'type': 'GITHUB_PR',
    'title': 'PR #156 Abierto en DevNiola/Prism (Issue #146 - $70 USDC)',
    'details': 'Workflow de seguridad automatizado implementado (.github/workflows/security.yml) con cargo-audit, pnpm audit, CodeQL y Trivy. Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20.',
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
        "🚀 *DOBLETE DE PRs ENTREGADOS — DEVNIOLA/PRISM*\n\n"
        "📦 *PR #156:* Security Scanning (Issue #146 — $70 USDC)\n"
        "📦 *PR #157:* Performance Benchmarks (Issue #148 — $75 USDC)\n"
        "👑 *Dominio en Prism:* 8/8 PRs del repositorio (100% monopolio, $570 USDC)\n\n"
        "📊 *Métricas Actualizadas:*\n"
        "   • Sprint Micro-Bounties: $1,545.00 USDC (20 PRs)\n"
        "     - Ganado Oficial: $685.00 USDC (8 PRs)\n"
        "     - En Revisión: $860.00 USDC (12 PRs)\n"
        "   • Grants & Hackathons: $30,400.00 USDC (19 submissions)\n"
        "   • Gran Total Presentado: $34,945.00 USDC\n"
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
