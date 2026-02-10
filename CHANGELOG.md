# CHANGELOG

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
