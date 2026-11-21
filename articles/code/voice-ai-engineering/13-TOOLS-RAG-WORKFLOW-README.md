# Article 13 — Tools, RAG & Agent Workflow (offline lab)

## What this lab does

Uses standard-library Python only. Simulates knowledge lookup with source IDs, tenant-scoped appointments, a prepare/approval/commit state machine, cancellation and reconnect invalidation, and in-memory idempotency. It does not use real voice services, models, booking platforms, biometric verification, authentication, or databases.

## Run the example

```bash
cd Voice-Agent-Series/examples
python voice_tools_rag_workflow_lab.py
```

## Run the tests

```bash
python -m unittest test_voice_tools_rag_workflow_lab -v
```

## Regenerate the educational figures

```bash
python -m pip install matplotlib
python make_tools_rag_figures.py
```

The images are written to `../assets/`. All depicted timings and appointments are examples, not measurements or genuine availability.

## Architectural boundaries

* `LocalKnowledgeBase.search`: scoped lexical lookup; this is **not** vector search or a production RAG solution. Retrieved snippets are **data**, never instructions.
* `prepare_booking`: saves an intent, not a booking.
* `confirm_booking`: commits after explicit simulated gateway signals for a final transcript and a verified speaker. These Boolean signals are supplied by test code and do not prove real speaker identity.
* `start`: changes generation and invalidates stale pending intents.
* `idempotency`: keeps results **only in memory** and is **not** thread-safe or crash-safe.

For production, use authenticated identity and per-record authorization, durable idempotency keys with uniqueness constraints and atomic writes, approval expiry, audited tools, backend transaction reconciliation, network timeouts, and voice-session instrumentation. Never use this demo to store or process real appointments.

## Source readings

- https://developers.openai.com/api/docs/guides/function-calling
- https://developers.openai.com/api/docs/guides/retrieval
- https://docs.livekit.io/agents/logic/external-data/
- https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
