# Article 12 — Robust Voice AI in the Wild: Lab Guide

**Educational simulation only.** This is a **decision-policy and reconnection-state lab**, not real audio processing. No STT/VAD model, diarizer, WebRTC client, live microphone, cloud service, identity verification, or action-service API is included.

## Run (Python 3.10+, no external libraries)

From the root `Voice-Agent-Series` directory:

```bash
python examples/voice_robustness_lab.py
python examples/voice_robustness_lab.py --json
python -m unittest discover -s examples -p 'test_voice_robustness_lab.py' -v
python -m unittest discover -s examples -p 'test_*.py' -q
```

To rebuild the three illustrative figures:

```bash
python -m pip install numpy matplotlib
python examples/make_robustness_figures.py
```

## Design and files

- `voice_robustness_lab.py` — independent evidence-based decision policy, Unicode-aware *minimal* token normalization and edit distance, synthetic RMS diagnostics, capped retry delays, and reconnect-generation protection.
- `12-synthetic-resilience-cases.jsonl` — 18 intentionally artificial cases: quiet, noise, echo, overlap, accent, code-switch, disconnect, silence, and critical details. All transcript text is invented.
- `test_voice_robustness_lab.py` — 36 focused tests verifying branch decisions, basic errors, replay protection, and fixture summaries.
- `make_robustness_figures.py` — three reproducible explanatory figures.

## Interpret results correctly

The local policy is deliberately conservative: it waits when text is partial, ignores input not confirmed to be directed at the user, asks to repeat unintelligible speech, and requires explicit confirmation for selected sensitive details. On network failure it holds the session. These flags are **supplied by the test file**; they are not computed by real acoustic algorithms. Real-world systems must define how those flags are obtained, calibrated, audited, and validated.

Expected excerpt:

```text
SYNTHETIC EDUCATIONAL DATA — not a production benchmark
Cases: 18 | policy expectations matched: 18
accent               n= 2 WER=0.143
code-switch          n= 2 WER=0.222
noise                n= 3 WER=0.583
quiet                n= 2 WER=0.0
```

The `policy_case_match` score checks **agreement with the expected decisions authored in the fixture**, NOT real accuracy. The simplistic WER normalizes punctuation and case and splits on spaces; it lacks a robust Arabic word-segmentation/normalization policy. The dataset is too small and artificial for any comparison of STT products, languages, or noise filters. A WER above 1.0 can be valid when the hypothesis has enough insertions. Empty reference strings return a null WER for aggregate subgroups.

`snr_db(speech_rms, noise_rms)` assumes the two RMS values are separately known; it cannot blindly estimate SNR from one mixed recording. The clipping metric is a coarse floating-PCM threshold indicator. `retry_delays` is deterministic for testing; add bounded randomized jitter in real distributed systems to prevent synchronized reconnect storms.

## Reconnections and external actions

`RecoveryState` is an in-memory demonstration of rejecting duplicate or stale-generation events and invalidating pending confirmations on disconnect. It has **no persistence, authentication, concurrency control, or real-world side effects**. In production, use a durable action state and idempotency keys supported by the **external action service**, look up the authoritative status of any ambiguous previous action, and request a new confirmation when needed. Do not treat a fresh transport connection as evidence that a transaction was not previously completed.

## Reader exercises

1. Add another code-switching case and document your normalization policy.
2. Add a background-speaker case and ensure the agent does not interpret the utterance as user intent.
3. Add a disconnected critical-action case and ensure it never yields `respond_to_user`.
4. Simulate delayed delivery of a packet from the previous session generation.
5. Replace synthetic evidence with explicitly consented and representative real acoustic data in **your own environment**, then evaluate actual recognition and quality metrics separately.

## References

- [MDN audio capture constraints](https://developer.mozilla.org/en-US/docs/Web/API/Media_Capture_and_Streams_API/Constraints)
- [LiveKit turn-taking tuning](https://docs.livekit.io/agents/logic/turns/tuning/)
- [LiveKit noise and echo cancellation](https://docs.livekit.io/transport/media/noise-cancellation/)
- [OpenAI realtime transcription](https://developers.openai.com/api/docs/guides/realtime-transcription)
- [MDN restartIce](https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/restartIce)
