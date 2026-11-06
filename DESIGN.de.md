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
Sprache / Language: [Русский](DESIGN.md) · [English](DESIGN.en.md) · [中文](DESIGN.zh.md) · **Deutsch** · [Polski](DESIGN.pl.md)

# Zengge Color Remote
## Überblick
Windows-App zur Steuerung von LEDnetWF. Unterstützt mehrere BLE-Verbindungen, gemeinsame Helligkeit und Stromversorgung, RGB-Farbe, musikgesteuerte Frequenzreaktion, Fade und Anpassung an die durchschnittliche Displayfarbe. Sprachen: Russisch, Englisch, vereinfachtes Chinesisch, Deutsch und Polnisch. Standard ist die Windows-Anzeigesprache; die Sprache kann manuell geändert werden.
## Farben
Dunkel blaugrauer Hintergrund mit pfirsichfarbenem Akzent. Text im Farbkreis ist je nach relativer Leuchtdichte schwarz oder weiß; Schwelle 0,179.
## Typografie
Segoe UI 10 pt; Titel 21 pt fett; HEX 20 pt fett. Aktiver Tab 12 pt fett, inaktiver Tab 10 pt.
## Layout
Fenster 1040×800, Mindestgröße 960×760. Links 350 px: Suche, Verbindung, Lampenliste, ausgewählte Lampen trennen, Helligkeit und Stromversorgung. Rechts vier Tabs: Farbe, Musik, Fade und Bildschirm. Statusbereich unten mit drei Zeilen.
## Formen
Farbkreis bis 270 px. Flache Schaltflächen. Aktiver Tab größer: 22×12 px Innenabstand und pfirsichfarbene Fläche; inaktive Tabs mit 14×6 px und sekundärer Fläche.
## Komponenten
Farbe: Kreis mit HEX, Palette, RGB und expliziter Übernahme. Musik: System- oder Prozessquelle, automatischer Start, Empfindlichkeit, Mindesthelligkeit, reaktive Helligkeit, Pulsstärke und Glättung. Frequenzmischer mit logarithmischem Spektrum, Bereich, einstellbarer Schwelle und bearbeitbarem Farbverlauf samt Profilen. Fade: eigener Farbverlauf, Profile und manuelle Übergangszeit in Millisekunden. Bildschirm: Durchschnittsfarbe aller Displays und eigene Helligkeit. Alle Modi teilen BLE-Transport, Glättung und Helligkeitsskalierung.
Die Palette ist ein eigenes HSV-Fenster: Sättigungs-/Wertfeld, Farbtonleiste, aktuelle/neue Vorschau, HEX/RGB sowie Bestätigen/Abbrechen. Pfeiltasten bedienen Feld und Farbton. Der System-Farbwähler wird nicht verwendet. Eine Auswahl sendet erst nach dem Anwenden einen Lampenbefehl.
