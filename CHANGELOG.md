# Change Log

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
