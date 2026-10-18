import json
from datetime import datetime, timezone

# 1. Update data.json
data_path = 'dashboard/data.json'
with open(data_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

existing_ids = [b.get('id') for b in d.get('bounties', [])]
if 'prism-issue-135' not in existing_ids:
    new_bounty = {
        'id': 'prism-issue-135',
        'title': 'feat(devops): add docker-compose and Makefile for local development (closes #135)',
        'repository': 'DevNiola/Prism',
        'maintainer': '@DevNiola',
        'platform': 'GitHub / Stellar Wave',
        'bounty_type': 'DevOps & Containerization',
        'reward': '75 USDC',
        'reward_amount': 75.0,
        'status': 'In Review',
        'pr_url': 'https://github.com/DevNiola/Prism/pull/153',
        'issue_url': 'https://github.com/DevNiola/Prism/issues/135',
        'settlement_wallet': '0x8366bCe3a2D379Dec7656D7A67015789FaF999f20',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'notes': 'PR #153 opened. Monopolio absoluto en DevNiola/Prism (4/4 PRs del repo). docker-compose.yml orquestando web, server y redis con healthchecks, red dedicada, volumen persistente, Makefile con make up y Dockerfiles multi-stage de producción.'
    }
    d['bounties'].insert(0, new_bounty)
    print('Added prism-issue-135 to bounties list!')

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
    'title': 'PR #153 Abierto en DevNiola/Prism (Issue #135)',
    'details': 'Entorno local con docker-compose.yml y Makefile (make up) para web (3000), server (3001) y redis (6379) con healthchecks y volumen persistente. 4/4 PRs monopólicas. Settlement Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20.',
    'severity': 'success'
}

events.insert(0, new_event)
with open(events_path, 'w', encoding='utf-8') as f:
    json.dump(events[:50], f, indent=2, ensure_ascii=False)

print('Updated live_events.json with PR #153 event!')
