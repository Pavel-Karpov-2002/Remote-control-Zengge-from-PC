# Product
Language / Язык: [Русский](PRODUCT.md) · **English** · [中文](PRODUCT.zh.md) · [Deutsch](PRODUCT.de.md) · [Polski](PRODUCT.pl.md)
<!-- impeccable:product-schema 1 -->

## Platform
Windows desktop x64, Python 3.12, Tkinter, Bleak/WinRT.

## Purpose
Desktop app for controlling LEDnetWF over Bluetooth LE: multiple lamps, RGB, shared brightness, frequency-based music response, Fade, and screen color matching. UI languages are Russian, English, Simplified Chinese, German, and Polish; the default follows the Windows display language, with a saved in-app selector.

## Capabilities and constraints
Commands go to all connected lamps; selected lamps can be disconnected. Losing one connection does not cancel the others. Actual adapter capacity depends on hardware.
Audio sources: all system audio or an application process with child processes. Lists visible windows and sessions on active output devices before playback starts.
Audio spectrum with draggable frequency boundaries and a vertical threshold. Low notes map to red and high notes to white; brightness responds to energy in the selected band. Sensitivity, pulse strength, reactive brightness, and smoothing are available.
Fade cycles continuously through colors or individual shades, with separate brightness and cycle timing. Screen mode uses the average color across connected desktop monitors and has its own brightness control.
During silence or a pause, retain the last color and brightness. Stopping an effect restores manual color; power-off turns lamps off.
Audio is not recorded or sent over the network. Per-LED groups are out of scope.

## Distribution
Source: Pavel-Karpov-2002/Remote-control-Zengge-from-PC. Executables/installers belong in GitHub Releases, not Git history.

## Visual requirements
Compact dark desktop panel with familiar Windows controls and five selectable interface languages.
