import math
import tempfile
import unittest
import wave
from pathlib import Path
from tts_metrics_lab import (
    pcm_bytes_per_second, frame_bytes, real_time_factor, inspect_wav
)


class TTSAudioMetricsTests(unittest.TestCase):
    def test_pcm_rate(self):
        self.assertEqual(pcm_bytes_per_second(24000, 1, 2), 48000)

    def test_20ms_pcm_frame(self):
        self.assertEqual(frame_bytes(24000, 1, 2, 20), 960)

    def test_stereo_frame(self):
        self.assertEqual(frame_bytes(16000, 2, 2, 20), 1280)

    def test_fractional_sample_boundary_rejected(self):
        with self.assertRaises(ValueError):
            frame_bytes(22050, 1, 2, 1)

    def test_invalid_format_rejected(self):
        with self.assertRaises(ValueError):
            pcm_bytes_per_second(24000, 0, 2)

    def test_rtf(self):
        self.assertAlmostEqual(real_time_factor(0.8, 4.0), 0.2)

    def test_rtf_bad_audio_duration(self):
        with self.assertRaises(ValueError):
            real_time_factor(1, 0)

    def test_rtf_nan_rejected(self):
        with self.assertRaises(ValueError):
            real_time_factor(math.nan, 2)

    def test_inspect_wav(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'tts.wav'
            with wave.open(str(path), 'wb') as output:
                output.setnchannels(1)
                output.setsampwidth(2)
                output.setframerate(24000)
                output.writeframes(b'\x00\x00' * 24000)
            stats = inspect_wav(path)
            self.assertEqual(stats.sample_rate, 24000)
            self.assertEqual(stats.frames, 24000)
            self.assertEqual(stats.duration_s, 1.0)


if __name__ == '__main__':
    unittest.main()
