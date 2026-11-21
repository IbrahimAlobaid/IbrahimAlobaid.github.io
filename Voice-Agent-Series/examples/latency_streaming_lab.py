"""Article 11: deterministic, provider-neutral voice latency telemetry lab.

All event timestamps in a trace MUST be in milliseconds on a single monotonic
clock/reference timeline. Do not subtract independent server/client clocks.
The bundled data is synthetic, not an STT/LLM/TTS service benchmark.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

FIELDS = (
    "user_speech_end_ms",
    "turn_committed_ms",
    "transcript_final_ms",
    "llm_request_ms",
    "llm_first_token_ms",
    "text_ready_for_tts_ms",
    "tts_request_ms",
    "tts_first_chunk_ms",
    "client_audio_arrived_ms",
    "client_first_audible_ms",
)


@dataclass(frozen=True)
class TurnTrace:
    turn_id: str
    scenario: str
    user_speech_end_ms: float
    turn_committed_ms: float
    transcript_final_ms: float
    llm_request_ms: float
    llm_first_token_ms: float
    text_ready_for_tts_ms: float
    tts_request_ms: float
    tts_first_chunk_ms: float
    client_audio_arrived_ms: float
    client_first_audible_ms: float
    clock_id: str = "synthetic-shared-monotonic-clock"

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "TurnTrace":
        if not isinstance(data.get("turn_id"), str) or not data["turn_id"].strip():
            raise ValueError("turn_id must be a nonempty string")
        if not isinstance(data.get("scenario"), str) or not data["scenario"].strip():
            raise ValueError("scenario must be a nonempty string")
        clock_id = data.get("clock_id", "synthetic-shared-monotonic-clock")
        if not isinstance(clock_id, str) or not clock_id.strip():
            raise ValueError("clock_id must be a nonempty string")
        values: dict[str, float] = {}
        for field in FIELDS:
            value = data.get(field)
            if isinstance(value, bool) or not isinstance(value, (float, int)):
                raise ValueError(f"{field} must be numeric")
            if not math.isfinite(float(value)) or float(value) < 0:
                raise ValueError(f"{field} must be finite and nonnegative")
            values[field] = float(value)
        result = cls(
            turn_id=str(data["turn_id"]), scenario=str(data["scenario"]),
            clock_id=clock_id, **values,
        )
        result.validate()
        return result

    def validate(self) -> None:
        # These pairs are causally ordered. Other stages may overlap.
        for earlier, later in (
            ("user_speech_end_ms", "turn_committed_ms"),
            ("user_speech_end_ms", "transcript_final_ms"),
            ("llm_request_ms", "llm_first_token_ms"),
            ("llm_first_token_ms", "text_ready_for_tts_ms"),
            ("text_ready_for_tts_ms", "tts_request_ms"),
            ("tts_request_ms", "tts_first_chunk_ms"),
            ("tts_first_chunk_ms", "client_audio_arrived_ms"),
            ("client_audio_arrived_ms", "client_first_audible_ms"),
            ("user_speech_end_ms", "client_first_audible_ms"),
        ):
            if getattr(self, later) < getattr(self, earlier):
                raise ValueError(f"Out-of-order events: {earlier} > {later}")

    def metrics(self) -> dict[str, float]:
        """Each duration has its own anchor; stage metrics are NOT additive."""
        self.validate()
        return {
            "e2e_to_first_audible_ms": self.client_first_audible_ms - self.user_speech_end_ms,
            "endpointing_wait_ms": self.turn_committed_ms - self.user_speech_end_ms,
            "stt_tail_ms": self.transcript_final_ms - self.user_speech_end_ms,
            "llm_ttft_ms": self.llm_first_token_ms - self.llm_request_ms,
            "text_aggregation_ms": self.text_ready_for_tts_ms - self.llm_first_token_ms,
            "tts_ttfb_ms": self.tts_first_chunk_ms - self.tts_request_ms,
            "delivery_playout_ms": self.client_first_audible_ms - self.tts_first_chunk_ms,
        }


def percentile_nearest_rank(values: Iterable[float], p: float) -> float:
    """Nearest-rank percentile: sorted[ceil(p*n/100)-1]; p=0 is min."""
    items = list(values)
    if not items:
        raise ValueError("Cannot compute a percentile of an empty sample")
    if not math.isfinite(p) or not 0 <= p <= 100:
        raise ValueError("Percentile must be between 0 and 100")
    for v in items:
        if isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v):
            raise ValueError("Percentile values must be finite numbers")
    items.sort()
    return items[max(0, math.ceil(p * len(items) / 100) - 1)]


def summary(traces: Iterable[TurnTrace]) -> dict[str, dict[str, float | int]]:
    """Group comparable user-to-first-audible durations by scenario."""
    groups: dict[str, list[float]] = {}
    ids: set[str] = set()
    clock_ids: set[str] = set()
    for trace in traces:
        trace.validate()
        if trace.turn_id in ids:
            raise ValueError(f"Duplicate turn_id: {trace.turn_id}")
        ids.add(trace.turn_id)
        clock_ids.add(trace.clock_id)
        groups.setdefault(trace.scenario, []).append(trace.metrics()["e2e_to_first_audible_ms"])
    if not groups:
        raise ValueError("No traces supplied")
    # All rows may use independent monotonic origins if durations are formed *within* rows.
    # Different clocks within ONE row are not representable by this format.
    return {
        scenario: {
            "n": len(values),
            "p50_ms": percentile_nearest_rank(values, 50),
            "p95_ms": percentile_nearest_rank(values, 95),
            "p99_ms": percentile_nearest_rank(values, 99),
            "min_ms": min(values),
            "max_ms": max(values),
        }
        for scenario, values in sorted(groups.items())
    }


def load_jsonl(path: str | Path) -> list[TurnTrace]:
    path = Path(path)
    traces: list[TurnTrace] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
            if not isinstance(parsed, dict):
                raise ValueError("A JSONL row must be an object")
            traces.append(TurnTrace.from_dict(parsed))
        except (ValueError, TypeError) as exc:
            raise ValueError(f"{path.name}:{number}: {exc}") from exc
    if not traces:
        raise ValueError("Input file contains no traces")
    return traces


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(Path(__file__).with_name("11-synthetic-traces.jsonl")))
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary")
    args = parser.parse_args()
    results = summary(load_jsonl(args.input))
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("Synthetic example only — NOT a voice-provider benchmark")
        print(f"{'Scenario':<20}{'n':>5}{'p50 (ms)':>12}{'p95 (ms)':>12}{'p99 (ms)':>12}")
        for name, metrics in results.items():
            print(f"{name:<20}{metrics['n']:>5}{metrics['p50_ms']:>12.0f}{metrics['p95_ms']:>12.0f}{metrics['p99_ms']:>12.0f}")


if __name__ == "__main__":
    main()
