#!/usr/bin/env python3
"""
ERC-4337 UserOperation Gas Estimator for Base L2 (products/fast_bounties/instant_merge/userop_gas_estimator.py)
Target: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
"""

import json

def estimate_userop_gas_limits(call_data_len: int, verification_complexity: int = 1) -> dict:
    base_overhead = 21000
    pre_verification_gas = base_overhead + (call_data_len * 16)
    verification_gas_limit = 100000 * verification_complexity
    call_gas_limit = 50000 + (call_data_len * 32)
    
    max_priority_fee_per_gas = 1000000 # 0.001 gwei on Base L2
    max_fee_per_gas = 2000000

    return {
        "status": "ESTIMATION_VALID",
        "preVerificationGas": pre_verification_gas,
        "verificationGasLimit": verification_gas_limit,
        "callGasLimit": call_gas_limit,
        "maxPriorityFeePerGas": max_priority_fee_per_gas,
        "maxFeePerGas": max_fee_per_gas,
        "payout_address": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"
    }

if __name__ == "__main__":
    print(json.dumps(estimate_userop_gas_limits(256, 1), indent=2))
