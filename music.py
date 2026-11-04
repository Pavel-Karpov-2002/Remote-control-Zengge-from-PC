"""Local-only WASAPI loopback capture and music envelope/onset analysis."""
import colorsys
import math
import queue
import threading
import time
import numpy as np


class MusicAnalyzer:
    def __init__(self, rate):
        self.rate = rate
        self.average = 0.001
        self.envelope = 0.0
        self.hue = 0.02
        self.last_beat = -1.0
        self.beat = False
        self.audible = False
        self.target_hue = self.hue
        self.last_time = None
        self.last_rgb = (0, 0, 0)

    def process(self, samples, channels, gain, now):
        frames = np.asarray(samples, dtype=np.float32).reshape(-1, channels)
        # Select the loudest channel: opposite-phase stereo must not cancel out.
        energies = np.mean(frames * frames, axis=0)
        mono = frames[:, int(np.argmax(energies))]
        rms = float(np.sqrt(np.max(energies)))
        self.audible = rms > 0.002
        dt = len(mono) / self.rate if self.last_time is None else max(0.001, min(0.15, now - self.last_time))
        self.last_time = now
        if not self.audible:
            self.beat = False
            return self.last_rgb, 0
        spectrum = np.abs(np.fft.rfft(mono * np.hanning(len(mono)))) / len(mono)
        frequencies = np.fft.rfftfreq(len(mono), 1 / self.rate)
        bass = float(np.linalg.norm(spectrum[(frequencies >= 40) & (frequencies <= 220)]))
        self.beat = bass > max(0.003 / gain, self.average * 1.55) and now - self.last_beat > 0.22
        if self.beat:
            self.target_hue = (self.target_hue + 0.137) % 1
            self.last_beat = now
        average_alpha = 1 - math.exp(-dt / 0.7)
        self.average += (bass - self.average) * average_alpha
        hue_delta = (self.target_hue - self.hue + 0.5) % 1 - 0.5
        self.hue = (self.hue + hue_delta * (1 - math.exp(-dt / 0.25))) % 1
        target = min(1.0, max(0.0, (rms - 0.002) * gain * 4))
        # Time-based envelope remains smooth at any callback rate.
        tau = 0.18 if target > self.envelope else 0.45
        self.envelope += (target - self.envelope) * (1 - math.exp(-dt / tau))
        brightness = self.envelope
        rgb = tuple(round(v * 255) for v in colorsys.hsv_to_rgb(self.hue, 1.0, brightness))
        self.last_rgb = rgb
        return rgb, min(100, round(rms * gain * 400))


class MusicCapture:
    def __init__(self):
        self.events = queue.Queue()
        self.thread = None
        self.stop_event = threading.Event()
        self.gain = 2.0
        self.source = None
        self.wave = tuple(0.0 for _ in range(512))
        self.latest = ((0, 0, 0), 0)
        self.audible = False

    @property
    def running(self):
        return self.thread is not None and self.thread.is_alive()

    def start(self, source=None):
        if self.running:
            raise RuntimeError('Захват звука ещё останавливается. Повторите через секунду.')
        self.source = source
        self.stop_event.clear()
        self.latest = ((0, 0, 0), 0)
        self.audible = False
        self.thread = threading.Thread(target=self._capture, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def analyze(self, analyzer, samples, channels, now):
        self.latest = analyzer.process(samples, channels, self.gain, now)
        self.audible = analyzer.audible
        frames = np.asarray(samples).reshape(-1, channels)
        channel = int(np.argmax(np.mean(frames * frames, axis=0)))
        mono = frames[:, channel]
        # Rolling history of actual PCM samples; no decorative animation.
        points = mono[np.linspace(0, len(mono) - 1, 128).astype(int)]
        self.wave = (self.wave + tuple(float(v) for v in points))[-512:]

    def _capture(self):
        if self.source is not None:
            try:
                from audio_sources import capture_process
                capture_process(self, self.source)
            except Exception as exc:
                self.events.put(('error', str(exc) or type(exc).__name__))
            finally:
                self.events.put(('stopped', ''))
            return
        try:
            import pyaudiowpatch as pa
        except Exception as exc:
            self.events.put(('error', str(exc)))
            self.events.put(('stopped', ''))
            return
        chunks = queue.Queue(maxsize=1)
        def callback(data, count, info, status):
            try:
                chunks.get_nowait()
            except queue.Empty:
                pass
            try:
                chunks.put_nowait(data)
            except queue.Full:
                pass
            return (None, pa.paComplete if self.stop_event.is_set() else pa.paContinue)
        try:
            with pa.PyAudio() as audio:
                device = audio.get_default_wasapi_loopback()
                channels = int(device['maxInputChannels'])
                rate = int(device['defaultSampleRate'])
                analyzer = MusicAnalyzer(rate)
                with audio.open(format=pa.paFloat32, channels=channels, rate=rate,
                                frames_per_buffer=2048, input=True,
                                input_device_index=int(device['index']), stream_callback=callback) as stream:
                    self.events.put(('ready', device['name']))
                    while not self.stop_event.is_set():
                        try:
                            raw = chunks.get(timeout=0.1)
                            samples = np.frombuffer(raw, dtype=np.float32)
                        except queue.Empty:
                            if not stream.is_active():
                                raise RuntimeError('Аудиоустройство отключилось. Выберите выход Windows и запустите режим снова.')
                            samples = np.zeros(2048 * channels, dtype=np.float32)
                        if samples.size:
                            self.analyze(analyzer, samples, channels, time.monotonic())
        except Exception as exc:
            self.events.put(('error', str(exc) or type(exc).__name__))
        finally:
            self.events.put(('stopped', ''))

