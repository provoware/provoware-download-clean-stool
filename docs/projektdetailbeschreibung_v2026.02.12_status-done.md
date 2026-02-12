# Projektdetailbeschreibung (Version 2026.02.12, Status: DONE)

## Zielbild in einfacher Sprache
Dieses Tool räumt den Download-Ordner sicher auf, erklärt jeden Schritt verständlich und bietet klare Hilfe bei Fehlern.

## Umfang dieser Iteration (3 abgeschlossene Punkte)
1. **Regelwerk präzisiert:** README-Update darf alle 2–3 Iterationen erfolgen (oder sofort bei kritischen Änderungen).
2. **Aufgaben-Zählung geschärft:** Die 3 Pflichtpunkte beziehen sich auf funktionale Aspekte außerhalb reiner Info-Dateien.
3. **Erweiterbarkeit bewertet:** Technische Prüfung der Architektur mit konkreten Next Steps für nahezu perfekte Erweiterbarkeit.

## Dateinamen mit Version + Status (Strategie)
Gewünschtes Muster:
- `dateiname__vYYYY.MM.DD__status.ext`
- Statuswerte: `draft`, `review`, `done`, `deprecated`

Beispiele:
- `scan_report__v2026.02.12__done.json`
- `preset_export__v2026.02.12__review.json`

### Warum keine Sofort-Umbenennung aller bestehenden Dateien?
Eine globale Umbenennung würde viele Risiken erzeugen:
- Imports in Python brechen
- Shell-Skripte finden Dateien nicht mehr
- Tooling und Registry verlieren Referenzen

Darum: sichere Migration in Wellen (ohne Betriebsunterbrechung).

## Migrationsplan (sicher, schrittweise)
1. **Inventar erzeugen**: Alle Dateireferenzen in `app/`, `core/`, `tools/`, `start.sh` erfassen.
2. **Alias-Phase**: Neue Dateinamen einführen, alte Pfade vorübergehend als kompatible Verweise behalten.
3. **Umstellung + Tests**: Importpfade und Skriptpfade aktualisieren, Gates komplett laufen lassen.
4. **Bereinigung**: Alte Namen entfernen, Registry final anpassen.

## Erweiterbarkeits-Check (Ist-Analyse)
Stärken:
- Trennung von `core`, `app`, `tools`, `data` ist vorhanden.
- Qualitäts-Gates und Start-Routine sind bereits etabliert.

Verbesserung für „nahezu perfekt“:
- **Plugin-Punkte definieren** (Plugin = andockbares Zusatzmodul) für Scanner/Exporter.
- **Konfigurationsschema zentral validieren** (Schema = feste Strukturregeln für Einstellungen).
- **Einheitliche Fehlercodes** für GUI/CLI/API, damit Support leichter wird.

## Barrierefreiheit und Hilfetexte
- Nutzerhinweise bleiben in kurzer, klarer Sprache.
- Jede Fehlermeldung sollte 1–3 direkte Next Steps enthalten.
- Kontrast- und Theme-Checks bleiben Pflicht vor Release.

## Vollständige Befehle für die Prüfung
```bash
python -m compileall -q .
bash tools/run_quality_checks.sh
python tools/smoke_test.py
bash start.sh
```

## Zwei kurze Laienvorschläge
- Starte bei Problemen zuerst `bash start.sh`; dort bekommst du direkte Reparatur-Hinweise.
- Nutze danach `bash tools/run_quality_checks.sh`, um Fehler früh und automatisch zu finden.

## Detaillierter nächster Schritt
Als nächstes sollte ein kleines Modul `core/plugins.py` eingeführt werden, das Erweiterungen über eine registrierte Liste lädt. So kann man neue Funktionen ergänzen, ohne bestehende Kernlogik umzubauen.
