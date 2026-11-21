"""Educational, dependency-free voice architecture timing/decision lab.

Events are milliseconds from *user speech end*, not real measurements.
Run: python examples/architecture_tradeoff_lab.py
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from statistics import median
from typing import Iterable


@dataclass(frozen=True)
class TurnTrace:
    """One turn's observed timestamps relative to user-speech end (ms)."""
    architecture: str
    user_speech_end_ms: int
    audible_start_ms: int
    response_audio_ready_ms: int
    interruption_started_ms: int | None = None
    playback_stopped_ms: int | None = None

    def __post_init__(self) -> None:
        if self.architecture not in {"cascaded", "realtime", "hybrid"}:
            raise ValueError("Unknown architecture")
        if min(self.user_speech_end_ms, self.audible_start_ms, self.response_audio_ready_ms) < 0:
            raise ValueError("timestamps must be nonnegative")
        if not (self.user_speech_end_ms <= self.response_audio_ready_ms <= self.audible_start_ms):
            raise ValueError("Audio must be ready before audible playback begins")
        if (self.interruption_started_ms is None) != (self.playback_stopped_ms is None):
            raise ValueError("Provide both interruption and playback stop timestamps")
        if self.interruption_started_ms is not None:
            if self.interruption_started_ms < 0 or self.playback_stopped_ms < self.interruption_started_ms:
                raise ValueError("Stop cannot precede interruption")

    @property
    def response_latency_ms(self) -> int:
        """End-of-user-speech to first *audible* agent audio."""
        return self.audible_start_ms - self.user_speech_end_ms

    @property
    def playback_delay_ms(self) -> int:
        """Ready first audio to actually audible first audio."""
        return self.audible_start_ms - self.response_audio_ready_ms

    @property
    def interruption_stop_latency_ms(self) -> int | None:
        if self.interruption_started_ms is None:
            return None
        assert self.playback_stopped_ms is not None
        return self.playback_stopped_ms - self.interruption_started_ms


def nearest_rank_percentile(values: Iterable[int], percentile: int) -> int:
    """Nearest-rank percentile; intentionally simple and defined for teaching."""
    data = sorted(values)
    if not data or not (0 < percentile <= 100):
        raise ValueError("Nonempty values and percentile in (0, 100] required")
    return data[ceil(percentile / 100 * len(data)) - 1]


def summarize(traces: Iterable[TurnTrace]) -> dict[str, dict[str, float | int]]:
    groups: dict[str, list[TurnTrace]] = {}
    for trace in traces:
        groups.setdefault(trace.architecture, []).append(trace)
    result: dict[str, dict[str, float | int]] = {}
    for architecture, turns in sorted(groups.items()):
        latencies = [t.response_latency_ms for t in turns]
        interruptions = [t.interruption_stop_latency_ms for t in turns if t.interruption_stop_latency_ms is not None]
        row: dict[str, float | int] = {
            "turns": len(turns),
            "response_p50_ms": median(latencies),
            "response_p95_ms": nearest_rank_percentile(latencies, 95),
            "playback_delay_p50_ms": median(t.playback_delay_ms for t in turns),
        }
        if interruptions:
            row["interruption_stop_p95_ms"] = nearest_rank_percentile(interruptions, 95)
        result[architecture] = row
    return result


def decision_hints(*, exact_wording: bool, live_captions: bool, nuanced_voice_input: bool, simple_provider_setup: bool) -> list[str]:
    """Qualitative decision cues—not model quality or speed predictions."""
    hints: list[str] = []
    if exact_wording or live_captions:
        hints.append("Consider cascaded STT-LLM-TTS or a hybrid with separate STT/TTS.")
    if nuanced_voice_input:
        hints.append("Evaluate a speech-native realtime model for prosody and voice cues.")
    if simple_provider_setup:
        hints.append("A single-provider realtime model may simplify setup, but verify constraints.")
    if not hints:
        hints.append("Prototype both paths; benchmark your actual languages, devices, and networks.")
    return hints


if __name__ == "__main__":
    # SYNTHETIC values only, from an invented illustrative timeline.
    demo = [
        TurnTrace("cascaded", 0, 780, 700, interruption_started_ms=2200, playback_stopped_ms=2310),
        TurnTrace("cascaded", 0, 845, 765),
        TurnTrace("realtime", 0, 450, 380, interruption_started_ms=1400, playback_stopped_ms=1470),
        TurnTrace("realtime", 0, 510, 435),
    ]
    print("SYNTHETIC ONLY — not provider performance data")
    for arch, metrics in summarize(demo).items():
        print(arch, metrics)
    print("Decision hints:")
    for hint in decision_hints(exact_wording=True, live_captions=True, nuanced_voice_input=False, simple_provider_setup=False):
        print("-", hint)
