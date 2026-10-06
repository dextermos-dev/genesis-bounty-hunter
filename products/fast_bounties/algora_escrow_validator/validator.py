"""
Algora Escrow & Webhook Signature Validator
Módulo seguro de verificación criptográfica de eventos y release de bounties.
"""
import hmac
import hashlib
import time
import json
from typing import Dict, Any, Tuple

class AlgoraWebhookValidator:
    def __init__(self, secret_key: str, max_drift_seconds: int = 300):
        self.secret_key = secret_key.encode('utf-8')
        self.max_drift_seconds = max_drift_seconds
        self.processed_nonces = set()

    def verify_signature(self, payload: bytes, signature_header: str, timestamp_header: str, nonce: str) -> Tuple[bool, str]:
        if not signature_header or not timestamp_header:
            return False, "Missing signature or timestamp headers"

        try:
            ts = int(timestamp_header)
        except ValueError:
            return False, "Invalid timestamp format"

        now = int(time.time())
        if abs(now - ts) > self.max_drift_seconds:
            return False, f"Timestamp drift exceeds {self.max_drift_seconds}s limit"

        if nonce in self.processed_nonces:
            return False, "Replay attack detected: Nonce already used"

        msg = f"{ts}.{nonce}.".encode('utf-8') + payload
        expected_sig = hmac.new(self.secret_key, msg, hashlib.sha256).hexdigest()

        if hmac.compare_digest(expected_sig, signature_header):
            self.processed_nonces.add(nonce)
            if len(self.processed_nonces) > 50000:
                self.processed_nonces.clear()
            return True, "Valid signature"
        return False, "Signature mismatch"

def test_algora_validator():
    secret = "secret_key_12345"
    validator = AlgoraWebhookValidator(secret)
    payload = json.dumps({"event": "pull_request.merged", "bounty_id": "algora_1", "payout_amount": 150.0, "wallet": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"}).encode('utf-8')
    ts = str(int(time.time()))
    nonce = "nonce_xyz_001"
    
    # Compute signature
    msg = f"{ts}.{nonce}.".encode('utf-8') + payload
    sig = hmac.new(secret.encode('utf-8'), msg, hashlib.sha256).hexdigest()
    
    valid, msg_res = validator.verify_signature(payload, sig, ts, nonce)
    assert valid, f"Verification failed: {msg_res}"
    print("[PASS] Algora Webhook Validator: Valid Signature Verified.")
    
    # Replay test
    replay_valid, replay_msg = validator.verify_signature(payload, sig, ts, nonce)
    assert not replay_valid and "Replay" in replay_msg
    print("[PASS] Algora Webhook Validator: Replay Attack Successfully Blocked.")

if __name__ == "__main__":
    test_algora_validator()
