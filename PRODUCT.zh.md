# Product
语言 / Language: [Русский](PRODUCT.md) · [English](PRODUCT.en.md) · **中文** · [Deutsch](PRODUCT.de.md) · [Polski](PRODUCT.pl.md)
<!-- impeccable:product-schema 1 -->

## 平台
Windows x64 桌面应用，Python 3.12、Tkinter、Bleak/WinRT。

## 用途
通过 Bluetooth LE 控制 LEDnetWF 的桌面应用：支持多盏灯、RGB、统一亮度、音乐频谱响应、Fade 和屏幕颜色匹配。界面支持俄语、英语、简体中文、德语和波兰语。默认采用 Windows 显示语言；应用内选择会保存。

## 功能和限制
命令发送给所有已连接灯具；可断开所选灯具。一盏灯断开不会取消其他连接。实际连接数量取决于硬件。
音源包括所有系统声音，或包含子进程的应用进程。播放前即可列出活动输出设备上的可见窗口和音频会话。
音频频谱具有可拖动的频率边界和垂直阈值。低音映射为红色，高音映射为白色；亮度随选中频段的能量变化。提供灵敏度、脉冲强度、响应式亮度和平滑度。
Fade 可连续循环颜色或逐个切换色调，并可独立设置亮度和循环时间。屏幕模式使用桌面所有显示器的平均颜色，并有独立亮度设置。
静音或暂停时保留最后的颜色和亮度。停止效果后恢复手动颜色；关闭电源则关闭灯具。
音频不会被录制或发送到网络。不支持单独控制 LED 分组。

## 发布
源代码：Pavel-Karpov-2002/Remote-control-Zengge-from-PC。EXE 和安装程序发布在 GitHub Releases，不提交至 Git 历史。

## 视觉要求
紧凑的深色桌面面板，使用熟悉的 Windows 控件并支持五种界面语言。
