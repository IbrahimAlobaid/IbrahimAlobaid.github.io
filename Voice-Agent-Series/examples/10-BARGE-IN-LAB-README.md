# Article 10 lab — Interruptions, Barge-In & Playback State

## Goals

Learn to coordinate generated audio, client buffering, playback acknowledgement, candidate pauses, confirmed cancellation, stale chunks, and conversation truncation. The code is deliberately **provider independent** except for an illustrative dictionary builder for OpenAI Realtime WebSocket.

## Requirements

Python 3.10+; standard library only for the lab and tests. Optional: `Pillow` to regenerate article diagrams.

## Run

From `Voice-Agent-Series/examples`:

```bash
python interruption_playback_lab.py
python -m unittest test_interruption_playback_lab -v
python -m unittest discover -s . -p 'test_*.py' -q
```

Regenerate drawings (optional):

```bash
python make_interruption_figures.py
```

## What is simulated

A response `item_demo` has 3600ms generated audio, 3100ms synthesized, 2600ms transmitted, 2400ms buffered, and 1500ms acknowledged as played at the moment of a true interruption.

- Old generation messages get rejected by the `epoch` guard.
- Playback can be paused on *candidate* interruption and resumed after a false positive.
- Only a confirmed interruption invalidates that generation and yields a truncation event template.
- A `played_ms` cursor is accepted from the client/player in the toy lab; no real player is connected.
- Complete **known aligned** caption chunks can be retained as approximate played text. Without alignment, the method returns `None`, never a fabricated exact transcript.

## Known limitations

This code is **not** a drop-in player, WebRTC transport, OpenAI SDK client, Pipecat processor, or thread-safe production coordinator. It assumes an authoritative final playback-stop acknowledgement, and it does **not** implement actual audio I/O, output-device latency estimation, speech detection, network failures, retransmits, tool cancellation, remote API errors, or privacy and access controls. Neither generated nor player-reported audio proves human perception. Do not use simulated counts as a vendor benchmark.

## Production integration checklist

1. Use stable `item_id`, content index and response-generation IDs.
2. Instrument the real client output layer and provide per-item monotonic playback position.
3. Stop output rapidly on candidate barge-in; confirm actual user intent.
4. On confirmed interruption, clear queued output and cancel/ignore stale LLM and TTS work.
5. Guard all late packets and acknowledgements with an active epoch.
6. Reconcile remote conversation state through your **specific** provider API.
7. Distinguish cancellable speech generation from external tool side effects.
8. Log timing metrics without storing unnecessary user audio or personal data.
9. Test echo, noisy rooms, backchannels, browser audio latency and loss of connectivity.

## References

- https://developers.openai.com/api/docs/guides/realtime-conversations
- https://docs.livekit.io/agents/logic/turns/
- https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/getOutputTimestamp
