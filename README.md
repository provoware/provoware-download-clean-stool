# Downloads Organizer (Laienfreundlich, barrierearm, robust)

- **Fertig:** Startlogik mit Selbstprüfung aktiv, Wizard mit Buttons verfügbar, Theme-Mapping stabil dokumentiert.
- **Offen:** Vollständige Input-/Output-Validierung, ausgebautes Quality-Gate mit Formatter/Linter, vollständiges deutsches Textaudit.
- **Status/Nächste Schritte:** Fortschritt ca. 70%, als Nächstes Unit-Tests für Kernmodule, danach Formatter+Linting in der Prüfpipeline, dann Kontrast-/Hilfetext-Audit für Barrierefreiheit.

Dieses Tool hilft dabei, den Ordner `Downloads` sicher aufzuräumen, **ohne Kommandozeile im normalen Betrieb**. Die Bedienung erfolgt über **Buttons, Dropdowns und Auswahlfelder**. Ziel ist ein stabiler, fehlertoleranter Assistent mit klaren Rückmeldungen in einfacher Sprache.

## 1) Zielbild für den Release (professionelle Gesamtanalyse)

Die folgende Liste beschreibt, was bis zu einem „perfekten Laien-Release“ umgesetzt und abgesichert sein muss.

1. **Null-Abbruch-UX (Benutzererlebnis)**
   - Jeder Fehlerdialog bietet immer eine Lösungskette:
     1) **Erneut versuchen**
     2) **Automatische Reparatur starten**
     3) **Protokoll anzeigen (Logdatei)**
   - Es darf keinen toten Exit-Knoten geben („Programm schließt einfach“ ohne Erklärung).

2. **Vollautomatische Startroutine mit Selbstheilung (Self-Repair)**
   - Automatisches Erstellen der virtuellen Umgebung.
   - Automatische Installation/Aktualisierung von Abhängigkeiten.
   - Prüfung kritischer Module vor GUI-Start.
   - Falls ein Schritt fehlschlägt: verständliche Ursache + konkrete nächste Aktion.

3. **Durchgängige Validierung (Eingabe + Ergebnis)**
   - Jede Funktion prüft Eingaben (Input-Validierung) und bestätigt Ergebnisse (Output-Validierung).
   - Beispiele:
     - Pfad existiert?
     - JSON-Konfiguration korrekt?
     - Verschobene Dateien tatsächlich am Ziel?
     - Undo vollständig?

4. **Robustheit und Absturzsicherheit nach Standards**
   - Defensive Programmierung (Fehler früh erkennen).
   - Deterministische Zustände (ein Schritt = klarer Zustand).
   - Sichere Dateibehandlung (atomare Schritte, wenn möglich).
   - Log-Level-Standard: `DEBUG`, `INFO`, `WARN`, `ERROR`.

5. **Barrierefreiheit als Release-Kriterium**
   - Hoher Kontrast, klare Fokus-Reihenfolge, große Klickflächen.
   - Themes: Hell, Dunkel, High-Contrast, Extra-Groß.
   - Einheitliche, einfache Sprache in allen Dialogen.

6. **Automatisierte Qualitätssicherung (Quality Gate)**
   - Auto-Checks vor Programmstart:
     - Syntax/Compile-Checks
     - Smoke-Test (Startfähigkeit)
     - Linting/Formatierung
     - Unit-Tests
   - Ergebnisbericht für Nutzer und Entwickler.

7. **Wartbare Architektur (Trennung von Verantwortlichkeiten)**
   - GUI (`app/`) getrennt von Kernlogik (`core/`).
   - Variable Daten (`data/`), Laufzeitdaten (`logs/`, `exports/`) und Konfiguration klar getrennt.

8. **Laienverständliche Toolsprache (Deutsch als Standard im Tool)**
   - Fachbegriffe nur mit kurzer Erklärung in Klammern.
   - Keine Schuldzuweisungen („Fehler von Ihnen“), stattdessen lösungsorientierte Texte.

## 2) Global anerkannte/gängige Vorgaben für Stabilität

Diese Standards sollten als verbindliche Leitplanken im Projekt gelten:

1. **Fail-safe Defaults (sichere Standardwerte)**: Bei Unsicherheit nichts zerstören, nur verschieben.
2. **Graceful Degradation**: Bei Teilfehlern sinnvolle Alternative statt Komplettabbruch.
3. **Single Source of Truth**: Einstellungen zentral, konsistent und versioniert.
4. **Observable System**: Jeder wichtige Schritt ist im Log nachvollziehbar.
5. **Idempotente Hilfsaktionen**: Reparaturaktionen mehrfach ausführbar ohne Seiteneffekte.
6. **Reproduzierbarkeit**: Start- und Testabläufe mit denselben Befehlen wiederholbar.
7. **Explizite Exit-Strategie**: Jeder Exit-Knoten hat Handlungsempfehlungen.

## 3) Ist-Stand und Lückenanalyse (kurz)

Bereits vorhanden:
- Automatische Startlogik mit venv, Paketinstallation, Modulprüfung, Qualitätsprüfung und Smoke-Test.
- Linux-GUI-Bibliotheken `libGL.so.1`, `libEGL.so.1` und `libxkbcommon.so.0` werden vor dem Smoke-Test automatisch geprüft und bei Bedarf geführt repariert.
- GUI-Fehlerdialoge mit Reparatur-/Info-Fokus.
- Wizard-basierter, button-gesteuerter Ablauf.

Noch vor Release zu schließen:
- Vollständige Input-/Output-Validierung in allen Kernpfaden.
- Einheitliche Theme-Benennung und dokumentierte Kontrastprüfung.
- Erweiterte automatisierte Tests + Formatter/Linting im Quality Gate.
- Durchgängige, einheitliche deutsche Klartext-Meldungen.

## 4) Entwicklungsfortschritt je Iteration (mit Prozent)

1. **Iteration 1 – Grundlagen stabilisiert: 35%**
   - Startskript, Basistests, erste Fehlerdialoge vorhanden.
2. **Iteration 2 – UX & Fehlertoleranz ausgebaut: 55%**
   - Wizard-Struktur und Undo-Flow verbessert.
3. **Iteration 3 – Release-Readiness-Dokumentation: 70%**
   - README, Entwicklerdoku und TODO auf Release-Kriterien ausgerichtet.

**Nächster logischer Schritt (optimal):**
- Iteration 4 auf **85%** bringen durch:
  1) Unit-Tests für `scanner/planner/executor/settings`,
  2) Formatter/Linter in `tools/run_quality_checks.sh`,
  3) Vollständige Validierungs-Matrix pro Funktion,
  4) UI-Textaudit in einfacher deutscher Sprache.

## 5) Bedienung für Laien (ohne Terminal im Normalfall)

1. `start.sh` per Doppelklick oder Dateimanager starten.
2. Ordner auswählen.
3. Profil (Senior/Standard/Power) auswählen.
4. Vorschau prüfen.
5. Auf **Ausführen** klicken.
6. Bei Problemen: **Erneut versuchen** oder **Reparatur**.

## 6) Vollständige Befehle (für Support/Entwickler)

```bash
chmod +x start.sh
./start.sh
```

Optional manuell:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
bash tools/run_quality_checks.sh
python tools/smoke_test.py
python -m app.main
```

## 7) Weiterführende Laienvorschläge

1. Ergebnisbericht nach jedem Lauf automatisch anzeigen.
2. „Was bedeutet das?“ Hilfetexte neben kritischen Optionen einblenden.
3. Ampel-Status im UI:
   - Grün = alles ok
   - Gelb = Hinweis
   - Rot = Aktion erforderlich
4. Assistent für Erstnutzer beim ersten Start (2-Minuten-Einführung).

## 8) Projektstruktur

- `app/` – Oberfläche (GUI)
- `core/` – Kernlogik (Scan, Plan, Ausführung, Undo, Logging, Selfcheck)
- `data/` – Konfiguration und Presets
- `tools/` – Qualitätsprüfungen, Reparatur- und Fehlerdialoge
- `docs/` – Entwicklerdokumentation
- `todo.txt` – Release-Aufgaben, priorisiert
