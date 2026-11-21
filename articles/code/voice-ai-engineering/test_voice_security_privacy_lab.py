import unittest
from voice_security_privacy_lab import PolicyDenied, Principal, VoiceSecurityPolicyLab


class Clock:
    def __init__(self): self.t = 1000.0
    def __call__(self): return self.t
    def advance(self, seconds): self.t += seconds


class VoiceSecurityLabTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.policy = VoiceSecurityPolicyLab(now=self.clock)
        self.principal = Principal('tenant-A', 'principal-A', frozenset({'appointment:write'}))
        self.s = self.policy.start(self.principal)

    def prepare(self, **overrides):
        req = dict(target_tenant='tenant-A', operation='appointment.cancel',
                   parameters={'appointment_id': 'A-1'}, transcript_state='final', origin='direct_user')
        req.update(overrides)
        return self.policy.prepare_action(self.s.session_id, **req)

    def confirm(self, intent):
        self.policy.confirm_action(self.s.session_id, intent.intent_id,
                                   confirmation='confirm', transcript_state='final', origin='direct_user')

    def test_default_no_recording(self):
        self.assertFalse(self.s.recording_consent)
    def test_mic_permission_is_not_recording_consent(self):
        with self.assertRaises(PolicyDenied): self.policy.register_recording_metadata(self.s.session_id, retention_seconds=4)
    def test_grant_separate_recording_consent(self):
        self.policy.set_recording_consent(self.s.session_id, True, explicit_user_choice=True)
        self.assertTrue(self.s.recording_consent)
    def test_recording_choice_not_implicit(self):
        with self.assertRaises(PolicyDenied): self.policy.set_recording_consent(self.s.session_id, True, explicit_user_choice=False)
    def test_recording_revocation_clears_local_metadata(self):
        self.policy.set_recording_consent(self.s.session_id, True, explicit_user_choice=True)
        self.policy.register_recording_metadata(self.s.session_id, retention_seconds=60)
        self.policy.set_recording_consent(self.s.session_id, False, explicit_user_choice=True)
        self.assertFalse(self.policy.artifacts)
    def test_retention_purges_at_expiry(self):
        self.policy.set_recording_consent(self.s.session_id, True, explicit_user_choice=True)
        self.policy.register_recording_metadata(self.s.session_id, retention_seconds=10)
        self.clock.advance(10)
        self.assertEqual(1, self.policy.purge_expired())
    def test_retention_not_yet_expired(self):
        self.policy.set_recording_consent(self.s.session_id, True, explicit_user_choice=True)
        self.policy.register_recording_metadata(self.s.session_id, retention_seconds=10)
        self.clock.advance(9)
        self.assertEqual(0, self.policy.purge_expired())
    def test_reject_invalid_retention(self):
        self.policy.set_recording_consent(self.s.session_id, True, explicit_user_choice=True)
        with self.assertRaises(PolicyDenied): self.policy.register_recording_metadata(self.s.session_id, retention_seconds=0)
    def test_tenant_isolation(self):
        with self.assertRaises(PolicyDenied): self.prepare(target_tenant='tenant-B')
    def test_reject_interim_stt(self):
        with self.assertRaises(PolicyDenied): self.prepare(transcript_state='interim')
    def test_untrusted_retrieved_content_not_authority(self):
        with self.assertRaises(PolicyDenied): self.prepare(origin='retrieved_document')
    def test_missing_server_scope_denied(self):
        other = self.policy.start(Principal('tenant-A','readonly', frozenset()))
        with self.assertRaises(PolicyDenied):
            self.policy.prepare_action(other.session_id, target_tenant='tenant-A', operation='appointment.cancel',
                                       parameters={'appointment_id':'A-1'}, transcript_state='final', origin='direct_user')
    def test_server_authentication_required(self):
        with self.assertRaises(PolicyDenied):
            self.policy.start(Principal('tenant-A','fake', frozenset(), server_authenticated=False))
    def test_operation_allowlist(self):
        with self.assertRaises(PolicyDenied): self.prepare(operation='send_all_records')
    def test_parameter_schema_rejects_extra(self):
        with self.assertRaises(PolicyDenied): self.prepare(parameters={'appointment_id':'A-1', 'admin': True})
    def test_parameter_schema_rejects_empty_id(self):
        with self.assertRaises(PolicyDenied): self.prepare(parameters={'appointment_id':' '})
    def test_unconfirmed_action_denied(self):
        i = self.prepare()
        with self.assertRaises(PolicyDenied): self.policy.execute_action(self.s.session_id, i.intent_id, idempotency_key='k1')
    def test_interim_confirmation_denied(self):
        i = self.prepare()
        with self.assertRaises(PolicyDenied):
            self.policy.confirm_action(self.s.session_id, i.intent_id, confirmation='confirm', transcript_state='interim', origin='direct_user')
    def test_external_confirmation_denied(self):
        i = self.prepare()
        with self.assertRaises(PolicyDenied):
            self.policy.confirm_action(self.s.session_id, i.intent_id, confirmation='confirm', transcript_state='final', origin='retrieved_document')
    def test_wrong_confirmation_denied(self):
        i = self.prepare()
        with self.assertRaises(PolicyDenied):
            self.policy.confirm_action(self.s.session_id, i.intent_id, confirmation='maybe', transcript_state='final', origin='direct_user')
    def test_cross_session_confirmation_denied(self):
        i = self.prepare()
        s2 = self.policy.start(self.principal)
        with self.assertRaises(PolicyDenied):
            self.policy.confirm_action(s2.session_id, i.intent_id, confirmation='confirm', transcript_state='final', origin='direct_user')
    def test_confirmation_expiry_denied(self):
        i = self.prepare(ttl_seconds=5)
        self.clock.advance(5)
        with self.assertRaises(PolicyDenied): self.confirm(i)
    def test_reconnect_invalidates_pending_confirmation(self):
        i = self.prepare(); self.confirm(i); self.policy.reconnect(self.s.session_id)
        with self.assertRaises(PolicyDenied): self.policy.execute_action(self.s.session_id, i.intent_id, idempotency_key='k1')
    def test_normal_commit_uses_explicit_confirmation(self):
        i = self.prepare(); self.confirm(i)
        self.assertEqual('appointment.cancel', self.policy.execute_action(self.s.session_id, i.intent_id, idempotency_key='k1').operation)
    def test_idempotent_retry_is_same_receipt(self):
        i = self.prepare(); self.confirm(i)
        a = self.policy.execute_action(self.s.session_id, i.intent_id, idempotency_key='k1')
        b = self.policy.execute_action(self.s.session_id, i.intent_id, idempotency_key='k1')
        self.assertEqual(a, b)
    def test_idempotency_reused_with_different_effect_denied(self):
        a = self.prepare(); self.confirm(a)
        self.policy.execute_action(self.s.session_id, a.intent_id, idempotency_key='same')
        b = self.prepare(parameters={'appointment_id': 'A-2'}); self.confirm(b)
        with self.assertRaises(PolicyDenied): self.policy.execute_action(self.s.session_id, b.intent_id, idempotency_key='same')
    def test_foreign_session_execute_denied(self):
        i = self.prepare(); self.confirm(i)
        s2 = self.policy.start(self.principal)
        with self.assertRaises(PolicyDenied):
            self.policy.execute_action(s2.session_id, i.intent_id, idempotency_key='k2')
    def test_closed_session_denied(self):
        i = self.prepare(); self.confirm(i); self.policy.end(self.s.session_id)
        with self.assertRaises(PolicyDenied): self.policy.execute_action(self.s.session_id, i.intent_id, idempotency_key='k1')
    def test_audit_no_raw_audio_or_tool_args(self):
        i = self.prepare(parameters={'appointment_id':'private-identity-value'})
        self.confirm(i)
        log = str(self.policy.audit)
        self.assertNotIn('private-identity-value', log)
        self.assertNotIn(i.digest, log)
    def test_intent_digest_tenant_and_action_bound(self):
        a = self.prepare(); b = self.prepare(parameters={'appointment_id':'A-2'})
        self.assertNotEqual(a.digest, b.digest)
    def test_blank_idempotency_key_denied(self):
        i = self.prepare(); self.confirm(i)
        with self.assertRaises(PolicyDenied): self.policy.execute_action(self.s.session_id, i.intent_id, idempotency_key='')
    def test_expired_before_execute_denied(self):
        i = self.prepare(ttl_seconds=10); self.confirm(i); self.clock.advance(10)
        with self.assertRaises(PolicyDenied): self.policy.execute_action(self.s.session_id, i.intent_id, idempotency_key='k1')


if __name__ == '__main__':
    unittest.main()
