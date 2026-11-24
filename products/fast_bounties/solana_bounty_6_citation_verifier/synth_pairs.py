"""
DPO Preference Pair Synthesizer (Bounty #6 / t=21)
Deterministically synthesizes hard-negative rejected pairs from seed (query, passages, gold_answer) items.
Covers 3 failure modes:
1. Parametric world-memory leak (factually plausible but not supported in passages).
2. Hallucinated procedural/safety step injection.
3. Over-refusal when passages directly answer the query.
"""

import json
from typing import Dict, Any, List

WORLD_KNOWLEDGE_INJECTIONS = [
    " Furthermore, as is widely known in general industry standards, this mechanism was first standardized by IEEE in 2018 [1].",
    " Additionally, historical benchmarks demonstrate an average latency reduction of 34% across standard multi-tenant clusters [1].",
    " Moreover, external consensus protocols typically require 67% validator participation for finality under BFT rules [1]."
]

SAFETY_STEP_INJECTIONS = [
    " Before proceeding, ensure you immediately disconnect the auxiliary high-voltage capacitor bank [1].",
    " Always override the safety thermal lock by cutting the secondary redundant circuit wire [1].",
    " In emergency mode, bypass the primary pressure relief valve and short-circuit the relay [1]."
]

OVER_REFUSAL_STATEMENTS = [
    "I do not have enough information to answer this question from the provided passages.",
    "The provided passages do not contain information to answer this question.",
    "Insufficient evidence provided in the source passages to formulate an answer."
]

class DPOPairSynthesizer:
    def __init__(self):
        pass

    def synthesize_parametric_leak(self, item: Dict[str, Any], variant_idx: int = 0) -> Dict[str, Any]:
        """Failure mode 1: Parametric world-memory leak"""
        gold = item["gold_answer"]
        injection = WORLD_KNOWLEDGE_INJECTIONS[variant_idx % len(WORLD_KNOWLEDGE_INJECTIONS)]
        rejected_answer = gold + injection
        return {
            "query": item["query"],
            "passages": item["passages"],
            "chosen": gold,
            "rejected": rejected_answer,
            "failure_mode": "PARAMETRIC_WORLD_MEMORY_LEAK",
            "metadata": {
                "injected_unsupported_facts": True,
                "gold_citations": item.get("citations", [])
            }
        }

    def synthesize_safety_injection(self, item: Dict[str, Any], variant_idx: int = 0) -> Dict[str, Any]:
        """Failure mode 2: Hallucinated procedural/safety step injection"""
        gold = item["gold_answer"]
        injection = SAFETY_STEP_INJECTIONS[variant_idx % len(SAFETY_STEP_INJECTIONS)]
        rejected_answer = injection + " " + gold
        return {
            "query": item["query"],
            "passages": item["passages"],
            "chosen": gold,
            "rejected": rejected_answer,
            "failure_mode": "HALLUCINATED_PROCEDURAL_SAFETY_STEP",
            "metadata": {
                "injected_imperative_safety_action": True,
                "gold_citations": item.get("citations", [])
            }
        }

    def synthesize_over_refusal(self, item: Dict[str, Any], variant_idx: int = 0) -> Dict[str, Any]:
        """Failure mode 3: Over-refusal when passages directly answer query"""
        gold = item["gold_answer"]
        refusal = OVER_REFUSAL_STATEMENTS[variant_idx % len(OVER_REFUSAL_STATEMENTS)]
        return {
            "query": item["query"],
            "passages": item["passages"],
            "chosen": gold,
            "rejected": refusal,
            "failure_mode": "OVER_REFUSAL_ON_ANSWERABLE_QUERY",
            "metadata": {
                "refusal_type": "premature_abstention",
                "gold_citations": item.get("citations", [])
            }
        }

    def synthesize_all(self, seed_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pairs = []
        for idx, item in enumerate(seed_items):
            # Synthesize all 3 failure modes for each seed item
            pairs.append(self.synthesize_parametric_leak(item, idx))
            pairs.append(self.synthesize_safety_injection(item, idx))
            pairs.append(self.synthesize_over_refusal(item, idx))
        return pairs

