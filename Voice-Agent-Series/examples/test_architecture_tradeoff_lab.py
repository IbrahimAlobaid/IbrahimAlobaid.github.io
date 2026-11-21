import unittest
from architecture_tradeoff_lab import TurnTrace, decision_hints, nearest_rank_percentile, summarize


class ArchitectureLabTests(unittest.TestCase):
    def test_response_is_audible_not_just_ready(self):
        t = TurnTrace("cascaded", 100, 700, 620)
        self.assertEqual(t.response_latency_ms, 600)
        self.assertEqual(t.playback_delay_ms, 80)

    def test_interruption_latency(self):
        t = TurnTrace("realtime", 0, 300, 200, 2000, 2075)
        self.assertEqual(t.interruption_stop_latency_ms, 75)

    def test_no_interrupt(self):
        self.assertIsNone(TurnTrace("hybrid", 0, 400, 360).interruption_stop_latency_ms)

    def test_partial_interruption_rejected(self):
        with self.assertRaises(ValueError):
            TurnTrace("realtime", 0, 400, 380, 1000)

    def test_negative_latency_rejected(self):
        with self.assertRaises(ValueError):
            TurnTrace("realtime", 0, 100, 150)

    def test_bad_architecture_rejected(self):
        with self.assertRaises(ValueError):
            TurnTrace("unknown", 0, 150, 100)

    def test_stopped_before_interruption_rejected(self):
        with self.assertRaises(ValueError):
            TurnTrace("realtime", 0, 300, 200, 1600, 1200)

    def test_rank_p95(self):
        self.assertEqual(nearest_rank_percentile([100, 200, 300, 400], 95), 400)

    def test_rank_empty(self):
        with self.assertRaises(ValueError):
            nearest_rank_percentile([], 95)

    def test_summary_groups_and_metrics(self):
        traces = [TurnTrace("cascaded", 0, 500, 450), TurnTrace("cascaded", 0, 900, 800), TurnTrace("realtime", 0, 350, 300)]
        metrics = summarize(traces)
        self.assertEqual(metrics["cascaded"]["response_p50_ms"], 700)
        self.assertEqual(metrics["realtime"]["response_p95_ms"], 350)

    def test_decision_hints(self):
        hints = decision_hints(exact_wording=True, live_captions=False, nuanced_voice_input=True, simple_provider_setup=False)
        self.assertEqual(len(hints), 2)
        self.assertIn("cascaded", hints[0])

    def test_default_recommendation_is_test(self):
        self.assertIn("benchmark", decision_hints(exact_wording=False, live_captions=False, nuanced_voice_input=False, simple_provider_setup=False)[0])


if __name__ == "__main__":
    unittest.main()
