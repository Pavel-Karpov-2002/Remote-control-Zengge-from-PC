"""Discover Windows mixer sessions and capture only a selected process tree."""
from dataclasses import dataclass
import sys
import numpy as np

@dataclass(frozen=True)
class AudioSource:
    pid: int
    name: str
    created: float
    title: str = ''

    @property
    def label(self):
        title = f' — {self.title[:60]}' if self.title else ''
        return f'{self.name}{title} (PID {self.pid})'


def window_processes():
    """Visible top-level app windows exist even before an audio session does."""
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    windows = []
    @callback_type
    def visit(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length:
                title = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, title, length + 1)
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                windows.append((pid.value, title.value))
        return True
    user32.EnumWindows(visit, 0)
    return windows


def mixer_sources(active_only=False):
    import os
    import comtypes
    import psutil
    from pycaw.pycaw import AudioUtilities
    from pycaw.constants import AudioSessionState
    from pycaw.api.audiopolicy import IAudioSessionControl2
    from pycaw.utils import AudioSession
    found = {}
    def add(process, title=''):
        try:
            while True:
                parent = process.parent()
                if parent is None or parent.name().lower() != process.name().lower():
                    break
                process = parent
            if process.pid == os.getpid():
                return
            previous = found.get(process.pid)
            if previous and not title:
                return
            found[process.pid] = AudioSource(process.pid, process.name(), process.create_time(), title)
        except (psutil.Error, AttributeError):
            pass
    # Enumerate windows first: sessions alone omit apps that have never played audio.
    if not active_only:
        for pid, title in window_processes():
            try:
                add(psutil.Process(pid), title)
            except psutil.Error:
                pass
    comtypes.CoInitialize()
    try:
        # Every active output, including inactive sessions; not just the default output.
        for device in AudioUtilities.GetAllDevices(data_flow=0, device_state=1):
            try:
                enumerator = device.AudioSessionManager.GetSessionEnumerator()
                for i in range(enumerator.GetCount()):
                    control = enumerator.GetSession(i).QueryInterface(IAudioSessionControl2)
                    session = AudioSession(control)
                    if active_only and session.State != AudioSessionState.Active:
                        continue
                    process = session.Process
                    if process is not None:
                        add(process)
            except (comtypes.COMError, OSError):
                continue
    except (comtypes.COMError, OSError):
        if not found:
            raise
    finally:
        comtypes.CoUninitialize()
    return sorted(found.values(), key=lambda source: (source.name.lower(), source.pid))


def capture_process(owner, source):
    import psutil
    from proctap._native import ProcessLoopback
    from music import MusicAnalyzer
    if sys.getwindowsversion().build < 20348:
        raise RuntimeError('Захват приложения требует Windows build 20348+ или Windows 11. Выберите весь системный звук.')
    process = psutil.Process(source.pid)
    if process.create_time() != source.created:
        raise RuntimeError('Приложение перезапущено. Обновите список и выберите его снова.')
    tap = ProcessLoopback(source.pid)
    try:
        tap.start()
        if not tap.is_process_specific():
            raise RuntimeError('Windows не разрешила отдельный захват приложения. Общий звук не используется; выберите другой источник.')
        fmt = tap.get_format()
        rate, channels = int(fmt['sample_rate']), int(fmt['channels'])
        bits = int(fmt['bits_per_sample'])
        if bits not in (16, 32):
            raise RuntimeError('Неподдерживаемый формат захвата приложения.')
        analyzer = MusicAnalyzer(rate)
        owner.events.put(('ready', source.label))
        import time
        last_audio = time.monotonic()
        pending = np.empty(0, dtype=np.float32)
        while not owner.stop_event.wait(0.025):
            if not process.is_running():
                raise RuntimeError('Выбранное приложение закрыто. Обновите список источников.')
            raw = tap.read()
            now = time.monotonic()
            if raw:
                samples = np.frombuffer(raw, dtype=np.float32 if bits == 32 else np.int16).astype(np.float32)
                if bits == 16:
                    samples /= 32768.0
                pending = np.concatenate((pending, samples))[-8192 * channels:]
                last_audio = now
                while pending.size >= 2048 * channels:
                    owner.analyze(analyzer, pending[:2048 * channels], channels, now)
                    pending = pending[2048 * channels:]
            elif now - last_audio > 0.1:
                owner.analyze(analyzer, np.zeros(2048 * channels, dtype=np.float32), channels, now)
    finally:
        tap.stop()
