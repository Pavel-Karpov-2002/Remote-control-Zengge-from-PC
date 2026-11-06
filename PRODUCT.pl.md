# Product
Język / Language: [Русский](PRODUCT.md) · [English](PRODUCT.en.md) · [中文](PRODUCT.zh.md) · [Deutsch](PRODUCT.de.md) · **Polski**
<!-- impeccable:product-schema 1 -->

## Platforma
Windows desktop x64, Python 3.12, Tkinter, Bleak/WinRT.

## Cel
Aplikacja desktopowa do sterowania LEDnetWF przez Bluetooth LE: wiele lamp, RGB, wspólna jasność, reakcja na częstotliwości muzyki, Fade i dopasowanie koloru ekranu. Języki interfejsu: rosyjski, angielski, chiński uproszczony, niemiecki i polski. Domyślnie używany jest język wyświetlania Windows; wybór w aplikacji jest zapisywany.

## Możliwości i ograniczenia
Polecenia trafiają do wszystkich połączonych lamp; zaznaczone lampy można rozłączyć. Utrata jednego połączenia nie kończy pozostałych. Rzeczywista pojemność adaptera zależy od sprzętu.
Źródła audio: cały dźwięk systemowy lub proces aplikacji wraz z procesami potomnymi. Lista widocznych okien i sesji aktywnych urządzeń wyjściowych jest dostępna przed rozpoczęciem odtwarzania.
Widmo audio z przesuwanymi granicami częstotliwości i pionowym progiem. Niskie nuty odpowiadają czerwieni, wysokie — bieli; jasność reaguje na energię wybranego pasma. Dostępne są czułość, siła pulsowania, reakcja jasności i płynność.
Fade płynnie przechodzi przez kolory lub osobne odcienie, z niezależną jasnością i czasem cyklu. Tryb ekranu używa średniego koloru podłączonych monitorów pulpitu i ma osobną regulację jasności.
Podczas ciszy lub pauzy pozostaje ostatni kolor i jasność. Zatrzymanie efektu przywraca kolor ręczny; wyłączenie gasi lampy.
Dźwięk nie jest nagrywany ani wysyłany przez sieć. Sterowanie grupami pojedynczych LED nie jest przewidziane.

## Dystrybucja
Kod źródłowy: Pavel-Karpov-2002/Remote-control-Zengge-from-PC. Pliki EXE i instalatory publikowane są w GitHub Releases, nie w historii Git.

## Wymagania wizualne
Kompaktowy, ciemny panel desktopowy ze znanymi kontrolkami Windows i pięcioma językami interfejsu.
