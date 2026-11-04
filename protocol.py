"""LEDnetWF wire protocol, based on 8none1/zengge_lednetwf."""
import colorsys

SERVICE = '0000ffff-0000-1000-8000-00805f9b34fb'
WRITE = '0000ff01-0000-1000-8000-00805f9b34fb'
NOTIFY = '0000ff02-0000-1000-8000-00805f9b34fb'

class Protocol:
    def __init__(self):
        self.counter = 0

    def prepare(self, template):
        packet = bytearray.fromhex(template)
        self.counter = self.counter % 255 + 1
        # First byte is fragmentation flags, second is the command counter.
        packet[1] = self.counter
        packet[-1] = sum(packet[8:-1]) & 255
        return packet

    def initialize(self):
        return self.prepare('00 01 80 00 00 04 05 0a 81 8a 8b 96')

    def power(self, enabled):
        packet = self.prepare('00 04 80 00 00 0d 0e 0b 3b 23 00 00 00 00 00 00 00 32 00 00 90')
        packet[9] = 0x23 if enabled else 0x24
        packet[-1] = sum(packet[8:-1]) & 255
        return packet

    def rgb(self, r, g, b):
        if any(type(v) is not int or not 0 <= v <= 255 for v in (r, g, b)):
            raise ValueError('RGB должен содержать целые числа от 0 до 255')
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        packet = self.prepare('00 05 80 00 00 0d 0e 0b 3b a1 00 64 64 00 00 00 00 00 00 00 00')
        packet[10:13] = bytes((int(h * 180), int(s * 100), int(v * 100)))
        packet[-1] = sum(packet[8:-1]) & 255
        return packet
