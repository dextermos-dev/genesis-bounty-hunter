import json
from datetime import datetime, timezone

data_path = 'dashboard/data.json'
with open(data_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

existing_ids = [b.get('id') for b in d.get('bounties', [])]
if 'prism-issue-140' not in existing_ids:
    new_bounty = {
        'id': 'prism-issue-140',
        'title': 'chore(devops): add dependabot configuration for dependency updates (closes #140)',
        'repository': 'DevNiola/Prism',
        'maintainer': '@DevNiola',
        'platform': 'GitHub / Stellar Wave',
        'bounty_type': 'DevOps & Automation',
        'reward': '70 USDC',
        'reward_amount': 70.0,
        'status': 'In Review',
        'pr_url': 'https://github.com/DevNiola/Prism/pull/150',
        'issue_url': 'https://github.com/DevNiola/Prism/issues/140',
        'settlement_wallet': '0x8366bCe3a2D379Dec7656D7A67015789FaF999f20',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'notes': 'PR #150 opened. Primer PR en la historia del repositorio DevNiola/Prism (monopolio 100%). Añade .github/dependabot.yml con actualización semanal y agrupación de dependencias menores/parche en Cargo, npm y GitHub Actions. Validación schema official exitosa.'
    }
    d['bounties'].insert(0, new_bounty)
    print('Added prism-issue-140 to bounties list!')

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

print('Updated data.json successfully!')
print(f'Won: ${won_sum} ({len(won_bounties)} PRs)')
print(f'In Review: ${in_review_sum} ({len(in_review_bounties)} PRs)')
print(f'Total Pipeline: ${won_sum + in_review_sum} ({d["submitted_prs_count"]} PRs)')
