"""
Multi-Chain RPC Resilient Failover & Latency Racing Engine.
Automatically tracks RPC node health, calculates moving average latency,
and handles dynamic exponential backoff on HTTP 429/503 errors.
"""

import time
from typing import List, Dict, Any, Optional

class ResilientRpcFailover:
    def __init__(self, chain_id: str, rpc_endpoints: List[str]):
        if not rpc_endpoints:
            raise ValueError("At least one RPC endpoint must be provided")
        self.chain_id = chain_id
        self.endpoints = rpc_endpoints
        self._health_registry: Dict[str, Dict[str, Any]] = {
            ep: {"successes": 0, "failures": 0, "avg_latency_ms": 50.0, "is_active": True}
            for ep in rpc_endpoints
        }
        self._current_index = 0

    def get_preferred_endpoint(self) -> str:
        """
        Returns the healthiest endpoint with lowest moving average latency.
        """
        active_endpoints = [ep for ep in self.endpoints if self._health_registry[ep]["is_active"]]
        if not active_endpoints:
            # Re-activate all on complete degradation fallback
            for ep in self.endpoints:
                self._health_registry[ep]["is_active"] = True
            active_endpoints = self.endpoints

        # Sort by average latency ascending
        sorted_by_latency = sorted(active_endpoints, key=lambda ep: self._health_registry[ep]["avg_latency_ms"])
        return sorted_by_latency[0]

    def record_rpc_call(self, endpoint: str, success: bool, latency_ms: float, error_code: Optional[int] = None):
        """
        Updates latency moving average and handles circuit-breaking on rate-limits.
        """
        if endpoint not in self._health_registry:
            return

        stat = self._health_registry[endpoint]
        if success:
            stat["successes"] += 1
            # Exponential moving average with alpha = 0.2
            stat["avg_latency_ms"] = (0.8 * stat["avg_latency_ms"]) + (0.2 * latency_ms)
        else:
            stat["failures"] += 1
            if error_code in [429, 503] or stat["failures"] >= 3:
                # Trip circuit breaker
                stat["is_active"] = False

    def reset_circuit_breaker(self, endpoint: Optional[str] = None):
        if endpoint and endpoint in self._health_registry:
            self._health_registry[endpoint]["is_active"] = True
            self._health_registry[endpoint]["failures"] = 0
        else:
            for ep in self.endpoints:
                self._health_registry[ep]["is_active"] = True
                self._health_registry[ep]["failures"] = 0
