# Article 14 — Voice Security, Privacy & Safety Lab

**Scope:** An offline, standard-library-only demonstration of application-side policy checks for voice agents. **It does not connect to STT/LLM/TTS providers, capture or store audio, verify identity, encrypt media, or change a real booking.**

## Run

From the `Voice-Agent-Series` root:

```bash
python examples/voice_security_privacy_lab.py
python -m unittest discover -s examples -p 'test_voice_security_privacy_lab.py' -v
```

For the currently available series-wide tests:

```bash
python -m unittest discover -s examples -p 'test_*.py'
```

To regenerate the three diagrams (optional):

```bash
python -m pip install matplotlib
python examples/make_voice_security_figures.py
```

## Controls demonstrated

| Topic | Expected behavior | Code |
|---|---|---|
| Identity | Trust a server-established principal, never an STT guess | `start` |
| Tenant boundaries | Deny cross-tenant writes | `prepare_action` |
| Scopes + schema | Require backend scopes, allowlisted operations, exact args | `prepare_action` |
| Origin + STT state | Interim transcripts and RAG documents cannot authorize writes | `prepare_action` |
| Confirmation | Final, direct, action-specific, unexpired approval | `confirm_action` |
| Session changes | Reconnect and end invalidate old approvals | `reconnect`, `end` |
| Idempotency | Same request key and effect yields one demo receipt | `execute_action` |
| Mic vs recording | No recording consent by default; separate choice | `set_recording_consent` |
| Limited retention | Synthetic metadata expiry and revocation | `purge_expired` |
| Audit | Event class, tenant, outcome, timestamp; no raw transcript | `_audit` |

## Explicit limitations

1. `Principal(server_authenticated=True)` is a **stub for trusted server authentication**, not actual OAuth/OIDC, MFA, or voice biometric verification.
2. `origin="direct_user"` and `confirmation="confirm"` are **trusted application classifications** for the demonstration; the LLM cannot self-assert them.
3. This simulator does not authenticate actual speech or verify a human understood the confirmation prompt; production workflows must bind identity and device/session intent appropriately.
4. The in-memory idempotency ledger is **not durable, concurrent, atomic or transactional** and must never be used as an actual booking backend.
5. The `Artifact` class stores **only synthetic metadata**, not recordings. Deletion cannot be claimed for remote providers, caches, backups, or subprocessors based on this code.
6. A maximum of 24 hours in the *demonstration's* metadata retention routine is an arbitrary teaching safeguard, **not a recommended or statutory retention period**.
7. Audit metadata can still be sensitive; production logs need their own access control, purpose, and retention plan.
8. This code does not implement encryption, secure key storage, rate limiting, incident response, DPA review, or regulatory compliance.

## Suggested production exercise

Place a real OIDC authentication layer before the policy engine, validate each tool call with a durable authorization service, store an action digest and idempotency key in one database transaction, and test intentionally malicious RAG contents and replay after reconnection. Independently review provider retention, offsite backups, and user deletion operations.

## References

- https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/principles-gdpr_en
- https://www.rfc-editor.org/rfc/rfc8827.html
