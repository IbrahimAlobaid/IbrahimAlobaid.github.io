"""Article 08: deterministic transport and jitter exercises.

Pure Python, no network, browser, or AI service required. Values are synthetic.
This illustrates timing principles; it is NOT an RFC-compliant RTP receiver,
a production jitter buffer, or an actual WebRTC/WebSocket benchmark.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class PacketObservation:
    """One synthetic packet seen by the receiver; times share a clock (ms)."""

    seq: int
    sent_ms: float
    arrived_ms: float

    def __post_init__(self) -> None:
        if not isinstance(self.seq, int) or isinstance(self.seq, bool) or self.seq < 0:
            raise ValueError("sequence must be a nonnegative integer")
        if any(not isinstance(t, (int, float)) or not isfinite(t) or t < 0
               for t in (self.sent_ms, self.arrived_ms)):
            raise ValueError("times must be finite and nonnegative")
        if self.arrived_ms < self.sent_ms:
            raise ValueError("simulation uses a shared clock; arrival >= send")


class InterarrivalJitter:
    """RFC 3550-style exponentially smoothed transit variation, in milliseconds.

    *The formula* is used for teaching, not for computing browser getStats jitter.
    """

    def __init__(self) -> None:
        self.jitter_ms = 0.0
        self._previous_transit_ms: float | None = None

    def update(self, packet: PacketObservation) -> float:
        transit_ms = packet.arrived_ms - packet.sent_ms
        if self._previous_transit_ms is not None:
            delta = abs(transit_ms - self._previous_transit_ms)
            self.jitter_ms += (delta - self.jitter_ms) / 16.0
        self._previous_transit_ms = transit_ms
        return self.jitter_ms


@dataclass(frozen=True)
class StreamSummary:
    received_unique: int
    missing: int
    duplicates: int
    reordered: int
    loss_percent: float
    jitter_ms: float


def summarize_packets(observations: list[PacketObservation], expected_packets: int) -> StreamSummary:
    if not isinstance(expected_packets, int) or isinstance(expected_packets, bool) or not (1 <= expected_packets <= 10000):
        raise ValueError("expected_packets must be in 1..10000")
    seen: set[int] = set()
    last_seq = -1
    last_arrival = -1.0
    duplicate_count = 0
    reordered = 0
    jitter = InterarrivalJitter()
    for packet in observations:
        if packet.seq >= expected_packets:
            raise ValueError("sequence outside configured synthetic stream")
        if packet.arrived_ms < last_arrival:
            raise ValueError("observations must be in arrival order")
        last_arrival = packet.arrived_ms
        if packet.seq in seen:
            duplicate_count += 1
            continue
        if packet.seq < last_seq:
            reordered += 1
        last_seq = max(last_seq, packet.seq)
        seen.add(packet.seq)
        jitter.update(packet)
    missing = expected_packets - len(seen)
    return StreamSummary(len(seen), missing, duplicate_count, reordered,
                         round(100.0 * missing / expected_packets, 2),
                         round(jitter.jitter_ms, 3))


def raw_audio_kbps(sample_rate: int, bits_per_sample: int, channels: int) -> float:
    if any(not isinstance(v, int) or isinstance(v, bool) or v <= 0
           for v in (sample_rate, bits_per_sample, channels)):
        raise ValueError("positive integers required")
    return sample_rate * bits_per_sample * channels / 1000.0


def frame_bytes(sample_rate: int, frame_ms: int, bits_per_sample: int, channels: int) -> int:
    if bits_per_sample % 8:
        raise ValueError("byte-aligned samples only")
    if any(not isinstance(v, int) or isinstance(v, bool) or v <= 0
           for v in (sample_rate, frame_ms, bits_per_sample, channels)):
        raise ValueError("positive integers required")
    sample_units = sample_rate * frame_ms
    if sample_units % 1000:
        raise ValueError("frame duration does not contain an integer number of samples")
    return sample_units // 1000 * (bits_per_sample // 8) * channels


def example_stream() -> list[PacketObservation]:
    # Missing seq=2; seq=4 arrives before seq=3. Values are illustrative only.
    return [
        PacketObservation(0, 0, 38),
        PacketObservation(1, 20, 57),
        PacketObservation(4, 80, 105),
        PacketObservation(3, 60, 111),
        PacketObservation(5, 100, 148),
    ]


def main() -> None:
    summary = summarize_packets(example_stream(), expected_packets=6)
    print("DEMO ONLY — synthetic packet arrivals, not a network benchmark")
    print(f"unique={summary.received_unique}, missing={summary.missing}, "
          f"duplicates={summary.duplicates}, reordered={summary.reordered}")
    print(f"observed loss={summary.loss_percent:.2f}%; smoothed transit variation={summary.jitter_ms:.3f} ms")
    print(f"48 kHz / 32-bit / mono: {raw_audio_kbps(48000, 32, 1):.0f} kbit/s raw audio")
    print(f"20 ms frame: {frame_bytes(48000, 20, 32, 1)} bytes")
    print("Note: WebRTC getStats reports its own RTP metrics; do not equate them to this model.")


if __name__ == "__main__":
    main()
