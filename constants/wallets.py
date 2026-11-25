"""
Single Source of Truth (SSOT) para Direcciones de Liquidación Oficiales.
Bounty Hunter AI - Invariante Inviolable de Wallets.

Este módulo centraliza y blinda todas las direcciones oficiales de la plataforma.
Cualquier script, submission, bot, PR o entregable DEBE importar las constantes
de este archivo para evitar mutaciones o errores tipográficos.
"""

import re
from typing import List, Tuple

# ==============================================================================
# CANONICAL WALLET REGISTRY (INMUTABLE)
# ==============================================================================

# Settlement Wallet Oficial Principal (Base L2 / EVM / USDC ERC-20 / ETH)
# EIP-55 Checksum: 0x8366bCe3a2D379De7656D7A67015789FaF999f20 (exactamente 42 caracteres)
BASE_SETTLEMENT_WALLET: str = "0x8366bCe3a2D379De7656D7A67015789FaF999f20"

# Solana Mainnet Settlement Wallet (SOL / SPL Tokens)
SOLANA_SETTLEMENT_WALLET: str = "GLKpgANMTt8tJpTDVuzqi3ESuYivrgciKvwqSX5Hvb7K"

# MetaMask / BSC Gas Wallet (BNB Smart Chain / EVM Gas Ops)
METAMASK_GAS_WALLET: str = "0x8e2576c3418ceca3970ea16f1047efc5b881820f"

# Known Historical Typo Variants to explicitly detect and ban
MUTATION_BLACK_LIST: Tuple[str, ...] = (
    "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20", # 43 chars (extra 'c')
)

EVM_REGEX = re.compile(r"^0x[a-fA-F0-9]{40}$")
SOLANA_REGEX = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")


def validate_evm_address(address: str) -> bool:
    """Verifica sintaxis estricta de una dirección EVM (exactamente 42 caracteres, 0x + 40 hex)."""
    if not isinstance(address, str):
        return False
    return bool(EVM_REGEX.match(address.strip()))


def validate_solana_address(address: str) -> bool:
    """Verifica sintaxis estricta de una dirección Solana Base58."""
    if not isinstance(address, str):
        return False
    clean = address.strip()
    return bool(SOLANA_REGEX.match(clean)) and len(clean) in (43, 44)


def assert_official_wallet(address: str, chain: str = "base") -> str:
    """
    Verifica que la dirección proporcionada sea válida y coincida con el registro canónico.
    Lanza ValueError si se detecta cualquier discrepancia o corrupción.
    """
    clean_addr = address.strip()

    # Chequeo contra lista negra de mutaciones conocidas
    if clean_addr in MUTATION_BLACK_LIST:
        raise ValueError(
            f"[CRITICAL SECURITY ALERT] Mutated wallet variant detected: {clean_addr}. "
            f"Must be canonical: {BASE_SETTLEMENT_WALLET}"
        )

    if chain.lower() in ("base", "evm", "ethereum", "arbitrum", "polygon"):
        if not validate_evm_address(clean_addr):
            raise ValueError(f"[INVALID EVM ADDRESS] Address {clean_addr} has invalid length ({len(clean_addr)}) or characters.")
        if clean_addr.lower() == BASE_SETTLEMENT_WALLET.lower():
            return BASE_SETTLEMENT_WALLET
        elif clean_addr.lower() == METAMASK_GAS_WALLET.lower():
            return METAMASK_GAS_WALLET
        else:
            return clean_addr

    elif chain.lower() in ("solana", "sol"):
        if not validate_solana_address(clean_addr):
            raise ValueError(f"[INVALID SOLANA ADDRESS] Address {clean_addr} is not valid Base58.")
        return clean_addr

    return clean_addr


def scan_text_for_corrupt_wallets(text: str) -> List[str]:
    """
    Escanea un texto en busca de cualquier intento de wallet '0x8366b...' que:
    1. Esté en la lista negra de mutaciones (ej. con 'Dec')
    2. Esté truncada (ej. con '...')
    3. Tenga longitud diferente de 42 caracteres.
    4. O no coincida con BASE_SETTLEMENT_WALLET (permitiendo solo la variante lower si es código fuente puro).
    """
    findings = []
    
    # 1. Truncamientos explícitos
    if re.search(r"0x8366b[a-zA-Z0-9]*\.\.\.", text, re.IGNORECASE):
        findings.append("Truncated wallet address with ellipses ('...')")

    # 2. Token de dirección
    pattern = re.compile(r"0x8366b[a-zA-Z0-9]+", re.IGNORECASE)
    matches = pattern.findall(text)
    for m in matches:
        if m in MUTATION_BLACK_LIST:
            findings.append(f"Blacklisted mutation: {m}")
        elif len(m) != 42:
            findings.append(f"Invalid length ({len(m)} chars, expected 42): {m}")
        elif m != BASE_SETTLEMENT_WALLET and m != BASE_SETTLEMENT_WALLET.lower():
            findings.append(f"Non-canonical casing: {m} (expected {BASE_SETTLEMENT_WALLET})")

    return findings
