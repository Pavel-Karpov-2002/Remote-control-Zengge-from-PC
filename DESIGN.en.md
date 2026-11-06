---
name: Zengge Color Remote
colors:
  background: "#1D2029"
  surface: "#333541"
  foreground: "#F4F6FA"
  muted: "#BFC3D3"
  accent: "#FFD7C1"
typography:
  body:
    fontFamily: Segoe UI
    fontSize: 10pt
spacing:
  outer: 24px
  columns: 28px
---
Language / Язык: [Русский](DESIGN.md) · **English** · [中文](DESIGN.zh.md) · [Deutsch](DESIGN.de.md) · [Polski](DESIGN.pl.md)

# Zengge Color Remote
## Overview
Windows desktop control app for LEDnetWF. Supports multiple BLE connections, shared brightness and power, RGB color, frequency-based music response, Fade, and matching the average color of displays. Interface languages: Russian, English, Simplified Chinese, German, and Polish; defaults to the Windows display language and allows manual selection.
## Colors
Dark blue-gray background with a peach accent. Text inside the color circle uses black or white based on relative luminance, with a 0.179 threshold.
## Typography
Segoe UI 10pt; title 21pt bold; HEX 20pt bold. Active tab 12pt bold, inactive tab 10pt.
## Layout
Window 1040×800, minimum 960×760. Left 350px: device search, connection, lamp list, selected disconnect, brightness, and power. Right side has four separate tabs: Color, Music, Fade, and Screen. Three-line status area at the bottom.
## Shapes
Color circle up to 270px. Flat buttons. Active tab is larger: 22×12px padding and peach fill; inactive tab uses 14×6px padding and secondary surface.
## Components
Color: circle with HEX, palette, RGB, and explicit apply action. Music: system or process source, auto-start, sensitivity, minimum brightness, reactive brightness, pulse strength, and smoothing. Frequency mixer shows a logarithmic spectrum, range, adjustable threshold, and editable gradient with profiles. Fade: custom color gradient, profiles, and manually entered transition time in milliseconds. Screen: average color across displays and separate brightness. All modes share BLE transport, smoothing, and brightness scaling.
Palette is a custom HSV window: saturation/value field, hue strip, current/new swatches, HEX/RGB, confirm/cancel. Arrow keys control the field and hue. The system color chooser is not used. Selection does not send a lamp command until applied.
