import json

with open("dashboard/data.json", "r") as f:
    d = json.load(f)

# Add Bounty #6 and #7 to fast_bounties_today
b6 = {
    "id": "solana-6",
    "name": "Grounded Citation Verifier & DPO Synthesizer (t=21)",
    "platform": "Solana Mainnet",
    "amount": "$22.00",
    "crypto": "0.1000 SOL",
    "status": "Entregado en GitHub Issue #6",
    "target": "Escrow Vault 6cXR7EkU...XN",
    "url": "https://github.com/incidere/solana-agent-bounties/issues/6"
}

b7 = {
    "id": "solana-7",
    "name": "DeFi Derivative Stripper & Implied-FDV Ranker (t=22)",
    "platform": "Solana Mainnet",
    "amount": "$26.40",
    "crypto": "0.1200 SOL",
    "status": "Entregado en GitHub Issue #7",
    "target": "Escrow Vault 6cXR7EkU...XN",
    "url": "https://github.com/incidere/solana-agent-bounties/issues/7"
}

# Update list
fast = d.get("fast_bounties_today", [])
# prepend or append
fast.append(b6)
fast.append(b7)
d["fast_bounties_today"] = fast

# Update KPI
d["kpis"]["fast_bounties_today_usd"] = 286.80

with open("dashboard/data.json", "w") as f:
    json.dump(d, f, indent=2)

print("✅ data.json updated with 9 fast bounties totaling $286.80 USD!")

# Now update app.js ACTIVE_FAST_BOUNTIES array
with open("dashboard/app.js", "r") as f:
    app_js = f.read()

# Add to ACTIVE_FAST_BOUNTIES array in app.js
new_entries = """  {
    id: "solana-6",
    platform: "Solana Mainnet",
    platformClass: "solana",
    title: "Grounded Citation Verifier & DPO Synthesizer (t=21)",
    rewardUsd: "$22.00",
    rewardCrypto: "0.1000 SOL",
    statusText: "Entregado (32 Tests)",
    highlightText: "🛡️ 4 Hard Gates + DPO Mode Synthesizer",
    blockInfo: "Escrow: 6cXR7EkU...XN",
    rail: "Solana Mainnet (Zero-Gas)",
    url: "https://github.com/incidere/solana-agent-bounties/issues/6",
    linkText: "Ver Entrega GitHub ↗"
  },
  {
    id: "solana-7",
    platform: "Solana Mainnet",
    platformClass: "solana",
    title: "DeFi Derivative Stripper & Implied-FDV Ranker (t=22)",
    rewardUsd: "$26.40",
    rewardCrypto: "0.1200 SOL",
    statusText: "Entregado (42 Tests)",
    highlightText: "⚡ Zero-Network Node 22+ CLI (Byte-Identical)",
    blockInfo: "Escrow: 6cXR7EkU...XN",
    rail: "Solana Mainnet (Zero-Gas)",
    url: "https://github.com/incidere/solana-agent-bounties/issues/7",
    linkText: "Ver Entrega GitHub ↗"
  },
"""

# Insert right after const ACTIVE_FAST_BOUNTIES = [
app_js = app_js.replace("const ACTIVE_FAST_BOUNTIES = [\n", "const ACTIVE_FAST_BOUNTIES = [\n" + new_entries)

with open("dashboard/app.js", "w") as f:
    f.write(app_js)

print("✅ dashboard/app.js updated with both new Solana bounties!")

