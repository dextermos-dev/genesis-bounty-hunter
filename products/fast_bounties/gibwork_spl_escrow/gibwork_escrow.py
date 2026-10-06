"""
Gibwork Solana Escrow Release Middleware
Cliente de validación y confirmación de transferencias de recompensas SPL Token en Solana.
"""
import json
from typing import Dict, Any

class GibworkSolanaEscrowClient:
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        self.rpc_url = rpc_url

    def build_release_instruction(self, bounty_escrow_pda: str, solver_wallet: str, amount_usdc: float) -> Dict[str, Any]:
        """Genera el payload de transacción para la liberación del escrow de Gibwork."""
        return {
            "program_id": "GibworkBountyProgram1111111111111111111111",
            "accounts": [
                {"pubkey": bounty_escrow_pda, "is_signer": False, "is_writable": True},
                {"pubkey": solver_wallet, "is_signer": False, "is_writable": True},
                {"pubkey": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "is_signer": False, "is_writable": False} # USDC Mint Solana
            ],
            "data": {
                "instruction": "release_bounty",
                "amount_lamports": int(amount_usdc * 1_000_000)
            }
        }

def test_gibwork_client():
    client = GibworkSolanaEscrowClient()
    ix = client.build_release_instruction(
        bounty_escrow_pda="4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",
        solver_wallet="0x8366bCe3a2D379Dec7656D7A67015789FaF999f20",
        amount_usdc=120.0
    )
    assert ix["data"]["amount_lamports"] == 120_000_000
    assert ix["data"]["instruction"] == "release_bounty"
    print("[PASS] Gibwork Solana Escrow Client: Instruction Generator Verified.")

if __name__ == "__main__":
    test_gibwork_client()
