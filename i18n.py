"""Built-in translations for the Windows UI and system-language selection."""
import ctypes
import locale
import re

LANGUAGE_NAMES = {
    'ru': 'Русский',
    'en': 'English',
    'zh': '中文',
    'de': 'Deutsch',
    'pl': 'Polski',
}

# Russian is the source language; each tuple is English, Chinese, German, Polish.
_ROWS = {
    'Включите Bluetooth и нажмите «Найти».': ('Enable Bluetooth and click “Find”.', '请开启蓝牙并点击“查找”。', 'Aktiviere Bluetooth und klicke auf „Suchen“.', 'Włącz Bluetooth i kliknij „Szukaj”.'),
    'Лампы': ('Lamps', '灯具', 'Lampen', 'Lampy'),
    'Найти': ('Find', '查找', 'Suchen', 'Szukaj'),
    'Подключить': ('Connect', '连接', 'Verbinden', 'Połącz'),
    'Отключить выбранные': ('Disconnect selected', '断开所选设备', 'Ausgewählte trennen', 'Rozłącz wybrane'),
    'Подключённые лампы': ('Connected lamps', '已连接的灯具', 'Verbundene Lampen', 'Połączone lampy'),
    'Адрес Bluetooth': ('Bluetooth address', '蓝牙地址', 'Bluetooth-Adresse', 'Adres Bluetooth'),
    'Нет подключений. Команды будут отправляться всем лампам.': ('No connections. Commands will be sent to all lamps.', '尚未连接。命令将发送到所有灯具。', 'Keine Verbindung. Befehle werden an alle Lampen gesendet.', 'Brak połączeń. Polecenia będą wysyłane do wszystkich lamp.'),
    'Яркость': ('Brightness', '亮度', 'Helligkeit', 'Jasność'),
    'Включить': ('Turn on', '打开', 'Einschalten', 'Włącz'),
    'Выключить': ('Turn off', '关闭', 'Ausschalten', 'Wyłącz'),
    'Цвет': ('Color', '颜色', 'Farbe', 'Kolor'),
    'Музыка': ('Music', '音乐', 'Musik', 'Muzyka'),
    'Экран': ('Screen', '屏幕', 'Bildschirm', 'Ekran'),
    'Палитра…': ('Palette…', '调色板…', 'Farbpalette…', 'Paleta…'),
    'Применить цвет': ('Apply color', '应用颜色', 'Farbe anwenden', 'Zastosuj kolor'),
    'Предпросмотр цвета, а не подтверждённое состояние ламп.': ('Color preview; this does not confirm the lamps’ actual state.', '颜色预览，不代表灯具已确认此状态。', 'Farbvorschau; der tatsächliche Lampenzustand wird nicht bestätigt.', 'Podgląd koloru; nie potwierdza stanu lamp.'),
    'Источник': ('Audio source', '音源', 'Audioquelle', 'Źródło dźwięku'),
    'Запустить': ('Start', '启动', 'Starten', 'Uruchom'),
    'Остановить': ('Stop', '停止', 'Stoppen', 'Zatrzymaj'),
    'Весь системный звук': ('All system audio', '全部系统声音', 'Gesamter Systemton', 'Cały dźwięk systemowy'),
    'Обновить': ('Refresh', '刷新', 'Aktualisieren', 'Odśwież'),
    'Автовыбор источника и запуск при появлении звука': ('Automatically select source and start when audio begins', '自动选择音源并在有声音时启动', 'Quelle automatisch wählen und bei Ton starten', 'Automatycznie wybierz źródło i uruchom po wykryciu dźwięku'),
    'Звук с выхода Windows по умолчанию': ('Audio from the default Windows output', '来自 Windows 默认输出的声音', 'Ton vom Windows-Standardausgang', 'Dźwięk z domyślnego wyjścia Windows'),
    'Чувствительность': ('Sensitivity', '灵敏度', 'Empfindlichkeit', 'Czułość'),
    'Минимальная яркость музыки': ('Minimum music brightness', '音乐最低亮度', 'Mindesthelligkeit für Musik', 'Minimalna jasność muzyki'),
    'Яркость в такт музыке': ('Brightness reacts to music', '亮度随音乐变化', 'Helligkeit an Musik anpassen', 'Jasność reaguje na muzykę'),
    'Сила пульсации': ('Pulse strength', '脉冲强度', 'Pulsstärke', 'Siła pulsowania'),
    'Плавность': ('Smoothing', '平滑度', 'Glättung', 'Płynność'),
    'Fade: переливание оттенка в режиме музыки': ('Fade: cycle hues in music mode', '音乐模式下渐变色调', 'Fade: Farbtöne im Musikmodus wechseln', 'Fade: zmieniaj odcienie w trybie muzyki'),
    'Скорость Fade': ('Fade speed', '渐变速度', 'Fade-Geschwindigkeit', 'Szybkość Fade'),
    'Частотный микшер': ('Frequency mixer', '频率混音器', 'Frequenzmischer', 'Mikser częstotliwości'),
    'Порог': ('Threshold', '阈值', 'Schwelle', 'Próg'),
    'Диапазон': ('Range', '范围', 'Bereich', 'Zakres'),
    'Гц': ('Hz', '赫兹', 'Hz', 'Hz'),
    'Низкие ноты → красный     Высокие → белый': ('Low notes → red     High notes → white', '低音 → 红色     高音 → 白色', 'Tiefe Töne → Rot     Hohe → Weiß', 'Niskie nuty → czerwony     Wysokie → biały'),
    'Цветовой градиент частот': ('Frequency color gradient', '频率颜色渐变', 'Frequenz-Farbverlauf', 'Gradient kolorów częstotliwości'),
    'Двойной щелчок — добавить/изменить цветовую точку': ('Double-click to add or change a color point', '双击以添加或更改颜色节点', 'Doppelklick fügt einen Farbpunkt hinzu oder ändert ihn', 'Dwuklik dodaje lub zmienia punkt koloru'),
    'Профиль': ('Profile', '配置', 'Profil', 'Profil'),
    'Загрузить': ('Load', '加载', 'Laden', 'Wczytaj'),
    'Сохранить…': ('Save…', '保存…', 'Speichern…', 'Zapisz…'),
    'Удалить': ('Delete', '删除', 'Löschen', 'Usuń'),
    'Режим переливания': ('Color cycling mode', '颜色渐变模式', 'Farbwechselmodus', 'Tryb zmiany kolorów'),
    'Цветовой градиент Fade': ('Fade color gradient', 'Fade 颜色渐变', 'Fade-Farbverlauf', 'Gradient kolorów Fade'),
    'Двойной щелчок — добавить цвет · ЛКМ — двигать · ПКМ — удалить': ('Double-click to add a color · left-drag to move · right-click to delete', '双击添加颜色 · 按住左键拖动 · 右键删除', 'Doppelklick fügt Farbe hinzu · mit linker Taste ziehen · Rechtsklick löscht', 'Dwuklik dodaje kolor · przeciągnij lewym przyciskiem · usuń prawym'),
    'Профиль Fade': ('Fade profile', 'Fade 配置', 'Fade-Profil', 'Profil Fade'),
    'Яркость переливания': ('Fade brightness', '渐变亮度', 'Fade-Helligkeit', 'Jasność Fade'),
    'Время перехода на один оттенок (мс)': ('Transition time per color (ms)', '每种颜色的过渡时间（毫秒）', 'Übergangszeit pro Farbton (ms)', 'Czas przejścia jednego odcienia (ms)'),
    'мс на каждый переход': ('ms per transition', '毫秒/次过渡', 'ms pro Übergang', 'ms na przejście'),
    'Средний цвет экранов': ('Average screen color', '屏幕平均颜色', 'Durchschnittsfarbe des Bildschirms', 'Średni kolor ekranu'),
    'Режим Fade': ('Fade mode', '渐变模式', 'Fade-Modus', 'Tryb Fade'),
    'Цветовой градиент Fade': ('Fade color gradient', 'Fade 颜色渐变', 'Fade-Farbverlauf', 'Gradient kolorów Fade'),
    'Яркость переливания': ('Fade brightness', '渐变亮度', 'Fade-Helligkeit', 'Jasność Fade'),
    'Время перехода на один оттенок (мс)': ('Transition time per color (ms)', '每种颜色的过渡时间（毫秒）', 'Übergangszeit pro Farbton (ms)', 'Czas przejścia jednego odcienia (ms)'),
    'мс на каждый переход': ('ms per transition', '毫秒/次过渡', 'ms pro Übergang', 'ms na przejście'),
    'Профиль Fade': ('Fade profile', 'Fade 配置', 'Fade-Profil', 'Profil Fade'),
    'Сохранить профиль спектра': ('Save spectrum profile', '保存频谱配置', 'Spektrumprofil speichern', 'Zapisz profil widma'),
    'Сохранить профиль Fade': ('Save Fade profile', '保存 Fade 配置', 'Fade-Profil speichern', 'Zapisz profil Fade'),
    'Название профиля:': ('Profile name:', '配置名称：', 'Profilname:', 'Nazwa profilu:'),
    'Загружен профиль спектра «{}».': ('Spectrum profile “{}” loaded.', '已加载频谱配置“{}”。', 'Spektrumprofil „{}“ geladen.', 'Wczytano profil widma „{}”.'),
    'Цветовой градиент': ('Color gradient', '颜色渐变', 'Farbverlauf', 'Gradient kolorów'),
    'Выбрать цвет': ('Choose color', '选择颜色', 'Farbe auswählen', 'Wybierz kolor'),
    'Текущий': ('Current', '当前', 'Aktuell', 'Bieżący'),
    'Новый': ('New', '新建', 'Neu', 'Nowy'),
    'Отмена': ('Cancel', '取消', 'Abbrechen', 'Anuluj'),
    'Введите HEX из 6 символов, например FF8040.': ('Enter a 6-character HEX value, e.g. FF8040.', '请输入 6 位 HEX 值，例如 FF8040。', 'Gib einen 6-stelligen HEX-Wert ein, z. B. FF8040.', 'Wpisz 6-znakowy kod HEX, np. FF8040.'),
    'Введите R, G и B от 0 до 255.': ('Enter R, G and B values from 0 to 255.', '请输入 0 到 255 之间的 R、G、B 值。', 'Gib R-, G- und B-Werte von 0 bis 255 ein.', 'Wpisz wartości R, G i B od 0 do 255.'),
    'Введите R, G и B от 0 до 255.': ('Enter R, G and B values from 0 to 255.', '请输入 0 到 255 之间的 R、G、B 值。', 'Gib R-, G- und B-Werte von 0 bis 255 ein.', 'Wpisz wartości R, G i B od 0 do 255.'),
    'Сохранить профиль спектра': ('Save spectrum profile', '保存频谱配置', 'Spektrumprofil speichern', 'Zapisz profil widma'),
    'Сохранить профиль Fade': ('Save Fade profile', '保存 Fade 配置', 'Fade-Profil speichern', 'Zapisz profil Fade'),
    'Название профиля:': ('Profile name:', '配置名称：', 'Profilname:', 'Nazwa profilu:'),
    'Введите целые значения R, G и B от 0 до 255.': ('Enter integer R, G and B values from 0 to 255.', '请输入 0 到 255 之间的整数 R、G、B 值。', 'Gib ganzzahlige R-, G- und B-Werte von 0 bis 255 ein.', 'Wpisz całkowite wartości R, G i B od 0 do 255.'),
    'Русский': ('Russian', '俄语', 'Russisch', 'Rosyjski'),
    'Найдено устройств:': ('Devices found:', '找到的设备：', 'Gefundene Geräte:', 'Znalezione urządzenia:'),
    'LEDnetWF не найден. Включите лампу и повторите поиск.': ('No LEDnetWF devices found. Turn on a lamp and search again.', '未找到 LEDnetWF 设备。请打开灯具并重新搜索。', 'Keine LEDnetWF-Geräte gefunden. Schalte eine Lampe ein und suche erneut.', 'Nie znaleziono urządzeń LEDnetWF. Włącz lampę i wyszukaj ponownie.'),
    'Лампа подключена. Можно добавить следующую.': ('Lamp connected. You can add another.', '灯具已连接。可以继续添加。', 'Lampe verbunden. Du kannst eine weitere hinzufügen.', 'Lampa połączona. Możesz dodać następną.'),
    'Выбранные лампы отключены.': ('Selected lamps disconnected.', '所选灯具已断开。', 'Ausgewählte Lampen getrennt.', 'Wybrane lampy rozłączone.'),
    'Команда отправлена.': ('Command sent.', '命令已发送。', 'Befehl gesendet.', 'Wysłano polecenie.'),
    'Цвет отправлен на устройство.': ('Color sent to device.', '颜色已发送到设备。', 'Farbe an Gerät gesendet.', 'Wysłano kolor do urządzenia.'),
    'Подключены лампы выбранного профиля.': ('Lamps for the selected profile are connected.', '所选配置中的灯具已连接。', 'Lampen des ausgewählten Profils sind verbunden.', 'Lampy z wybranego profilu są połączone.'),
    'Режим музыки остановлен.': ('Music mode stopped.', '音乐模式已停止。', 'Musikmodus gestoppt.', 'Tryb muzyki zatrzymany.'),
    'Запуск захвата системного звука…': ('Starting system audio capture…', '正在启动系统声音捕获…', 'Systemaudio wird erfasst…', 'Uruchamianie przechwytywania dźwięku…'),
    'Режим музыки: включите воспроизведение на ПК.': ('Music mode: start audio playback on your PC.', '音乐模式：请在电脑上播放声音。', 'Musikmodus: Starte die Audiowiedergabe am PC.', 'Tryb muzyki: rozpocznij odtwarzanie na komputerze.'),
    'Включено плавное переливание цветов.': ('Color fade enabled.', '颜色渐变已启用。', 'Farbwechsel aktiviert.', 'Włączono płynne zmienianie kolorów.'),
    'Подстройка цвета под средний цвет экранов Windows.': ('Matching lamp color to the average Windows screen color.', '灯具颜色正在匹配 Windows 屏幕平均颜色。', 'Lampenfarbe wird an die durchschnittliche Windows-Bildschirmfarbe angepasst.', 'Dopasowywanie koloru lampy do średniego koloru ekranów Windows.'),
    'Источник: ': ('Source: ', '音源：', 'Quelle: ', 'Źródło: '),
    'Режим музыки остановлен.': ('Music mode stopped.', '音乐模式已停止。', 'Musikmodus gestoppt.', 'Tryb muzyki zatrzymany.'),
    'Не удалось получить цвет экранов: ': ('Could not capture screen color: ', '无法获取屏幕颜色：', 'Bildschirmfarbe konnte nicht erfasst werden: ', 'Nie udało się pobrać koloru ekranu: '),
    'Не удалось захватить звук: ': ('Could not capture audio: ', '无法捕获音频：', 'Audio konnte nicht erfasst werden: ', 'Nie udało się przechwycić dźwięku: '),
    'Ошибка передачи музыки: ': ('Music transfer error: ', '音乐传输错误：', 'Fehler bei der Musikübertragung: ', 'Błąd przesyłania muzyki: '),
    'Устройство отключено. Можно подключиться снова.': ('Device disconnected. You can reconnect.', '设备已断开。可以重新连接。', 'Gerät getrennt. Du kannst die Verbindung erneut herstellen.', 'Urządzenie rozłączone. Możesz połączyć ponownie.'),
    'Ошибка: ': ('Error: ', '错误：', 'Fehler: ', 'Błąd: '),
    'Проверьте Bluetooth и закройте приложение лампы на телефоне.': ('Check Bluetooth and close the lamp app on your phone.', '请检查蓝牙并关闭手机上的灯具应用。', 'Prüfe Bluetooth und schließe die Lampen-App auf dem Smartphone.', 'Sprawdź Bluetooth i zamknij aplikację lampy w telefonie.'),
    'Подключение…': ('Connecting…', '正在连接…', 'Verbindung wird hergestellt…', 'Łączenie…'),
    'Поиск устройств… около 7 секунд.': ('Searching for devices… about 7 seconds.', '正在搜索设备…约需 7 秒。', 'Suche nach Geräten… etwa 7 Sekunden.', 'Wyszukiwanie urządzeń… około 7 sekund.'),
    'Отправка команды…': ('Sending command…', '正在发送命令…', 'Befehl wird gesendet…', 'Wysyłanie polecenia…'),
    'Не удалось захватить звук: ': ('Could not capture audio: ', '无法捕获音频：', 'Audio konnte nicht erfasst werden: ', 'Nie udało się przechwycić dźwięku: '),
    'Не удалось получить цвет экранов: ': ('Could not capture screen color: ', '无法获取屏幕颜色：', 'Bildschirmfarbe konnte nicht erfasst werden: ', 'Nie udało się pobrać koloru ekranu: '),
    'Ошибка передачи музыки: ': ('Music transfer error: ', '音乐传输错误：', 'Fehler bei der Musikübertragung: ', 'Błąd przesyłania muzyki: '),
    'Источник': ('Audio source', '音源', 'Audioquelle', 'Źródło dźwięku'),
    'Выберите окно приложения или звуковой сеанс. Список доступен до начала воспроизведения.': ('Choose an application window or audio session. The list is available before playback starts.', '选择应用窗口或音频会话。播放开始前即可查看列表。', 'Wähle ein Anwendungsfenster oder eine Audiositzung. Die Liste ist vor Wiedergabestart verfügbar.', 'Wybierz okno aplikacji lub sesję audio. Lista jest dostępna przed rozpoczęciem odtwarzania.'),
    'Список приложений недоступен: ': ('Application list unavailable: ', '应用列表不可用：', 'Anwendungsliste nicht verfügbar: ', 'Lista aplikacji niedostępna: '),
    'Список приложений недоступен:': ('Application list unavailable:', '应用列表不可用：', 'Anwendungsliste nicht verfügbar:', 'Lista aplikacji niedostępna:'),
    'Низкие ноты → красный     Высокие → белый': ('Low notes → red     High notes → white', '低音 → 红色     高音 → 白色', 'Tiefe Töne → Rot     Hohe → Weiß', 'Niskie nuty → czerwony     Wysokie → biały'),
    'Ожидание аудиосигнала': ('Waiting for audio signal', '等待音频信号', 'Warte auf Audiosignal', 'Oczekiwanie na sygnał audio'),
    'Точка удалена · ПКМ удаляет, ЛКМ перетаскивает': ('Point deleted · right-click deletes, left-drag moves', '已删除节点 · 右键删除，左键拖动', 'Punkt gelöscht · Rechtsklick löscht, Ziehen mit links verschiebt', 'Punkt usunięty · prawy przycisk usuwa, lewy przeciąga'),
    'Выбранный цвет': ('Selected color', '所选颜色', 'Ausgewählte Farbe', 'Wybrany kolor'),
    'Точка {hz} Гц · двойной щелчок меняет цвет · Delete удаляет точку': ('Point {hz} Hz · double-click changes color · Delete removes the point', '节点 {hz} 赫兹 · 双击更改颜色 · Delete 删除节点', 'Punkt {hz} Hz · Doppelklick ändert Farbe · Delete löscht den Punkt', 'Punkt {hz} Hz · dwuklik zmienia kolor · Delete usuwa punkt'),
    'Точка {hz} Гц · перетаскивайте ЛКМ, удаляйте ПКМ': ('Point {hz} Hz · drag with left mouse, delete with right mouse', '节点 {hz} 赫兹 · 左键拖动，右键删除', 'Punkt {hz} Hz · mit linker Taste ziehen, mit rechter löschen', 'Punkt {hz} Hz · przeciągnij lewym, usuń prawym przyciskiem'),
    'Точка {hz} Гц': ('Point {hz} Hz', '节点 {hz} 赫兹', 'Punkt {hz} Hz', 'Punkt {hz} Hz'),
    'В профиле нужно не менее двух цветовых точек.': ('A profile must contain at least two color points.', '配置至少需要两个颜色节点。', 'Ein Profil muss mindestens zwei Farbpunkte enthalten.', 'Profil musi zawierać co najmniej dwa punkty kolorów.'),
    'Не удалось загрузить профиль: ': ('Could not load profile: ', '无法加载配置：', 'Profil konnte nicht geladen werden: ', 'Nie udało się wczytać profilu: '),
    'Не удалось загрузить профиль Fade: ': ('Could not load Fade profile: ', '无法加载 Fade 配置：', 'Fade-Profil konnte nicht geladen werden: ', 'Nie udało się wczytać profilu Fade: '),
    'Переключение ламп профиля начнётся после завершения текущей команды.': ('Profile lamp switching will begin when the current command finishes.', '当前命令完成后将切换配置中的灯具。', 'Die Lampen des Profils werden nach Abschluss des aktuellen Befehls gewechselt.', 'Przełączanie lamp profilu rozpocznie się po zakończeniu bieżącego polecenia.'),
    'Устройство отключено. Можно подключиться снова.': ('Device disconnected. You can reconnect.', '设备已断开。可以重新连接。', 'Gerät getrennt. Du kannst die Verbindung erneut herstellen.', 'Urządzenie rozłączone. Możesz połączyć ponownie.'),
    'Устройство отключено.': ('Device disconnected.', '设备已断开。', 'Gerät getrennt.', 'Urządzenie rozłączone.'),
    'Не удалось подключить устройство: ': ('Could not connect to device: ', '无法连接设备：', 'Gerät konnte nicht verbunden werden: ', 'Nie udało się połączyć z urządzeniem: '),
    'Устройство не поддерживает протокол LEDnetWF (FFFF/FF01).': ('The device does not support the LEDnetWF protocol (FFFF/FF01).', '设备不支持 LEDnetWF 协议（FFFF/FF01）。', 'Das Gerät unterstützt das LEDnetWF-Protokoll (FFFF/FF01) nicht.', 'Urządzenie nie obsługuje protokołu LEDnetWF (FFFF/FF01).'),
    'Отключение…': ('Disconnecting…', '正在断开…', 'Verbindung wird getrennt…', 'Rozłączanie…'),
    'Сохранить…': ('Save…', '保存…', 'Speichern…', 'Zapisz…'),
}


def detect_system_language():
    try:
        primary = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3ff
        return {0x19: 'ru', 0x09: 'en', 0x04: 'zh', 0x07: 'de', 0x15: 'pl'}.get(primary, 'en')
    except (AttributeError, OSError):
        name = (locale.getlocale()[0] or '').lower()
        if name.startswith('ru'):
            return 'ru'
        if name.startswith('zh'):
            return 'zh'
        if name.startswith('de'):
            return 'de'
        if name.startswith('pl'):
            return 'pl'
        return 'en'


def translate(text, language='ru'):
    if not isinstance(text, str) or language == 'ru':
        return text
    for template, translations in (
        ('Точка {hz} Гц · двойной щелчок меняет цвет · Delete удаляет точку', ('Point {hz} Hz · double-click changes color · Delete removes the point', '节点 {hz} 赫兹 · 双击更改颜色 · Delete 删除节点', 'Punkt {hz} Hz · Doppelklick ändert Farbe · Delete löscht den Punkt', 'Punkt {hz} Hz · dwuklik zmienia kolor · Delete usuwa punkt')),
        ('Точка {hz} Гц · перетаскивайте ЛКМ, удаляйте ПКМ', ('Point {hz} Hz · drag with left mouse, delete with right mouse', '节点 {hz} 赫兹 · 左键拖动，右键删除', 'Punkt {hz} Hz · mit linker Taste ziehen, mit rechter löschen', 'Punkt {hz} Hz · przeciągnij lewym, usuń prawym przyciskiem')),
        ('Точка {hz} Гц', ('Point {hz} Hz', '节点 {hz} 赫兹', 'Punkt {hz} Hz', 'Punkt {hz} Hz')),
    ):
        pattern = re.escape(template).replace(r'\{hz\}', r'(?P<hz>\d+)')
        match = re.fullmatch(pattern, text)
        if match:
            index = {'en': 0, 'zh': 1, 'de': 2, 'pl': 3}.get(language, 0)
            return translations[index].format(hz=match.group('hz'))
    for russian, translations in _ROWS.items():
        values = (russian,) + translations
        if text in values:
            return values[{'ru': 0, 'en': 1, 'zh': 2, 'de': 3, 'pl': 4}.get(language, 1)]
    # Preserve runtime values while translating recurring status templates.
    match = re.fullmatch(r'Подключено: (\d+)\. Команды — всем подключённым лампам\.', text)
    if match:
        n = match.group(1)
        return {'en': f'Connected: {n}. Commands go to all connected lamps.', 'zh': f'已连接：{n}。命令将发送到所有已连接的灯具。', 'de': f'Verbunden: {n}. Befehle gehen an alle verbundenen Lampen.', 'pl': f'Połączono: {n}. Polecenia trafią do wszystkich połączonych lamp.'}.get(language, text)
    match = re.fullmatch(r'Найдено устройств: (\d+)\.', text)
    if match:
        n = match.group(1)
        return {'en': f'Devices found: {n}.', 'zh': f'找到设备：{n}。', 'de': f'Geräte gefunden: {n}.', 'pl': f'Znalezione urządzenia: {n}.'}.get(language, text)
    match = re.fullmatch(r'(\d+) Гц\s+·\s+активен', text)
    if match:
        hz = match.group(1)
        return {'en': f'{hz} Hz · active', 'zh': f'{hz} 赫兹 · 活跃', 'de': f'{hz} Hz · aktiv', 'pl': f'{hz} Hz · aktywne'}.get(language, text)
    match = re.fullmatch(r'(\d+) Гц', text)
    if match:
        hz = match.group(1)
        return {'en': f'{hz} Hz', 'zh': f'{hz} 赫兹', 'de': f'{hz} Hz', 'pl': f'{hz} Hz'}.get(language, text)
    match = re.fullmatch(r'(\d+) кГц', text)
    if match:
        khz = match.group(1)
        return {'en': f'{khz} kHz', 'zh': f'{khz} 千赫', 'de': f'{khz} kHz', 'pl': f'{khz} kHz'}.get(language, text)
    match = re.fullmatch(r'(\d+(?:\.\d+)?) с', text)
    if match:
        seconds = match.group(1)
        return {'en': f'{seconds} s', 'zh': f'{seconds} 秒', 'de': f'{seconds} s', 'pl': f'{seconds} s'}.get(language, text)
    match = re.fullmatch(r'Точка (\d+) Гц · двойной щелчок меняет цвет · Delete удаляет точку', text)
    if match:
        hz = match.group(1)
        return {'en': f'Point {hz} Hz · double-click changes color · Delete removes the point', 'zh': f'节点 {hz} 赫兹 · 双击更改颜色 · Delete 删除节点', 'de': f'Punkt {hz} Hz · Doppelklick ändert Farbe · Delete löscht den Punkt', 'pl': f'Punkt {hz} Hz · dwuklik zmienia kolor · Delete usuwa punkt'}.get(language, text)
    match = re.fullmatch(r'Точка (\d+) Гц · перетаскивайте ЛКМ, удаляйте ПКМ', text)
    if match:
        hz = match.group(1)
        return {'en': f'Point {hz} Hz · drag with left mouse, delete with right mouse', 'zh': f'节点 {hz} 赫兹 · 左键拖动，右键删除', 'de': f'Punkt {hz} Hz · mit linker Taste ziehen, mit rechter löschen', 'pl': f'Punkt {hz} Hz · przeciągnij lewym, usuń prawym przyciskiem'}.get(language, text)
    match = re.fullmatch(r'Уровень (\d+\.\d{3})  ·  (.+)', text)
    if match:
        level, frequency = match.groups()
        translated_frequency = translate(frequency, language) if frequency.endswith(' Гц') else {
            'en': 'waiting for signal above threshold', 'zh': '等待高于阈值的信号',
            'de': 'warte auf Signal oberhalb der Schwelle', 'pl': 'oczekiwanie na sygnał powyżej progu',
        }.get(language, frequency)
        return {'en': f'Level {level}  ·  {translated_frequency}', 'zh': f'电平 {level}  ·  {translated_frequency}',
                'de': f'Pegel {level}  ·  {translated_frequency}', 'pl': f'Poziom {level}  ·  {translated_frequency}'}.get(language, text)
    match = re.fullmatch(r'Загружен профиль спектра «(.+)»\.', text)
    if match:
        name = match.group(1)
        return {'en': f'Spectrum profile “{name}” loaded.', 'zh': f'已加载频谱配置“{name}”。', 'de': f'Spektrumprofil „{name}“ geladen.', 'pl': f'Wczytano profil widma „{name}”.'}.get(language, text)
    match = re.fullmatch(r'Профиль спектра «(.+)» удалён\.', text)
    if match:
        name = match.group(1)
        return {'en': f'Spectrum profile “{name}” deleted.', 'zh': f'已删除频谱配置“{name}”。', 'de': f'Spektrumprofil „{name}“ gelöscht.', 'pl': f'Usunięto profil widma „{name}”.'}.get(language, text)
    match = re.fullmatch(r'Загружен профиль Fade «(.+)»\.', text)
    if match:
        name = match.group(1)
        return {'en': f'Fade profile “{name}” loaded.', 'zh': f'已加载 Fade 配置“{name}”。', 'de': f'Fade-Profil „{name}“ geladen.', 'pl': f'Wczytano profil Fade „{name}”.'}.get(language, text)
    match = re.fullmatch(r'Профиль Fade «(.+)» удалён\.', text)
    if match:
        name = match.group(1)
        return {'en': f'Fade profile “{name}” deleted.', 'zh': f'已删除 Fade 配置“{name}”。', 'de': f'Fade-Profil „{name}“ gelöscht.', 'pl': f'Usunięto profil Fade „{name}”.'}.get(language, text)
    for prefix, translations in (
        ('Не удалось загрузить профиль Fade: ', ('Could not load Fade profile: ', '无法加载 Fade 配置：', 'Fade-Profil konnte nicht geladen werden: ', 'Nie udało się wczytać profilu Fade: ')),
        ('Не удалось загрузить профиль: ', ('Could not load profile: ', '无法加载配置：', 'Profil konnte nicht geladen werden: ', 'Nie udało się wczytać profilu: ')),
        ('Не удалось подключить устройство: ', ('Could not connect to device: ', '无法连接设备：', 'Gerät konnte nicht verbunden werden: ', 'Nie udało się połączyć z urządzeniem: ')),
        ('Источник: ', ('Source: ', '音源：', 'Quelle: ', 'Źródło: ')),
        ('Не удалось получить цвет экранов: ', ('Could not capture screen color: ', '无法获取屏幕颜色：', 'Bildschirmfarbe konnte nicht erfasst werden: ', 'Nie udało się pobrać koloru ekranu: ')),
        ('Не удалось захватить звук: ', ('Could not capture audio: ', '无法捕获音频：', 'Audio konnte nicht erfasst werden: ', 'Nie udało się przechwycić dźwięku: ')),
        ('Ошибка передачи музыки: ', ('Music transfer error: ', '音乐传输错误：', 'Fehler bei der Musikübertragung: ', 'Błąd przesyłania muzyki: ')),
        ('Список приложений недоступен: ', ('Application list unavailable: ', '应用列表不可用：', 'Anwendungsliste nicht verfügbar: ', 'Lista aplikacji niedostępna: ')),
    ):
        if text.startswith(prefix):
            return translations[{'en': 0, 'zh': 1, 'de': 2, 'pl': 3}.get(language, 0)] + text[len(prefix):]
    return text
