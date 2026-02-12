# Provoware Clean Tool 2026 – Informationsstand (barrierearm, einheitlich, laienfreundlich)

Dieses Projekt sortiert den Ordner **Downloads** sicher und nachvollziehbar.
Der Fokus liegt auf:
- **Barrierefreiheit** (gute Lesbarkeit, klare Sprache, klare Bedienung)
- **stabiler Startroutine** (automatische Prüfungen und Reparaturversuche)
- **einheitlichen Qualitätsstandards** (Syntax, Tests, Qualitätschecks)


## 0) Release-Status (jede Iteration aktualisieren)

Die aktuelle Release-Checkliste liegt in **`RELEASE_CHECKLIST.md`**.

 - **Entwicklungsfortschritt:** **93%**
 - **Abgeschlossene Punkte:** **86**
 - **Offene Punkte:** **2**
 - **Nächster Schritt:** Start-Routine weiter in Richtung Themen-Check + Web-Startpfad ausbauen und danach den finalen Release-Check schließen.

### Schnellüberblick (laienfreundlich)

- **Was wurde analysiert?** Alle aktuell offenen Punkte wurden in drei kleine, direkt umsetzbare Pakete zerlegt.
- **Was ist jetzt klarer?** Es gibt eine feste Reihenfolge mit messbaren Kriterien und kopierbaren Befehlen.
- **Was mache ich bei Warnungen?** `cat exports/setup_log.txt` öffnen, `bash tools/run_quality_checks.sh` ausführen, danach `bash start.sh` erneut starten.

## 0.2) Nächste logische Schritte (in einfacher Sprache)

1. **Hilfezeile in Analyse + Plan fest ergänzen (A11y = Barrierefreiheit)**  
   Ziel: In beiden Schritten eine kurze feste Hilfe zeigen: Tastaturweg, Kontrast-Hinweis, klare nächste Aktion.

2. **Start-Autoreparatur robuster machen (Autorepair = automatische Reparatur)**  
   Ziel: Fehlende Module automatisch erkennen, reparieren und den Ausgang klar als „erfolgreich“ oder „nicht möglich“ melden.

3. **Qualitätslauf vollautomatisch machen (Quality-Gate = Qualitäts-Schranke)**  
   Ziel: `tools/run_quality_checks.sh` führt Formatierung + Lint automatisch aus und zeigt bei Fehlern einfache Next Steps.

### Vollständige Befehle (kopierbar)

```bash
python -m compileall -q .
bash tools/run_quality_checks.sh
python tools/smoke_test.py
bash start.sh
```

### Abnahme (wann ist es fertig?)

- Alle drei Punkte sind abgeschlossen und als DONE dokumentiert.
- Mindestens ein Hilfe- oder Accessibility-Punkt ist sichtbar verbessert.
- Alle vier Befehle laufen grün oder sind mit klarem Grund als NEXT ITERATION dokumentiert.


## 0.4) Aktuelle Iteration (3 abgeschlossene Text-Punkte)

1. **README-Status geschärft (klar, kurz, messbar)**  
   Fortschritt und nächste Schritte sind jetzt kompakt und laienfreundlich formuliert.
2. **Changelog-Eintrag im 3-Zeilen-Format ergänzt**  
   Was/Warum/Wirkung wurde als Mini-Protokoll ergänzt.
3. **todo.txt auf DONE/NEXT aktualisiert**  
   Abschluss und nächster kleiner Schritt sind mit Datum nachgeführt.

### Zwei kurze Laienvorschläge
- Öffne zuerst `README.md` und arbeite nur die vier Prüf-Befehle der Reihe nach ab.
- Wenn ein Schritt fehlschlägt, nutze zuerst den dort genannten „Next Step“, statt alles gleichzeitig zu ändern.

### Detaillierter nächster Schritt (einfach erklärt)
Führe `bash start.sh` aus und prüfe danach in `exports/setup_log.txt`, ob fehlende Pakete automatisch erkannt und gelöst wurden. Wenn dort noch Warnungen stehen, behebe nur **einen** Warnpunkt und starte den Ablauf erneut.

## 0.3) Vollständige Analyse: nächste offene Punkte und Optimierungen

### Offen

1. **Accessibility-Hilfe im Hauptfluss erweitern**  
   Im Analyse- und Plan-Schritt fehlt noch eine kurze, feste Hilfezeile mit Tastaturweg, Kontrast-Hinweis und klarer nächster Aktion.

2. **Start-Routine mit sicherer Auto-Reparatur härten**  
   Die Startroutine soll bei fehlenden Modulen zuerst verständlich erklären, dann automatisch reparieren und den Erfolg sofort prüfen (Input-/Output-Validierung).

3. **Qualität + Formatierung vollständig automatisieren**  
   Quality-Check soll Formatierung und Lint (Regelprüfung) als Standard ausführen und bei Fehlern einfache Next Steps zeigen.

### Optimierungsreihenfolge (kleinster sinnvoller Weg)

1. **Paket A – Hilfe & Barrierefreiheit**  
   Kurztexte pro betroffenem Schritt ergänzen (maximal 2 Sätze), Fokus-Reihenfolge prüfen, Kontrast-Hinweis sichtbar machen.

2. **Paket B – Start-Autorepair**  
   Modulprüfungen zentralisieren, fehlende Abhängigkeiten automatisch nachinstallieren, Reparaturergebnis eindeutig als „erfolgreich/nicht möglich“ melden.

3. **Paket C – Quality-Automation**  
   Format- und Qualitätscheck in `tools/run_quality_checks.sh` verpflichtend bündeln und bei Problemen laienfreundliche Lösungsvorschläge ausgeben.

### Vollständige Befehle für die nächste Umsetzungsiteration

```bash
python -m compileall -q .
bash tools/run_quality_checks.sh
python tools/smoke_test.py
bash start.sh
```

### Abnahmekriterien (Definition von „fertig“)

- Jede der drei Optimierungen ist als eigener, abgeschlossener Punkt dokumentiert.
- Mindestens eine Änderung verbessert Hilfe, Texte oder Barrierefreiheit direkt im betroffenen Bereich.
- Alle vier Prüf-Befehle laufen mit Exitcode 0 oder sind mit klarer Next-Iteration-Begründung dokumentiert.

**Abgeschlossen:**

- Entwicklerbereich zeigt jetzt eine klare Status-Legende (✅ abgeschlossen / 🟡 offen) mit barrierearmer Kurz-Erklärung in einfacher Sprache.
- Filter-Buttons im Entwicklerbereich haben jetzt größere Klickflächen und eigene Accessibility-Namen für bessere Tastatur- und Screenreader-Bedienung.

- Analyse-Trefferliste zeigt jetzt einen klaren Auswahlstatus (X von Y) mit nächster Aktion in einfacher Sprache; Aktionsbuttons reagieren barrierearm auf den Auswahlzustand.
- Neue Aktion „Auswahlpfade kopieren“ übernimmt markierte Trefferpfade direkt in die Zwischenablage; bei leerer Auswahl erscheint ein Fehlerdialog mit klaren Next Steps.
- Quality-Check enthält jetzt einen JSON-Struktur-Check für settings, Standards-Manifest und alle Presets mit klaren Next Steps bei fehlenden Pflichtfeldern.
- Abschlussmeldung im Quality-Check zeigt jetzt bei Warnungen einen klaren Warnstatus statt pauschal „OK“.
- Einstellungen unterstützen jetzt einen laienfreundlichen Schalter-Standard mit Einsteiger-Modus, Dateitypenauswahl, Zielordner-Modus, Zielpfad und aktivierbaren Hilfehinweisen.
- Kernmodul `core/settings.py` liefert jetzt eine kompakte Empfehlungs-Hilfe für Laien („welche Schalter sind sinnvoll?“) und validiert die neuen Einstellungswerte robust.

- Neues Fokus-Highlight markiert jetzt interaktive Elemente (Button, Auswahlfelder, Listen, Checkboxen) klar mit gut sichtbarem Rahmen für bessere Tastaturbedienung.
- Neue Schaltfläche „Grafik-Verbesserungen anzeigen“ öffnet eine kurze Checkliste mit 4 konkreten UI-Optimierungen in einfacher Sprache.
- Neue Theme-Schnellwahl (Alt+1 bis Alt+5) setzt jedes Farbschema direkt per Tastatur oder Klick und aktualisiert die Live-Vorschau sofort.
- Live-Vorschau zeigt jetzt zusätzlich einen Interaktivitäts-/Kontraststatus mit Kurzbewertung und konkretem nächsten Klick in einfacher Sprache.
- Theme-Vorschau hat jetzt den neuen Modus „Auto (Fensterbreite)“ für Bereichsskalierung und Position; das Layout passt sich bei Fenstergröße dynamisch und barrierearm automatisch an.
- Vorschau aktualisiert Auto-Modi jetzt auch bei Fenster-Resize mit robuster Input-/Output-Validierung und klarer Auto-Rückmeldung im Hinweistext.
- Theme-Stile enthalten jetzt globale A11y-Standards für deaktivierte Buttons, größere Checkbox-Indikatoren und klare Auswahl-Kontraste in Listen/Dropdowns.
- Komboboxen werden jetzt zentral mit Input-/Output-Validierung gesetzt; ungültige Preset-/Schnellmodus-Werte stoppen mit klaren Next Steps statt still zu scheitern.
- Analyse-Schritt enthält jetzt eine auswählbare Trefferliste (Mehrfachauswahl) inklusive Aktionstasten "Alle markieren" und "Auswahl löschen"; nur markierte Dateien gehen in den Plan.
- Optionen enthalten jetzt zwei klare Workflow-Beispiele in einfacher Sprache (Laptop frei machen / externe Platte prüfen) und bestätigen, dass Haupt-Aktionstasten in jedem Schritt vorhanden sind.
- Startansicht enthält jetzt eine linke Kategorie-Leiste als visuelle Hauptansicht-Vorschau (ohne Logikwechsel) mit klaren, barrierearmen Kategorien.
- Startansicht enthält jetzt zentrale Aktionskarten als visuelle Hauptansicht-Vorschau (ohne Logikwechsel) mit leicht verständlichen Kurztexten.
- Dashboard zeigt jetzt einen eigenen Persistenz-Status (✅/⚠️), der nach jedem Speichern klar meldet, ob Einstellungen beim Neustart verfügbar sind.
- Speichern wird jetzt aktiv verifiziert (Reload-Check): Ordner, Theme, Textgröße und Duplikatmodus werden direkt nach dem Schreiben geprüft und bei Problemen mit Next Steps erklärt.
- Neue Schnellbuttons „Lesbarkeit sofort maximieren“ (`Alt+K`) und „Ausgewogene Ansicht laden“ (`Alt+L`) setzen Theme, Textgröße, Vorschau-Skalierung und Position in einem Klick für barrierearme Starts.
- Live-Theme-Vorschau zeigt jetzt zusätzlich einen klaren A11y-Hinweis (Zugänglichkeit) je Farbschema inklusive Textgrößenstatus in einfacher Sprache.
- Dashboard-Schnellübersicht ist jetzt HTML-sicher (maskierte Sonderzeichen) und zeigt Berechtigungsstatus konsistent mit klaren Symbolen für OK/Warnung.
- Startseite hat jetzt ein robusteres, luftigeres Layout (einheitliche Abstände, Mindestbreiten, Hilfe-/Dashboard-Karten) plus Tastatur-Schnellwahl `Alt+O` für die Ordnerauswahl.
 - `AGENTS.md` verlangt jetzt pro Iteration genau drei vollständig abgeschlossene Punkte statt zwei, inklusive angepasster DoD- und Planungsregeln.
- Neue Schnellwahl „Aufräumziel“ steuert typische Reinigungen (ausgewogen, große Dateien, alte Dateien, Duplikate zuerst) mit farbiger Hilfe in einfacher Sprache.
- Linux-Berechtigungsprüfung ist jetzt im Dashboard, vor Analyse und vor Ausführung integriert; bei fehlenden Rechten erscheinen klare Next Steps inklusive Terminal-Befehl.
- Neue Vorschau-Steuerung „Bereichsskalierung“ erlaubt 100–150% Live-Skalierung für verschiedene Bildschirmgrößen mit robuster Input-/Output-Validierung.
- Neue Vorschau-Steuerung „Vorschau-Position“ erlaubt flexible Anordnung (links/rechts/untereinander) für bessere Orientierung und Kontrastprüfung.
- Neue Live-Theme-Vorschau im ersten Schritt zeigt Farben, Fokus und Listenbeispiel sofort; Theme und großer Text werden direkt mit klarer Vorschauhilfe angewendet.
- Startroutine prüft jetzt `sudo` vor System-Reparaturen und gibt bei fehlender Berechtigung klare Next Steps in einfacher Sprache statt still zu scheitern.
- Startroutine nutzt jetzt einen zentralen Modul-Check statt doppeltem Inline-Code; dadurch ist die Prüflogik wartbarer und leichter testbar.
- Entwicklerdoku enthält jetzt den finalen Release-Rahmen mit klaren technischen Schritten und laienverständlicher Begründung.
- Benutzereinstellungen bleiben jetzt zuverlässig zwischen Starts erhalten (Ordner + Anzeige), inklusive klarer Offline-Hinweise im Dashboard.
- Neues Theme **„blau“** ergänzt und Theme-Auswahl jetzt strikt validiert; bei ungültiger Auswahl erscheint ein klarer Fehlerdialog mit Next Steps.
- Ausführung und Undo im `core/executor.py` nutzen jetzt zentrale Input-/Output-Validierung inklusive robuster Undo-Datenprüfung mit klaren Next Steps.
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
- Fehlerfenster zeigen jetzt eine einheitliche Mini-Hilfe mit „Was ist passiert?“ und „Was kann ich jetzt klicken?“.
- Basis-Barrierefreiheit dokumentiert (Themes inkl. High-Contrast, einfache Sprache).

    - Werkzeugname überarbeitet: Aus „Downloads Organizer“ bzw. „Downloads Aufräumer“ wurde „Provoware Clean Tool 2026“ für eine klare, laienfreundliche Benennung.
    - Einheitliche Erstellung der Verlaufsschaltflächen: neue Hilfsmethode `_create_standard_button()` sorgt für konsistente Größe, Tooltip und Accessibility‑Namen – die Verlaufsexport- und Verlaufslösch-Knöpfe nutzen diese nun.

    - Analyse-Trefferliste sortierbar nach Name/Größe: Ein Dropdown erlaubt die Sortierung nach alphabetischer Reihenfolge oder nach Dateigröße; nach dem Scan werden die Treffer entsprechend neu aufgebaut. Die Plan-Liste hat jetzt ein Kontextmenü, mit dem sich der Zielordner eines geplanten Eintrags direkt im Dateimanager öffnen lässt.

    - Neue Hilfe-Schaltfläche auf der Startseite: Sie öffnet eine Kurzanleitung in einfacher Sprache, die die vier Hauptschritte erklärt (Ordner wählen, Scannen, Vorschau prüfen, Aufräumen starten) und auf die Aktionskarten hinweist. Die Schaltfläche ist barrierearm gestaltet und verfügt über klare Accessibility‑Namen.

    - Drei Schnellstart-Buttons („Fotos sortieren“, „Große Dateien prüfen“, „Duplikate finden“) stehen jetzt im Options-Schritt bereit. Sie laden jeweils ein voreingestelltes Preset, starten automatisch einen Scan und zeigen die Ergebnisse in einer Vorschau. Große Klickflächen, klare Beschriftungen und hilfreiche Tooltips machen diese Buttons auch für Laien leicht nutzbar.

    - Eine zentrale Textdatei (`data/ui_texts.json`) speichert die Kurzanleitung sowie Beschriftungen und Tooltips der Schnellstart-Buttons. Diese externe Datei ermöglicht zukünftige Anpassungen oder Übersetzungen der Texte ohne Codeänderungen.
    - Ein Verlauf im Entwicklerbereich zeigt jetzt, wie viele Dateien und Megabytes bei früheren Aufräuml\u00e4ufen verarbeitet wurden. Die Liste kann als CSV exportiert oder gel\u00f6scht werden; nach jedem Planlauf wird ein Eintrag hinzugef\u00fcgt. Hilfetexte erkl\u00e4ren die Bedienung.

    - Drei weitere Schnellstart-Buttons (\u201eDokumente sortieren\u201c, \u201eMusik sortieren\u201c, \u201eAlles sortieren\u201c) wurden erg\u00e4nzt. Sie nutzen eigene Presets (quick_docs, quick_music, quick_all) und starten den Scan sofort. Die Buttons sind gro\u00df, haben klare Beschriftungen und laienfreundliche Tooltips.

    - Ein neues API-Skelett (`app/web_api.py`) stellt zwei FastAPI-Endpunkte zur Verf\u00fcgung: `/status` liefert den aktuellen Systemstatus, `/dry_run` f\u00fchrt einen Platzhalter-Trockenlauf aus. Die Endpunkte liefern laienfreundliche JSON-Antworten und dienen als Grundlage f\u00fcr weitere Web-Funktionen.

    - Der Einsteiger- bzw. Button-Only-Modus (novice_mode) blendet jetzt komplexe Filter, Grenzen und Ziele im Optionen-Schritt aus und r\u00fcckt die Schnellstart-Buttons in den Mittelpunkt. Dadurch k\u00f6nnen Laien ohne Facheinstellungen direkt eine Aufr\u00e4umaktion starten.

    - Die Analyse-Trefferliste ist jetzt farblich kodiert: Bilder erscheinen hellblau, Videos helllila, Archive hellorange und andere Dateien hellgrau. Dies erleichtert die Orientierung und unterscheidet Dateitypen auf einen Blick.

    - Unter der Sortierauswahl im Analyse-Schritt befinden sich neue Schaltfl\u00e4chen ("Nur Bilder", "Nur Videos", "Nur Archive", "Nur Andere", "Alle"). Diese Buttons markieren automatisch nur die gew\u00fcnschten Dateitypen oder alle Treffer und heben andere Auswahlm\u00f6glichkeiten auf – ideal f\u00fcr Laien.

    - Der Hilfe-Text im Analyse-Schritt erkl\u00e4rt nun die Farbcodierung der Trefferliste und die neue Schnell-Auswahl per Button in einfacher Sprache.

- Startroutine prüft jetzt optional die Ausbaupfade „Web-Frontend“ und „AppImage-Build“ und zeigt dafür klare Next Steps mit vollständigen Befehlen.
- README enthält jetzt eine laienfreundliche Mini-Roadmap für Web-Frontend und AppImage mit zwei kleinsten Startpunkten.

- Startroutine zeigt jetzt am Ende eine kompakte Laien-Übersicht (Abhängigkeiten, Qualität, Auto-Reparatur, optionale Ausbaupfade) mit klaren Next Steps.
- README-Status enthält jetzt einen Schnellüberblick in einfacher Sprache mit kopierbaren Befehlen für den Warnfall.

**Offen (für „perfekte“ Release-Version):**
 - Vollständiger Button-Only-Modus ohne freie Texteingaben (alle Schritte nur mit Buttons und Dropdowns).
 - Weitere Schnellstart-Buttons (7–10) als große Kacheln inklusive speicherbarer Nutzer‑Presets.

Kurz erklärt: Der Kernpfad ist stabil (Scannen, Planen, Verschieben, Undo, Validierung), aber die große, voll-interaktive Komfortoberfläche aus dem Zielbild ist noch nicht vollständig umgesetzt.

## 0.1) Transparenz: Warum sind noch nicht alle Wunschfunktionen drin?

Die bisherige Umsetzung hat zuerst den **sicheren Kernpfad** priorisiert: Validierung, Undo, Qualitäts-Gates, Start-Reparatur, verständliche Fehlerhilfe.

Die von Ihnen genannte Oberfläche aus dem Zielbild ist eine **größere UX-Ausbaustufe** (UX = Bedienerlebnis) mit mehreren Bausteinen:
- neues Dashboard mit Live-Statistik,
- zusätzliche Aktionsflächen,
- mehrstufige Zielordner-Logik,
- vollständige Button-/Dropdown-Navigation.

Diese Punkte sind realistisch, aber sie wurden noch nicht als eigene abgeschlossene Mini-Iterationen umgesetzt. Der aktuelle Stand ist deshalb „technisch robust im Kern“, aber noch nicht „vollständig wie im Zielbild“.

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
2. Einheitliche Mini-Hilfe in Fehlerfenstern ist aktiv:
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

Stand dieser Informationsdatei: 2026-02-12


## 8) Mini-Roadmap: Web-Frontend und AppImage (einfach erklärt)

Kurzantwort auf die häufige Frage „Ist das einfach?“: **Ja, als kleiner Zusatz ist es gut machbar**, wenn wir in zwei Mini-Punkten arbeiten.

### 8.1 Web-Frontend (Browser-Oberfläche)

- Idee: Bestehende Kernlogik (`core/`) bleibt unverändert.
- Neu: Ein kleines API-Modul (Programmierschnittstelle) in `app/web_api.py`, z. B. mit FastAPI oder Flask.
- Vorteil: Desktop-GUI und Web-UI können später parallel bestehen.

**Kleinster Startbefehl:**

```bash
python3 -m pip install fastapi uvicorn
uvicorn app.web_api:app --reload --host 0.0.0.0 --port 8000
```

### 8.2 AppImage (portable Linux-App)

- Idee: Das bestehende Projekt wird in ein AppDir gepackt und danach als `.AppImage` gebaut.
- Neu: Ein Build-Skript, das die vorhandene `start.sh` und Python-Umgebung einbindet.
- Vorteil: Nutzer:innen können eine Datei herunterladen und direkt starten.

**Kleinster Startbefehl:**

```bash
mkdir -p tools/appimage
cd tools/appimage
wget https://github.com/AppImage/AppImageKit/releases/latest/download/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
```

**Laienhinweis:** AppImage ist ein „portable Paket“ (eine einzelne ausführbare Datei). Das ist praktisch, braucht aber einen sauberen Build-Schritt mit Tests.
