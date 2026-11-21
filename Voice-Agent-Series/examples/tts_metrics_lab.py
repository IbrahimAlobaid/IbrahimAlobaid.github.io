"""Minimal, provider-independent TTS metrics and PCM/WAV lab.

No network/API/model is required. Use with any generated PCM WAV file.
"""
from __future__ import annotations
import argparse
import math
import wave
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AudioStats:
    frames: int
    channels: int
    sample_rate: int
    sample_width: int
    duration_s: float
    bytes_per_second: int


def pcm_bytes_per_second(sample_rate: int, channels: int, sample_width: int) -> int:
    """Return raw PCM byte rate; sample_width is bytes per sample."""
    if any(type(v) is not int or v <= 0 for v in (sample_rate, channels, sample_width)):
        raise ValueError('Audio format values must be positive integers')
    return sample_rate * channels * sample_width


def frame_bytes(sample_rate: int, channels: int, sample_width: int, duration_ms: int) -> int:
    """Bytes for a PCM frame at exact integer sample boundary."""
    if type(duration_ms) is not int or duration_ms <= 0:
        raise ValueError('duration_ms must be a positive integer')
    samples_numerator = sample_rate * duration_ms
    if samples_numerator % 1000:
        raise ValueError('Frame length is not an integer number of samples')
    return (samples_numerator // 1000) * channels * sample_width


def real_time_factor(computation_seconds: float, audio_seconds: float) -> float:
    """RTF <1: synthesizing faster than real-time (for that measured interval)."""
    if not math.isfinite(computation_seconds) or computation_seconds < 0:
        raise ValueError('computation_seconds must be finite and >= 0')
    if not math.isfinite(audio_seconds) or audio_seconds <= 0:
        raise ValueError('audio_seconds must be finite and > 0')
    return computation_seconds / audio_seconds


def inspect_wav(path: str | Path) -> AudioStats:
    with wave.open(str(path), 'rb') as wav:
        if wav.getcomptype() != 'NONE':
            raise ValueError('Expected uncompressed PCM WAV')
        n = wav.getnframes()
        rate = wav.getframerate()
        channels = wav.getnchannels()
        width = wav.getsampwidth()
    return AudioStats(
        frames=n,
        channels=channels,
        sample_rate=rate,
        sample_width=width,
        duration_s=n / rate,
        bytes_per_second=pcm_bytes_per_second(rate, channels, width),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description='Inspect actual synthesized PCM WAV and RTF')
    parser.add_argument('wav', help='Path to WAV output produced by TTS')
    parser.add_argument('--compute-seconds', type=float, help='Measured synthesis time in seconds')
    args = parser.parse_args()
    stats = inspect_wav(args.wav)
    print(f'Sample rate: {stats.sample_rate} Hz | channels: {stats.channels} | bit depth: {8 * stats.sample_width}')
    print(f'Audio duration: {stats.duration_s:.3f} s | raw PCM rate: {stats.bytes_per_second:,} bytes/s')
    print(f'20-ms frame: {frame_bytes(stats.sample_rate, stats.channels, stats.sample_width, 20):,} bytes')
    if args.compute_seconds is not None:
        print(f'RTF (wall time / audio duration): {real_time_factor(args.compute_seconds, stats.duration_s):.3f}')


if __name__ == '__main__':
    main()
