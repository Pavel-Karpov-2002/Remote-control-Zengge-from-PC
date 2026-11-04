import asyncio
from concurrent.futures import Future
import queue
import unittest
from unittest.mock import patch
import numpy as np
from music import MusicAnalyzer, MusicCapture

class AnalyzerTests(unittest.TestCase):
    def test_beat_and_silence(self):
        analyzer = MusicAnalyzer(48000)
        silence = np.zeros(2048, dtype=np.float32)
        self.assertEqual(analyzer.process(silence, 1, 2, 0)[0], (0,0,0))
        bass = (0.4 * np.sin(2 * np.pi * 80 * np.arange(2048) / 48000)).astype(np.float32)
        rgb, level = analyzer.process(bass, 1, 2, 1)
        self.assertTrue(analyzer.beat)
        hue = analyzer.hue
        self.assertGreater(max(rgb), 0)
        analyzer.process(bass, 1, 2, 1.05)
        self.assertFalse(analyzer.beat)  # onset refractory interval
        held = rgb = analyzer.last_rgb
        for i in range(40):
            rgb, level = analyzer.process(silence, 1, 2, 2 + i * .05)
        self.assertEqual(rgb, held)
        self.assertEqual(level, 0)

    def test_antiphase_stereo_and_gain(self):
        signal = .02 * np.sin(2 * np.pi * 1000 * np.arange(2048) / 48000)
        stereo = np.column_stack((signal, -signal)).ravel()
        low, _ = MusicAnalyzer(48000).process(stereo, 2, .5, 0)
        high, _ = MusicAnalyzer(48000).process(stereo, 2, 8, 0)
        self.assertGreater(max(low), 0)
        self.assertGreater(max(high), max(low))

class FakeBluetooth:
    def __init__(self):
        self.events = queue.Queue()
        self.calls = []
    def submit(self, action, *args):
        f = Future()
        self.calls.append((action, args, f))
        return f

class FakeCapture:
    running = False
    latest = ((240,0,0), 50)
    audible = True
    def __init__(self):
        self.events = queue.Queue()
    def start(self, source=None):
        self.running = True
    def stop(self):
        self.running = False

class MusicGuiTests(unittest.TestCase):
    def test_backpressure_stop_and_restore(self):
        import tkinter as tk
        from app import App
        root = tk.Tk()
        with patch('app.Bluetooth', FakeBluetooth), patch('app.MusicCapture', FakeCapture):
            app = App(root)
        try:
            app.connected = True
            app.toggle_music()
            self.assertTrue(app.music_active)
            app.busy = False
            app.poll_music()
            count = len(app.ble.calls)
            app.music.latest = ((0,240,0), 60)
            for _ in range(20):
                app.poll_music()
            self.assertEqual(len(app.ble.calls), count)
            app.stop_music()
            app.poll_music()
            self.assertEqual(len(app.ble.calls), count)
            app.music_future.set_result(None)
            app.poll_music()
            self.assertEqual(app.ble.calls[-1][:2], ('color', ((255,128,64),)))
            self.assertFalse(app.music_active)
        finally:
            root.destroy()

