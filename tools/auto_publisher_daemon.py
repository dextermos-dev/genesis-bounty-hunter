#!/usr/bin/env python3
"""
Daemon Autónomo de Publicación y Monitoreo (tools/auto_publisher_daemon.py)
"""

import time
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.live_monitor import run_monitoring_cycle
from dashboard.data_builder import update_dashboard_data_file

def run_daemon():
    print("[🚀] Daemon Autónomo de Publicación y Monitoreo Iniciado con Nuevo PAT.")
    while True:
        try:
            print("[🔍] Monitoreando estado de ramas, PRs y feedback en GitHub...")
            monitor_res = run_monitoring_cycle()
            update_dashboard_data_file()
        except Exception as e:
            print(f"[!] Error en ciclo de daemon: {e}")
        
        time.sleep(60)

if __name__ == "__main__":
    run_daemon()
