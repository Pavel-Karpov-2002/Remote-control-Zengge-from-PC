import asyncio
import queue
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from bluetooth import Bluetooth, Connection
from lighting import SmoothColor, music_light
from music import MusicAnalyzer

class FakeClient:
    def __init__(self, fail=False):
        self.is_connected = True
        self.packets = []
        self.active = self.peak = 0
        self.fail = fail
    async def write_gatt_char(self, char, packet, response):
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(.002)
            if self.fail:
                raise RuntimeError('lost')
            self.packets.append(bytes(packet))
        finally:
            self.active -= 1
    async def disconnect(self):
        self.is_connected = False

class MultiLampTests(unittest.IsolatedAsyncioTestCase):
    def make_worker(self):
        b=Bluetooth.__new__(Bluetooth)
        b.events=queue.Queue()
        b.connections={}
        for address in ('A','B'):
            b.connections[address]=Connection(FakeClient(), SimpleNamespace(properties=['write']), address)
        return b

    async def test_independent_counters_broadcast_and_disconnect(self):
        b=self.make_worker()
        a,c=b.connections.values()
        await b.color((255,0,0))
        self.assertEqual(a.client.packets[0],c.client.packets[0])
        await b.disconnect(['A'])
        self.assertEqual(list(b.connections),['B'])
        await b.color((0,255,0))
        self.assertEqual(len(c.client.packets),2)
        self.assertEqual(len(a.client.packets),1)
        self.assertTrue(c.client.is_connected)

    async def test_failed_lamp_does_not_stop_healthy_lamp(self):
        b=self.make_worker()
        b.connections['A'].client.fail=True
        c=b.connections['B']
        await b.music_color((200,100,0))
        self.assertEqual(list(b.connections), ['B'])
        await b.music_color((20,100,0))
        self.assertEqual(len(c.client.packets),2)

    async def test_all_writes_serial_per_lamp(self):
        b=self.make_worker()
        await asyncio.gather(*(b.color((i,0,0)) for i in range(10)))
        for c in b.connections.values():
            self.assertEqual(c.client.peak,1)
            self.assertEqual([p[1] for p in c.client.packets],list(range(1,11)))

    async def test_failed_new_connection_preserves_existing(self):
        b=self.make_worker()
        class FailingClient(FakeClient):
            services=SimpleNamespace(get_service=lambda _:None)
            async def connect(self):
                return None
        client=FailingClient()
        with patch('bluetooth.BleakClient', return_value=client):
            with self.assertRaises(RuntimeError):
                await b.connect(SimpleNamespace(address='C',name='third'))
        self.assertEqual(set(b.connections),{'A','B'})
        self.assertFalse(client.is_connected)

class SmoothnessTests(unittest.TestCase):
    def test_transition_is_gradual_and_converges(self):
        s=SmoothColor((255,0,0))
        first=s.update((0,255,0),0,.4)
        self.assertGreater(first[0],200)
        self.assertGreater(first[1],0)
        for i in range(1,100):
            last=s.update((0,255,0),i*.05,.4)
        self.assertLess(last[0],3)
        self.assertEqual(last[1],255)
    def test_strength_is_independent_of_maximum(self):
        weak,_=music_light((50,0,0),50,True,strength=0)
        strong,_=music_light((50,0,0),50,True,strength=100)
        self.assertEqual(weak,(128,0,0))
        self.assertEqual(strong,(25,0,0))
    def test_silence_freezes_last_audible_color(self):
        a=MusicAnalyzer(48000)
        signal=.2*np.sin(2*np.pi*90*np.arange(2048)/48000)
        for i in range(30):
            rgb,_=a.process(signal,1,2,i*.05)
        self.assertTrue(a.audible)
        self.assertGreater(max(rgb),0)
        for i in range(100):
            silent,level=a.process(np.zeros(2048),1,2,2+i*.05)
        self.assertEqual(silent,rgb)
        self.assertEqual(level,0)
        self.assertFalse(a.audible)

class DiscoveryTests(unittest.TestCase):
    def test_silent_window_is_listed_without_audio_session(self):
        import psutil
        from audio_sources import mixer_sources
        import subprocess,sys
        child=subprocess.Popen(['powershell.exe','-NoProfile','-Command','Start-Sleep -Seconds 20'], creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            with patch('audio_sources.window_processes',return_value=[(child.pid,'Silent player')]), patch('pycaw.pycaw.AudioUtilities.GetAllDevices',return_value=[]):
                sources=mixer_sources()
            self.assertTrue(any(s.pid==child.pid for s in sources))
        finally:
            child.terminate()
            child.wait(timeout=5)

