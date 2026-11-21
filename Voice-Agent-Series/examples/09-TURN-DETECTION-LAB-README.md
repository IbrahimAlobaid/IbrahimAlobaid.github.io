# Article 09 lab — VAD, endpointing and turn detection

## Objective

Learn the difference between the **end of a speech segment** and **the end of a conversational turn**, using a tiny deterministic state machine.

**The lab does not contain a trained VAD model.** It consumes synthetic frame-by-frame probabilities. The interruption rule only tests sustained speech; it has no semantic understanding and does not perform echo cancellation.

## Quickstart

Requirements: Python 3.10+; no third-party packages for the lab/tests.

From the root `Voice-Agent-Series` directory:

```bash
python examples/turn_detection_lab.py
python -m unittest discover -s examples -p 'test_turn_detection_lab.py' -v
python -m unittest discover -s examples -p 'test_*.py' -v
```

Expected example timeline:

```text
  100 ms  turn_started
  100 ms  speech_started
  840 ms  speech_stopped
 1100 ms  speech_started
 1740 ms  speech_stopped
 2200 ms  turn_ended
```

The 400 ms pause splits acoustic segments but does **not** end the turn when endpointing is configured to 700 ms.

## Experiment with the timeout

```bash
cd examples
python - <<'PY'
from turn_detection_lab import TurnConfig, frames, run_probabilities
signal = frames(600, .96) + frames(400, .01) + frames(500, .96) + frames(900, .01)
for window in (300, 700):
    cfg = TurnConfig(endpoint_ms=window, min_silence_ms=240)
    print('Endpoint window', window, 'ms')
    print([(e.at_ms, e.name) for e in run_probabilities(signal, cfg)])
PY
```

For 300 ms, the pause can prematurely end the turn and start a second turn; for 700 ms, it remains a single turn. Both are simplistic, context-blind behaviors.

## Illustrations

To regenerate the two charts:

```bash
python -m pip install matplotlib numpy
python examples/make_turn_detection_figures.py
```

Files produced under `assets/`:

- `turn-detection-timeline.png` (synthetic speech probability, short pause, turn boundary)
- `turn-detection-tradeoff.png` (entirely illustrative numbers, not provider benchmarks)

## From lab to real audio

A production implementation needs a real audio capture and frame pipeline, an actual VAD/turn model, streaming STT when applicable, echo suppression, transport/session management, realistic barge-in handling, and playback acknowledgements. Read [Pipecat Speech Input](https://docs.pipecat.ai/pipecat/learn/speech-input) and [LiveKit Turns](https://docs.livekit.io/agents/logic/turns/).

**Safety:** don't capture or persist users' microphone audio without appropriate consent and access controls. Never use the fake-probability lab as a clinical or authentication decision system.
