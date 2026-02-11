# Release-Finalisierung – Statusdatei (Iteration)

Stand: 2026-02-11

## Entwicklungsfortschritt

- **Gesamtfortschritt:** **83%**
- **Abgeschlossene Punkte:** **15**
- **Offene Punkte:** **3**

Berechnung (einfach): `15 abgeschlossen / 18 gesamt = 83,3%`.

## Release-Checkliste

### ✅ Abgeschlossen (15)
- [x] Startroutine mit klaren Auto-Reparatur-Endstatusmeldungen.
- [x] Qualitäts-Gate-Skript vorhanden (`tools/run_quality_checks.sh`).
- [x] Smoke-Test-Skript vorhanden (`tools/smoke_test.py`).
- [x] Fehlerdialog mit Next-Step-Aktionen (erneut, reparatur, protokoll).
- [x] Headless-Start wird abgefangen, kein harter Crash.
- [x] Basis-Theme-Unterstützung inkl. High-Contrast dokumentiert.
- [x] Einfache Sprache in zentralen Nutzerhinweisen dokumentiert.
- [x] Logging- und Debug-Hinweise dokumentiert.
- [x] Undo-Ansatz als Sicherheitsprinzip dokumentiert.
- [x] Repo-Struktur (`app/core/tools/data`) dokumentiert.
- [x] Changelog-Prozess aktiv.
- [x] Todo-Prozess mit DONE/NEXT aktiv.
- [x] Entwicklerdoku enthält Prioritäten für Release-Stabilität.
- [x] Startbefehl und manuelle Fallback-Befehle sind dokumentiert.
- [x] Standardisierte A11y-Checkliste (Kontrast, Fokus) wird automatisch im Quality-Gate geprüft.

### ⏳ Offen (3)
- [ ] Automatische Codeformatierung fest in Quality-Gate integrieren.
- [ ] Kernmodule mit zusätzlichen automatischen Tests absichern.
- [ ] Input-/Output-Validierung als zentralen Standard technisch erzwingen.

## Nächster Schritt (eine Iteration)

1. Input-/Output-Validierung per gemeinsamem Helper in `core/` technisch erzwingen.
2. Danach Smoke- und Quality-Checks um diesen Validierungsstandard ergänzen.

### Vollständige Befehle

```bash
python -m compileall -q .
bash tools/run_quality_checks.sh
python tools/smoke_test.py
bash start.sh
```

## Laien-Hinweis

Wenn etwas nicht klappt: erst `bash start.sh` starten. Das Skript zeigt in einfacher Sprache, was fehlt und was der nächste Klick oder Befehl ist.
