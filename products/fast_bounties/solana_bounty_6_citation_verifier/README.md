# Grounded Passage Citation Verifier & Abstention DPO Pair Synthesizer
**Zero-Gas Solana Agent Bounty (`0.10 SOL` · Issue #6 · `t=21`)**

- **Vault / Escrow (Solana Mainnet):** `6cXR7EkUHAn4VWjEkS4ywnxu7m5zZ26EsVaRLixnpvXN`
- **Settlement Wallet (Solana):** `GLKpgANMTt8tJpTDVuzqi3ESuYivrgciKvwqSX5Hvb7K`
- **Whiteboard Delivery:** `https://stellarator.site/yard/w/sub-dextermos-t21`

---

### Clean-Room Architecture
1. **`verifier.py` (4 Deterministic Hard Gates):**
   - **Gate 1:** Citation index validity (`[1]..[k]`) and strict lexical/span grounding overlap against supporting segments.
   - **Gate 2:** High-stakes procedural safety action gate (`SAFETY_PROCEDURAL_LEXICON`). Any imperative safety verb absent from the cited passage segments deterministically forces score to `0.0`.
   - **Gate 3:** Calibrated abstention detection on unanswerable perturbations, refusing partial speculation while rejecting over-refusal on answerable queries.
   - **Gate 4:** Strict word budget enforcement (`<= 120` words).
2. **`synth_pairs.py` (DPO Pair Synthesizer):**
   - Generates hard-negative rejected pairs across 3 failure modes:
     * Mode 1: Parametric world-memory leak (plausible outside facts absent from passages).
     * Mode 2: Hallucinated procedural/safety step injection.
     * Mode 3: Over-refusal on answerable queries.
3. **`test_citation_verifier.py` (32 Adversarial Fixtures):**
   - 100% offline, zero external dependencies, 32/32 tests passing.

