import unittest
import numpy as np
from lighting import dim, music_light
from music import MusicAnalyzer, MusicCapture

class BrightnessTests(unittest.TestCase):
    def test_limits_and_scaling(self):
        self.assertEqual(dim((255,128,64),0), (0,0,0))
        self.assertEqual(dim((200,100,20),50), (100,50,10))
        self.assertEqual(dim((255,128,64),100), (255,128,64))
    def test_music_brightness_modes(self):
        reactive, _ = music_light((60,0,0),50,True)
        steady, _ = music_light((60,0,0),50,False)
        self.assertEqual(reactive,(30,0,0))
        self.assertEqual(steady,(128,0,0))
        silence, _ = music_light((0,0,0),50,True)
        self.assertEqual(silence,(0,0,0))
        held, _ = music_light((0,0,0),50,False,0)
        self.assertEqual(held,(128,0,0))
    def test_wave_is_captured_pcm_and_clears(self):
        capture=MusicCapture()
        analyzer=MusicAnalyzer(48000)
        tone=np.sin(np.arange(2048)*.1).astype(np.float32)*.1
        capture.analyze(analyzer,tone,1,0)
        self.assertGreater(max(capture.wave),.05)
        self.assertLess(min(capture.wave),-.05)
        for i in range(4):
            capture.analyze(analyzer,np.zeros(2048,dtype=np.float32),1,i)
        self.assertTrue(all(v==0 for v in capture.wave))
