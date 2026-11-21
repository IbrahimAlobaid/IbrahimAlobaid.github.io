"""Article 14 — offline demonstration of voice-agent application policy boundaries.

This is educational code, NOT an authentication, encryption, audit, consent-law,
or production storage solution. Every principal is assumed to be established by
trusted server authentication; speech cannot grant server permissions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable
import hashlib
import json
import secrets
import time


class PolicyDenied(ValueError):
    """A server-side policy rejects this attempted operation."""


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    user_id: str
    scopes: frozenset[str]
    server_authenticated: bool = True


@dataclass
class Session:
    session_id: str
    principal: Principal
    generation: int = 1
    active: bool = True
    recording_consent: bool = False


@dataclass
class PendingAction:
    intent_id: str
    session_id: str
    tenant_id: str
    user_id: str
    generation: int
    operation: str
    parameters: dict
    digest: str
    expires_at: float
    approved: bool = False


@dataclass(frozen=True)
class Receipt:
    receipt_id: str
    intent_id: str
    tenant_id: str
    operation: str
    effect_digest: str


@dataclass
class Artifact:
    """Metadata only: no raw audio/transcript is stored in this lab."""
    artifact_id: str
    session_id: str
    created_at: float
    retention_seconds: float
    kind: str


class VoiceSecurityPolicyLab:
    """In-memory, single-process simulation of trust boundaries and safeguards.

    A real system also needs a durable transactional idempotency ledger, actual
    identity verification, per-resource authorization, tested encryption,
    provider-level deletion, key rotation and an appropriate legal process.
    """

    def __init__(self, now: Callable[[], float] = time.time):
        self.now = now
        self.sessions: dict[str, Session] = {}
        self.pending: dict[str, PendingAction] = {}
        self.receipts: dict[tuple[str, str], Receipt] = {}
        self.idempotency_digests: dict[tuple[str, str], str] = {}
        self.artifacts: dict[str, Artifact] = {}
        self.audit: list[dict[str, str | float]] = []

    def _audit(self, category: str, tenant_id: str, outcome: str) -> None:
        # No raw speech, name, transcript, prompt, tool arguments or API tokens.
        self.audit.append({"event": category, "tenant": tenant_id, "outcome": outcome, "at": self.now()})

    def start(self, principal: Principal) -> Session:
        if not principal.server_authenticated or not principal.user_id or not principal.tenant_id:
            raise PolicyDenied("trusted server authentication required")
        sess = Session(secrets.token_hex(10), principal)
        self.sessions[sess.session_id] = sess
        self._audit("session_start", principal.tenant_id, "accepted")
        return sess

    def session(self, session_id: str) -> Session:
        sess = self.sessions.get(session_id)
        if sess is None or not sess.active:
            raise PolicyDenied("unknown or inactive session")
        return sess

    def set_recording_consent(self, session_id: str, allow: bool, *, explicit_user_choice: bool) -> None:
        sess = self.session(session_id)
        if not explicit_user_choice or type(allow) is not bool:
            raise PolicyDenied("separate, explicit recording choice required")
        sess.recording_consent = allow
        if not allow:
            # Only local demo metadata. Production deletion must cover all stores and processors.
            self.artifacts = {k: v for k, v in self.artifacts.items() if v.session_id != session_id}
        self._audit("recording_consent", sess.principal.tenant_id, "granted" if allow else "revoked")

    def register_recording_metadata(self, session_id: str, *, retention_seconds: float) -> str:
        sess = self.session(session_id)
        if not sess.recording_consent:
            raise PolicyDenied("recording consent missing")
        if not (0 < retention_seconds <= 86400):
            raise PolicyDenied("demonstration retention window must be within 24 hours")
        aid = secrets.token_hex(8)
        self.artifacts[aid] = Artifact(aid, session_id, self.now(), retention_seconds, "recording_metadata")
        self._audit("artifact_metadata", sess.principal.tenant_id, "registered")
        return aid

    def purge_expired(self) -> int:
        expired = [aid for aid, item in self.artifacts.items()
                   if self.now() >= item.created_at + item.retention_seconds]
        for aid in expired:
            del self.artifacts[aid]
        return len(expired)

    @staticmethod
    def _fingerprint(tenant: str, user: str, operation: str, parameters: dict) -> str:
        blob = json.dumps({"tenant": tenant, "user": user, "op": operation, "args": parameters},
                          ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def prepare_action(self, session_id: str, *, target_tenant: str, operation: str,
                       parameters: dict, transcript_state: str, origin: str,
                       ttl_seconds: float = 60) -> PendingAction:
        sess = self.session(session_id)
        p = sess.principal
        if target_tenant != p.tenant_id:
            self._audit("tool_policy", p.tenant_id, "denied_tenant")
            raise PolicyDenied("cross-tenant access denied")
        if transcript_state != "final" or origin != "direct_user":
            raise PolicyDenied("interim transcript or untrusted retrieved text cannot authorize a write")
        if operation not in {"appointment.cancel", "appointment.create"}:
            raise PolicyDenied("operation is not on the allowlist")
        if "appointment:write" not in p.scopes:
            raise PolicyDenied("missing server-issued scope")
        if not isinstance(parameters, dict) or set(parameters) != {"appointment_id"}:
            raise PolicyDenied("invalid parameter schema")
        if not isinstance(parameters["appointment_id"], str) or not parameters["appointment_id"].strip():
            raise PolicyDenied("appointment_id must be a nonempty string")
        if not (0 < ttl_seconds <= 300):
            raise PolicyDenied("invalid approval lifetime")
        digest = self._fingerprint(p.tenant_id, p.user_id, operation, parameters)
        intent = PendingAction(secrets.token_hex(10), session_id, p.tenant_id, p.user_id,
                               sess.generation, operation, dict(parameters), digest,
                               self.now() + ttl_seconds)
        self.pending[intent.intent_id] = intent
        self._audit("action_prepare", p.tenant_id, "awaiting_confirmation")
        return intent

    def confirm_action(self, session_id: str, intent_id: str, *, confirmation: str,
                       transcript_state: str, origin: str) -> None:
        sess = self.session(session_id)
        intent = self.pending.get(intent_id)
        if not intent or intent.session_id != session_id:
            raise PolicyDenied("action does not belong to this session")
        if intent.generation != sess.generation or self.now() >= intent.expires_at:
            raise PolicyDenied("stale or expired approval")
        if transcript_state != "final" or origin != "direct_user" or confirmation != "confirm":
            raise PolicyDenied("final explicit user confirmation required")
        intent.approved = True
        self._audit("action_approval", sess.principal.tenant_id, "accepted")

    def execute_action(self, session_id: str, intent_id: str, *, idempotency_key: str) -> Receipt:
        sess = self.session(session_id)
        intent = self.pending.get(intent_id)
        if not intent or intent.session_id != session_id:
            raise PolicyDenied("missing or foreign intent")
        if intent.generation != sess.generation or self.now() >= intent.expires_at or not intent.approved:
            raise PolicyDenied("cannot execute stale, expired or unapproved action")
        if not idempotency_key or len(idempotency_key) > 128:
            raise PolicyDenied("valid idempotency key required")
        key = (sess.principal.tenant_id, idempotency_key)
        if key in self.receipts:
            if self.idempotency_digests[key] != intent.digest:
                raise PolicyDenied("idempotency key reused for different effect")
            return self.receipts[key]
        # Demo receipt only. No external call; not an atomic transaction/storage implementation.
        receipt = Receipt(secrets.token_hex(8), intent.intent_id, intent.tenant_id,
                          intent.operation, intent.digest)
        self.receipts[key] = receipt
        self.idempotency_digests[key] = intent.digest
        self._audit("action_execution", sess.principal.tenant_id, "simulated_once")
        return receipt

    def reconnect(self, session_id: str) -> None:
        sess = self.session(session_id)
        sess.generation += 1
        for intent in self.pending.values():
            if intent.session_id == session_id:
                intent.approved = False
        self._audit("session_reconnect", sess.principal.tenant_id, "prior_approvals_invalidated")

    def end(self, session_id: str) -> None:
        sess = self.session(session_id)
        sess.active = False
        for intent in self.pending.values():
            if intent.session_id == session_id:
                intent.approved = False
        self._audit("session_end", sess.principal.tenant_id, "ended")


def demo() -> None:
    engine = VoiceSecurityPolicyLab()
    # Principal is *trusted backend context*, NOT something supplied by STT/LLM.
    s = engine.start(Principal("clinic-demo", "user-demo", frozenset({"appointment:write"})))
    print("Recording consent by default:", s.recording_consent)
    request = engine.prepare_action(s.session_id, target_tenant="clinic-demo",
                                    operation="appointment.cancel", parameters={"appointment_id": "A-001"},
                                    transcript_state="final", origin="direct_user")
    print("Approval required:", request.approved is False)
    engine.confirm_action(s.session_id, request.intent_id, confirmation="confirm",
                          transcript_state="final", origin="direct_user")
    receipt = engine.execute_action(s.session_id, request.intent_id, idempotency_key="demo-cancel-A001")
    retry = engine.execute_action(s.session_id, request.intent_id, idempotency_key="demo-cancel-A001")
    print("Simulated action idempotent:", receipt == retry)
    print("Audit metadata only:", engine.audit)


if __name__ == "__main__":
    demo()
