"""Brightness policy shared by static and music modes."""
import colorsys
import math

def dim(rgb, percent):
    scale = min(100, max(0, float(percent))) / 100
    return tuple(round(channel * scale) for channel in rgb)

def music_light(rgb, percent, reactive=True, previous_hue=0.02, strength=100):
    hue, saturation, value = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    if value > 0:
        previous_hue = hue
    if reactive:
        depth = min(100, max(0, strength)) / 100
        value = 1 - depth * (1 - value)
        adjusted = tuple(round(v * 255) for v in colorsys.hsv_to_rgb(previous_hue, 1, value))
        return dim(adjusted, percent), previous_hue
    full = tuple(round(v * 255) for v in colorsys.hsv_to_rgb(previous_hue, 1, 1))
    return dim(full, percent), previous_hue


class SmoothColor:
    """Shortest hue interpolation and independent, time-based brightness smoothing."""
    def __init__(self, rgb=(255,128,64)):
        self.hsv = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
        self.last_time = None

    def update(self, rgb, now, seconds=0.4):
        target_h, target_s, target_v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
        hue, saturation, value = self.hsv
        if target_v == 0:
            target_h, target_s = hue, saturation
        elif value < 0.001 or saturation < 0.01:
            hue = target_h
        dt = .05 if self.last_time is None else max(0, min(.2, now-self.last_time))
        self.last_time = now
        alpha = 1 - math.exp(-dt / max(.05, seconds))
        hue = (hue + ((target_h-hue+.5) % 1-.5)*alpha) % 1
        saturation += (target_s-saturation)*alpha
        value += (target_v-value)*alpha
        self.hsv = (hue, saturation, value)
        return tuple(round(v*255) for v in colorsys.hsv_to_rgb(*self.hsv))
