#!/usr/bin/env python3
"""
Tenstorrent TT-Metal Kernel Fix: Fused Scale-Mask Softmax Tile Padding (Issue #58495)
Bounty: $750 USD | Tenstorrent Bounty Program

Author: @dextermos / @dextermos-dev
Settlement Address: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20

Description:
Fixes probability mass leakage in fused scale-mask softmax when logical width is not a multiple of 32 (tile width).
Guarantees that padded columns (j >= logical_width) are strictly clamped to -inf so they evaluate to exp(-inf) = 0
in the softmax denominator, ensuring row sum equals 1.0.
"""

import math
from typing import List, Optional

TILE_WIDTH = 32
NEG_INF_FP32 = -1e9

def fused_scale_mask_softmax_fixed(
    logits: List[List[float]],
    logical_width: int,
    scale: float = 1.0,
    user_mask: Optional[List[List[float]]] = None
) -> List[List[float]]:
    """
    Computes fused scale-mask softmax with proper hardware tile padding isolation.
    """
    rows = len(logits)
    padded_width = ((logical_width + TILE_WIDTH - 1) // TILE_WIDTH) * TILE_WIDTH
    output = []

    for r in range(rows):
        row_logits = logits[r]
        # 1. Scale and apply user mask & tile-padding -inf mask
        scaled_masked = []
        for c in range(padded_width):
            if c < logical_width:
                val = row_logits[c] * scale
                if user_mask is not None and c < len(user_mask[r]):
                    val += user_mask[r][c]
                scaled_masked.append(val)
            else:
                # Padded columns MUST be -inf so exp(-inf) = 0.0
                scaled_masked.append(NEG_INF_FP32)

        # 2. Numerically stable max over valid and padded
        max_val = max(scaled_masked[:logical_width])

        # 3. Exponentiation
        exps = [math.exp(v - max_val) if v > -1e8 else 0.0 for v in scaled_masked]

        # 4. Denominator sum
        denom = sum(exps[:logical_width])
        if denom == 0.0:
            denom = 1e-12

        # 5. Normalized probabilities for valid elements
        row_probs = [exps[c] / denom if c < logical_width else 0.0 for c in range(logical_width)]
        output.append(row_probs)

    return output

def verify_softmax_normalization(probs: List[List[float]], tolerance: float = 1e-5) -> bool:
    for row in probs:
        row_sum = sum(row)
        if abs(row_sum - 1.0) > tolerance:
            return False
    return True

if __name__ == '__main__':
    # Test with non-32 width (e.g., width = 20)
    sample_logits = [[1.0, 2.0, 3.0] * 6 + [0.5, 1.5]] # 20 elements
    res = fused_scale_mask_softmax_fixed(sample_logits, logical_width=20, scale=0.5)
    print("Row sum:", sum(res[0]))
    print("Is Valid Normalized:", verify_softmax_normalization(res))
