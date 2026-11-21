"""Unit tests for the educational VAD/endpointing state machine."""
import unittest
from turn_detection_lab import AcousticTurnGate, TurnConfig, frames, run_probabilities, example_session


def names(events):
    return [e.name for e in events]


class TurnDetectionTests(unittest.TestCase):
    def test_silence_has_no_events(self):
        self.assertEqual(run_probabilities(frames(2200, .01)), [])

    def test_noisy_short_spike_does_not_start(self):
        self.assertEqual(run_probabilities(frames(80, .9) + frames(900, .01)), [])

    def test_speech_start_after_min_duration(self):
        out = run_probabilities(frames(100, .95))
        self.assertEqual(names(out), ['turn_started', 'speech_started'])
        self.assertEqual(out[0].at_ms, 100)

    def test_utterance_pause_is_not_immediately_turn_end(self):
        out = run_probabilities(frames(300, .95) + frames(360, .01))
        self.assertIn('speech_stopped', names(out))
        self.assertNotIn('turn_ended', names(out))

    def test_long_silence_ends_turn(self):
        out = run_probabilities(frames(300, .95) + frames(1000, .01))
        self.assertEqual(names(out), ['turn_started', 'speech_started', 'speech_stopped', 'turn_ended'])

    def test_two_segments_in_one_turn(self):
        out = example_session()
        self.assertEqual(names(out), ['turn_started','speech_started','speech_stopped',
                                      'speech_started','speech_stopped','turn_ended'])

    def test_two_turns(self):
        out = run_probabilities(frames(300,.9) + frames(900,.01) +
                                frames(300,.9) + frames(900,.01))
        self.assertEqual(names(out).count('turn_started'), 2)
        self.assertEqual(names(out).count('turn_ended'), 2)

    def test_hysteresis_avoids_boundary_flicker(self):
        out = run_probabilities(frames(140,.9) + frames(400,.45) + frames(800,.01))
        self.assertEqual(names(out).count('speech_started'), 1)
        self.assertEqual(names(out).count('speech_stopped'), 1)

    def test_agent_not_playing_does_not_interrupt(self):
        out = run_probabilities(frames(400,.9), assistant_playing=False)
        self.assertNotIn('interrupted_assistant', names(out))

    def test_barge_in_after_sustained_speech(self):
        out = run_probabilities(frames(260,.9), assistant_playing=True)
        self.assertEqual(names(out).count('interrupted_assistant'), 1)
        self.assertEqual([e.at_ms for e in out if e.name=='interrupted_assistant'], [200])

    def test_short_barge_in_not_confirmed(self):
        out = run_probabilities(frames(160,.9) + frames(800,.01), assistant_playing=True)
        self.assertNotIn('interrupted_assistant', names(out))

    def test_interruption_not_repeated_while_playing(self):
        out = run_probabilities(frames(800,.9), assistant_playing=True)
        self.assertEqual(names(out).count('interrupted_assistant'), 1)

    def test_repeated_runs_are_deterministic(self):
        p = frames(220,.9)+frames(720,.05)
        self.assertEqual(run_probabilities(p), run_probabilities(p))

    def test_probability_outside_range_raises(self):
        with self.assertRaises(ValueError): AcousticTurnGate().process(1.1)
        with self.assertRaises(ValueError): AcousticTurnGate().process(-.02)

    def test_invalid_config_raises(self):
        for kwargs in [dict(frame_ms=0),dict(start_threshold=.2, continue_threshold=.3),
                       dict(endpoint_ms=100),dict(min_interrupt_ms=0)]:
            with self.assertRaises(ValueError): TurnConfig(**kwargs)

    def test_frames_requires_exact_multiple(self):
        with self.assertRaises(ValueError): frames(23,.7)

    def test_turn_end_happens_at_endpoint_delay_from_silence(self):
        out = run_probabilities(frames(300,.9)+frames(700,.01))
        e = next(x for x in out if x.name == 'turn_ended')
        self.assertEqual(e.at_ms, 1000)

    def test_gap_between_segments_not_a_new_turn(self):
        out = run_probabilities(frames(500,.9)+frames(660,.01)+frames(200,.9))
        self.assertEqual(names(out).count('turn_started'),1)
        self.assertEqual(names(out).count('speech_started'),2)
        self.assertNotIn('turn_ended',names(out))


if __name__ == '__main__':
    unittest.main()
