"""Local-only WASAPI loopback capture and music envelope/onset analysis."""
import colorsys
import math
import queue
import threading
import time
import numpy as np


DEFAULT_COLOR_MAP = ((40, (255, 0, 0)), (12000, (255, 255, 255)))


def interpolate_color(frequency, points):
    """Return the RGB color assigned to a pitch by the editable gradient."""
    points = sorted(points or DEFAULT_COLOR_MAP, key=lambda point: point[0])
    if frequency <= points[0][0]:
        return points[0][1]
    for (left_hz, left_rgb), (right_hz, right_rgb) in zip(points, points[1:]):
        if frequency <= right_hz:
            span = max(1e-9, math.log(right_hz / left_hz))
            amount = min(1.0, max(0.0, math.log(max(left_hz, frequency) / left_hz) / span))
            return tuple(round(a + (b - a) * amount) for a, b in zip(left_rgb, right_rgb))
    return points[-1][1]


class MusicAnalyzer:
    SPECTRUM_LOW = 35
    SPECTRUM_HIGH = 12000
    SPECTRUM_BANDS = 48

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
        self.spectrum = (0.0,) * self.SPECTRUM_BANDS
        self.frequency = 0
        self.band_level = 0.0
        self._edges = tuple(self.SPECTRUM_LOW * (self.SPECTRUM_HIGH / self.SPECTRUM_LOW) ** (i / self.SPECTRUM_BANDS)
                            for i in range(self.SPECTRUM_BANDS + 1))

    def process(self, samples, channels, gain, now, frequency_low=40, frequency_high=8000,
                threshold=0.008, color_map=None, min_brightness=20):
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
            self.spectrum = (0.0,) * self.SPECTRUM_BANDS
            self.frequency = 0
            self.band_level = 0.0
            return self.last_rgb, 0

        window = np.hanning(len(mono))
        spectrum = np.abs(np.fft.rfft(mono * window)) * (2 / max(float(window.sum()), 1))
        frequencies = np.fft.rfftfreq(len(mono), 1 / self.rate)
        bands = []
        for left, right in zip(self._edges[:-1], self._edges[1:]):
            region = spectrum[(frequencies >= left) & (frequencies < right)]
            bands.append(float(np.linalg.norm(region)))
        # Keep the vertical spectrum scale independent from the trigger control.
        # The dashed threshold line can then move to the actual trigger level.
        self.spectrum = tuple(min(1.0, value * max(0.1, float(gain)) / 0.12) for value in bands)

        floor = max(self.SPECTRUM_LOW, min(float(frequency_low), self.rate / 2))
        ceiling = max(floor + 1, min(float(frequency_high), self.rate / 2))
        selected = (frequencies >= floor) & (frequencies <= ceiling)
        selected_spectrum = spectrum[selected]
        selected_frequencies = frequencies[selected]
        # Keep the measured signal level independent of sensitivity/gain.
        self.band_level = float(np.linalg.norm(selected_spectrum))
        trigger_level = self.band_level * max(0.1, float(gain))
        self.frequency = 0
        if trigger_level >= threshold and selected_spectrum.size and float(selected_spectrum.max()) > 0:
            # Use the dominant spectral peak for pitch-to-color mapping. A
            # centroid across the whole range drifts into the mids/highs when
            # many quiet harmonics are present, even while the bass is dominant.
            peak = int(np.argmax(selected_spectrum))
            self.frequency = round(float(selected_frequencies[peak]))

        bass = float(np.linalg.norm(spectrum[(frequencies >= 40) & (frequencies <= 220)]))
        self.beat = bass > max(0.003 / gain, self.average * 1.55) and now - self.last_beat > 0.22
        if self.beat:
            self.target_hue = (self.target_hue + 0.137) % 1
            self.last_beat = now
        average_alpha = 1 - math.exp(-dt / 0.7)
        self.average += (bass - self.average) * average_alpha

        if self.frequency:
            # Map pitch on a musical/log scale with fixed endpoints. The trigger
            # range filters what is heard; it must not remap bass into blue just
            # because the selected range spans several octaves.
            pitch_low, pitch_high = 40.0, min(12000.0, self.rate / 2)
            position = min(1.0, max(0.0, math.log(max(pitch_low, self.frequency) / pitch_low) /
                                    max(0.001, math.log(pitch_high / pitch_low))))
            mapped_rgb = interpolate_color(self.frequency, color_map)
            hue, saturation, mapped_value = colorsys.rgb_to_hsv(*(channel / 255 for channel in mapped_rgb))
            minimum = min(100.0, max(0.0, float(min_brightness))) / 100
            # Drive the pulse envelope from the unamplified broadband RMS.
            # Narrow-band FFT energy can exceed this range even on moderate
            # music and pin brightness at 100%, hiding the minimum control.
            audio_level = min(1.0, max(0.0, rms * 3.0))
            brightness_target = min(1.0, minimum + audio_level)
            tau = 0.12 if brightness_target > self.envelope else 0.28
            self.envelope += (brightness_target - self.envelope) * (1 - math.exp(-dt / tau))
            self.hue = hue
            self.last_rgb = tuple(round(v * 255) for v in colorsys.hsv_to_rgb(
                hue, saturation, mapped_value * self.envelope))
        return self.last_rgb, min(100, round(rms * gain * 400))


class MusicCapture:
    def __init__(self):
        self.events = queue.Queue()
        self.thread = None
        self.stop_event = threading.Event()
        self.gain = 2.0
        self.frequency_low = 40
        self.frequency_high = 8000
        self.trigger_threshold = 0.008
        self.min_brightness = 20
        self.color_map = DEFAULT_COLOR_MAP
        self.source = None
        self.latest = ((0, 0, 0), 0)
        self.audible = False
        self.spectrum = (0.0,) * MusicAnalyzer.SPECTRUM_BANDS
        self.frequency = 0
        self.band_level = 0.0

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
        self.spectrum = (0.0,) * MusicAnalyzer.SPECTRUM_BANDS
        self.frequency = 0
        self.band_level = 0.0
        self.thread = threading.Thread(target=self._capture, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def analyze(self, analyzer, samples, channels, now):
        self.latest = analyzer.process(
            samples, channels, self.gain, now,
            self.frequency_low, self.frequency_high, self.trigger_threshold, self.color_map,
            self.min_brightness,
        )
        self.audible = analyzer.audible
        self.spectrum = analyzer.spectrum
        self.frequency = analyzer.frequency
        self.band_level = analyzer.band_level
        frames = np.asarray(samples).reshape(-1, channels)
        channel = int(np.argmax(np.mean(frames * frames, axis=0)))
        mono = frames[:, channel]
        # Rolling history of actual PCM samples; no decorative animation.

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

