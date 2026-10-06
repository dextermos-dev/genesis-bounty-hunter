# 🚀 Tenstorrent TT-Metal Fix: Fused Scale-Mask Softmax Tile-Padding Leakage (Issue #58495)

**Bounty Target:** $750 USD | Tenstorrent Bounty Program  
**Issue Reference:** [tenstorrent/tt-metal#58495](https://github.com/tenstorrent/tt-metal/issues/58495)  
**Author:** `@dextermos` / `@dextermos-dev`  
**Settlement Wallet Address:** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`

---

## 🔍 Root Cause Analysis
When the logical width $W$ of an input tensor is not a multiple of 32 (the hardware tile width in TT-Metal architectures), the fused kernel previously applied the user-provided attention mask but omitted applying the implicit $-\infty$ tile-padding mask to tail columns $j \ge W$.

Consequently:
1. Padded elements participated in the denominator exponentiation: $\sum \exp(x_j)$.
2. Normalized probabilities leaked probability mass into invalid padding columns.
3. Row sums failed the normalization invariant: $\sum_{j=0}^{W-1} P_{i,j} < 1.0$, corrupting downstream multi-head attention weights.

---

## 🛠️ Implementation Strategy & Architecture
1. **Implicit Tail Masking:** Automatically clamp all columns $j \ge W$ to $-\infty$ ($-10^9$ in FP32) during the fused scale-mask dispatch.
2. **Numerically Stable Exponentiation:** Compute $\max(x_{\text{valid}})$ and evaluate $\exp(x_j - \max)$ such that padded columns strictly yield $\exp(-\infty) = 0.0$.
3. **Denominator Isolation:** Sum exponents strictly across valid logical elements $j < W$.

---

## 🧪 Verification & Test Suite
- Tested against arbitrary non-32 widths: $W \in \{1, 15, 17, 25, 31, 33, 50, 63, 100\}$.
- **Result:** **100% PASS** with $| \sum P_{i,j} - 1.0 | < 10^{-5}$.
- Source Reference: `products/tenstorrent_kernels/fused_softmax_padding_fix.py`
- Test Suite: `tests/test_tenstorrent_kernel_fixes.py`
