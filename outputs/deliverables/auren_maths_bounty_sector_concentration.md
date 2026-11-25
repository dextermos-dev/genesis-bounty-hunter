# 📐 AUREN Maths Bounty: Sector Exposure Inversion in `sector_exposure()` Corrupts Single-Sector Penalty and Falsely Penalizes Diversified Portfolios

- **Target Repository:** `Ayush441-python/AUREN`
- **Program:** AUREN Bug & Maths Bounty Program ($400 USDC Pool)
- **Category:** **Maths Bounty ($50 USDC)**
- **Author & Quant Researcher:** Dexter Mos ([`@dextermos`](https://github.com/dextermos))
- **Settlement Wallet (USDC on Base L2):** `0x8366bCe3a2D379De7656D7A67015789FaF999f20`
- **Tested Target Commit:** `HEAD` (`main`)

---

## 1. Executive Summary

In `engine/metrics.py`, `sector_exposure(w)` is defined to calculate portfolio sector concentration and drive the 15-point risk score penalty (`sector_max > 0.50`, "More than 50% sits in one sector"):

```python
# engine/metrics.py lines 6-8
def sector_exposure(w: pd.Series) -> pd.Series:
    """Weight per broad group (Big Tech, Crypto, ...)."""
    return w.groupby(w.index.map(lambda t: GROUPS.get(t, "Other"))).sum().sort_values(ascending=False)
```

However, `sector_exposure(w)` maps tickers using `GROUPS` (the broad thematic cluster like "Big Tech", "AI & Semiconductors") instead of `SECTORS` (the actual economic industry classification like "Semiconductors", "Software", "Consumer Technology").

This causes a severe mathematical failure in risk scoring with both **False Negatives** (dangerous risk masking) and **False Positives** (penalizing diversified portfolios):

1. **False Negative (Undiversified Portfolios Evade Risk Penalty):**
   A portfolio composed 100% of semiconductors (e.g., 50% `NVDA` + 50% `AMD`, or `AVGO` + `QCOM` + `TSM`) has **100% true exposure** to the single cyclical semiconductor sector. However, because `NVDA` is mapped to group `"Big Tech"` and `AMD` is mapped to group `"AI & Semiconductors"`, Auren reports only 50% exposure. The penalty `sector_max > 0.50` evaluates to `False`, allowing a single-sector portfolio to completely evade the 15-point risk penalty.

2. **False Positive (Well-Diversified Portfolios Falsely Penalized):**
   A portfolio holding 30% `NVDA` (Semiconductors), 25% `MSFT` (Software), 20% `AAPL` (Consumer Hardware), and 25% `AMZN` (E-Commerce & Cloud) is diversified across 4 distinct economic sectors, with no individual sector exceeding 30%. However, because all four tickers belong to the `"Big Tech"` group, Auren reports **100% in one sector** and hits the user with an erroneous 15-point risk penalty: `"100% sits in one sector"`.

---

## 2. Mathematical Proof & Detailed Root Cause

In `engine/universe.py`:
- `SECTORS` maps each ticker to its specific industry:
  ```python
  "NVDA": "Semiconductors",
  "AMD": "Semiconductors",
  "AVGO": "Semiconductors",
  "MSFT": "Software",
  "AAPL": "Consumer Technology",
  "AMZN": "E-Commerce & Cloud"
  ```
- `GROUPS` maps tickers to thematic baskets:
  ```python
  "NVDA": "Big Tech",
  "MSFT": "Big Tech",
  "AAPL": "Big Tech",
  "AMZN": "Big Tech",
  "AMD": "AI & Semiconductors"
  ```

In `engine/score.py`, the risk model specifies:
```python
RULE_TABLE = [
    ...
    (15, "More than 50% sits in one sector"),
]
...
(sector_max > 0.50, 15, f"{sector_max:.0%} sits in one sector"),
```

And in `api.py`:
```python
exposure = sector_exposure(w)
score, level, hits = risk_score(
    conc, vol, mdd, pairs, float(exposure.max()) if not exposure.empty else 0.0
)
```

Because `sector_exposure()` queries `GROUPS` rather than `SECTORS`:
$$\text{Exposure}_{\text{reported}}(g) = \sum_{i \in g} w_i \quad \text{where } g \in \text{GROUPS}$$
instead of the standard financial definition:
$$\text{Exposure}_{\text{true}}(s) = \sum_{i \in s} w_i \quad \text{where } s \in \text{SECTORS}$$

---

## 3. Step-by-Step Proof of Concept (PoC)

### Scenario A: 100% Semiconductor Portfolio Evades Risk Penalty (False Negative)

Portfolio: `{"NVDA": 0.50, "AMD": 0.50}`
- Both companies are semiconductor manufacturers (`SECTORS["NVDA"] == "Semiconductors"` and `SECTORS["AMD"] == "Semiconductors"`).
- **True Sector Exposure:** $\text{Semiconductors} = 50\% + 50\% = \mathbf{100\%}$.
- **Expected Penalty:** Since $100\% > 50\%$, the 15-point penalty must trigger.
- **Auren Calculation:**
  - `NVDA` mapped to `Big Tech` ($50\%$)
  - `AMD` mapped to `AI & Semiconductors` ($50\%$)
  - `sector_max` $= 0.50$.
  - Evaluation: `0.50 > 0.50` $\rightarrow$ **`False`**.
- **Impact:** Undiversified portfolio evades 15-point risk score penalty.

### Scenario B: Multi-Sector Diversified Portfolio Falsely Penalized (False Positive)

Portfolio: `{"NVDA": 0.30, "MSFT": 0.25, "AAPL": 0.20, "AMZN": 0.25}`
- **True Sector Exposure:**
  - Semiconductors: 30%
  - Software: 25%
  - Consumer Technology: 20%
  - E-Commerce & Cloud: 25%
  - Maximum sector exposure: $\mathbf{30\%} \le 50\%$.
- **Expected Penalty:** None (no single sector exceeds 50%).
- **Auren Calculation:**
  - All four tickers belong to `GROUPS["Big Tech"]`.
  - Reported exposure: `Big Tech: 100%`.
  - Evaluation: `1.00 > 0.50` $\rightarrow$ **`True`**.
- **Impact:** Portfolio is erroneously hit with 15 penalty points and message `"100% sits in one sector"`.

---

## 4. Reproducible Python Verification Script

```python
import pandas as pd
from engine.universe import SECTORS, GROUPS
from engine.metrics import sector_exposure
from engine.score import risk_score

# --- Test Case A: Undiversified Semiconductor Portfolio ---
w_chips = pd.Series({"NVDA": 0.50, "AMD": 0.50})
rep_chips = sector_exposure(w_chips)
true_chips = w_chips.groupby(w_chips.index.map(lambda t: SECTORS.get(t, "Other"))).sum()

print("--- Test Case A (NVDA 50%, AMD 50%) ---")
print("Reported by Auren:\n", rep_chips)
print("True Sector:\n", true_chips)
assert rep_chips.max() == 0.50, "Auren reports 50% max"
assert true_chips.max() == 1.00, "True sector is 100%"
print("Flaw Confirmed: 100% semiconductor portfolio triggers penalty?", rep_chips.max() > 0.50) # False!

# --- Test Case B: Multi-Sector Diversified Portfolio ---
w_div = pd.Series({"NVDA": 0.30, "MSFT": 0.25, "AAPL": 0.20, "AMZN": 0.25})
rep_div = sector_exposure(w_div)
true_div = w_div.groupby(w_div.index.map(lambda t: SECTORS.get(t, "Other"))).sum()

print("\n--- Test Case B (NVDA 30%, MSFT 25%, AAPL 20%, AMZN 25%) ---")
print("Reported by Auren:\n", rep_div)
print("True Sector:\n", true_div)
assert rep_div.max() == 1.00, "Auren reports 100% max"
assert true_div.max() == 0.30, "True sector is 30%"
print("Flaw Confirmed: Diversified portfolio erroneously penalized?", rep_div.max() > 0.50) # True!
```

---

## 5. Recommended Code Fix

In `engine/metrics.py`:

```diff
--- a/engine/metrics.py
+++ b/engine/metrics.py
@@ -1,8 +1,14 @@
 import numpy as np
 import pandas as pd
-from engine.universe import GROUPS
+from engine.universe import GROUPS, SECTORS
 
 
-def sector_exposure(w: pd.Series) -> pd.Series:
-    """Weight per broad group (Big Tech, Crypto, ...)."""
+def sector_exposure(w: pd.Series) -> pd.Series:
+    """Weight per economic industry/sector (Semiconductors, Software, etc.)."""
+    return w.groupby(w.index.map(lambda t: SECTORS.get(t, "Other"))).sum().sort_values(ascending=False)
+
+
+def group_exposure(w: pd.Series) -> pd.Series:
+    """Weight per broad group/thematic cluster (Big Tech, Crypto, ...)."""
     return w.groupby(w.index.map(lambda t: GROUPS.get(t, "Other"))).sum().sort_values(ascending=False)
```

In `engine/score.py` and `api.py`:
- Use `sector_exposure(w)` to check against `SECTORS` for the "50% in one sector" industry penalty.
- Optionally add a distinct rule for thematic group concentration using `group_exposure(w)`.

---

## 6. Settlement Details

- **Program:** AUREN Maths Bounty ($50 USDC)
- **Settlement Chain:** Base L2 (Chain ID: 8453)
- **Settlement Asset:** USDC (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`)
- **Recipient Address:** `0x8366bCe3a2D379De7656D7A67015789FaF999f20`
