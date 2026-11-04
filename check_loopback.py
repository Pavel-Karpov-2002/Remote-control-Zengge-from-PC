"""Manual integration check: two processes, only one emits a quiet test tone."""
import subprocess
import sys
import time
import wave
from pathlib import Path
import numpy as np
import psutil
from audio_sources import AudioSource
from music import MusicCapture

if __name__ == '__main__':
    path = Path('build/loopback-test.wav').resolve()
    with wave.open(str(path), 'wb') as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(48000)
        tone = (np.sin(2*np.pi*180*np.arange(48000)/48000)*900).astype(np.int16)
        out.writeframes(tone.tobytes())
    player = subprocess.Popen([sys.executable, '-c', 'import winsound,time,sys; winsound.PlaySound(sys.argv[1],winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_LOOP); time.sleep(20)', str(path)])
    silent = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(20)'])
    try:
        time.sleep(.4)
        levels = []
        for child in (silent, player):
            proc = psutil.Process(child.pid)
            capture = MusicCapture()
            capture.start(AudioSource(proc.pid,proc.name(),proc.create_time()))
            maximum = 0
            for _ in range(25):
                time.sleep(.05)
                maximum = max(maximum, capture.latest[1])
            capture.stop()
            capture.thread.join(4)
            errors = [event for event in list(capture.events.queue) if event[0]=='error']
            if errors:
                raise RuntimeError(errors)
            levels.append(maximum)
        print('Levels (silent process, tone process):', levels)
        assert levels[0] == 0 and levels[1] > 0, levels
        print('Per-process isolation: PASS')
    finally:
        for child in (player, silent):
            child.terminate()
            child.wait(timeout=5)
        path.unlink(missing_ok=True)
