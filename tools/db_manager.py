#!/usr/bin/env python3
"""
tools/db_manager.py
Herramienta de gestión, consulta, backup y sincronización para la
Base de Datos Maestra SQLite de Bounty Hunter AI.
"""

import os
import sys
import json
import sqlite3
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "bounty_hunter_master.sqlite")
DUMP_PATH = os.path.join(BASE_DIR, "database", "bounty_hunter_master_dump.sql")

def get_connection():
    if not os.path.exists(DB_PATH):
        print(f"[-] Base de datos no encontrada en {DB_PATH}.")
        print("[*] Ejecute primero: python3 tools/init_and_migrate_database.py")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def show_stats():
    conn = get_connection()
    cur = conn.cursor()
    print("=" * 65)
    print("ESTADÍSTICAS GENERALES DE LA BASE DE DATOS MAESTRA")
    print(f"Ruta: {DB_PATH} ({os.path.getsize(DB_PATH):,} bytes)")
    print("=" * 65)

    tables = ["bounties", "won_prs", "wallets", "transactions_ledger", "portfolio_snapshots", "mining_telemetry", "maintainer_feedback"]
    for t in tables:
        cur.execute(f"SELECT count(*) FROM {t};")
        cnt = cur.fetchone()[0]
        print(f"  • Tabla '{t}': {cnt:,} registros")

    print("\n" + "-" * 65)
    print("ÚLTIMO SNAPSHOT FINANCIERO REGISTRADO:")
    print("-" * 65)
    cur.execute("SELECT * FROM portfolio_snapshots ORDER BY id DESC LIMIT 1;")
    snap = cur.fetchone()
    if snap:
        print(f"  Fecha Snapshot:            {snap['snapshot_date']}")
        print(f"  Saldo Líquido Real:        ${snap['total_liquid_usd']:,.2f} USD")
        print(f"  Ganado Pendiente (Main):   ${snap['won_pending_usd']:,.2f} USDC ({snap['won_prs_count']} PRs)")
        print(f"  Cobro Confirmado Lunes:    ${snap['confirmed_monday_usd']:,.2f} USDC (Chain-Love)")
        print(f"  Pipeline Global Evaluación:${snap['active_global_review_usd']:,.2f} USDC ({snap['tracked_bounties_count']} bounties)")
        print(f"    └─ Sprints GitHub:       ${snap['sprint_review_usd']:,.2f} USDC")
        print(f"    └─ Grants & Hackathons:  ${snap['grants_review_usd']:,.2f} USDC")
        print(f"  Histórico / Archivados:    ${snap['archived_pipeline_usd']:,.2f} USD")
        print(f"  GRAN TOTAL MONITOREADO:    ${snap['grand_total_monitored_usd']:,.2f} USD")
        print(f"  Settlement Wallet:         {snap['settlement_wallet']}")
    print("=" * 65)
    conn.close()

def list_won_prs():
    conn = get_connection()
    cur = conn.cursor()
    print("=" * 75)
    print("LISTADO AUDITADO DE PRS GANADAS (WON / LANDED ON MAIN)")
    print("=" * 75)
    cur.execute("SELECT id, repo, pr, nominal_amount_usd, audited_amount_usd, title, status FROM won_prs ORDER BY id ASC;")
    rows = cur.fetchall()
    total_nom = 0
    total_aud = 0
    for r in rows:
        nom = r['nominal_amount_usd']
        aud = r['audited_amount_usd']
        total_nom += nom
        total_aud += aud
        diff = f" (Auditado a ${aud:,.2f})" if nom != aud else ""
        print(f"[{r['id']}] {r['repo']} {r['pr']} -> ${nom:,.2f}{diff}")
        print(f"      Título: {r['title'][:65]}")
    print("-" * 75)
    print(f"Total Nominal: ${total_nom:,.2f} USDC | Total Auditado Real: ${total_aud:,.2f} USDC")
    print("=" * 75)
    conn.close()

def export_dump():
    conn = get_connection()
    print(f"[*] Exportando volcado SQL hacia {DUMP_PATH}...")
    with open(DUMP_PATH, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")
    print(f"[+] Volcado SQL actualizado ({os.path.getsize(DUMP_PATH):,} bytes).")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Gestor de Base de Datos Bounty Hunter AI")
    parser.add_argument("command", choices=["stats", "won-prs", "export", "dump"], help="Comando a ejecutar")
    args = parser.parse_args()

    if args.command == "stats":
        show_stats()
    elif args.command == "won-prs":
        list_won_prs()
    elif args.command in ["export", "dump"]:
        export_dump()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        show_stats()
    else:
        main()
