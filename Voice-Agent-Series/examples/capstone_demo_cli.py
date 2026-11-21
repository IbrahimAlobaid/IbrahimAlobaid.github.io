"""No-network demo showing why a trusted UI action must authorize commits."""
from __future__ import annotations
import json
from capstone_domain import DemoBookingService


def main():
    service = DemoBookingService(clock=lambda: 10.0)
    service.create_session("demo", "session-A", "user-A")
    print("FAQ:", json.dumps(service.knowledge("policy"), ensure_ascii=False))
    print("SLOTS:", json.dumps(service.list_slots("2026-12-02"), ensure_ascii=False))
    print("PROPOSAL:", json.dumps(service.propose("demo", "session-A", "demo-101")))
    # This simulates a trusted, authenticated UI action. NO real authentication.
    trusted = service.demo_trusted_approval_details("demo", "session-A")
    print("TRUSTED SIMULATED ACTION:", service.confirm_from_trusted_ui(**trusted))
    # The real application must implement login, tenant authorization, CSRF
    # protections, durable idempotency and external booking API integration.


if __name__ == "__main__":
    main()
