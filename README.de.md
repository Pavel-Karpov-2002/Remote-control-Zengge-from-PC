# Zengge für Windows

Sprache / Language: [Русский](README.md) · [English](README.en.md) · [中文](README.zh.md) · **Deutsch** · [Polski](README.pl.md)

Steuere LEDnetWF-Lampen über Bluetooth LE: verbinde mehrere Lampen, stelle RGB-Farbe und Helligkeit ein, reagiere auf Musikfrequenzen, nutze fließende Fade-Effekte oder passe die Farbe an den durchschnittlichen Desktop-Farbton an.

**[Neueste Windows-x64-Version herunterladen](https://github.com/Pavel-Karpov-2002/Remote-control-Zengge-from-PC/releases/latest/download/ZenggeColorRemote.exe)**

Version 0.4.0. Die App bietet separate Tabs für Farbe, Musik, Fade und Bildschirm. Die Oberfläche unterstützt Russisch, Englisch, vereinfachtes Chinesisch, Deutsch und Polnisch. Beim ersten Start wird die Windows-Anzeigesprache verwendet. Die Auswahl lässt sich in der App ändern und wird gespeichert.

Python ist nicht erforderlich. Lade `ZenggeColorRemote.exe` unter [Releases](https://github.com/Pavel-Karpov-2002/Remote-control-Zengge-from-PC/releases) herunter und starte die Datei.

## Lampen verbinden

1. Aktiviere Bluetooth am PC und schalte die Lampe ein. Schließe die Smartphone-App, falls sie die Verbindung belegt.
2. Klicke auf **Suchen**, wähle eine Lampe und klicke auf **Verbinden**.
3. Wähle weitere Lampen aus und verbinde sie. Wiederhole die Suche bei Bedarf.
4. Verbundene Lampen erhalten dieselben Befehle für Farbe, Helligkeit, Stromversorgung und Effekte.
5. Zum Trennen wählst du die Lampe in der Liste und klickst auf **Ausgewählte trennen**. Mit Strg oder Umschalt kannst du mehrere Zeilen markieren. Beim Schließen des Fensters werden alle Lampen getrennt.

Die Verbindung zu einer Lampe kann abbrechen, ohne die anderen zu stoppen. Anzahl gleichzeitiger Verbindungen und Suche bei bestehender Verbindung hängen vom Bluetooth-Adapter und Treiber ab. Eine neue Verbindung beendet bestehende Verbindungen nicht. Die angezeigte Farbe ist der ausgewählte oder gesendete Wert, keine bestätigte Rückmeldung der Lampe.

## Farbe und Helligkeit

Klicke auf **Einschalten**. Wähle im Tab „Farbe“ einen Farbton über **Farbpalette…** oder gib RGB-Werte (0–255) ein und klicke auf **Farbe anwenden**. Der gemeinsame Regler **Helligkeit** (0–100 %) steuert das manuelle Licht und begrenzt die maximale Helligkeit im Musikmodus.

## Musik

Verbinde die Lampen und öffne den Tab „Musik“. Wähle eine Audioquelle oder aktiviere die automatische Quellenauswahl und den Start bei erkanntem Ton. Fade und Bildschirm haben eigene Tabs und Startknöpfe. Lampen werden automatisch eingeschaltet.

| Einstellung | Funktion |
| --- | --- |
| Audioquelle | Gesamter Ton des Windows-Standardausgangs oder eine Anwendung einschließlich ihrer Unterprozesse |
| Aktualisieren | Aktualisiert Fenster und Audiositzungen aktiver Ausgänge; Wiedergabe muss nicht vorher gestartet werden |
| Frequenzmischer | Logarithmisches Spektrum mit wählbarem Bereich, einstellbarer Auslöseschwelle und eigenem Farbverlauf. Punkte per Doppelklick hinzufügen, mit linker Maustaste ziehen und per Rechtsklick löschen. |
| Spektrumprofile | Speichern Frequenzbereich, Schwelle, Farbverlauf und ausgewählte Lampen. Beim Profilwechsel werden die verbundenen Lampen angepasst. |
| Empfindlichkeit | Signalverstärkung zur Frequenz­erkennung; ändert die Helligkeit nicht direkt |
| Mindesthelligkeit für Musik | Untere Helligkeitsgrenze; der Audiopegel wird addiert, maximal 100 % |
| Helligkeit an Musik anpassen | Aktiviert Helligkeitsänderungen durch den Audiopegel; sonst bleibt sie konstant |
| Pulsstärke | Tiefe der Helligkeitsänderung: 0 % ist konstant, 100 % die stärkste Reaktion |
| Glättung | Glättet Farb- und Helligkeitsübergänge; höhere Werte ergeben langsamere, weichere Übergänge |
| Fade | Farben wie im Mischer auf einer Verlaufsleiste einstellen. Eigene Farbprofile, Helligkeit und manuelle Übergangszeit in Millisekunden. |
| Bildschirm | Passt die Farbe an den Durchschnitt aller Windows-Monitore an und besitzt einen eigenen Helligkeitsregler. |

Einstellungen bleiben zwischen Starts erhalten. Die App verbindet gespeicherte Lampen erneut. Das Mausrad bedient den Regler unter dem Zeiger.

**Bei Pausen, Stille und nach dem Ende eines Titels bleiben die letzte Farbe und Helligkeit erhalten.** Das gilt auch bei aktivierter reaktiver Helligkeit. Sobald wieder Ton anliegt, setzt die Änderung fort. **Stoppen** beendet den Effekt und stellt die manuelle Farbe wieder her. **Ausschalten** beendet den Effekt und schaltet alle verbundenen Lampen aus.

Beende den Effekt, bevor du die Quelle wechselst. Nach einem Neustart einer Anwendung aktualisierst du die Liste und wählst sie erneut aus. Fenstertitel helfen bei der Identifikation; erfasst wird der Prozess samt Unterprozessen. Browser-Tabs lassen sich nicht trennen. Ein Fenster ohne Audiostream kann vorab ausgewählt werden und wird bei Wiedergabestart aktiv. Hintergrundanwendungen ohne Fenster oder Audiositzung erscheinen möglicherweise erst später.

Systemton wird über WASAPI-Loopback erfasst; ein Mikrofon ist nicht nötig. Die Spektrumanalyse erfolgt lokal; Audio wird weder gespeichert noch übertragen. Die Bildschirmfarbe wird per Windows GDI vom virtuellen Desktop einschließlich weiterer Monitore erfasst. Einzelne Anwendungen erfordern Windows Build 20348+ / Windows 11. Ältere Versionen unterstützen Systemaudio. Ist die Anwendungserfassung nicht verfügbar, meldet die App einen Fehler und wechselt nicht automatisch zum Systemton. DRM-geschützte Audiodaten sind möglicherweise nicht verfügbar. Sprache und Systemtöne beeinflussen den Musikmodus, wenn sie zur ausgewählten Quelle gehören.

## Build

Windows mit Python 3.12 x64 und Tkinter:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
.\build.ps1
```

Build-Ausgabe: `dist/ColorRemote/ZenggeColorRemote.exe`. Ausführbare Dateien werden unter Releases veröffentlicht und nicht in Git eingecheckt.

## Protokoll und Kompatibilität

Das Protokoll basiert auf [8none1/zengge_lednetwf](https://github.com/8none1/zengge_lednetwf), Commit `f4d20fc3225e4b8b5637b5951fff59d91882a53c`. Dienst-UUID FFFF, Schreibmerkmal FF01, Benachrichtigungen FF02. RGB wird mit der Genauigkeit des Controllers in das dokumentierte HSV-3B-A1-Paket umgewandelt. Der Transport nutzt Bleak/WinRT; Linux und Home Assistant sind nicht erforderlich.

Der ursprüngliche Autor setzt die Forschung unter [lednetwf_ble](https://github.com/8none1/lednetwf_ble) fort. Befehle können je nach Modell und Firmware abweichen. Einzelne LEDs und integrierte Controller-Effekte werden in dieser Version nicht unterstützt.
