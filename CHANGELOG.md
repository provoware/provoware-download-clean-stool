# Change Log

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.7] – 2026‑02‑10

## [1.0.11] – 2026‑02‑10

### Changed

* Was: `start.sh` prüft vor dem Smoke-Test jetzt explizit auf die Linux-Systembibliothek `libGL.so.1`, zeigt bei Bedarf eine klare Reparaturhilfe in einfacher Sprache und bietet direkt „Jetzt installieren“ (per `zenity`) mit automatischer `apt`-Reparatur (`libgl1`) an.
* Warum: Auf frischen Linux-Systemen kann die GUI trotz korrekter Python-Pakete nicht starten, wenn der Grafik-Baustein fehlt.
* Wirkung: Nutzer sehen die Ursache sofort, bekommen eine laienfreundliche Lösung und können den Fehler ohne Logsuche automatisiert beheben.

## [1.0.10] – 2026‑02‑10

### Changed

* Was: `start.sh` bereitet Requirements jetzt in `exports/requirements.sanitized.txt` auf, prüft nach der Installation automatisch auf Versionskonflikte (`pip check`) und startet eine automatische Reparatur (offline zuerst, dann online mit `--upgrade-strategy eager`).
* Warum: Abhängigkeitskonflikte wurden bisher nicht aktiv erkannt/behoben und konnten den Start trotz installierter Pakete blockieren.
* Wirkung: Stabilere Abhängigkeitsauflösung, bessere Offline-Resilienz und klare Hilfe-Ausgaben für Nutzer:innen bei verbleibenden Paketproblemen.

## [1.0.9] – 2026‑02‑10

### Changed

* Was: `start.sh` gibt nach der Paketprüfung jetzt immer eine klare Abschluss-Zusammenfassung aus (erfolgreich installiert, übersprungen, Fehler, Offline-/Online-Quelle).
* Warum: Die Startroutine soll vollautomatisch transparent sein, damit Nutzer sofort verstehen, was passiert ist und was noch zu tun ist.
* Wirkung: Besseres Nutzerfeedback in einfacher Sprache und schnellere Fehleranalyse ohne manuelles Log-Durchsuchen.

## [1.0.8] – 2026‑02‑10

### Changed

* Was: `start.sh` versucht bei fehlenden Kernmodulen (`PySide6`, `PIL`) jetzt zusätzlich eine automatische Reparatur über `apt` (Ubuntu/Kubuntu), führt danach einen Recheck aus und bricht nur noch mit klarer Hilfe ab, wenn Module weiterhin fehlen.
* Warum: Das Tool ist Linux-first für Kubuntu gedacht; fehlende Python-GUI-Abhängigkeiten sollen ohne manuelle Analyse direkt durch die Startroutine behoben werden.
* Wirkung: Mehr Autonomie beim Start, verständlichere Fehlermeldungen in einfacher Sprache und klarere Next-Steps für den Nutzer bei verbleibenden Problemen.

## [1.0.7] – 2026‑02‑10

### Changed

* Was: `start.sh` bereinigt Requirement-Zeilen jetzt Linux-robust (Whitespace, Inline-Kommentare, CRLF-Reste) und überspringt nicht installierbare Optionseinträge (`-...`) statt sie fälschlich als Paket zu behandeln.
* Warum: In gemischten Umgebungen (z. B. kopierte `requirements.txt` mit Windows-Zeilenenden) führte die bisherige Logik leichter zu unnötigen Install-Fehlern.
* Wirkung: Stabilere automatische Abhängigkeitsauflösung beim Start, weniger Fehlalarme und klareres Nutzerfeedback durch explizite `[OK]`-Statusmeldungen je Paket.

## [1.0.6] – 2026‑02‑10

### Changed

* Was: Haupt-Dashboard (Schritt 1) zeigt jetzt eine laienfreundliche Schnellübersicht mit Systemstatus, Zielordner, aktivem Preset, Filter- und Duplikatmodus sowie klaren Nächste-Schritte-Hinweisen.
* Warum: Nutzer:innen sollen direkt beim Start verständliche Orientierung bekommen und wichtige Einstellungen auf einen Blick prüfen können.
* Wirkung: Bessere Auffindbarkeit zentraler Infos, lesbarere Darstellung (WordWrap) und mehr Barrierefreiheit durch einfache Sprache im Einstieg.

## [1.0.5] – 2026‑02‑10

### Changed

* Was: README startet jetzt mit drei kompakten Stichpunkt-Zeilen zu Fertig/Offen/Fortschritt inkl. nächster Schritte, und AGENTS.md fordert pro Iteration ein Hilfeelement plus einen Barrierefreiheitsaspekt.
* Warum: Fortschritt und Handlungsplan sollen sofort sichtbar sein und Iterationen sollen durchgehend nutzerfreundlicher sowie barriereärmer werden.
* Wirkung: Klarerer Status für Laien direkt beim Öffnen und verbindliche Qualitätsrichtung für kommende Patches.

## [1.0.4] – 2026‑02‑10

### Fixed

* Was: Theme-Auswahl mappt jetzt konsistent zwischen UI-Werten ("hell/dunkel") und internen Werten ("light/dark").
* Warum: Gespeicherte englische Themes wurden in der deutschen Auswahl nicht korrekt vorausgewählt und konnten inkonsistent zurückgeschrieben werden.
* Wirkung: Theme-Anzeige und Speichern funktionieren stabil in beide Richtungen.

## [1.0.3] – 2026‑02‑10

### Changed

* Was: `start.sh` nutzt jetzt optional den Ordner `offline_wheels/` und installiert Pakete zuerst offline, danach erst online als Fallback.
* Warum: Das Tool soll portabel/offline startfähig bleiben, wenn Abhängigkeiten bereits mitgeliefert werden.
* Wirkung: Ohne Internet kann der Start weiterlaufen, sobald passende Wheels lokal im Projekt liegen.

## [1.0.2] – 2026‑02‑10

### Fixed

* Was: `tools/smoke_test.py` ergänzt den Projektpfad jetzt vor den Imports in `sys.path`.
* Warum: Der Smoke-Test wurde als Datei gestartet und fand dadurch `core` im Standard-Pfad nicht zuverlässig.
* Wirkung: `python tools/smoke_test.py` läuft reproduzierbar aus dem Projektordner ohne `ModuleNotFoundError`.

## [1.0.1] – 2026‑02‑10

### Changed

* Was: `core/settings.py` lädt UI-Texte jetzt zentral aus `settings.json` über das Feld `ui_texts` mit sicheren Fallback-Texten.
* Warum: Texte sollen versionierbar und außerhalb des Codes pflegbar sein.
* Wirkung: Konfiguration ist robust gegen fehlende Keys und unterstützt einheitliche Textquellen.

## [1.0.0] – 2026‑02‑10

### Added

* Initial public release of the Downloads Organizer.
* Four‑step wizard for folder cleaning with presets and custom options.
* Duplicate detection (quick and safe modes).
* Dry‑run plan preview and undo functionality.
* Theme support with light, dark, high‑contrast and extra‑large text modes.
* Self‑check on startup, quality check and logs.

### Fixed

* None yet; this is the first release.
