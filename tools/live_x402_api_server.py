"""
Live RFC-x402 M2M Monetization Micro-Service API Server
Genesis Bounty Hunter AI - Route 3: Pay-Per-Request Micro-Settlements on Base L2
Settlement Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
"""

import json
import hashlib
import time
from typing import Dict, Any, Optional
from products.base_agent_gateway.base_agent_settler import BaseAgentGateway
from products.solana_anchor_guard.anchor_guard import AnchorGuardAuditor
from products.webacy_integration.webacy_agent_shield import WebacyAgentShield


class LiveX402MicroServiceServer:
    """
    Exposes Genesis AI Agent capabilities as paid RFC-x402 HTTP endpoints:
    1. /api/v1/audit/anchor -> $5.00 USDC per static AST audit
    2. /api/v1/shield/url   -> $0.50 USDC per malicious URL/drainer scan
    3. /api/v1/shield/threat-> $1.00 USDC per counterparty wallet threat check
    """

    OFFICIAL_SETTLEMENT_WALLET = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"

    ENDPOINT_PRICING = {
        "/api/v1/audit/anchor": 5.00,
        "/api/v1/shield/url": 0.50,
        "/api/v1/shield/threat": 1.00
    }

    def __init__(self):
        self.gateway = BaseAgentGateway()
        self.anchor_auditor = AnchorGuardAuditor()
        self.webacy_shield = WebacyAgentShield()
        self.total_revenue_collected = 0.0

    def handle_request(self, endpoint: str, payload: Dict[str, Any], auth_payment_header: Optional[str] = None) -> Dict[str, Any]:
        """
        Handles incoming HTTP/M2M request, enforcing RFC-x402 payment challenge if not prepaid.
        """
        if endpoint not in self.ENDPOINT_PRICING:
            return {"status": 404, "error": "Endpoint not found"}

        cost = self.ENDPOINT_PRICING[endpoint]

        # If no payment proof header provided, return HTTP 402 challenge
        if not auth_payment_header or not auth_payment_header.startswith("Base-x402 "):
            task_id = hashlib.sha256(f"{endpoint}:{time.time()}".encode()).hexdigest()[:12]
            quote = self.gateway.generate_x402_quote(task_id=task_id, cost_usdc=cost)
            return {
                "status": 402,
                "message": "Payment Required",
                "x402_quote": quote
            }

        # Payment proof provided -> Execute endpoint logic
        tx_hash = auth_payment_header.replace("Base-x402 ", "").strip()
        if len(tx_hash) != 66:
            return {"status": 400, "error": "Invalid Base L2 transaction proof hash"}

        self.total_revenue_collected += cost

        # Execute endpoint payload
        if endpoint == "/api/v1/audit/anchor":
            source_code = payload.get("source_code", "")
            result = self.anchor_auditor.audit_source_code(source_code)
        elif endpoint == "/api/v1/shield/url":
            url = payload.get("url", "")
            result = self.webacy_shield.evaluate_url_safety(url)
        elif endpoint == "/api/v1/shield/threat":
            address = payload.get("address", "")
            chain = payload.get("chain", "base")
            result = self.webacy_shield.evaluate_address_threat(address, chain=chain)
        else:
            result = {"status": "SUCCESS"}

        return {
            "status": 200,
            "data": result,
            "receipt": {
                "cost_usdc": cost,
                "network": "Base L2 (8453)",
                "beneficiary": self.OFFICIAL_SETTLEMENT_WALLET,
                "tx_proof": tx_hash,
                "timestamp": int(time.time())
            }
        }
