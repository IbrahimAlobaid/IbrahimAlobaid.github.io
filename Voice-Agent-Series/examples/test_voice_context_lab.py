import unittest
from voice_context_lab import VoiceContext


class VoiceContextTests(unittest.TestCase):
    def test_interim_not_committed(self):
        s = VoiceContext()
        s.on_interim_transcript("maybe")
        self.assertEqual(s.turns, [])
        self.assertEqual(s.prompt_context()["recent_turns"], [])

    def test_final_transcript_committed(self):
        s = VoiceContext()
        s.commit_user_turn("Hello")
        self.assertEqual(s.turns[-1].text, "Hello")
        self.assertEqual(s.partial_transcript, "")

    def test_correcting_slot_invalidates_approval(self):
        s = VoiceContext()
        s.commit_user_turn("details", {"service": "call", "date": "2026-11-26", "time": "10:00"})
        s.approve_current_details()
        s.commit_user_turn("make it 3", {"time": "15:00"})
        self.assertFalse(s.user_approved)
        self.assertEqual(s.slots["time"], "15:00")

    def test_same_slot_does_not_reset_approval(self):
        s = VoiceContext()
        s.commit_user_turn("details", {"service": "call", "date": "2026-11-26", "time": "10:00"})
        s.approve_current_details()
        s.commit_user_turn("still ten", {"time": "10:00"})
        self.assertTrue(s.user_approved)

    def test_interruption_only_commits_acknowledged_segment(self):
        s = VoiceContext()
        s.queue_reply(["First sentence.", "Second sentence."])
        s.acknowledge_played_segment(0)
        s.interrupt_reply()
        self.assertEqual(s.turns[-1].text, "First sentence.")
        self.assertEqual(s.turns[-1].delivery, "partial")

    def test_interruption_without_playback_keeps_no_assistant_turn(self):
        s = VoiceContext()
        s.queue_reply(["Not heard."])
        s.interrupt_reply()
        self.assertEqual(len(s.turns), 0)

    def test_full_playback_commits(self):
        s = VoiceContext()
        s.queue_reply(["A", "B"])
        s.acknowledge_played_segment(0)
        s.acknowledge_played_segment(1)
        s.finish_reply()
        self.assertEqual(s.turns[-1].text, "A B")
        self.assertEqual(s.turns[-1].delivery, "final")

    def test_out_of_order_playback_rejected(self):
        s = VoiceContext()
        s.queue_reply(["A", "B"])
        with self.assertRaises(ValueError):
            s.acknowledge_played_segment(1)

    def test_finish_without_ack_rejected(self):
        s = VoiceContext()
        s.queue_reply(["A"])
        with self.assertRaises(RuntimeError):
            s.finish_reply()

    def test_no_booking_before_approval(self):
        s = VoiceContext()
        s.commit_user_turn("details", {"service": "call", "date": "2026-11-26", "time": "10:00"})
        self.assertFalse(s.ready_to_request_booking())
        s.approve_current_details()
        self.assertTrue(s.ready_to_request_booking())

    def test_recent_turn_limit_preserves_state(self):
        s = VoiceContext()
        s.commit_user_turn("details", {"service": "call", "date": "2026-11-26", "time": "10:00"})
        for i in range(10):
            s.commit_user_turn(f"chat {i}")
        payload = s.prompt_context(recent_turns=2)
        self.assertEqual(len(payload["recent_turns"]), 2)
        self.assertEqual(payload["task_state"]["slots"]["service"], "call")

    def test_unapproved_unknown_field(self):
        with self.assertRaises(ValueError):
            VoiceContext().commit_user_turn("hello", {"secret": "value"})

    def test_no_duplicate_pending_speech(self):
        s = VoiceContext()
        s.queue_reply(["A"])
        with self.assertRaises(RuntimeError):
            s.queue_reply(["B"])

    def test_no_approval_if_missing_slots(self):
        with self.assertRaises(ValueError):
            VoiceContext().approve_current_details()

    def test_no_zero_history_slicing_bug(self):
        s = VoiceContext()
        s.commit_user_turn("Hi")
        self.assertEqual(s.prompt_context(recent_turns=0)["recent_turns"], [])


if __name__ == "__main__":
    unittest.main()
