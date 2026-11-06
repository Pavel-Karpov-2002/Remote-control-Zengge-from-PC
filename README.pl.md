# Zengge dla Windows

Język / Language: [Русский](README.md) · [English](README.en.md) · [中文](README.zh.md) · [Deutsch](README.de.md) · **Polski**

Steruj lampami LEDnetWF przez Bluetooth LE: podłączaj wiele lamp, ustawiaj kolor RGB i jasność, reaguj na częstotliwości muzyki, uruchamiaj płynne efekty Fade lub dopasuj kolor do średniej barwy pulpitu.

**[Pobierz najnowszą wersję dla Windows x64](https://github.com/Pavel-Karpov-2002/Remote-control-Zengge-from-PC/releases/latest/download/ZenggeColorRemote.exe)**

Wersja 0.4.0. Aplikacja ma osobne karty Kolor, Muzyka, Fade i Ekran. Interfejs obsługuje rosyjski, angielski, chiński uproszczony, niemiecki i polski. Przy pierwszym uruchomieniu używa języka wyświetlania Windows. Język można zmienić w aplikacji; wybór zostaje zapisany.

Python nie jest wymagany. Pobierz i uruchom `ZenggeColorRemote.exe` z sekcji [Releases](https://github.com/Pavel-Karpov-2002/Remote-control-Zengge-from-PC/releases).

## Łączenie lamp

1. Włącz Bluetooth na komputerze i zasilanie lampy. Zamknij aplikację lampy na telefonie, jeśli zajmuje połączenie.
2. Kliknij **Szukaj**, wybierz lampę i kliknij **Połącz**.
3. Wybierz kolejną lampę i połącz ją. W razie potrzeby ponów wyszukiwanie.
4. Połączone lampy otrzymują wspólne polecenia koloru, jasności, zasilania i efektów.
5. Aby rozłączyć lampę, zaznacz ją na liście i kliknij **Rozłącz wybrane**. Ctrl lub Shift pozwala zaznaczyć kilka wierszy. Zamknięcie okna rozłącza wszystkie lampy.

Utrata połączenia z jedną lampą nie zatrzymuje pozostałych. Liczba jednoczesnych połączeń i możliwość wyszukiwania podczas połączenia zależą od adaptera Bluetooth i sterownika. Nowe połączenie nie przerywa istniejących. Kolor widoczny w aplikacji to wybrana lub wysłana wartość, a nie potwierdzony stan lampy.

## Kolor i jasność

Kliknij **Włącz**. Na karcie Kolor wybierz odcień przez **Paleta…** albo wpisz wartości RGB (0–255), a następnie kliknij **Zastosuj kolor**. Wspólny suwak **Jasność** (0–100%) reguluje światło ręczne i ogranicza maksymalny poziom trybu muzyki.

## Muzyka

Połącz lampy i otwórz kartę Muzyka. Wybierz źródło dźwięku lub włącz automatyczny wybór i start po wykryciu dźwięku. Fade i Ekran mają osobne karty oraz przyciski uruchamiania. Lampy włączają się automatycznie.

| Ustawienie | Działanie |
| --- | --- |
| Źródło dźwięku | Cały dźwięk z domyślnego wyjścia Windows albo wybrana aplikacja wraz z procesami potomnymi |
| Odśwież | Odświeża listę okien i sesji audio aktywnych wyjść; odtwarzanie nie musi być wcześniej uruchomione |
| Mikser częstotliwości | Logarytmiczne widmo z wybieranym zakresem, regulowanym progiem i własnym gradientem kolorów. Dodaj punkty dwuklikiem, przeciągaj lewym przyciskiem, usuwaj prawym. |
| Profile widma | Zapisują zakres częstotliwości, próg, gradient i wybrane lampy. Zmiana profilu przełącza połączone lampy. |
| Czułość | Wzmocnienie sygnału do wykrywania częstotliwości; samo nie zmienia jasności |
| Minimalna jasność muzyki | Dolny limit jasności; dodawany jest do niego poziom dźwięku, maksymalnie do 100% |
| Jasność reaguje na muzykę | Włącza zmianę jasności zależną od poziomu dźwięku; bez tej opcji jasność jest stała |
| Siła pulsowania | Głębokość zmian jasności: 0% oznacza stałą jasność, 100% — najsilniejszą reakcję |
| Płynność | Wygładza przejścia koloru i jasności; wyższa wartość oznacza wolniejsze, łagodniejsze przejścia |
| Fade | Kolory ustawia się na pasku gradientu, tak jak w mikserze. Osobne profile palety, jasność i ręcznie ustawiany czas przejścia w milisekundach. |
| Ekran | Dopasowuje kolor do średniej obrazu ze wszystkich monitorów Windows i ma osobny regulator jasności. |

Ustawienia są zachowywane między uruchomieniami. Aplikacja ponownie łączy zapisane lampy. Kółko myszy reguluje suwak pod wskaźnikiem.

**Podczas pauzy, ciszy i po końcu utworu zachowywane są ostatni kolor i jasność.** Dotyczy to także włączonej reakcji jasności. Po powrocie dźwięku zmiany są kontynuowane. **Zatrzymaj** kończy efekt i przywraca kolor ręczny. **Wyłącz** kończy efekt i wyłącza wszystkie połączone lampy.

Zatrzymaj efekt przed zmianą źródła. Po ponownym uruchomieniu aplikacji odśwież listę i wybierz ją ponownie. Tytuły okien ułatwiają rozpoznanie aplikacji, ale przechwytywanie obejmuje proces i jego procesy potomne; kart przeglądarki nie można rozdzielić. Okno bez strumienia audio można wybrać wcześniej — stanie się aktywne, gdy rozpocznie odtwarzanie. Aplikacje działające w tle bez okna lub sesji audio mogą pojawić się później.

Dźwięk systemowy jest pobierany przez WASAPI loopback; mikrofon nie jest potrzebny. Analiza widma działa lokalnie: dźwięk nie jest zapisywany ani wysyłany przez sieć. Średni kolor ekranu jest przechwytywany przez Windows GDI z pulpitu wirtualnego, także z dodatkowymi monitorami. Przechwytywanie pojedynczych aplikacji wymaga Windows build 20348+ / Windows 11. Starsze wersje obsługują dźwięk systemowy. Jeśli przechwytywanie aplikacji jest niedostępne, aplikacja zgłasza błąd i nie przełącza się na dźwięk systemowy. Dźwięk chroniony DRM może być niedostępny. Mowa i dźwięki systemowe wpływają na tryb muzyki, jeśli należą do wybranego źródła.

## Budowanie

Windows z Pythonem 3.12 x64 i Tkinterem:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
.\build.ps1
```

Wynik budowania: `dist/ColorRemote/ZenggeColorRemote.exe`. Pliki wykonywalne są publikowane w Releases, a nie w repozytorium Git.

## Protokół i zgodność

Protokół bazuje na [8none1/zengge_lednetwf](https://github.com/8none1/zengge_lednetwf), commit `f4d20fc3225e4b8b5637b5951fff59d91882a53c`. UUID usługi FFFF, zapis FF01, powiadomienia FF02. RGB jest konwertowane do udokumentowanego pakietu HSV 3B A1 z precyzją kontrolera. Transport wykorzystuje Bleak/WinRT; Linux i Home Assistant nie są wymagane.

Autor oryginalnego projektu kontynuuje badania w [lednetwf_ble](https://github.com/8none1/lednetwf_ble). Polecenia mogą różnić się zależnie od modelu i oprogramowania układowego. Sterowanie poszczególnymi diodami i wbudowane efekty kontrolera nie są obsługiwane w tej wersji.
