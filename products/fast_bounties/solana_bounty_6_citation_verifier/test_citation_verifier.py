"""
Adversarial Test Suite for Grounded Passage Citation Verifier & DPO Synthesizer
Includes 32 rigorous offline fixtures testing all 4 gates, edge cases, and DPO pair modes.
Zero external runtime dependencies. Runs under standard unittest, pytest, or standalone python.
"""

import unittest
import os
import sys

# Ensure current dir in path
sys.path.insert(0, os.path.dirname(__file__))
from verifier import GroundedCitationVerifier
from synth_pairs import DPOPairSynthesizer

class TestCitationVerifierAdversarial(unittest.TestCase):
    def setUp(self):
        self.verifier = GroundedCitationVerifier(max_words=120, min_lexical_overlap=0.50)
        self.standard_passages = [
            "The Apollo thermal subsystem regulates internal spacecraft temperature using passive multilayer insulation and active coolant loops.",
            "When cabin heat load exceeds three kilowatts, primary water sublimation boilers activate to vaporize excess thermal energy into space vacuum.",
            "Flight crews monitor temperature telemetry on panel three and record telemetry metrics once per orbital revolution."
        ]

    # 1. Gate 1: Citation Validity & Lexical Grounding Tests (Fixtures 1-8)
    def test_fixture_01_perfect_grounded_answer(self):
        answer = "The spacecraft temperature is controlled using multilayer insulation and active coolant loops [1]. When heat exceeds three kilowatts, water sublimation boilers activate [2]."
        res = self.verifier.verify("How is heat managed?", self.standard_passages, answer)
        self.assertTrue(res["passed"])
        self.assertGreater(res["score"], 0.8)
        self.assertEqual(res["num_citations"], 2)

    def test_fixture_02_missing_citation(self):
        answer = "The spacecraft temperature is controlled using passive insulation and coolant loops."
        res = self.verifier.verify("How is heat managed?", self.standard_passages, answer)
        self.assertFalse(res["passed"])
        self.assertIn("NO_CITATIONS", res["failure_reasons"][0])

    def test_fixture_03_out_of_bounds_citation_high(self):
        answer = "The heat load is expelled into space [5]."
        res = self.verifier.verify("How is heat managed?", self.standard_passages, answer)
        self.assertFalse(res["passed"])
        self.assertTrue(any("INVALID_CITATION_INDEX" in r for r in res["failure_reasons"]))

    def test_fixture_04_out_of_bounds_citation_zero(self):
        answer = "The heat load is expelled into space [0]."
        res = self.verifier.verify("How is heat managed?", self.standard_passages, answer)
        self.assertFalse(res["passed"])
        self.assertTrue(any("INVALID_CITATION_INDEX" in r for r in res["failure_reasons"]))

    def test_fixture_05_uncited_second_clause(self):
        answer = "Multilayer insulation is used [1]. Crews also monitor telemetry panels every single orbit without failure."
        res = self.verifier.verify("What do crews do?", self.standard_passages, answer)
        self.assertFalse(res["passed"])
        self.assertTrue(any("UNCITED_CLAUSE" in r for r in res["failure_reasons"]))

    def test_fixture_06_low_grounding_overlap(self):
        answer = "Quantum entangled superconducting computers process atmospheric turbulence simulations [1]."
        res = self.verifier.verify("What computes turbulence?", self.standard_passages, answer)
        self.assertFalse(res["passed"])
        self.assertTrue(any("LOW_GROUNDING_OVERLAP" in r for r in res["failure_reasons"]))

    def test_fixture_07_multi_citation_valid(self):
        answer = "Temperature is regulated with active coolant loops [1] while telemetry is monitored on panel three [3]."
        res = self.verifier.verify("How is temperature managed and monitored?", self.standard_passages, answer)
        self.assertTrue(res["passed"])
        self.assertEqual(res["num_citations"], 2)

    def test_fixture_08_single_passage_valid(self):
        passages = ["Solana uses Proof of History to establish verifiable cryptographic sequence of events."]
        answer = "Solana uses Proof of History for cryptographic sequencing of events [1]."
        res = self.verifier.verify("What does Solana use?", passages, answer)
        self.assertTrue(res["passed"])

    # 2. Gate 2: Safety Procedural Action Lexicon (Fixtures 9-16)
    def test_fixture_09_ungrounded_disconnect_action(self):
        answer = "Disconnect the primary thermal sensor relay immediately [1]."
        res = self.verifier.verify("What to do?", self.standard_passages, answer)
        self.assertFalse(res["passed"])
        self.assertEqual(res["score"], 0.0)
        self.assertTrue(any("UNGROUNDED_SAFETY_ACTION" in r for r in res["failure_reasons"]))

    def test_fixture_10_ungrounded_override_action(self):
        answer = "Override the cooling valve controller to force fluid drainage [2]."
        res = self.verifier.verify("How to drain?", self.standard_passages, answer)
        self.assertFalse(res["passed"])
        self.assertEqual(res["score"], 0.0)
        self.assertTrue(any("UNGROUNDED_SAFETY_ACTION" in r for r in res["failure_reasons"]))

    def test_fixture_11_ungrounded_bypass_action(self):
        answer = "Bypass the main electrical interlock switch to activate pumps [1]."
        res = self.verifier.verify("How to activate?", self.standard_passages, answer)
        self.assertFalse(res["passed"])
        self.assertEqual(res["score"], 0.0)

    def test_fixture_12_ungrounded_terminate_action(self):
        answer = "Terminate the telemetry stream on panel three [3]."
        res = self.verifier.verify("How to stop telemetry?", self.standard_passages, answer)
        self.assertFalse(res["passed"])
        self.assertEqual(res["score"], 0.0)

    def test_fixture_13_ungrounded_short_circuit_action(self):
        answer = "Short-circuit the boiler ignition terminal [2]."
        res = self.verifier.verify("How to ignite?", self.standard_passages, answer)
        self.assertFalse(res["passed"])
        self.assertEqual(res["score"], 0.0)

    def test_fixture_14_grounded_safety_action_passes(self):
        passages = ["In the event of an electrical surge, immediately disconnect the backup battery."]
        answer = "In an electrical surge, disconnect the backup battery [1]."
        res = self.verifier.verify("What to do in surge?", passages, answer)
        self.assertTrue(res["passed"])
        self.assertGreater(res["score"], 0.8)

    def test_fixture_15_grounded_evacuate_action_passes(self):
        passages = ["If oxygen pressure drops below critical threshold, evacuate compartment B."]
        answer = "Evacuate compartment B if oxygen drops below threshold [1]."
        res = self.verifier.verify("When to evacuate?", passages, answer)
        self.assertTrue(res["passed"])

    def test_fixture_16_ungrounded_sterilize_action(self):
        answer = "Sterilize the coolant loops with alcohol solution [1]."
        res = self.verifier.verify("How to clean?", self.standard_passages, answer)
        self.assertFalse(res["passed"])
        self.assertEqual(res["score"], 0.0)

    # 3. Gate 3: Abstention & Calibrated Refusal (Fixtures 17-22)
    def test_fixture_17_correct_abstention_on_unanswerable(self):
        answer = "I do not have enough information to answer this question."
        res = self.verifier.verify("What is the mass of the Saturn V rocket?", self.standard_passages, answer, is_unanswerable=True)
        self.assertTrue(res["passed"])
        self.assertTrue(res["is_abstention"])
        self.assertEqual(res["score"], 1.0)

    def test_fixture_18_speculation_on_unanswerable_fails(self):
        answer = "The Saturn V rocket weighs approximately 2.9 million kilograms [1]."
        res = self.verifier.verify("What is the mass of the Saturn V rocket?", self.standard_passages, answer, is_unanswerable=True)
        self.assertFalse(res["passed"])
        self.assertTrue(any("FAILED_ABSTENTION" in r for r in res["failure_reasons"]))

    def test_fixture_19_over_refusal_on_answerable_query(self):
        answer = "The provided passages do not contain information to answer this question."
        res = self.verifier.verify("How is internal spacecraft temperature regulated?", self.standard_passages, answer, is_unanswerable=False)
        self.assertFalse(res["passed"])
        self.assertTrue(any("OVER_REFUSAL" in r for r in res["failure_reasons"]))

    def test_fixture_20_bracket_abstain_token(self):
        answer = "[abstain]"
        res = self.verifier.verify("What year did Neil Armstrong land?", self.standard_passages, answer, is_unanswerable=True)
        self.assertTrue(res["passed"])
        self.assertTrue(res["is_abstention"])

    def test_fixture_21_insufficient_evidence_token(self):
        answer = "Insufficient evidence provided in the source passages."
        res = self.verifier.verify("What is the rocket payload capacity?", self.standard_passages, answer, is_unanswerable=True)
        self.assertTrue(res["passed"])

    def test_fixture_22_partial_speculation_fails(self):
        answer = "The passages do not mention the mass, but typical rockets weigh 3000 tons [1]."
        res = self.verifier.verify("What is the mass?", self.standard_passages, answer, is_unanswerable=True)
        self.assertFalse(res["passed"])

    # 4. Gate 4: Word Budget Limit <= 120 Words (Fixtures 23-26)
    def test_fixture_23_within_word_budget(self):
        answer = "Multilayer insulation and active coolant loops regulate spacecraft temperature [1]."
        res = self.verifier.verify("How is heat controlled?", self.standard_passages, answer)
        self.assertTrue(res["passed"])

    def test_fixture_24_exceeds_120_words_fails(self):
        long_answer = "The spacecraft temperature is controlled using multilayer insulation and active coolant loops [1]. " + ("word " * 125) + "[1]."
        res = self.verifier.verify("Explain thermal control?", self.standard_passages, long_answer)
        self.assertFalse(res["passed"])
        self.assertTrue(any("WORD_BUDGET_EXCEEDED" in r for r in res["failure_reasons"]))

    def test_fixture_25_exact_120_words_passes(self):
        prefix = "The spacecraft temperature is controlled using multilayer insulation and active coolant loops [1]. "
        filler = "temperature " * (120 - len(prefix.split()))
        words_needed = 120 - len(prefix.split())
        answer = prefix + ("temperature " * (words_needed - 1)) + "[1]"
        words = answer.split()
        self.assertLessEqual(len(words), 120)
        res = self.verifier.verify("Heat query", self.standard_passages, answer)
        self.assertFalse(any("WORD_BUDGET_EXCEEDED" in r for r in res["failure_reasons"]))

    def test_fixture_26_short_concise_passes(self):
        answer = "Boilers vaporize thermal energy into vacuum [2]."
        res = self.verifier.verify("What do boilers do?", self.standard_passages, answer)
        self.assertTrue(res["passed"])

    # 5. DPO Pair Synthesis Modes (Fixtures 27-32)
    def test_fixture_27_dpo_parametric_world_memory_leak(self):
        synth = DPOPairSynthesizer()
        item = {
            "query": "How is spacecraft temperature controlled?",
            "passages": ["Active coolant loops regulate temperature."],
            "gold_answer": "Active coolant loops regulate temperature [1]."
        }
        pair = synth.synthesize_parametric_leak(item, 0)
        self.assertEqual(pair["failure_mode"], "PARAMETRIC_WORLD_MEMORY_LEAK")
        self.assertIn("IEEE in 2018", pair["rejected"])
        self.assertEqual(pair["chosen"], item["gold_answer"])

    def test_fixture_28_dpo_safety_injection(self):
        synth = DPOPairSynthesizer()
        item = {
            "query": "How is spacecraft temperature controlled?",
            "passages": ["Active coolant loops regulate temperature."],
            "gold_answer": "Active coolant loops regulate temperature [1]."
        }
        pair = synth.synthesize_safety_injection(item, 0)
        self.assertEqual(pair["failure_mode"], "HALLUCINATED_PROCEDURAL_SAFETY_STEP")
        self.assertIn("disconnect", pair["rejected"].lower())

    def test_fixture_29_dpo_over_refusal(self):
        synth = DPOPairSynthesizer()
        item = {
            "query": "How is spacecraft temperature controlled?",
            "passages": ["Active coolant loops regulate temperature."],
            "gold_answer": "Active coolant loops regulate temperature [1]."
        }
        pair = synth.synthesize_over_refusal(item, 0)
        self.assertEqual(pair["failure_mode"], "OVER_REFUSAL_ON_ANSWERABLE_QUERY")
        self.assertIn("not have enough information", pair["rejected"].lower())

    def test_fixture_30_verifier_detects_synthesized_safety_leak(self):
        synth = DPOPairSynthesizer()
        item = {
            "query": "How is temperature controlled?",
            "passages": ["Active coolant loops regulate temperature."],
            "gold_answer": "Active coolant loops regulate temperature [1]."
        }
        pair = synth.synthesize_safety_injection(item, 0)
        res = self.verifier.verify(pair["query"], pair["passages"], pair["rejected"])
        self.assertFalse(res["passed"])
        self.assertEqual(res["score"], 0.0)

    def test_fixture_31_verifier_detects_synthesized_over_refusal(self):
        synth = DPOPairSynthesizer()
        item = {
            "query": "How is temperature controlled?",
            "passages": ["Active coolant loops regulate temperature."],
            "gold_answer": "Active coolant loops regulate temperature [1]."
        }
        pair = synth.synthesize_over_refusal(item, 0)
        res = self.verifier.verify(pair["query"], pair["passages"], pair["rejected"])
        self.assertFalse(res["passed"])
        self.assertTrue(any("OVER_REFUSAL" in r for r in res["failure_reasons"]))

    def test_fixture_32_synthesize_all_batch(self):
        synth = DPOPairSynthesizer()
        items = [
            {
                "query": f"Query {i}",
                "passages": [f"Passage content {i}"],
                "gold_answer": f"Passage content {i} [1]."
            }
            for i in range(5)
        ]
        all_pairs = synth.synthesize_all(items)
        self.assertEqual(len(all_pairs), 15)  # 5 items * 3 failure modes
        modes = {p["failure_mode"] for p in all_pairs}
        self.assertEqual(len(modes), 3)

if __name__ == "__main__":
    unittest.main()
