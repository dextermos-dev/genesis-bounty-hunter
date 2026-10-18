import json
from datetime import datetime, timezone
import requests
from dotenv import dotenv_values

data_path = 'dashboard/data.json'
with open(data_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

existing_ids = [b.get('id') for b in d.get('bounties', [])]

# Add prism-issue-147 if not present
if 'prism-issue-147' not in existing_ids:
    d['bounties'].insert(0, {
        'id': 'prism-issue-147',
        'title': 'feat(devops): add Terraform configuration for AWS deployment (closes #147)',
        'repository': 'DevNiola/Prism',
        'maintainer': '@DevNiola',
        'platform': 'GitHub / Stellar Wave',
        'bounty_type': 'Infrastructure as Code',
        'reward': '70 USDC',
        'reward_amount': 70.0,
        'status': 'In Review',
        'pr_url': 'https://github.com/DevNiola/Prism/pull/160',
        'issue_url': 'https://github.com/DevNiola/Prism/issues/147',
        'settlement_wallet': '0x8366bCe3a2D379Dec7656D7A67015789FaF999f20',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'notes': 'PR #160 opened. AWS Terraform configuration with multi-AZ VPC, ALB dual target groups, ElastiCache Redis, ECS Fargate services for server and web, and Route53/ACM support.'
    })
    print('Added prism-issue-147 to bounties!')

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
    'title': 'PR #160 Abierto en DevNiola/Prism (Issue #147 - $70 USDC)',
    'details': 'Infraestructura Terraform para AWS implementada (deploy/terraform/) con VPC, ALB, ElastiCache Redis y ECS Fargate. 11/11 PRs en Prism. Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20.',
    'severity': 'success'
})

events.insert(0, {
    'timestamp': datetime.now().strftime('%H:%M:%S'),
    'type': 'APPLICATION',
    'title': 'Postulación Formal Enviada a MindVault Mobile (Batch 3 #191)',
    'details': 'Dossier de postulación técnica y 5 PRs mergeadas en Stellar enviado a mindvault_mobile #191. Esperando asignación oficial de mantenedor. Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20.',
    'severity': 'info'
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
        "🚀 *PR #160 ENTREGADO — TERRAFORM AWS EN PRISM*\n\n"
        "📦 *PR #160:* AWS Terraform Modules (Issue #147 — $70 USDC)\n"
        "👑 *Dominio Prism:* 11/11 PRs del repositorio ($780.00 USDC bajo control)\n"
        "⚡ *MindVault Mobile:* Postulación formal enviada en Issue #191 (Batch 3)\n\n"
        "📊 *Métricas Consolidadas:*\n"
        "   • Sprint Micro-Bounties: $1,755.00 USDC (23 PRs)\n"
        "     - Ganado Oficial: $685.00 USDC (8 PRs)\n"
        "     - En Revisión: $1,070.00 USDC (15 PRs)\n"
        "   • Grants & Hackathons: $30,400.00 USDC (19 submissions)\n"
        "   • Gran Total Presentado: $35,155.00 USDC\n"
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
