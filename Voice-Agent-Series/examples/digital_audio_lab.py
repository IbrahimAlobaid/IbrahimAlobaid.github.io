"""Voice AI Engineering — Article 02: PCM WAV laboratory.

Requires Python 3.10+ and no third-party packages.
Run: python examples/digital_audio_lab.py
     python examples/digital_audio_lab.py --input path/to/mono_16bit_pcm.wav
"""
import argparse
import math
import struct
import wave
from pathlib import Path


def write_demo(path: Path, sample_rate: int = 16_000, seconds: float = 1.0) -> None:
    """Write a one-second, mono, 16-bit PCM sine wave to a WAV container."""
    frame_count = round(sample_rate * seconds)
    samples = [
        round(0.30 * 32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
        for i in range(frame_count)
    ]
    audio_bytes = struct.pack(f"<{len(samples)}h", *samples)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16 bits per sample
        wav.setframerate(sample_rate)
        wav.writeframes(audio_bytes)


def analyze(path: Path, chunk_ms: int = 20) -> dict:
    """Read mono, signed 16-bit PCM WAV; compute peak and RMS in chunks."""
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_rate = wav.getframerate()
        bytes_per_sample = wav.getsampwidth()
        total_frames = wav.getnframes()
        if channels != 1 or bytes_per_sample != 2 or wav.getcomptype() != "NONE":
            raise ValueError("Expected uncompressed, mono, signed 16-bit PCM WAV")
        if not 1 <= chunk_ms <= 1000:
            raise ValueError("chunk_ms must be between 1 and 1000")
        frames_per_chunk = max(1, round(sample_rate * chunk_ms / 1000))
        peak = 0
        sum_squares = 0
        samples_read = 0
        chunks = 0
        first_chunk_bytes = 0
        while True:
            raw = wav.readframes(frames_per_chunk)
            if not raw:
                break
            count = len(raw) // 2
            values = struct.unpack(f"<{count}h", raw)
            peak = max(peak, max(map(abs, values)))
            sum_squares += sum(v * v for v in values)
            samples_read += count
            chunks += 1
            if chunks == 1:
                first_chunk_bytes = len(raw)
        return {
            "sample_rate": sample_rate,
            "channels": channels,
            "bit_depth": bytes_per_sample * 8,
            "frames": total_frames,
            "duration_s": total_frames / sample_rate,
            "nominal_chunk_ms": chunk_ms,
            "actual_full_chunk_ms": frames_per_chunk * 1000 / sample_rate,
            "chunk_bytes": frames_per_chunk * channels * bytes_per_sample,
            "first_chunk_bytes": first_chunk_bytes,
            "chunks": chunks,
            "peak_normalized": peak / 32768,
            "rms_normalized": math.sqrt(sum_squares / samples_read) / 32768 if samples_read else 0,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect PCM audio for voice agents")
    parser.add_argument("--input", type=Path, help="Optional mono 16-bit PCM WAV")
    parser.add_argument("--chunk-ms", type=int, default=20)
    args = parser.parse_args()
    source = args.input or Path("demo_16k_mono.wav")
    if args.input is None:
        write_demo(source)
        print(f"Generated example: {source}")
    result = analyze(source, chunk_ms=args.chunk_ms)
    for key, value in result.items():
        print(f"{key}: {value}")
    print("Note: This example WAV contains a 44-byte header in its simplest form; check actual file metadata.")


if __name__ == "__main__":
    main()
