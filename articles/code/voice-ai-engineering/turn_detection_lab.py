"""Deterministic teaching lab: acoustic VAD, utterance pause and turn endpointing.

Run: python examples/turn_detection_lab.py
No external packages, microphones, STT or real VAD model are used.
Each input value is a synthetic speech probability for one frame.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TurnConfig:
    frame_ms: int = 20
    start_threshold: float = 0.65
    continue_threshold: float = 0.35
    min_speech_ms: int = 100
    min_silence_ms: int = 240
    endpoint_ms: int = 700
    min_interrupt_ms: int = 200

    def __post_init__(self):
        if self.frame_ms <= 0:
            raise ValueError('frame_ms must be positive')
        if not 0 < self.continue_threshold < self.start_threshold < 1:
            raise ValueError('thresholds must satisfy 0 < continue < start < 1')
        if min(self.min_speech_ms, self.min_silence_ms,
               self.endpoint_ms, self.min_interrupt_ms) <= 0:
            raise ValueError('all durations must be positive')
        if self.endpoint_ms < self.min_silence_ms:
            raise ValueError('endpoint_ms must be >= min_silence_ms')


@dataclass(frozen=True)
class TurnEvent:
    at_ms: int
    name: str


class AcousticTurnGate:
    """An educational *acoustic-only* state machine, not an ML turn detector.

    Events: turn_started, speech_started, speech_stopped,
            interrupted_assistant, turn_ended.
    A segment may stop and restart inside one turn. Endpointing starts from
    the first low-probability frame rather than waiting another full timeout
    after the segment-stopped event.
    """
    def __init__(self, cfg: TurnConfig | None = None):
        self.cfg = cfg or TurnConfig()
        self.now_ms = 0
        self.turn_open = False
        self.segment_active = False
        self.candidate_speech_ms = 0
        self.silence_ms = 0
        self.assistant_playing = False
        self.interrupted_this_turn = False
        self.segment_speech_ms = 0

    def set_assistant_playing(self, playing: bool) -> None:
        self.assistant_playing = playing
        if not playing:
            self.interrupted_this_turn = False

    def _open_segment(self, out: list[TurnEvent]) -> None:
        if not self.turn_open:
            self.turn_open = True
            out.append(TurnEvent(self.now_ms, 'turn_started'))
        self.segment_active = True
        self.silence_ms = 0
        self.segment_speech_ms = self.candidate_speech_ms
        self.candidate_speech_ms = 0
        out.append(TurnEvent(self.now_ms, 'speech_started'))

    def process(self, probability: float) -> list[TurnEvent]:
        if not 0 <= probability <= 1:
            raise ValueError('speech probability must be between 0 and 1')
        self.now_ms += self.cfg.frame_ms
        events: list[TurnEvent] = []
        cfg = self.cfg
        if self.segment_active:
            if probability >= cfg.continue_threshold:
                self.silence_ms = 0
                self.segment_speech_ms += cfg.frame_ms
            else:
                self.silence_ms += cfg.frame_ms
                if self.silence_ms >= cfg.min_silence_ms:
                    self.segment_active = False
                    self.segment_speech_ms = 0
                    events.append(TurnEvent(self.now_ms, 'speech_stopped'))
        else:
            if probability >= cfg.start_threshold:
                self.candidate_speech_ms += cfg.frame_ms
                if self.candidate_speech_ms >= cfg.min_speech_ms:
                    self._open_segment(events)
            else:
                self.candidate_speech_ms = 0
                if self.turn_open:
                    # The user did not restart. Measure ongoing pause from
                    # the first low-probability frame of this silent period.
                    self.silence_ms += cfg.frame_ms

        if (self.turn_open and self.segment_active and self.assistant_playing
                and not self.interrupted_this_turn
                and self.segment_speech_ms >= cfg.min_interrupt_ms):
            events.append(TurnEvent(self.now_ms, 'interrupted_assistant'))
            self.interrupted_this_turn = True

        if self.turn_open and not self.segment_active and self.silence_ms >= cfg.endpoint_ms:
            events.append(TurnEvent(self.now_ms, 'turn_ended'))
            self.turn_open = False
            self.silence_ms = 0
            self.candidate_speech_ms = 0
            self.interrupted_this_turn = False
        return events


def run_probabilities(probabilities: Iterable[float], cfg: TurnConfig | None = None,
                      assistant_playing: bool = False) -> list[TurnEvent]:
    detector = AcousticTurnGate(cfg)
    detector.set_assistant_playing(assistant_playing)
    result: list[TurnEvent] = []
    for value in probabilities:
        result.extend(detector.process(value))
    return result


def frames(ms: int, probability: float, frame_ms: int = 20) -> list[float]:
    if ms < 0 or ms % frame_ms:
        raise ValueError('duration must be a nonnegative multiple of frame_ms')
    return [probability] * (ms // frame_ms)


def example_session() -> list[TurnEvent]:
    # Speech, a 400-ms thinking pause, continuation, then a true ending.
    signal = (frames(600, 0.95) + frames(400, 0.03)
              + frames(500, 0.96) + frames(900, 0.02))
    return run_probabilities(signal)


if __name__ == '__main__':
    print('Synthetic example: speech -> thinking pause -> more speech -> end')
    for e in example_session():
        print(f'{e.at_ms:>5} ms  {e.name}')
    print('Educational acoustic-only probabilities; not live audio or a trained VAD.')
