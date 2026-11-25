"""
Autonomous RFC-x402 M2M Client for Base L2 Services
Enables AI agents to query paid endpoints with automatic HTTP 402 negotiation.
Settlement Wallet: 0x8366bCe3a2D379De7656D7A67015789FaF999f20
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional


class X402ServiceClient:
    """
    Client for consuming RFC-x402 pay-per-request microservices on Base L2.
    """

    DEFAULT_BASE_URL = "http://127.0.0.1:8402"
    SETTLEMENT_WALLET = "0x8366bCe3a2D379De7656D7A67015789FaF999f20"
    BASE_USDC_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def request_service(self, endpoint: str, payload: Dict[str, Any], tx_proof: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes a POST request to an RFC-x402 endpoint.
        If tx_proof is omitted, receives the 402 Payment Challenge with exact settlement terms.
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        if tx_proof:
            headers["Authorization"] = f"Base-x402 {tx_proof}"

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers)

        try:
            with urllib.request.urlopen(req) as resp:
                return {
                    "status": resp.status,
                    "data": json.loads(resp.read().decode("utf-8")),
                    "is_paid": True
                }
        except urllib.error.HTTPError as e:
            if e.code == 402:
                body = json.loads(e.read().decode("utf-8"))
                return {
                    "status": 402,
                    "is_paid": False,
                    "challenge": body,
                    "quote": body.get("x402_quote", {}),
                    "required_payment": {
                        "amount_usdc": body.get("x402_quote", {}).get("cost_usdc"),
                        "recipient": self.SETTLEMENT_WALLET,
                        "asset": self.BASE_USDC_CONTRACT,
                        "network": "Base L2 (EIP-155:8453)"
                    }
                }
            raise
