"""Provider-independent STT partial/final event handling and basic WER.

This program simulates transcript events; it does NOT perform speech recognition.
Run: python examples/stt_event_lab.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
import unicodedata


@dataclass(frozen=True)
class STTEvent:
    kind: str  # 'partial', 'final', or 'turn_end'
    segment_id: str = ""
    text: str = ""


@dataclass
class TranscriptAssembler:
    """A simple ordered transcript view keyed by provider segment ID.

    A final segment is immutable in this educational implementation.
    Real providers differ in segment boundaries and update semantics.
    """
    finalized: dict[str, str] = field(default_factory=dict)
    pending: dict[str, str] = field(default_factory=dict)
    turn_ended: bool = False

    def handle(self, event: STTEvent) -> None:
        if event.kind == "turn_end":
            self.turn_ended = True
            return
        if not event.segment_id:
            raise ValueError("segment_id is required for partial/final events")
        if event.kind == "partial":
            if event.segment_id not in self.finalized:
                self.pending[event.segment_id] = event.text
        elif event.kind == "final":
            old = self.finalized.get(event.segment_id)
            if old is not None and old != event.text:
                raise ValueError("conflicting final transcript for same segment ID")
            self.finalized[event.segment_id] = event.text
            self.pending.pop(event.segment_id, None)
        else:
            raise ValueError(f"unsupported event kind: {event.kind}")

    @property
    def stable_text(self) -> str:
        return " ".join(piece for piece in self.finalized.values() if piece)

    @property
    def display_text(self) -> str:
        # Order is first-seen order in this compact example. For full systems,
        # providers may supply timestamps/sequence IDs for canonical ordering.
        parts = list(self.finalized.values()) + list(self.pending.values())
        return " ".join(piece for piece in parts if piece)


def normalize_for_wer(text: str) -> list[str]:
    """Simple, explicit normalization: casefold, punctuation to whitespace.

    Arabic diacritics and hamza distinctions are intentionally preserved.
    Production benchmarks must document their normalizer and tokenization.
    """
    text = unicodedata.normalize("NFC", text).casefold()
    text = "".join(" " if unicodedata.category(c).startswith("P") else c for c in text)
    return text.split()


def word_error_rate(reference: str, hypothesis: str) -> float:
    """Levenshtein distance on whitespace tokens divided by reference count."""
    ref = normalize_for_wer(reference)
    hyp = normalize_for_wer(hypothesis)
    if not ref:
        if hyp:
            raise ValueError("WER undefined for an empty reference with words predicted")
        return 0.0  # Convention for two empty strings in this teaching lab.
    prev = list(range(len(hyp) + 1))
    for i, word in enumerate(ref, 1):
        cur = [i]
        for j, candidate in enumerate(hyp, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (word != candidate)))
        prev = cur
    return prev[-1] / len(ref)


def demo() -> None:
    events = [
        STTEvent("partial", "s1", "أريد موعد يوم الثلا"),
        STTEvent("partial", "s1", "أريد موعد يوم الثلاثاء"),
        STTEvent("final", "s1", "أريد موعد يوم الثلاثاء"),
        STTEvent("turn_end"),
    ]
    assembler = TranscriptAssembler()
    print("STT event simulation (NOT a speech recognizer):")
    for event in events:
        assembler.handle(event)
        print(f"{event.kind:8} | visible={assembler.display_text!r} "
              f"| final={assembler.stable_text!r} | turn_end={assembler.turn_ended}")
    print("WER example:", word_error_rate("أريد موعد يوم الثلاثاء", "أريد موعد يوم الخميس"))


if __name__ == "__main__":
    demo()
