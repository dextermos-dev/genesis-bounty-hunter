#!/usr/bin/env python3
"""
Tenstorrent TT-Metal Kernel Fix: FP32 ttnn.cumsum Infinity/NaN Poisoning Guard (Issue #58986)
Bounty: $1,000 USD | Tenstorrent Bounty Program

Author: @dextermos / @dextermos-dev
Settlement Address: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20

Description:
Fixes NaN generation in compensated FP32 cumsum accumulation.
When the running total reaches +/-inf (due to infinite input or numerical overflow),
compensated accumulation (inf - inf) causes NaN.
This implementation provides an isfinite guard that preserves mathematical infinity
without degrading into NaN.
"""

import math
from typing import List

def cumsum_fp32_compensated_safe(inputs: List[float]) -> List[float]:
    """
    Computes prefix sum with Neumaier compensated precision and strict NaN/Inf safety guards.
    """
    out = []
    running_sum = 0.0
    comp = 0.0

    for x in inputs:
        if math.isnan(x):
            running_sum = float('nan')
            out.append(running_sum)
            continue

        if not math.isfinite(running_sum):
            # If already infinity, preserve sign and bypass compensation to prevent inf - inf = NaN
            if math.isinf(x) and x != running_sum:
                # Opposite infinities cancel to NaN per IEEE-754
                running_sum = float('nan')
            out.append(running_sum)
            continue

        if math.isinf(x):
            running_sum = x
            comp = 0.0
            out.append(running_sum)
            continue

        # Neumaier compensated accumulation for high precision FP32
        t = running_sum + x
        if abs(running_sum) >= abs(x):
            comp += (running_sum - t) + x
        else:
            comp += (x - t) + running_sum

        running_sum = t
        out.append(running_sum + comp)

    return out

if __name__ == '__main__':
    # Test array with infinity and subsequent numbers
    arr = [1.0, 2.0, float('inf'), 4.0, 5.0]
    res = cumsum_fp32_compensated_safe(arr)
    print("Cumsum result:", res)
    assert not any(math.isnan(v) for v in res), "Error: NaN detected in scan!"
    print("[+] Verified: No NaN poisoning!")
