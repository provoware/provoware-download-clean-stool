# CHANGELOG

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
