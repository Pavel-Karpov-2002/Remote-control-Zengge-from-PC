import colorsys
import ctypes
import json
import math
import os
import queue
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import simpledialog, ttk
from color_picker import ask_color
from bluetooth import Bluetooth
from music import MusicCapture, DEFAULT_COLOR_MAP
from lighting import dim, music_light, SmoothColor

BG, FG, MUTED, PANEL = '#1D2029', '#F4F6FA', '#BFC3D3', '#333541'
ACCENT = '#FFD7C1'
APP_VERSION = '0.4.0'
DEFAULT_FADE_COLORS = ((35, (255, 0, 0)), (90, (255, 115, 25)),
                       (230, (255, 235, 40)), (600, (40, 230, 85)),
                       (1600, (20, 190, 255)), (4200, (95, 55, 255)),
                       (8000, (245, 45, 200)), (12000, (255, 0, 0)))

class App:
    def __init__(self, root):
        self.root = root
        self.ble = Bluetooth()
        self.music = MusicCapture()
        self.settings_path = Path(os.environ.get('APPDATA', str(Path.home()))) / 'ZenggeColorRemote' / 'settings.json'
        try:
            self.saved_settings = json.loads(self.settings_path.read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            self.saved_settings = {}
        if not isinstance(self.saved_settings, dict):
            self.saved_settings = {}
        try:
            self.color_map = [(int(point[0]), tuple(int(channel) for channel in point[1]))
                              for point in self.saved_settings.get('color_map', DEFAULT_COLOR_MAP)]
        except (TypeError, ValueError, IndexError):
            self.color_map = list(DEFAULT_COLOR_MAP)
        if len(self.color_map) < 2:
            self.color_map = list(DEFAULT_COLOR_MAP)
        try:
            self.fade_color_map = [(int(point[0]), tuple(int(channel) for channel in point[1]))
                                   for point in self.saved_settings.get('fade_color_map', DEFAULT_FADE_COLORS)]
        except (TypeError, ValueError, IndexError):
            self.fade_color_map = list(DEFAULT_FADE_COLORS)
        if len(self.fade_color_map) < 2:
            self.fade_color_map = list(DEFAULT_FADE_COLORS)
        self.fade_profiles = self.saved_settings.get('fade_profiles', {})
        if not isinstance(self.fade_profiles, dict):
            self.fade_profiles = {}
        self.music.color_map = tuple(self.color_map)
        self.music.frequency_low = max(35, min(11900, int(self.saved_settings.get('frequency_low', 40))))
        self.music.frequency_high = max(self.music.frequency_low + 40,
                                        min(12000, int(self.saved_settings.get('frequency_high', 8000))))
        self.music.trigger_threshold = max(.003, min(.12, float(self.saved_settings.get('trigger_threshold', .008))))
        self.music.min_brightness = max(0, min(100, float(self.saved_settings.get('music_min_brightness', 20))))
        self.spectrum_profiles = self.saved_settings.get('spectrum_profiles', {})
        if not isinstance(self.spectrum_profiles, dict):
            self.spectrum_profiles = {}
        self.remembered_devices = {str(address).lower() for address in self.saved_settings.get('devices', [])}
        self.auto_connect_queue = []
        self.auto_connecting = False
        self.profile_connect_targets = None
        self.profile_missing_devices = set()
        self.current_auto_device = None
        self.auto_refreshing = False
        self.active_audio_sources = []
        self.auto_start_on_audio = tk.BooleanVar(value=bool(self.saved_settings.get('auto_start_on_audio', True)))
        self.auto_start_blocked = False
        self.settings_save_job = None
        self.music_active = False
        self.effect_active = False
        self.effect_mode = 'music'
        self.music_future = None
        self.restore_color = None
        self.last_music_rgb = None
        self.music_hue = 0.02
        self.brightness_job = None
        self.music_last_input = (255,128,64)
        self.transition = SmoothColor()
        self.fade_started = 0.0
        self.music_fade = tk.BooleanVar(value=bool(self.saved_settings.get('music_fade', False)))
        self.music_fade_speed = tk.DoubleVar(value=float(self.saved_settings.get('music_fade_speed', .25)))
        self.fade_brightness = tk.DoubleVar(value=float(self.saved_settings.get('fade_brightness', 75)))
        self.fade_tone_ms = tk.IntVar(value=int(self.saved_settings.get('fade_tone_ms', 800)))
        self.screen_brightness = tk.DoubleVar(value=float(self.saved_settings.get('screen_brightness', 85)))
        self.screen_color = None
        self.screen_stop = threading.Event()
        self.connections = {}
        self.connected = False
        self.busy = False
        self.closing = False
        self.devices = []
        self.sources = [None]
        self.refreshing_sources = False
        root.title(f'Zengge • Color Remote v{APP_VERSION}')
        root.geometry('1040x800')
        root.minsize(960, 760)
        root.configure(bg=BG)
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('.', background=BG, foreground=FG, font=('Segoe UI', 10))
        style.configure('TButton', padding=(12, 10), background=PANEL, foreground=FG, borderwidth=0)
        style.configure('Primary.TButton', background=ACCENT, foreground='#35231C', font=('Segoe UI', 11, 'bold'), padding=(14, 12))
        style.map('Primary.TButton', background=[('disabled', '#383139'), ('pressed', '#EDBA9D'), ('active', '#FFE5D6')], foreground=[('disabled', '#A89CA3')])
        style.configure('Remote.TNotebook', background=BG, borderwidth=0, bordercolor=BG, lightcolor=BG, darkcolor=BG)
        style.layout('Remote.TNotebook.Tab', [])
        style.configure('TScale', background=BG, troughcolor=PANEL)
        style.configure('TProgressbar', background=ACCENT, troughcolor=PANEL, borderwidth=0)
        style.configure('TCheckbutton', background=BG, foreground=FG)
        style.map('TCheckbutton', background=[('active', BG)])
        style.map('TButton', background=[('active', '#414452'), ('disabled', '#272A34')], foreground=[('disabled', '#9195A5')])
        style.configure('TCombobox', fieldbackground=PANEL, background=PANEL, foreground=FG, padding=6)
        style.map('TCombobox', fieldbackground=[('readonly', PANEL)], foreground=[('readonly', FG)])
        style.configure('TNotebook.Tab', padding=(16, 8))
        style.map('TNotebook.Tab', background=[('selected', PANEL), ('active', '#414452')], foreground=[('selected', ACCENT), ('!selected', MUTED)])
        style.configure('Treeview', background=PANEL, fieldbackground=PANEL, foreground=FG, rowheight=26)
        style.configure('Treeview.Heading', background=BG, foreground=MUTED, relief='flat')
        style.map('Treeview', background=[('selected', '#575163')], foreground=[('selected', FG)])
        style.configure('TSpinbox', fieldbackground=PANEL, foreground=FG, arrowsize=16)
        root.option_add('*TCombobox*Listbox.background', PANEL)
        root.option_add('*TCombobox*Listbox.foreground', FG)
        shell = ttk.Frame(root, padding=24)
        shell.pack(fill='both', expand=True)
        header = ttk.Frame(shell)
        header.pack(fill='x', pady=(0, 20))
        ttk.Label(header, text='Zengge', font=('Segoe UI', 21, 'bold')).pack(side='left')
        ttk.Label(header, text='Color Remote', foreground=MUTED).pack(side='right')
        self.status = tk.StringVar(value='Включите Bluetooth и нажмите «Найти».')
        status_label = tk.Label(shell, textvariable=self.status, bg=BG, fg=MUTED, font=('Segoe UI', 10), height=3, anchor='w', justify='left', wraplength=920)
        status_label.pack(side='bottom', fill='x', pady=(16, 0))
        body = ttk.Frame(shell)
        body.pack(fill='both', expand=True)
        frame = ttk.Frame(body, width=350)
        frame.pack(side='left', fill='y', padx=(0, 28))
        frame.pack_propagate(False)
        right = ttk.Frame(body)
        right.pack(side='left', fill='both', expand=True)
        shell.bind('<Configure>', lambda e: status_label.configure(wraplength=max(300, e.width-48)))
        row = ttk.Frame(frame)
        row.pack(fill='x')
        ttk.Label(row, text='Лампы', font=('Segoe UI', 11, 'bold')).pack(side='left')
        self.scan_button = ttk.Button(row, text='Найти', command=self.scan)
        self.scan_button.pack(side='right')
        self.device = ttk.Combobox(frame, state='readonly')
        self.device.pack(fill='x', pady=(8, 8))
        self.device.bind('<<ComboboxSelected>>', lambda _: self.controls())
        row = ttk.Frame(frame)
        row.pack(fill='x')
        self.connect_button = ttk.Button(row, text='Подключить', command=self.connect)
        self.connect_button.pack(side='left')
        self.disconnect_button = ttk.Button(row, text='Отключить выбранные', command=lambda: self.run('disconnect', list(self.connection_list.selection())))
        self.disconnect_button.pack(side='left', padx=(8, 0))
        self.connection_list = ttk.Treeview(frame, columns=('address',), height=5, selectmode='extended')
        self.connection_list.heading('#0', text='Подключённые лампы')
        self.connection_list.heading('address', text='Адрес Bluetooth')
        self.connection_list.column('#0', width=155, minwidth=90)
        self.connection_list.column('address', width=150, minwidth=100)
        self.connection_list.pack(fill='x', pady=(8, 0))
        self.connection_list.bind('<<TreeviewSelect>>', lambda _: self.controls())
        self.connection_summary = tk.StringVar(value='Нет подключений. Команды будут отправляться всем лампам.')
        ttk.Label(frame, textvariable=self.connection_summary, foreground=MUTED, wraplength=330).pack(anchor='w', pady=(8, 0))
        row = ttk.Frame(frame)
        row.pack(fill='x', pady=(16, 8))
        ttk.Label(row, text='Яркость').pack(side='left')
        self.brightness = tk.DoubleVar(value=100)
        self.brightness_text = tk.StringVar(value='100%')
        ttk.Scale(row, from_=0, to=100, variable=self.brightness,
                  command=self.change_brightness).pack(side='left', fill='x', expand=True, padx=12)
        ttk.Label(row, textvariable=self.brightness_text, width=5).pack(side='right')
        row = ttk.Frame(frame)
        row.pack(fill='x', pady=(0, 16))
        self.on_button = ttk.Button(row, text='Включить', command=lambda: self.run('power', True))
        self.on_button.pack(side='left', fill='x', expand=True, padx=(0, 6))
        self.off_button = ttk.Button(row, text='Выключить', command=lambda: self.run('power', False))
        self.off_button.pack(side='left', fill='x', expand=True, padx=(6, 0))
        tab_bar = ttk.Frame(right)
        tab_bar.pack(fill='x', pady=(0, 10))
        self.tab_buttons = []
        for index, title in enumerate(('Цвет', 'Музыка', 'Fade', 'Экран')):
            button = tk.Button(tab_bar, text=title, command=lambda i=index: self.tabs.select(i), relief='flat', borderwidth=0, cursor='hand2', takefocus=True, highlightthickness=1, highlightbackground=BG, highlightcolor=ACCENT)
            button.pack(side='left', anchor='s', padx=(0, 10))
            self.tab_buttons.append(button)
        self.tabs = ttk.Notebook(right, style='Remote.TNotebook')
        self.tabs.pack(fill='both', expand=True, pady=(0, 12))
        color_frame = ttk.Frame(self.tabs, padding=12)
        music_frame = ttk.Frame(self.tabs, padding=12)
        self.fade_controls = ttk.Frame(self.tabs, padding=12)
        self.screen_controls = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(color_frame, text='Цвет')
        self.tabs.add(music_frame, text='Музыка')
        self.tabs.add(self.fade_controls, text='Fade')
        self.tabs.add(self.screen_controls, text='Экран')
        self.tabs.bind('<<NotebookTabChanged>>', self.update_tabs)
        self.tabs.enable_traversal()
        self.update_tabs()
        self.selected_color = '#FF8040'
        self.preview = tk.Canvas(color_frame, height=200, bg=BG, highlightthickness=0)
        self.preview.pack(fill='both', expand=True, pady=(8, 8))
        self.preview.bind('<Configure>', self.draw_preview)
        ttk.Button(color_frame, text='Палитра…', command=self.pick).pack(pady=(0, 18))
        self.rgb = [tk.StringVar(value=str(v)) for v in (255, 128, 64)]
        row = ttk.Frame(color_frame)
        row.pack(fill='x')
        for i, label in enumerate(('R', 'G', 'B')):
            col = ttk.Frame(row)
            col.pack(side='left', fill='x', expand=True, padx=(0, 8) if i < 2 else 0)
            ttk.Label(col, text=label, foreground=MUTED).pack(anchor='w')
            spin = ttk.Spinbox(col, from_=0, to=255, textvariable=self.rgb[i], width=8)
            spin.pack(fill='x', pady=(4, 0))
            self.rgb[i].trace_add('write', self.update_preview)
        row = ttk.Frame(color_frame)
        row.pack(fill='x', pady=16)
        self.apply_button = ttk.Button(row, text='Применить цвет', style='Primary.TButton', command=self.apply)
        self.apply_button.pack(fill='x', expand=True)
        ttk.Label(color_frame, text='Предпросмотр цвета, а не подтверждённое состояние ламп.', foreground=MUTED, wraplength=440, anchor='center', justify='center').pack(fill='x', pady=(0, 8))
        self.audio_view = ttk.Frame(music_frame)
        self.audio_scroll = tk.Canvas(self.audio_view, background=BG, highlightthickness=0,
                                      yscrollincrement=24)
        self.audio_scroll.pack(side='left', fill='both', expand=True)
        self.audio_scrollbar = ttk.Scrollbar(self.audio_view, orient='vertical', command=self.audio_scroll.yview)
        self.audio_scrollbar.pack(side='right', fill='y')
        self.audio_scroll.configure(yscrollcommand=self.audio_scrollbar.set)
        self.audio_controls = ttk.Frame(self.audio_scroll)
        self.audio_window = self.audio_scroll.create_window((0, 0), window=self.audio_controls, anchor='nw')
        self.audio_controls.bind('<Configure>', lambda _: self.audio_scroll.configure(
            scrollregion=self.audio_scroll.bbox('all')))
        self.audio_scroll.bind('<Configure>', lambda event: self.audio_scroll.itemconfigure(
            self.audio_window, width=event.width))
        self.audio_view.bind_all('<MouseWheel>', self.scroll_audio_controls, add='+')
        self.audio_view.pack(fill='both', expand=True)

        row = ttk.Frame(self.audio_controls)
        row.pack(fill='x')
        ttk.Label(row, text='Источник', font=('Segoe UI', 11, 'bold')).pack(side='left')
        self.music_button = ttk.Button(row, text='Запустить', style='Primary.TButton', command=self.toggle_music)
        self.music_button.pack(side='right')
        row = ttk.Frame(self.audio_controls)
        row.pack(fill='x', pady=(6, 0))
        self.source_box = ttk.Combobox(row, state='readonly', values=['Весь системный звук'])
        self.source_box.pack(side='left', fill='x', expand=True)
        self.source_box.current(0)
        self.refresh_button = ttk.Button(row, text='Обновить', command=self.refresh_sources)
        self.refresh_button.pack(side='right', padx=(8, 0))
        ttk.Checkbutton(self.audio_controls, text='Автовыбор источника и запуск при появлении звука',
                        variable=self.auto_start_on_audio,
                        command=self.schedule_save_settings).pack(anchor='w', pady=(4, 2))
        self.audio_status = tk.StringVar(value='Звук с выхода Windows по умолчанию')
        audio_label = ttk.Label(self.audio_controls, textvariable=self.audio_status, foreground=MUTED, wraplength=440)
        audio_label.pack(fill='x', pady=(4, 6))
        music_frame.bind('<Configure>', lambda e: audio_label.configure(wraplength=max(240, e.width-24)))
        row = ttk.Frame(self.audio_controls)
        row.pack(fill='x')
        ttk.Label(row, text='Чувствительность').pack(side='left')
        self.gain = tk.DoubleVar(value=2)
        ttk.Scale(row, from_=0.5, to=8, variable=self.gain,
                  command=lambda value: setattr(self.music, 'gain', float(value))).pack(side='left', fill='x', expand=True, padx=12)
        min_brightness_row = ttk.Frame(self.audio_controls)
        min_brightness_row.pack(fill='x', pady=(4, 0))
        ttk.Label(min_brightness_row, text='Минимальная яркость музыки').pack(side='left')
        self.music_min_brightness = tk.DoubleVar(value=self.music.min_brightness)
        self.music_min_brightness_text = tk.StringVar(value=f'{round(self.music.min_brightness)}%')
        ttk.Scale(min_brightness_row, from_=0, to=100, variable=self.music_min_brightness,
                  command=self.update_music_min_brightness).pack(side='left', fill='x', expand=True, padx=12)
        ttk.Label(min_brightness_row, textvariable=self.music_min_brightness_text, width=5).pack(side='right')
        self.level = ttk.Progressbar(self.audio_controls, maximum=100)
        self.level.pack(fill='x', pady=(8, 12))
        self.reactive_brightness = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.audio_controls, text='Яркость в такт музыке', variable=self.reactive_brightness).pack(anchor='w', pady=(0, 12))
        row = ttk.Frame(self.audio_controls)
        row.pack(fill='x', pady=(0, 8))
        ttk.Label(row, text='Сила пульсации').pack(side='left')
        self.pulse_strength = tk.DoubleVar(value=70)
        self.pulse_text = tk.StringVar(value='70%')
        ttk.Scale(row, from_=0, to=100, variable=self.pulse_strength,
                  command=lambda value: self.pulse_text.set(f'{round(float(value))}%')).pack(side='left', fill='x', expand=True, padx=12)
        ttk.Label(row, textvariable=self.pulse_text, width=5).pack(side='right')
        row = ttk.Frame(self.audio_controls)
        row.pack(fill='x', pady=(0, 10))
        ttk.Label(row, text='Плавность').pack(side='left')
        self.smoothness = tk.DoubleVar(value=.4)
        ttk.Scale(row, from_=.1, to=1.2, variable=self.smoothness).pack(side='left', fill='x', expand=True, padx=12)
        ttk.Checkbutton(self.audio_controls, text='Fade: переливание оттенка в режиме музыки',
                        variable=self.music_fade).pack(anchor='w', pady=(0, 5))
        music_fade_row = ttk.Frame(self.audio_controls)
        music_fade_row.pack(fill='x', pady=(0, 8))
        ttk.Label(music_fade_row, text='Скорость Fade', foreground=MUTED).pack(side='left')
        self.music_fade_speed_text = tk.StringVar(value='4.0 с')
        ttk.Scale(music_fade_row, from_=.03, to=.8, variable=self.music_fade_speed,
                  command=lambda value: self.music_fade_speed_text.set(f'{1 / max(.01, float(value)):.1f} с')).pack(
            side='left', fill='x', expand=True, padx=12)
        ttk.Label(music_fade_row, textvariable=self.music_fade_speed_text, width=7).pack(side='right')
        ttk.Label(self.audio_controls, text='Частотный микшер', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(2, 7))
        spectrum_row = ttk.Frame(self.audio_controls)
        spectrum_row.pack(fill='x')
        self.spectrum = tk.Canvas(spectrum_row, height=100, background=PANEL, highlightthickness=0, takefocus=True)
        self.spectrum.pack(side='left', fill='both', expand=True)
        self.spectrum.bind('<Configure>', lambda _: self.draw_spectrum())
        self.spectrum.bind('<Button-1>', self.adjust_frequency_range)
        self.spectrum.bind('<B1-Motion>', self.adjust_frequency_range)
        threshold_panel = ttk.Frame(spectrum_row, padding=(12, 0, 0, 0))
        threshold_panel.pack(side='right', fill='y')
        ttk.Label(threshold_panel, text='Порог', foreground=MUTED).pack()
        self.trigger_threshold = tk.DoubleVar(value=self.music.trigger_threshold)
        self.threshold_scale = ttk.Scale(
            threshold_panel, from_=0.12, to=0.003, variable=self.trigger_threshold,
            orient='vertical', command=self.update_music_trigger,
        )
        self.threshold_scale.pack(fill='y', expand=True, pady=4)
        self.threshold_text = tk.StringVar(value='')
        ttk.Label(threshold_panel, textvariable=self.threshold_text, foreground=MUTED).pack()
        self.frequency_low = tk.IntVar(value=self.music.frequency_low)
        self.frequency_high = tk.IntVar(value=self.music.frequency_high)
        range_row = ttk.Frame(self.audio_controls)
        range_row.pack(fill='x', pady=(6, 0))
        ttk.Label(range_row, text='Диапазон', foreground=MUTED).pack(side='left')
        self.frequency_low_input = ttk.Spinbox(range_row, from_=35, to=11900, increment=10, width=7,
                                               textvariable=self.frequency_low, command=self.update_music_range)
        self.frequency_low_input.pack(side='left', padx=(8, 3))
        ttk.Label(range_row, text='—', foreground=MUTED).pack(side='left')
        self.frequency_high_input = ttk.Spinbox(range_row, from_=45, to=12000, increment=100, width=7,
                                                textvariable=self.frequency_high, command=self.update_music_range)
        self.frequency_high_input.pack(side='left', padx=(3, 5))
        ttk.Label(range_row, text='Гц', foreground=MUTED).pack(side='left')
        self.pitch_readout = tk.StringVar(value='Низкие ноты → красный     Высокие → белый')
        ttk.Label(range_row, textvariable=self.pitch_readout, foreground=MUTED).pack(side='right')
        self.frequency_low.trace_add('write', self.update_music_range)
        self.frequency_high.trace_add('write', self.update_music_range)
        ttk.Label(self.audio_controls, text='Цветовой градиент частот', foreground=MUTED).pack(anchor='w', pady=(8, 3))
        self.gradient = tk.Canvas(self.audio_controls, height=42, background=PANEL, highlightthickness=0,
                                  cursor='crosshair', takefocus=True)
        self.gradient.pack(fill='x')
        self.gradient.bind('<Configure>', lambda _: self.draw_gradient())
        self.gradient.bind('<Double-Button-1>', self.add_gradient_point)
        self.gradient.bind('<ButtonPress-1>', self.select_gradient_point)
        self.gradient.bind('<B1-Motion>', self.move_gradient_point)
        self.gradient.bind('<ButtonRelease-1>', lambda _: setattr(self, 'drag_gradient_index', None))
        self.gradient.bind('<Button-3>', self.delete_gradient_point)
        self.gradient.bind('<Delete>', self.delete_gradient_point)
        self.gradient_hint = tk.StringVar(value='Двойной щелчок — добавить/изменить цветовую точку')
        ttk.Label(self.audio_controls, textvariable=self.gradient_hint, foreground=MUTED).pack(anchor='w', pady=(2, 6))
        profile_row = ttk.Frame(self.audio_controls)
        profile_row.pack(fill='x', pady=(0, 8))
        ttk.Label(profile_row, text='Профиль').pack(side='left')
        self.profile_name = tk.StringVar()
        self.profile_box = ttk.Combobox(profile_row, textvariable=self.profile_name, state='readonly', width=15)
        self.profile_box.pack(side='left', fill='x', expand=True, padx=(8, 6))
        self.profile_box.bind('<<ComboboxSelected>>', lambda _: self.load_spectrum_profile())
        ttk.Button(profile_row, text='Загрузить', command=self.load_spectrum_profile).pack(side='left', padx=(0, 4))
        ttk.Button(profile_row, text='Сохранить…', command=self.save_spectrum_profile).pack(side='left', padx=(0, 4))
        ttk.Button(profile_row, text='Удалить', command=self.delete_spectrum_profile).pack(side='left')
        self.refresh_spectrum_profiles()
        self.update_music_trigger()
        self.draw_gradient()
        fade_start_row = ttk.Frame(self.fade_controls)
        fade_start_row.pack(fill='x', pady=(0, 12))
        ttk.Label(fade_start_row, text='Режим переливания', font=('Segoe UI', 11, 'bold')).pack(side='left')
        self.fade_button = ttk.Button(fade_start_row, text='Запустить', style='Primary.TButton', command=self.toggle_music)
        self.fade_button.pack(side='right')
        ttk.Label(self.fade_controls, text='Цветовой градиент Fade', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(4, 7))
        self.fade_gradient = tk.Canvas(self.fade_controls, height=48, background=PANEL, highlightthickness=0,
                                       cursor='crosshair', takefocus=True)
        self.fade_gradient.pack(fill='x')
        self.fade_gradient.bind('<Configure>', lambda _: self.draw_fade_gradient())
        self.fade_gradient.bind('<Double-Button-1>', self.add_fade_point)
        self.fade_gradient.bind('<ButtonPress-1>', self.select_fade_point)
        self.fade_gradient.bind('<B1-Motion>', self.move_fade_point)
        self.fade_gradient.bind('<ButtonRelease-1>', lambda _: setattr(self, 'drag_fade_index', None))
        self.fade_gradient.bind('<Button-3>', self.delete_fade_point)
        self.fade_gradient.bind('<Delete>', self.delete_fade_point)
        self.fade_gradient_hint = tk.StringVar(value='Двойной щелчок — добавить цвет · ЛКМ — двигать · ПКМ — удалить')
        ttk.Label(self.fade_controls, textvariable=self.fade_gradient_hint, foreground=MUTED).pack(anchor='w', pady=(2, 7))
        fade_profile_row = ttk.Frame(self.fade_controls)
        fade_profile_row.pack(fill='x', pady=(0, 12))
        ttk.Label(fade_profile_row, text='Профиль Fade').pack(side='left')
        self.fade_profile_name = tk.StringVar()
        self.fade_profile_box = ttk.Combobox(fade_profile_row, textvariable=self.fade_profile_name,
                                             state='readonly', width=14)
        self.fade_profile_box.pack(side='left', fill='x', expand=True, padx=(8, 6))
        self.fade_profile_box.bind('<<ComboboxSelected>>', lambda _: self.load_fade_profile())
        ttk.Button(fade_profile_row, text='Загрузить', command=self.load_fade_profile).pack(side='left', padx=(0, 4))
        ttk.Button(fade_profile_row, text='Сохранить…', command=self.save_fade_profile).pack(side='left', padx=(0, 4))
        ttk.Button(fade_profile_row, text='Удалить', command=self.delete_fade_profile).pack(side='left')
        self.refresh_fade_profiles()
        ttk.Label(self.fade_controls, text='Яркость переливания').pack(anchor='w', pady=(0, 4))
        fade_brightness_row = ttk.Frame(self.fade_controls)
        fade_brightness_row.pack(fill='x', pady=(0, 14))
        ttk.Scale(fade_brightness_row, from_=0, to=100, variable=self.fade_brightness,
                  command=lambda value: self.fade_brightness_text.set(f'{round(float(value))}%')).pack(side='left', fill='x', expand=True)
        self.fade_brightness_text = tk.StringVar(value='75%')
        ttk.Label(fade_brightness_row, textvariable=self.fade_brightness_text, width=5).pack(side='right', padx=(10, 0))
        ttk.Label(self.fade_controls, text='Время перехода на один оттенок (мс)').pack(anchor='w', pady=(0, 4))
        fade_speed_row = ttk.Frame(self.fade_controls)
        fade_speed_row.pack(fill='x')
        self.fade_tone_input = ttk.Spinbox(fade_speed_row, from_=1, to=60000, increment=10,
                                           textvariable=self.fade_tone_ms, width=10)
        self.fade_tone_input.pack(side='left')
        ttk.Label(fade_speed_row, text='мс на каждый переход', foreground=MUTED).pack(side='left', padx=(8, 0))
        self.draw_fade_gradient()
        screen_heading_row = ttk.Frame(self.screen_controls)
        screen_heading_row.pack(fill='x', pady=(4, 8))
        ttk.Label(screen_heading_row, text='Средний цвет экранов', font=('Segoe UI', 11, 'bold')).pack(side='left')
        self.screen_button = ttk.Button(screen_heading_row, text='Запустить', style='Primary.TButton', command=self.toggle_music)
        self.screen_button.pack(side='right')
        screen_brightness_row = ttk.Frame(self.screen_controls)
        screen_brightness_row.pack(fill='x', pady=(0, 12))
        ttk.Label(screen_brightness_row, text='Яркость').pack(side='left')
        self.screen_brightness_text = tk.StringVar(value='85%')
        ttk.Scale(screen_brightness_row, from_=0, to=100, variable=self.screen_brightness,
                  command=lambda value: self.screen_brightness_text.set(f'{round(float(value))}%')).pack(side='left', fill='x', expand=True, padx=12)
        ttk.Label(screen_brightness_row, textvariable=self.screen_brightness_text, width=5).pack(side='right')
        ttk.Label(self.screen_controls, text='Плавность', foreground=MUTED).pack(anchor='w', pady=(0, 4))
        screen_smoothness_row = ttk.Frame(self.screen_controls)
        screen_smoothness_row.pack(fill='x')
        ttk.Scale(screen_smoothness_row, from_=.1, to=1.2, variable=self.smoothness).pack(side='left', fill='x', expand=True)
        self.set_effect_mode('music')
        self.controls()
        self.refresh_sources()
        root.protocol('WM_DELETE_WINDOW', self.close)
        for setting in (self.auto_start_on_audio, self.music_fade, self.music_fade_speed,
                        self.fade_brightness, self.fade_tone_ms, self.screen_brightness,
                        self.frequency_low, self.frequency_high, self.trigger_threshold,
                        self.music_min_brightness):
            setting.trace_add('write', self.schedule_save_settings)
        self.bind_scale_wheels(root)
        root.after(50, self.poll)
        if self.remembered_devices:
            root.after(800, self.scan)
        root.after(1200, self.auto_detect_audio)

    def update_tabs(self, *_):
        selected = self.tabs.index('current')
        for index, button in enumerate(self.tab_buttons):
            active = index == selected
            button.configure(
                font=('Segoe UI', 12 if active else 10, 'bold' if active else 'normal'),
                padx=22 if active else 14, pady=12 if active else 6,
                bg=ACCENT if active else PANEL, fg='#35231C' if active else MUTED,
                activebackground='#FFE5D6' if active else '#414452',
                activeforeground='#35231C' if active else FG)
        mode_for_tab = {1: 'music', 2: 'fade', 3: 'screen'}
        mode = mode_for_tab.get(selected)
        if mode is None:
            if self.effect_active:
                self.stop_music(restore=True)
        else:
            self.set_effect_mode(mode)

    def set_effect_mode(self, mode):
        if mode == self.effect_mode:
            return
        if self.effect_active:
            self.stop_music(restore=True)
        self.effect_mode = mode
        self.controls()

    def set_preview(self, rgb):
        color = '#%02X%02X%02X' % rgb
        if color != self.selected_color:
            self.selected_color = color
            self.draw_preview()

    def draw_preview(self, *_):
        w, h = self.preview.winfo_width(), self.preview.winfo_height()
        diameter = min(270, w-24, h-16)
        if diameter < 40:
            return
        x, y = w/2, h/2
        self.preview.delete('all')
        self.preview.create_oval(x-diameter/2, y-diameter/2, x+diameter/2, y+diameter/2, fill=self.selected_color, outline='')
        rgb = tuple(int(self.selected_color[i:i+2], 16) for i in (1, 3, 5))
        def linear(v):
            v /= 255
            return v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4
        luminance = sum(weight*linear(v) for weight,v in zip((.2126,.7152,.0722),rgb))
        ink = '#000000' if luminance > .179 else '#FFFFFF'
        title = {'music': 'Музыка', 'fade': 'Fade', 'screen': 'Экран'}.get(self.effect_mode, 'Выбранный цвет') if self.effect_active else 'Выбранный цвет'
        self.preview.create_text(x,y-16,text=title,fill=ink,font=('Segoe UI',10))
        self.preview.create_text(x,y+16,text=self.selected_color,fill=ink,font=('Segoe UI',20,'bold'))

    def change_brightness(self, value):
        self.brightness_text.set(f'{round(float(value))}%')
        self.update_preview()
        if self.brightness_job is not None:
            self.root.after_cancel(self.brightness_job)
        self.brightness_job = self.root.after(160, self.send_brightness)

    def send_brightness(self):
        self.brightness_job = None
        if self.closing or not self.connected or self.effect_active:
            return
        if self.busy:
            self.brightness_job = self.root.after(100, self.send_brightness)
            return
        self.apply()

    def draw_wave(self):
        self.draw_spectrum()

    @staticmethod
    def spectrum_x(frequency):
        low, high = 35, 12000
        return math.log(max(low, min(high, float(frequency))) / low) / math.log(high / low)

    @staticmethod
    def trigger_db(value):
        return f'{20 * math.log10(max(float(value), 1e-6)):.0f} dB'

    def update_music_trigger(self, value=None):
        try:
            self.music.trigger_threshold = max(0.003, min(0.12, float(value if value is not None else self.trigger_threshold.get())))
            self.threshold_text.set(self.trigger_db(self.music.trigger_threshold))
            self.draw_spectrum()
            self.schedule_save_settings()
        except (ValueError, tk.TclError):
            pass

    def update_music_min_brightness(self, value):
        self.music.min_brightness = max(0.0, min(100.0, float(value)))
        self.music_min_brightness_text.set(f'{round(self.music.min_brightness)}%')
        self.schedule_save_settings()

    def update_music_range(self, *_):
        try:
            low = max(35, min(11900, int(self.frequency_low.get())))
            high = max(low + 40, min(12000, int(self.frequency_high.get())))
            if self.frequency_low.get() != low:
                self.frequency_low.set(low)
            if self.frequency_high.get() != high:
                self.frequency_high.set(high)
            self.music.frequency_low, self.music.frequency_high = low, high
            self.draw_spectrum()
            self.schedule_save_settings()
        except (ValueError, tk.TclError):
            pass

    def scroll_audio_controls(self, event):
        if event.widget.winfo_class() == 'TScale':
            return None
        widget = event.widget
        inside_audio = False
        while widget is not None:
            if widget is self.audio_view:
                inside_audio = True
                break
            widget = getattr(widget, 'master', None)
        if inside_audio:
            self.audio_scroll.yview_scroll(-1 if event.delta > 0 else 1, 'units')
            return 'break'

    def adjust_frequency_range(self, event):
        width = max(1, self.spectrum.winfo_width() - 12)
        position = min(1, max(0, (event.x - 6) / width))
        frequency = round(35 * (12000 / 35) ** position)
        low_position = self.spectrum_x(self.frequency_low.get())
        high_position = self.spectrum_x(self.frequency_high.get())
        if abs(position - low_position) <= abs(position - high_position):
            self.frequency_low.set(min(frequency, self.frequency_high.get() - 40))
        else:
            self.frequency_high.set(max(frequency, self.frequency_low.get() + 40))

    def gradient_x(self, frequency):
        width = max(1, self.gradient.winfo_width() - 12)
        return 6 + self.spectrum_x(frequency) * width

    def gradient_frequency(self, x):
        width = max(1, self.gradient.winfo_width() - 12)
        position = min(1, max(0, (x - 6) / width))
        return round(35 * (12000 / 35) ** position)

    def draw_gradient(self):
        if not hasattr(self, 'gradient') or not self.gradient.winfo_exists():
            return
        from music import interpolate_color
        canvas = self.gradient
        canvas.delete('all')
        width, height = max(120, canvas.winfo_width()), max(30, canvas.winfo_height())
        left, right = 6, width - 6
        for x in range(left, right):
            frequency = self.gradient_frequency(x)
            rgb = interpolate_color(frequency, self.color_map)
            color = '#%02X%02X%02X' % rgb
            canvas.create_line(x, 5, x, height - 13, fill=color)
        for index, (frequency, rgb) in enumerate(self.color_map):
            x = self.gradient_x(frequency)
            color = '#%02X%02X%02X' % rgb
            canvas.create_oval(x - 5, 5, x + 5, 15, fill=color, outline=ACCENT if index == getattr(self, 'selected_gradient', -1) else FG)
            canvas.create_text(x, height - 6, text=f'{frequency} Гц', fill=FG, font=('Segoe UI', 8))

    def add_gradient_point(self, event):
        frequency = self.gradient_frequency(event.x)
        nearest = min(range(len(self.color_map)), key=lambda index: abs(self.gradient_x(self.color_map[index][0]) - event.x))
        if abs(self.gradient_x(self.color_map[nearest][0]) - event.x) < 10:
            frequency = self.color_map[nearest][0]
        initial = self.color_map[nearest][1]
        color = ask_color(self.root, initial)
        if color:
            self.color_map = [point for point in self.color_map if point[0] != frequency]
            self.color_map.append((frequency, tuple(round(channel) for channel in color)))
            self.color_map.sort(key=lambda point: point[0])
            self.selected_gradient = next(i for i, point in enumerate(self.color_map) if point[0] == frequency)
            self.music.color_map = tuple(self.color_map)
            self.schedule_save_settings()
            self.gradient_hint.set(f'Точка {frequency} Гц · двойной щелчок меняет цвет · Delete удаляет точку')
            self.draw_gradient()
        return 'break'

    def select_gradient_point(self, event):
        if not self.color_map:
            return
        nearest = min(range(len(self.color_map)),
                      key=lambda index: abs(self.gradient_x(self.color_map[index][0]) - event.x))
        self.selected_gradient = nearest
        self.drag_gradient_index = nearest if abs(self.gradient_x(self.color_map[nearest][0]) - event.x) < 12 else None
        self.draw_gradient()

    def move_gradient_point(self, event):
        index = getattr(self, 'drag_gradient_index', None)
        if index is None or not 0 <= index < len(self.color_map):
            return
        frequency = self.gradient_frequency(event.x)
        minimum = self.color_map[index - 1][0] + 1 if index else 35
        maximum = self.color_map[index + 1][0] - 1 if index + 1 < len(self.color_map) else 12000
        frequency = min(maximum, max(minimum, frequency))
        color = self.color_map[index][1]
        self.color_map[index] = (frequency, color)
        self.color_map.sort(key=lambda point: point[0])
        self.selected_gradient = next(i for i, point in enumerate(self.color_map) if point[0] == frequency)
        self.drag_gradient_index = self.selected_gradient
        self.music.color_map = tuple(self.color_map)
        self.schedule_save_settings()
        self.gradient_hint.set(f'Точка {frequency} Гц · перетаскивайте ЛКМ, удаляйте ПКМ')
        self.draw_gradient()

    def delete_gradient_point(self, _event=None):
        index = getattr(self, 'selected_gradient', -1)
        if _event is not None and getattr(_event, 'num', None) == 3 and self.color_map:
            index = min(range(len(self.color_map)),
                        key=lambda i: abs(self.gradient_x(self.color_map[i][0]) - _event.x))
        if 0 <= index < len(self.color_map) and len(self.color_map) > 1:
            self.color_map.pop(index)
            self.selected_gradient = -1
            self.music.color_map = tuple(self.color_map)
            self.schedule_save_settings()
            self.gradient_hint.set('Точка удалена · ПКМ удаляет, ЛКМ перетаскивает')
            self.draw_gradient()
        return 'break'

    def draw_spectrum(self):
        if not hasattr(self, 'spectrum') or not self.spectrum.winfo_exists():
            return
        canvas = self.spectrum
        canvas.delete('all')
        width = max(120, canvas.winfo_width())
        height = max(64, canvas.winfo_height())
        pad, bottom, top = 7, height - 17, 7
        levels = getattr(self.music, 'spectrum', ())
        count = len(levels)
        if count:
            step = (width - 2 * pad) / count
            low_pos = self.spectrum_x(self.frequency_low.get())
            high_pos = self.spectrum_x(self.frequency_high.get())
            for index, level in enumerate(levels):
                center = (index + .5) / count
                selected = low_pos <= center <= high_pos
                bar_h = max(2, (bottom - top) * min(1, max(0, float(level))))
                if selected:
                    hue_pos = min(1, max(0, (center - low_pos) / max(.001, high_pos - low_pos)))
                    # Match the red-low to white-high note mapping shown by the live lamp.
                    hue = hue_pos * .52
                    saturation = 1 - hue_pos
                    rgb = tuple(round(channel * 255) for channel in colorsys.hsv_to_rgb(hue, saturation, .96))
                    color = '#%02X%02X%02X' % rgb
                else:
                    color = '#575A68'
                x0 = pad + index * step + 1
                x1 = pad + (index + 1) * step - 1
                canvas.create_rectangle(x0, bottom - bar_h, max(x0 + 1, x1), bottom, fill=color, outline='')
            threshold_y = bottom - (bottom - top) * min(1.0, max(0.0, self.music.trigger_threshold / .12))
            canvas.create_line(pad, threshold_y, width - pad, threshold_y, fill=ACCENT,
                               dash=(4, 3), width=2)
            for position in (low_pos, high_pos):
                x = pad + position * (width - 2 * pad)
                canvas.create_line(x, top, x, bottom, fill=ACCENT, width=2)
        else:
            canvas.create_text(width / 2, height / 2, text='Ожидание аудиосигнала', fill=MUTED,
                               font=('Segoe UI', 10))
        canvas.create_text(pad, height - 6, text='35 Гц', fill=MUTED, anchor='w', font=('Segoe UI', 8))
        canvas.create_text(width - pad, height - 6, text='12 кГц', fill=MUTED, anchor='e', font=('Segoe UI', 8))

    def refresh_sources(self):
        if self.refreshing_sources or self.effect_active:
            return
        self.refreshing_sources = True
        self.controls()
        def discover():
            try:
                from audio_sources import mixer_sources
                self.music.events.put(('sources', mixer_sources()))
            except Exception as exc:
                self.music.events.put(('sources_error', str(exc)))
        threading.Thread(target=discover, daemon=True).start()

    def auto_detect_audio(self):
        if self.closing:
            return
        if self.auto_start_on_audio.get() and not self.auto_refreshing and not self.effect_active:
            self.auto_refreshing = True
            def discover_active():
                try:
                    from audio_sources import mixer_sources
                    self.music.events.put(('active_sources', mixer_sources(active_only=True)))
                except Exception as exc:
                    self.music.events.put(('active_sources_error', str(exc)))
            threading.Thread(target=discover_active, daemon=True, name='ZenggeActiveAudio').start()
        self.root.after(1500, self.auto_detect_audio)

    def maybe_auto_start_music(self):
        if (self.active_audio_sources and self.auto_start_on_audio.get() and self.connected
                and self.effect_mode == 'music' and not self.effect_active and not self.busy
                and not self.auto_start_blocked and not self.auto_connecting):
            active = self.active_audio_sources[0]
            for index, source in enumerate(self.sources):
                if source and source.pid == active.pid and source.created == active.created:
                    self.source_box.current(index)
                    break
            self.toggle_music(automatic=True)

    def load_source_selection(self, source):
        for index, candidate in enumerate(self.sources):
            if candidate and candidate.pid == source.pid and candidate.created == source.created:
                self.source_box.current(index)
                return
        self.sources.append(source)
        values = list(self.source_box['values'])
        values.append(source.label)
        self.source_box['values'] = values
        self.source_box.current(len(self.sources) - 1)

    def schedule_save_settings(self, *_):
        if self.closing:
            self.save_settings()
            return
        if self.settings_save_job is not None:
            try:
                self.root.after_cancel(self.settings_save_job)
            except tk.TclError:
                pass
        self.settings_save_job = self.root.after(350, self.save_settings)

    def save_settings(self):
        self.settings_save_job = None
        settings = {
            'frequency_low': self.music.frequency_low,
            'frequency_high': self.music.frequency_high,
            'trigger_threshold': self.music.trigger_threshold,
            'music_min_brightness': self.music.min_brightness,
            'color_map': self.color_map,
            'devices': sorted(self.remembered_devices),
            'auto_start_on_audio': self.auto_start_on_audio.get(),
            'music_fade': self.music_fade.get(),
            'music_fade_speed': self.music_fade_speed.get(),
            'fade_brightness': self.fade_brightness.get(),
            'fade_tone_ms': self.fade_tone_ms.get(),
            'fade_color_map': self.fade_color_map,
            'fade_profiles': self.fade_profiles,
            'screen_brightness': self.screen_brightness.get(),
            'spectrum_profiles': self.spectrum_profiles,
        }
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.settings_path.with_suffix('.tmp')
            temporary.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding='utf-8')
            temporary.replace(self.settings_path)
        except OSError:
            pass

    def refresh_spectrum_profiles(self):
        if not hasattr(self, 'profile_box'):
            return
        names = sorted(self.spectrum_profiles, key=str.casefold)
        self.profile_box['values'] = names
        if self.profile_name.get() not in names:
            self.profile_name.set(names[0] if names else '')

    def save_spectrum_profile(self):
        name = simpledialog.askstring('Сохранить профиль спектра', 'Название профиля:', parent=self.root)
        if not name or not name.strip():
            return
        name = name.strip()
        self.spectrum_profiles[name] = {
            'frequency_low': self.music.frequency_low,
            'frequency_high': self.music.frequency_high,
            'trigger_threshold': self.music.trigger_threshold,
            'color_map': self.color_map,
            'devices': sorted(address.lower() for address in self.connections),
        }
        self.profile_name.set(name)
        self.refresh_spectrum_profiles()
        self.save_settings()

    def load_spectrum_profile(self):
        name = self.profile_name.get()
        profile = self.spectrum_profiles.get(name)
        if not profile:
            return
        try:
            low = max(35, min(11900, int(profile['frequency_low'])))
            high = max(low + 40, min(12000, int(profile['frequency_high'])))
            threshold = max(.003, min(.12, float(profile['trigger_threshold'])))
            points = [(int(point[0]), tuple(max(0, min(255, int(c))) for c in point[1]))
                      for point in profile['color_map']]
            if len(points) < 2:
                raise ValueError('В профиле нужно не менее двух цветовых точек.')
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            self.status.set(f'Не удалось загрузить профиль: {exc}')
            return
        self.frequency_low.set(low)
        self.frequency_high.set(high)
        self.trigger_threshold.set(threshold)
        self.color_map = sorted(points, key=lambda point: point[0])
        self.music.color_map = tuple(self.color_map)
        self.selected_gradient = -1
        self.draw_gradient()
        self.update_music_range()
        self.update_music_trigger()
        self.save_settings()
        self.status.set(f'Загружен профиль спектра «{name}».')
        if 'devices' in profile:
            self.switch_profile_devices(profile['devices'])

    def switch_profile_devices(self, addresses):
        if self.busy:
            self.status.set('Переключение ламп профиля начнётся после завершения текущей команды.')
            self.root.after(250, lambda: self.switch_profile_devices(addresses))
            return
        target = {str(address).lower() for address in addresses}
        self.profile_connect_targets = target
        self.remembered_devices.update(target)
        self.auto_connecting = True
        disconnect = [address for address in self.connections if address.lower() not in target]
        if disconnect:
            self.run('disconnect', disconnect)
        else:
            self.connect_missing_profile_devices()

    def connect_missing_profile_devices(self):
        if self.busy or self.profile_connect_targets is None:
            return
        current = {address.lower() for address in self.connections}
        missing = self.profile_connect_targets - current
        if not missing:
            self.profile_connect_targets = None
            self.auto_connecting = False
            self.status.set('Подключены лампы выбранного профиля.')
            self.save_settings()
            return
        self.run('scan')

    def delete_spectrum_profile(self):
        name = self.profile_name.get()
        if not name or name not in self.spectrum_profiles:
            return
        del self.spectrum_profiles[name]
        self.refresh_spectrum_profiles()
        self.save_settings()
        self.status.set(f'Профиль спектра «{name}» удалён.')

    def fade_gradient_x(self, position):
        width = max(1, self.fade_gradient.winfo_width() - 12)
        return 6 + self.spectrum_x(position) * width

    def fade_gradient_position(self, x):
        width = max(1, self.fade_gradient.winfo_width() - 12)
        amount = min(1.0, max(0.0, (x - 6) / width))
        return round(35 * (12000 / 35) ** amount)

    def draw_fade_gradient(self):
        if not hasattr(self, 'fade_gradient') or not self.fade_gradient.winfo_exists():
            return
        from music import interpolate_color
        canvas = self.fade_gradient
        canvas.delete('all')
        width, height = max(120, canvas.winfo_width()), max(36, canvas.winfo_height())
        for x in range(6, width - 6):
            rgb = interpolate_color(self.fade_gradient_position(x), self.fade_color_map)
            canvas.create_line(x, 5, x, height - 13, fill='#%02X%02X%02X' % rgb)
        for index, (position, rgb) in enumerate(self.fade_color_map):
            x = self.fade_gradient_x(position)
            canvas.create_oval(x - 5, 5, x + 5, 15, fill='#%02X%02X%02X' % rgb,
                               outline=ACCENT if index == getattr(self, 'selected_fade_point', -1) else FG)
            canvas.create_text(x, height - 6, text=str(index + 1), fill=FG, font=('Segoe UI', 8))

    def add_fade_point(self, event):
        position = self.fade_gradient_position(event.x)
        nearest = min(range(len(self.fade_color_map)),
                      key=lambda i: abs(self.fade_gradient_x(self.fade_color_map[i][0]) - event.x))
        if abs(self.fade_gradient_x(self.fade_color_map[nearest][0]) - event.x) < 10:
            position = self.fade_color_map[nearest][0]
        color = ask_color(self.root, self.fade_color_map[nearest][1])
        if color:
            self.fade_color_map = [point for point in self.fade_color_map if point[0] != position]
            self.fade_color_map.append((position, tuple(round(channel) for channel in color)))
            self.fade_color_map.sort(key=lambda point: point[0])
            self.selected_fade_point = next(i for i, point in enumerate(self.fade_color_map) if point[0] == position)
            self.draw_fade_gradient()
            self.schedule_save_settings()
        return 'break'

    def select_fade_point(self, event):
        nearest = min(range(len(self.fade_color_map)),
                      key=lambda i: abs(self.fade_gradient_x(self.fade_color_map[i][0]) - event.x))
        self.selected_fade_point = nearest
        self.drag_fade_index = nearest if abs(self.fade_gradient_x(self.fade_color_map[nearest][0]) - event.x) < 12 else None
        self.draw_fade_gradient()

    def move_fade_point(self, event):
        index = getattr(self, 'drag_fade_index', None)
        if index is None or not 0 <= index < len(self.fade_color_map):
            return
        position = self.fade_gradient_position(event.x)
        minimum = self.fade_color_map[index - 1][0] + 1 if index else 35
        maximum = self.fade_color_map[index + 1][0] - 1 if index + 1 < len(self.fade_color_map) else 12000
        position = min(maximum, max(minimum, position))
        self.fade_color_map[index] = (position, self.fade_color_map[index][1])
        self.fade_color_map.sort(key=lambda point: point[0])
        self.selected_fade_point = next(i for i, point in enumerate(self.fade_color_map) if point[0] == position)
        self.drag_fade_index = self.selected_fade_point
        self.draw_fade_gradient()
        self.schedule_save_settings()

    def delete_fade_point(self, event=None):
        index = getattr(self, 'selected_fade_point', -1)
        if event is not None and getattr(event, 'num', None) == 3:
            index = min(range(len(self.fade_color_map)),
                        key=lambda i: abs(self.fade_gradient_x(self.fade_color_map[i][0]) - event.x))
        if 0 <= index < len(self.fade_color_map) and len(self.fade_color_map) > 2:
            self.fade_color_map.pop(index)
            self.selected_fade_point = -1
            self.draw_fade_gradient()
            self.schedule_save_settings()
        return 'break'

    def fade_color_at(self, elapsed):
        count = len(self.fade_color_map)
        closes_loop = self.fade_color_map[0][1] == self.fade_color_map[-1][1]
        transitions = count - 1 if closes_loop else count
        step = max(1, int(self.fade_tone_ms.get()))
        phase = (elapsed * 1000 / step) % transitions
        index = int(phase)
        amount = phase - index
        left = self.fade_color_map[index][1]
        right = self.fade_color_map[index + 1][1] if index + 1 < count else self.fade_color_map[0][1]
        return tuple(round(a + (b - a) * amount) for a, b in zip(left, right))

    def refresh_fade_profiles(self):
        if not hasattr(self, 'fade_profile_box'):
            return
        names = sorted(self.fade_profiles, key=str.casefold)
        self.fade_profile_box['values'] = names
        if self.fade_profile_name.get() not in names:
            self.fade_profile_name.set(names[0] if names else '')

    def save_fade_profile(self):
        name = simpledialog.askstring('Сохранить профиль Fade', 'Название профиля:', parent=self.root)
        if not name or not name.strip():
            return
        name = name.strip()
        self.fade_profiles[name] = {'color_map': self.fade_color_map}
        self.fade_profile_name.set(name)
        self.refresh_fade_profiles()
        self.save_settings()

    def load_fade_profile(self):
        name = self.fade_profile_name.get()
        profile = self.fade_profiles.get(name)
        if not profile:
            return
        try:
            points = [(int(point[0]), tuple(max(0, min(255, int(c))) for c in point[1]))
                      for point in profile['color_map']]
            if len(points) < 2:
                raise ValueError('В профиле нужно не менее двух цветовых точек.')
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            self.status.set(f'Не удалось загрузить профиль Fade: {exc}')
            return
        self.fade_color_map = sorted(points, key=lambda point: point[0])
        self.selected_fade_point = -1
        self.draw_fade_gradient()
        self.save_settings()
        self.status.set(f'Загружен профиль Fade «{name}».')

    def delete_fade_profile(self):
        name = self.fade_profile_name.get()
        if name and name in self.fade_profiles:
            del self.fade_profiles[name]
            self.refresh_fade_profiles()
            self.save_settings()
            self.status.set(f'Профиль Fade «{name}» удалён.')

    def bind_scale_wheels(self, parent):
        for widget in parent.winfo_children():
            if widget.winfo_class() == 'TScale':
                widget.bind('<MouseWheel>', lambda event, scale=widget: self.scale_mousewheel(event, scale), add='+')
            self.bind_scale_wheels(widget)

    def scale_mousewheel(self, event, scale):
        try:
            variable_name = str(scale.cget('variable'))
            variable = next(value for value in self.__dict__.values()
                            if isinstance(value, tk.Variable) and str(value) == variable_name)
            start, end = float(scale.cget('from')), float(scale.cget('to'))
            step = abs(end - start) / 100
            upward = event.delta > 0
            if str(scale.cget('orient')) == 'vertical':
                delta = step if upward else -step
                lower, upper = min(start, end), max(start, end)
            else:
                delta = step if upward else -step
                if end < start:
                    delta = -delta
                lower, upper = min(start, end), max(start, end)
            value = min(upper, max(lower, variable.get() + delta))
            variable.set(value)
            callback = scale.cget('command')
            if callback:
                self.root.tk.call(callback, str(value))
            self.schedule_save_settings()
            return 'break'
        except (StopIteration, tk.TclError, TypeError, ValueError):
            return None

    def update_connections(self, connections):
        selected = set(self.connection_list.selection())
        previous = set(self.connections)
        self.connections = {item['address']: item['name'] for item in connections}
        self.remembered_devices.update(address.lower() for address in self.connections)
        self.schedule_save_settings()
        self.connected = bool(self.connections)
        for item in self.connection_list.get_children():
            self.connection_list.delete(item)
        for address, name in self.connections.items():
            self.connection_list.insert('', 'end', iid=address, text=name, values=(address,))
        select = (selected | (set(self.connections)-previous)) & set(self.connections)
        self.connection_list.selection_set(list(select))
        self.connection_summary.set(f'Подключено: {len(self.connections)}. Команды — всем подключённым лампам.')
        self.last_music_rgb = None
        if not self.connected:
            self.stop_music(restore=False)
        self.controls()
        self.maybe_auto_start_music()

    def controls(self):
        for button in (self.on_button, self.off_button):
            button.configure(state='normal' if self.connected and not self.busy else 'disabled')
        self.disconnect_button.configure(state='normal' if self.connection_list.selection() and not self.busy else 'disabled')
        self.apply_button.configure(state='normal' if self.connected and not self.busy and not self.effect_active else 'disabled')
        start_state = 'normal' if self.effect_active or (self.connected and not self.busy and not self.music.running) else 'disabled'
        start_text = 'Остановить' if self.effect_active else 'Запустить'
        self.music_button.configure(text=start_text, state=start_state)
        self.fade_button.configure(text=start_text, state=start_state)
        self.screen_button.configure(text=start_text, state=start_state)
        selecting = self.effect_mode == 'music' and not self.effect_active and not self.music.running
        self.source_box.configure(state='readonly' if selecting and not self.refreshing_sources else 'disabled')
        self.refresh_button.configure(state='normal' if selecting and not self.refreshing_sources else 'disabled')
        self.scan_button.configure(state='normal' if not self.busy else 'disabled')
        index = self.device.current()
        candidate = index >= 0 and index < len(self.devices) and self.devices[index][0].address not in self.connections
        self.connect_button.configure(state='normal' if not self.busy and candidate else 'disabled')
        self.device.configure(state='readonly' if not self.busy else 'disabled')

    def run(self, action, *args):
        if self.busy:
            return
        if action == 'power':
            self.stop_music(restore=False)
        self.busy = True
        self.controls()
        self.status.set({'scan': 'Поиск устройств… около 7 секунд.', 'connect': 'Подключение…', 'disconnect': 'Отключение…'}.get(action, 'Отправка команды…'))
        self.ble.submit(action, *args)

    def scan(self):
        self.run('scan')

    def connect_next_auto(self):
        if self.auto_connect_queue and not self.busy:
            device = self.auto_connect_queue.pop(0)
            self.current_auto_device = device
            self.auto_connecting = True
            self.run('connect', device)
        else:
            self.auto_connecting = False
            self.current_auto_device = None
            if self.profile_connect_targets is not None:
                self.finish_profile_switch()
                return
            self.maybe_auto_start_music()

    def finish_profile_switch(self):
        missing = self.profile_missing_devices
        self.profile_connect_targets = None
        self.profile_missing_devices = set()
        self.auto_connecting = False
        self.status.set('Подключены лампы выбранного профиля.' if not missing else
                        'Не найдены лампы профиля: ' + ', '.join(sorted(missing)))
        self.save_settings()
        self.maybe_auto_start_music()

    def connect(self):
        index = self.device.current()
        if index >= 0:
            self.run('connect', self.devices[index][0])

    def values(self):
        rgb = tuple(int(v.get()) for v in self.rgb)
        if any(v < 0 or v > 255 for v in rgb):
            raise ValueError()
        return rgb

    def update_preview(self, *_):
        try:
            self.set_preview(dim(self.values(), self.brightness.get()))
        except ValueError:
            pass

    def pick(self):
        try:
            initial = self.values()
        except ValueError:
            initial = (255, 128, 64)
        color = ask_color(self.root, initial)
        if color:
            for variable, value in zip(self.rgb, color):
                variable.set(str(round(value)))

    def apply(self):
        try:
            rgb = self.values()
        except ValueError:
            self.status.set('Введите целые значения R, G и B от 0 до 255.')
            return
        self.run('color', dim(rgb, self.brightness.get()))

    def toggle_music(self, automatic=False):
        if self.effect_active:
            if not automatic:
                self.auto_start_blocked = True
            self.stop_music()
            return
        try:
            self.saved_rgb = self.values()
            if self.effect_mode == 'music':
                index = self.source_box.current()
                self.music.start(self.sources[index] if index >= 0 else None)
        except (ValueError, RuntimeError) as exc:
            self.status.set(str(exc) or 'Введите RGB от 0 до 255.')
            return
        self.restore_color = None
        self.last_music_rgb = None
        self.music_last_input = self.saved_rgb
        self.transition = SmoothColor(dim(self.saved_rgb, self.brightness.get()))
        self.effect_active = True
        self.music_active = self.effect_mode == 'music'
        if self.effect_mode == 'music':
            self.audio_status.set('Запуск захвата системного звука…')
            self.status.set('Режим музыки: включите воспроизведение на ПК.')
        elif self.effect_mode == 'fade':
            self.fade_started = time.monotonic()
            self.status.set('Включено плавное переливание цветов.')
        else:
            self.screen_color = None
            self.screen_stop = threading.Event()
            threading.Thread(target=self.capture_screen_loop, args=(self.screen_stop,), daemon=True,
                             name='ZenggeScreenColor').start()
            self.status.set('Подстройка цвета под средний цвет экранов Windows.')
        self.controls()
        # Power on first; music frames wait for this operation to finish.
        self.busy = True
        self.ble.submit('power', True)
        self.controls()

    def stop_music(self, restore=True):
        if self.effect_active or self.music_active:
            was_music = self.music_active
            self.effect_active = False
            self.music_active = False
            if was_music:
                self.music.stop()
            self.screen_stop.set()
            self.screen_color = None
            self.restore_color = self.saved_rgb if restore else None
            if was_music:
                self.audio_status.set('Режим музыки остановлен.')
                self.level['value'] = 0
            self.update_preview()
        if not restore:
            self.restore_color = None
        self.controls()

    def capture_screen_loop(self, stop_event):
        from screen_capture import capture_average_rgb

        while not stop_event.is_set():
            try:
                color = capture_average_rgb()
                if not stop_event.is_set():
                    self.music.events.put(('screen_color', color))
            except Exception as exc:
                if not stop_event.is_set():
                    self.music.events.put(('screen_error', str(exc) or type(exc).__name__))
                return
            stop_event.wait(.3)

    def poll_music(self):
        try:
            while True:
                kind, text = self.music.events.get_nowait()
                if kind == 'sources':
                    selected = self.sources[max(0, self.source_box.current())]
                    self.sources = [None] + text
                    self.source_box['values'] = ['Весь системный звук'] + [s.label for s in text]
                    identity = lambda source: (source.pid, source.created) if source else None
                    index = next((i for i, source in enumerate(self.sources) if identity(source) == identity(selected)), 0)
                    self.source_box.current(index)
                    self.refreshing_sources = False
                    self.audio_status.set('Выберите окно приложения или звуковой сеанс. Список доступен до начала воспроизведения.')
                elif kind == 'sources_error':
                    self.refreshing_sources = False
                    self.audio_status.set('Список приложений недоступен: ' + text)
                elif kind == 'active_sources':
                    self.auto_refreshing = False
                    self.active_audio_sources = text
                    if not text:
                        self.auto_start_blocked = False
                    else:
                        self.load_source_selection(text[0])
                        self.maybe_auto_start_music()
                elif kind == 'active_sources_error':
                    self.auto_refreshing = False
                elif kind == 'ready' and self.music_active:
                    self.audio_status.set('Источник: ' + text)
                elif kind == 'screen_color' and self.effect_active and self.effect_mode == 'screen':
                    self.screen_color = text
                elif kind == 'screen_error':
                    self.screen_stop.set()
                    self.status.set('Не удалось получить цвет экранов: ' + text)
                elif kind == 'error':
                    self.stop_music(restore=False)
                    self.audio_status.set('Не удалось захватить звук: ' + text)
        except queue.Empty:
            pass
        available = self.music_future is None or self.music_future.done()
        if self.effect_active and self.connected:
            now = time.monotonic()
            target = None
            if self.effect_mode == 'music':
                rgb, level = self.music.latest
                self.level['value'] = level
                if self.music.frequency:
                    self.pitch_readout.set(f'{self.music.frequency} Гц  ·  активен')
                else:
                    self.pitch_readout.set('Низкие ноты → красный     Высокие → белый')
                if self.music.audible:
                    self.music_last_input = rgb
                # Silence holds the last detected pitch color and brightness.
                target, self.music_hue = music_light(self.music_last_input, self.brightness.get(),
                                                      self.reactive_brightness.get(), self.music_hue,
                                                      self.pulse_strength.get())
            elif self.effect_mode == 'fade':
                base = self.fade_color_at(now - self.fade_started)
                target = dim(base, self.fade_brightness.get() * self.brightness.get() / 100)
            elif self.effect_mode == 'screen' and self.screen_color is not None:
                target = dim(self.screen_color, self.screen_brightness.get() * self.brightness.get() / 100)
            if target is not None:
                if self.effect_mode == 'music' and self.music_fade.get():
                    fade_h, fade_s, fade_v = colorsys.rgb_to_hsv(*(channel / 255 for channel in target))
                    fade_h = (now * max(.01, self.music_fade_speed.get())) % 1
                    target = tuple(round(channel * 255) for channel in colorsys.hsv_to_rgb(
                        fade_h, max(.8, fade_s), fade_v))
                rgb = self.transition.update(target, now, self.smoothness.get())
                self.set_preview(rgb)
                # Send every effect frame (24 Hz), including repeated RGB
                # values, so the lamp receives a steady command cadence.
                if available and not self.busy:
                    self.last_music_rgb = rgb
                    self.music_future = self.ble.submit('music_color', rgb)
        elif self.restore_color is not None and available and not self.busy and self.connected:
            rgb, self.restore_color = self.restore_color, None
            self.run('color', dim(rgb, self.brightness.get()))
        if self.effect_mode == 'music':
            self.draw_spectrum()
        self.controls()

    def poll(self):
        try:
            while True:
                kind, action, result = self.ble.events.get_nowait()
                if kind == 'connections':
                    self.update_connections(result)
                    continue
                if kind == 'device_error':
                    self.status.set(result)
                    continue
                if action == 'music_color':
                    if kind == 'error':
                        self.stop_music(restore=False)
                        self.status.set('Ошибка передачи музыки: ' + result)
                    continue
                if kind == 'disconnected':
                    self.stop_music(restore=False)
                    self.connected = False
                    self.status.set('Устройство отключено. Можно подключиться снова.')
                else:
                    self.busy = False
                    if kind == 'error':
                        if self.music_active:
                            self.stop_music(restore=False)
                        self.status.set('Ошибка: ' + result + ' Проверьте Bluetooth и закройте приложение лампы на телефоне.')
                        if action == 'connect' and self.auto_connecting:
                            if self.profile_connect_targets is not None and self.current_auto_device is not None:
                                self.profile_missing_devices.add(self.current_auto_device.address.lower())
                            self.root.after(0, self.connect_next_auto)
                    elif action == 'scan':
                        self.devices = result
                        self.device['values'] = [f'{a.local_name or d.name or "LEDnetWF"}  ({d.address})' for d, a in result]
                        if result:
                            self.device.current(0)
                        else:
                            self.device.set('')
                        self.status.set(f'Найдено устройств: {len(result)}.' if result else 'LEDnetWF не найден. Включите лампу и повторите поиск.')
                        current_addresses = {address.lower() for address in self.connections}
                        if self.profile_connect_targets is not None:
                            found_addresses = {device.address.lower() for device, _ in result}
                            self.profile_missing_devices.update(
                                self.profile_connect_targets - found_addresses - current_addresses)
                            self.auto_connect_queue = [device for device, _ in result
                                                       if device.address.lower() in self.profile_connect_targets
                                                       and device.address.lower() not in current_addresses]
                        else:
                            self.auto_connect_queue = [device for device, _advertisement in result
                                                       if device.address.lower() in self.remembered_devices
                                                       and device.address.lower() not in current_addresses]
                        if self.auto_connect_queue:
                            self.auto_connecting = True
                            self.connect_next_auto()
                        elif self.profile_connect_targets is not None:
                            self.finish_profile_switch()
                    elif action == 'connect':
                        self.update_connections(result)
                        self.status.set('Лампа подключена. Можно добавить следующую.')
                        if self.auto_connecting:
                            self.connect_next_auto()
                    elif action == 'disconnect':
                        self.update_connections(result)
                        self.status.set('Выбранные лампы отключены.')
                        if self.profile_connect_targets is not None:
                            self.root.after(0, self.connect_missing_profile_devices)
                    else:
                        self.status.set('Команда отправлена.' if action == 'power' else 'Цвет отправлен на устройство.')
                self.controls()
        except queue.Empty:
            pass
        self.poll_music()
        if not self.closing:
            self.root.after(42, self.poll)  # approximately 24 effect frames per second

    def close(self):
        if self.closing:
            return
        self.closing = True
        self.save_settings()
        self.stop_music(restore=False)
        self.root.withdraw()
        future = self.ble.submit('disconnect')
        def finish():
            if future.done():
                self.ble.loop.call_soon_threadsafe(self.ble.loop.stop)
                self.root.destroy()
            else:
                self.root.after(100, finish)
        self.root.after(100, finish)
        self.root.after(5000, self.root.destroy)

if __name__ == '__main__':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass
    root = tk.Tk()
    App(root)
    root.mainloop()

