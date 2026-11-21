"""Deterministic playback / barge-in lab for Voice AI Engineering, Article 10.

No audio, LLM, TTS, network, or provider SDK.  Times are synthetic milliseconds.
Crucially, only client playback acknowledgements can advance `played_ms`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal

Stage = Literal["generated", "synthesized", "transmitted", "buffered"]
ORDER: tuple[Stage, ...] = ("generated", "synthesized", "transmitted", "buffered")


class Status(str, Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    INTERRUPTED = "interrupted"
    FINISHED = "finished"


@dataclass(frozen=True)
class AlignedCaption:
    start_ms: int
    end_ms: int
    text: str

    def __post_init__(self) -> None:
        if self.start_ms < 0 or self.end_ms <= self.start_ms:
            raise ValueError("caption interval must have positive duration")


@dataclass
class PlaybackTurn:
    item_id: str
    epoch: int
    total_ms: int
    generated_ms: int = 0
    synthesized_ms: int = 0
    transmitted_ms: int = 0
    buffered_ms: int = 0
    played_ms: int = 0
    status: Status = Status.PLAYING
    captions: list[AlignedCaption] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.item_id.strip() or self.total_ms <= 0:
            raise ValueError("invalid item_id or duration")


class PlaybackController:
    """Simulates output ownership and reconciles playback with context.

    Production integrations must implement real media-stop confirmation,
    cancellation and remote API event handling outside this teaching lab.
    """

    def __init__(self) -> None:
        self._epoch = 0
        self.active: PlaybackTurn | None = None
        self.audit: list[str] = []

    def start(self, item_id: str, total_ms: int, captions: list[AlignedCaption] | None = None) -> int:
        if self.active and self.active.status in (Status.PLAYING, Status.PAUSED):
            raise RuntimeError("stop or finish the current turn first")
        self._epoch += 1
        self.active = PlaybackTurn(item_id, self._epoch, total_ms, captions=captions or [])
        self.audit.append(f"started:{item_id}:{self._epoch}")
        return self._epoch

    def _valid(self, epoch: int, *, paused_allowed: bool = False) -> bool:
        t = self.active
        return (t is not None and epoch == t.epoch and
                (t.status == Status.PLAYING or (paused_allowed and t.status == Status.PAUSED)))

    def advance(self, stage: Stage, up_to_ms: int, epoch: int) -> bool:
        """Advance an upstream data boundary; stale epochs are silently dropped."""
        if stage not in ORDER:
            raise ValueError("unknown stage")
        if not self._valid(epoch):
            return False
        t = self.active
        assert t is not None
        prev_stage = ORDER[ORDER.index(stage) - 1] if stage != "generated" else None
        upper = getattr(t, f"{prev_stage}_ms") if prev_stage else t.total_ms
        current = getattr(t, f"{stage}_ms")
        if not current <= up_to_ms <= upper:
            raise ValueError(f"{stage} cursor must be monotonic and <= upstream cursor")
        setattr(t, f"{stage}_ms", up_to_ms)
        return True

    def acknowledge_playback(self, played_ms: int, epoch: int) -> bool:
        """Accept a monotonic player acknowledgement; never infer it from sent audio."""
        if not self._valid(epoch, paused_allowed=True):
            return False
        t = self.active
        assert t is not None
        if not t.played_ms <= played_ms <= t.buffered_ms:
            raise ValueError("playback cursor must be monotonic and <= buffered audio")
        t.played_ms = played_ms
        return True

    def pause_for_candidate(self, epoch: int) -> bool:
        """Immediately request pause; preserve potential resume on false interruption."""
        if not self._valid(epoch):
            return False
        assert self.active is not None
        self.active.status = Status.PAUSED
        self.audit.append("candidate_paused")
        return True

    def resume_false_interrupt(self, epoch: int) -> bool:
        if not self._valid(epoch, paused_allowed=True) or self.active.status != Status.PAUSED:
            return False
        self.active.status = Status.PLAYING
        self.audit.append("false_interrupt_resumed")
        return True

    def confirm_interruption(self, epoch: int, *, final_played_ms: int) -> dict[str, int | str] | None:
        """Requires final client stop acknowledgement (here passed as final_played_ms)."""
        if not self._valid(epoch, paused_allowed=True):
            return None
        assert self.active is not None
        t = self.active
        self.acknowledge_playback(final_played_ms, epoch)
        t.status = Status.INTERRUPTED
        self._epoch += 1  # invalidate all pending old-generation events
        self.audit.append(f"interrupted:{t.item_id}:{t.played_ms}")
        return {
            "action": "cancel_generation_and_tts;clear_output_queue;sync_context",
            "item_id": t.item_id,
            "played_ms": t.played_ms,
            "unheard_buffered_ms": t.buffered_ms - t.played_ms,
            "unheard_generated_ms": t.generated_ms - t.played_ms,
        }

    def mark_finished(self, epoch: int) -> bool:
        if not self._valid(epoch):
            return False
        assert self.active is not None
        if self.active.played_ms != self.active.total_ms:
            raise ValueError("cannot finish before playback completion is acknowledged")
        self.active.status = Status.FINISHED
        self.audit.append("finished")
        return True

    def played_caption(self) -> str | None:
        """Only fully played aligned segments; None = no trustworthy alignment."""
        t = self.active
        if t is None or not t.captions:
            return None
        return " ".join(c.text for c in t.captions if c.end_ms <= t.played_ms)

    def realtime_ws_truncate_event(self, epoch: int, content_index: int = 0) -> dict | None:
        """Illustrative OpenAI Realtime WebSocket client event after interruption.

        Not intended for WebRTC/SIP managed buffers or for other providers.
        """
        t = self.active
        if not t or t.epoch != epoch or t.status != Status.INTERRUPTED:
            return None
        if content_index < 0:
            raise ValueError("invalid content_index")
        return {
            "type": "conversation.item.truncate",
            "item_id": t.item_id,
            "content_index": content_index,
            "audio_end_ms": t.played_ms,
        }


def demonstration() -> dict:
    c = PlaybackController()
    token = c.start("item_demo", 3600, [
        AlignedCaption(0, 600, "You can"),
        AlignedCaption(600, 1400, "use your passport"),
        AlignedCaption(1400, 2300, "or identity card"),
    ])
    for name, ms in [("generated", 3600), ("synthesized", 3100),
                     ("transmitted", 2600), ("buffered", 2400)]:
        c.advance(name, ms, token)
    c.acknowledge_playback(1400, token)
    c.pause_for_candidate(token)
    plan = c.confirm_interruption(token, final_played_ms=1500)
    return {"plan": plan, "caption": c.played_caption(),
            "api_event": c.realtime_ws_truncate_event(token), "audit": c.audit}


if __name__ == "__main__":
    import json
    print(json.dumps(demonstration(), ensure_ascii=False, indent=2))
