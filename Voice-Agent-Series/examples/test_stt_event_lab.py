import unittest
from stt_event_lab import STTEvent, TranscriptAssembler, normalize_for_wer, word_error_rate


class TranscriptTests(unittest.TestCase):
    def test_partial_is_replaced_by_new_partial(self):
        s = TranscriptAssembler()
        s.handle(STTEvent("partial", "a", "أريد مو"))
        s.handle(STTEvent("partial", "a", "أريد موعد"))
        self.assertEqual(s.display_text, "أريد موعد")
        self.assertEqual(s.stable_text, "")

    def test_final_commits_once(self):
        s = TranscriptAssembler()
        s.handle(STTEvent("partial", "a", "book Tues"))
        s.handle(STTEvent("final", "a", "book Tuesday"))
        s.handle(STTEvent("partial", "a", "stale hypothesis"))
        self.assertEqual(s.display_text, "book Tuesday")
        self.assertEqual(s.stable_text, "book Tuesday")

    def test_end_is_independent_from_final(self):
        s = TranscriptAssembler()
        s.handle(STTEvent("final", "a", "hello"))
        self.assertFalse(s.turn_ended)
        s.handle(STTEvent("turn_end"))
        self.assertTrue(s.turn_ended)

    def test_duplicate_conflicting_final_rejected(self):
        s = TranscriptAssembler()
        s.handle(STTEvent("final", "a", "yes"))
        with self.assertRaises(ValueError):
            s.handle(STTEvent("final", "a", "no"))

    def test_wer_substitution(self):
        self.assertAlmostEqual(word_error_rate("أريد موعد يوم الثلاثاء", "أريد موعد يوم الخميس"), 0.25)

    def test_wer_insertion_and_deletion(self):
        self.assertAlmostEqual(word_error_rate("one two three", "one two"), 1 / 3)
        self.assertAlmostEqual(word_error_rate("one two", "one two three"), 0.5)

    def test_normalization_punctuation_case(self):
        self.assertEqual(normalize_for_wer("Hello, WORLD!"), ["hello", "world"])


if __name__ == "__main__":
    unittest.main()
