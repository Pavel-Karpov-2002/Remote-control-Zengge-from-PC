import queue
import threading
import unittest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from audio_sources import AudioSource, capture_process

class SourceSafetyTests(unittest.TestCase):
    def test_system_fallback_is_rejected(self):
        source = AudioSource(123, 'player.exe', 10.0)
        owner = SimpleNamespace(stop_event=threading.Event(), events=queue.Queue(), gain=2)
        with patch('psutil.Process') as process, patch('proctap._native.ProcessLoopback') as native:
            process.return_value.create_time.return_value = 10.0
            native.return_value.is_process_specific.return_value = False
            with self.assertRaisesRegex(RuntimeError, 'Общий звук не используется'):
                capture_process(owner, source)
            native.return_value.stop.assert_called_once()
            native.return_value.read.assert_not_called()

    def test_reused_pid_is_rejected(self):
        source = AudioSource(123, 'player.exe', 10.0)
        with patch('psutil.Process') as process, patch('proctap._native.ProcessLoopback') as native:
            process.return_value.create_time.return_value = 20.0
            with self.assertRaisesRegex(RuntimeError, 'перезапущено'):
                capture_process(None, source)
            native.assert_not_called()
