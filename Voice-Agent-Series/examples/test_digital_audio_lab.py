"""Run: python -m unittest discover -s examples -p 'test_*.py'"""
import tempfile
import unittest
from pathlib import Path

from digital_audio_lab import analyze, write_demo


class TestAudioLab(unittest.TestCase):
    def test_format_and_duration(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / "test.wav"
            write_demo(dest)
            result = analyze(dest)
            self.assertEqual(result["sample_rate"], 16_000)
            self.assertEqual(result["channels"], 1)
            self.assertEqual(result["bit_depth"], 16)
            self.assertEqual(result["frames"], 16_000)
            self.assertEqual(result["duration_s"], 1)

    def test_twenty_millisecond_chunks(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / "test.wav"
            write_demo(dest)
            result = analyze(dest, chunk_ms=20)
            self.assertEqual(result["chunk_bytes"], 640)
            self.assertEqual(result["first_chunk_bytes"], 640)
            self.assertEqual(result["chunks"], 50)

    def test_signal_levels(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / "test.wav"
            write_demo(dest)
            result = analyze(dest)
            self.assertAlmostEqual(result["peak_normalized"], 0.30, delta=0.01)
            self.assertAlmostEqual(result["rms_normalized"], 0.30 / 2**0.5, delta=0.01)

    def test_invalid_chunk_ms(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / "test.wav"
            write_demo(dest)
            with self.assertRaises(ValueError):
                analyze(dest, chunk_ms=0)


if __name__ == "__main__":
    unittest.main()
