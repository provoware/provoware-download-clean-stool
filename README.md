# Downloads Organizer – Informationsstand (barrierearm, einheitlich, laienfreundlich)

Dieses Projekt sortiert den Ordner **Downloads** sicher und nachvollziehbar.
Der Fokus liegt auf:
- **Barrierefreiheit** (gute Lesbarkeit, klare Sprache, klare Bedienung)
- **stabiler Startroutine** (automatische Prüfungen und Reparaturversuche)
- **einheitlichen Qualitätsstandards** (Syntax, Tests, Qualitätschecks)


## 0) Release-Status (jede Iteration aktualisieren)

Die aktuelle Release-Checkliste liegt in **`RELEASE_CHECKLIST.md`**.

- **Entwicklungsfortschritt:** **94%**
- **Abgeschlossene Punkte:** **20**
- **Offene Punkte:** **1**
- **Nächster Schritt:** Zentrale Input-/Output-Validierung als letzten Kernschritt in `core/executor.py` technisch erzwingen, damit auch Ausführung und Undo denselben Standard nutzen.

**Abgeschlossen:**
- Neuer zentraler Validierungs-Helper in `core/validation.py`; `planner.build_plan` prüft jetzt Input- und Output-Standards mit klaren Next-Step-Fehlertexten.
- `core/scanner.py` nutzt jetzt zentrale Input-/Output-Validierung (Pfad, Filterliste, Schwellenwerte, Duplikatmodus) mit klaren Next-Step-Fehlertexten in einfacher Sprache.
- Quality-Gate enthält jetzt einen automatischen A11y-Theme-Check (Kontrast + sichtbarer Fokus) mit verständlichen Next-Step-Hinweisen.
- Quality-Gate führt bei Format-/Lint-Warnungen jetzt automatisch Reparaturläufe aus und prüft danach erneut.
- Smoke-Test enthält jetzt einen zusätzlichen automatischen Planner-Check (Duplikat-Grund, relativer Zielpfad, Summary-Werte).
- Smoke-Test enthält jetzt einen zusätzlichen automatischen Scanner-Check (Parser, Typfilter, Safe-Duplikaterkennung, ungültiger Modus).
- Smoke-Test erfüllt Ruff-E402 jetzt ohne Sonderregel (`# ruff: noqa: E402`) durch saubere, verzögerte Importe.
- Startroutine mit Auto-Prüfung, Auto-Reparatur und klaren Endstatusmeldungen.
- Qualitäts- und Smoke-Gates sind vorhanden und ausführbar.
- Fehlerführung mit klaren Next Steps (erneut versuchen, reparieren, protokoll).
- Basis-Barrierefreiheit dokumentiert (Themes inkl. High-Contrast, einfache Sprache).

**Offen (für „perfekte“ Release-Version):**
- Input-/Output-Validierung im `executor` ergänzen und mit einem Undo-Fehlerszenario absichern.

Kurz erklärt: Der Scanner ist jetzt validiert; als letzter Kernschritt folgt der Executor für durchgängige Input-/Output-Sicherheit.

## 1) Was jetzt als Standard gilt

1. **Einfache Sprache**
   - Kurze Sätze, klare Handlungsschritte.
   - Fachbegriff immer mit Erklärung in Klammern, z. B. *Logging (Protokollierung)*.

2. **Barrierefreiheit**
   - Hoher Kontrast für Texte und Buttons.
   - Mehrere Themes (Hell, Dunkel, High Contrast).
   - Verständliche Fehlertexte mit klaren nächsten Schritten.

3. **Fehlerführung mit Next Steps**
   - Fehlerdialoge bieten immer:
     1) **Erneut versuchen**
     2) **Reparatur starten**
     3) **Protokoll anzeigen**

4. **Validierung**
   - Jede Funktion soll Eingaben prüfen (*Input-Validierung*).
   - Jede Funktion soll Ergebnis prüfen (*Output-Validierung*).

5. **Debug und Logging**
   - Einheitliche Log-Stufen: `DEBUG`, `INFO`, `WARN`, `ERROR`.
   - Meldungen mit Lösungsvorschlägen in einfacher Sprache.

## 2) Vollautomatische Startroutine (Autocheck + Autorepair)

`start.sh` soll die nötigen Schritte automatisch ausführen:
- virtuelle Umgebung vorbereiten
- Abhängigkeiten prüfen/installieren
- Qualitätsprüfungen starten
- Smoke-Test starten
- danach die App starten
- bei Auto-Reparatur immer klaren Endstatus zeigen: **erfolgreich**, **nicht möglich** oder **nicht nötig**

Wenn etwas fehlt, soll der Nutzer direkt eine verständliche Rückmeldung und einen Reparaturweg bekommen.

## 3) Einheitliche Struktur für Wartbarkeit

- `app/` → Oberfläche (GUI)
- `core/` → Kernlogik
- `tools/` → Prüf- und Hilfsskripte
- `data/` → variable Daten und Konfigurationen

Zielbild:
- Systemnahe Dateien und variable Daten logisch trennen.
- Konfigurationen zentral und nachvollziehbar halten.

## 4) Vollständige Befehle (kopierbar)

```bash
chmod +x start.sh
./start.sh
```

Manuell (Support/Entwicklung):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m compileall -q .
bash tools/run_quality_checks.sh
python tools/smoke_test.py
bash start.sh
```

## 5) Automatische Qualität und Formatierung

Für den nächsten stabilen Release gelten diese Pflichtpunkte:
- automatisierte Tests für Kernmodule
- automatischer Format-Check und Linting (Code-Regelprüfung)
- einheitlicher Qualitätslauf über `tools/run_quality_checks.sh`

## 6) Laien-Vorschläge (nächste sinnvolle Verbesserungen)

1. Nach jedem Lauf einen Kurzbericht zeigen:
   - „X Dateien verschoben, Y MB frei, Undo möglich“.  
2. In jedem Fehlerfenster eine Mini-Hilfe zeigen:
   - „Was ist passiert?“
   - „Was kann ich jetzt klicken?“
3. In den Theme-Einstellungen kurze Vorschau ergänzen:
   - „Empfohlen bei Sehschwäche: High Contrast“.

## 7) Sinnvolle „Actions“ für bessere Entwicklung (mit vollständigen Befehlen)

Diese Reihenfolge ist praxistauglich und hilft bei Qualität, Barrierefreiheit und Wartbarkeit:

1. **Autocheck direkt beim Start**
   - Zweck: Fehler früh erkennen.
   - Befehl:

```bash
./start.sh
```

2. **Syntax + Qualitätslauf vor jedem Commit**
   - Zweck: konsistente Standards und weniger Fehler im Team.
   - Befehle:

```bash
python -m compileall -q .
bash tools/run_quality_checks.sh
python tools/smoke_test.py
```

3. **Automatisches Formatieren (Code-Formatierung)**
   - Zweck: überall gleiche Codeform ohne Diskussion.
   - Befehle:

```bash
python -m pip install black isort
black .
isort .
```

4. **Debug-Modus (Fehlersuche) mit klaren Logs**
   - Zweck: Probleme schnell verstehen und lösen.
   - Befehle:

```bash
export LOG_LEVEL=DEBUG
./start.sh
```

5. **Barrierefreiheits-Quickcheck (A11y = Zugänglichkeit)**
   - Zweck: gute Lesbarkeit und sichere Bedienung für alle.
   - Prüfen:
     - Theme „High Contrast“ auswählbar.
     - Fokus sichtbar (man sieht, welches Feld aktiv ist).
     - Fehlertexte in einfacher Sprache mit klaren Buttons.

6. **Todo immer aktuell halten**
   - Zweck: klare Prioritäten und keine offenen „unsichtbaren“ Baustellen.
   - Regel:
     - Eine Zeile `DONE: ... (Datum)`
     - Eine Zeile `NEXT: ... (Datum)`


7. **Abbruchfreien Start gezielt prüfen (robuster Linux-Lib-Check)**
   - Zweck: Sicherstellen, dass frisch installierte Systembibliotheken direkt erkannt werden.
   - Befehle:

```bash
bash start.sh
ldconfig -p | rg "libGL.so.1|libEGL.so.1|libxkbcommon.so.0"
```

---

Stand dieser Informationsdatei: 2026-02-10
