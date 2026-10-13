#!/usr/bin/env python3
"""
Pipeline Cleaner & Realistic Categorizer
Classifies active October 2026 submissions vs archived past cycle bounties (August/September 2026).
Settlement Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
"""

import json
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard", "data.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

bounties = data.get("bounties", [])

ACTIVE_OCTOBER_KEYWORDS = [
    "webacy_startup_accelerator_grant",
    "solana_mobile_seeker_hackathon",
    "agentkit_action_provider_base_x402",
    "base_l2_agent_gateway_x402",
    "solana_anchor_guard_litesvm",
    "tenstorrent_fused_softmax_58495",
    "tenstorrent_cumsum_nan_guard_58986",
    "elizaos_m2m_zero_gas_plugin",
    "rustchain_mining_telemetry_engine",
    "rustchain_issue_8033",
    "soroban_escrow_5",
    "micro_x402_gateway_base",
    "micro_ci_binary_proof_claim",
    "micro_eliza_agent_plugin_base",
    "micro_solana_seeker_mwa",
    "micro_agentkit_escrow_settler",
    "arc_microgrants_circle_dorahacks",
    "cyfrin_issue_442_mcp_auditor",
    "spectral_auth_77",
    "spectral_hyperliquid_82",
    "gibwork_177"
]

active_count = 0
archived_count = 0
active_in_review_usd = 0.0
archived_usd = 0.0

for b in bounties:
    bid = b.get("bounty_id", "")
    amount = float(b.get("reward_amount", 0))

    is_october_active = any(k in bid for k in ACTIVE_OCTOBER_KEYWORDS)

    if is_october_active:
        b["status"] = "SUBMITTED"
        b["cycle"] = "OCTUBRE_2026_ACTIVO"
        b["in_review"] = True
        b["payout_status"] = "EN_EVALUACION_ACTIVA"
        active_count += 1
        active_in_review_usd += amount
    else:
        b["status"] = "ARCHIVADO"
        b["cycle"] = "CICLO_ANTERIOR_AGO_SEP"
        b["in_review"] = False
        b["payout_status"] = "CICLO_CERRADO_ARCHIVADO"
        archived_count += 1
        archived_usd += amount

data["total_bounties_count"] = len(bounties)
data["active_bounties_count"] = active_count
data["archived_bounties_count"] = archived_count
data["in_review_usd"] = round(active_in_review_usd, 2)
data["active_pipeline_value_usd"] = round(active_in_review_usd, 2)
data["archived_pipeline_usd"] = round(archived_usd, 2)
data["total_pipeline_value_usd"] = round(active_in_review_usd + archived_usd, 2)
data["submitted_prs_count"] = active_count

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"=== PIPELINE PURIFICATION COMPLETE ===")
print(f"🌟 Bounties Activos (Octubre 2026): {active_count} | ${active_in_review_usd:,.2f} USDC")
print(f"🏛️ Bounties Archivados (Ciclos Pasados): {archived_count} | ${archived_usd:,.2f} USDC")
print(f"📊 Total General Registrado: {len(bounties)} | ${active_in_review_usd + archived_usd:,.2f} USDC")
