# Release-Plan und Checkliste (Version 2026-02-12, Draft)

Dieser Plan fasst zusammen, welche Schritte bis zum finalen Release des **Provoware Clean Tool 2026** noch ausstehen. Er ist aus der Perspektive des Endzustands geschrieben, um rückwärts zu planen.

## Zielzustand

- **Fehlerfreies, benutzerfreundliches Tool:** Die Anwendung räumt den Ordner „Downloads“ zuverlässig auf, läuft stabil auf gängigen Linux-Distributionen, und die Benutzeroberfläche entspricht dem Soft-Neon-Design.
- **Barrierefreies UI:** Alle Texte erfüllen die WCAG‑Kontrastanforderungen【802954798247748†L40-L47】, Fokusrahmen sind sichtbar, und es gibt klare, einfache Hinweise zu jedem Schritt.
- **Plugin‑fähige Architektur:** Neue Funktionen (z. B. Datei‑Scanner, Export‑Module) lassen sich als Plug‑ins ergänzen. Der Kern lädt Plug‑ins dynamisch und hält sie von der Kernlogik getrennt【221412317637110†L75-L87】.
- **Zentrale Versionierung:** Jede Datei im Projekt wird in einer Versions‑Registry erfasst (`data/version_registry.json`), inklusive Status (`draft`, `review`, `done`) und Datum. Änderungen werden als neue Dateien mit Suffix `__vYYYY.MM.DD__status` eingespielt und die Registry entsprechend aktualisiert.
- **Dokumentation & Hilfen:** Es gibt eine vollständige Anwender‑Anleitung, eine Entwickler‑Dokumentation und klare Release‑Checklisten. Fehlerdialoge enthalten immer 1–3 nachvollziehbare nächste Schritte.

## Rückwärtsplanung

1. **Zippbares Release:** Am Ende liegt ein Zip‑Archiv mit der gültigen Verzeichnisstruktur vor. Eine `start.sh` oder `.desktop` Datei startet die Anwendung ohne weitere Installationsschritte. Die README erklärt den Schnellstart für Laien.
2. **Endgültige Validierung:** Vor dem Zippen sind alle Qualitäts‑Checks (`bash tools/run_quality_checks.sh`) und die Smoke‑Tests fehlerfrei, und das A11y‑Theme‑Check bestätigt die Kontraste.
3. **Dokumentationen aktualisieren:** Die README, das Entwicklerhandbuch (`docs/developer_manual.md`) und die Release‑Checkliste werden auf den finalen Stand gebracht. Das Plan‑Dokument (diese Datei) wird auf `__done` gesetzt.
4. **Versionierung anwenden:** Alle Dateien, die seit der aktuellen Iteration modifiziert wurden, werden mit Version‑Suffix benannt und in der `version_registry.json` eingetragen.
5. **Letzte Anpassungen:** Offene Aufgaben aus `todo.txt` werden bewertet. Nicht mehr relevante Punkte werden entfernt; verbleibende Punkte fließen in die nächste Iteration.

## Offene Aufgaben (kompakt)

| Bereich | Aufgabe | Ziel |
| --- | --- | --- |
| **Design** | Kartenabstände und aktiver Kartenrand gemäß Domotic‑Referenz einhalten. | Einheitliche Optik, bessere Lesbarkeit. |
| **Barrierefreiheit** | Theme‑Prüfung automatisieren (dunkel/neon/kontrast durchschalten). | Sicherstellen, dass alle Themes klare Texte liefern. |
| **Plugin‑System** | Grundstruktur `core/plugins.py` anlegen, Standard‑Interface definieren, dynamischen Loader implementieren. | Erweiterbarkeit ohne Kernanpassung. |
| **Versionierung** | Versions‑Registry implementieren, Suffix‑Migration vorbereiten. | Transparente Nachvollziehbarkeit aller Änderungen. |
| **Dokumentation** | Anwender‑Anleitung ergänzen: Klick‑Start‑Beschreibung, Fehlertoleranz, Hilfssystem. | Laienfreundliche, verständliche Hilfe. |
| **Bereinigung** | Alte oder redundante Dateien entfernen (z. B. `baumstruktur.txt`) und `todo.txt` entschlacken. | Aufgeräumtes Repository ohne Altlasten. |

Diese Liste wird in den nächsten Iterationen detailliert abgearbeitet und angepasst. Jede Aufgabe sollte einem Mini‑Schritt entsprechen, der in maximal 2–3 Stunden erledigt werden kann.