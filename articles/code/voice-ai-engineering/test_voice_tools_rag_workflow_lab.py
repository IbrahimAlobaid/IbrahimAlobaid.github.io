"""Offline checks for article 13 — no voice service calls."""
import unittest
from voice_tools_rag_workflow_lab import (
    LocalKnowledgeBase, OfflineBookingWorkflow, EXAMPLE_DOCS, EXAMPLE_SLOTS,
    StaleSession, Denied, WorkflowError, IdempotencyConflict, words,
)


class RagTests(unittest.TestCase):
    def setUp(self):
        self.kb = LocalKnowledgeBase(EXAMPLE_DOCS)

    def test_tokenizer_multilingual(self):
        self.assertIn("الحجز", words("هل يمكن الحجز في النظام"))

    def test_tenant_isolation(self):
        self.assertNotIn("policy-b-1", [r.source_id for r in self.kb.search("clinic-a", "سياسة الإلغاء")])

    def test_second_tenant(self):
        self.assertEqual("policy-b-1", self.kb.search("clinic-b", "سياسة الإلغاء")[0].source_id)

    def test_no_result(self):
        self.assertEqual([], self.kb.search("clinic-a", "الطقس والرطوبة"))

    def test_evidence_contains_reference(self):
        self.assertTrue(all(r.source_id and r.title for r in self.kb.search("clinic-a", "الإلغاء")))

    def test_injection_is_data_only(self):
        evidence = self.kb.search("clinic-a", "Hours weekdays")
        self.assertTrue(any("Ignore previous" in e.excerpt for e in evidence))
        # Retrieval has no side-effecting tool.
        self.assertFalse(hasattr(self.kb, "confirm_booking"))

    def test_invalid_limit(self):
        with self.assertRaises(WorkflowError):
            self.kb.search("clinic-a", "ساعات", 0)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.w = OfflineBookingWorkflow(EXAMPLE_SLOTS)
        self.a = self.w.start("clinic-a", "u1")

    def prepare(self):
        return self.w.prepare_booking(self.a, "a-morning")

    def confirm(self, intent, key="abc", final=True, speaker=True, phrase="أؤكد الحجز"):
        return self.w.confirm_booking(self.a, intent.intent_id, final_transcript=final,
            speaker_verified=speaker, spoken_confirmation=phrase, idempotency_key=key)

    def test_only_same_tenant_available(self):
        self.assertEqual({"a-morning", "a-afternoon"}, {s.slot_id for s in self.w.available_slots(self.a)})

    def test_prepare_does_not_write(self):
        self.prepare()
        self.assertFalse(self.w.confirmed)

    def test_cross_tenant_slot_denied(self):
        with self.assertRaises(Denied):
            self.w.prepare_booking(self.a, "b-morning")

    def test_unauthed_session_denied(self):
        x = self.w.start("clinic-b", "guest", authenticated=False)
        with self.assertRaises(Denied):
            self.w.available_slots(x)

    def test_no_partial_transcript_commit(self):
        p = self.prepare()
        with self.assertRaises(Denied):
            self.confirm(p, final=False)
        self.assertFalse(self.w.confirmed)

    def test_no_unverified_speaker(self):
        p = self.prepare()
        with self.assertRaises(Denied):
            self.confirm(p, speaker=False)
        self.assertFalse(self.w.confirmed)

    def test_ambiguous_phrase_rejected(self):
        p = self.prepare()
        with self.assertRaises(Denied):
            self.confirm(p, phrase="مممم")

    def test_explicit_confirm(self):
        p = self.prepare()
        self.assertEqual("booked", self.confirm(p)["status"])
        self.assertEqual("u1", self.w.confirmed["a-morning"])

    def test_english_confirm(self):
        p = self.prepare()
        self.assertEqual("booked", self.confirm(p, phrase="confirm booking")["status"])

    def test_retry_same_key_does_not_double_commit(self):
        p = self.prepare()
        first = self.confirm(p)
        second = self.confirm(p)
        self.assertEqual(first, second)
        self.assertEqual(1, sum(e["kind"] == "booking_committed" for e in self.w.events))

    def test_conflicting_key_denied(self):
        p = self.prepare()
        self.confirm(p)
        other = self.w.prepare_booking(self.a, "a-afternoon")
        with self.assertRaises(IdempotencyConflict):
            self.confirm(other, key="abc")

    def test_reused_slot_denied(self):
        p = self.prepare()
        self.confirm(p)
        with self.assertRaises(WorkflowError):
            self.w.prepare_booking(self.a, "a-morning")

    def test_stale_generation_after_reconnect(self):
        p = self.prepare()
        newer = self.w.start("clinic-a", "u1")
        with self.assertRaises(StaleSession):
            self.confirm(p)
        with self.assertRaises(Denied):
            self.w.confirm_booking(newer, p.intent_id, final_transcript=True,
                speaker_verified=True, spoken_confirmation="أؤكد الحجز", idempotency_key="reconnect")

    def test_cancellation(self):
        p = self.prepare()
        self.w.cancel(self.a, p.intent_id)
        with self.assertRaises(Denied):
            self.confirm(p)

    def test_other_user_cannot_confirm(self):
        p = self.prepare()
        x = self.w.start("clinic-a", "u2")
        with self.assertRaises(Denied):
            self.w.confirm_booking(x, p.intent_id, final_transcript=True,
                speaker_verified=True, spoken_confirmation="confirm booking", idempotency_key="user2")

    def test_other_tenant_cannot_confirm(self):
        p = self.prepare()
        x = self.w.start("clinic-b", "u1")
        with self.assertRaises(Denied):
            self.w.confirm_booking(x, p.intent_id, final_transcript=True,
                speaker_verified=True, spoken_confirmation="confirm booking", idempotency_key="other")

    def test_missing_idempotency_key(self):
        p = self.prepare()
        with self.assertRaises(Denied):
            self.confirm(p, key="")

    def test_proposal_not_confirm(self):
        self.prepare()
        self.assertEqual(0, sum(e["kind"] == "booking_committed" for e in self.w.events))

    def test_no_duplicate_slot_across_users(self):
        p = self.prepare()
        self.confirm(p)
        x = self.w.start("clinic-a", "u2")
        self.assertNotIn("a-morning", [s.slot_id for s in self.w.available_slots(x)])


if __name__ == "__main__":
    unittest.main()
