"""No secrets, audio hardware, network, or external dependencies required."""
import unittest
from capstone_domain import DemoBookingService, DomainError, KNOWLEDGE


class CapstoneDomainTests(unittest.TestCase):
    def setUp(self):
        self.now = 100.0
        self.svc = DemoBookingService(clock=lambda: self.now, ttl_seconds=90)
        self.svc.create_session("alpha", "A", "alice")
        self.svc.create_session("beta", "B", "bob")

    def pending(self):
        self.svc.propose("alpha", "A", "demo-101")
        return self.svc.demo_trusted_approval_details("alpha", "A")

    def assert_denied(self, cb):
        with self.assertRaises(DomainError):
            cb()

    def test_faq_existing(self):
        self.assertEqual(self.svc.knowledge("hours")["status"], "found")
    def test_faq_source(self):
        self.assertEqual(self.svc.knowledge("policy")["source"], "demo-policy:policy")
    def test_faq_unknown(self):
        self.assertEqual(self.svc.knowledge("secret")["status"], "not_found")
    def test_knowledge_closed_set(self):
        self.assertEqual(len(KNOWLEDGE), 4)
    def test_day_filters_slots(self):
        self.assertEqual(len(self.svc.list_slots("2026-12-02")), 2)
    def test_day_different(self):
        self.assertEqual(len(self.svc.list_slots("2026-12-03")), 1)
    def test_day_empty(self):
        self.assertEqual(self.svc.list_slots("2027-01-01"), [])
    def test_day_rejects_bad_date(self):
        self.assert_denied(lambda: self.svc.list_slots("tomorrow"))
    def test_slot_nonexistent(self):
        self.assert_denied(lambda: self.svc.propose("alpha", "A", "nope"))
    def test_unknown_session(self):
        self.assert_denied(lambda: self.svc.propose("alpha", "nope", "demo-101"))
    def test_unknown_tenant(self):
        self.assert_denied(lambda: self.svc.propose("beta", "A", "demo-101"))
    def test_duplicate_session(self):
        self.assert_denied(lambda: self.svc.create_session("alpha", "A", "alice"))
    def test_empty_subject(self):
        self.assert_denied(lambda: self.svc.create_session("t", "x", ""))
    def test_proposal_not_committed(self):
        self.pending()
        self.assertEqual(self.svc.bookings, {})
    def test_llm_result_does_not_expose_secret(self):
        proposal = self.svc.propose("alpha", "A", "demo-101")
        self.assertNotIn("approval_token", proposal)
    def test_pending_requires_resolution(self):
        self.pending()
        self.assert_denied(lambda: self.svc.propose("alpha", "A", "demo-102"))
    def test_cancel_removes_pending(self):
        self.pending()
        self.svc.cancel("alpha", "A")
        self.assertIsNone(self.svc.sessions[("alpha", "A")].pending)
    def test_cancel_revision_increment(self):
        self.pending()
        revision = self.svc.sessions[("alpha", "A")].revision
        self.svc.cancel("alpha", "A")
        self.assertGreater(self.svc.sessions[("alpha", "A")].revision, revision)
    def test_confirm_correct(self):
        p = self.pending()
        result = self.svc.confirm_from_trusted_ui(**p)
        self.assertEqual(result["status"], "simulated_committed")
    def test_confirm_wrong_subject(self):
        p = self.pending()
        p["authenticated_subject"] = "mallory"
        self.assert_denied(lambda: self.svc.confirm_from_trusted_ui(**p))
    def test_confirm_wrong_token(self):
        p = self.pending()
        p["approval_token"] = "wrong"
        self.assert_denied(lambda: self.svc.confirm_from_trusted_ui(**p))
    def test_confirm_wrong_id(self):
        p = self.pending()
        p["request_id"] = "wrong"
        self.assert_denied(lambda: self.svc.confirm_from_trusted_ui(**p))
    def test_confirm_wrong_generation(self):
        p = self.pending()
        p["generation"] += 1
        self.assert_denied(lambda: self.svc.confirm_from_trusted_ui(**p))
    def test_confirm_wrong_revision(self):
        p = self.pending()
        p["revision"] += 1
        self.assert_denied(lambda: self.svc.confirm_from_trusted_ui(**p))
    def test_confirm_expired(self):
        p = self.pending()
        self.now = 190.0
        self.assert_denied(lambda: self.svc.confirm_from_trusted_ui(**p))
    def test_confirm_before_expiry(self):
        p = self.pending()
        self.now = 189.9
        self.assertEqual(self.svc.confirm_from_trusted_ui(**p)["slot_id"], "demo-101")
    def test_reconnect_invalidates(self):
        p = self.pending()
        self.svc.reconnect("alpha", "A")
        self.assert_denied(lambda: self.svc.confirm_from_trusted_ui(**p))
    def test_no_pending_refused(self):
        self.assert_denied(lambda: self.svc.demo_trusted_approval_details("alpha", "A"))
    def test_idempotent_retry(self):
        p = self.pending()
        first = self.svc.confirm_from_trusted_ui(**p)
        second = self.svc.confirm_from_trusted_ui(**p)
        self.assertEqual(first, second)
        self.assertEqual(len(self.svc.bookings), 1)
    def test_retry_wrong_token_is_denied(self):
        p = self.pending()
        self.svc.confirm_from_trusted_ui(**p)
        p["approval_token"] = "a different token"
        self.assert_denied(lambda: self.svc.confirm_from_trusted_ui(**p))
    def test_retry_wrong_generation_is_denied(self):
        p = self.pending()
        self.svc.confirm_from_trusted_ui(**p)
        p["generation"] += 1
        self.assert_denied(lambda: self.svc.confirm_from_trusted_ui(**p))
    def test_idempotency_isolation(self):
        p = self.pending()
        self.svc.confirm_from_trusted_ui(**p)
        self.svc.propose("beta", "B", "demo-102")
        q = self.svc.demo_trusted_approval_details("beta", "B")
        self.svc.confirm_from_trusted_ui(**q)
        self.assertEqual(len(self.svc.bookings), 2)
    def test_no_mutation_on_faq(self):
        self.svc.knowledge("hours")
        self.assertEqual(self.svc.bookings, {})
    def test_no_mutation_on_find_slots(self):
        self.svc.list_slots("2026-12-02")
        self.assertEqual(self.svc.bookings, {})
    def test_confirm_while_cancelled(self):
        p = self.pending()
        self.svc.cancel("alpha", "A")
        self.assert_denied(lambda: self.svc.confirm_from_trusted_ui(**p))
    def test_separate_session_cannot_read_pending(self):
        self.pending()
        self.assert_denied(lambda: self.svc.demo_trusted_approval_details("beta", "B"))
    def test_empty_tenant_rejected(self):
        self.assert_denied(lambda: self.svc.create_session("", "s", "subject"))
    def test_ttl_must_be_positive(self):
        with self.assertRaises(ValueError):
            DemoBookingService(clock=lambda: 0, ttl_seconds=0)


if __name__ == "__main__":
    unittest.main()
