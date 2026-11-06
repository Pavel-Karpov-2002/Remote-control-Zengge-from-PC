# Zengge Windows 版

语言 / Language: [Русский](README.md) · [English](README.en.md) · **中文** · [Deutsch](README.de.md) · [Polski](README.pl.md)

通过 Bluetooth LE 控制 LEDnetWF 灯具：连接多盏灯、设置 RGB 颜色和亮度、根据音乐频谱改变效果、运行平滑的 Fade 渐变，或匹配 Windows 桌面的平均颜色。

**[下载最新 Windows x64 版本](https://github.com/Pavel-Karpov-2002/Remote-control-Zengge-from-PC/releases/latest/download/ZenggeColorRemote.exe)**

版本 0.4.0。应用包含独立的“颜色”“音乐”“Fade”和“屏幕”选项卡。界面支持俄语、英语、简体中文、德语和波兰语。首次启动时使用 Windows 显示语言，也可以在应用中切换；选择会被保存。

无需安装 Python。从 [Releases](https://github.com/Pavel-Karpov-2002/Remote-control-Zengge-from-PC/releases) 下载并运行 `ZenggeColorRemote.exe`。

## 连接灯具

1. 打开电脑的 Bluetooth 并给灯具通电。如果手机应用占用了连接，请将其关闭。
2. 点击“查找”，选择灯具并点击“连接”。
3. 选择下一盏灯并连接。需要时再次搜索。
4. 已连接的灯具会收到相同的颜色、亮度、电源和效果命令。
5. 要断开某盏灯，请在列表中选中它并点击“断开所选设备”。按住 Ctrl 或 Shift 可选择多行。关闭窗口时会断开所有灯具。

一盏灯断开不会停止其他灯。可同时连接的数量以及连接期间能否搜索，取决于 Bluetooth 适配器和驱动程序。连接新灯不会取消现有连接。应用显示的是选中或发送的颜色，并非灯具确认后的状态。

## 颜色和亮度

点击“打开”。在“颜色”选项卡中，通过“调色板…”选择颜色，或输入 0–255 的 RGB 值，然后点击“应用颜色”。共享的“亮度”滑块（0–100%）控制手动亮度，也限制音乐模式的最高亮度。

## 音乐

连接灯具并打开“音乐”选项卡。可手动选择音源，也可启用自动选择音源并在有声音时启动。Fade 和屏幕模式分别位于独立选项卡，并有各自的启动按钮。灯具会自动开启。

| 设置 | 功能 |
| --- | --- |
| 音源 | Windows 默认输出的所有声音，或包含其子进程的指定应用程序 |
| 刷新 | 更新所有活动输出上的窗口和音频会话列表；无需先开始播放 |
| 频率混音器 | 对数频谱，可设置频率范围、触发阈值和自定义颜色渐变。双击添加节点，按住鼠标左键拖动，右键删除。 |
| 频谱配置 | 保存频率范围、阈值、渐变和所选灯具。切换配置时会切换连接的灯具。 |
| 灵敏度 | 用于检测频率的信号增益；本身不会改变亮度 |
| 音乐最低亮度 | 亮度下限；在此基础上叠加音频信号，最高为 100% |
| 亮度随音乐变化 | 根据音量改变亮度；关闭后亮度保持不变 |
| 脉冲强度 | 亮度变化幅度：0% 表示恒定，100% 表示最大响应 |
| 平滑度 | 平滑颜色和亮度过渡；数值越高，变化越慢、越柔和 |
| Fade | 像混音器一样在渐变条上设置颜色。Fade 有独立调色板配置、亮度和手动输入的毫秒过渡时间。 |
| 屏幕 | 匹配所有 Windows 显示器画面的平均颜色，并可单独调节亮度。 |

设置会在启动之间保留。应用会重新连接先前保存的灯具。鼠标滚轮可调节指针下方的滑块。

**暂停、静音和曲目结束时会保持最后的颜色和亮度。** 启用音乐亮度响应时也如此。声音恢复后效果继续。点击“停止”结束效果并恢复手动颜色；点击“关闭”结束效果并关闭所有已连接灯具。

更换音源前请先停止效果。应用重启后，刷新列表并重新选择音源。窗口标题可帮助识别应用，但采集以进程及其子进程为单位，无法区分浏览器标签页。可提前选择尚无音频流的窗口，开始播放后即会生效。没有窗口或音频会话的后台应用可能暂时不会显示。

系统声音使用 WASAPI loopback 采集，无需麦克风。频谱在本地分析，音频不会保存或上传。屏幕平均颜色通过 Windows GDI 和虚拟桌面采集，包括扩展显示器。单个应用采集需要 Windows build 20348+ / Windows 11；旧版本可使用系统声音。如果无法单独采集应用，程序会报告错误，不会自动改用系统声音。受 DRM 保护的音频可能无法采集。所选音源中的语音和系统声音也会影响音乐模式。

## 构建

需要 Windows、Python 3.12 x64 和 Tkinter：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
.\build.ps1
```

构建输出：`dist/ColorRemote/ZenggeColorRemote.exe`。可执行文件通过 Releases 发布，不提交到 Git 历史。

## 协议与兼容性

协议基于 [8none1/zengge_lednetwf](https://github.com/8none1/zengge_lednetwf)，提交 `f4d20fc3225e4b8b5637b5951fff59d91882a53c`。服务 UUID 为 FFFF，写入特征为 FF01，通知特征为 FF02。RGB 按控制器精度转换为文档所述 HSV 3B A1 数据包。传输使用 Bleak/WinRT；无需 Linux 或 Home Assistant。

原作者已将后续研究移至 [lednetwf_ble](https://github.com/8none1/lednetwf_ble)。不同型号和固件的命令可能不同。本版本不支持单独控制 LED，也不支持控制器内置效果。
