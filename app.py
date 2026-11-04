import ctypes
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk, colorchooser
from bluetooth import Bluetooth
from music import MusicCapture
from lighting import dim, music_light, SmoothColor

BG, FG, MUTED, PANEL = '#20242B', '#F4F6FA', '#BEC7D5', '#2B3039'

class App:
    def __init__(self, root):
        self.root = root
        self.ble = Bluetooth()
        self.music = MusicCapture()
        self.music_active = False
        self.music_future = None
        self.restore_color = None
        self.last_music_rgb = None
        self.music_hue = 0.02
        self.brightness_job = None
        self.music_last_input = (255,128,64)
        self.transition = SmoothColor()
        self.connections = {}
        self.connected = False
        self.busy = False
        self.closing = False
        self.devices = []
        self.sources = [None]
        self.refreshing_sources = False
        root.title('Zengge • Свет')
        root.geometry('660x1000')
        root.minsize(660, 960)
        root.configure(bg=BG)
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('.', background=BG, foreground=FG, font=('Segoe UI', 10))
        style.configure('TButton', padding=(12, 8), background=PANEL, foreground=FG)
        style.map('TButton', background=[('active', '#3A4658'), ('disabled', '#252930')], foreground=[('disabled', '#87909E')])
        style.configure('TCombobox', fieldbackground=PANEL, background=PANEL, foreground=FG, padding=6)
        style.map('TCombobox', fieldbackground=[('readonly', PANEL)], foreground=[('readonly', FG)])
        style.configure('TNotebook.Tab', padding=(16, 8))
        style.map('TNotebook.Tab', background=[('selected', PANEL)], foreground=[('selected', FG)])
        style.configure('Treeview', background=PANEL, fieldbackground=PANEL, foreground=FG, rowheight=26)
        style.configure('Treeview.Heading', background=BG, foreground=FG)
        style.configure('TSpinbox', fieldbackground=PANEL, foreground=FG, arrowsize=16)
        root.option_add('*TCombobox*Listbox.background', PANEL)
        root.option_add('*TCombobox*Listbox.foreground', FG)
        frame = ttk.Frame(root, padding=24)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Управление светом', font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        ttk.Label(frame, text='Zengge / LEDnetWF · Bluetooth LE', foreground=MUTED).pack(anchor='w', pady=(2, 22))
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
        self.disconnect_button.pack(side='left', padx=8)
        self.connection_list = ttk.Treeview(frame, columns=('address',), height=2, selectmode='extended')
        self.connection_list.heading('#0', text='Подключённые лампы')
        self.connection_list.heading('address', text='Адрес Bluetooth')
        self.connection_list.column('#0', width=280)
        self.connection_list.column('address', width=170)
        self.connection_list.pack(fill='x', pady=(8, 0))
        self.connection_list.bind('<<TreeviewSelect>>', lambda _: self.controls())
        self.connection_summary = tk.StringVar(value='Нет подключений. Команды будут отправляться всем лампам.')
        ttk.Label(frame, textvariable=self.connection_summary, foreground=MUTED).pack(anchor='w', pady=(4, 0))
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
        self.on_button.pack(side='left', padx=8)
        self.off_button = ttk.Button(row, text='Выключить', command=lambda: self.run('power', False))
        self.off_button.pack(side='left')
        self.tabs = ttk.Notebook(frame)
        self.tabs.pack(fill='both', expand=True, pady=(0, 12))
        color_frame = ttk.Frame(self.tabs, padding=12)
        music_frame = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(color_frame, text='Цвет')
        self.tabs.add(music_frame, text='Музыка')
        row = ttk.Frame(color_frame)
        row.pack(fill='x')
        ttk.Label(row, text='Цвет подсветки', font=('Segoe UI', 11, 'bold')).pack(side='left')
        ttk.Button(row, text='Палитра…', command=self.pick).pack(side='right')
        self.preview = tk.Canvas(color_frame, height=64, bg='#FF8040', highlightthickness=0)
        self.preview.pack(fill='x', pady=(12, 12))
        self.rgb = [tk.StringVar(value=str(v)) for v in (255, 128, 64)]
        row = ttk.Frame(color_frame)
        row.pack(fill='x')
        for i, label in enumerate(('R · Красный', 'G · Зелёный', 'B · Синий')):
            col = ttk.Frame(row)
            col.pack(side='left', fill='x', expand=True, padx=(0, 8) if i < 2 else 0)
            ttk.Label(col, text=label, foreground=MUTED).pack(anchor='w')
            spin = ttk.Spinbox(col, from_=0, to=255, textvariable=self.rgb[i], width=8)
            spin.pack(fill='x', pady=(4, 0))
            self.rgb[i].trace_add('write', self.update_preview)
        row = ttk.Frame(color_frame)
        row.pack(fill='x', pady=16)
        self.apply_button = ttk.Button(row, text='Применить цвет', command=self.apply)
        self.apply_button.pack(side='left')
        row = ttk.Frame(music_frame)
        row.pack(fill='x')
        ttk.Label(row, text='В такт музыке', font=('Segoe UI', 11, 'bold')).pack(side='left')
        self.music_button = ttk.Button(row, text='Запустить', command=self.toggle_music)
        self.music_button.pack(side='right')
        row = ttk.Frame(music_frame)
        row.pack(fill='x', pady=(10, 0))
        self.source_box = ttk.Combobox(row, state='readonly', values=['Весь системный звук'])
        self.source_box.pack(side='left', fill='x', expand=True)
        self.source_box.current(0)
        self.refresh_button = ttk.Button(row, text='Обновить', command=self.refresh_sources)
        self.refresh_button.pack(side='right', padx=(8, 0))
        self.audio_status = tk.StringVar(value='Звук с выхода Windows по умолчанию')
        ttk.Label(music_frame, textvariable=self.audio_status, foreground=MUTED, wraplength=500).pack(anchor='w', pady=(4, 6))
        row = ttk.Frame(music_frame)
        row.pack(fill='x')
        ttk.Label(row, text='Чувствительность').pack(side='left')
        self.gain = tk.DoubleVar(value=2)
        ttk.Scale(row, from_=0.5, to=8, variable=self.gain,
                  command=lambda value: setattr(self.music, 'gain', float(value))).pack(side='left', fill='x', expand=True, padx=12)
        self.level = ttk.Progressbar(music_frame, maximum=100)
        self.level.pack(fill='x', pady=(8, 12))
        self.reactive_brightness = tk.BooleanVar(value=True)
        ttk.Checkbutton(music_frame, text='Яркость в такт музыке', variable=self.reactive_brightness).pack(anchor='w', pady=(0, 12))
        row = ttk.Frame(music_frame)
        row.pack(fill='x', pady=(0, 8))
        ttk.Label(row, text='Сила пульсации').pack(side='left')
        self.pulse_strength = tk.DoubleVar(value=70)
        self.pulse_text = tk.StringVar(value='70%')
        ttk.Scale(row, from_=0, to=100, variable=self.pulse_strength,
                  command=lambda value: self.pulse_text.set(f'{round(float(value))}%')).pack(side='left', fill='x', expand=True, padx=12)
        ttk.Label(row, textvariable=self.pulse_text, width=5).pack(side='right')
        row = ttk.Frame(music_frame)
        row.pack(fill='x', pady=(0, 10))
        ttk.Label(row, text='Плавность').pack(side='left')
        self.smoothness = tk.DoubleVar(value=.4)
        ttk.Scale(row, from_=.1, to=1.2, variable=self.smoothness).pack(side='left', fill='x', expand=True, padx=12)
        ttk.Label(music_frame, text='Звуковая волна' , foreground=MUTED).pack(anchor='w')
        self.waveform = tk.Canvas(music_frame, height=100, background=PANEL, highlightthickness=0)
        self.waveform.pack(fill='x', pady=(6, 0))
        self.wave_line = self.waveform.create_line(0, 50, 500, 50, fill='#88B9FF', width=2)
        self.status = tk.StringVar(value='Включите Bluetooth и нажмите «Найти».')
        ttk.Label(frame, textvariable=self.status, foreground=MUTED, wraplength=460).pack(anchor='w', pady=(4, 0))
        self.controls()
        self.refresh_sources()
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(50, self.poll)

    def change_brightness(self, value):
        self.brightness_text.set(f'{round(float(value))}%')
        self.update_preview()
        if self.brightness_job is not None:
            self.root.after_cancel(self.brightness_job)
        self.brightness_job = self.root.after(160, self.send_brightness)

    def send_brightness(self):
        self.brightness_job = None
        if self.closing or not self.connected or self.music_active:
            return
        if self.busy:
            self.brightness_job = self.root.after(100, self.send_brightness)
            return
        self.apply()

    def draw_wave(self):
        width = max(2, self.waveform.winfo_width())
        height = max(2, self.waveform.winfo_height())
        samples = getattr(self.music, 'wave', (0.0, 0.0)) if self.music_active else (0.0, 0.0)
        gain = self.gain.get() * 2
        points = []
        for i, sample in enumerate(samples):
            points.extend((i * (width - 1) / (len(samples) - 1), height / 2 - max(-1, min(1, sample * gain)) * (height / 2 - 4)))
        self.waveform.coords(self.wave_line, *points)

    def refresh_sources(self):
        if self.refreshing_sources or self.music_active:
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

    def update_connections(self, connections):
        selected = set(self.connection_list.selection())
        previous = set(self.connections)
        self.connections = {item['address']: item['name'] for item in connections}
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

    def controls(self):
        for button in (self.on_button, self.off_button):
            button.configure(state='normal' if self.connected and not self.busy else 'disabled')
        self.disconnect_button.configure(state='normal' if self.connection_list.selection() and not self.busy else 'disabled')
        self.apply_button.configure(state='normal' if self.connected and not self.busy and not self.music_active else 'disabled')
        self.music_button.configure(text='Остановить' if self.music_active else 'Запустить', state='normal' if self.music_active or (self.connected and not self.busy and not self.music.running) else 'disabled')
        selecting = not self.music_active and not self.music.running
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
            self.preview.configure(bg='#%02x%02x%02x' % dim(self.values(), self.brightness.get()))
        except ValueError:
            pass

    def pick(self):
        color = colorchooser.askcolor(self.preview.cget('bg'), parent=self.root, title='Цвет подсветки')[0]
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

    def toggle_music(self):
        if self.music_active:
            self.stop_music()
            return
        try:
            self.saved_rgb = self.values()
            index = self.source_box.current()
            self.music.start(self.sources[index] if index >= 0 else None)
        except (ValueError, RuntimeError) as exc:
            self.status.set(str(exc) or 'Введите RGB от 0 до 255.')
            return
        self.restore_color = None
        self.last_music_rgb = None
        self.music_last_input = self.saved_rgb
        self.transition = SmoothColor(dim(self.saved_rgb, self.brightness.get()))
        self.music_active = True
        self.audio_status.set('Запуск захвата системного звука…')
        self.status.set('Режим музыки: включите воспроизведение на ПК.')
        self.controls()
        # Power on first; music frames wait for this operation to finish.
        self.busy = True
        self.ble.submit('power', True)
        self.controls()

    def stop_music(self, restore=True):
        if self.music_active:
            self.music_active = False
            self.music.stop()
            self.restore_color = self.saved_rgb if restore else None
            self.audio_status.set('Режим музыки остановлен.')
            self.level['value'] = 0
            self.update_preview()
        if not restore:
            self.restore_color = None
        self.controls()

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
                elif kind == 'ready' and self.music_active:
                    self.audio_status.set('Источник: ' + text)
                elif kind == 'error':
                    self.stop_music(restore=False)
                    self.audio_status.set('Не удалось захватить звук: ' + text)
        except queue.Empty:
            pass
        available = self.music_future is None or self.music_future.done()
        if self.music_active and self.connected:
            rgb, level = self.music.latest
            self.level['value'] = level
            if self.music.audible:
                self.music_last_input = rgb
            # Silence holds the last audible color and intensity in both modes.
            rgb, self.music_hue = music_light(self.music_last_input, self.brightness.get(), self.reactive_brightness.get(), self.music_hue, self.pulse_strength.get())
            rgb = self.transition.update(rgb, time.monotonic(), self.smoothness.get())
            self.preview.configure(bg='#%02x%02x%02x' % rgb)
            if available and not self.busy and rgb != self.last_music_rgb:
                self.last_music_rgb = rgb
                self.music_future = self.ble.submit('music_color', rgb)
        elif self.restore_color is not None and available and not self.busy and self.connected:
            rgb, self.restore_color = self.restore_color, None
            self.run('color', dim(rgb, self.brightness.get()))
        self.draw_wave()
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
                    elif action == 'scan':
                        self.devices = result
                        self.device['values'] = [f'{a.local_name or d.name or "LEDnetWF"}  ({d.address})' for d, a in result]
                        if result:
                            self.device.current(0)
                        else:
                            self.device.set('')
                        self.status.set(f'Найдено устройств: {len(result)}.' if result else 'LEDnetWF не найден. Включите лампу и повторите поиск.')
                    elif action == 'connect':
                        self.update_connections(result)
                        self.status.set('Лампа подключена. Можно добавить следующую.')
                    elif action == 'disconnect':
                        self.update_connections(result)
                        self.status.set('Выбранные лампы отключены.')
                    else:
                        self.status.set('Команда отправлена.' if action == 'power' else 'Цвет отправлен на устройство.')
                self.controls()
        except queue.Empty:
            pass
        self.poll_music()
        if not self.closing:
            self.root.after(50, self.poll)

    def close(self):
        if self.closing:
            return
        self.closing = True
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

