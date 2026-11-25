#!/usr/bin/env python3
"""
Wallet Guardrail Sentinel (tools/wallet_guard.py)
Bounty Hunter AI - Cero Tolerancia a Errores de Wallet.

Audita exhaustivamente el repositorio, archivos preparados para commit o entregables
para garantizar que ninguna dirección de liquidación sufra mutaciones o erratas.
"""

import sys
import os
import re
from typing import List, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from constants.wallets import (
    BASE_SETTLEMENT_WALLET,
    SOLANA_SETTLEMENT_WALLET,
    METAMASK_GAS_WALLET,
    MUTATION_BLACK_LIST,
    scan_text_for_corrupt_wallets,
    validate_evm_address
)

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".idea",
    ".vscode",
    "scratch",
    ".gemini"
}

ALLOWED_EXTENSIONS = (
    ".py", ".md", ".json", ".yml", ".yaml", ".sol", ".ts", ".js", ".html", ".sh", ".bat", ".txt"
)


def audit_file(filepath: str) -> List[Tuple[int, str, str]]:
    """
    Audita un archivo línea por línea en busca de mutaciones o wallets corruptas.
    Retorna lista de (line_number, issue_description, line_content).
    """
    issues = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        return [(0, f"No se pudo leer el archivo: {e}", "")]

    for idx, line in enumerate(lines, 1):
        # Permitir claves explícitas de acortamiento visual en UI (ej. 'shortAddr')
        if "shortAddr" in line:
            continue

        # 1. Chequeo de lista negra de mutaciones explícitas
        for bad in MUTATION_BLACK_LIST:
            if bad in line:
                issues.append((idx, f"Contiene wallet corrupta prohibida: {bad}", line.strip()))

        # 2. Chequeo de variantes de 0x8366b...
        corrupt_variants = scan_text_for_corrupt_wallets(line)
        for variant in corrupt_variants:
            issues.append((idx, f"Variante mutada detectada ('{variant}'). Debe ser '{BASE_SETTLEMENT_WALLET}'", line.strip()))

    return issues


def audit_repository(root_dir: str = ".") -> int:
    """
    Audita todo el repositorio. Retorna número total de infracciones.
    """
    print(f"[*] Iniciando Auditoría WalletGuard en: {os.path.abspath(root_dir)}")
    print(f"[*] Wallet Canónica Base L2: {BASE_SETTLEMENT_WALLET}")
    print(f"[*] Wallet Canónica Solana:  {SOLANA_SETTLEMENT_WALLET}")
    print(f"[*] Wallet Canónica BSC/Gas: {METAMASK_GAS_WALLET}")

    total_files = 0
    total_issues = 0

    for root, dirs, files in os.walk(root_dir):
        # Excluir directorios ignorados
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if not file.endswith(ALLOWED_EXTENSIONS):
                continue

            filepath = os.path.join(root, file)
            # No auditar este mismo archivo si define la lista negra
            relpath = os.path.relpath(filepath, root_dir)
            if relpath in ("tools/wallet_guard.py", "constants/wallets.py", "tests/test_wallet_guard_invariants.py"):
                continue

            total_files += 1
            issues = audit_file(filepath)
            if issues:
                print(f"\n[❌ ALERTA ROJA] Fallo de integridad de wallet en: {relpath}")
                for line_no, desc, snippet in issues:
                    print(f"   Línea {line_no}: {desc}")
                    print(f"   Fragmento: {snippet[:120]}")
                total_issues += len(issues)

    print("\n" + "=" * 60)
    print(f"[*] Auditoría finalizada: {total_files} archivos inspeccionados.")
    if total_issues == 0:
        print("[✔] 100% LIMPIO: Cero mutaciones de wallet detectadas en el repositorio.")
        return 0
    else:
        print(f"[CRÍTICO] Se encontraron {total_issues} violaciones a la invariante de wallet.")
        return 1


if __name__ == "__main__":
    exit_code = audit_repository(".")
    sys.exit(exit_code)
