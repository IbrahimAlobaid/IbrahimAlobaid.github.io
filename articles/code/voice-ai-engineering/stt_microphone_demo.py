"""Local microphone transcription with faster-whisper (segmented prototype).

Requires: python -m pip install faster-whisper sounddevice numpy
Run a real microphone test: python examples/stt_microphone_demo.py --microphone --language ar
Or transcribe a prerecorded file: python examples/stt_microphone_demo.py --input path/to/speech.wav --language ar

This is NOT a production streaming STT client. It does NOT emit partials.
It captures one fixed window at a time, then transcribes that window.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def transcribe(model, audio, language: str | None) -> str:
    segments, _ = model.transcribe(audio, beam_size=3, language=language, vad_filter=False)
    return " ".join(s.text.strip() for s in segments).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Educational STT microphone/file prototype")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--input", type=Path, help="Path to real speech recording")
    mode.add_argument("--microphone", action="store_true", help="Record small microphone windows")
    parser.add_argument("--model", default="base", help="Multilingual faster-whisper model (base, small, ...)")
    parser.add_argument("--language", default=None, help="Optional language code: ar, en, tr, ...")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("--compute-type", default="int8", help="e.g. int8 on CPU; float16 on suitable CUDA")
    parser.add_argument("--window-seconds", type=float, default=4.0)
    parser.add_argument("--windows", type=int, default=3)
    args = parser.parse_args()

    if args.window_seconds <= 0 or args.windows <= 0:
        parser.error("--window-seconds and --windows must be positive")
    if args.input is not None and not args.input.is_file():
        parser.error(f"file not found: {args.input}")

    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SystemExit("Install dependencies: python -m pip install faster-whisper sounddevice numpy") from exc
    print("Loading the STT model. The first run may download model weights.")
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)

    if args.input is not None:
        print("Transcript:", transcribe(model, str(args.input), args.language))
        return

    try:
        import sounddevice as sd
    except ImportError as exc:
        raise SystemExit("Install microphone dependency: python -m pip install sounddevice") from exc

    sample_rate = 16000
    n_samples = int(args.window_seconds * sample_rate)
    print("Recording microphone audio locally, one fixed window at a time.")
    print("This demo returns a final transcript after each window; it does not stream partials.")
    for index in range(1, args.windows + 1):
        try:
            print(f"Window {index}/{args.windows}: speak for {args.window_seconds:g} seconds...")
            recording = sd.rec(n_samples, samplerate=sample_rate, channels=1, dtype="float32")
            sd.wait()
        except (KeyboardInterrupt, Exception) as exc:
            # Do not suppress device errors; display a concise diagnostic.
            if isinstance(exc, KeyboardInterrupt):
                print("Stopped by user.")
                return
            raise SystemExit(f"Microphone capture failed: {exc}") from exc
        audio = recording.reshape(-1)
        print(f"Final window {index}: {transcribe(model, audio, args.language)!r}")
    print("Done. Fixed-window boundaries may split words; use a true streaming STT API for production.")


if __name__ == "__main__":
    main()
