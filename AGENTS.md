# AGENTS.md
# AGENTS.md – Minimal-Patch-Iteration (Fehlerfreiheit zuerst)
Version: 1.1
Ziel: In jeder Iteration nur den notwendigsten Code anfassen, sauber validieren, dokumentieren, nächsten Schritt planen.
Leitmotiv: Kleine Schritte, harte Gates, kein Scope-Drift.

────────────────────────────────────────────────────────────

## 0) Grundregel (Mikro-Iteration)
Jede Iteration darf maximal:
- 1 Problemklasse lösen (z.B. Theme-Mapping ODER Deutsch-Strings ODER Repair-Center-Exit)
- maximal 1–3 Dateien anfassen
- maximal 1 zusammenhängenden Codebereich pro Datei patchen (ein “Patch-Block”)

Wenn mehr nötig wäre: STOP → neue Iteration planen.

────────────────────────────────────────────────────────────

## 1) Scope-Kontrolle (Nur nötigster Code)
### 1.1 Change-Scope ist bindend
Vor dem Patch muss feststehen:
- Problem (1 Satz)
- Ziel (1 Satz)
- Exakte Dateien (Liste)
- Exakter Patch-Block je Datei (Funktion/Abschnitt)

### 1.2 Verboten in Iterationen
- “Nebenbei” Refactor/Formatierung außerhalb des Patch-Blocks
- Umbenennen/Umstrukturieren ohne zwingenden Grund
- Neue Features, wenn Bugfix/Robustheit das Ziel ist
- “Auf Verdacht” mehrere Stellen ändern

────────────────────────────────────────────────────────────

## 2) Patch-Methodik (Kleinstmöglicher Fix)
### 2.1 Minimaler Patch
- Nur das ändern, was direkt den Fehler behebt oder die Robustheit konkret erhöht.
- Keine kosmetischen Änderungen, außer sie sind Teil der Fehlerursache.
- Keine neuen Abhängigkeiten ohne separate Iteration.

### 2.2 Patch-Block-Disziplin
Pro Datei:
- ändere genau einen klar abgegrenzten Block (z.B. eine Funktion, ein Mapping, ein Dialogtext-Set).
- Wenn du einen zweiten Block anfassen musst: STOP → neue Iteration.

────────────────────────────────────────────────────────────

## 3) Hard Stops (Abbruchregeln)
Iteration wird abgebrochen und als nächste Iteration geplant, wenn:
- zusätzliche Dateien nötig werden, die nicht im Plan stehen
- die Ursache unklar ist (erst Analyse-Iteration planen)
- ein Gate nach 1 Korrekturversuch weiter fehlschlägt
- Datenverlust-Risiko entsteht (Undo/Papierkorb fehlt)

────────────────────────────────────────────────────────────

## 4) Validierung (Gates, immer gleich, immer kurz)
Reihenfolge ist fix. Erwartung: Exitcode 0.

GATE 1 – Syntax:
- python -m compileall -q .

GATE 2 – Repo-Quality:
- bash tools/run_quality_checks.sh

GATE 3 – Smoke (wenn vorhanden):
- python tools/smoke_test.py

GATE 4 – End-to-End Start:
- bash start.sh

GATE 5 – Mini-UX-Check (manuell, 2 Minuten):
- Sprache Deutsch in Dialogen des betroffenen Bereichs
- Fehlerdialog bietet Next-Step-Buttons (“Erneut versuchen”, “Reparatur”, “Protokoll”)
- betroffene Funktion läuft ohne Crash

Wenn ein Gate rot:
- 1 gezielter Fix innerhalb derselben Iteration
- Gates erneut
Wenn erneut rot:
- STOP → “NEXT ITERATION” planen (kein weiteres Herumprobieren)

────────────────────────────────────────────────────────────

## 5) Dokumentation (nur wenn Gates grün oder sauber verschoben)
### 5.1 CHANGELOG.md (Mini)
- 3 Zeilen: Was, Warum, Wirkung

### 5.2 todo.txt (Mini)
- 1 Zeile “DONE: … (Datum)”
- 1 Zeile “NEXT: … (Datum)”

### 5.3 Patch-Notiz (Optional, aber empfohlen)
- In der Iterationsausgabe: “Geänderte Dateien: …” + “Patch-Block: …”

────────────────────────────────────────────────────────────

## 6) Definition of Done (Iteration zählt nur, wenn)
- Change-Scope eingehalten (Dateien + Patch-Blocks)
- Gates: grün ODER sauber als NEXT ITERATION dokumentiert
- Changelog + todo aktualisiert
- Kein Scope-Drift
- Mindestens 1 Hilfeelement (z. B. Hilfetext, Next-Step-Hinweis, Reparaturhilfe) im betroffenen Bereich optimiert ODER erweitert
- Mindestens 1 Aspekt der Barrierefreiheit verbessert ODER erweitert (z. B. Kontrast, Fokusführung, verständliche Sprache)

────────────────────────────────────────────────────────────

## 7) Iterations-Template (zwingend)
### A) Fundstelle (nur beobachten)
- Problem:
- Risiko:
- Erwartung:

### B) Change-Scope (vor Patch)
- Ziel:
- Dateien:
- Patch-Block je Datei:

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
- Nächster Schritt: 2empfehlungen und einen detaillierten vorschlag mit einfacher sprache begründet

────────────────────────────────────────────────────────────

## 8) Release-Finalisierung (zusätzliche Pflicht in Doku-Iterationen)
Wenn die Iteration Release-Status betrifft, dann immer zusätzlich:
- `RELEASE_CHECKLIST.md` aktualisieren (Fortschritt %, offen/geschlossen, nächster Schritt).
- README-Release-Status synchron halten (gleiche Zahlen).
- Entwicklerdoku (`docs/developer_manual.md`) um den nächsten technischen Release-Schritt ergänzen.

Minimalformat je Iteration:
- Fortschritt: `X%`
- Abgeschlossen: `N`
- Offen: `M`
- Nächster Schritt: 1 klarer Arbeitsschritt mit Begründung in einfacher Sprache.

