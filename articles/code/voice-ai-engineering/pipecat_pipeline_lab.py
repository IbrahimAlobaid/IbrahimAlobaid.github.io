"""Dependency-free timeline lab for Article 07.

This DOES NOT establish a real voice connection or measure any AI provider.
Use synthetic events to understand end-to-end timing and session transitions.
"""

from dataclasses import dataclass, field
from typing import Mapping


class TimelineError(ValueError):
    """An impossible or incomplete session timeline."""


@dataclass
class SessionTimeline:
    """All timestamps are monotonic milliseconds from one session clock."""

    points: dict[str, float] = field(default_factory=dict)

    def mark(self, name: str, time_ms: float) -> None:
        if not name.strip() or time_ms < 0:
            raise TimelineError("Event name and nonnegative time required")
        if name in self.points:
            raise TimelineError(f"Duplicate event: {name}")
        self.points[name] = float(time_ms)

    def interval(self, start: str, end: str) -> float:
        if start not in self.points or end not in self.points:
            raise TimelineError(f"Missing event: {start} or {end}")
        elapsed = self.points[end] - self.points[start]
        if elapsed < 0:
            raise TimelineError(f"Events out of order: {start} > {end}")
        return elapsed

    def response_latency(self) -> float:
        """Time from end of user speech to first audible response."""
        return self.interval("user_speech_end", "first_audio_audible")

    def interrupt_stop_latency(self) -> float:
        """Time from barge-in onset to stopping the audible response."""
        return self.interval("user_interruption", "playback_stopped")


def example_trace() -> SessionTimeline:
    """Illustrative numbers: not a vendor benchmark."""
    timeline = SessionTimeline()
    for event, ms in (
        ("client_connected", 0),
        ("user_speech_start", 1000),
        ("user_speech_end", 2800),
        ("stt_final", 2960),
        ("llm_first_text", 3230),
        ("tts_first_audio_ready", 3530),
        ("first_audio_audible", 3640),
        ("user_interruption", 4090),
        ("playback_stopped", 4180),
        ("client_disconnected", 7000),
    ):
        timeline.mark(event, ms)
    return timeline


if __name__ == "__main__":
    demo = example_trace()
    print("Illustrative timeline — NOT real measurements")
    print(f"Response latency: {demo.response_latency():.0f} ms")
    print(f"Interruption stop latency: {demo.interrupt_stop_latency():.0f} ms")
