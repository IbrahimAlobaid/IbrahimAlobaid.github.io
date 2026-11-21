"""Optional real speech synthesis using Piper's current local Python API.

Install: python -m pip install piper-tts
Voice:   python -m piper.download_voices en_US-lessac-medium
Run:     python examples/tts_piper_demo.py --model en_US-lessac-medium.onnx
Requires downloaded voice model. No provider key or cloud request is used.
"""
from __future__ import annotations
import argparse
import time
import wave
from pathlib import Path

from tts_metrics_lab import inspect_wav, real_time_factor


def synthesize(model_path: Path, text: str, output: Path) -> dict[str, float]:
    # Import is intentionally optional to keep the metrics lab dependency-free.
    from piper import PiperVoice
    if not model_path.exists():
        raise FileNotFoundError(f'Voice model not found: {model_path}')
    if not text.strip():
        raise ValueError('Text must not be empty')
    output.parent.mkdir(parents=True, exist_ok=True)
    voice = PiperVoice.load(str(model_path))  # warm model load excluded from synthesis interval
    start = time.perf_counter()
    first_chunk_s = None
    with wave.open(str(output), 'wb') as wav:
        for chunk in voice.synthesize(text):
            if first_chunk_s is None:
                first_chunk_s = time.perf_counter() - start
                wav.setframerate(chunk.sample_rate)
                wav.setsampwidth(chunk.sample_width)
                wav.setnchannels(chunk.sample_channels)
            wav.writeframesraw(chunk.audio_int16_bytes)
        if first_chunk_s is None:
            raise RuntimeError('Piper did not yield any audio chunks')
    elapsed = time.perf_counter() - start
    stats = inspect_wav(output)
    return {
        'time_to_first_generated_chunk_s': first_chunk_s,
        'synthesis_wall_seconds': elapsed,
        'audio_duration_seconds': stats.duration_s,
        'rtf': real_time_factor(elapsed, stats.duration_s),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Create WAV speech locally using Piper')
    parser.add_argument('--model', type=Path, default=Path('en_US-lessac-medium.onnx'))
    parser.add_argument('--text', default='Hello! I am your voice assistant. How can I help?')
    parser.add_argument('--output', type=Path, default=Path('examples/tts_piper_output.wav'))
    args = parser.parse_args()
    metrics = synthesize(args.model, args.text, args.output)
    print(f'File: {args.output}')
    for name, value in metrics.items():
        print(f'{name}: {value:.3f}')
    print('Reminder: first generated chunk != first byte on wire != first sound heard by user.')


if __name__ == '__main__':
    main()
