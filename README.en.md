# Zengge for Windows

Language / Язык: [Русский](README.md) · **English** · [中文](README.zh.md) · [Deutsch](README.de.md) · [Polski](README.pl.md)

Control LEDnetWF lamps over Bluetooth LE: connect multiple lamps, set RGB color and brightness, react to music frequencies, run smooth Fade effects, or match the average desktop color.

**[Download the latest Windows x64 release](https://github.com/Pavel-Karpov-2002/Remote-control-Zengge-from-PC/releases/latest/download/ZenggeColorRemote.exe)**

Version 0.4.0. The app includes separate Color, Music, Fade, and Screen tabs. The interface supports Russian, English, Simplified Chinese, German, and Polish. On first launch it follows the Windows display language; you can change it in the app and the choice is saved.

Python is not required. Download and run `ZenggeColorRemote.exe` from [Releases](https://github.com/Pavel-Karpov-2002/Remote-control-Zengge-from-PC/releases).

## Connecting lamps

1. Turn on Bluetooth on the PC and power on the lamp. Close the phone app if it is holding the connection.
2. Click **Find**, select a lamp, and click **Connect**.
3. Select another lamp and connect it. Repeat the search if needed.
4. Connected lamps share color, brightness, power, and effect commands.
5. To disconnect a lamp, select it in the list and click **Disconnect selected**. Use Ctrl or Shift to select several rows. Closing the window disconnects all lamps.

A lost connection to one lamp does not stop the others. The number of simultaneous connections and scanning while connected depend on the Bluetooth adapter and driver. A new connection does not cancel existing ones. The color shown in the app is the selected or transmitted value, not a confirmed lamp state.

## Color and brightness

Click **Turn on**. In the Color tab, choose a shade with **Palette…** or enter RGB values (0–255), then click **Apply color**. The shared **Brightness** control (0–100%) sets manual brightness and limits the music mode’s maximum.

## Music

Connect lamps and open the Music tab. Choose an audio source manually, or enable automatic source selection and start when sound begins. Fade and Screen are separate tabs, each with its own start button. Lamps turn on automatically.

| Setting | What it does |
| --- | --- |
| Audio source | All audio from the default Windows output, or a selected application including its child processes |
| Refresh | Updates the list of windows and audio sessions on active outputs; playback does not need to be started first |
| Frequency mixer | Logarithmic spectrum with a selectable range, adjustable trigger threshold, and custom color gradient. Add points with a double-click, move with left-drag, and delete with right-click. |
| Spectrum profiles | Save the frequency range, threshold, gradient, and selected lamps. Selecting a profile switches the connected lamps. |
| Sensitivity | Signal gain for frequency detection; it does not change brightness by itself |
| Minimum music brightness | Brightness floor; the audio level is added to it and the result is capped at 100% |
| Brightness reacts to music | Enables brightness changes from audio level; otherwise brightness stays constant |
| Pulse strength | Depth of brightness changes: 0% is constant, 100% is the strongest response |
| Smoothing | Smooths color and brightness transitions; higher values make transitions slower and softer |
| Fade | Set colors on a gradient bar like the mixer. Fade has its own palette profiles, brightness, and manually entered transition time in milliseconds. |
| Screen | Matches color to the average image across Windows monitors, with a separate brightness control. |

Settings persist between launches. The app reconnects to previously saved lamps. The mouse wheel adjusts the slider under the pointer.

**During pauses, silence, and the end of a track, the last color and brightness are held.** This also applies when reactive brightness is enabled. Changes resume when audio returns. **Stop** ends the effect and restores the manual color. **Turn off** stops the effect and switches off all connected lamps.

Stop the effect before changing its source. If an app has restarted, refresh the list and select it again. Window titles help identify apps, but capture follows the process and its child processes; browser tabs cannot be separated. A window without an audio stream can be selected in advance and becomes active when it starts playback. Background apps without a window or audio session may not appear until a session exists.

System audio uses WASAPI loopback; no microphone is needed. Spectrum analysis runs locally: audio is not saved or sent over the network. Average screen color is captured with Windows GDI and the virtual desktop, including additional monitors. Capturing individual applications requires Windows build 20348+ / Windows 11. Older versions support system audio. If per-app capture is unavailable, the app reports an error instead of switching to system audio. DRM-protected audio may be unavailable. Speech and system sounds also affect the music mode when included in the selected source.

## Build

Windows with Python 3.12 x64 and Tkinter:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
.\build.ps1
```

Build output: `dist/ColorRemote/ZenggeColorRemote.exe`. Executables are published in Releases, not committed to Git.

## Protocol and compatibility

The protocol is based on [8none1/zengge_lednetwf](https://github.com/8none1/zengge_lednetwf), commit `f4d20fc3225e4b8b5637b5951fff59d91882a53c`. Service UUID FFFF, write characteristic FF01, notifications FF02. RGB is converted to the documented HSV 3B A1 packet at controller precision. Transport uses Bleak/WinRT; Linux and Home Assistant are not required.

The original author moved further research to [lednetwf_ble](https://github.com/8none1/lednetwf_ble). Commands may vary by model and firmware. Per-LED addressing and built-in controller effects are not implemented in this version.
