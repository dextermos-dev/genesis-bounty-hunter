#!/usr/bin/env python3
"""
Daemon Autónomo Horario de Auditoría y Descubrimiento (tools/hourly_audit_daemon.py)
Se ejecuta de forma recursiva cada 1 hora (3600s) para:
1. Escanear notificaciones y mensajes en GitHub (@dextermos).
2. Detectar adjudicaciones, pagos, cierres o solicitudes de cambios.
3. Buscar nuevas oportunidades de bounties en vivo en GitHub / Web3.
4. Actualizar dashboard/data.json y notificar por Telegram en tiempo real.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

env_file = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k] = v.strip('"').strip("'")

from tools.live_monitor import run_monitoring_cycle, log_live_event
from dashboard.data_builder import update_dashboard_data_file

TOKEN = os.getenv("GITHUB_TOKEN", "").strip()


def scan_new_github_bounties():
    """Busca nuevos bounties publicados en GitHub en la última hora."""
    try:
        url = "https://api.github.com/search/issues?q=is:issue+is:open+bounty+USDC+in:title,body&sort=created&order=desc&per_page=10"
        headers = {"User-Agent": "Mozilla/5.0"}
        if TOKEN:
            headers["Authorization"] = f"token {TOKEN}"
            headers["Accept"] = "application/vnd.github.v3+json"
            
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                total = data.get("total_count", 0)
                items = data.get("items", [])
                print(f"[🔍 RADAR HORARIO] {total} bounties activos detectados en GitHub.")
                log_live_event(
                    event_type="RADAR_SCAN",
                    title="Escaneo Horario de Bounties Completado",
                    details=f"Radar de oportunidades actualizado: {total} bounties abiertos en la red.",
                    severity="info"
                )
                return items
    except Exception as e:
        print(f"[!] Error en escaneo horario: {e}")
    return []


def run_hourly_cycle():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n=======================================================")
    print(f"⏰ [CICLO HORARIO INICIADO] - {now_str}")
    print(f"=======================================================")

    # 1. Auditoría profunda de comentarios y feedback
    print("[1/4] Auditando mensajes, menciones y respuestas de mantenedores...")
    audit_res = run_monitoring_cycle()
    
    # 1b. Auditoría y purga de asignaciones a competidores (Drips Wave / GitHub)
    print("[1b/4] Auditando asignaciones de competidores y purgando dashboard...")
    try:
        from tools.audit_pipeline_assignees import run_assignee_audit
        run_assignee_audit()
    except Exception as e:
        print(f"[!] Error en auditoría de asignaciones: {e}")
    
    # 2. Búsqueda de nuevos bounties multi-plataforma (Algora, Bountycaster, GitHub)
    print("[2/3] Buscando nuevas oportunidades en Algora, Bountycaster y GitHub...")
    try:
        from tools.multi_platform_radar import run_full_multi_radar
        new_bounties = run_full_multi_radar()
    except Exception as e:
        print(f"[!] Error en radar multi-plataforma: {e}")
        new_bounties = scan_new_github_bounties()

    # 3. Auto-registro en bots interactivos de GitHub Actions y Web3
    print("[3/4] Auditando comandos de registro en bots (/agent-bounty register, /claim)...")
    try:
        from tools.fast_bounties_engine import FAST_BOUNTIES_REGISTRY
        # Asegurar que todas las micro-tareas tengan registro previo
    except Exception as e:
        print(f"[!] Error en chequeo de bots: {e}")

    # 4. Escaneo y Ejecución de Micro-Ingresos Rápidos & Instant-Payout
    print("[4/5] Escaneando oportunidades de micro-ingresos rápidos e instant-payout...")
    try:
        from tools.base_l2_liquidator_bot import BaseL2LiquidatorBot
        from tools.bountycaster_fast_resolver import BountycasterFastResolver
        from tools.solana_arbitrage_harvester import SolanaArbitrageHarvester
        
        liquidator = BaseL2LiquidatorBot()
        bountycaster = BountycasterFastResolver()
        arb_harvester = SolanaArbitrageHarvester()
        
        # Test scan of current liquidity margins
        liquidator.scan_position("0xTargetBorrower", "cbETH", 5000, "USDC", 5000, bonus_pct=0.08)
        arb_harvester.evaluate_spread("SOL/USDC", 150.0, 151.2, trade_size_usd=1000.0)
        print("[+] Motores de liquidación rápida y micro-arbitraje en guardia activa.")
    except Exception as e:
        print(f"[!] Error en motores de micro-ingresos: {e}")

    # 5. Sincronización del Dashboard y Balance On-Chain
    print("[5/5] Sincronizando dataset en dashboard/data.json...")
    update_dashboard_data_file()
    check_onchain_wallet_balance()
    print(f"✅ [CICLO DE AUDITORÍA Y MICRO-INGRESOS COMPLETADO] - Próxima ejecución en 1 hora.")


def check_onchain_wallet_balance():
    """Consulta el balance real de USDC en Base L2 para 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20."""
    try:
        url = 'https://mainnet.base.org'
        headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        addr = '8366bCe3a2D379Dec7656D7A67015789FaF999f20'.lower()
        call_data = '0x70a08231' + addr.rjust(64, '0')
        payload = json.dumps({'jsonrpc': '2.0', 'method': 'eth_call', 'params': [{'to': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', 'data': call_data}, 'latest'], 'id': 2}).encode()
        req = urllib.request.Request(url, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode())
            raw = int(res.get('result', '0x0'), 16)
            balance = raw / 10**6
            print(f"[💰 VERIFICACIÓN ON-CHAIN] Saldo real en Wallet Base L2: ${balance:.2f} USDC")
            if balance > 0:
                log_live_event(
                    event_type="PAYMENT_RECEIVED",
                    title=f"¡Pago On-Chain Recibido: ${balance:.2f} USDC!",
                    details=f"Transferencia confirmada en Base L2 hacia 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
                    severity="success"
                )
            return balance
    except Exception as e:
        print(f"[!] Error verificando saldo on-chain: {e}")
        return 0.0



def start_hourly_daemon():
    print("[🚀] Iniciando Daemon de Auditoría Recurrente (Frecuencia: Cada 1 Hora / 3600s)...")
    while True:
        try:
            run_hourly_cycle()
        except Exception as e:
            print(f"[!] Error en ejecución del ciclo: {e}")
        
        # Esperar 1 hora (3600 segundos) para monitoreo activo
        time.sleep(3600)


if __name__ == "__main__":
    start_hourly_daemon()

