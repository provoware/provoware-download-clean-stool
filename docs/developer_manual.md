# Entwicklerdokumentation (Release-orientiert)

Diese Dokumentation beschreibt die technische Zielarchitektur für ein robustes, laienfreundliches Tool mit maximaler Fehlertoleranz.

## 1) Architekturprinzipien

1. **GUI-first, kein CLI-Zwang für Nutzer**
   - Alle Kernfunktionen müssen per Buttons/Dropdowns nutzbar sein.
2. **Trennung von Zuständigkeiten (Separation of Concerns)**
   - `app/`: UI und Interaktion
   - `core/`: Geschäftslogik (Business-Logik)
   - `data/`: Presets + Konfiguration
   - `logs/`, `exports/`: Laufzeitartefakte (nicht als feste Logikdateien)
3. **Sicher statt schnell**
   - Niemals direkt löschen; nur verschieben + Undo ermöglichen.
4. **Beobachtbarkeit (Observability)**
   - Jeder kritische Schritt wird geloggt.

## 2) Start-Routine und Abhängigkeitsauflösung

Die Startlogik in `start.sh` soll als „Autopilot“ funktionieren:

1. Virtuelle Umgebung erzeugen.
2. Abhängigkeiten automatisch installieren.
3. Kritische Imports prüfen.
4. Qualitätsskripte starten.
5. Smoke-Test ausführen.
6. GUI starten.

### Anforderungen an die Robustheit

- Jeder Schritt hat:
  - **Prüfung** (Was wurde erwartet?)
  - **Ergebnis** (Was ist passiert?)
  - **Lösungspfad** (Was jetzt tun?)
- Keine stillen Fehler („silent failures“).
- Fehlertexte in einfacher deutscher Sprache.

## 3) Exit-Knoten-Design (kein harter Abbruch ohne Hilfe)

Für jeden Exit-Knoten gilt Pflicht:

1. **Kurze Problemzusammenfassung**
2. **Wahrscheinliche Ursache**
3. **Sofortmaßnahmen als nummerierte Schritte**
4. **Optionen im Dialog**:
   - Erneut versuchen
   - Reparatur starten
   - Log anzeigen

### Exit-Knoten-Matrix (Soll)

1. **Venv-Erstellung fehlgeschlagen** → Hinweis auf `python3-venv`, Wiederholoption.
2. **Paketinstallation unvollständig** → Netzwerk-/Paketquellen-Hinweise.
3. **Import kritischer Module fehlgeschlagen** → klarer Modulname, Installationspfad.
4. **Quality Gate schlägt fehl** → Start optional, aber mit klarer Warnung.
5. **Smoke-Test fehlgeschlagen** → GUI blockieren, Reparaturpfad anbieten.
6. **GUI-Startfehler** → Log-Öffnung + diagnostische Anleitung.

## 4) Validierungsstrategie (Input + Output)

Jede Kernfunktion erhält zwei Ebenen:

1. **Input-Validierung**
   - Typ, Format, Wertebereich, Existenzprüfung.
2. **Output-Validierung**
   - Ergebnisobjekt vollständig?
   - Dateioperation wirklich durchgeführt?
   - Undo reproduzierbar?

### Mindestanforderung pro Modul

- `settings`: Schema-Validierung, Fallback auf Defaults.
- `scanner`: Nur zugängliche Dateien, Fehler je Datei protokollieren.
- `planner`: Kein leerer/inkonsistenter Plan ohne Warnung.
- `executor`: Jede Move-Operation bestätigen, Fehler einzeln erfassen.
- `undo`: Vollständigkeitscheck + Teilfehler verständlich melden.

## 5) Deutsche Toolsprache (einfach + präzise)

Leitfaden für UI-Texte:

1. **Kurze Sätze (max. 15 Wörter)**
2. **Aktive Sprache** („Klicken Sie auf …“)
3. **Fachwort + Erklärung in Klammern**
   - Beispiel: „Duplikat (gleiche Datei mehrfach vorhanden)“
4. **Immer Handlungsoption nennen**
5. **Keine technischen Stacktraces im Hauptdialog**
   - Details nur im Debug-/Log-Bereich.

## 6) Logging- und Debug-Modus

1. Standardmodus: nutzerfreundliche Meldungen.
2. Debug-Modus: technische Details, Zeitstempel, Modulpfad, Ursache.
3. Log-Level konsistent nutzen:
   - `INFO`: normaler Ablauf
   - `WARN`: recoverable Problem
   - `ERROR`: kritischer Fehler
   - `DEBUG`: tiefe Diagnose

## 7) Qualitätssicherung (automatisiert)

Release-Pipeline (Sollzustand):

1. Compile-Check
2. Unit-Tests
3. Smoke-Test
4. Formatter-Check (`black --check`, `isort --check-only`)
5. Linter (`ruff check`)

Alle Checks sollen in einem Qualitätsbericht zusammenlaufen.

## 8) Barrierefreiheit und Theme-Standards

Pflichtkriterien:

1. Kontrast nach WCAG-orientierten Mindestwerten.
2. Tastaturbedienbarkeit für Hauptaktionen.
3. Fokusrahmen sichtbar.
4. Theme-Namen technisch und im UI identisch.
5. Senior-Modus mit größeren Schriften und Abständen.

## 9) Iterationsmodell mit Fortschritt

1. **Iteration 1 (35%)**: Grundfunktionen + Startlogik stabil.
2. **Iteration 2 (55%)**: Fehlerdialoge/Recovery integriert.
3. **Iteration 3 (70%)**: Dokumentation + Release-Kriterien geschärft.
4. **Nächste Iteration (Ziel 85%)**:
   - Automatisierte Tests vervollständigen
   - Quality Gate erweitern
   - UI-Sprachprüfung systematisieren
   - Validierungs-Checkliste pro Modul technisch erzwingen

## 10) Konkrete nächste Schritte (priorisiert)

1. Testabdeckung Kernmodule aufbauen.
2. Formatter/Linter in Qualitätsskript integrieren.
3. Validierungs-Helper zentralisieren (`core/validation.py`, optional).
4. Fehlermeldungen per Styleguide vereinheitlichen.
5. Release-Checkliste vor Freeze einmal komplett durchlaufen.

## 11) Release-Finalisierung (Iterationstracking, Stand 2026-02-12)

Verbindlicher Verweis: `RELEASE_CHECKLIST.md` ist die zentrale Statusdatei für den Release-Zustand.

Aktueller Stand (Iteration):
- **Fortschritt:** 92%
- **Abgeschlossen:** 31 Punkte
- **Offen:** 2 Punkte

Nächste Release-Iteration (technisch sinnvoll):
1. Dashboard-Verlaufsstatistik (Dateien/MB je Lauf) als zentrale Nutzertransparenz ergänzen.
2. Hilfebereich „Implementiert vs. Geplant“ als feste Ansicht in der GUI ergänzen.

Einfache Begründung: Der Kern ist technisch stabil; jetzt erhöhen diese zwei UX-Punkte die Release-Reife sichtbar für Laien und Support.


## 12) Konkrete Start- und Prüfkommandos (vollständig, kopierbar)

```bash
python -m compileall -q .
bash tools/run_quality_checks.sh
python tools/smoke_test.py
bash start.sh
```

Laienhinweis: Wenn ein Schritt fehlschlägt, zuerst die angezeigte Hilfe im Dialog lesen und genau den ersten vorgeschlagenen Schritt ausführen.
