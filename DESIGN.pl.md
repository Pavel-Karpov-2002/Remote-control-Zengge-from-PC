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
Język / Language: [Русский](DESIGN.md) · [English](DESIGN.en.md) · [中文](DESIGN.zh.md) · [Deutsch](DESIGN.de.md) · **Polski**

# Zengge Color Remote
## Przegląd
Aplikacja Windows do sterowania LEDnetWF. Obsługuje wiele połączeń BLE, wspólną jasność i zasilanie, kolory RGB, reakcję na częstotliwości muzyki, Fade oraz dopasowanie do średniego koloru ekranów. Języki interfejsu: rosyjski, angielski, chiński uproszczony, niemiecki i polski. Domyślnie używany jest język wyświetlania Windows; można wybrać go ręcznie.
## Kolory
Ciemne niebieskoszare tło i brzoskwiniowy akcent. Tekst w kole barw jest czarny lub biały zależnie od luminancji względnej, próg 0,179.
## Typografia
Segoe UI 10 pt; tytuł 21 pt pogrubiony; HEX 20 pt pogrubiony. Aktywna karta 12 pt pogrubiona, nieaktywna 10 pt.
## Układ
Okno 1040×800, minimum 960×760. Lewa kolumna 350 px: wyszukiwanie, łączenie, lista lamp, rozłączanie zaznaczonych, jasność i zasilanie. Po prawej cztery osobne karty: Kolor, Muzyka, Fade i Ekran. Trzywierszowy status na dole.
## Kształty
Koło kolorów do 270 px. Płaskie przyciski. Aktywna karta jest większa: odstęp 22×12 px i brzoskwiniowe tło; nieaktywna ma odstęp 14×6 px i powierzchnię drugorzędną.
## Komponenty
Kolor: koło z HEX, paleta, RGB i jawne zastosowanie. Muzyka: źródło systemowe lub proces, autostart, czułość, minimalna jasność, reakcja jasności, siła pulsowania i płynność. Mikser częstotliwości pokazuje widmo logarytmiczne, zakres, regulowany próg oraz edytowalny gradient z profilami. Fade: własny gradient, profile i ręcznie wpisywany czas przejścia w milisekundach. Ekran: średni kolor wszystkich ekranów i osobna jasność. Wszystkie tryby współdzielą transport BLE, płynność i skalowanie jasności.
Paleta to własne okno HSV: pole nasycenia/jasności, pasek odcienia, próbki bieżąca/nowa, HEX/RGB oraz zatwierdzenie/anulowanie. Strzałki sterują polem i odcieniem. Systemowe okno wyboru koloru nie jest używane. Wybór nie wysyła polecenia lampie przed zastosowaniem.
