"""
Constants Package for Bounty Hunter AI
"""

from constants.wallets import (
    BASE_SETTLEMENT_WALLET,
    SOLANA_SETTLEMENT_WALLET,
    METAMASK_GAS_WALLET,
    validate_evm_address,
    validate_solana_address,
    assert_official_wallet,
    scan_text_for_corrupt_wallets
)

__all__ = [
    "BASE_SETTLEMENT_WALLET",
    "SOLANA_SETTLEMENT_WALLET",
    "METAMASK_GAS_WALLET",
    "validate_evm_address",
    "validate_solana_address",
    "assert_official_wallet",
    "scan_text_for_corrupt_wallets"
]
