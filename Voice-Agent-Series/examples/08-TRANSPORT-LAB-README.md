# Article 08 — Transport lab / مختبر نقل الصوت

## What this lab is / ما الذي يقدمه؟

Two distinct exercises:

1. **Offline deterministic simulation:** `transport_network_lab.py` uses a synthetic packet trace to illustrate interarrival variation, out-of-order arrival, missing/duplicate packets, and raw PCM size. It is not a real transport benchmark.
2. **Local microphone → WebSocket server → browser speaker:** `ws_voice_demo/` runs a real binary frame loopback with a Python server and an AudioWorklet. It does not use WebRTC, STT, TTS, or LLM. You can hear your microphone returned through your headphones.

## Requirements

- Python 3.10+ (Python 3.11+ recommended), `pip` available.
- Modern Chromium/Firefox browser supporting AudioWorklet and `getUserMedia`.
- Microphone and **headphones** (avoid feedback).
- Offline packet lab only uses the Python standard library; WebSocket lab needs the `websockets` package.

## A. Offline simulation

From the `Voice-Agent-Series/` folder:

```bash
python examples/transport_network_lab.py
python -m unittest discover -s examples -p 'test_*.py' -v
```

Output from the current synthetic example (not actual network performance):

```text
unique=5, missing=1, duplicates=0, reordered=1
observed loss=16.67%; smoothed transit variation=2.422 ms
48 kHz / 32-bit / mono: 1536 kbit/s raw audio
20 ms frame: 3840 bytes
```

## B. Real local WebSocket audio loopback

Terminal #1:

```bash
python -m pip install -r examples/ws_voice_demo/requirements.txt
python examples/ws_voice_demo/server.py
```

Terminal #2:

```bash
python -m http.server 8008 --bind 127.0.0.1 --directory examples/ws_voice_demo
```

Open `http://127.0.0.1:8008` on the same computer. Start and allow mic access. Speak softly into the mic while wearing headphones. The browser samples at the `AudioContext` sample rate, packages ~20 ms of mono Float32 as an `ArrayBuffer`, sends it as a binary WebSocket frame, and receives the exact frame back from the server. The client queues a small amount of samples for audio playback. Stop closes the session and microphone.

**Safety:** This is bound to `127.0.0.1`, uses an allowlist for the browser `Origin`, disables compression, limits frame sizes and queues, and stores no audio. `ws://` is acceptable for this **localhost exercise only**; a real deployment needs WSS, user authentication, monitoring, rate limits, and an entirely different security review. Do not expose the demo directly to the internet.

**Limitations:** Local echo is not network transport benchmarking. The sample browser code drops frames if `bufferedAmount` or playback queue grows too high, without packet loss concealment. It has no resampling, audio codec, sequencing protocol, sophisticated jitter buffer, network handover, or automated reconnection. Actual microphone/browser playback was not exercised in the authoring environment.

## C. Inspect a real WebRTC transport

Use the working Pipecat project from Article 07 to start a real WebRTC session. In the connected browser client, retrieve an actual `RTCPeerConnection` and inspect its `getStats()` results for `inbound-rtp` audio statistics and the selected candidate pair. The snippets in the article are illustrative because client SDKs expose the peer connection differently.

## D. Regenerate article diagrams

```bash
python -m pip install matplotlib
python examples/make_transport_figures.py
```

Generated files appear under `assets/`. All diagram times are synthetic and do not represent benchmark data.

## Sources

- [MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [MDN AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Using_AudioWorklet)
- [MDN WebRTC connectivity](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Connectivity)
- [Pipecat transports](https://docs.pipecat.ai/pipecat/learn/transports)
- [websockets 16.x server API](https://websockets.readthedocs.io/en/16.1/reference/asyncio/server.html)
