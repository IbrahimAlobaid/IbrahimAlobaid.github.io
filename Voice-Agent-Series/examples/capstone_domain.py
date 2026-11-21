"""Article 16: local, synthetic reference domain for a voice agent.

No external actions are performed. A trusted application must authenticate the
user and deliver an approval token out-of-band; an LLM tool cannot commit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from secrets import token_hex, compare_digest
from hashlib import sha256
from threading import RLock
from typing import Callable


class DomainError(ValueError):
    """Safe, business-readable error without secrets or PII."""


@dataclass(frozen=True)
class DemoSlot:
    id: str
    start_iso: str
    service: str


DEMO_SLOTS = (
    DemoSlot("demo-101", "2026-12-02T10:00:00+03:00", "consultation"),
    DemoSlot("demo-102", "2026-12-02T11:00:00+03:00", "consultation"),
    DemoSlot("demo-103", "2026-12-03T15:00:00+03:00", "consultation"),
)

KNOWLEDGE = {
    "hours": "Demo office hours: Monday to Friday, 09:00–17:00 (UTC+03).",
    "location": "This is a fictitious remote service; there is no real office.",
    "privacy": "The demo keeps appointment state in memory only; no live customer data is collected by the domain module.",
    "policy": "A proposal is not a booking. Final confirmation must come from a separately authenticated application action.",
}


@dataclass
class Pending:
    request_id: str
    approval_token: str
    slot_id: str
    generation: int
    revision: int
    expires_at: float


@dataclass
class Session:
    tenant_id: str
    session_id: str
    authenticated_subject: str
    generation: int = 0
    revision: int = 0
    pending: Pending | None = None
    committed_request_ids: set[str] = field(default_factory=set)


class DemoBookingService:
    """Multi-session demo; deliberately not durable, distributed, or production auth."""

    def __init__(self, clock: Callable[[], float], ttl_seconds: int = 90):
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self.clock = clock
        self.ttl_seconds = ttl_seconds
        self.sessions: dict[tuple[str, str], Session] = {}
        self.bookings: dict[tuple[str, str], dict[str, str]] = {}
        self.receipt_proofs: dict[tuple[str, str], tuple[str, int, int]] = {}
        self._lock = RLock()

    def create_session(self, tenant: str, session_id: str, subject: str) -> Session:
        if not all((tenant, session_id, subject)):
            raise DomainError("An authenticated tenant, session and subject are required")
        key = tenant, session_id
        with self._lock:
            if key in self.sessions:
                raise DomainError("Session already exists")
            session = Session(tenant, session_id, subject)
            self.sessions[key] = session
            return session

    def _session(self, tenant: str, session_id: str) -> Session:
        session = self.sessions.get((tenant, session_id))
        if session is None:
            raise DomainError("Unknown session")
        return session

    def knowledge(self, topic: str) -> dict[str, str]:
        key = topic.strip().lower()
        if key not in KNOWLEDGE:
            return {"status": "not_found", "message": "Topic not found; ask a clarifying question"}
        return {"status": "found", "answer": KNOWLEDGE[key], "source": f"demo-policy:{key}"}

    def list_slots(self, day_iso: str) -> list[dict[str, str]]:
        try:
            day = datetime.strptime(day_iso, "%Y-%m-%d").date()
        except ValueError as exc:
            raise DomainError("Day must be YYYY-MM-DD") from exc
        return [
            {"slot_id": x.id, "time": x.start_iso, "service": x.service}
            for x in DEMO_SLOTS if datetime.fromisoformat(x.start_iso).date() == day
        ]

    def propose(self, tenant: str, session_id: str, slot_id: str) -> dict[str, str | int]:
        """No external writes and approval token never enters LLM tool output."""
        with self._lock:
            session = self._session(tenant, session_id)
            if slot_id not in {x.id for x in DEMO_SLOTS}:
                raise DomainError("Unknown demonstration slot")
            if session.pending:
                raise DomainError("Resolve or cancel the existing proposal first")
            session.revision += 1
            p = Pending(
                request_id=token_hex(8),
                approval_token=token_hex(16),
                slot_id=slot_id,
                generation=session.generation,
                revision=session.revision,
                expires_at=self.clock() + self.ttl_seconds,
            )
            session.pending = p
            return {
                "status": "awaiting_trusted_ui_confirmation",
                "request_id": p.request_id,
                "slot_id": slot_id,
                "revision": session.revision,
                "message": "Proposed only. No booking has been made.",
            }

    def cancel(self, tenant: str, session_id: str) -> None:
        with self._lock:
            session = self._session(tenant, session_id)
            session.pending = None
            session.revision += 1

    def reconnect(self, tenant: str, session_id: str) -> None:
        with self._lock:
            session = self._session(tenant, session_id)
            session.pending = None
            session.generation += 1
            session.revision += 1

    def confirm_from_trusted_ui(
        self,
        *, tenant: str, session_id: str, authenticated_subject: str,
        request_id: str, approval_token: str, generation: int, revision: int,
    ) -> dict[str, str]:
        """Must only be called from a separately authenticated application endpoint.

        Trusted UI integration is intentionally not implemented in this pack.
        This method only enforces domain preconditions after authentication.
        """
        with self._lock:
            session = self._session(tenant, session_id)
            if session.authenticated_subject != authenticated_subject:
                raise DomainError("Subject is not authorized for this session")
            # Deduplicate successful retries, and never change the slot.
            key = (tenant, request_id)
            if request_id in session.committed_request_ids and key in self.bookings:
                proof = self.receipt_proofs[key]
                candidate = sha256(approval_token.encode("utf-8")).hexdigest()
                if not (compare_digest(proof[0], candidate) and proof[1:] == (generation, revision)):
                    raise DomainError("Invalid retry proof")
                return dict(self.bookings[key])
            p = session.pending
            if p is None:
                raise DomainError("No active proposal")
            if not (p.request_id == request_id and p.approval_token == approval_token):
                raise DomainError("Invalid approval details")
            if (p.generation, p.revision) != (generation, revision):
                raise DomainError("Stale proposal")
            if (session.generation, session.revision) != (generation, revision):
                raise DomainError("Session state changed")
            if self.clock() >= p.expires_at:
                session.pending = None
                raise DomainError("Approval expired")
            result = {"status": "simulated_committed", "booking_id": token_hex(8), "slot_id": p.slot_id}
            self.bookings[key] = result
            self.receipt_proofs[key] = (sha256(approval_token.encode("utf-8")).hexdigest(), generation, revision)
            session.committed_request_ids.add(request_id)
            session.pending = None
            return dict(result)

    def demo_trusted_approval_details(self, tenant: str, session_id: str) -> dict[str, str | int]:
        """For a LOCAL TEST HARNESS only. Never expose this via LLM tools or API."""
        with self._lock:
            session = self._session(tenant, session_id)
            if session.pending is None:
                raise DomainError("No active proposal")
            p = session.pending
            return {
                "tenant": tenant, "session_id": session_id,
                "authenticated_subject": session.authenticated_subject,
                "request_id": p.request_id, "approval_token": p.approval_token,
                "generation": p.generation, "revision": p.revision,
            }
