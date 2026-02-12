# Projektbeschreibung in einfacher Sprache (für Laien)

## Was ist dieses Projekt?

Dieses Projekt heißt **Provoware Clean Tool**.
Es hilft beim Aufräumen vom Ordner **Downloads**.

Kurz gesagt:
- Das Tool sucht Dateien.
- Das Tool macht Vorschläge zum Sortieren.
- Das Tool verschiebt Dateien sicher (nicht sofort löschen).
- Das Tool zeigt klare Hilfe bei Fehlern.

## Für wen ist das gedacht?

Für Menschen, die:
- schnell Ordnung in Downloads wollen,
- wenig Technik-Wissen haben,
- große Buttons und klare Sprache brauchen,
- eine sichere Rückgängig-Funktion wollen.

## Was bedeutet „sicher“ hier genau?

- Dateien werden zuerst **verschoben** (move), nicht hart gelöscht.
- Es gibt eine **Rückgängig-Funktion** (Undo = letzten Schritt zurücknehmen).
- Vor dem Start laufen automatische Prüfungen.
- Bei Problemen zeigt das Tool direkte nächste Schritte.

## Was passiert beim Start automatisch?

Die Start-Routine (`start.sh`) arbeitet wie ein Autopilot:
1. Sie prüft Python und wichtige Dateien.
2. Sie installiert nötige Pakete (Abhängigkeiten) automatisch.
3. Sie startet Qualitätsprüfungen.
4. Sie führt einen Smoke-Test (Kurztest) aus.
5. Danach startet die Oberfläche.

Wenn etwas fehlt, sehen Sie eine Meldung in einfacher Sprache mit Lösungsvorschlag.

## Was sehe ich im Dashboard?

Im Dashboard sehen Sie alles auf einem Blick:
- aktiven Zielordner,
- gewähltes Preset,
- Filter,
- Speicher-Status,
- Gate-Status (Prüfstatus),
- Hilfe für den nächsten Klick.

Neu gibt es zusätzlich eine kleine **Systemgesundheit**:
- Auto-Prüfung,
- Einstellungen,
- Barrierefreiheit.

Damit sehen Sie schnell: „Alles grün“ oder „Hier zuerst reparieren“.

## Barrierefreiheit (A11y)

A11y bedeutet: **Barrierefreiheit**.
Das Projekt nutzt dafür:
- klare Kontraste,
- sichtbare Fokus-Rahmen bei Tastatur-Nutzung,
- verständliche deutsche Meldungen,
- mehrere Themes (light, dark, neon, kontrast, blau, senior).

Tipp: Bei schwieriger Lesbarkeit direkt auf **kontrast** oder **senior** wechseln.

## Typischer Ablauf in 5 Schritten

1. Tool mit `bash start.sh` starten.
2. Zielordner wählen.
3. Passendes Preset oder Schnellkachel wählen.
4. Vorschau prüfen.
5. Erst dann bestätigen.

## Häufige Fragen

### Muss ich Internet haben?
Für die normale Nutzung: meistens nein.
Für Erstinstallation von Paketen: eventuell ja.

### Kann ich etwas kaputt machen?
Das Risiko ist reduziert, weil das Tool mit Vorschau und Rückgängig arbeitet.
Trotzdem: wichtige Daten regelmäßig sichern.

### Was mache ich bei einer Warnung?
1. Hilfe-Center öffnen.
2. „Reparatur“ anklicken.
3. Log/Protokoll lesen, wenn es weiter hakt.

## Wichtige Befehle (zum Kopieren)

```bash
python -m compileall -q .
bash tools/run_quality_checks.sh
python tools/smoke_test.py
bash start.sh
```

## Zwei kurze Laienvorschläge

- Nutzen Sie zuerst den Theme-Modus **senior**, wenn Texte zu klein wirken.
- Starten Sie bei Unsicherheit immer mit einem kleinen Testordner statt mit allen Dateien.

## Nächster einfacher Schritt

Erstellen Sie als nächstes einen „Sicher testen“-Ordner mit 10 Beispiel-Dateien (Bilder, PDF, Musik) und führen Sie damit einen kompletten Probelauf durch. So lernen Sie die Oberfläche ohne Risiko kennen.
