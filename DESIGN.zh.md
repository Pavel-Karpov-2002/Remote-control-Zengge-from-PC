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
语言 / Language: [Русский](DESIGN.md) · [English](DESIGN.en.md) · **中文** · [Deutsch](DESIGN.de.md) · [Polski](DESIGN.pl.md)

# Zengge Color Remote
## 概览
用于控制 LEDnetWF 的 Windows 桌面应用。支持多个 BLE 连接、统一亮度和电源、RGB 颜色、音乐频谱响应、Fade 渐变以及匹配显示器的平均颜色。界面语言：俄语、英语、简体中文、德语和波兰语。默认采用 Windows 显示语言，也可手动选择。
## 颜色
深蓝灰背景和桃色强调色。色环中的文字根据相对亮度使用黑色或白色，阈值为 0.179。
## 字体
Segoe UI 10pt；标题 21pt 粗体；HEX 20pt 粗体。当前选项卡 12pt 粗体，其他选项卡 10pt。
## 布局
窗口 1040×800，最小 960×760。左侧 350px：搜索、连接、灯具列表、断开所选设备、亮度和电源。右侧四个独立选项卡：颜色、音乐、Fade、屏幕。底部三行状态区。
## 形状
色环最大 270px。扁平按钮。当前选项卡较大：内边距 22×12px、桃色填充；其他选项卡内边距 14×6px，使用次级表面颜色。
## 组件
颜色：带 HEX 的色环、调色板、RGB 和明确的应用操作。音乐：系统或进程音源、自动启动、灵敏度、最低亮度、响应式亮度、脉冲强度和平滑度。频率混音器显示对数频谱、范围、可调阈值和带配置的可编辑渐变。Fade：自定义颜色渐变、配置和手动输入的毫秒过渡时间。屏幕：所有显示器的平均颜色和独立亮度。所有模式共用 BLE 传输、平滑处理和亮度缩放。
调色板是自定义 HSV 窗口：饱和度/明度区域、色相条、当前/新颜色预览、HEX/RGB 和确认/取消。方向键控制区域和色相。不使用系统颜色选择器。只有点击应用后才会向灯具发送颜色命令。
