import unittest
from interruption_playback_lab import AlignedCaption, PlaybackController, Status, demonstration


def filled():
    c = PlaybackController()
    e = c.start('a', 3000, [AlignedCaption(0, 800, 'Hello'), AlignedCaption(800, 1800, 'world')])
    for k, n in [('generated', 3000), ('synthesized', 2600), ('transmitted', 2400), ('buffered', 2100)]:
        assert c.advance(k, n, e)
    return c, e


class TestPlaybackLab(unittest.TestCase):
    def test_new_turn(self):
        c = PlaybackController(); e = c.start('a', 1000)
        self.assertEqual((e, c.active.status), (1, Status.PLAYING))

    def test_empty_id_rejected(self):
        with self.assertRaises(ValueError): PlaybackController().start('  ', 1000)

    def test_negative_duration_rejected(self):
        with self.assertRaises(ValueError): PlaybackController().start('a', -1)

    def test_overflow_generation(self):
        c = PlaybackController(); e = c.start('a', 1000)
        with self.assertRaises(ValueError): c.advance('generated', 1001, e)

    def test_order_required(self):
        c = PlaybackController(); e = c.start('a', 1000)
        with self.assertRaises(ValueError): c.advance('buffered', 100, e)

    def test_playback_never_derived_from_sent(self):
        c, e = filled()
        self.assertEqual(c.active.played_ms, 0)
        self.assertEqual(c.active.transmitted_ms, 2400)

    def test_buffered_ceiling(self):
        c, e = filled()
        with self.assertRaises(ValueError): c.acknowledge_playback(2101, e)

    def test_playback_monotonic(self):
        c, e = filled(); c.acknowledge_playback(1000, e)
        with self.assertRaises(ValueError): c.acknowledge_playback(900, e)

    def test_candidate_pause(self):
        c, e = filled()
        self.assertTrue(c.pause_for_candidate(e))
        self.assertEqual(c.active.status, Status.PAUSED)
        self.assertFalse(c.advance('generated', 3000, e))

    def test_false_interruption_resume(self):
        c, e = filled(); c.pause_for_candidate(e)
        self.assertTrue(c.resume_false_interrupt(e))
        self.assertEqual(c.active.status, Status.PLAYING)

    def test_true_interruption_truncation(self):
        c, e = filled(); c.acknowledge_playback(700, e)
        c.pause_for_candidate(e)
        plan = c.confirm_interruption(e, final_played_ms=1200)
        self.assertEqual(plan['unheard_buffered_ms'], 900)
        self.assertEqual(c.realtime_ws_truncate_event(e)['audio_end_ms'], 1200)
        self.assertEqual(c.active.status, Status.INTERRUPTED)

    def test_double_interrupt_idempotent(self):
        c, e = filled(); c.pause_for_candidate(e)
        c.confirm_interruption(e, final_played_ms=1000)
        self.assertIsNone(c.confirm_interruption(e, final_played_ms=1100))

    def test_late_audio_discarded(self):
        c, e = filled(); c.pause_for_candidate(e)
        c.confirm_interruption(e, final_played_ms=1000)
        self.assertFalse(c.advance('buffered', 2100, e))
        self.assertFalse(c.acknowledge_playback(1500, e))

    def test_new_turn_reject_old_epoch(self):
        c, e = filled(); c.pause_for_candidate(e); c.confirm_interruption(e, final_played_ms=1000)
        new_e = c.start('new', 500)
        self.assertNotEqual(new_e, e)
        self.assertFalse(c.advance('generated', 3000, e))

    def test_played_caption_only_complete(self):
        c, e = filled(); c.acknowledge_playback(1000, e)
        self.assertEqual(c.played_caption(), 'Hello')

    def test_no_alignment_means_unknown(self):
        c = PlaybackController(); c.start('x', 1000)
        self.assertIsNone(c.played_caption())

    def test_finish_only_after_full_playback(self):
        c = PlaybackController(); e = c.start('x', 1000)
        for stage in ('generated', 'synthesized', 'transmitted', 'buffered'):
            c.advance(stage, 1000, e)
        with self.assertRaises(ValueError): c.mark_finished(e)
        c.acknowledge_playback(1000, e)
        self.assertTrue(c.mark_finished(e))

    def test_pause_no_old_continuation(self):
        c, e = filled(); c.pause_for_candidate(e); c.confirm_interruption(e, final_played_ms=100)
        self.assertFalse(c.resume_false_interrupt(e))

    def test_truncate_only_after_stop(self):
        c, e = filled(); self.assertIsNone(c.realtime_ws_truncate_event(e))

    def test_example(self):
        d = demonstration(); self.assertEqual(d['plan']['played_ms'], 1500)
        self.assertEqual(d['caption'], 'You can use your passport')

    def test_caption_invalid(self):
        with self.assertRaises(ValueError): AlignedCaption(300, 300, 'bad')


if __name__ == '__main__':
    unittest.main()
