## 2026-02-12 – UI-Fit-Iteration: Bildschirmgerechter Start + dynamische Scroll-Absicherung
- **Was:** `app/main.py` ergänzt eine automatische Fensteranpassung an die verfügbare Bildschirmfläche, höhenabhängige Scrollleisten-Regeln für alle Hauptseiten und eine neue Bildschirm-Hilfe in einfacher Sprache.
- **Warum:** In der bisherigen Ansicht konnten untere Bedienelemente auf kleineren Displays unter den sichtbaren Bereich rutschen und waren schwer erreichbar.
- **Wirkung:** Die Oberfläche bleibt auf einem Bildschirm besser nutzbar, mit klarer Fallback-Navigation per Scrollleisten und verständlicher A11y-Hilfe.

## 2026-02-12 – Start-Iteration: Priorisierter Modul-Reparaturblock + robuster Qualitätszähler + klare A11y-Startführung
- **Was:** `start.sh` ergänzt einen priorisierten Modul-Reparaturblock (kritisch/mittel) im Setup-Log, kapselt Warn-/Info-Zähler in `extract_quality_count` und strukturiert die A11y-Start-Hilfe als 5 klare Schritte.
- **Warum:** Startprobleme sollten schneller priorisiert lösbar sein, Qualitätszähler nicht durch ungültige Werte kippen und Hilfetexte für Einsteiger:innen klarer werden.
- **Wirkung:** Bessere autonome Selbstreparatur, stabilere Qualitätsausgabe und barriereärmere Nutzerführung in einfacher Sprache.

## 2026-02-12 – Responsive-UX-Iteration: Dynamische Seitenhöhe + große Scrollleisten
- **Was:** `app/main.py` nutzt pro Hauptseite jetzt `QScrollArea`, schaltet die Startvorschau je Fensterbreite automatisch um und erweitert die A11y-Styles um breite, kontraststarke Scrollleisten plus größere Skalier-Ecke.
- **Warum:** Auf kleineren Displays waren untere Inhalte, Auswahlfelder und Aktionen teils abgeschnitten und dadurch für Laien schwer erreichbar.
- **Wirkung:** Alle Bereiche bleiben erreichbar, die Ansicht passt sich flexibler an den Bildschirm an und die Bedienung ist für sehschwächere Nutzer:innen deutlich einfacher.

## 2026-02-12 – Start/Release-Iteration: AppImage-Auto-Fix für Laien
- **Was:** `tools/release_gap_report.py` bietet jetzt `--auto-fix-appimage` für automatische Basis-Reparatur (Werkzeug + AppDir), und `start.sh` nutzt diesen Pfad als direkten Optional-Check-Hinweis.
- **Warum:** AppImage-Vorbereitung sollte ohne manuelle Einzelrecherche reproduzierbar und laienfreundlich ablaufen.
- **Wirkung:** Weniger manuelle Schritte, klarere Next Steps bei Fehlern und konsistenter JA/NEIN-Check nach dem Auto-Fix.
## 2026-02-12 (Quality-Dialog Folgeaktionen)
- Was: `tools/quality_gate_gui.py` unterstützt jetzt direkte Aktionen (`auto_fix`, `quality`, `restart`) plus sicheren `report`-Fallback.
- Warum: Nach einem fehlgeschlagenen Qualitätslauf sollen Nutzende ohne Umweg den nächsten sinnvollen Schritt starten können.
- Wirkung: Klarere Hilfe, robustere Debug-Flag-Validierung (`DEBUG_LOG_MODE`) und bessere Tastatur-/A11y-Hinweise im Dialog.

## 2026-02-12 – UX/Start-Iteration: Feste Hilfezeilen + Modul-Autoreparatur
- **Was:** `app/main.py` ergänzt feste Hilfezeilen in „Analyse“ und „Plan“ (Tastaturweg, Kontrast-Hinweis, nächste Aktion); `start.sh` erkennt zusätzlich fehlende Python-Module per Importtest und versucht eine automatische Reparatur mit klarer Erfolgs-/Fehlerausgabe.
- **Warum:** Nutzer:innen sollen in beiden Arbeitsschritten sofort barrierearme Orientierung erhalten und Startprobleme durch fehlende Module automatisch, nachvollziehbar und robust gelöst bekommen.
- **Wirkung:** Bessere A11y-Führung im UI, klarer Reparaturstatus („erfolgreich“/„nicht möglich“) und stabilerer Start ohne manuelle Fehlersuche.
## 2026-02-12 – Quality-Iteration: Exit-Knoten-Audit + klare Selfcheck-Next-Steps
- **Was:** Neues Tool `tools/exit_path_audit.py` ergänzt und in `tools/run_quality_checks.sh` als fester Schritt integriert; `core/selfcheck.py` liefert jetzt bei Erfolg/Fehlern klare „Nächster Schritt“-Hinweise.
- **Warum:** Exit-Pfade sollten nicht nur abbrechen, sondern immer eine direkte, laienfreundliche Lösung anbieten und automatisch geprüft werden.
- **Wirkung:** Konsistentere Fehlermeldungen, besserer Accessibility-Textfluss und automatischer Nachweis, dass zentrale Exit-Knoten konkrete Lösungswege bieten.

## 2026-02-12 – Debug-Iteration: Optischer GUI-HTML-Snapshot
- **Was:** `app/main.py` erzeugt jetzt automatisch `docs/debugging_gui_state.html`, ergänzt den Button „Debug-HTML öffnen“ und erweitert den Smoke-Test in `tools/smoke_test.py` um Snapshot-Prüfungen.
- **Warum:** Der aktuelle GUI-Zustand soll jederzeit visuell nachvollziehbar und als einfache Testdatei nutzbar sein.
- **Wirkung:** Bessere Debug-Transparenz, direkter Zugriff auf den Live-Stand und robustere Qualitätsabsicherung für den HTML-Snapshot.

## 2026-02-12 – UX-Iteration: Modus-Trennung + Tool-Bibel + Gate-Übersicht
- **Was:** `app/main.py` ergänzt eine Modus-Auswahl (Laien/Entwickler), einen Tool-Bibel-Dialog mit schnellen Dokumentpfaden und eine kompakte Gate-Übersicht (G1–G4) im Dashboard.
- **Warum:** Laien sollen weniger kognitive Last haben, während fortgeschrittene Nutzer technische Transparenz direkt im Tool erhalten.
- **Wirkung:** Klarere Informationshierarchie, bessere Auffindbarkeit der Entwicklerdoku und verständlichere Statuskommunikation für den nächsten Schritt.

## 2026-02-12 – Start-Iteration: A11y-Theme-Gate + Auto-Fix-Qualitätslauf + klarere Hilfe
- **Was:** `start.sh` führt jetzt automatisch den A11y-Theme-Check aus, erweitert die A11y-Hilfe um Theme-Auswahl/Prüfbefehl und startet bei Qualitätswarnungen genau einen Auto-Fix mit anschließendem Kontrolllauf.
- **Warum:** Nutzer:innen sollen Kontrast-/Theme-Probleme und Qualitätswarnungen ohne Fachwissen direkt beim Start mit klarer Reihenfolge beheben können.
- **Wirkung:** Bessere Barrierefreiheit, robusterer Startprozess und verständliche Next Steps bei verbleibenden Warnungen.

## 2026-02-12 – Quality-Iteration: Zahlenbereichsprüfung + Hilfetexte + robuste JSON-Checks
- **Was:** `tools/run_quality_checks.sh` erweitert den JSON-Check um optionale Min/Max-Bereiche und prüft `confirm_threshold` in allen Presets auf den Bereich 1–100.
- **Warum:** Falsche Zahlenwerte sollen früh und eindeutig erkannt werden, bevor sie später zu schwer verständlichen Laufzeitproblemen führen.
- **Wirkung:** Der Qualitätslauf liefert bei Bereichsverstößen jetzt klare Korrekturbeispiele in einfacher Sprache und erhöht die Release-Sicherheit.

## 2026-02-12 – AppImage-Readiness-Kurzcheck
- **Was:** `tools/release_gap_report.py` prüft AppImage-Mindestkriterien mit `--appimage-only`; `start.sh` zeigt den JA/NEIN-Status jetzt direkt beim Start.
- **Warum:** Die Frage „Ist das AppImage releasefertig?“ sollte ohne manuelles Durchsuchen der Logs in einem Schritt beantwortbar sein.
- **Wirkung:** Klarer Release-Status in einfacher Sprache plus direkte Next Steps bei fehlenden Build-Bausteinen.

## 2026-02-12 – Doku-Iteration: Feste Standard-Prüfroutinen-Tabelle im Entwicklerhandbuch
- **Was:** In `docs/developer_manual.md` wurde eine separate Tabelle „Standard → konkrete Prüfroutine" ergänzt, inklusive Automatisierungsstatus und Nutzerfeedback in einfacher Sprache.
- **Warum:** Für das letzte kleine Refactoring-Teilstück fehlte eine feste, schnell prüfbare Zuordnung von Standards zu konkreten Checks.
- **Wirkung:** Entwickler:innen sehen jetzt sofort, welcher Standard durch welchen Befehl abgesichert ist und ob die Startroutine das automatisch übernimmt.

## 2026-02-12 – Manifest-Iteration: Vorgabenabdeckung ergänzt und Lücken geschlossen
- **Was:** `data/standards_manifest.json` auf v1.1 erweitert (G5 Mini-UX-Gate, Doku-Pflichten, Auto-Qualität/Formatierung, Hilfeelement- und Next-Step-Pflichten) und README-Abschnitt zur Manifest-Abdeckung ergänzt.
- **Warum:** Die Frage „Sind alle Vorgaben im Manifest?“ sollte direkt mit klarer, prüfbarer Struktur beantwortbar sein.
- **Wirkung:** Fehlende Manifest-Punkte sind jetzt explizit dokumentiert; offene Arbeit ist auf die laufende technische Ausführung pro Iteration begrenzt.

## 2026-02-12 – Qualitäts-Iteration: GUI-Kurzbericht an Start-Log angeglichen
- **Was:** `tools/quality_gate_gui.py` enthält jetzt eine robuste Warn-/Hinweis-Erkennung aus dem Report, Input-Validierung und denselben Kompaktblock mit Auto-Fix-Schritten wie `start.sh`.
- **Warum:** GUI- und Terminal-Nutzer sollten identische, laienfreundliche Next Steps erhalten, damit die Fehlerbehebung konsistent bleibt.
- **Wirkung:** Einheitlicher Qualitätsdialog mit klarer 3-Schritt-Hilfe, besserer Barrierefreiheit und weniger Missverständnissen bei Warnungen.

## 2026-02-12 – Iteration
- **Was:** AGENTS-Regeln präzisiert (README alle 2–3 Iterationen; 3-Punkte-Zählung nur für Funktionsaspekte außerhalb von Info-Dateien) und detaillierte Projektbeschreibung inkl. Dateinamen-Suffix-Strategie ergänzt.
- **Warum:** Mehr Klarheit bei Scope, Wartbarkeit und sicherer Umstellung auf versionierte Dateinamen.
- **Wirkung:** Iterationen sind besser steuerbar; Erweiterbarkeit und Migrationspfad sind dokumentiert und sofort nutzbar.

## 2026-02-12 – Doku-Iteration: Standards-Check + README-Oberflächenbild + klare Refactoring-Aussage
- **Was:** README um einen kompakten Standards-Check (Info-Dateien), ein eingebettetes kleines Oberflächenbild (SVG, Alt-Text) und ein klares Refactoring-Kurzfazit ergänzt.
- **Warum:** Die Fragen zu Globalstandards, Dokumentationsabdeckung und README-Bild sollten direkt, barrierearm und ohne Zusatzdateien beantwortet werden.
- **Wirkung:** Schnellere Orientierung für Teams, sichtbare UI-Vorschau in der README und besser nachvollziehbare Doku-Reife.

## 2026-02-12 – Start-Iteration: Optional-Kurzbericht + Status-Validierung + Debug-Hilfe
- **Was:** `start.sh` ergänzt einen einheitlichen Kurzbericht für optionale Checks, validiert optionalen Status strikt auf `OK/WARN` und protokolliert im Debug-Modus den genauen Prüf-Befehl.
- **Warum:** Optionale Warnungen sollten ohne Fachwissen sofort in einer klaren Reihenfolge lösbar sein, während fehlerhafte Statuswerte technisch abgefangen werden.
- **Wirkung:** Robustere Startausgabe, bessere Nachvollziehbarkeit im Debug-Log und barriereärmere Next Steps für Web-/AppImage-Ausbaupfade.

## 2026-02-12 – A11y/Quality/Start-Iteration: Zustandskontrast, Registry-Gate und Debug-Hilfe
- **Was:** `tools/a11y_theme_check.py` prüft nun Standard-, Auswahl- und Disabled-Kontrast; `tools/run_quality_checks.sh` ergänzt einen 8/8-Check für `data/version_registry.json`; `start.sh` validiert `DEBUG_LOG_MODE` strikt und protokolliert im Debug-Modus zusätzliche Hinweise.
- **Warum:** Kontrastprobleme entstehen oft in Zuständen (ausgewählt/deaktiviert), Registry-Fehler sollen früh auffallen und Debug-Ausgaben sollen ohne Fachsprache klar steuerbar sein.
- **Wirkung:** Bessere Barrierefreiheit über mehrere Theme-Zustände, höhere Doku-/Release-Sicherheit und verständlichere Fehlersuche mit klaren Next Steps.

## 2026-02-12 – Quality-Iteration: robustere Auto-Prüfung mit klarer Abschlusshilfe
- **Was:** `tools/run_quality_checks.sh` nutzt für Tool-Installationen jetzt bevorzugt `venv/bin/python`, validiert alle zentralen 0/1-Flags strikt und ergänzt eine kurze Abschluss-Zusammenfassung mit klarer Reparatur-Reihenfolge.
- **Warum:** Dadurch laufen automatische Abhängigkeitsauflösungen stabiler im Projektkontext, Fehlkonfigurationen werden früh abgefangen und Nutzer:innen erhalten besser verständliche Next Steps.
- **Wirkung:** Höhere Zuverlässigkeit der vollautomatischen Qualitätsprüfung, bessere Barrierefreiheit durch einfache Sprache und weniger Support-Aufwand bei fehlerhaften Startparametern.


## 2026-02-12 – Release-Iteration: Restpunkte zu Tests und Validierungsstandard geschlossen
- **Was:** `core/validation.py`, `tools/smoke_test.py` und `tools/run_quality_checks.sh` um verpflichtende Input-/Output-Validierung plus automatische Prüfungen erweitert.
- **Warum:** Die letzten offenen Release-Punkte (mehr Kernmodul-Tests und technische Erzwingung der Validierungsstandards) sollten reproduzierbar abgeschlossen werden.
- **Wirkung:** Qualitätslauf meldet Standardlücken sofort mit Next Steps, und der Smoke-Test deckt zentrale Validierungsfehler jetzt automatisch ab.
## 2026-02-12 – Release-Iteration: Codeformat-Releasepunkt abgeschlossen + Status-Sync + A11y-Textpflege
- **Was:** `RELEASE_CHECKLIST.md` markiert den offenen Releasepunkt zur festen Codeformatierung im Quality-Gate als abgeschlossen; README-Status wurde auf denselben Stand synchronisiert und um einen kurzen A11y-Hinweis ergänzt.
- **Warum:** Ein offener Release-Punkt sollte vollständig beendet und in allen Steuerdokumenten konsistent sichtbar sein, damit keine widersprüchlichen Reifestände entstehen.
- **Wirkung:** Messbarer Release-Fortschritt (16/18), klarere barrierearme Orientierung in einfacher Sprache und eine belastbare Basis für die letzten zwei offenen Punkte.

## 2026-02-12 – Start-Iteration: Qualitäts-Kompaktblock + Zähler-Validierung + klare Auto-Fix-Hilfe
- **Was:** `start.sh` ergänzt einen kompakten Qualitätsblock mit Warn-/Hinweiszähler, validiert diese Werte als nicht-negative Ganzzahlen und zeigt klare Auto-Fix-Befehle in richtiger Reihenfolge.
- **Warum:** Nutzer:innen sollten Warnungen ohne Rätselraten und ohne fehlerhafte Statusanzeige direkt beheben können.
- **Wirkung:** Stabilere Startausgabe, bessere Barrierefreiheit durch einfache Sprache und schnellere Selbstreparatur mit kopierbaren Befehlen.

## 2026-02-12 – Quality-Iteration: Schrittzählung + Typvalidierung + klarere Hilfe
- **Was:** `tools/run_quality_checks.sh` nutzt jetzt eine konsistente 6/6-Schrittanzeige, prüft bei JSON-Dateien zusätzlich zentrale Datentypen und gibt bei Typfehlern verständlichere Next Steps aus.
- **Warum:** Pflichtfelder allein reichen nicht aus; falsche Werttypen führen sonst erst später zu schwerer verständlichen Laufzeitproblemen.
- **Wirkung:** Frühere Fehlererkennung, klarere Nutzerführung und robustere Qualitäts-Gates für Konfigurationen.

## 2026-02-12 – Start-Iteration: Arbeitsordner-Autoprüfung + Rechtecheck + Hilfe
- **Was:** `start.sh` prüft beim Start den Arbeitsordner im Linux-Nutzerpfad (`~/.local/share/provoware-clean-tool-2026`), legt ihn bei Bedarf an und synchronisiert ihn in `data/settings.json`.
- **Warum:** Das Tool soll ohne manuelle Vorarbeit mit einem sicheren Projektstandard-Ordner starten und Rechteprobleme früh, verständlich und reproduzierbar melden.
- **Wirkung:** Höhere Startstabilität, klare Reparaturhinweise bei Linux-Rechten und barriereärmere Nutzerführung durch einfache Next Steps.

## 2026-02-12 – Start/Quality-Iteration: Venv-Autoreparatur + Auto-Tool-Install + A11y-Kurzhilfe
- **Was:** `start.sh` erkennt jetzt den verfügbaren Paketmanager (`apt-get`/`dnf`/`pacman`) für eine automatische Venv-Reparatur, `tools/run_quality_checks.sh` installiert fehlende Qualitätswerkzeuge optional automatisch, und die Startausgabe ergänzt feste A11y-Hinweise.
- **Warum:** Abhängigkeiten und Qualitätswerkzeuge sollen ohne manuelle Hürden nachgezogen werden, während Nutzer:innen klare Hilfe zu Tastatur und Kontrast direkt beim Start sehen.
- **Wirkung:** Höhere Autonomie der Startroutine, weniger Setup-Abbrüche und besser verständliche, barrierearme Next Steps im Standardablauf.

## 2026-02-12 – Text-Iteration: Status, Hilfe, Aufgabenpflege
- **Was:** README-Status (Fortschritt/Abgeschlossen/Offen/Nächster Schritt) präzisiert, zwei Laienvorschläge ergänzt und `todo.txt` konsistent mit DONE/NEXT aktualisiert.
- **Warum:** Reine Textdateien sollten den aktuellen Stand ohne Umwege verständlich, barrierearm und direkt ausführbar zeigen.
- **Wirkung:** Bessere Orientierung für Nicht-Techniker, klarere Übergabe für das Team und nachvollziehbarer nächster Arbeitsschritt.

## 2026-02-11 – Planungs-Iteration: Nächste logische 3-Schritte klar dokumentiert
- **Was:** README um einen laienfreundlichen Abschnitt „Nächste logische Schritte“ mit genau drei priorisierten Punkten, Abnahmekriterien und vollständigen Befehlen ergänzt.
- **Warum:** Die Frage nach den nächsten sinnvollen Arbeiten sollte als sofort nutzbarer, standardisierter 3-Punkte-Plan beantwortet werden.
- **Wirkung:** Team und Nutzer:innen können die nächste Iteration direkt, nachvollziehbar und barrierearm starten.

## 2026-02-11 – Analyse-Iteration: Nächste offene Punkte priorisiert
- **Was:** README ergänzt um vollständige Analyse der drei nächsten offenen Optimierungspunkte (Accessibility-Hilfe, Start-Autoreparatur, Quality-Automation) inklusive Reihenfolge und Abnahmekriterien.
- **Warum:** Der Projektstand war inhaltlich breit, aber die nächsten konkreten Schritte nicht kompakt priorisiert und für Laien nicht sofort umsetzbar beschrieben.
- **Wirkung:** Es gibt jetzt einen klaren, messbaren Drei-Punkte-Plan mit kopierbaren Befehlen für die nächste merge-ready Iteration.

## 2026-02-11 – UI-Iteration: Farbige Trefferliste & Typ-Auswahl

- **Was:** Die Analyse-Trefferliste ist farblich kodiert (hellblau für Bilder, helllila für Videos, hellorange für Archive, hellgrau für andere Dateien). Außerdem wurden neue Schaltflächen („Nur Bilder“, „Nur Videos“, „Nur Archive“, „Nur Andere“, „Alle") unter der Sortierauswahl ergänzt, um schnell nur bestimmte Dateitypen auszuwählen. Der Hilfe-Text im Analyse-Schritt erklärt nun die Farb-Kodierung und die Schnell-Auswahl.
- **Warum:** Laien sollen die verschiedenen Dateitypen auf einen Blick unterscheiden können und ohne komplizierte Mehrfachauswahl schnell nur die gewünschten Dateien markieren können.
- **Wirkung:** Bessere Übersichtlichkeit durch Farbkodierung, schnelleres Arbeiten durch direkte Typauswahl, verständliche Anleitung zum Nutzen der neuen Funktionen.

## 2026-02-11 – Schnellstart‑Buttons 4–6, Web‑API & Button‑Only‑Iteration

- **Was:** Im Options-Schritt wurden drei weitere Schnellstart‑Buttons (Dokumente sortieren, Musik sortieren, Alles sortieren) ergänzt. Sie laden jeweils eigene Presets (`quick_docs`, `quick_music`, `quick_all`), starten sofort einen Scan und zeigen die Vorschau an. Zudem wurde ein erstes API‑Skelett (`app/web_api.py`) mit zwei Endpunkten (`/status`, `/dry_run`) geschaffen und der Einsteiger‑Modus (Button‑Only) implementiert, der komplexe Filter im Options‑Schritt ausblendet und die Schnellstart‑Buttons in den Mittelpunkt rückt.
- **Warum:** Einige Nutzer:innen möchten ihre Dateien ohne manuelle Filter oder komplexe Menüs aufräumen, andere wünschen eine webbasierte Steuerung. Weitere Schnellstart‑Buttons decken zusätzliche Dateitypen ab, ein API‑Prototyp ermöglicht künftige Web‑UIs und der Einsteiger‑Modus erleichtert die Bedienung für Laien.
- **Wirkung:** Schnellerer Einstieg durch sechs große Schnellstart‑Schalter, laienfreundliche Web‑Schnittstelle für Statusabfrage und Trockenlauf, sowie vereinfachte Oberfläche im Einsteiger‑Modus. Zusammen legen die Änderungen die Grundlage für mehr Komfort und flexiblere Nutzung.

## 2026-02-11 – Namens- & Refactoring-Iteration

- **Was:** Der Fenstertitel und die Projektbezeichnung wurden von „Downloads Organizer/Aufräumer“ in „Provoware Clean Tool 2026“ geändert. Zudem wurde eine Hilfsmethode zur standardisierten Button-Erzeugung eingeführt, die konsistente Größen, Tooltips und Accessibility‑Namen setzt. Verlaufsschaltflächen nutzen diese nun.
- **Warum:** Ein einheitlicher Name erhöht die Wiedererkennung des Tools und vermeidet Verwirrung. Einheitliche Buttons verbessern Lesbarkeit und Barrierefreiheit.
- **Wirkung:** Klare Benennung des Programms; alle Hauptfunktionen der Verlaufsansicht verfügen jetzt über konsistente Schaltflächen mit verbesserter Barrierefreiheit.

## 2026-02-11 – Dashboard-Verlauf-Iteration

- **Was:** Ein neues Modul `core/history.py` speichert jeden Aufräumlauf mit Zeitstempel, Dateianzahl und Megabyte-Anzahl in einer JSON-Datei. Die Startseite (Entwicklerbereich) zeigt jetzt einen Verlauf aller Läufe mit Export- und Lösch-Schaltflächen. Nach einer erfolgreichen Ausführung wird automatisch ein neuer Eintrag angelegt. Hilfetexte erklären den Verlauf und führen zu Export oder Reset.  
- **Warum:** Nutzer:innen sollen sehen, wie viel Speicherplatz sie über mehrere Aufräumläufe gewonnen haben, die Daten exportieren können oder bei Bedarf den Verlauf löschen. Dies stärkt die Transparenz und gibt Kontrolle über die eigenen Nutzungsdaten.  
- **Wirkung:** Im Dashboard gibt es jetzt eine barrierearme Verlaufsliste; Export speichert die Historie als CSV in den Ordner `exports`, und ein Lösch-Knopf entfernt alle Einträge. Die Änderung verbessert die Nachvollziehbarkeit und die Bedienung bleibt laienfreundlich.

## 2026-02-12 – UI/Language-Iteration: Deutscher Fenstertitel + Hilfe-Knopf
## 2026-02-12 – Quick-Buttons & Textsystem-Iteration
**Was:** Im Options-Schritt wurden drei Schnellstart-Buttons („Fotos sortieren“, „Große Dateien prüfen“, „Duplikate finden“) hinzugefügt, die jeweils ein voreingestelltes Preset laden und sofort einen Scan starten. Ein zentraler Textkatalog (`ui_texts.json`) speichert jetzt die Kurzanleitung und die Bezeichnungen/Tooltips der Schnellstart-Buttons. Darüber hinaus wurde die Analyse-Trefferliste sortierbar nach Name oder Größe gestaltet und im Plan-Schritt ein Rechtsklick-Menü „Zielordner öffnen“ ergänzt.  
**Warum:** Häufige Reinigungsaufgaben sollen ohne manuelle Filtereinstellung direkt ausführbar sein. Ein zentraler Textkatalog vereinfacht spätere Textänderungen und Übersetzungen. Die Sortier-Optionen und das Kontextmenü erhöhen die Übersicht und sparen Klicks.  
**Wirkung:** Schnellere, laienfreundliche Bedienung durch große Schnellstart-Kacheln; besser wartbarer Code durch zentrale Textdatei; höhere Orientierung in der Analyse- und Plan-Ansicht durch Sortierfunktion und zusätzlichen Kontextbefehl.

- **Was:** `app/main.py` setzt nun den Fenstertitel vollständig auf Deutsch („Downloads Aufräumer“) und ergänzt auf der Startseite eine barrierearme „Hilfe“-Schaltfläche mit Kurzanleitung; `README.md` Release-Status und „Abgeschlossen“-Liste entsprechend aktualisiert.
- **Warum:** Englischsprachige Begriffe verwirrten Laien, und eine schnell zugängliche Hilfe war nicht vorhanden.
- **Wirkung:** Klarere Benennung ohne Fachbegriffe, schnellerer Einstieg durch leicht verständliche Anleitung und vollständige Dokumentation der Änderung in den Infodateien.

## 2026-02-12 – UI/Info-Iteration: Status-Legende + zugänglichere Filter im Entwicklerbereich
- **Was:** `app/main.py` ergänzt im Entwicklerbereich eine klare Status-Legende (✅/🟡) mit kurzer Bedienhilfe; die Filter-Buttons „Alle“ und „Nur offen“ wurden mit größeren Klickflächen und Accessibility-Namen ausgestattet. `README.md` und `todo.txt` wurden auf den neuen Iterationsstand synchronisiert.
- **Warum:** Der Entwickler-Hilfebereich sollte visuell klarer, für Tastatur-/Screenreader-Nutzung verständlicher und in den Info-Dateien konsistent dokumentiert werden.
- **Wirkung:** Besseres Layout mit schnellerer Orientierung im Statusbereich sowie nachvollziehbarer, einheitlicher Projektstand in den Infodateien.

## 2026-02-12 – UI-Iteration: Auswahlstatus + Pfadkopie in der Trefferliste
- **Was:** `app/main.py` ergänzt im Analyse-Schritt einen live aktualisierten Auswahlstatus (X von Y) sowie den neuen Button „Auswahlpfade kopieren“ mit Zwischenablage-Ausgabe.
- **Warum:** Die Trefferliste brauchte klarere Rückmeldung zur aktuellen Auswahl und eine schnelle, laienfreundliche Weitergabe markierter Dateipfade.
- **Wirkung:** Bessere Orientierung, barriereärmere Aktionen und klare Next Steps bei leerer Auswahl ohne stilles Scheitern.

## 2026-02-12 – UI/Smoke-Iteration: Status-Hilfebereich + Filterprüfung
- **Was:** `app/main.py` ergänzt im Entwicklerbereich den Hilfebereich „Implementiert vs. Geplant“ mit zwei Filtern („Alle“, „Nur offen“); `tools/smoke_test.py` enthält eine Mini-Prüfung für beide Filterpfade.
- **Warum:** Nutzer:innen sollen den Projektstatus sofort sehen, und die Filterlogik soll automatisiert gegen Abstürze abgesichert sein.
- **Wirkung:** Mehr Transparenz in der GUI sowie stabile Smoke-Absicherung mit sinnvollen Statusinhalten für beide Filtermodi.

## 2026-02-12 – Qualitäts-Iteration: JSON-Pflichtfelder + ehrliche Abschlussmeldung
- **Was:** `tools/run_quality_checks.sh` prüft jetzt zusätzlich zentrale JSON-Dateien auf Pflichtfelder und zeigt bei Warnungen einen klaren Warn-Abschluss statt pauschalem OK.
- **Warum:** Für Release-Reife fehlte eine automatische Strukturprüfung variabler Konfigurationsdateien und eine eindeutigere Ergebnisanzeige bei verbleibenden Warnungen.
- **Wirkung:** Defekte Konfigurationen werden früher erkannt und Nutzer:innen erhalten verständliche Next Steps in einfacher Sprache.

## 2026-02-12 – Settings-Iteration: Laien-Schalter + Einstellungs-Hilfetexte
- **Was:** `core/settings.py` erweitert um Einsteiger-Modus, Dateitypen-Schalter, Zielordner-Modus/Zielpfad und aktivierbare Hilfehinweise inklusive robuster Normalisierung; `README.md` Release-Status und „Abgeschlossen“-Liste entsprechend aktualisiert.
- **Warum:** Für Laien fehlten klare, schalterbasierte Einstellungsoptionen mit verständlichen Empfehlungen statt technischer Rohwerte.
- **Wirkung:** Einstellungen sind jetzt stärker barrierearm geführt, valider beim Laden/Speichern und liefern direkt nutzbare Next-Step-Hinweise in einfacher Sprache.

## 2026-02-12 – UI-Iteration: Fokusrahmen + Grafik-Checkliste
- **Was:** `app/main.py` ergänzt sichtbare Fokusrahmen für zentrale Eingabeelemente und einen neuen Hilfebutton „Grafik-Verbesserungen anzeigen“ mit 4 konkreten UI-Tipps.
- **Warum:** Die Frage nach weiteren grafischen Verbesserungen sollte direkt in der Oberfläche beantwortet werden, während die Tastatur-Nutzung noch klarer erkennbar wird.
- **Wirkung:** Bessere Barrierefreiheit durch deutlichen Fokuszustand und sofort nutzbare, laienfreundliche Empfehlungen zu Kontrast, Abständen und Statuskonsistenz.

## 2026-02-12 – Start/README-Iteration: Laien-Übersicht + Schnellüberblick
- **Was:** `start.sh` ergänzt eine validierte Abschluss-Zusammenfassung in einfacher Sprache mit klaren Next Steps; `README.md` ergänzt einen kompakten Schnellüberblick für den Warnfall.
- **Warum:** Nutzer:innen sollten den Gesamtstatus ohne Fachwissen sofort verstehen und bei Warnungen direkt die richtigen Befehle sehen.
- **Wirkung:** Bessere Übersichtlichkeit beim Start, weniger Unsicherheit im Fehlerfall und klarere Selbsthilfe für Nicht-Techniker.

## 2026-02-12 – UI-Iteration: Theme-Schnellwahl + Interaktivitätsstatus
- **Was:** `app/main.py` ergänzt Theme-Schnellwahl-Tasten (`Alt+1` bis `Alt+5`) und erweitert die Live-Vorschau um einen klaren Interaktivitäts-/Kontraststatus mit nächstem Klick.
- **Warum:** Der Theme-Wechsel sollte schneller und ohne Umwege nutzbar sein; zusätzlich fehlte eine laienfreundliche Rückmeldung zur aktuellen visuellen Qualität.
- **Wirkung:** Bedienung ist direkter per Tastatur/Klick möglich, und Nutzer:innen erhalten sofort verständliche Hinweise zu Kontrast, Lesbarkeit und nächster Aktion.

## 2026-02-11 – UI-Iteration: Auto-Vorschauprofil + Resize-Aktualisierung
- **Was:** `app/main.py` ergänzt für Vorschau-Skalierung und Vorschau-Position jeweils „Auto (Fensterbreite)“, löst daraus ein dynamisches Profil auf und aktualisiert die Vorschau bei Fenstergrößenänderung automatisch.
- **Warum:** Die UI sollte sich ohne manuelles Nachstellen flexibel an unterschiedliche Bildschirmgrößen anpassen und dabei barrierearme Lesbarkeit/Kontrast erhalten.
- **Wirkung:** Elemente und Bereiche bleiben besser aufeinander abgestimmt, inklusive klarer Auto-Rückmeldung in der Live-Vorschau und robuster Input-/Output-Validierung bei Auto-Auflösung.

## 2026-02-11 – Start-Iteration: Optional-Check Web-Frontend + AppImage-Roadmap
- **Was:** `start.sh` prüft jetzt optional die Bereitschaft für Web-Frontend- und AppImage-Ausbaupfade mit klaren Next Steps; `README.md` ergänzt eine einfache Mini-Roadmap mit sofort nutzbaren Befehlen.
- **Warum:** Die Frage nach Web-Frontend und AppImage sollte ohne Umwege direkt im Projekt beantwortet und als kleinster umsetzbarer Startpfad vorbereitet werden.
- **Wirkung:** Nutzer:innen sehen sofort, was bereits bereit ist, welche Abhängigkeiten fehlen und wie die nächsten zwei Mini-Schritte konkret aussehen.
## 2026-02-12 – UI-Iteration: Globale A11y-Styles + zentrale Combo-Validierung
- **Was:** `app/main.py` ergänzt globale A11y-Styles (disabled-Kontrast, größere Checkbox-Indikatoren, klare Listen-/Dropdown-Auswahl) und führt `_set_combo_text_or_raise` für robuste Combo-Auswahl mit Input-/Output-Validierung ein.
- **Warum:** Barrierefreiheit und Validierung sollten einheitlich wirken, damit Schnellmodi und Presets bei ungültigen Werten nicht still fehlschlagen.
- **Wirkung:** Bessere Lesbarkeit in allen Themes, klarere Tastatur-/Auswahl-Rückmeldung und verständliche Next Steps bei fehlerhaften Kombobox-Werten.

## 2026-02-11 – UI-Iteration: auswählbare Trefferliste + Workflow-Beispiele
- **Was:** `app/main.py` ergänzt im Analyse-Schritt eine auswählbare Trefferliste mit Mehrfachauswahl sowie die Aktionstasten „Alle markieren“ und „Auswahl löschen“; zusätzlich wurden im Options-Schritt zwei kurze Workflow-Beispiele in einfacher Sprache ergänzt.
- **Warum:** Bisher konnten gefundene Dateien nicht gezielt ausgewählt werden, und der Ablauf war für zwei typische Alltagsszenarien noch nicht klar genug erklärt.
- **Wirkung:** Nutzer:innen können Treffer präzise steuern, erkennen vorhandene Aktionstasten leichter und verstehen den Gesamtworkflow schneller und sicherer.

## 2026-02-12 – UI-Iteration: Kategorie-Leiste + Aktionskarten (visuelle Vorschau)
- **Was:** `app/main.py` ergänzt in der Startansicht eine linke Kategorie-Leiste und zentrale Aktionskarten als reine Vorschau ohne Logikwechsel.
- **Warum:** Die gewünschte Hauptansicht sollte in zwei kleinen, sicheren Schritten vorbereitet werden, ohne bestehende Abläufe zu riskieren.
- **Wirkung:** Nutzer:innen sehen den künftigen Aufbau früher, verstehen die Navigation besser und behalten stabile Funktionalität im aktuellen Assistenten.

## 2026-02-12 – UI-Iteration: Persistenzstatus + verifiziertes Speichern
- **Was:** `app/main.py` ergänzt `_save_settings_with_feedback`, verifiziert gespeicherte Werte per Reload und zeigt im Dashboard einen klaren Persistenzstatus mit ✅/⚠️.
- **Warum:** Nutzer:innen sollten direkt sehen, ob Einstellungen wirklich dauerhaft gespeichert wurden, statt dies erst nach einem Neustart zu bemerken.
- **Wirkung:** Mehr Transparenz und Stabilität bei Theme-, Ordner- und Filtereinstellungen mit verständlichen Next Steps im Fehlerfall.

## 2026-02-11 – UI-Iteration: A11y-Schnellmodi + Live-A11y-Hinweis
- **Was:** `app/main.py` ergänzt zwei neue Schnellaktionen „Lesbarkeit sofort maximieren“ (`Alt+K`) und „Ausgewogene Ansicht laden“ (`Alt+L`) für Theme, Textgröße, Vorschau-Skalierung und Position; zusätzlich zeigt die Live-Vorschau jetzt einen laienfreundlichen A11y-Hinweis pro Theme.
- **Warum:** Für den Einstieg fehlte ein sofort nutzbarer Barrierefreiheits-Kurzweg und eine klare Erklärung, welches Theme in welcher Situation hilft.
- **Wirkung:** Nutzer:innen erreichen mit einem Klick eine gut lesbare Oberfläche und bekommen direkt verständliche Orientierung zu Kontrast, Fokus und Textgröße.

## 2026-02-12 – UI-Iteration: Dashboard-Sicherheit + barriereärmeres Startlayout
- **Was:** `app/main.py` maskiert Dashboard-Inhalte jetzt HTML-sicher, zeigt Berechtigungen konsistent mit OK/Warnsymbol und verbessert das Startlayout mit klaren Abständen, Kartenrahmen, Mindestbreiten und Shortcut `Alt+O` für die Ordnerwahl.
- **Warum:** Die Schnellübersicht sollte robust gegen Sonderzeichen bleiben und die erste Oberfläche visuell ruhiger, besser fokussierbar und schneller per Tastatur bedienbar sein.
- **Wirkung:** Stabilere Anzeige ohne fehlerhafte Rich-Text-Effekte, bessere Lesbarkeit/Kontraststruktur und zugänglichere Bedienung im ersten Schritt.

## 2026-02-12 – UI-Iteration: Flexible Vorschau-Skalierung + variable Positionierung
- **Was:** `app/main.py` ergänzt zwei neue Vorschau-Regler: „Bereichsskalierung“ (100/115/130/150%) und „Vorschau-Position“ (links/rechts/untereinander), jeweils mit robuster Input-/Output-Validierung und klaren Next-Step-Fehlertexten.
- **Warum:** Für unterschiedliche Bildschirmgrößen und Sehbedarfe fehlte bisher eine direkte Feinsteuerung der Vorschaufläche und ihrer Anordnung.
- **Wirkung:** Mehr Flexibilität, bessere Barrierefreiheit und schnellere Theme-/Kontrastprüfung, weil Layout und Größe direkt live angepasst werden können.

## 2026-02-12 – Release-Iteration: Modulcheck bereinigt + Doku finalisiert
- **Was:** `start.sh` nutzt jetzt eine zentrale Funktion für die Prüfung fehlender Python-Module, und die Release-Dokumente wurden auf den aktuellen Stand (92%) angehoben.
- **Warum:** Doppelter Prüfcode war unnötig und erschwerte Wartung; zusätzlich brauchte der Release-Stand klare, konsistente Leitlinien für Entwickler:innen und Laien.
- **Wirkung:** Weniger Redundanz im Startcode, bessere Wartbarkeit und verständliche, synchronisierte Release-Dokumentation mit klaren nächsten Schritten.

## 2026-02-11 – UI-Iteration: Linux-Berechtigungen + Aufräumziel-Schnellwahl

## 2026-02-11 – Analyse-Iteration: Trefferliste sortieren & Zielordner-Öffnen-Menü
- **Was:** `app/main.py` ermöglicht nun die Sortierung der Trefferliste im Analyse-Schritt nach Name oder Dateigröße über ein Dropdown-Feld. Im Plan-Schritt ist ein neues Kontextmenü verfügbar: Ein Rechtsklick auf einen Eintrag bietet die Option „Zielordner öffnen“, die den entsprechenden Zielordner im Dateimanager startet. Zudem wurden `README.md` und `todo.txt` aktualisiert, um diese Änderungen zu dokumentieren.
- **Warum:** Viele Nutzer:innen wünschten, große Dateien schneller erkennen zu können und die Möglichkeit zu haben, aus dem Plan direkt zum Zielordner zu springen. Das erleichtert die Überprüfung des Aufräumvorschlags und reduziert die Navigation im Dateisystem.
- **Wirkung:** Die Trefferauswahl ist übersichtlicher und praxistauglicher: Größere Dateien können leicht nach vorne sortiert werden, und der Zugriff auf das Zielverzeichnis erfolgt per Klick – ohne mühsames Suchen im Explorer.
- **Was:** `app/main.py` prüft jetzt Linux-Rechte (Lesen/Öffnen/Schreiben) im Dashboard sowie vor Scan/Plan/Ausführung und ergänzt zusätzlich eine neue Schnellwahl „Aufräumziel“ mit vier üblichen Reinigungsprofilen.
- **Warum:** Nutzer:innen wollten klare Sicherheit bei Berechtigungen und zugleich eine laienfreundliche, maximal konfigurierbare Führung für typische Aufräumaufgaben.
- **Wirkung:** Weniger Abbrüche durch Rechteprobleme, verständliche Next Steps inklusive `chmod`-Hinweis und schnellerer Einstieg über farbig erklärte Reinigungsoptionen.

## 2026-02-11 – UI-Iteration: Live-Theme-Vorschau im Startschritt
- **Was:** `app/main.py` ergänzt jetzt eine echte Live-Vorschaukarte (Hinweistext + Beispiel-Button + Beispiel-Liste) und aktualisiert sie bei Theme-/Textgrößen-Änderung sofort mit Input-/Output-Validierung.
- **Warum:** Nutzer:innen sollten Farben, Fokus und Lesbarkeit vor dem Speichern direkt sehen, statt erst nach dem nächsten Schritt.
- **Wirkung:** Bessere Barrierefreiheit und klarere Entscheidungen, weil Kontrast und Bedienzustände sofort sichtbar sind.

## 2026-02-11 – UI-Iteration: Neues Theme „blau“ + sichere Theme-Validierung
- **Was:** `app/main.py` bietet jetzt zusätzlich das Farbschema „blau“, validiert die Theme-Auswahl strikt und zeigt bei ungültiger Auswahl einen klaren Fehlerdialog mit Next Steps.
- **Warum:** Die Oberfläche sollte näher an die gewünschte Farbvielfalt aus dem Zielbild kommen, ohne instabile oder ungültige Theme-Zustände zu speichern.
- **Wirkung:** Mehr Theme-Auswahl mit gutem Kontrast, robustere Eingabeprüfung und verständlichere Hilfe bei falscher Auswahl.

## 2026-02-11 – Start-Iteration: sudo-Fallback mit klaren Next Steps ergänzt
- **Was:** `start.sh` nutzt jetzt eine zentrale Funktion `run_with_sudo`, die vor System-Reparaturen `sudo`-Verfügbarkeit und Berechtigung prüft und verständliche Hilfe ausgibt.
- **Warum:** In eingeschränkten Umgebungen schlugen apt-Reparaturen bisher ohne klare Ursache fehl oder endeten nur mit technischen Fehltexten.
- **Wirkung:** Nutzer:innen sehen sofort, warum eine Auto-Reparatur nicht lief, und erhalten direkt den nächsten einfachen Schritt inklusive Log-Hinweis.

## 2026-02-11 – Doku-Iteration: Transparente Lückenliste zum Zielbild ergänzt
- **Was:** `README.md` zeigt den Status jetzt ehrlich mit offenen UX-Funktionen (Zielbild, Button-only, Dashboard-Statistik, Ordnervorlagen) und erklärt den Unterschied zwischen stabilem Kernpfad und geplanter Komfortoberfläche.
- **Warum:** Die Rückfrage „Warum fehlt das alles noch?“ sollte direkt im Projekt verständlich beantwortet werden, statt implizit „fertig“ zu signalisieren.
- **Wirkung:** Nutzer:innen sehen sofort, welche Funktionen bereits robust implementiert sind und welche als nächste Iterationen konkret folgen.

## 2026-02-11 – UI-Iteration: Einheitliche Mini-Hilfe in Fehlerfenstern
- **Was:** `app/main.py` nutzt jetzt einen zentralen Fehlerdialog-Helper mit den zwei Pflichtzeilen „Was ist passiert?“ und „Was kann ich jetzt klicken?“ für zentrale Fehlerfälle.
- **Warum:** Die Fehlerführung sollte in jedem betroffenen Fehlerfenster gleich, barrierearm und sofort verständlich sein.
- **Wirkung:** Nutzer:innen erhalten konsistente Next Steps direkt im Dialog und finden schneller die passende Aktion.

## 2026-02-11 – Executor-Iteration: Zentrale Validierung in Ausführung und Undo abgeschlossen
- **Was:** `core/executor.py` validiert jetzt `ActionPlan`/`PlanItem`, prüft Move-Output und lädt Undo-Daten strikt typisiert mit klaren Next-Step-Fehlermeldungen.
- **Warum:** Der letzte offene Release-Punkt verlangte denselben Input-/Output-Standard auch für den Ausführungs- und Undo-Pfad.
- **Wirkung:** Fehler in Move/Undo werden früher und verständlicher erkannt; beschädigte Undo-Daten führen nicht mehr zu stillen Folgefehlern.

## 2026-02-11 – UX-Iteration: Persistente Benutzereinstellungen und klarer Offline-Hinweis
- **Was:** `app/main.py` lädt den gespeicherten Download-Ordner beim Start, zeigt ihn direkt an und speichert Theme-/Text-Einstellungen jetzt sofort persistent; zusätzlich ergänzt das Dashboard einen verständlichen Offline-Hinweis.
- **Warum:** Die Anfrage verlangte verlässliche Persistenz und bessere Mobilität/Offline-Transparenz ohne zusätzlichen Klickaufwand.
- **Wirkung:** Nutzer:innen starten schneller, verlieren Einstellungen nicht zwischen Sitzungen und erhalten klare Orientierung, dass die Kernfunktion offline nutzbar bleibt.

## 2026-02-11 – Scanner-Iteration: Zentrale Validierung in Scan- und Duplikatpfad integriert
- **Was:** `core/scanner.py` validiert jetzt Eingaben (Root-Verzeichnis, Typfilter, Schwellenwerte, Modus) und prüft Ausgaben mit klaren Next-Step-Fehlern.
- **Warum:** Der Scanner sollte denselben robusten Input-/Output-Standard wie der Planner nutzen, damit Fehler früh und verständlich auffallen.
- **Wirkung:** Stabilerer Kernpfad mit einheitlichem Validierungsverhalten und laienfreundlicher Fehlerführung für Scan und Duplikaterkennung.

## 2026-02-11 – Core-Iteration: Zentrale Input-/Output-Validierung im Planner erzwungen
- **Was:** Neues Modul `core/validation.py` ergänzt und `core/planner.py` nutzt diese Helper jetzt verbindlich für Eingabetypen, Verzeichnisprüfung und Output-Konsistenzprüfung.
- **Warum:** Der offene Release-Punkt verlangte einen zentralen, technisch erzwungenen Validierungsstandard statt verteilter Einzelprüfungen.
- **Wirkung:** Planungsfehler werden früher mit klaren Next Steps in einfacher Sprache erkannt; die Kernlogik wird robuster und einheitlicher.

## 2026-02-11 – A11y-Iteration: Automatischer Theme-Check im Quality-Gate integriert
- **Was:** Neues Skript `tools/a11y_theme_check.py` prüft alle Themes automatisiert auf Mindestkontrast und sichtbare Fokus-Regeln; `tools/run_quality_checks.sh` führt diesen Check jetzt als festen Schritt aus.
- **Warum:** Der offene Release-Punkt „A11y-Checks automatisiert prüfbar machen“ sollte als kleinstes vollständiges Inkrement abgeschlossen werden.
- **Wirkung:** Kontrast- und Fokusprobleme werden früh erkannt, mit klaren Next Steps in einfacher Sprache vor dem App-Start.

## 2026-02-11 – Smoke-Iteration: Zusätzlicher Scanner-Test im Smoke-Test integriert
- **Was:** `tools/smoke_test.py` prüft jetzt zusätzlich `core.scanner` (Größen-/Altersparser, Typfilter im Scan, Safe-Duplikaterkennung und ungültiger Modus).
- **Warum:** Der offene Release-Punkt „zusätzliche automatische Tests pro Kernmodul“ sollte für `core.scanner` als nächster kleinster Schritt abgeschlossen werden.
- **Wirkung:** Scanner-Fehler werden früher erkannt, die Startroutine bleibt stabiler und gibt klarere Qualitätssignale vor dem GUI-Start.

## 2026-02-10 – Smoke-Iteration: Zusätzlicher Planner-Test im Smoke-Test integriert
- **Was:** `tools/smoke_test.py` prüft jetzt zusätzlich die Planungslogik (`build_plan`) inkl. Duplikat-Kennzeichnung, relativem Zielpfad und `summary()`-Ergebnissen.
- **Warum:** Der offene Release-Punkt „zusätzliche automatische Tests pro Kernmodul“ wurde für das Modul `core.planner` konkret weiter reduziert.
- **Wirkung:** Frühere Erkennung von Planungsfehlern ohne GUI-Start und damit stabilerer Qualitätslauf in der Startroutine.


## 2026-02-10 – Quality-Iteration: Smoke-Test ohne Ruff-E402-Sonderregel
- **Was:** `tools/smoke_test.py` entfernt die Datei-Sonderregel `# ruff: noqa: E402` und nutzt stattdessen einen `main()`-Ablauf mit verzögerten Imports via `importlib`.
- **Warum:** Der offene Qualitätspunkt verlangte regelkonformen Importfluss ohne globale Sonderausnahmen.
- **Wirkung:** Lint-Regeln bleiben strikt aktiv, der Smoke-Test bleibt robust und liefert weiter verständliche Fehlermeldungen in einfacher Sprache.

## 2026-02-10 – Qualitäts-Iteration: Auto-Fix bei Warnungen direkt im Quality-Gate
- **Was:** `tools/run_quality_checks.sh` startet bei Warnungen jetzt automatisch Black/Isort/Ruff-Fixläufe (steuerbar über `AUTO_FIX_ON_WARN`) und validiert danach erneut.
- **Warum:** Nutzer:innen sollten nicht erst manuell `AUTO_FIX=1` nachstarten müssen, wenn die Korrektur sofort möglich ist.
- **Wirkung:** Schnellere, barrierearme Qualitätssicherung mit klaren Next-Step-Meldungen, wenn nach Auto-Fix noch Restprobleme bleiben.

# CHANGELOG

## 2026-02-10 – Doku-Iteration: Release-Lücken im README klar sichtbar
- **Was:** README-Statusblock ergänzt um explizite Listen „Abgeschlossen“ und „Offen (für perfekte Release-Version)“.
- **Warum:** Die offene Frage „was fehlt noch“ sollte sofort oben im Projekt in einfacher Sprache beantwortet werden.
- **Wirkung:** Release-Reifegrad ist transparent; nächste Arbeitsschritte sind ohne Suche direkt sichtbar.

## 2026-02-10 – Prozess-Iteration: README-Fortschrittspflicht in AGENTS verbindlich gemacht
- **Was:** `AGENTS.md` um eine Pflichtsektion ergänzt: README muss pro Iteration oben exakte Prozentzahl plus Listen für „Abgeschlossen“ und „Offen“ enthalten und aktualisiert werden.
- **Warum:** Die neue Teamvorgabe verlangt transparenten Fortschritt mit klarer Sicht auf erledigte und offene Punkte in jeder Iteration.
- **Wirkung:** Künftige Iterationen dokumentieren den Entwicklungsstand konsistent, nachvollziehbar und ohne Interpretationsspielraum.

## 2026-02-10 – UI-Iteration: Light-Theme mit klarerer Hierarchie und besserer Lesbarkeit
- **Was:** Den `light`-Stylesheet-Block in `app/main.py` gezielt überarbeitet (ruhigerer Seitenhintergrund, stärkere Rahmen, größere Klickflächen, deutlicher Fokusrahmen).
- **Warum:** Auf die Frage nach Design-/Layout-Verbesserung sollte das helle Design sichtbarer strukturiert und für Tastatur-/Sehhilfe besser erkennbar werden.
- **Wirkung:** Einheitlicheres Layout im hellen Modus mit besserem Kontrastverhalten und klarerer Orientierung bei Navigation und Auswahl.

## 2026-02-10 – Standards-Iteration: Manifestvorgaben für Qualität und Barrierefreiheit ergänzt
- **Was:** Neue Datei `data/standards_manifest.json` ergänzt, die verbindliche Standards für einfache Sprache, Accessibility-Defaults, Qualitäts-Gates, Auto-Start-Feedback und Validierungsregeln zentral festlegt.
- **Warum:** Bisher fehlte eine maschinenlesbare Referenzdatei für einheitliche Vorgaben, wodurch Standards schwerer reproduzierbar und weniger robust überprüfbar waren.
- **Wirkung:** Team und Startroutine erhalten eine klare, strukturierte Soll-Vorgabe für konsistente Qualität, bessere Zugänglichkeit und nachvollziehbare nächste Automatisierungsschritte.

## 2026-02-10 – UI-Iteration: Optionen visuell in klare Referenz-Abschnitte gegliedert
- **Was:** `app/main.py` strukturiert die Optionen-Seite neu mit klar nummerierten Bereichen (Preset, Dateitypen, Grenzen, Duplikate), ergänzenden Hilfetexten und größeren Primär-Buttons.
- **Warum:** Das Design sollte näher an ein vorgegebenes, klar gegliedertes Referenzbild rücken und gleichzeitig für Laien leichter erfassbar sein.
- **Wirkung:** Bessere visuelle Orientierung, klarere Schrittfolge und verbesserte Bedienbarkeit durch größere Klickflächen und einfache Sprache.

## 2026-02-10 – UI-Iteration: Dunkles Referenz-Layout mit besserer Fokusführung
- **Was:** `app/main.py` aktualisiert den Theme-Stylesheet-Block für `dark` und `kontrast` mit panelähnlicher Farbwelt, klaren Button-Hierarchien, größeren Klickflächen und sichtbaren Fokusrahmen für Tastatur-Navigation.
- **Warum:** Das GUI sollte visuell näher an das vorgegebene Originalbild heranrücken und gleichzeitig barriereärmer bedienbar werden.
- **Wirkung:** Einheitlicheres, kontraststarkes Erscheinungsbild im Dark-Design und deutlich bessere Orientierung für Nutzer:innen mit Tastatur oder Seh-Einschränkungen.

## 2026-02-10 – UI-Iteration: Barrierearme Einstiegshilfe und moderne Bedienhinweise
- **Was:** `app/main.py` erweitert die Startseite um klare Einstiegshilfe, zusätzlichen Hilfebereich, bessere Tooltips und Accessibility-Namen/-Beschreibungen für zentrale Bedienelemente.
- **Warum:** Der Einstieg sollte für Laien verständlicher werden und Screenreader/Keyboard-Bedienung bessere Orientierung bieten.
- **Wirkung:** Moderneres, klareres Layout mit verbessertem Kontrast-/Lesefluss und direkter Hilfe für den nächsten Schritt ohne Fachwissen.

## 2026-02-10 – Qualitäts-Iteration: Kernmodul-Checks im Smoke-Test ergänzt
- **Was:** `tools/smoke_test.py` prüft jetzt zusätzlich `core.settings` mit einem temporären Testlauf für Laden/Speichern inkl. Schema- und Revisions-Validierung.
- **Warum:** Offener Punkt aus `todo.txt`: Kernmodule sollten automatisiert im Qualitätslauf sichtbar geprüft werden.
- **Wirkung:** Frühere Fehlererkennung bei Konfigurations-Import/Export, klarere Nutzerhilfe bei Defekten und robustere Qualitätsaussage ohne manuellen Aufwand.

## 2026-02-10 – Qualitäts-Iteration: Fehlende Formatter/Linter mit klarer Hilfe markieren
- **Was:** `tools/run_quality_checks.sh` behandelt fehlende Tools (`black`, `isort`, `ruff`) jetzt als Warnung mit klarer Installationsanleitung (`python3 -m pip install <tool>`), statt sie still zu überspringen.
- **Warum:** Für einen verlässlichen Release-Status muss sichtbar sein, wenn ein Pflicht-Check mangels Abhängigkeit nicht ausgeführt wurde.
- **Wirkung:** Bessere Nutzerführung in einfacher Sprache, klarer Next-Step für Auto-Nachrüstung und höhere Barrierefreiheit durch verständliche Fehlerrückmeldung.

## 2026-02-10 – Release-Iteration: Offene Punkte quantifiziert und finales Tracking vereinheitlicht
- **Was:** `RELEASE_CHECKLIST.md` neu eingeführt und mit Prozentfortschritt, Anzahl offener/abgeschlossener Punkte sowie nächstem Schritt befüllt; README, AGENTS.md und Entwicklerdoku auf diesen Iterationsstatus synchronisiert.
- **Warum:** Für die Release-Finalisierung fehlte eine zentrale, pro Iteration aktualisierbare Statusquelle mit klaren Kennzahlen.
- **Wirkung:** Transparenter Entwicklungsstand (78%, 14 abgeschlossen, 4 offen), klare Priorität für die nächste Mini-Iteration und einheitlicher Release-Ablauf für Team und Support.

## 2026-02-10 – Reparatur-Iteration: PySide6-Ausfall ohne Crash abgefangen
- **Was:** `tools/repair_center_gui.py` prüft jetzt PySide6 vor dem GUI-Start, versucht automatisch eine Abhängigkeitsinstallation und zeigt bei weiterem Fehlschlag eine klare Next-Step-Fehlermeldung (Zenity/Konsole) mit Protokollhinweis.
- **Warum:** Ohne PySide6 brach das Reparaturtool mit `ModuleNotFoundError` hart ab statt Hilfe anzubieten.
- **Wirkung:** Robuster Startablauf mit verständlicher Hilfe in einfacher Sprache und zusätzlichem „Protokoll öffnen“-Button für bessere Zugänglichkeit.

## 2026-02-10 – Start-Iteration: Qualitäts-Hinweis in einfacher Sprache je Warn-/Info-Lage
- **Was:** `start.sh` erzeugt nach dem Qualitätslauf jetzt einen klaren Next-Step-Hinweis abhängig von `WARN`/`INFO`-Anzahl (`Warnung zuerst beheben`, `Hinweise später umsetzen`, `keine Aktion nötig`).
- **Warum:** Die bisherige Standardmeldung war bei Warnungen zu allgemein und half nicht klar beim ersten nächsten Schritt.
- **Wirkung:** Bessere Nutzerführung in einfacher Sprache und höhere Barrierefreiheit durch kontextabhängige, verständliche Handlungsempfehlung.

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

## 2026-02-10 – Start-Iteration: Linux-Bibliotheken nach Installation verlässlich erkennen
- **Was:** `start.sh` prüft fehlende Linux-Bibliotheken jetzt robuster über `ldconfig` **und** typische Systempfade und aktualisiert den Cache nach apt-Installation mit `ldconfig`.
- **Warum:** Auf einigen Systemen wird eine gerade installierte Bibliothek im selben Lauf nicht sofort über `ldconfig -p` gefunden, wodurch unnötige Wiederhol-Reparaturen entstehen konnten.
- **Wirkung:** Die Startroutine bricht seltener ab und führt Nutzer:innen zuverlässiger ohne Endlosschleifen durch den Setup-Prozess.

## 2026-02-10 – UI-Iteration: Helles Theme mit klaren Fokusrahmen und besserem Kontrast
- **Was:** Das `light`-Theme in `app/main.py` wurde von leer auf vollständige, einheitliche Styles (Buttons, Fokus, Listen, Auswahlfarben) umgestellt.
- **Warum:** Interaktive Elemente waren im hellen Modus visuell zu zurückhaltend; Fokuszustände und Lesbarkeit sollten klarer und barriereärmer werden.
- **Wirkung:** Bessere Nutzerführung über sichtbare Hover-/Fokuszustände, konsistente Kontraste und verständlichere Bedienung mit Tastatur.

## 2026-02-11 – Prozess-Iteration: AGENTS auf Zwei-Punkte-Iteration umgestellt
- **Was:** `AGENTS.md` auf Version 2.1 angehoben und die Iterationsregel auf genau zwei vollständig abgeschlossene Punkte pro Iteration umgestellt (inkl. Scope/DoD/Planung).
- **Warum:** Der Arbeitsmodus soll pro Durchlauf nicht nur einen, sondern zwei klar abgegrenzte, merge-fähige Fortschrittspunkte erzwingen.
- **Wirkung:** Iterationen bleiben klein, aber liefern pro Merge mehr sichtbaren Fortschritt bei weiterhin klaren Qualitäts-Gates.

## 2026-02-12 – Release-Transparenz: Automatischer Lücken-Report im Quality-/Start-Flow
- **Was:** Neues Skript `tools/release_gap_report.py` ergänzt, in `tools/run_quality_checks.sh` als zusätzlicher Schritt eingebunden und in `start.sh` mit klarer Hilfe-Ausgabe verknüpft.
- **Warum:** Die Frage „Was fehlt noch für den Release?“ sollte jederzeit automatisch, konsistent und in einfacher Sprache beantwortet werden.
- **Wirkung:** Nutzer:innen sehen offene oder widersprüchliche Release-Punkte direkt mit konkretem ersten Next Step statt manueller Suche in mehreren Dateien.

## 2026-02-12 – Iteration: Validierung + stabile Reparaturhinweise
- **Was:** Neue Validierungen für Auswahlwerte und Verzeichnispfade ergänzt, Settings-Normalisierung daran gekoppelt und Start-Reparaturblock mit Modul-Importstatus erweitert.
- **Warum:** Damit Laien Fehler früher verstehen und Startprobleme schrittweise ohne Abbruch beheben können.
- **Wirkung:** Robustere Eingaben, klarere Rückmeldungen und weniger unklare Reparaturabbrüche.

## 2026-02-12 – Start/Quality-Iteration: Mini-UX-Gate fest integriert
- **Was:** `start.sh` protokolliert den Modul-Reparaturstatus jetzt auch im Fall „keine fehlenden Module“ mit Kompaktblock; neues Skript `tools/mini_ux_gate.py`; `tools/run_quality_checks.sh` ergänzt festen Schritt 10/11 für das Mini-UX-Gate.
- **Warum:** Der Mini-UX-Gate aus den Standards sollte technisch verbindlich automatisiert laufen und bei allen Startzuständen nachvollziehbar protokolliert sein.
- **Wirkung:** Bessere Nachvollziehbarkeit im Setup-Log, frühere UX-/A11y-Hinweise und klarere Next Steps im Qualitätslauf.

## 2026-02-12 – Start-Iteration: Vorprüfung + Auto-Format im Startfluss
- **Was:** `start.sh` ergänzt eine feste Vorprüfung für Pflichtdateien, einen validierten Schalter `ENABLE_AUTO_FORMAT` (0/1) und einen automatischen Format-Schritt vor dem Qualitäts-Gate.
- **Warum:** Startabbrüche durch fehlende Basisdateien oder uneinheitliche Formatstände sollten früh, verständlich und mit klaren Befehlen abgefangen werden.
- **Wirkung:** Stabilerer Start, konsistentere Codebasis und bessere Nutzerführung durch klare Next Steps in einfacher Sprache.
