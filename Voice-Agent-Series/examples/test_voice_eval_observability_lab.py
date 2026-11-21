import copy
import unittest
from pathlib import Path
from voice_eval_observability_lab import (
    InvalidCase, evaluate, is_unsafe_write, load_jsonl, percentile, release_gate,
    safe_log_event, validate_case,
)

PATH = Path(__file__).with_name("15-synthetic-evaluation-cases.jsonl")

class VoiceEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_jsonl(PATH, "baseline")
        cls.regression = load_jsonl(PATH, "regression")

    def test_fixture_counts(self):
        self.assertEqual(len(self.baseline), 24)
        self.assertEqual(len(self.regression), 8)

    def test_baseline_release_passes(self):
        self.assertEqual(release_gate(evaluate(self.baseline))["status"], "PASS")

    def test_regression_release_blocks(self):
        self.assertEqual(release_gate(evaluate(self.regression), min_samples=5)["status"], "BLOCK")

    def test_baseline_has_interruptions(self):
        self.assertGreater(evaluate(self.baseline)["interruption_samples"], 0)

    def test_regression_detects_unsafe(self):
        self.assertGreater(evaluate(self.regression)["unsafe_write_count"], 0)

    def test_regression_detects_privacy(self):
        self.assertGreater(evaluate(self.regression)["privacy_leak_count"], 0)

    def test_regression_detects_long_latency(self):
        self.assertGreater(evaluate(self.regression)["ttfa_p95_ms"], 1800)

    def test_invalid_missing_field(self):
        c=copy.deepcopy(self.baseline[0]); del c["id"]
        with self.assertRaises(InvalidCase): validate_case(c)

    def test_invalid_time_order(self):
        c=copy.deepcopy(self.baseline[0]); c["first_played_ms"] = -1
        with self.assertRaises(InvalidCase): validate_case(c)

    def test_invalid_bool(self):
        c=copy.deepcopy(self.baseline[0]); c["authorized"] = "false"
        with self.assertRaises(InvalidCase): validate_case(c)

    def test_no_interrupt_timestamps(self):
        c=copy.deepcopy(self.baseline[0]); c["interrupted"] = False; c["interrupt_start_ms"] = 1
        with self.assertRaises(InvalidCase): validate_case(c)

    def test_interrupt_order(self):
        c=next(copy.deepcopy(c) for c in self.baseline if c["interrupted"])
        c["audio_stopped_ms"] = c["interrupt_start_ms"]-1
        with self.assertRaises(InvalidCase): validate_case(c)

    def test_nearest_rank(self):
        self.assertEqual(percentile([1,4,2,3,5], .95), 5)
        self.assertEqual(percentile([1,4,2,3,5], .50), 3)

    def test_empty_percentile(self): self.assertIsNone(percentile([], .95))
    def test_bad_percentile(self):
        with self.assertRaises(ValueError): percentile([1], 1.1)

    def test_empty_dataset(self):
        with self.assertRaises(ValueError): evaluate([])

    def test_duplicate_ids(self):
        with self.assertRaises(InvalidCase): evaluate([self.baseline[0], self.baseline[0]])

    def test_unsafe_write_without_confirmation(self):
        c=copy.deepcopy(self.baseline[0]); c.update(expected_tool="cancel", actual_tool="cancel",tool_executed=True,confirmation_required=True,confirmed=False)
        self.assertTrue(is_unsafe_write(c))

    def test_unsafe_write_other_tenant(self):
        c=copy.deepcopy(self.baseline[0]); c.update(expected_tool="cancel",actual_tool="cancel",tool_executed=True,tenant_match=False)
        self.assertTrue(is_unsafe_write(c))

    def test_unsafe_write_replay(self):
        c=copy.deepcopy(self.baseline[0]); c.update(expected_tool="cancel",actual_tool="cancel",tool_executed=True,idempotent=False)
        self.assertTrue(is_unsafe_write(c))

    def test_unsafe_write_unauthorized(self):
        c=copy.deepcopy(self.baseline[0]); c.update(expected_tool="cancel",actual_tool="cancel",tool_executed=True,authorized=False)
        self.assertTrue(is_unsafe_write(c))

    def test_unsafe_write_unexpected_action(self):
        c=copy.deepcopy(self.baseline[0]); c.update(expected_tool="none",actual_tool="cancel",tool_executed=True)
        self.assertTrue(is_unsafe_write(c))

    def test_safe_log_allowlist(self):
        c=copy.deepcopy(self.baseline[0]); c["raw_transcript"]="name@example.com"; c["api_key"]="SECRET"
        fields=safe_log_event(c)
        self.assertNotIn("raw_transcript",fields)
        self.assertNotIn("api_key",fields)
        self.assertEqual(fields["id"],c["id"])

    def test_group_filter(self): self.assertEqual(len(load_jsonl(PATH,"baseline")),24)
    def test_invalid_partial_time(self):
        c=copy.deepcopy(self.baseline[0]); c["stt_final_ms"] = float("nan")
        with self.assertRaises(InvalidCase): validate_case(c)

    def test_metric_names(self):
        d=evaluate(self.baseline)
        self.assertIn("ttfa_p95_ms",d)
        self.assertIn("intent_and_tool_exact_match_rate",d)

    def test_coverage_gate(self):
        sample=[c for c in self.baseline if not c["interrupted"]]
        self.assertFalse(release_gate(evaluate(sample),min_samples=1)["checks"]["interruption_coverage"])

    def test_min_samples_gate(self):
        self.assertFalse(release_gate(evaluate(self.baseline),min_samples=100)["checks"]["sample_count"])

    def test_intent_mismatch(self):
        c=copy.deepcopy(self.baseline[0]); c["actual_intent"]="wrong"
        self.assertEqual(evaluate([c])["intent_and_tool_exact_match_rate"], 0.0)

    def test_latencies_nonnegative(self):
        d=evaluate(self.baseline)
        self.assertGreaterEqual(d["ttfa_p50_ms"],0)
        self.assertLessEqual(d["ttfa_p50_ms"],d["ttfa_p95_ms"])

if __name__=='__main__': unittest.main()
