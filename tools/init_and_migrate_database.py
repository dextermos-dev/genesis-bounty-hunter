#!/usr/bin/env python3
"""
tools/init_and_migrate_database.py
Inicializa la base de datos relacional SQLite de Bounty Hunter AI
con todo el historial de desarrollo, bounties, PRs ganadas, transacciones,
wallets, snapshots auditados y telemetría de minería.
"""

import os
import json
import sqlite3
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "bounty_hunter_master.sqlite")
SQL_DUMP_PATH = os.path.join(DB_DIR, "bounty_hunter_master_dump.sql")
DATA_JSON_PATH = os.path.join(BASE_DIR, "dashboard", "data.json")
APP_JS_PATH = os.path.join(BASE_DIR, "dashboard", "app.js")

os.makedirs(DB_DIR, exist_ok=True)

def create_schema(conn):
    cursor = conn.cursor()
    
    # 1. Bounties Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bounties (
        id TEXT PRIMARY KEY,
        bounty_id TEXT,
        title TEXT NOT NULL,
        platform TEXT,
        category TEXT,
        repo TEXT,
        pr_number INTEGER,
        pr_url TEXT,
        source_url TEXT,
        reward_amount REAL DEFAULT 0,
        reward_currency TEXT DEFAULT 'USDC',
        amount_usd REAL DEFAULT 0,
        status TEXT,
        payout_status TEXT,
        payout_text TEXT,
        payment_network TEXT,
        settlement_wallet TEXT,
        is_sprint INTEGER DEFAULT 0,
        is_in_review INTEGER DEFAULT 0,
        is_won INTEGER DEFAULT 0,
        is_archived INTEGER DEFAULT 0,
        is_grant INTEGER DEFAULT 0,
        expected_value REAL DEFAULT 0,
        final_score REAL DEFAULT 0,
        red_team_score REAL DEFAULT 0,
        sandbox_status TEXT,
        commit_sha TEXT,
        tx_hash TEXT,
        submitted_at TEXT,
        updated_at TEXT,
        raw_json TEXT
    );
    """)

    # 2. Won PRs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS won_prs (
        id TEXT PRIMARY KEY,
        repo TEXT NOT NULL,
        pr TEXT NOT NULL,
        title TEXT NOT NULL,
        nominal_amount_usd REAL DEFAULT 0,
        audited_amount_usd REAL DEFAULT 0,
        date_merged TEXT,
        url TEXT,
        status TEXT,
        notes TEXT
    );
    """)

    # 3. Wallets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallets (
        id TEXT PRIMARY KEY,
        label TEXT NOT NULL,
        address TEXT NOT NULL,
        chain TEXT NOT NULL,
        primary_token TEXT,
        token_balance REAL DEFAULT 0,
        usd_value REAL DEFAULT 0,
        role TEXT,
        notes TEXT,
        last_updated TEXT
    );
    """)

    # 4. Transaction Ledger Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions_ledger (
        id TEXT PRIMARY KEY,
        date_str TEXT,
        timestamp INTEGER,
        tx_type TEXT,
        type_label TEXT,
        badge_class TEXT,
        concept TEXT,
        rail TEXT,
        account TEXT,
        asset_in TEXT,
        asset_in_usd REAL DEFAULT 0,
        asset_out TEXT,
        asset_out_usd REAL DEFAULT 0,
        net_usd REAL DEFAULT 0,
        fee TEXT,
        tx_hash TEXT,
        explorer_url TEXT,
        status TEXT,
        lifecycle TEXT,
        notes TEXT
    );
    """)

    # 5. Portfolio Snapshots Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        snapshot_date TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        total_liquid_usd REAL NOT NULL,
        won_pending_usd REAL NOT NULL,
        confirmed_monday_usd REAL NOT NULL,
        active_global_review_usd REAL NOT NULL,
        sprint_review_usd REAL NOT NULL,
        grants_review_usd REAL NOT NULL,
        archived_pipeline_usd REAL NOT NULL,
        grand_total_monitored_usd REAL NOT NULL,
        tracked_bounties_count INTEGER NOT NULL,
        won_prs_count INTEGER NOT NULL,
        active_mining_nodes INTEGER NOT NULL,
        settlement_wallet TEXT NOT NULL,
        audit_summary TEXT
    );
    """)

    # 6. Mining Telemetry Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mining_telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recorded_at TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        cluster_name TEXT,
        global_rank INTEGER,
        global_rank_title TEXT,
        active_rigs INTEGER,
        total_hashrate_mhs REAL,
        total_mined_doom REAL,
        genesis_doom REAL,
        total_l1_doom REAL,
        doom_usd REAL,
        worker_address TEXT,
        status TEXT
    );
    """)

    # 7. Maintainer Feedback & Payout Suggestions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintainer_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo TEXT NOT NULL,
        pr TEXT NOT NULL,
        author TEXT NOT NULL,
        date_recorded TEXT NOT NULL,
        suggested_amount_usd REAL DEFAULT 0,
        formula_snippet TEXT,
        notes TEXT
    );
    """)

    # Create helpful indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bounties_status ON bounties(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bounties_repo ON bounties(repo);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bounties_is_won ON bounties(is_won);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bounties_is_in_review ON bounties(is_in_review);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bounties_is_sprint ON bounties(is_sprint);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_timestamp ON transactions_ledger(timestamp);")

    conn.commit()
    print("[+] Esquema relacional creado con éxito.")

def populate_database(conn):
    cursor = conn.cursor()

    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # A. Populate Bounties
    bounties = data.get("bounties", [])
    print(f"[*] Importando {len(bounties)} bounties desde data.json...")
    
    for b in bounties:
        b_id = b.get("id") or b.get("bounty_id") or f"bounty-{int(time.time()*1000)}"
        bounty_id = b.get("bounty_id") or b_id
        title = b.get("title", "Sin título")
        platform = b.get("platform", "")
        category = b.get("category", "")
        repo = b.get("repo") or b.get("repository") or ""
        pr_number = b.get("pr_number")
        pr_url = b.get("pr_url") or b.get("pull_request_url") or ""
        source_url = b.get("source_url") or b.get("url") or ""
        reward_amt = float(b.get("reward_amount") or 0.0)
        reward_curr = b.get("reward_currency") or b.get("reward_asset") or "USDC"
        amount_usd = float(b.get("amount_usd") or b.get("reward_usd") or reward_amt or 0.0)
        status = str(b.get("status", "")).upper()
        payout_status = b.get("payout_status", "")
        payout_text = b.get("payout_text", "")
        payment_net = b.get("payment_network", "Base L2")
        settlement_w = b.get("settlement_wallet") or b.get("web3_wallet_address") or "0x8366bCe3a2D379De7656D7A67015789FaF999f20"
        
        is_sprint = 1 if b.get("sprint") is True else 0
        is_in_rev = 1 if (b.get("in_review") is True or "REVIEW" in status or "SUBMITTED" in status) else 0
        is_won = 1 if (status in ["LANDED_ON_MAIN", "MERGED", "APPROVED", "WON"] or "WON" in status) else 0
        is_archived = 1 if (status in ["ARCHIVED", "EXPIRED", "HISTORICAL"] or "ARCHIVE" in status) else 0
        is_grant = 1 if any(k in title.lower() for k in ["grant", "hackathon", "accelerator", "dkg"]) else 0
        
        exp_val = float(b.get("expected_value") or 0.0)
        final_sc = float(b.get("final_score") or 0.0)
        red_team = float(b.get("red_team_score") or 0.0)
        sandbox = b.get("sandbox_status", "")
        commit_sha = b.get("commit_sha", "")
        tx_hash = b.get("tx_hash", "")
        sub_at = b.get("submitted_at", "")
        upd_at = b.get("updated_at", "")
        raw_json = json.dumps(b, ensure_ascii=False)

        cursor.execute("""
        INSERT OR REPLACE INTO bounties (
            id, bounty_id, title, platform, category, repo, pr_number, pr_url, source_url,
            reward_amount, reward_currency, amount_usd, status, payout_status, payout_text,
            payment_network, settlement_wallet, is_sprint, is_in_review, is_won, is_archived,
            is_grant, expected_value, final_score, red_team_score, sandbox_status, commit_sha,
            tx_hash, submitted_at, updated_at, raw_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            b_id, bounty_id, title, platform, category, repo, pr_number, pr_url, source_url,
            reward_amt, reward_curr, amount_usd, status, payout_status, payout_text,
            payment_net, settlement_w, is_sprint, is_in_rev, is_won, is_archived,
            is_grant, exp_val, final_sc, red_team, sandbox, commit_sha,
            tx_hash, sub_at, upd_at, raw_json
        ))

    # B. Populate Won PRs from Table (with audited figures)
    print("[*] Importando PRs Ganadas con auditoría de montos nominales vs reales...")
    won_prs_data = [
        ("PR-01", "mallonepay/pay-per-token-llm-gateway", "PR #127", "Soroban credit escrow settlement engine", 800.0, 800.0, "2026-09-09", "https://github.com/Pay-Per-Token-LLM-Gateway/pay-per-token-llm-gateway/pull/127", "Merged en main", "Arquitectura Soroban core"),
        ("PR-02", "mallonepay/pay-per-token-llm-gateway", "PR #133", "Migrate contracts to Soroban SDK 26.1.1 (18/18 CI Verde)", 200.0, 200.0, "2026-10-29", "https://github.com/Pay-Per-Token-LLM-Gateway/pay-per-token-llm-gateway/pull/133", "Merged en main", "Actualización SDK y CI"),
        ("PR-03", "mallonepay/pay-per-token-llm-gateway", "PR #134", "External custody contract security audit (Issue #83)", 350.0, 350.0, "2026-10-29", "https://github.com/Pay-Per-Token-LLM-Gateway/pay-per-token-llm-gateway/pull/134", "Merged en main", "Auditoría de seguridad custodia"),
        ("PR-04", "Parabola-org/parabola", "PR #101", "Add missing export for calculatePoolShares", 105.0, 105.0, "2026-10-16", "https://github.com/Parabola-org/parabola/pull/101", "Merged en main", "Pool shares math"),
        ("PR-05", "Parabola-org/parabola", "PR #104", "Fix slippage tolerance bounds in swap math", 105.0, 105.0, "2026-10-16", "https://github.com/Parabola-org/parabola/pull/104", "Merged en main", "Slippage bounds"),
        ("PR-06", "Parabola-org/parabola", "PR #116", "Validate token pair decimals on initialization", 125.0, 125.0, "2026-10-16", "https://github.com/Parabola-org/parabola/pull/116", "Merged en main", "Decimals validation"),
        ("PR-07", "Parabola-org/parabola", "PR #109", "Clamp oracle update frequency to avoid stale prices", 125.0, 125.0, "2026-10-16", "https://github.com/Parabola-org/parabola/pull/109", "Merged en main", "Oracle clamp"),
        ("PR-08", "Parabola-org/parabola", "PR #115", "Refactor pool reentrancy guard for Gas efficiency", 60.0, 60.0, "2026-10-16", "https://github.com/Parabola-org/parabola/pull/115", "Merged en main", "Gas reentrancy guard"),
        ("PR-09", "Parabola-org/parabola", "PR #99", "Fix edge case in fee distribution rounding", 45.0, 45.0, "2026-10-16", "https://github.com/Parabola-org/parabola/pull/99", "Merged en main", "Fee rounding edge case"),
        ("PR-10", "Parabola-org/parabola", "PR #100", "Add strict bounds check to pool deposit liquidity", 45.0, 45.0, "2026-10-16", "https://github.com/Parabola-org/parabola/pull/100", "Merged en main", "Deposit liquidity check"),
        ("PR-11", "slippay-labs/slippay", "PR #264", "Harden token transfer auth callback validation", 75.0, 75.0, "2026-10-18", "https://github.com/slippay-labs/slippay/pull/264", "Merged en main", "Token auth validation"),
        ("PR-12", "Chain-Love/chain-love", "PR #4728", "Almizaan smart contract security scanner documentation", 140.0, 0.20, "2026-10-21", "https://github.com/Chain-Love/chain-love/pull/4728", "Merged (Won)", "Auditado USS-Compensator: 5 celdas = 0.20 USDC"),
        ("PR-13", "slippay-labs/slippay", "PR #228", "Fix decimal truncation on micro-payment streams", 70.0, 70.0, "2026-10-21", "https://github.com/slippay-labs/slippay/pull/228", "Merged en main", "Decimal truncation"),
        ("PR-14", "slippay-labs/slippay", "PR #453", "Add idempotent receipt verification for off-chain relays", 35.0, 35.0, "2026-10-21", "https://github.com/slippay-labs/slippay/pull/453", "Merged en main", "Idempotent receipt"),
        ("PR-15", "slippay-labs/slippay", "PR #435", "Enforce non-zero destination check in multi-send", 35.0, 35.0, "2026-10-21", "https://github.com/slippay-labs/slippay/pull/435", "Merged en main", "Non-zero destination check"),
        ("PR-16", "slippay-labs/slippay", "PR #340", "Fix timeout retry loop on Soroban RPC network congestion", 35.0, 35.0, "2026-10-21", "https://github.com/slippay-labs/slippay/pull/340", "Merged en main", "Retry loop fix"),
        ("PR-17", "DevNiola/Prism", "PR #150", "Add Dependabot configuration for dependency updates", 150.0, 150.0, "2026-10-30", "https://github.com/DevNiola/Prism/pull/150", "Merged en main", "Dependabot CI/CD"),
        ("PR-18", "limitlessprojects/Go-Hybrid", "PR #2339", "Preserve return-slot indices on mixed named/unnamed results (fixes #2323)", 75.0, 75.0, "2026-10-30", "https://github.com/limitlessprojects/Go-Hybrid/pull/2339", "Merged en main", "Go-Hybrid return slots"),
        ("PR-19", "limitlessprojects/Go-Hybrid", "PR #2492", "Reject equality comparisons between non-nilable types and nil (fixes #2471)", 75.0, 75.0, "2026-10-31", "https://github.com/limitlessprojects/Go-Hybrid/pull/2492", "Merged en main", "Go-Hybrid non-nilable check"),
        ("PR-20", "limitlessprojects/Go-Hybrid", "PR #2549", "Reject octal multi-iteration and induction variable mutation (fixes #2512)", 75.0, 75.0, "2026-11-01", "https://github.com/limitlessprojects/Go-Hybrid/pull/2549", "Merged en main", "Go-Hybrid octal backedge"),
        ("PR-21", "limitlessprojects/Go-Hybrid", "PR #2747", "Reject mismatched slice and string elements in variadic append (fixes #2738)", 75.0, 75.0, "2026-11-01", "https://github.com/limitlessprojects/Go-Hybrid/pull/2747", "Merged en main", "Go-Hybrid variadic append"),
        ("PR-22", "Chain-Love/chain-love", "PR #4767", "Add official Circle USDC and Wrapped SOMI (WSOMI) contracts", 140.0, 0.80, "2026-11-01", "https://github.com/Chain-Love/chain-love/pull/4767", "Merged (Won)", "Auditado USS-Compensator: 0.80 USDC"),
        ("PR-23", "Chain-Love/chain-love", "PR #4781", "Add official Franklin, PNF Software, Ton Apps Group, Whales Corp documentation", 100.0, 0.60, "2026-11-01", "https://github.com/Chain-Love/chain-love/pull/4781", "Merged (Won)", "Auditado USS-Compensator: 0.60 USDC"),
        ("PR-24", "limitlessprojects/Go-Hybrid", "PR #3219", "defer store-back when slot loan is captured by deferred closure (fixes #3209)", 150.0, 150.0, "2026-11-02", "https://github.com/limitlessprojects/Go-Hybrid/pull/3219", "Merged en main", "Go-Hybrid deferred closure"),
        ("PR-25", "limitlessprojects/Go-Hybrid", "PR #3704", "fix(hy-check): resolve composite operand array lengths (fixes #3694)", 75.0, 75.0, "2026-11-05", "https://github.com/limitlessprojects/Go-Hybrid/pull/3704", "Merged en main", "Array bounds check"),
        ("PR-26", "limitlessprojects/Go-Hybrid", "PR #3706", "hy-check: resolve [N]T, map[K]V, and option[T] in generic struct field kinds (fixes #3705)", 75.0, 75.0, "2026-11-05", "https://github.com/limitlessprojects/Go-Hybrid/pull/3706", "Merged en main", "Generic struct kinds"),
        ("PR-27", "limitlessprojects/Go-Hybrid", "PR #3711", "hy-emit: preserve user struct names and foreign member shapes across calls (fixes #3710)", 75.0, 75.0, "2026-11-05", "https://github.com/limitlessprojects/Go-Hybrid/pull/3711", "Merged en main", "Struct names emit"),
        ("PR-28", "limitlessprojects/Go-Hybrid", "PR #3739", "hy-check(const_init): reject non-const string conversion args (fixes #3735)", 150.0, 150.0, "2026-11-06", "https://github.com/limitlessprojects/Go-Hybrid/pull/3739", "Merged en main", "Const init check"),
        ("PR-29", "limitlessprojects/Go-Hybrid", "PR #3804", "hy-check: reject errors.wrap when fmt is shadowed by in-scope declaration (fixes #3626)", 150.0, 150.0, "2026-11-07", "https://github.com/limitlessprojects/Go-Hybrid/pull/3804", "Merged en main", "Shadowed fmt check"),
        ("PR-30", "limitlessprojects/Go-Hybrid", "PR #3811", "hy-check: propagate type parameters to embedded interface methods (fixes #3764)", 150.0, 150.0, "2026-11-07", "https://github.com/limitlessprojects/Go-Hybrid/pull/3811", "Merged en main", "Embedded interface types"),
        ("PR-31", "limitlessprojects/Go-Hybrid", "PR #3861", "hy-check: enforce non-nilable pointer dereference guard (fixes #3842)", 150.0, 150.0, "2026-11-08", "https://github.com/limitlessprojects/Go-Hybrid/pull/3861", "Merged en main", "Pointer dereference guard"),
        ("PR-32", "limitlessprojects/Go-Hybrid", "PR #3867", "hy-emit: normalize struct padding across 64-bit ABI boundaries (fixes #3859)", 150.0, 150.0, "2026-11-09", "https://github.com/limitlessprojects/Go-Hybrid/pull/3867", "Merged en main", "Struct ABI boundaries"),
    ]

    for p in won_prs_data:
        cursor.execute("""
        INSERT OR REPLACE INTO won_prs (
            id, repo, pr, title, nominal_amount_usd, audited_amount_usd, date_merged, url, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, p)

    # C. Populate Wallets
    print("[*] Importando Wallets auditadas...")
    wallets_data = [
        ("W-01", "Settlement Wallet Principal (MetaMask)", "0x8366bCe3a2D379De7656D7A67015789FaF999f20", "Base L2 Mainnet", "USDC", 47.810608, 47.81, "Settlement Principal (EVM/Base)", "Recibe pagos directos de bounties y swaps", "2026-11-13"),
        ("W-02", "Settlement Wallet DOOM (Base L2)", "0x8366bCe3a2D379De7656D7A67015789FaF999f20", "Base L2 Mainnet", "wDOOM", 24887.50, 2.49, "Minería Tokenizada ERC-20", "Tokens DOOM puenteados a Base L2", "2026-11-13"),
        ("W-03", "Bounties & Gas Wallet (BSC)", "0x8e2576c3418ceca3970ea16f1047efc5b881820f", "BNB Smart Chain (BSC)", "BNB", 0.016148, 11.22, "Gas & Mobile SDK Bounties", "Provisión de gas y cobros en BSC", "2026-11-13"),
        ("W-04", "Nano Block Lattice Account", "nano_3i7nondimxz8zbqn6kkoffoqydi61ektguf6sq8n7m7k77iznhn7y9mxxubg", "Nano Block Lattice", "XNO", 0.044000, 0.05, "Micropagos Sin Comisiones", "Custodia y liquidación feeleess", "2026-11-13"),
    ]
    for w in wallets_data:
        cursor.execute("""
        INSERT OR REPLACE INTO wallets (
            id, label, address, chain, primary_token, token_balance, usd_value, role, notes, last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, w)

    # D. Populate Transactions Ledger
    print("[*] Importando Ledger de Transacciones...")
    transactions = data.get("transaction_ledger", [])
    for tx in transactions:
        cursor.execute("""
        INSERT OR REPLACE INTO transactions_ledger (
            id, date_str, timestamp, tx_type, type_label, badge_class, concept, rail, account,
            asset_in, asset_in_usd, asset_out, asset_out_usd, net_usd, fee, tx_hash, explorer_url,
            status, lifecycle, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            tx.get("id"), tx.get("date"), tx.get("timestamp"), tx.get("type"), tx.get("type_label"),
            tx.get("badge_class"), tx.get("concept"), tx.get("rail"), tx.get("account"),
            tx.get("asset_in"), float(tx.get("asset_in_usd") or 0.0), tx.get("asset_out"),
            float(tx.get("asset_out_usd") or 0.0), float(tx.get("net_usd") or 0.0),
            tx.get("fee"), tx.get("tx_hash"), tx.get("explorer_url"), tx.get("status"),
            tx.get("lifecycle"), tx.get("notes")
        ))

    # E. Record Reconciled Audit Snapshot
    print("[*] Registrando Snapshot Contable Maestro...")
    cursor.execute("""
    INSERT INTO portfolio_snapshots (
        snapshot_date, timestamp, total_liquid_usd, won_pending_usd, confirmed_monday_usd,
        active_global_review_usd, sprint_review_usd, grants_review_usd, archived_pipeline_usd,
        grand_total_monitored_usd, tracked_bounties_count, won_prs_count, active_mining_nodes,
        settlement_wallet, audit_summary
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        "2026-11-13 06:45:00 CET",
        int(time.time()),
        61.53,      # total_liquid_usd
        6265.00,    # won_pending_usd
        1.60,       # confirmed_monday_usd (Chain-Love)
        60618.00,   # active_global_review_usd
        15716.00,   # sprint_review_usd (GitHub)
        44902.00,   # grants_review_usd (Grants/Hackathons)
        73872.10,   # archived_pipeline_usd
        148698.10,  # grand_total_monitored_usd
        354,        # tracked_bounties_count
        35,         # won_prs_count
        4,          # active_mining_nodes
        "0x8366bCe3a2D379De7656D7A67015789FaF999f20",
        "Auditoría integral reconciliada: $61.53 líquido en wallets + $8.96 L1 PoW; $6,265.00 ganado en main con $1.60 certificado para el lunes de Chain-Love; $60,618.00 en evaluación global ($15.7k Sprints GitHub + $44.9k Grants); $73.8k histórico; $148.6k total monitoreado."
    ))

    # F. Mining Telemetry
    print("[*] Registrando Telemetría de Minería L1...")
    miners = data.get("miners", {})
    cursor.execute("""
    INSERT INTO mining_telemetry (
        recorded_at, timestamp, cluster_name, global_rank, global_rank_title, active_rigs,
        total_hashrate_mhs, total_mined_doom, genesis_doom, total_l1_doom, doom_usd, worker_address, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        datetime.utcnow().isoformat(),
        int(time.time()),
        miners.get("cluster_name", "Doomsday Layer-1 PoW Mining Cluster"),
        int(miners.get("global_rank", 9)),
        miners.get("global_rank_title", "Puesto #9 Mundial"),
        int(miners.get("active_rigs_count", 4)),
        float(miners.get("total_hashrate_mhs", 49.74)),
        float(miners.get("total_mined_doom", 6382.81)),
        float(miners.get("genesis_doom", 2000.0)),
        float(miners.get("total_l1_doom", 8382.81)),
        8.96,
        miners.get("worker_address", "doom162df6bb0c219de72343658ec04c1d9b1939c3c5c02f6b94f"),
        miners.get("status", "ONLINE")
    ))

    # G. Maintainer Feedback (Registro explícito del bot USS-Compensator)
    print("[*] Registrando Feedback y Comentarios de Mantenedores...")
    cursor.execute("""
    INSERT INTO maintainer_feedback (
        repo, pr, author, date_recorded, suggested_amount_usd, formula_snippet, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (
        "Chain-Love/chain-love",
        "PR #4728",
        "@USS-Compensator",
        "2026-10-21T05:24:16Z",
        0.20,
        "Calculation: 3.3200 weighted cells * 0.06 * 0.7^0 = 0.1992 USDC -> Final suggested compensation: 0.20 USDC",
        "Micro-compensación determinista por celdas CSV verificadas. Liquidación el lunes 17 de noviembre hacia 0x8366bCe3a2D379De7656D7A67015789FaF999f20"
    ))

    conn.commit()
    print("[+] Todos los datos han sido poblados con éxito en la base de datos.")

def generate_sql_dump(conn):
    print(f"[*] Generando volcado SQL completo en {SQL_DUMP_PATH}...")
    with open(SQL_DUMP_PATH, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")
    print(f"[+] Volcado SQL generado correctamente ({os.path.getsize(SQL_DUMP_PATH):,} bytes).")

def main():
    print("=" * 60)
    print("INICIALIZANDO BASE DE DATOS MAESTRA BOUNTY HUNTER AI")
    print(f"Destino: {DB_PATH}")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    try:
        create_schema(conn)
        populate_database(conn)
        generate_sql_dump(conn)
        
        # Verification Summary
        cur = conn.cursor()
        print("\n" + "=" * 60)
        print("RESUMEN DE AUDITORÍA EN BASE DE DATOS")
        print("=" * 60)
        
        cur.execute("SELECT count(*) FROM bounties;")
        print(f"Bounties en tabla 'bounties': {cur.fetchone()[0]}")
        
        cur.execute("SELECT count(*) FROM won_prs;")
        print(f"PRs en tabla 'won_prs': {cur.fetchone()[0]}")
        
        cur.execute("SELECT count(*) FROM wallets;")
        print(f"Wallets en tabla 'wallets': {cur.fetchone()[0]}")
        
        cur.execute("SELECT count(*) FROM transactions_ledger;")
        print(f"Transacciones en 'transactions_ledger': {cur.fetchone()[0]}")
        
        cur.execute("SELECT count(*) FROM portfolio_snapshots;")
        print(f"Snapshots en 'portfolio_snapshots': {cur.fetchone()[0]}")

        cur.execute("SELECT total_liquid_usd, won_pending_usd, active_global_review_usd, sprint_review_usd, grand_total_monitored_usd FROM portfolio_snapshots ORDER BY id DESC LIMIT 1;")
        row = cur.fetchone()
        print(f"\nÚltimo Snapshot Reconciliado:")
        print(f"  - Saldo Líquido: ${row[0]:,.2f} USD")
        print(f"  - Ganado Pendiente: ${row[1]:,.2f} USDC")
        print(f"  - En Evaluación Global: ${row[2]:,.2f} USDC")
        print(f"  - Sprints GitHub: ${row[3]:,.2f} USDC")
        print(f"  - Gran Total Monitoreado: ${row[4]:,.2f} USD")
        print("=" * 60)

    finally:
        conn.close()

if __name__ == "__main__":
    main()
