# Benutzerhandbuch – Provoware Clean Tool 2026

Dieses Handbuch erklärt die Bedienung des **Provoware Clean Tool 2026** Schritt für Schritt in einfacher deutscher Sprache. Das Programm hilft Ihnen dabei, den Ordner **Downloads** sicher aufzuräumen, ohne Dateien ungewollt zu löschen. Alle Oberflächenelemente sind barrierearm gestaltet: hohe Kontraste, sichtbare Fokusrahmen, große Schaltflächen und klare Sprache.

## 1) Starten des Programms

Sie können das Werkzeug direkt über eine Shell oder per Doppelklick starten:

1. **Im Terminal:** Öffnen Sie ein Terminalfenster und wechseln Sie in das Verzeichnis des Tools. Geben Sie danach
   ```bash
   bash start.sh
   ```
   ein. Das Skript prüft automatisch, ob alle benötigten Module vorhanden sind, erstellt bei Bedarf eine virtuelle Umgebung und führt Qualitätsprüfungen aus. Anschließend startet das grafische Hauptfenster.
2. **Per AppImage (nach dem finalen Release):** In der fertigen Version finden Sie eine Datei `ProvowareCleanTool2026.AppImage` im Verzeichnis `dist/`. Machen Sie die Datei ausführbar (`chmod +x ProvowareCleanTool2026.AppImage`) und doppelklicken Sie sie. Das Programm öffnet sich ohne weitere Installation.

Sollte der Startprozess Fehler melden, lesen Sie die angezeigten Hinweise sorgfältig. Das Programm schlägt stets 1–3 konkrete nächste Schritte vor (z. B. „Erneut versuchen“, „Reparatur starten“ oder „Log öffnen“). Weitere Details finden Sie in den Logdateien im Unterordner `logs/`.

## 2) Aufbau der Benutzeroberfläche

Nach dem Start sehen Sie eine moderne Oberfläche mit dunklem Hintergrund und leuchtenden Akzenten („Soft‑Neon‑Design“). Das Hauptfenster ist in vier Bereiche gegliedert:

1. **Linke Leiste:** Symbole für Grundaktionen und Einstellungen. Der aktive Bereich ist farblich hervorgehoben. Nutzen Sie die Tab‑Taste, um durch die Symbole zu navigieren; drücken Sie Enter, um einen Bereich zu öffnen.
2. **Karten‑Raster („Schnellstart“):** In der Mitte finden Sie große, farbige Karten für typische Aktionen (nur Bilder scannen, nur Dokumente, nach Duplikaten suchen …). Jede Karte zeigt eine kurze Erklärung. Betätigen Sie die Leertaste oder Enter, um eine Aktion zu wählen. Mit der Tabulator‑Taste springen Sie zur nächsten Karte.
3. **Rechte Spalte:** Hier befinden sich Zusatzinformationen wie Profil, Verlauf und optionale Analyse‑Werkzeuge. Dieser Bereich passt sich automatisch der Fenstergröße an.
4. **Unterer Abschnitt:** Breite Übersicht mit Diagrammen oder Listen, die den Fortschritt und das Ergebnis einer Analyse darstellen.

Alle interaktiven Elemente verfügen über verständliche Beschriftungen (Accessible‑Namen) und sind per Tastatur erreichbar. Fokusrahmen machen sichtbar, welches Element gerade ausgewählt ist.

## 3) Typischer Arbeitsablauf

1. **Aktion wählen:** Wählen Sie zunächst eine Schnellstart‑Karte (z. B. „Nur Bilder scannen“). In der Entwickleransicht können Sie über das Menü auch eigene Voreinstellungen erstellen.
2. **Scannen:** Das Programm durchsucht den Download‑Ordner nach passenden Dateien. Der Fortschritt wird in der unteren Karte angezeigt.
3. **Plan einsehen:** Nach dem Scan erstellt das Tool einen Plan. Sie sehen, welche Dateien wohin verschoben würden (z. B. in Unterordner wie `Downloads/Bilder/`). Nichts wird ohne Ihre Zustimmung verschoben.
4. **Aufräumen:** Wenn der Plan sinnvoll aussieht, klicken Sie auf „Aufräumen“. Die Dateien werden verschoben. Ein Protokoll wird erstellt. Sie können jeden Schritt über die Undo‑Funktion rückgängig machen.
5. **Undo/History:** Unter „Verlauf“ können Sie frühere Aufräumaktionen einsehen und bei Bedarf rückgängig machen. Das Tool löscht keine Dateien endgültig.

## 4) Themes und Darstellung anpassen

Im Menü „Einstellungen“ können Sie zwischen verschiedenen Themen wählen:

| Tastenkürzel | Theme | Beschreibung |
|--------------|-------|--------------|
| **Alt + 1**  | **dunkel** | Klassisches dunkles Theme mit hoher Lesbarkeit |
| **Alt + 3**  | **neon**   | Soft‑Neon‑Design mit leuchtenden Blau/Violett/Rottönen |
| **Alt + 5**  | **kontrast** | Besonders kontrastreiches Theme für sehschwache Personen |
| **Alt + 4**  | **senior** | Größere Schrift und großzügige Abstände |

Jedes Theme wurde mit dem automatischen A11y‑Check überprüft. Sollten die Farben zu grell sein, wechseln Sie einfach auf das Senior‑ oder Kontrast‑Theme. Über das Auswahlfeld „Vorschaugröße“ können Sie die Darstellung (Auto/80 %/60 %/40 %) an Ihre Bildschirmgröße anpassen. Die Live‑Vorschau zeigt, wie Buttons und Listen im gewählten Theme aussehen.

## 5) Barrierefreiheit und Tastaturbedienung

- **Kontraste:** Alle Texte erfüllen die empfohlenen WCAG‑Kontrastverhältnisse. Der A11y‑Theme‑Check (`python tools/a11y_theme_check.py`) prüft dies automatisch【802954798247748†L40-L47】.
- **Tastaturfokus:** Jeder Button und jedes Eingabefeld hat einen sichtbaren Fokusrahmen. Navigieren Sie mit der Tab‑Taste, bestätigen Sie mit Enter.
- **Senior‑Modus:** Größere Schrift, größere Schaltflächen und mehr Abstand helfen Menschen mit Sehschwäche. Aktivieren Sie den Senior‑Modus über Alt + 4.
- **Hilfefenster:** Klicken Sie auf „Hilfe“ oder drücken Sie F1, um ein Hilfefenster mit kurzen Erklärungen zu öffnen. Fehlermeldungen enthalten immer konkrete nächste Schritte.

## 6) Fehlertoleranz und Sicherheit

- **Keine Löschungen:** Das Tool verschiebt Dateien nur. Nichts wird dauerhaft gelöscht. Wenn etwas schiefgeht, können Sie über „Undo“ jeden Schritt rückgängig machen.
- **Automatische Reparatur:** Die Start‑Routine versucht, fehlende Module zu installieren und Rechteprobleme zu korrigieren. Bei Fehlern wird ein klarer Hilfetext angezeigt.
- **Protokolle:** Alle Aktionen werden in `logs/` festgehalten. Prüfen Sie `exports/setup_log.txt` und `logs/app.log`, wenn Sie Hilfe benötigen.
- **Versionierung:** Intern wird jede Datei des Projekts versioniert. Änderungen sind nachvollziehbar und können bei Bedarf zurückgerollt werden.

## 7) Weitere Tipps

1. **Auf dem Laufenden bleiben:** Führen Sie nach Updates zuerst `bash start.sh` aus und lesen Sie dann die Startzusammenfassung. Dort finden Sie Hinweise, ob weitere Schritte nötig sind.
2. **Qualitätsprüfung manuell starten:** Mit
   ```bash
   bash tools/run_quality_checks.sh
   ```
   prüfen Sie jederzeit, ob das Projekt alle internen Qualitätskriterien erfüllt. Der Bericht gibt klare Hinweise in Alltagssprache.
3. **Debug‑Modus aktivieren:** Setzen Sie die Umgebungsvariable `DEBUG_LOG_MODE=1`, um zusätzliche technische Informationen zu erhalten (z. B. `DEBUG_LOG_MODE=1 bash start.sh`). Die normale Nutzung bleibt davon unberührt.

Dieses Handbuch wird laufend erweitert. Für technische Details wenden Sie sich an das Entwicklerhandbuch (`docs/developer_manual.md`).