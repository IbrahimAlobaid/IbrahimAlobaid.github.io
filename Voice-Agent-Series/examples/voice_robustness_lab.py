"""Article 12 lab: deterministic voice-agent resilience policy (NOT an audio model).

All detection flags in the bundled JSONL are synthetic test inputs; they do not
represent calibrated probabilities from a production VAD/STT/diarization system.
This code performs no external actions and uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable


class Action(str, Enum):
    WAIT = "wait_for_more_audio"
    IGNORE = "ignore_unaddressed_audio"
    CLARIFY = "ask_to_repeat"
    CONFIRM = "confirm_sensitive_details"
    RESPOND = "respond_to_user"
    HOLD = "hold_and_reconnect"


@dataclass(frozen=True)
class Evidence:
    speech_detected: bool = False
    foreground_confirmed: bool = False
    echo_suspected: bool = False
    final_transcript: bool = False
    transcript: str = ""
    critical_detail: bool = False
    network_up: bool = True


@dataclass(frozen=True)
class Decision:
    action: Action
    reason: str


def decide(e: Evidence) -> Decision:
    """Conservative illustrative ordering; policy, NOT diarization or VAD."""
    if not e.network_up:
        return Decision(Action.HOLD, "audio link unavailable; do not assume delivery")
    if not e.speech_detected:
        return Decision(Action.WAIT, "no usable near-end speech evidence")
    if not e.foreground_confirmed:
        return Decision(Action.IGNORE, "input is not confirmed as intended speaker")
    if e.echo_suspected and not e.final_transcript:
        return Decision(Action.WAIT, "potential echo; wait for cleaner evidence")
    if not e.final_transcript:
        return Decision(Action.WAIT, "ASR remains partial/unstable")
    if not e.transcript.strip():
        return Decision(Action.CLARIFY, "final text is blank/unintelligible")
    if e.critical_detail:
        return Decision(Action.CONFIRM, "sensitive field requires explicit confirmation")
    return Decision(Action.RESPOND, "final addressed non-critical request")


def normalize_tokens(text: str) -> list[str]:
    """Basic illustrative tokenization; NOT Arabic-aware or multilingual WER."""
    chars = []
    for c in unicodedata.normalize("NFKC", text).casefold():
        chars.append(" " if unicodedata.category(c).startswith("P") else c)
    return " ".join("".join(chars).split()).split()


def word_errors(reference: str, hypothesis: str) -> tuple[int, int]:
    """(edit distance, reference token count); score with WER=errors/ref_count."""
    a, b = normalize_tokens(reference), normalize_tokens(hypothesis)
    dp = list(range(len(b) + 1))
    for i, ref_word in enumerate(a, start=1):
        prev = dp[0]
        dp[0] = i
        for j, hyp_word in enumerate(b, start=1):
            saved = dp[j]
            dp[j] = min(dp[j] + 1, dp[j-1] + 1, prev + int(ref_word != hyp_word))
            prev = saved
    return dp[-1], len(a)


def snr_db(speech_rms: float, noise_rms: float) -> float:
    """Synthetic RMS illustration: requires separate known speech/noise signals."""
    if not (math.isfinite(speech_rms) and math.isfinite(noise_rms)):
        raise ValueError("RMS inputs must be finite")
    if speech_rms < 0 or noise_rms < 0:
        raise ValueError("RMS cannot be negative")
    if noise_rms == 0:
        return math.inf if speech_rms > 0 else math.nan
    if speech_rms == 0:
        return -math.inf
    return 20 * math.log10(speech_rms / noise_rms)


def clipping_fraction(samples: Iterable[float], threshold: float = 0.99) -> float:
    if not 0 < threshold <= 1:
        raise ValueError("threshold must lie in (0, 1]")
    values = list(samples)
    if not values:
        raise ValueError("at least one audio sample required")
    if any(not math.isfinite(x) or abs(x) > 1 for x in values):
        raise ValueError("samples must be finite normalized floats in [-1,1]")
    return sum(abs(x) >= threshold for x in values) / len(values)


def retry_delays(max_retries: int = 4, base_seconds: float = 0.5, cap_seconds: float = 8.0) -> list[float]:
    """Deterministic capped exponential waits; production should add jitter."""
    if max_retries < 0 or not (0 < base_seconds <= cap_seconds):
        raise ValueError("invalid retry settings")
    return [min(cap_seconds, base_seconds * 2**attempt) for attempt in range(max_retries)]


class RecoveryState:
    """Reject stale packets and duplicate events; does not reconnect a socket."""

    def __init__(self) -> None:
        self.generation = 1
        self.connected = True
        self._seen_ids: set[str] = set()
        self.pending_confirmation: str | None = None
        self.committed_action_ids: set[str] = set()

    def lose_connection(self) -> None:
        self.connected = False
        self.pending_confirmation = None  # Never pretend a confirmation survived a drop.

    def on_reconnected(self) -> int:
        self.connected = True
        self.generation += 1
        self._seen_ids.clear()
        return self.generation

    def receive(self, event_id: str, generation: int) -> bool:
        if not event_id:
            raise ValueError("event_id required")
        if not self.connected or generation != self.generation or event_id in self._seen_ids:
            return False
        self._seen_ids.add(event_id)
        return True

    def propose_action(self, action_id: str) -> None:
        if not self.connected or not action_id:
            raise ValueError("cannot propose an action in this state")
        self.pending_confirmation = action_id

    def confirm_action(self, action_id: str) -> bool:
        """Local state only; never issues a real-world action."""
        if not self.connected or action_id != self.pending_confirmation:
            return False
        self.pending_confirmation = None
        if action_id in self.committed_action_ids:
            return False
        self.committed_action_ids.add(action_id)
        return True


def read_cases(path: Path) -> list[dict]:
    cases = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            item = json.loads(line)
            for field in ("scenario", "reference", "hypothesis", "expected_action", "evidence"):
                if field not in item:
                    raise ValueError(f"case line {i}: missing {field}")
            cases.append(item)
    return cases


def evaluate_cases(cases: list[dict]) -> dict:
    by_scenario = defaultdict(lambda: {"n": 0, "errors": 0, "ref_tokens": 0})
    matching = 0
    actions = Counter()
    for case in cases:
        evidence = Evidence(**case["evidence"])
        action = decide(evidence).action.value
        actions[action] += 1
        matching += int(action == case["expected_action"])
        errors, ref_count = word_errors(case["reference"], case["hypothesis"])
        row = by_scenario[case["scenario"]]
        row["n"] += 1
        row["errors"] += errors
        row["ref_tokens"] += ref_count
    return {
        "synthetic_only": True,
        "n": len(cases),
        "policy_case_match": matching,
        "actions": dict(sorted(actions.items())),
        "scenario_wer": {
            s: {"n": row["n"], "wer": round(row["errors"] / row["ref_tokens"], 3) if row["ref_tokens"] else None}
            for s, row in sorted(by_scenario.items())
        },
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Deterministic voice resilience policy lab")
    p.add_argument("--dataset", type=Path, default=Path(__file__).with_name("12-synthetic-resilience-cases.jsonl"))
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    results = evaluate_cases(read_cases(args.dataset))
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("SYNTHETIC EDUCATIONAL DATA — not a production benchmark")
        print(f"Cases: {results['n']} | policy expectations matched: {results['policy_case_match']}")
        for k, row in results["scenario_wer"].items():
            print(f"{k:<20} n={row['n']:>2} WER={row['wer']}")
        print("Action counts:", results["actions"])


if __name__ == "__main__":
    main()
