# CHANGELOG

## 2026-02-10 – Start-Iteration: Auto-Reparatur-Endstatus klar ausgewiesen
- **Was:** `start.sh` zeigt jetzt zusätzlich einen expliziten Auto-Reparatur-Status (`nicht nötig`, `erfolgreich`, `nicht möglich`) inklusive Symbol und einfacher Statusmeldung.
- **Warum:** Offener Punkt aus `todo.txt`: Der Reparaturausgang sollte ohne Fachwissen sofort verständlich sein.
- **Wirkung:** Nutzer:innen sehen direkt, ob die automatische Reparatur geklappt hat und welche nächsten Schritte nötig sind.

## 2026-02-10 – Doku-Iteration: Entwickler-Actionplan ergänzt
- **Was:** README um einen klaren Abschnitt „Sinnvolle Actions“ mit vollständigen Befehlen für Start, Qualitätsgates, Auto-Formatierung, Debug-Mode und A11y-Quickcheck erweitert.
- **Warum:** Die Frage nach konkreten, hilfreichen Entwicklungsaktionen sollte mit sofort nutzbaren, laienfreundlichen Standards beantwortet werden.
- **Wirkung:** Entwickler:innen erhalten eine einheitliche, barrierearme Schrittfolge für bessere Codequalität und reproduzierbare Abläufe.

## 2026-02-10 – Start-Iteration: Headless-Start ohne Crash
- **Was:** `start.sh` erkennt jetzt fehlende grafische Sitzung (`DISPLAY`/`WAYLAND_DISPLAY`) vor dem GUI-Start und zeigt eine klare Hilfe mit nächsten Schritten.
- **Warum:** In Headless-Umgebungen kam es bisher zu einem harten GUI-Startfehler statt zu einer verständlichen Rückmeldung.
- **Wirkung:** Startablauf bleibt stabil ohne Crash; Nutzer:innen erhalten barrierearme Anleitung für Desktop-Start oder Display-Setup.

## 2026-02-10 – Qualitäts-Iteration: Syntax-Gate auf Projektcode begrenzt
- **Was:** `tools/run_quality_checks.sh` prüft `compileall` jetzt gezielt nur `app/`, `core/`, `tools/` und `start.sh` statt den gesamten Projektordner.
- **Warum:** So bleiben Gate-Meldungen konsistent auf eigenem Code und vermeiden Rauschen aus virtuellen Umgebungen oder Build-Artefakten.
- **Wirkung:** Klarere Qualitätsrückmeldungen, weniger Fehlalarme und bessere Nutzerführung in der Startroutine.

## 2026-02-10 – Start-Iteration: Qualitätsstatus im Start klar zusammengefasst
- **Was:** `start.sh` zeigt nach dem Qualitätslauf jetzt einen kompakten Status mit Symbol, Warn-/Info-Anzahl und klarem nächsten Schritt inkl. Log-Pfad.
- **Warum:** Nutzer:innen sollen ohne Fachwissen sofort verstehen, ob sie handeln müssen und wo die Details stehen.
- **Wirkung:** Bessere Zugänglichkeit durch klare, einfache Rückmeldung und schnellere Fehlerführung im Startablauf.

## 2026-02-10 – Doku-Iteration: Info-Dateien vereinheitlicht
- **Was:** README auf barrierearme, einheitliche Standards mit klaren Pflichtbefehlen aktualisiert.
- **Warum:** Anforderungen zu einfacher Sprache, automatischer Prüfung/Startroutine und klaren Qualitätsstandards mussten zentral und verständlich dokumentiert werden.
- **Wirkung:** Nutzer:innen und Support sehen jetzt sofort ein konsistentes Vorgehen inkl. Next Steps, Qualitäts-Gates und laienfreundlicher Empfehlungen.

## 2026-02-10 – Fehlerdialog-Iteration: Next-Step-Buttons ergänzt
- **Was:** `tools/boot_error_gui.py` zeigt im Zenity-Dialog jetzt klare Next-Step-Aktionen: „Erneut versuchen“, „Reparatur“ und „Protokoll“.
- **Warum:** Offener Punkt aus `todo.txt`: Fehlerfälle sollten direkt bedienbare Hilfewege statt nur einer Schließen-Aktion bieten.
- **Wirkung:** Bessere Barrierefreiheit und Nutzerführung durch verständliche Auswahl direkt im Fehlerdialog.
