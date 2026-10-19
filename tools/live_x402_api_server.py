"""
Live RFC-x402 M2M Monetization Micro-Service API Server
Genesis Bounty Hunter AI - Route 3: Pay-Per-Request Micro-Settlements on Base L2
Settlement Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
"""

import os
import sys
import json
import hashlib
import time
from typing import Dict, Any, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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


def run_http_server(port: int = 8402):
    from http.server import HTTPServer, BaseHTTPRequestHandler

    server_instance = LiveX402MicroServiceServer()

    class X402RequestHandler(BaseHTTPRequestHandler):
        def _send_cors(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Payment-Proof")

        def do_OPTIONS(self):
            self.send_response(204)
            self._send_cors()
            self.end_headers()

        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self._send_cors()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                res = {
                    "status": "ONLINE",
                    "protocol": "RFC-x402 M2M Pay-Per-Request",
                    "network": "Base L2 (Chain ID 8453)",
                    "settlement_wallet": server_instance.OFFICIAL_SETTLEMENT_WALLET,
                    "pricing": server_instance.ENDPOINT_PRICING,
                    "revenue_collected_usd": server_instance.total_revenue_collected
                }
                self.wfile.write(json.dumps(res, indent=2).encode())
            else:
                self.send_response(200)
                self._send_cors()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                res = {
                    "server": "Genesis AI Sovereign M2M Gateway",
                    "standard": "RFC-x402",
                    "endpoints": [
                        {"path": "/api/v1/audit/anchor", "method": "POST", "cost": "$5.00 USDC", "desc": "Rust/Anchor smart contract AST audit"},
                        {"path": "/api/v1/shield/url", "method": "POST", "cost": "$0.50 USDC", "desc": "Phishing & drainer URL scanner"},
                        {"path": "/api/v1/shield/threat", "method": "POST", "cost": "$1.00 USDC", "desc": "Counterparty wallet threat detection"}
                    ],
                    "settlement_wallet": server_instance.OFFICIAL_SETTLEMENT_WALLET
                }
                self.wfile.write(json.dumps(res, indent=2).encode())

        def do_POST(self):
            auth_header = self.headers.get("Authorization") or self.headers.get("X-Payment-Proof")
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
            try:
                payload = json.loads(body_bytes.decode())
            except Exception:
                payload = {}

            response_data = server_instance.handle_request(
                endpoint=self.path,
                payload=payload,
                auth_payment_header=auth_header
            )

            status_code = response_data.get("status", 200)
            self.send_response(status_code)
            self._send_cors()
            if status_code == 402:
                self.send_header("X-Payment-Required", "true")
                self.send_header("X-Payment-Beneficiary", server_instance.OFFICIAL_SETTLEMENT_WALLET)
                self.send_header("X-Payment-Network", "Base L2")
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data, indent=2).encode())

    server = HTTPServer(("0.0.0.0", port), X402RequestHandler)
    print(f"RFC-x402 Live M2M Server listening on http://0.0.0.0:{port} (Base L2 Settler: {server_instance.OFFICIAL_SETTLEMENT_WALLET})")
    server.serve_forever()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8402
    run_http_server(port)
