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

