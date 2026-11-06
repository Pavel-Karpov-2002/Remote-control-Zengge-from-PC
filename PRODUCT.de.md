# Product
Sprache / Language: [Русский](PRODUCT.md) · [English](PRODUCT.en.md) · [中文](PRODUCT.zh.md) · **Deutsch** · [Polski](PRODUCT.pl.md)
<!-- impeccable:product-schema 1 -->

## Plattform
Windows Desktop x64, Python 3.12, Tkinter, Bleak/WinRT.

## Zweck
Desktop-App zur Steuerung von LEDnetWF über Bluetooth LE: mehrere Lampen, RGB, gemeinsame Helligkeit, musikgesteuerte Frequenzreaktion, Fade und Bildschirm-Farbabgleich. UI-Sprachen: Russisch, Englisch, vereinfachtes Chinesisch, Deutsch und Polnisch. Standard ist die Windows-Anzeigesprache; die Auswahl in der App wird gespeichert.

## Funktionen und Grenzen
Befehle gehen an alle verbundenen Lampen; ausgewählte Lampen können getrennt werden. Der Verbindungsverlust einer Lampe beendet die anderen Verbindungen nicht. Die tatsächliche Kapazität hängt von der Hardware ab.
Audioquellen: gesamter Systemton oder ein Anwendungsprozess samt Unterprozessen. Sichtbare Fenster und Sitzungen aktiver Ausgänge werden auch vor Wiedergabestart aufgelistet.
Audiospektrum mit verschiebbaren Frequenzgrenzen und vertikaler Schwelle. Tiefe Töne entsprechen Rot, hohe Töne Weiß; die Helligkeit reagiert auf die Energie im ausgewählten Band. Empfindlichkeit, Pulsstärke, reaktive Helligkeit und Glättung sind verfügbar.
Fade wechselt kontinuierlich durch Farben oder einzelne Farbtöne, mit eigener Helligkeit und Zykluszeit. Der Bildschirmmodus verwendet die Durchschnittsfarbe der angeschlossenen Desktop-Monitore und hat eine eigene Helligkeitsregelung.
Bei Stille oder Pause bleiben letzte Farbe und Helligkeit erhalten. Stoppen stellt die manuelle Farbe wieder her; Ausschalten schaltet Lampen aus.
Audio wird weder aufgezeichnet noch über das Netzwerk gesendet. Einzelne LED-Gruppen gehören nicht zum Umfang.

## Verteilung
Quellcode: Pavel-Karpov-2002/Remote-control-Zengge-from-PC. Ausführbare Dateien und Installer gehören in GitHub Releases, nicht in die Git-Historie.

## Visuelle Anforderungen
Kompaktes dunkles Desktop-Panel mit vertrauten Windows-Steuerelementen und fünf wählbaren UI-Sprachen.
