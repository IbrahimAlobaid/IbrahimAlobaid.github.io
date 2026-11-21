"""Voice-context educational lab (Python >= 3.10, no dependencies).

This is a deterministic state-management example, NOT a speech recognizer,
LLM, audio transport, production booking service, or reliable word aligner.
Transport ACKs here mean entire text segments finished playing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
from typing import Literal

ALLOWED_SLOTS = ("service", "date", "time")


@dataclass(frozen=True)
class Turn:
    role: Literal["user", "assistant"]
    text: str
    delivery: Literal["final", "partial"] = "final"


@dataclass
class SpeechQueue:
    segments: list[str]
    next_ack: int = 0


@dataclass
class VoiceContext:
    """Session-scoped context; does not persist or execute real actions."""
    instructions: str = (
        "You are a concise appointment voice assistant. "
        "Never claim a booking happened without external confirmation. "
        "Ask one short question when essential details are missing."
    )
    turns: list[Turn] = field(default_factory=list)
    slots: dict[str, str | None] = field(default_factory=lambda: dict.fromkeys(ALLOWED_SLOTS))
    user_approved: bool = False
    partial_transcript: str = ""
    pending: SpeechQueue | None = None

    def on_interim_transcript(self, text: str) -> None:
        """An STT interim hypothesis is not a confirmed user turn."""
        self.partial_transcript = text

    def commit_user_turn(self, text: str, updates: dict[str, str] | None = None) -> None:
        """Call only after receiving an STT final transcript.

        `updates` are EXTERNALLY parsed/validated slot values; this example
        deliberately does not infer them with regex or an LLM.
        """
        if not text.strip():
            raise ValueError("Final transcript must be non-empty")
        updates = updates or {}
        self._validate_updates(updates)
        self.turns.append(Turn("user", text.strip()))
        if any(self.slots[k] != v for k, v in updates.items()):
            self.user_approved = False
        self.slots.update(updates)
        self.partial_transcript = ""

    @staticmethod
    def _validate_updates(updates: dict[str, str]) -> None:
        if set(updates) - set(ALLOWED_SLOTS):
            raise ValueError("Unknown slot")
        if any(not isinstance(v, str) or not v.strip() for v in updates.values()):
            raise ValueError("Slot values must be non-empty strings")
        if "date" in updates and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", updates["date"]):
            raise ValueError("Use YYYY-MM-DD")
        if "time" in updates and not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", updates["time"]):
            raise ValueError("Use HH:MM")
        # Real apps must also validate calendar dates, timezone, service IDs,
        # and available times using authoritative server data.

    def queue_reply(self, segments: list[str]) -> None:
        """Create uncommitted assistant speech, split at safe boundaries."""
        if self.pending is not None:
            raise RuntimeError("Finish or interrupt previous reply first")
        if not segments or any(not x.strip() for x in segments):
            raise ValueError("Segments must contain speakable text")
        self.pending = SpeechQueue(segments=list(segments))

    def acknowledge_played_segment(self, index: int) -> None:
        """Transport confirms entire segment `index` finished playing."""
        if self.pending is None or index != self.pending.next_ack:
            raise ValueError("Out-of-order or unexpected playback ACK")
        self.pending.next_ack += 1

    def finish_reply(self) -> None:
        if self.pending is None or self.pending.next_ack != len(self.pending.segments):
            raise RuntimeError("Cannot commit segments not acknowledged played")
        self.turns.append(Turn("assistant", " ".join(self.pending.segments)))
        self.pending = None

    def interrupt_reply(self) -> None:
        """Discard unplayed segments; conservatively omit in-progress text."""
        if self.pending is None:
            return
        played = self.pending.segments[: self.pending.next_ack]
        if played:
            self.turns.append(Turn("assistant", " ".join(played), "partial"))
        self.pending = None

    def ready_to_request_booking(self) -> bool:
        return all(self.slots.values()) and self.user_approved

    def approve_current_details(self) -> None:
        """Invoke only after explicit user approval, never from a guess."""
        if not all(self.slots.values()):
            raise ValueError("Missing appointment details")
        self.user_approved = True

    def prompt_context(self, recent_turns: int = 6) -> dict[str, object]:
        """Build a small, inspectable prompt payload, but do not call an LLM."""
        if recent_turns < 0:
            raise ValueError("recent_turns must be >= 0")
        recent = self.turns[-recent_turns:] if recent_turns else []
        return {
            "developer_instructions": self.instructions,
            "task_state": {"slots": dict(self.slots), "user_approved": self.user_approved},
            "recent_turns": [vars(turn) for turn in recent],
        }


def demo() -> None:
    state = VoiceContext()
    state.on_interim_transcript("Book me on Thurs...")
    state.commit_user_turn("Book a consultation on Thursday at 10.", {
        "service": "consultation", "date": "2026-11-26", "time": "10:00"
    })
    state.queue_reply(["You requested a consultation at ten.", "I will now summarize the details."])
    state.acknowledge_played_segment(0)
    state.interrupt_reply()
    state.commit_user_turn("Actually, make it three in the afternoon.", {"time": "15:00"})
    print(json.dumps(state.prompt_context(), ensure_ascii=False, indent=2))
    print("Needs explicit approval:", not state.ready_to_request_booking())
    state.approve_current_details()
    print("Ready to REQUEST booking (not booked):", state.ready_to_request_booking())


if __name__ == "__main__":
    demo()
