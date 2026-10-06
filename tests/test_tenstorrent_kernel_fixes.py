#!/usr/bin/env python3
"""
Unit test suite for Tenstorrent TT-Metal Kernel Fixes (Issues #58495 & #58986)
Author: @dextermos / @dextermos-dev
Settlement Address: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
"""

import unittest
import math
from products.tenstorrent_kernels.fused_softmax_padding_fix import (
    fused_scale_mask_softmax_fixed,
    verify_softmax_normalization
)
from products.tenstorrent_kernels.cumsum_infinity_guard import (
    cumsum_fp32_compensated_safe
)

class TestTenstorrentKernelFixes(unittest.TestCase):
    def test_softmax_non32_width_normalization(self):
        # Test odd/non-32 widths: 1, 15, 17, 31, 33, 50, 63, 100
        for width in [1, 15, 17, 31, 33, 50, 63, 100]:
            logits = [[float(i % 10) for i in range(width)]]
            probs = fused_scale_mask_softmax_fixed(logits, logical_width=width, scale=1.0)
            self.assertEqual(len(probs[0]), width)
            self.assertTrue(
                verify_softmax_normalization(probs, tolerance=1e-5),
                f"Softmax normalization failed for width {width}"
            )

    def test_softmax_with_causal_mask(self):
        width = 25
        logits = [[float(i) for i in range(width)]]
        mask = [[0.0 if j <= i else -1e9 for j in range(width)] for i in range(1)]
        probs = fused_scale_mask_softmax_fixed(logits, logical_width=width, scale=0.5, user_mask=mask)
        self.assertTrue(verify_softmax_normalization(probs, tolerance=1e-5))

    def test_cumsum_infinity_no_nan_poisoning(self):
        arr = [1.0, 2.0, float('inf'), 4.0, 5.0]
        res = cumsum_fp32_compensated_safe(arr)
        self.assertEqual(res[0], 1.0)
        self.assertEqual(res[1], 3.0)
        self.assertEqual(res[2], float('inf'))
        self.assertEqual(res[3], float('inf'))
        self.assertEqual(res[4], float('inf'))
        self.assertFalse(any(math.isnan(x) for x in res))

    def test_cumsum_negative_infinity_preservation(self):
        arr = [10.0, float('-inf'), 5.0, 10.0]
        res = cumsum_fp32_compensated_safe(arr)
        self.assertEqual(res[1], float('-inf'))
        self.assertEqual(res[2], float('-inf'))
        self.assertEqual(res[3], float('-inf'))
        self.assertFalse(any(math.isnan(x) for x in res))

if __name__ == '__main__':
    unittest.main()
