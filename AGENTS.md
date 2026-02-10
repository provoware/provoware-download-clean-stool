# AGENTS.md
# AGENTS.md – Single-Task-Completion Iteration (Merge-Ready by Default)
Version: 2.0
Ziel: Jede Iteration schließt **genau die kleinste sinnvolle Aufgabe vollständig** ab, ist merge-ready und erhöht den Release-Reifegrad.
Leitmotiv: Kleinstes vollständiges Inkrement, harte Qualitäts-Gates, sofort integrierbar.

────────────────────────────────────────────────────────────

## 0) Grundregel (Atomare Iteration)
Jede Iteration muss:
- genau **1 klar abgegrenzte Aufgabe** vollständig abschließen (nicht nur „anarbeiten“)
- so klein wie möglich sein (smallest shippable change)
- merge-ready sein (Code + Doku + Checks erledigt)
- den Release-Fortschritt messbar erhöhen

Maximal:
- 1 Problemklasse
- 1–3 Dateien
- 1 zusammenhängender Patch-Block pro Datei

Wenn mehr nötig ist: STOP → neue Iteration planen.

────────────────────────────────────────────────────────────

## 1) Scope-Kontrolle (bindend vor jedem Patch)
Vor dem Patch festhalten:
- Problem (1 Satz)
- Ziel (1 Satz)
- Exakte Dateien (Liste)
- Exakter Patch-Block je Datei
- Abnahmekriterium „fertig“ (1 Satz, testbar)

Verboten:
- Nebenbei-Refactorings außerhalb des Patch-Blocks
- Umbenennen/Umstrukturieren ohne zwingenden Grund
- Mehrere Aufgaben in einer Iteration
- Teilergebnisse ohne klare Fertigstellung

────────────────────────────────────────────────────────────

## 2) Patch-Methodik (vollständig, klein, robust)
- Nur notwendige Änderungen für die konkrete Aufgabe.
- Keine neuen Abhängigkeiten ohne zwingenden Bedarf.
- Jede betroffene Funktion validiert Eingaben (input) und bestätigt Ergebnis (output).
- Fehlerpfade enthalten klare Next Steps in einfacher Sprache.
- Mindestens ein Hilfeelement pro betroffener Stelle verbessern/ergänzen.

────────────────────────────────────────────────────────────

## 3) Architektur- und Qualitätsstandards (verpflichtend)
- Einheitliche Standards und Best Practices in jedem Patch.
- Barrierefreiheit (Accessibility) immer mitdenken: verständliche Sprache, klare Kontraste, fokusfreundliches Verhalten.
- Farb-/Kontrastverhalten robust halten; mehrere Themes als unterstütztes Zielbild nicht brechen.
- Tool-Logik sauber trennen, Struktur wartbar halten.
- System-Dateien getrennt von variablen Dateien und Konfiguration organisieren.
- Debug- und Logging-Modus mit detaillierten, laienverständlichen Hinweisen pflegen.

────────────────────────────────────────────────────────────

## 4) Vollautomatische Prüfung & Start-Routine
Pflichtziel: Start-Routine prüft automatisch Voraussetzungen und löst Abhängigkeiten soweit möglich automatisiert auf.

Anforderungen:
- Bei Start klare Nutzer-Rückmeldung: was geprüft wurde, was fehlt, wie es gelöst wurde.
- Automatische sinnvolle Tests für Codequalität.
- Automatisches Code-Formatting als standardisierter Schritt.
- Fehlerausgaben enthalten einfache Lösungsvorschläge.

────────────────────────────────────────────────────────────

## 5) Gates (Reihenfolge fix, Exitcode 0 erwartet)
GATE 1 – Syntax:
- `python -m compileall -q .`

GATE 2 – Repo-Quality:
- `bash tools/run_quality_checks.sh`

GATE 3 – Smoke (wenn vorhanden):
- `python tools/smoke_test.py`

GATE 4 – End-to-End Start:
- `bash start.sh`

GATE 5 – Mini-UX-Check (2 Minuten):
- deutsche, verständliche Dialoge im betroffenen Bereich
- Fehlerdialog mit Next Steps (z. B. „Erneut versuchen“, „Reparatur“, „Protokoll“)
- betroffene Funktion läuft ohne Crash
- Barrierefreiheit/Kontrast im betroffenen Bereich geprüft

Wenn ein Gate rot:
- 1 gezielter Fix in derselben Iteration
- Gates erneut
Wenn erneut rot:
- STOP → NEXT ITERATION planen

────────────────────────────────────────────────────────────

## 6) Dokumentation (pro Iteration Pflicht)
### 6.0 README-Status
Ganz oben in README immer aktualisieren:
- exakte Prozentzahl Fortschritt (z. B. `81%`)
- Liste **Abgeschlossen**
- Liste **Offen**

### 6.1 CHANGELOG.md (Mini)
- 3 Zeilen: Was, Warum, Wirkung

### 6.2 todo.txt (Pflicht)
- `DONE: … (Datum)`
- `NEXT: … (Datum)`

### 6.3 Ergebnis-Hinweise
- Immer 2 kurze Laienvorschläge (leicht verständlich)
- Immer 1 detaillierter nächster Schritt in einfacher Sprache

────────────────────────────────────────────────────────────

## 7) Definition of Done (nur dann DONE)
Eine Iteration ist nur DONE, wenn:
- kleinste Aufgabe vollständig abgeschlossen
- merge-ready (kein offener Pflichtpunkt)
- Change-Scope eingehalten
- Gates grün ODER sauber als NEXT ITERATION dokumentiert
- README + CHANGELOG + todo aktualisiert
- mindestens 1 Hilfeelement verbessert/ergänzt
- mindestens 1 Accessibility-Aspekt verbessert/geprüft
- Release-Reifegrad erhöht und klar dokumentiert

────────────────────────────────────────────────────────────

## 8) Merge- und Release-Flow (Standard)
Nach jeder DONE-Iteration:
- zeitnah mergen (kein unnötiges Warten)
- direkt nächste kleinste vollständige Aufgabe planen
- immer auf vollständig release-fertig hinarbeiten

Release-Doku bei Release-bezogenen Iterationen zusätzlich:
- `RELEASE_CHECKLIST.md` aktualisieren (Fortschritt %, Abgeschlossen, Offen, nächster Schritt)
- README-Release-Status synchron halten
- `docs/developer_manual.md` um nächsten technischen Release-Schritt ergänzen

Minimalformat:
- Fortschritt: `X%`
- Abgeschlossen: `N`
- Offen: `M`
- Nächster Schritt: 1 klarer Arbeitsschritt mit einfacher Begründung

────────────────────────────────────────────────────────────

## 9) Iterations-Template (zwingend)
### A) Fundstelle (beobachten)
- Problem:
- Risiko:
- Erwartung:

### B) Change-Scope (vor Patch)
- Ziel:
- Dateien:
- Patch-Block je Datei:
- Abnahmekriterium:

### C) Patch (kurz)
- Änderung 1:
- Änderung 2: (optional)

### D) Gates
- G1:
- G2:
- G3:
- G4:
- G5:

### E) Ergebnis
- Status: DONE / NEXT ITERATION
- Doku: README + CHANGELOG + todo aktualisiert
- Laienvorschläge: 2 kurze Empfehlungen
- Nächster Schritt: 1 detaillierter Vorschlag in einfacher Sprache
