import json
from datetime import datetime, timezone

# 1. Update data.json
data_path = 'dashboard/data.json'
with open(data_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

existing_ids = [b.get('id') for b in d.get('bounties', [])]
if 'prism-issue-141' not in existing_ids:
    new_bounty = {
        'id': 'prism-issue-141',
        'title': 'chore(devops): add pre-commit hooks for code formatting and linting (closes #141)',
        'repository': 'DevNiola/Prism',
        'maintainer': '@DevNiola',
        'platform': 'GitHub / Stellar Wave',
        'bounty_type': 'DevOps & Code Quality',
        'reward': '70 USDC',
        'reward_amount': 70.0,
        'status': 'In Review',
        'pr_url': 'https://github.com/DevNiola/Prism/pull/154',
        'issue_url': 'https://github.com/DevNiola/Prism/issues/141',
        'settlement_wallet': '0x8366bCe3a2D379Dec7656D7A67015789FaF999f20',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'notes': 'PR #154 opened. Monopolio absoluto en DevNiola/Prism (5/5 PRs del repo). .pre-commit-config.yaml con rustfmt, clippy, prettier y eslint. Scripts en package.json (format:check, format:write, hooks:install, hooks:run), prettier devDependency y documentación en CONTRIBUTING.md.'
    }
    d['bounties'].insert(0, new_bounty)
    print('Added prism-issue-141 to bounties list!')

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
    'title': 'PR #154 Abierto en DevNiola/Prism (Issue #141)',
    'details': 'Pre-commit hooks implementados (.pre-commit-config.yaml) con rustfmt, clippy, prettier y eslint. 5/5 PRs monopólicas en el repositorio. Settlement Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20.',
    'severity': 'success'
}

events.insert(0, new_event)
with open(events_path, 'w', encoding='utf-8') as f:
    json.dump(events[:50], f, indent=2, ensure_ascii=False)

print('Updated live_events.json with PR #154 event!')
