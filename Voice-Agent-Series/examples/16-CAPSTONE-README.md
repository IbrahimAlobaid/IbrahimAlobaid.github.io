# Article 16 — Voice Agent Capstone: Practical Instructions

These files belong to the Obsidian `Voice-Agent-Series` folder and support both Arabic and English Article 16 notes.

## Proven offline demo (no account, API, audio hardware or network required)

```bash
cd Voice-Agent-Series/examples
python capstone_demo_cli.py
python -m unittest -v test_capstone_domain.py
```

`capstone_demo_cli.py` prints synthetic FAQ data, synthetic availability, a pending proposal and a simulated locally authorized confirmation. It does NOT book an actual appointment.

`test_capstone_domain.py` checks tenant/session isolation, identity mismatch, expiry, cancellation, reconnect generation, invalid tokens, idempotent retries and more. The domain layer depends only on the Python standard library.

## Optional browser voice demo

The Python example `capstone_voice_agent.py` assembles Deepgram STT + OpenAI LLM + Cartesia TTS with Pipecat and Silero VAD. It is adapted from **current official Pipecat 1.x getting-started examples**, as reviewed on 2026-11-21. APIs are subject to changes.

1. Install Python 3.11+ (prefer 3.12) and make an isolated virtual environment.
2. Follow https://docs.pipecat.ai/pipecat/get-started/quickstart for the appropriate Pipecat and transport extras. A *suggested* command is:

   ```bash
   pip install 'pipecat-ai[deepgram,openai,cartesia,silero,runner,webrtc]' python-dotenv loguru
   ```

3. `cp capstone-agent.env.example .env` (or copy manually on Windows) and put valid keys only in local `.env`.
4. `python capstone_voice_agent.py`
5. Follow the runner URL for a browser. Common default: http://localhost:7860/client/

No live Pipecat/audio session was executed in this environment. Syntax compilation and domain tests are not proof of runtime provider compatibility. We did not test microphone access, WebRTC, interruptions, transport encryption, reconnect under packet loss, or audio playback receipts.

## Tool security contract

Only `read_faq`, `find_slots`, and `propose_slot` are registered with the LLM. No tool exposes the proposal's approval token or can commit a booking. `confirm_from_trusted_ui()` is a **domain-level test method** that assumes an independent, authenticated application has already authorized the action; that application does not exist in this package. The `demo_trusted_approval_details()` helper exists for local tests only and must never be exposed to any client or LLM.

## Minimum changes required for real production

- Bind tenant and user identity to a verified, server-issued session rather than fixed synthetic IDs.
- Implement authenticated, explicit confirmation in a trusted UI; use CSRF defenses where applicable.
- Use a durable transactional DB with unique constraints and idempotency keys, not process memory.
- Add end-to-end observability that excludes sensitive content by default.
- Implement a real service API with rate limits and scoped credentials.
- Use TLS/HTTPS, appropriately configured WebRTC/STUN/TURN, managed secrets and safe rotation.
- Run representative audio / multilingual / reconnection / provider failure tests in staging.
- Add a real evaluation and release-gating suite with rollback.

## Image assets

- `assets/capstone-voice-agent-cover.png`: AI-generated series cover (conceptual)
- `assets/capstone-architecture.png`: architecture illustration
- `assets/capstone-safe-actions.png`: domain state and trusted approval
- `assets/capstone-release-readiness.png`: tested/unverified boundary
- `examples/make_capstone_figures.py`: reproducible diagram generator; needs matplotlib

## Verification

```bash
python -m py_compile capstone_domain.py capstone_demo_cli.py capstone_voice_agent.py
python -m unittest -q test_capstone_domain.py
```

This last module must be syntax-valid even if dependencies are not installed; do not confuse syntax checks with imports or runtime tests.

## References

- https://github.com/pipecat-ai/pipecat/blob/main/examples/getting-started/06-voice-agent.py
- https://github.com/pipecat-ai/pipecat/blob/main/examples/getting-started/07-function-calling.py
- https://docs.pipecat.ai/pipecat/get-started/quickstart
- https://docs.pipecat.ai/client/concepts/choosing-a-transport
