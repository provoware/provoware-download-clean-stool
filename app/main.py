from __future__ import annotations

import json
import os
import platform
import sys
from html import escape
from pathlib import Path

# QtCore: erweitern um QUrl für Datei-URLs
from PySide6.QtCore import Qt, QUrl
# QtGui: QDesktopServices öffnet Ordner/Dateien im Dateimanager
from PySide6.QtGui import QColor, QDesktopServices, QGuiApplication
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QBoxLayout,
                               QCheckBox, QComboBox, QFileDialog, QGridLayout,
                               QHBoxLayout, QLabel, QListWidget,
                               QListWidgetItem, QMainWindow, QMenu,
                               QMessageBox, QPushButton, QScrollArea,
                               QStackedWidget, QVBoxLayout, QWidget)

from core.executor import execute_move_plan, undo_last
from core.history import append_history, clear_history, read_history
from core.logger import setup_logger
from core.planner import ActionPlan, build_plan
from core.scanner import (_parse_age, _parse_size, detect_duplicates,
                          scan_directory)
from core.selfcheck import run_selfcheck
from core.settings import Filters, Settings

LOGGER = setup_logger()


class MainWindow(QMainWindow):
    THEME_A11Y_HINTS = {
        "light": "Helles Standardschema mit guter Lesbarkeit für normale Raumbeleuchtung.",
        "dark": "Dunkles Schema für blendfreie Nutzung am Abend oder in dunklen Räumen.",
        "neon": "Soft-Neon-Schema mit dunklen Flächen, klaren Glow-Akzenten und hoher Lesbarkeit.",
        "kontrast": "Maximaler Kontrast mit sehr klaren Fokusrahmen für Sehunterstützung.",
        "blau": "Ruhiges blaues Schema mit klaren Konturen und guter Erkennbarkeit.",
        "senior": "Extra große Schrift und starke Umrandungen für ruhiges Lesen.",
    }
    THEME_INTERACTION_PROFILES = {
        "light": (
            "Sehr gut",
            "Kontrastwert 4.8/5 – klare Flächen und ruhige Standardbedienung.",
            "Für längere Arbeit: Bei Bedarf 'Großer Text' einschalten.",
        ),
        "dark": (
            "Gut",
            "Kontrastwert 4.5/5 – blendarm mit klaren Fokusrahmen.",
            "Für maximale Lesbarkeit: Schnellwahl 'Kontrast' testen.",
        ),
        "neon": (
            "Sehr gut",
            "Kontrastwert 4.7/5 – dunkler Soft-Neon-Look mit ruhigen Kanten und klaren Akzenten.",
            "Für empfindliche Augen: Bei Bedarf auf 'Senior' oder 'Kontrast' wechseln.",
        ),
        "kontrast": (
            "Maximal",
            "Kontrastwert 5.0/5 – höchste Sichtbarkeit für Text und Fokus.",
            "Wenn Farben zu stark wirken: Schnellwahl 'Senior' für ruhigere Flächen nutzen.",
        ),
        "blau": (
            "Sehr gut",
            "Kontrastwert 4.7/5 – ruhige Blautöne mit klaren Konturen.",
            "Bei kleinen Bildschirmen: Vorschau auf 'Untereinander' stellen.",
        ),
        "senior": (
            "Maximal",
            "Kontrastwert 4.9/5 – große Schrift und kräftige Umrandungen.",
            "Für schnelle Bedienung: Mit Alt+K direkt den Lesbarkeitsmodus aktivieren.",
        ),
    }
    DESIGN_SIMILARITY_TARGETS = {
        "light": {"contrast": 4.8, "layout": "Aktion links · Liste rechts"},
        "dark": {"contrast": 4.7, "layout": "Liste links · Aktion rechts"},
        "neon": {"contrast": 4.7, "layout": "Aktion links · Liste rechts"},
        "kontrast": {"contrast": 5.0, "layout": "Untereinander"},
        "blau": {"contrast": 4.7, "layout": "Aktion links · Liste rechts"},
        "senior": {"contrast": 4.9, "layout": "Untereinander"},
    }
    GLOBAL_A11Y_STYLE = """
        QPushButton:focus,
        QComboBox:focus,
        QListWidget:focus,
        QCheckBox:focus {
            outline: 3px solid #f59e0b;
            outline-offset: 2px;
        }
        QPushButton:disabled {
            background-color: #dbe3ef;
            color: #1f2937;
            border: 2px solid #4b5563;
            opacity: 1;
        }
        QCheckBox::indicator {
            width: 22px;
            height: 22px;
        }
        QListWidget::item:selected {
            background-color: #1d4ed8;
            color: #ffffff;
        }
        QComboBox QAbstractItemView {
            selection-background-color: #1d4ed8;
            selection-color: #ffffff;
        }
        QScrollArea {
            border: 1px solid #6b7280;
            border-radius: 10px;
            background: transparent;
        }
        QScrollBar:vertical {
            width: 28px;
            background: #dbe3ef;
            margin: 4px;
            border-radius: 12px;
        }
        QScrollBar::handle:vertical {
            min-height: 64px;
            background: #1d4ed8;
            border-radius: 12px;
            border: 3px solid #93c5fd;
        }
        QScrollBar:horizontal {
            height: 28px;
            background: #dbe3ef;
            margin: 4px;
            border-radius: 12px;
        }
        QScrollBar::handle:horizontal {
            min-width: 64px;
            background: #1d4ed8;
            border-radius: 12px;
            border: 3px solid #93c5fd;
        }
        QScrollBar::add-line,
        QScrollBar::sub-line {
            width: 0px;
            height: 0px;
        }
        QPushButton[quickTile="true"] {
            /* Karten im Schnellstart-Raster orientieren sich an der Domotic-Referenz:
               1px Rahmen in dezenter Farbe, große Radien, großzügiges Padding. */
            border-width: 1px;
            border-color: #4b6698;
            border-radius: 12px;
            padding: 12px 14px;
            min-height: 96px;
            text-align: left;
            background-color: #1b3362;
            color: #ffffff;
        }
        QPushButton[quickTile="true"]:hover {
            border-color: #61e1ff;
            background-color: #213f70;
        }
        QPushButton[quickTile="true"][quickSection="medien"] {
            border-color: #61e1ff;
        }
        QPushButton[quickTile="true"][quickSection="aufräumen"] {
            border-color: #7ec9ff;
        }
        QSizeGrip {
            width: 34px;
            height: 34px;
        }
    """
    GRAPHICS_IMPROVEMENT_TIPS = [
        "1) Fokus sichtbar halten: nutzen Sie gut erkennbare Ränder für Tastatur-Nutzung.",
        "2) Textblöcke entzerren: mehr Abstand zwischen Karten, damit Inhalte schneller erfasst werden.",
        "3) Farben absichern: prüfen Sie Theme-Kontrast immer mit Hell/Dunkel/Kontrast.",
        "4) Status vereinheitlichen: dieselben Symbole (✅ ⚠️) in allen grafischen Bereichen zeigen.",
    ]
    EXPERIENCE_MODES = {
        "Laien-Modus (empfohlen)": "beginner",
        "Entwickler-Modus (Tool-Bibel)": "developer",
    }
    TOOL_BIBLE_DOCS = [
        ("Entwicklerhandbuch", "docs/developer_manual.md"),
        ("Agenten-Regeln", "AGENTS.md"),
        ("Standards-Manifest", "data/standards_manifest.json"),
    ]
    QUICK_SECTION_META = {
        "Medien": {
            "badge": "🎵 Medien",
            "hint": "Ideal für Fotos, Dokumente und Musik.",
            "accent": "#2563eb",
        },
        "Aufräumen": {
            "badge": "🧹 Aufräumen",
            "hint": "Ideal für große Dateien, Duplikate und Komplettlauf.",
            "accent": "#0f766e",
        },
    }

    PROJECT_STATUS_ITEMS = [
        {
            "state": "done",
            "title": "Robuste Start-Routine",
            "detail": "Start prüft Voraussetzungen automatisch und zeigt klare Rückmeldungen.",
        },
        {
            "state": "done",
            "title": "Mehrere Lesbarkeits-Themes",
            "detail": "Farbthemen mit Kontrast-Hinweisen sind direkt auswählbar.",
        },
        {
            "state": "done",
            "title": "Dateigröße als Sortier-Filter",
            "detail": "Trefferliste lässt sich jetzt nach Name oder Größe sortieren.",
        },
        {
            "state": "open",
            "title": "Schnelltasten pro Zielordner",
            "detail": "Aktionen wie 'In Bilder verschieben' sollen direkt neben Treffern erscheinen.",
        },
    ]
    DASHBOARD_QUICK_HEALTH = [
        {
            "icon": "🧪",
            "title": "Auto-Prüfung",
            "value": "G1–G4 im Startlauf aktiv",
            "next_step": "Bei Warnsymbol 'start.sh' erneut starten und Hilfezeile lesen.",
        },
        {
            "icon": "💾",
            "title": "Einstellungen",
            "value": "Speichern mit Live-Status",
            "next_step": "Wenn ❌ erscheint: Button 'Einstellungen speichern' erneut klicken.",
        },
        {
            "icon": "♿",
            "title": "Barrierefreiheit",
            "value": "Themes mit Kontrast-Hinweis",
            "next_step": "Bei schlechter Lesbarkeit auf 'kontrast' oder 'senior' umstellen.",
        },
    ]

    def _show_error_with_mini_help(
        self,
        *,
        title: str,
        happened_text: str,
        next_clicks: list[str],
        buttons: list[tuple[str, QMessageBox.ButtonRole]] | None = None,
    ) -> str | None:
        """Zeigt ein barrierearmes Fehlerfenster mit Mini-Hilfe und gibt den geklickten Button-Text zurück."""

        clean_title = title.strip()
        clean_happened_text = happened_text.strip()
        clean_next_clicks = [entry.strip() for entry in next_clicks if entry.strip()]
        if not clean_title:
            raise ValueError(
                "Fehlertitel fehlt. Nächster Schritt: Bitte einen klaren Titel setzen."
            )
        if not clean_happened_text:
            raise ValueError(
                "Fehlerbeschreibung fehlt. Nächster Schritt: Bitte kurz erklären, was passiert ist."
            )
        if not clean_next_clicks:
            raise ValueError(
                "Mini-Hilfe fehlt. Nächster Schritt: Mindestens eine klickbare Option ergänzen."
            )

        message = QMessageBox(self)
        message.setWindowTitle(clean_title)
        message.setIcon(QMessageBox.Warning)
        message.setText(
            "<b>Was ist passiert?</b><br/>"
            f"{clean_happened_text}<br/><br/>"
            "<b>Was kann ich jetzt klicken?</b>"
        )
        message.setInformativeText(
            "\n".join(f"• {entry}" for entry in clean_next_clicks)
        )
        message.setAccessibleName(f"Fehlerdialog: {clean_title}")
        message.setAccessibleDescription(
            "Fehlerdialog mit Mini-Hilfe: Was ist passiert und welche Klicks jetzt sinnvoll sind"
        )

        added_buttons: dict[QPushButton, str] = {}
        if buttons:
            for text, role in buttons:
                if text.strip():
                    button = message.addButton(text.strip(), role)
                    added_buttons[button] = text.strip()
        if not added_buttons:
            ok_button = message.addButton("OK", QMessageBox.AcceptRole)
            added_buttons[ok_button] = "OK"

        message.exec()
        clicked = message.clickedButton()
        clicked_text = added_buttons.get(clicked)
        if clicked is not None and clicked_text is None:
            raise RuntimeError(
                "Unbekannter Dialog-Button. Nächster Schritt: Dialog-Konfiguration prüfen."
            )
        return clicked_text

    def _build_graphics_improvement_text(self) -> str:
        """Liefert eine kurze, laienfreundliche Checkliste für visuelle Verbesserungen."""

        tips = [tip.strip() for tip in self.GRAPHICS_IMPROVEMENT_TIPS if tip.strip()]
        if len(tips) < 3:
            raise ValueError(
                "Grafik-Hilfe unvollständig. Nächster Schritt: Mindestens drei konkrete Tipps ergänzen."
            )
        result = (
            "<b>Was kann an den grafischen Elementen noch verbessert werden?</b><br/>"
        )
        result += "<br/>".join(f"• {escape(tip)}" for tip in tips)
        if "•" not in result:
            raise RuntimeError(
                "Grafik-Hilfe konnte nicht aufgebaut werden. Nächster Schritt: Tipps prüfen und erneut öffnen."
            )
        return result

    def _get_project_status_entries(self) -> list[dict[str, str]]:
        """Liefert validierte Status-Einträge für den Hilfebereich 'Implementiert vs. Geplant'."""

        entries: list[dict[str, str]] = []
        for raw_entry in self.PROJECT_STATUS_ITEMS:
            state = str(raw_entry.get("state", "")).strip()
            title = str(raw_entry.get("title", "")).strip()
            detail = str(raw_entry.get("detail", "")).strip()
            if state not in {"done", "open"}:
                raise ValueError(
                    "Statuswert ist ungültig. Nächster Schritt: Nur 'done' oder 'open' verwenden."
                )
            if not title or not detail:
                raise ValueError(
                    "Status-Hilfe ist unvollständig. Nächster Schritt: Titel und Erklärung ergänzen."
                )
            entries.append({"state": state, "title": title, "detail": detail})

        if not entries:
            raise RuntimeError(
                "Status-Hilfe leer. Nächster Schritt: Mindestens einen Punkt als done/open eintragen."
            )
        return entries

    @staticmethod
    def _format_project_status_entry(entry: dict[str, str]) -> str:
        """Formatiert einen Status-Eintrag für die Anzeige mit klaren Zustands-Symbolen."""

        state = entry["state"]
        if state == "done":
            return f"✅ Implementiert: {entry['title']} – {entry['detail']}"
        if state == "open":
            return f"🟡 Geplant: {entry['title']} – {entry['detail']}"
        raise ValueError(
            "Status konnte nicht formatiert werden. Nächster Schritt: Statuswerte prüfen."
        )

    def _create_quick_section_header(self, section_name: str) -> QLabel:
        """Erzeugt eine validierte Bereichsüberschrift für Schnellstart-Karten."""

        clean_section = section_name.strip()
        section_meta = self.QUICK_SECTION_META.get(clean_section)
        if section_meta is None:
            raise ValueError(
                "Schnellstart-Bereich fehlt. Nächster Schritt: 'Medien' oder 'Aufräumen' verwenden."
            )

        badge = str(section_meta.get("badge", "")).strip()
        hint = str(section_meta.get("hint", "")).strip()
        accent = str(section_meta.get("accent", "")).strip()
        if not badge or not hint or not accent:
            raise RuntimeError(
                "Bereichsüberschrift unvollständig. Nächster Schritt: Badge, Hinweis und Farbe ergänzen."
            )

        header = QLabel(
            f"<b>{escape(badge)}</b><br/><span style='color:{escape(accent)}'>{escape(hint)}</span>"
        )
        header.setAccessibleName(f"Schnellstart Bereich {clean_section}")
        header.setAccessibleDescription(
            f"Überschrift für den Bereich {clean_section} mit kurzer Orientierungshilfe"
        )
        if header.text().strip() == "":
            raise RuntimeError(
                "Bereichsüberschrift konnte nicht erstellt werden. Nächster Schritt: Eingaben prüfen und erneut öffnen."
            )
        return header

    def _build_dashboard_health_cards(self) -> str:
        """Erstellt validierte Karten für den Dashboard-Bereich 'Systemgesundheit'."""

        cards: list[str] = []
        for entry in self.DASHBOARD_QUICK_HEALTH:
            icon = str(entry.get("icon", "")).strip()
            title = str(entry.get("title", "")).strip()
            value = str(entry.get("value", "")).strip()
            next_step = str(entry.get("next_step", "")).strip()
            if not icon or not title or not value or not next_step:
                raise ValueError(
                    "Dashboard-Karte unvollständig. Nächster Schritt: Symbol, Titel, Wert und Next Step ergänzen."
                )
            cards.append(
                "<div style='background:#111d33;border:1px solid #38598f;border-radius:14px;padding:8px;margin:6px 0;'>"
                f"<b>{escape(icon)} {escape(title)}</b><br/>"
                f"<span style='color:#d7e5ff'>{escape(value)}</span><br/>"
                f"<span style='color:#9fb2d8'>Nächster Klick: {escape(next_step)}</span></div>"
            )
        if len(cards) < 3:
            raise RuntimeError(
                "Zu wenige Dashboard-Karten. Nächster Schritt: Mindestens drei Gesundheitskarten definieren."
            )
        return "".join(cards)

    def _build_dashboard_role_hint(self) -> str:
        """Liefert zwei kurze Bedienpfade für Laien und Entwickler."""

        beginner_text = "<b>Laienpfad:</b> Ordner wählen → Kachel drücken → Vorschau prüfen → mit 'Weiter' bestätigen."
        developer_text = "<b>Entwicklerpfad:</b> Theme/Status prüfen → Debug-HTML öffnen → Gate-Ausgabe mit start.sh verifizieren."
        hint_block = f"{beginner_text}<br/>{developer_text}"
        if "→" not in hint_block:
            raise RuntimeError(
                "Rollen-Hinweis fehlerhaft. Nächster Schritt: Klare Schrittfolge mit Pfeilen ergänzen."
            )
        return hint_block

    def _build_quick_grid_keyboard_help(self) -> str:
        """Liefert eine kurze Tastaturhilfe für das Schnellstart-Raster."""

        entries = [
            "Navigation: Mit Tab springen Sie von Kachel zu Kachel.",
            "Start: Mit Enter oder Leertaste wird die aktive Kachel sofort ausgeführt.",
            "Sicherheit: Ergebnis immer in Schritt 3 prüfen, bevor Sie verschieben.",
        ]
        clean_entries = [entry.strip() for entry in entries if entry.strip()]
        if len(clean_entries) != 3:
            raise RuntimeError(
                "Tastaturhilfe unvollständig. Nächster Schritt: Genau drei klare Hinweise ergänzen."
            )
        help_text = "<br/>".join(f"• {escape(entry)}" for entry in clean_entries)
        if not help_text:
            raise RuntimeError(
                "Tastaturhilfe konnte nicht erstellt werden. Nächster Schritt: Hinweise erneut prüfen."
            )
        return help_text

    def _apply_project_status_filter(self, filter_mode: str) -> bool:
        """Setzt den Filter für den Hilfebereich und rendert die Ergebnisliste robust neu."""

        clean_mode = filter_mode.strip()
        if clean_mode not in {"all", "open"}:
            raise ValueError(
                "Filter ist ungültig. Nächster Schritt: Bitte 'Alle' oder 'Nur offen' verwenden."
            )

        entries = self._get_project_status_entries()
        filtered_entries = entries
        if clean_mode == "open":
            filtered_entries = [entry for entry in entries if entry["state"] == "open"]

        self.list_project_status.clear()
        for entry in filtered_entries:
            item = QListWidgetItem(self._format_project_status_entry(entry))
            item.setData(Qt.UserRole, entry["state"])
            self.list_project_status.addItem(item)

        if clean_mode == "open" and self.list_project_status.count() == 0:
            raise RuntimeError(
                "Filter 'Nur offen' zeigt keine Punkte. Nächster Schritt: Mindestens einen offenen Punkt pflegen."
            )

        total = len(entries)
        open_count = len([entry for entry in entries if entry["state"] == "open"])
        mode_label = "Alle" if clean_mode == "all" else "Nur offen"
        self.lbl_project_status_summary.setText(
            "<b>Status-Hilfe:</b> "
            f"Filter: {mode_label} | Sichtbar: {self.list_project_status.count()} von {total} | Offen gesamt: {open_count}"
        )
        return self.list_project_status.count() > 0

    def _show_general_help(self) -> None:
        """Zeigt eine kurze Kurzanleitung in deutscher Sprache.

        Diese Anleitung erklärt die vier Hauptschritte des Programms
        (Ordner wählen, Scannen, Vorschau, Aufräumen) sowie den Einsatz der
        Schnellstart-Karten. Das Dialogfenster ist barrierearm gestaltet.
        """
        # Die Meldung verwendet HTML zur Strukturierung, bleibt jedoch kurz und verständlich.
        # Greife zunächst auf den zentralen Textkatalog zurück (falls vorhanden),
        # andernfalls wird ein fester Standardtext verwendet. So können Texte später
        # leicht angepasst werden, ohne den Code zu ändern.
        help_text = self.ui_texts.get(
            "kurzanleitung",
            (
                "<b>Kurzanleitung:</b><br/>"
                "1) Ordner wählen.<br/>"
                "2) Scannen drücken.<br/>"
                "3) Vorschau prüfen.<br/>"
                "4) Aufräumen starten.<br/>"
                "Nutzen Sie die Aktionskarten auf der Startseite für typische Aufgaben."
            ),
        )
        message = QMessageBox(self)
        message.setIcon(QMessageBox.Information)
        message.setWindowTitle("Hilfe")
        message.setTextFormat(Qt.RichText)
        message.setText(help_text)
        message.setAccessibleName("Hilfe-Dialog")
        message.setAccessibleDescription(
            "Dialogfenster mit einer kurzen Anleitung zur Nutzung des Programms"
        )
        message.exec()

    def _build_gate_status_html(self) -> str:
        """Erstellt eine kompakte Gate-Übersicht mit verständlicher Ampelanzeige."""

        gate_specs = [
            ("G1 Syntax", "python -m compileall -q .", Path("exports/setup_log.txt")),
            (
                "G2 Qualität",
                "bash tools/run_quality_checks.sh",
                Path("exports/quality_report.txt"),
            ),
            ("G3 Smoke", "python tools/smoke_test.py", Path("tools/smoke_test.py")),
            ("G4 Start", "bash start.sh", Path("start.sh")),
        ]
        rows: list[str] = []
        for gate_name, gate_command, probe_path in gate_specs:
            probe_exists = probe_path.exists()
            icon = "✅" if probe_exists else "⚠️"
            state = "bereit" if probe_exists else "bitte ausführen"
            rows.append(
                f"• {icon} <b>{escape(gate_name)}:</b> {escape(state)}<br/>"
                f"&nbsp;&nbsp;&nbsp;&nbsp;Befehl: <code>{escape(gate_command)}</code>"
            )

        if len(rows) != len(gate_specs):
            raise RuntimeError(
                "Gate-Übersicht unvollständig. Nächster Schritt: Gate-Liste prüfen und erneut laden."
            )

        return "<br/>".join(rows)

    def _build_debug_gui_snapshot_html(self, context: dict[str, str]) -> str:
        """Erstellt eine visuelle HTML-Debugansicht des aktuellen GUI-Zustands."""

        required_keys = [
            "timestamp",
            "mode",
            "theme",
            "folder",
            "dashboard_html",
            "gate_html",
        ]
        safe_context: dict[str, str] = {}
        for key in required_keys:
            value = str(context.get(key, "")).strip()
            if not value:
                raise ValueError(
                    f"Debug-HTML Kontext '{key}' fehlt. Nächster Schritt: Zustand erneut laden und Export wiederholen."
                )
            safe_context[key] = value

        status_rows = "".join(
            (
                "<li><span class='state done'>✅ Implementiert</span>"
                if entry["state"] == "done"
                else "<li><span class='state open'>🟡 Geplant</span>"
            )
            + f" <strong>{escape(entry['title'])}</strong> – {escape(entry['detail'])}</li>"
            for entry in self._get_project_status_entries()
        )
        if not status_rows.strip():
            raise RuntimeError(
                "Debug-HTML enthält keine Statuspunkte. Nächster Schritt: Projektstatus prüfen und erneut exportieren."
            )

        theme_rows = "".join(
            f"<li><strong>{escape(name)}</strong>: {escape(desc)}</li>"
            for name, desc in self.THEME_A11Y_HINTS.items()
        )
        if not theme_rows.strip():
            raise RuntimeError(
                "Theme-Hinweise fehlen. Nächster Schritt: Theme-Liste prüfen und Export erneut starten."
            )

        return (
            "<!doctype html><html lang='de'><head><meta charset='utf-8'/>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'/>"
            "<title>GUI Debug Snapshot</title>"
            "<style>body{font-family:Arial,sans-serif;margin:0;background:#0b1220;color:#e5e7eb;}"
            ".wrap{max-width:1040px;margin:0 auto;padding:20px;}"
            ".card{background:#111827;border:2px solid #3b82f6;border-radius:14px;padding:16px;margin-bottom:14px;}"
            ".state{font-weight:700;} .done{color:#34d399;} .open{color:#fbbf24;}"
            "a{color:#93c5fd;} h1,h2{margin:0 0 10px;} ul{line-height:1.6;}"
            "code{background:#1f2937;padding:2px 6px;border-radius:6px;}"
            "</style></head><body><main class='wrap'>"
            "<h1>Optischer Debug-Stand der GUI</h1>"
            f"<p><strong>Zeit:</strong> {escape(safe_context['timestamp'])}<br/>"
            f"<strong>Modus:</strong> {escape(safe_context['mode'])}<br/>"
            f"<strong>Theme:</strong> {escape(safe_context['theme'])}<br/>"
            f"<strong>Ordner:</strong> {escape(safe_context['folder'])}</p>"
            "<section class='card'><h2>Dashboard (Live-Text)</h2>"
            f"<div>{safe_context['dashboard_html']}</div></section>"
            "<section class='card'><h2>Gate-Status (G1–G4)</h2>"
            f"<div>{safe_context['gate_html']}</div></section>"
            "<section class='card'><h2>Projektstatus</h2><ul>"
            f"{status_rows}</ul></section>"
            "<section class='card'><h2>A11y-Theme-Hinweise</h2><ul>"
            f"{theme_rows}</ul><p>Hinweis: Diese Datei wird bei jedem Dashboard-Update neu geschrieben.</p></section>"
            "</main></body></html>"
        )

    def _write_debug_gui_snapshot(self) -> Path:
        """Schreibt den aktuellen GUI-Zustand in eine HTML-Debugdatei."""

        dashboard_html = getattr(self.lbl_dashboard_info, "text", lambda: "")()
        if not dashboard_html.strip():
            raise RuntimeError(
                "Dashboard-Text ist leer. Nächster Schritt: Dashboard laden und Export erneut versuchen."
            )

        mode = self.combo_experience_mode.currentText().strip()
        theme = self.settings.theme.strip()
        folder = (
            str(self.root_path) if self.root_path else "Noch kein Ordner ausgewählt"
        )
        gate_html = self._build_gate_status_html()
        snapshot_html = self._build_debug_gui_snapshot_html(
            {
                "timestamp": __import__("datetime")
                .datetime.now()
                .strftime("%Y-%m-%d %H:%M:%S"),
                "mode": mode,
                "theme": theme,
                "folder": folder,
                "dashboard_html": dashboard_html,
                "gate_html": gate_html,
            }
        )

        target = (
            Path(__file__).resolve().parent.parent / "docs" / "debugging_gui_state.html"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(snapshot_html, encoding="utf-8")
        if not target.exists() or target.stat().st_size <= 0:
            raise RuntimeError(
                "Debug-HTML konnte nicht gespeichert werden. Nächster Schritt: Schreibrechte im Projektordner prüfen."
            )
        return target

    def _open_debug_gui_snapshot(self) -> None:
        """Öffnet die zuletzt erzeugte HTML-Debugansicht für den aktuellen GUI-Stand."""

        try:
            file_path = self._write_debug_gui_snapshot()
        except Exception as exc:
            self._show_error_with_mini_help(
                title="Debug-HTML nicht verfügbar",
                happened_text=str(exc),
                next_clicks=[
                    "Erneut versuchen: Dashboard neu laden und noch einmal auf 'Debug-HTML öffnen' klicken.",
                    "Reparatur: Mit 'bash start.sh' die automatische Prüfung ausführen.",
                    "Protokoll: logs/app.log öffnen und den letzten Fehler prüfen.",
                ],
            )
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(file_path)))

    def _show_tool_bible(self) -> None:
        """Öffnet einen Dialog mit schnellen Einstiegen in die technische Tool-Bibel."""

        available_docs: list[tuple[str, Path]] = []
        for label, relative_path in self.TOOL_BIBLE_DOCS:
            clean_label = label.strip()
            if not clean_label:
                raise ValueError(
                    "Dokumentname fehlt. Nächster Schritt: Tool-Bibel-Eintrag ergänzen."
                )
            abs_path = Path(relative_path).resolve()
            if abs_path.exists():
                available_docs.append((clean_label, abs_path))

        if not available_docs:
            raise RuntimeError(
                "Tool-Bibel ist aktuell nicht verfügbar. Nächster Schritt: Dokumente prüfen und erneut öffnen."
            )

        doc_lines = [
            f"• <b>{escape(label)}:</b> {escape(str(path))}"
            for label, path in available_docs
        ]
        message = QMessageBox(self)
        message.setWindowTitle("Tool-Bibel")
        message.setIcon(QMessageBox.Information)
        message.setText(
            "<b>Entwickler-Hub:</b><br/>"
            "Hier finden Sie technische Quellen. Für Laien reicht meist der Standardmodus.<br/><br/>"
            + "<br/>".join(doc_lines)
        )
        message.setInformativeText(
            "Nächster Schritt: Mit 'Ordner öffnen' den technischen Bereich prüfen oder mit 'Schließen' normal weiterarbeiten."
        )
        btn_open = message.addButton("Ordner öffnen", QMessageBox.ActionRole)
        message.addButton("Schließen", QMessageBox.RejectRole)
        message.setAccessibleName("Tool-Bibel Dialog")
        message.setAccessibleDescription(
            "Dialog mit schnellen Links für fortgeschrittene Nutzer und Entwickler"
        )
        message.exec()

        if message.clickedButton() == btn_open:
            docs_dir = Path("docs").resolve()
            if not docs_dir.exists():
                raise RuntimeError(
                    "Dokumentenordner fehlt. Nächster Schritt: Projektstruktur prüfen und erneut öffnen."
                )
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(docs_dir)))

    def _apply_experience_mode(self, selected_mode: str) -> None:
        """Schaltet zwischen Laien- und Entwicklerbereich mit klaren Hinweisen um."""

        clean_mode = selected_mode.strip()
        mode_key = self.EXPERIENCE_MODES.get(clean_mode)
        if mode_key is None:
            raise ValueError(
                "Bedienmodus ist ungültig. Nächster Schritt: Bitte einen sichtbaren Modus auswählen."
            )

        developer_visible = mode_key == "developer"
        for widget in self.developer_widgets:
            widget.setVisible(developer_visible)

        if developer_visible:
            self.lbl_mode_hint.setText(
                "<b>Entwickler-Modus aktiv:</b> Zusätzliche Status- und Tool-Bibel-Bereiche sind sichtbar."
            )
        else:
            self.lbl_mode_hint.setText(
                "<b>Laien-Modus aktiv:</b> Es werden nur die wichtigsten Schritte angezeigt."
            )

        if self.lbl_mode_hint.text().strip() == "":
            raise RuntimeError(
                "Modus-Hinweis fehlt. Nächster Schritt: Modus erneut auswählen."
            )

    def __init__(self) -> None:
        super().__init__()
        ok, msg = run_selfcheck()
        if not ok:
            self._show_error_with_mini_help(
                title="Fehler",
                happened_text=msg,
                next_clicks=[
                    "OK: Hinweis lesen und die Start-Routine erneut ausführen.",
                    "Danach im Projektordner 'bash start.sh' starten.",
                ],
            )
            raise SystemExit(msg)
        self.settings = Settings.load()
        self.root_path = self._load_persistent_download_dir()
        self.persistence_status_icon = "✅"
        self.persistence_status_text = (
            "Einstellungen gespeichert und beim Neustart verfügbar."
        )
        self.plan: ActionPlan | None = None
        self.scan_results = []
        self.duplicates_map = {}
        # Lade zentralen Textkatalog, damit alle Hilfe- und UI‑Texte anpassbar sind.
        self.ui_texts: dict[str, str] = {}
        self._load_ui_texts()
        # Liste für Verlaufsdaten wird im Willkommensbereich initialisiert
        self.list_history: QListWidget | None = None
        # Set a clear, fully German window title for laienfreundliche Bedienung
        # Zukünftiger Name des Werkzeugs: „Provoware Clean Tool 2026“.
        self.setWindowTitle("Provoware Clean Tool 2026")
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
        self._create_pages()
        self._fit_window_to_screen()
        self.apply_theme(self.settings.theme, self.settings.large_text)
        self.statusBar().showMessage(
            "Tipp: Nutzen Sie die große Ecke unten rechts oder die großen Scrollleisten für bessere Skalierung.",
            12000,
        )

    def _fit_window_to_screen(self) -> None:
        """Passt das Fenster an die aktuelle Bildschirmgröße an, damit Inhalte erreichbar bleiben."""

        screen = QGuiApplication.primaryScreen()
        if screen is None:
            raise RuntimeError(
                "Kein Bildschirm erkannt. Nächster Schritt: Monitor prüfen und Anwendung neu starten."
            )

        available = screen.availableGeometry()
        if available.width() < 640 or available.height() < 480:
            raise RuntimeError(
                "Bildschirmauflösung ist zu klein. Nächster Schritt: Auflösung erhöhen oder externen Monitor nutzen."
            )

        target_width = max(960, min(available.width() - 24, 1440))
        target_height = max(650, min(available.height() - 24, 980))
        if target_width < 900 or target_height < 620:
            raise RuntimeError(
                "Fenstergröße konnte nicht sicher berechnet werden. Nächster Schritt: Auflösung prüfen und erneut starten."
            )

        self.resize(target_width, target_height)
        self.move(available.left() + 12, available.top() + 12)
        self.setMinimumSize(900, 620)
        self._update_scrollbar_policies_by_window_height()

    def _update_scrollbar_policies_by_window_height(self) -> None:
        """Schaltet Scrollleisten je Fensterhöhe sichtbar, damit keine Felder verloren gehen."""

        page_scrolls = [
            getattr(self, "page_welcome", None),
            getattr(self, "page_options", None),
            getattr(self, "page_scan", None),
            getattr(self, "page_plan", None),
        ]
        valid_scrolls = [
            scroll for scroll in page_scrolls if isinstance(scroll, QScrollArea)
        ]
        if len(valid_scrolls) != 4:
            raise RuntimeError(
                "Scrollbereiche fehlen. Nächster Schritt: Startseite neu laden und Layout prüfen."
            )

        compact_height = self.height() < 860
        for scroll in valid_scrolls:
            horizontal_policy = (
                Qt.ScrollBarAsNeeded if compact_height else Qt.ScrollBarAlwaysOff
            )
            vertical_policy = Qt.ScrollBarAsNeeded
            scroll.setHorizontalScrollBarPolicy(horizontal_policy)
            scroll.setVerticalScrollBarPolicy(vertical_policy)

            if scroll.verticalScrollBarPolicy() != vertical_policy:
                raise RuntimeError(
                    "Scrollleisten konnten nicht gesetzt werden. Nächster Schritt: Anwendung neu starten."
                )

    def _load_ui_texts(self) -> None:
        """
        Lädt optionale UI‑Texte aus einer zentralen JSON‑Datei im data‑Ordner.

        Der Katalog enthält HTML‑Texte (z. B. Kurzanleitung) sowie Beschriftungen
        und Tooltips für Schnellstart‑Buttons. Wird die Datei nicht gefunden oder
        ist sie fehlerhaft, wird ein leerer Katalog verwendet. Texte im Code
        fungieren dann als Fallback.
        """
        try:
            file_path = (
                Path(__file__).resolve().parent.parent / "data" / "ui_texts.json"
            )
            if file_path.exists():
                import json

                with file_path.open("r", encoding="utf-8") as f:
                    raw = json.load(f)
                    if isinstance(raw, dict):
                        self.ui_texts = raw
                        return
            # falls Datei nicht existiert, leeres dict
            self.ui_texts = {}
        except Exception:
            # bei Fehlern wird der Katalog geleert, damit der Fallback greift
            self.ui_texts = {}
        return

    def _load_persistent_download_dir(self) -> Path | None:
        """Load persisted download directory if it exists and is accessible."""

        configured_dir = self.settings.download_dir.strip()
        if not configured_dir:
            return None

        candidate = Path(configured_dir).expanduser()
        if not candidate.exists() or not candidate.is_dir():
            LOGGER.warning(
                "Gespeicherter Ordner ungültig: %s. Nächster Schritt: Bitte Ordner neu wählen.",
                candidate,
            )
            return None

        return candidate

    def _check_folder_permissions(
        self, require_write: bool
    ) -> tuple[bool, str, list[str]]:
        """Prüft Linux-Berechtigungen für den gewählten Ordner mit klaren Next Steps."""

        if not self.root_path:
            return (
                False,
                "Es wurde noch kein Ordner ausgewählt.",
                [
                    "Erneut versuchen: Bitte zuerst im Schritt 1 einen Ordner auswählen.",
                    "Reparatur: Danach erneut auf 'Weiter' klicken.",
                ],
            )

        candidate = self.root_path.expanduser()
        if not candidate.exists() or not candidate.is_dir():
            return (
                False,
                "Der gewählte Ordner ist nicht erreichbar oder kein Ordner.",
                [
                    "Erneut versuchen: Bitte einen vorhandenen Ordner auswählen.",
                    "Reparatur: Bei externer Festplatte zuerst das Laufwerk einhängen.",
                ],
            )

        missing_flags: list[str] = []
        if not os.access(candidate, os.R_OK):
            missing_flags.append("Lesen")
        if not os.access(candidate, os.X_OK):
            missing_flags.append("Öffnen")
        if require_write and not os.access(candidate, os.W_OK):
            missing_flags.append("Schreiben")

        if missing_flags:
            joined = ", ".join(missing_flags)
            chmod_hint = f"chmod u+rwx '{candidate}'"
            return (
                False,
                f"Für den Ordner fehlen Linux-Berechtigungen: {joined}.",
                [
                    "Erneut versuchen: Anderen Ordner mit eigenen Rechten auswählen.",
                    f"Reparatur: Im Terminal Berechtigung setzen mit: {chmod_hint}",
                    "Protokoll: Bei Firmen-Geräten Administrator oder IT ansprechen.",
                ],
            )

        if require_write:
            info = "Berechtigungen OK: Lesen, Öffnen und Schreiben sind erlaubt."
        else:
            info = "Berechtigungen OK: Lesen und Öffnen sind erlaubt."
        return (
            True,
            info,
            ["Weiter: Sie können sicher mit dem nächsten Schritt fortfahren."],
        )

    def _save_settings_with_feedback(self, reason: str) -> tuple[bool, str]:
        """Speichert Einstellungen und prüft direkt, ob sie persistent verfügbar sind."""

        clean_reason = reason.strip()
        if not clean_reason:
            raise ValueError(
                "Speichergrund fehlt. Nächster Schritt: Bitte kurz angeben, was gespeichert wird."
            )

        self.settings.save()
        reloaded = Settings.load()
        persisted_ok = (
            reloaded.theme == self.settings.theme
            and reloaded.large_text == self.settings.large_text
            and reloaded.download_dir == self.settings.download_dir
            and reloaded.duplicates_mode == self.settings.duplicates_mode
        )

        if not persisted_ok:
            warning = (
                f"Speichern nach '{clean_reason}' konnte nicht bestätigt werden. "
                "Nächster Schritt: 'bash start.sh' ausführen und danach erneut speichern."
            )
            LOGGER.warning(warning)
            self.persistence_status_icon = "⚠️"
            self.persistence_status_text = warning
            return (False, warning)

        info = f"Speichern nach '{clean_reason}' erfolgreich bestätigt."
        LOGGER.info(info)
        self.persistence_status_icon = "✅"
        self.persistence_status_text = (
            "Einstellungen gespeichert und beim Neustart verfügbar."
        )
        return (True, info)

    def _apply_cleanup_goal(self, goal: str) -> None:
        """Setzt häufige Aufräumziele als laienfreundliche Schnellkonfiguration."""

        clean_goal = goal.strip().lower()
        presets = {
            "ausgewogen (empfohlen)": (
                "50MB",
                "30d",
                "safe",
                "⚖️ Ausgewogen: Alte und größere Dateien plus sichere Duplikat-Prüfung.",
            ),
            "große dateien": (
                "100MB",
                "any",
                "none",
                "📦 Große Dateien: Fokus auf viel Speichergewinn mit großen Dateien.",
            ),
            "alte dateien": (
                "any",
                "180d",
                "none",
                "🗂️ Alte Dateien: Fokus auf lange nicht genutzte Inhalte.",
            ),
            "duplikate zuerst": (
                "any",
                "any",
                "safe",
                "🧩 Duplikate zuerst: Gleiche Dateien besonders gründlich erkennen.",
            ),
        }
        preset = presets.get(clean_goal)
        if preset is None:
            raise ValueError(
                "Aufräumziel ist ungültig. Nächster Schritt: Bitte ein sichtbares Ziel aus der Liste auswählen."
            )

        size_value, age_value, dup_mode, help_text = preset
        self._set_combo_text_or_raise(
            combo=self.combo_size,
            value=size_value,
            field_name="Größenfilter",
        )
        self._set_combo_text_or_raise(
            combo=self.combo_age,
            value=age_value,
            field_name="Altersfilter",
        )
        self._set_combo_text_or_raise(
            combo=self.combo_dups,
            value=dup_mode,
            field_name="Duplikatmodus",
        )
        output_text = f"<b>Aktives Aufräumziel:</b> {help_text}"
        if not output_text.strip():
            raise RuntimeError(
                "Aufräumhilfe fehlt. Nächster Schritt: Bitte Auswahl erneut setzen."
            )
        self.lbl_cleanup_goal_hint.setText(output_text)

    def _set_combo_text_or_raise(
        self, *, combo: QComboBox, value: str, field_name: str
    ) -> None:
        """Setzt Combo-Werte robust mit Input-/Output-Validierung und klaren Next Steps."""

        clean_value = value.strip()
        clean_field_name = field_name.strip()
        if not clean_field_name:
            raise ValueError(
                "Feldname fehlt. Nächster Schritt: Bitte den Namen der Auswahl ergänzen."
            )
        if not clean_value:
            raise ValueError(
                f"Wert fehlt bei '{clean_field_name}'. Nächster Schritt: Bitte eine sichtbare Auswahl setzen."
            )

        if combo.findText(clean_value) < 0:
            raise ValueError(
                f"Wert '{clean_value}' ist bei '{clean_field_name}' nicht verfügbar. "
                "Nächster Schritt: Bitte eine Option aus der Liste auswählen."
            )

        combo.setCurrentText(clean_value)
        if combo.currentText().strip() != clean_value:
            raise RuntimeError(
                f"Auswahl '{clean_field_name}' konnte nicht gesetzt werden. "
                "Nächster Schritt: Bitte erneut auswählen und speichern."
            )

    # Theme stylesheets
    STYLES = {
        "light": """
            QWidget {
                background-color: #f3f6fb;
                color: #0f172a;
                selection-background-color: #1d4ed8;
                selection-color: #ffffff;
            }
            QMainWindow, QStackedWidget {
                background-color: #e8eef7;
            }
            QLabel {
                color: #0f172a;
                line-height: 1.35;
            }
            QPushButton {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #6b7280;
                border-radius: 10px;
                padding: 10px 14px;
                font-weight: 600;
                min-height: 38px;
            }
            QPushButton:hover {
                background-color: #e0ebff;
                border-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #d5e4ff;
            }
            QPushButton:focus,
            QCheckBox:focus,
            QComboBox:focus,
            QListWidget:focus {
                border: 3px solid #1d4ed8;
                outline: none;
            }
            QComboBox, QListWidget {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #6b7280;
                border-radius: 8px;
                padding: 8px;
                min-height: 34px;
            }
            QCheckBox {
                spacing: 10px;
            }
            QPushButton:focus,
            QCheckBox:focus,
            QComboBox:focus,
            QListWidget:focus {
                border: 3px solid #61e1ff;
                outline: none;
            }
        """,
        "dark": """
            QWidget {
                background-color: #121a2a;
                color: #f2f5ff;
                selection-background-color: #2f63d8;
                selection-color: #ffffff;
            }
            QLabel {
                color: #f2f5ff;
            }
            QMainWindow, QStackedWidget {
                background-color: #101a2b;
                border: 1px solid #2a3b5a;
            }
            QPushButton {
                background-color: #223757;
                color: #f8faff;
                border: 1px solid #4c5f83;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 600;
                min-height: 34px;
            }
            QPushButton:hover {
                background-color: #2b4670;
            }
            QPushButton:pressed {
                background-color: #1b2a44;
            }
            QPushButton:focus,
            QCheckBox:focus,
            QComboBox:focus,
            QListWidget:focus {
                border: 2px solid #7db6ff;
                outline: none;
            }
            QComboBox, QListWidget {
                background-color: #1a263c;
                color: #f2f5ff;
                border: 1px solid #4c5f83;
                border-radius: 6px;
                padding: 6px;
            }
            QCheckBox {
                spacing: 8px;
            }
        """,
        "neon": """
            QWidget {
                background-color: #222b58;
                color: #e8edf8;
                selection-background-color: #4f46e5;
                selection-color: #f8fbff;
            }
            QMainWindow, QStackedWidget {
                background-color: #111a2f;
                border: 1px solid #27345d;
                border-radius: 24px;
            }
            QLabel {
                color: #e8edf8;
            }
            QPushButton {
                background-color: #17243f;
                color: #f3f7ff;
                border: 1px solid #4f5fa3;
                border-radius: 16px;
                padding: 10px 14px;
                font-weight: 600;
                min-height: 38px;
            }
            QPushButton:hover {
                background-color: #1f2f52;
                border-color: #64d7ff;
            }
            QPushButton:pressed {
                background-color: #101a30;
            }
            QComboBox, QListWidget {
                background-color: #142139;
                color: #e8edf8;
                border: 1px solid #3c4f82;
                border-radius: 14px;
                padding: 8px;
                min-height: 34px;
            }
            QCheckBox {
                spacing: 10px;
            }
            QPushButton:focus, QCheckBox:focus, QComboBox:focus, QListWidget:focus {
                border: 3px solid #61e1ff;
                outline: none;
            }
        """,
        "kontrast": """
            QWidget { background-color: #000000; color: #ffff00; }
            QPushButton {
                background-color: #000000;
                color: #ffff00;
                border: 2px solid #ffff00;
                border-radius: 8px;
                padding: 8px 12px;
                min-height: 34px;
            }
            QPushButton:hover { background-color: #222222; }
            QPushButton:focus, QCheckBox:focus, QComboBox:focus, QListWidget:focus {
                border: 3px solid #00ffff;
                outline: none;
            }
            QComboBox, QListWidget {
                background-color: #000000;
                color: #ffff00;
                border: 2px solid #ffff00;
                padding: 6px;
            }
        """,
        "blau": """
            QWidget {
                background-color: #eaf4ff;
                color: #0a1f44;
                selection-background-color: #003a8c;
                selection-color: #ffffff;
            }
            QMainWindow, QStackedWidget {
                background-color: #d9ebff;
            }
            QPushButton {
                background-color: #ffffff;
                color: #0a1f44;
                border: 2px solid #0b4fb3;
                border-radius: 10px;
                padding: 10px 14px;
                min-height: 38px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #dcecff;
                border-color: #003a8c;
            }
            QPushButton:focus, QCheckBox:focus, QComboBox:focus, QListWidget:focus {
                border: 3px solid #ff8c00;
                outline: none;
            }
            QComboBox, QListWidget {
                background-color: #ffffff;
                color: #0a1f44;
                border: 1px solid #0b4fb3;
                border-radius: 8px;
                padding: 8px;
            }
        """,
        "senior": """
            QWidget {
                background-color: #ffffff;
                color: #000000;
                font-size: 18pt;
            }
            QPushButton {
                background-color: #e0e0e0;
                color: #000000;
                padding: 10px;
                font-size: 16pt;
                border: 2px solid #4b5563;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #c0c0c0;
            }
            QPushButton:focus,
            QCheckBox:focus,
            QComboBox:focus,
            QListWidget:focus {
                border: 3px solid #1d4ed8;
                outline: none;
            }
        """,
    }

    THEME_DISPLAY_TO_KEY = {
        "hell": "light",
        "dunkel": "dark",
        "neon": "neon",
        "kontrast": "kontrast",
        "blau": "blau",
        "senior": "senior",
    }
    THEME_KEY_TO_DISPLAY = {
        "light": "hell",
        "dark": "dunkel",
        "neon": "neon",
        "kontrast": "kontrast",
        "blau": "blau",
        "senior": "senior",
    }
    PREVIEW_SCALE_LABELS = {
        "Auto (Fensterbreite)": 0.0,
        "100 %": 1.0,
        "115 %": 1.15,
        "130 %": 1.3,
        "150 %": 1.5,
    }
    PREVIEW_POSITION_MODES = {
        "Auto (Fensterbreite)": "auto",
        "Aktion links · Liste rechts": "action_left",
        "Liste links · Aktion rechts": "list_left",
        "Untereinander": "stacked",
    }

    def _resolve_theme_key(self, selected_theme: str) -> str:
        """Validiert die Theme-Auswahl und gibt den internen Theme-Key zurück."""

        clean_selected_theme = selected_theme.strip().lower()
        if not clean_selected_theme:
            raise ValueError(
                "Farbschema fehlt. Nächster Schritt: Bitte ein Theme auswählen."
            )

        resolved_theme = self.THEME_DISPLAY_TO_KEY.get(clean_selected_theme)
        if resolved_theme is None or resolved_theme not in self.STYLES:
            raise ValueError(
                "Farbschema ist ungültig. Nächster Schritt: Bitte eines der sichtbaren Themes auswählen."
            )

        return resolved_theme

    def apply_theme(self, theme: str, large_text: bool) -> None:
        resolved_theme = theme if theme in self.STYLES else "kontrast"
        if theme not in self.STYLES:
            LOGGER.warning(
                "Unbekanntes Theme '%s'. Nächster Schritt: In den Einstellungen ein gültiges Theme wählen.",
                theme,
            )
        style = self.STYLES[resolved_theme] + self.GLOBAL_A11Y_STYLE
        if large_text and theme != "senior":
            # Increase base font size
            style += " QWidget { font-size: 14pt; }"
        self.setStyleSheet(style)

    def _build_theme_a11y_hint(self, theme_key: str, large_text: bool) -> str:
        """Liefert eine laienfreundliche A11y-Hilfe mit Input- und Output-Validierung."""

        clean_theme_key = theme_key.strip().lower()
        if clean_theme_key not in self.THEME_A11Y_HINTS:
            raise ValueError(
                "A11y-Hinweis kann nicht erstellt werden. Nächster Schritt: Bitte ein gültiges Farbschema wählen."
            )

        size_hint = (
            "Großer Text ist aktiv und verbessert die Lesbarkeit."
            if large_text
            else "Großer Text ist aus. Bei Bedarf im gleichen Schritt aktivieren."
        )
        output = f"{self.THEME_A11Y_HINTS[clean_theme_key]} {size_hint}"
        if not output.strip():
            raise RuntimeError(
                "A11y-Hinweis fehlt. Nächster Schritt: Theme bitte erneut auswählen."
            )
        return output

    def _build_design_similarity_hint(
        self,
        *,
        theme_key: str,
        contrast_label: str,
        selected_layout: str,
        selected_scale: str,
    ) -> str:
        """Erzeugt eine nachvollziehbare Design-Ähnlichkeitsbewertung zur Referenzvorgabe."""

        clean_theme_key = theme_key.strip().lower()
        clean_contrast_label = contrast_label.strip()
        clean_layout = selected_layout.strip()
        clean_scale = selected_scale.strip()
        if (
            clean_theme_key not in self.DESIGN_SIMILARITY_TARGETS
            or not clean_contrast_label
            or not clean_layout
            or not clean_scale
        ):
            raise ValueError(
                "Design-Ähnlichkeit kann nicht berechnet werden. Nächster Schritt: Theme, Layout und Skalierung sichtbar auswählen."
            )

        target = self.DESIGN_SIMILARITY_TARGETS[clean_theme_key]
        target_layout = target["layout"]
        target_contrast = float(target["contrast"])

        # Basis-Score auf Referenznähe: Theme + Kontrast + Layout + Schriftgröße.
        score = 55
        if clean_layout == target_layout:
            score += 20
        if clean_scale in {"115 %", "130 %", "150 %"}:
            score += 10
        if clean_contrast_label in {"Sehr gut", "Maximal"}:
            score += 15

        score = min(score, 100)
        support_hint = (
            "Nächster Schritt: Für maximale Nähe zur Referenz jetzt auf "
            f"'{target_layout}' wechseln und Kontraststatus 'Sehr gut' oder 'Maximal' halten."
        )
        output = (
            f"Design-Nähe zur Vorgabe: <b>{score}%</b> "
            f"(Ziel-Kontrast {target_contrast:.1f}/5, Ziel-Layout: {target_layout}). "
            f"{support_hint}"
        )
        if not output.strip():
            raise RuntimeError(
                "Design-Nähe fehlt. Nächster Schritt: Vorschau erneut öffnen und prüfen."
            )
        return output

    def _apply_accessibility_quick_mode(self, mode: str) -> None:
        """Aktiviert schnelle, barrierearme Presets für sofort bessere Lesbarkeit."""

        clean_mode = mode.strip().lower()
        presets = {
            "max_contrast": ("kontrast", True, "130 %", "Untereinander"),
            "balanced": ("blau", False, "115 %", "Aktion links · Liste rechts"),
        }
        preset = presets.get(clean_mode)
        if preset is None:
            raise ValueError(
                "Schnellmodus ist ungültig. Nächster Schritt: Bitte einen sichtbaren Hilfebutton verwenden."
            )

        theme_display, large_text, scale_text, position_text = preset
        self._set_combo_text_or_raise(
            combo=self.combo_theme,
            value=theme_display,
            field_name="Farbschema",
        )
        self.cb_large.setChecked(large_text)
        self._set_combo_text_or_raise(
            combo=self.combo_preview_scale,
            value=scale_text,
            field_name="Bereichsskalierung",
        )
        self._set_combo_text_or_raise(
            combo=self.combo_preview_position,
            value=position_text,
            field_name="Vorschau-Position",
        )
        self._sync_theme_preview()
        self._apply_responsive_welcome_layout()

    def _sync_theme_preview(self) -> None:
        """Aktualisiert die Live-Vorschau des Themes mit klarer Validierung."""

        selected_theme = self.combo_theme.currentText().strip().lower()
        if not selected_theme:
            raise ValueError(
                "Farbschema fehlt in der Vorschau. Nächster Schritt: Bitte ein sichtbares Theme auswählen."
            )

        large_text_enabled = self.cb_large.isChecked()
        if not isinstance(large_text_enabled, bool):
            raise TypeError(
                "Textmodus ist ungültig. Nächster Schritt: Bitte Auswahl erneut setzen."
            )

        resolved_theme = self._resolve_theme_key(selected_theme)
        self.apply_theme(resolved_theme, large_text_enabled)

        selected_scale = self.combo_preview_scale.currentText().strip()
        selected_position = self.combo_preview_position.currentText().strip()
        (
            resolved_scale_label,
            resolved_position_label,
            auto_layout_hint,
        ) = self._resolve_auto_preview_profile(
            selected_scale=selected_scale,
            selected_position=selected_position,
            window_width=self.width(),
        )

        scale_factor = self._resolve_preview_scale_factor(resolved_scale_label)
        self._apply_preview_scale(scale_factor)

        position_mode = self._resolve_preview_position_mode(resolved_position_label)
        self._apply_preview_layout(position_mode)

        preview_title = self.THEME_KEY_TO_DISPLAY.get(resolved_theme, "kontrast")
        position_title = resolved_position_label.lower()
        a11y_hint = self._build_theme_a11y_hint(resolved_theme, large_text_enabled)
        profile = self.THEME_INTERACTION_PROFILES.get(resolved_theme)
        if profile is None:
            raise RuntimeError(
                "Interaktionsprofil fehlt. Nächster Schritt: Bitte Theme-Daten prüfen."
            )
        contrast_level, contrast_text, next_click_hint = profile
        design_similarity_hint = self._build_design_similarity_hint(
            theme_key=resolved_theme,
            contrast_label=contrast_level,
            selected_layout=resolved_position_label,
            selected_scale=resolved_scale_label,
        )
        preview_text = (
            "<b>Live-Vorschau aktiv</b><br/>"
            f"Theme: <b>{preview_title}</b> · Großer Text: "
            f"<b>{'an' if large_text_enabled else 'aus'}</b><br/>"
            f"Bereichsskalierung: <b>{resolved_scale_label}</b> · Position: <b>{position_title}</b><br/>"
            f"Auto-Anpassung: {auto_layout_hint}<br/>"
            f"A11y-Hinweis (Zugänglichkeit): {a11y_hint}<br/>"
            f"Interaktivitäts-/Kontraststatus: <b>{contrast_level}</b> – {contrast_text}<br/>"
            f"{design_similarity_hint}<br/>"
            f"Empfohlener nächster Klick: {next_click_hint}<br/>"
            "Beispiel unten zeigt Button, Liste und Kontrast in Echtzeit."
        )
        if not preview_text.strip():
            raise RuntimeError(
                "Vorschauausgabe fehlt. Nächster Schritt: Bitte Theme-Auswahl erneut öffnen."
            )
        self.lbl_theme_preview_info.setText(preview_text)

    def _resolve_auto_preview_profile(
        self, *, selected_scale: str, selected_position: str, window_width: int
    ) -> tuple[str, str, str]:
        """Löst automatische Vorschau-Anpassungen robust auf Basis der Fensterbreite auf."""

        clean_scale = selected_scale.strip()
        clean_position = selected_position.strip()
        if not clean_scale or not clean_position:
            raise ValueError(
                "Auto-Profil kann nicht berechnet werden. Nächster Schritt: Bitte Skalierung und Position sichtbar auswählen."
            )
        if window_width <= 0:
            raise ValueError(
                "Fensterbreite ist ungültig. Nächster Schritt: Fenster erneut öffnen und Auto-Modus neu wählen."
            )

        auto_scale_requested = clean_scale == "Auto (Fensterbreite)"
        auto_position_requested = clean_position == "Auto (Fensterbreite)"
        if not auto_scale_requested and not auto_position_requested:
            return clean_scale, clean_position, "aus"

        if window_width < 980:
            auto_scale_label = "130 %"
            auto_position_label = "Untereinander"
            auto_hint = "aktiv – kompakte Breite erkannt, Elemente werden größer und untereinander angeordnet."
        elif window_width < 1280:
            auto_scale_label = "115 %"
            auto_position_label = "Aktion links · Liste rechts"
            auto_hint = "aktiv – mittlere Breite erkannt, ausgewogenes Standardlayout verwendet."
        else:
            auto_scale_label = "100 %"
            auto_position_label = "Liste links · Aktion rechts"
            auto_hint = "aktiv – breite Ansicht erkannt, mehr Platz für Listenorientierung genutzt."

        resolved_scale = auto_scale_label if auto_scale_requested else clean_scale
        resolved_position = (
            auto_position_label if auto_position_requested else clean_position
        )
        if resolved_scale not in self.PREVIEW_SCALE_LABELS:
            raise RuntimeError(
                "Auto-Skalierung konnte nicht aufgelöst werden. Nächster Schritt: Bitte festen Skalierungswert wählen."
            )
        if resolved_position not in self.PREVIEW_POSITION_MODES:
            raise RuntimeError(
                "Auto-Position konnte nicht aufgelöst werden. Nächster Schritt: Bitte feste Position wählen."
            )

        return resolved_scale, resolved_position, auto_hint

    def _resolve_preview_scale_factor(self, selected_scale: str) -> float:
        """Validiert die Bereichsskalierung der Vorschau."""

        clean_scale = selected_scale.strip()
        if not clean_scale:
            raise ValueError(
                "Bereichsskalierung fehlt. Nächster Schritt: Bitte eine sichtbare Skalierung wählen."
            )

        factor = self.PREVIEW_SCALE_LABELS.get(clean_scale)
        if factor is None:
            raise ValueError(
                "Bereichsskalierung ist ungültig. Nächster Schritt: Bitte eine Option aus der Liste wählen."
            )
        return factor

    def _apply_preview_scale(self, scale_factor: float) -> None:
        """Skaliert die Vorschau-Elemente robust und prüft das Ergebnis."""

        if scale_factor <= 0:
            raise ValueError(
                "Skalierungsfaktor ist ungültig. Nächster Schritt: Bitte eine positive Skalierung wählen."
            )

        button_height = max(int(38 * scale_factor), 38)
        list_height = max(int(90 * scale_factor), 90)
        self.preview_action_button.setMinimumHeight(button_height)
        self.preview_list.setMaximumHeight(list_height)
        self.preview_list.setMinimumHeight(min(list_height, 160))

        if self.preview_action_button.minimumHeight() < 38:
            raise RuntimeError(
                "Skalierung konnte nicht gesetzt werden. Nächster Schritt: Bitte Auswahl erneut anwenden."
            )

    def _resolve_preview_position_mode(self, selected_mode: str) -> str:
        """Validiert die gewählte Vorschau-Position."""

        clean_mode = selected_mode.strip()
        if not clean_mode:
            raise ValueError(
                "Positionsmodus fehlt. Nächster Schritt: Bitte eine sichtbare Position wählen."
            )

        resolved_mode = self.PREVIEW_POSITION_MODES.get(clean_mode)
        if resolved_mode is None:
            raise ValueError(
                "Positionsmodus ist ungültig. Nächster Schritt: Bitte einen Modus aus der Liste auswählen."
            )
        return resolved_mode

    def _apply_preview_layout(self, position_mode: str) -> None:
        """Ordnet Vorschau-Elemente flexibel neu an und prüft das Ergebnis."""

        if position_mode not in {"action_left", "list_left", "stacked"}:
            raise ValueError(
                "Positionsmodus ist ungültig. Nächster Schritt: Bitte eine andere Position wählen."
            )

        while self.preview_row.count():
            self.preview_row.takeAt(0)

        if position_mode == "action_left":
            self.preview_row.setDirection(QBoxLayout.LeftToRight)
            self.preview_row.addWidget(self.preview_action_button)
            self.preview_row.addWidget(self.preview_list)
        elif position_mode == "list_left":
            self.preview_row.setDirection(QBoxLayout.LeftToRight)
            self.preview_row.addWidget(self.preview_list)
            self.preview_row.addWidget(self.preview_action_button)
        else:
            self.preview_row.setDirection(QBoxLayout.TopToBottom)
            self.preview_row.addWidget(self.preview_action_button)
            self.preview_row.addWidget(self.preview_list)

        if self.preview_row.count() != 2:
            raise RuntimeError(
                "Vorschau-Positionierung fehlgeschlagen. Nächster Schritt: Bitte Position erneut auswählen."
            )

    def _build_scroll_page(self) -> tuple[QScrollArea, QWidget]:
        """Erzeugt eine Seite mit großen Scrollleisten für kleine Bildschirme."""

        content = QWidget()
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        return scroll, content

    def _apply_responsive_welcome_layout(self) -> None:
        """Schaltet die Start-Vorschau je Fensterbreite um, damit nichts abgeschnitten wird."""

        if not hasattr(self, "preview_shell"):
            return

        compact_mode = self.width() < 1220
        self.preview_shell.setDirection(
            QBoxLayout.TopToBottom if compact_mode else QBoxLayout.LeftToRight
        )
        if compact_mode:
            self.list_category_nav.setMaximumWidth(16777215)
            self.list_category_nav.setMinimumWidth(180)
            self.list_category_nav.setMaximumHeight(170)
        else:
            self.list_category_nav.setMinimumWidth(220)
            self.list_category_nav.setMaximumWidth(260)
            self.list_category_nav.setMaximumHeight(16777215)

    def _create_pages(self) -> None:
        self.page_welcome, self.page_welcome_content = self._build_scroll_page()
        self._setup_welcome_page()
        self.stack.addWidget(self.page_welcome)

        self.page_options, self.page_options_content = self._build_scroll_page()
        self._setup_options_page()
        self.stack.addWidget(self.page_options)

        self.page_scan, self.page_scan_content = self._build_scroll_page()
        self._setup_scan_page()
        self.stack.addWidget(self.page_scan)

        self.page_plan, self.page_plan_content = self._build_scroll_page()
        self._setup_plan_page()
        self.stack.addWidget(self.page_plan)

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt API
        """Aktualisiert die Vorschau bei Größenänderung, wenn Auto-Modi aktiv sind."""

        super().resizeEvent(event)
        if not hasattr(self, "combo_preview_scale") or not hasattr(
            self, "combo_preview_position"
        ):
            return

        auto_scale_active = (
            self.combo_preview_scale.currentText().strip() == "Auto (Fensterbreite)"
        )
        auto_position_active = (
            self.combo_preview_position.currentText().strip() == "Auto (Fensterbreite)"
        )
        if auto_scale_active or auto_position_active:
            self._sync_theme_preview()
        self._apply_responsive_welcome_layout()
        self._update_scrollbar_policies_by_window_height()

    # ---------------------------
    # Page 1: Welcome & Folder/Theme
    def _setup_welcome_page(self) -> None:
        layout = QVBoxLayout(self.page_welcome_content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        title = QLabel("<h2>Schritt 1/4 – Ordner und Anzeige</h2>")
        title.setAccessibleName("Schrittanzeige")
        title.setAccessibleDescription(
            "Überschrift für den ersten Schritt des Assistenten"
        )
        layout.addWidget(title)
        intro = QLabel(
            "<b>Einfach starten:</b> Wählen Sie zuerst Ihren Download-Ordner. "
            "Danach können Sie ein gut lesbares Farbschema auswählen."
        )
        intro.setWordWrap(True)
        intro.setAccessibleName("Einstiegshilfe")
        intro.setAccessibleDescription("Kurze Hilfe in einfacher Sprache für den Start")
        layout.addWidget(intro)

        mainview_hint = QLabel(
            "<b>Vorschau Hauptansicht:</b> Links sehen Sie die neue Kategorie-Leiste, "
            "in der Mitte die neuen Aktionskarten."
        )
        mainview_hint.setWordWrap(True)
        mainview_hint.setAccessibleName("Hauptansicht Vorschauhinweis")
        mainview_hint.setAccessibleDescription(
            "Erklärt in einfacher Sprache den Aufbau der neuen Hauptansicht"
        )
        layout.addWidget(mainview_hint)

        screen_fit_hint = QLabel(
            "<b>Bildschirm-Hilfe:</b> Wenn unten etwas fehlt, passt sich die Ansicht automatisch an. "
            "Zusätzlich können Sie jederzeit mit der Scrollleiste weiter nach unten gehen."
        )
        screen_fit_hint.setWordWrap(True)
        screen_fit_hint.setAccessibleName("Bildschirmhilfe")
        screen_fit_hint.setAccessibleDescription(
            "Erklärt in einfacher Sprache die automatische Anpassung und Scroll-Nutzung"
        )
        layout.addWidget(screen_fit_hint)

        # Hilfe-Schaltfläche: zeigt eine kurze Kurzanleitung für den Einstieg.
        btn_help = QPushButton("Hilfe")
        btn_help.setToolTip("Zeigt eine kurze Hilfe zur Bedienung")
        btn_help.setAccessibleName("Hilfe anzeigen")
        btn_help.setAccessibleDescription(
            "Öffnet eine Kurzanleitung zur Bedienung in einfacher Sprache"
        )
        btn_help.clicked.connect(self._show_general_help)
        layout.addWidget(btn_help)

        mode_bar = QHBoxLayout()
        mode_bar.addWidget(QLabel("Bedienmodus:"))
        self.combo_experience_mode = QComboBox()
        self.combo_experience_mode.addItems(list(self.EXPERIENCE_MODES.keys()))
        self.combo_experience_mode.setCurrentText("Laien-Modus (empfohlen)")
        self.combo_experience_mode.setToolTip(
            "Laien-Modus zeigt nur Kernschritte. Entwickler-Modus blendet Tool-Bibel und Statushilfe ein."
        )
        self.combo_experience_mode.setAccessibleName("Bedienmodus Auswahl")
        mode_bar.addWidget(self.combo_experience_mode, 1)
        btn_tool_bible = QPushButton("Tool-Bibel öffnen")
        btn_tool_bible.setToolTip(
            "Öffnet einen kurzen Entwickler-Hub mit Pfaden zu technischen Dokumenten"
        )
        btn_tool_bible.clicked.connect(self._show_tool_bible)
        mode_bar.addWidget(btn_tool_bible)
        layout.addLayout(mode_bar)

        self.lbl_mode_hint = QLabel()
        self.lbl_mode_hint.setWordWrap(True)
        self.lbl_mode_hint.setAccessibleName("Modus Hinweis")
        self.lbl_mode_hint.setStyleSheet(
            "border: 1px solid #6b7280; border-radius: 10px; padding: 10px;"
        )
        layout.addWidget(self.lbl_mode_hint)

        self.preview_shell = QBoxLayout(QBoxLayout.LeftToRight)
        self.preview_shell.setSpacing(12)

        self.list_category_nav = QListWidget()
        self.list_category_nav.setAccessibleName("Kategorie-Leiste")
        self.list_category_nav.setAccessibleDescription(
            "Linke Navigation mit Kategorien für die Hauptansicht"
        )
        self.list_category_nav.setToolTip(
            "Vorschau: Diese Kategorien steuern später die Hauptansicht"
        )
        self.list_category_nav.setMinimumWidth(220)
        self.list_category_nav.setMaximumWidth(260)
        self.list_category_nav.addItems(
            [
                "📂 Übersicht",
                "🧹 Schnell aufräumen",
                "🧪 Analyse",
                "🛡️ Sicherheit",
                "⚙️ Einstellungen",
                "🛠️ Entwicklerbereich",
            ]
        )
        self.list_category_nav.setCurrentRow(0)
        self.list_category_nav.setStyleSheet(
            "border: 1px solid #394b79; border-radius: 22px; padding: 10px;"
            "background: #0a1324;"
        )
        self.preview_shell.addWidget(self.list_category_nav)

        cards_wrap = QVBoxLayout()
        cards_wrap.setSpacing(10)

        card_specs = [
            "<b>Karte 1: Schnellstart</b><br/>Direkter Einstieg für einen sicheren Standardlauf.",
            "<b>Karte 2: Speicher freimachen</b><br/>Fokus auf große und alte Dateien mit klaren Schritten.",
            "<b>Karte 3: Duplikate prüfen</b><br/>Findet doppelte Dateien mit verständlicher Ergebnisliste.",
        ]
        if len(card_specs) != 3:
            raise ValueError(
                "Karten-Vorschau unvollständig. Nächster Schritt: Genau drei Aktionskarten bereitstellen."
            )

        self.preview_action_cards: list[QLabel] = []
        for card_text in card_specs:
            clean_text = card_text.strip()
            if not clean_text:
                raise ValueError(
                    "Leerer Kartentext erkannt. Nächster Schritt: Kartenhinweis ergänzen."
                )
            card = QLabel(clean_text)
            card.setWordWrap(True)
            card.setTextFormat(Qt.RichText)
            card.setMinimumHeight(68)
            card.setStyleSheet(
                "border: 1px solid #374a7a; border-radius: 24px; padding: 14px;"
                "background: #111d34;"
            )
            card.setAccessibleName("Aktionskarte Vorschau")
            card.setAccessibleDescription(
                "Vorschau einer zentralen Aktionskarte in der neuen Hauptansicht"
            )
            self.preview_action_cards.append(card)
            cards_wrap.addWidget(card)

        self.preview_shell.addLayout(cards_wrap, stretch=1)
        layout.addLayout(self.preview_shell)

        self.lbl_dashboard_info = QLabel()
        self.lbl_dashboard_info.setWordWrap(True)
        self.lbl_dashboard_info.setTextFormat(Qt.RichText)
        self.lbl_dashboard_info.setAccessibleName("Schnellübersicht")
        self.lbl_dashboard_info.setAccessibleDescription(
            "Zeigt aktuelle Einstellungen und Hilfehinweise"
        )
        self.lbl_dashboard_info.setStyleSheet(
            "border: 1px solid #384c7f; border-radius: 24px; padding: 14px;"
            "background: #0f182c;"
        )
        layout.addWidget(self.lbl_dashboard_info)
        # Folder selection
        hl_folder = QHBoxLayout()
        self.lbl_folder = QLabel("Kein Ordner ausgewählt")
        self.lbl_folder.setWordWrap(True)
        self.lbl_folder.setAccessibleName("Ausgewählter Ordner")
        btn_choose = QPushButton("Ordner wählen…")
        btn_choose.setToolTip("Öffnet den Dialog zur Ordnerauswahl")
        btn_choose.setAccessibleName("Ordner auswählen")
        btn_choose.setAccessibleDescription(
            "Öffnet die Auswahl für den Download-Ordner"
        )
        btn_choose.setShortcut("Alt+O")
        hl_folder.addWidget(self.lbl_folder)
        hl_folder.addWidget(btn_choose)
        layout.addLayout(hl_folder)
        if self.root_path:
            self.lbl_folder.setText(str(self.root_path))
        btn_choose.clicked.connect(self._choose_folder)

        actions_bar = QHBoxLayout()
        actions_bar.setSpacing(8)
        self.btn_dash_open_folder = QPushButton("Ordner im Dateimanager öffnen")
        self.btn_dash_open_folder.setToolTip(
            "Öffnet den aktuell ausgewählten Zielordner direkt aus dem Dashboard"
        )
        self.btn_dash_open_folder.clicked.connect(
            self._open_selected_folder_in_file_manager
        )
        self.btn_dash_help = QPushButton("Hilfe-Center")
        self.btn_dash_help.setToolTip(
            "Zeigt die Schritt-für-Schritt-Hilfe in einfacher Sprache"
        )
        self.btn_dash_help.clicked.connect(self._show_general_help)
        self.btn_dash_continue = QPushButton("Direkt zu Schritt 2")
        self.btn_dash_continue.setToolTip(
            "Speichert die Angaben und springt direkt in die Filter- und Rasteransicht"
        )
        self.btn_dash_continue.clicked.connect(self._welcome_next)
        for button in (
            self.btn_dash_open_folder,
            self.btn_dash_help,
            self.btn_dash_continue,
        ):
            button.setMinimumHeight(42)
            actions_bar.addWidget(button)
        layout.addLayout(actions_bar)
        # Theme selection
        hl_theme = QHBoxLayout()
        lbl_theme = QLabel("Farbschema:")
        hl_theme.addWidget(lbl_theme)
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(
            ["hell", "dunkel", "neon", "kontrast", "blau", "senior"]
        )
        self.combo_theme.setToolTip("Wählen Sie ein Farbschema mit guter Lesbarkeit")
        self.combo_theme.setAccessibleName("Farbschema")
        self.combo_theme.setMinimumWidth(160)
        theme_display = self.THEME_KEY_TO_DISPLAY.get(self.settings.theme, "kontrast")
        self.combo_theme.setCurrentText(theme_display)
        lbl_theme.setBuddy(self.combo_theme)
        hl_theme.addWidget(self.combo_theme)
        self.cb_large = QCheckBox("Großer Text")
        self.cb_large.setChecked(self.settings.large_text)
        self.cb_large.setToolTip("Vergrößert Text für bessere Lesbarkeit")
        self.cb_large.setAccessibleName("Großer Text aktivieren")
        hl_theme.addWidget(self.cb_large)
        layout.addLayout(hl_theme)

        hl_theme_quick = QHBoxLayout()
        hl_theme_quick.addWidget(QLabel("Theme-Schnellwahl:"))
        for shortcut, theme_key in [
            ("Alt+1", "light"),
            ("Alt+2", "dark"),
            ("Alt+3", "neon"),
            ("Alt+4", "kontrast"),
            ("Alt+5", "blau"),
            ("Alt+6", "senior"),
        ]:
            theme_display = self.THEME_KEY_TO_DISPLAY[theme_key]
            quick_button = QPushButton(theme_display)
            quick_button.setToolTip(
                f"Setzt das Theme sofort auf '{theme_display}' und aktualisiert die Live-Vorschau"
            )
            quick_button.setAccessibleName(f"Theme Schnellwahl {theme_display}")
            quick_button.setShortcut(shortcut)
            quick_button.clicked.connect(
                lambda _=False, value=theme_display: self.combo_theme.setCurrentText(
                    value
                )
            )
            hl_theme_quick.addWidget(quick_button)
        layout.addLayout(hl_theme_quick)

        hl_preview_controls = QHBoxLayout()
        lbl_preview_scale = QLabel("Bereichsskalierung:")
        self.combo_preview_scale = QComboBox()
        self.combo_preview_scale.addItems(list(self.PREVIEW_SCALE_LABELS.keys()))
        self.combo_preview_scale.setCurrentText("Auto (Fensterbreite)")
        self.combo_preview_scale.setToolTip(
            "Steuert die Größe der Vorschau-Fläche: fester Wert oder automatische Fensteranpassung"
        )
        self.combo_preview_scale.setAccessibleName("Bereichsskalierung Vorschau")
        self.combo_preview_scale.setAccessibleDescription(
            "Auswahlfeld für die Vorschaugröße mit klaren Prozentwerten"
        )
        self.combo_preview_scale.setMinimumWidth(140)
        lbl_preview_scale.setBuddy(self.combo_preview_scale)
        hl_preview_controls.addWidget(lbl_preview_scale)
        hl_preview_controls.addWidget(self.combo_preview_scale)

        lbl_preview_position = QLabel("Vorschau-Position:")
        self.combo_preview_position = QComboBox()
        self.combo_preview_position.addItems(list(self.PREVIEW_POSITION_MODES.keys()))
        self.combo_preview_position.setCurrentText("Auto (Fensterbreite)")
        self.combo_preview_position.setToolTip(
            "Legt fest, ob Aktion und Liste links, rechts, untereinander oder automatisch angeordnet sind"
        )
        self.combo_preview_position.setAccessibleName("Vorschau-Position wählen")
        self.combo_preview_position.setAccessibleDescription(
            "Auswahlfeld für die Anordnung der Vorschauelemente"
        )
        self.combo_preview_position.setMinimumWidth(220)
        lbl_preview_position.setBuddy(self.combo_preview_position)
        hl_preview_controls.addWidget(lbl_preview_position)
        hl_preview_controls.addWidget(self.combo_preview_position)
        layout.addLayout(hl_preview_controls)

        self.lbl_theme_preview_info = QLabel()
        self.lbl_theme_preview_info.setWordWrap(True)
        self.lbl_theme_preview_info.setAccessibleName("Theme Live-Vorschau Hinweis")
        self.lbl_theme_preview_info.setAccessibleDescription(
            "Zeigt den aktiven Vorschau-Status für Theme, Kontrast und Design-Nähe zur Vorgabe"
        )
        self.lbl_theme_preview_info.setToolTip(
            "Vergleichen Sie die aktuelle Ansicht mit der Zielvorgabe. Höhere Prozentwerte bedeuten höhere Design-Ähnlichkeit."
        )
        layout.addWidget(self.lbl_theme_preview_info)

        self.preview_row = QBoxLayout(QBoxLayout.LeftToRight)
        self.preview_action_button = QPushButton("Beispiel: Primäraktion")
        self.preview_action_button.setEnabled(False)
        self.preview_action_button.setToolTip(
            "Nur Vorschau: So sieht ein Aktionsbutton im gewählten Theme aus"
        )
        self.preview_action_button.setAccessibleName("Vorschau Primäraktion")
        self.preview_action_button.setAccessibleDescription(
            "Deaktivierter Beispielbutton zur Prüfung von Kontrast und Lesbarkeit"
        )
        self.preview_row.addWidget(self.preview_action_button)
        self.preview_list = QListWidget()
        self.preview_list.setAccessibleName("Theme Vorschau-Liste")
        self.preview_list.setAccessibleDescription(
            "Beispielliste mit markiertem Eintrag zur Kontrastprüfung"
        )
        self.preview_list.addItems(
            [
                "Beispiel-Liste: aktive Auswahl",
                "Beispiel-Liste: neutraler Eintrag",
            ]
        )
        self.preview_list.setCurrentRow(0)
        self.preview_list.setMaximumHeight(90)
        self.preview_row.addWidget(self.preview_list)
        layout.addLayout(self.preview_row)

        hl_accessibility_quick = QHBoxLayout()
        btn_max_contrast = QPushButton("Lesbarkeit sofort maximieren")
        btn_max_contrast.setToolTip(
            "Setzt Kontrast-Theme, großen Text und klare Stapelansicht mit einem Klick"
        )
        btn_max_contrast.setAccessibleName("Lesbarkeit sofort maximieren")
        btn_max_contrast.setShortcut("Alt+K")
        btn_max_contrast.clicked.connect(
            lambda: self._apply_accessibility_quick_mode("max_contrast")
        )
        hl_accessibility_quick.addWidget(btn_max_contrast)

        btn_balanced = QPushButton("Ausgewogene Ansicht laden")
        btn_balanced.setToolTip(
            "Lädt ein ruhiges Standard-Layout mit gutem Kontrast für den Alltag"
        )
        btn_balanced.setAccessibleName("Ausgewogene Ansicht laden")
        btn_balanced.setShortcut("Alt+L")
        btn_balanced.clicked.connect(
            lambda: self._apply_accessibility_quick_mode("balanced")
        )
        hl_accessibility_quick.addWidget(btn_balanced)

        btn_graphics_tips = QPushButton("Grafik-Verbesserungen anzeigen")
        btn_graphics_tips.setToolTip(
            "Zeigt eine kurze Checkliste, wie Farben, Fokus und Abstände weiter verbessert werden können"
        )
        btn_graphics_tips.setAccessibleName("Grafik Verbesserungs-Tipps")
        btn_graphics_tips.clicked.connect(self._show_graphics_improvement_help)
        hl_accessibility_quick.addWidget(btn_graphics_tips)

        btn_debug_html = QPushButton("Debug-HTML öffnen")
        btn_debug_html.setToolTip(
            "Erzeugt eine visuelle HTML-Datei mit dem aktuellen GUI-Status und öffnet sie"
        )
        btn_debug_html.setAccessibleName("Debug HTML des aktuellen GUI-Zustands öffnen")
        btn_debug_html.clicked.connect(self._open_debug_gui_snapshot)
        hl_accessibility_quick.addWidget(btn_debug_html)
        layout.addLayout(hl_accessibility_quick)

        self.combo_theme.currentTextChanged.connect(
            lambda _: self._sync_theme_preview()
        )
        self.cb_large.toggled.connect(lambda _: self._sync_theme_preview())
        self.combo_preview_scale.currentTextChanged.connect(
            lambda _: self._sync_theme_preview()
        )
        self.combo_preview_position.currentTextChanged.connect(
            lambda _: self._sync_theme_preview()
        )
        self._sync_theme_preview()

        help_box = QLabel(
            "<b>Hilfe:</b><br/>"
            "• Tastatur: Mit <b>Tab</b> wechseln Sie zwischen Feldern.<br/>"
            "• Theme-Schnellwahl: Mit <b>Alt+1 bis Alt+5</b> wechseln Sie direkt zwischen allen Farbschemata.<br/>"
            "• Schnellwahl: Mit <b>Alt+O</b> öffnen Sie direkt die Ordnerauswahl.<br/>"
            "• Schnellhilfe Lesbarkeit: <b>Alt+K</b> maximiert Kontrast, <b>Alt+L</b> lädt die ausgewogene Ansicht.<br/>"
            "• Bei Unsicherheit starten Sie mit dem Schema <b>kontrast</b>.<br/>"
            "• Für ruhige, helle Farben wählen Sie <b>blau</b>.<br/>"
            "• Auto (Fensterbreite) passt Vorschaugröße und Position bei Fensteränderungen automatisch an.<br/>"
            "• Bereichsskalierung und Vorschau-Position helfen bei eigener Bildschirmgröße.<br/>"
            "• Sie können Einstellungen später jederzeit ändern."
        )
        help_box.setWordWrap(True)
        help_box.setAccessibleName("Hilfebereich")
        help_box.setAccessibleDescription("Tipps für Bedienung und Lesbarkeit")
        help_box.setStyleSheet(
            "border: 1px solid #6b7280; border-radius: 10px; padding: 10px;"
        )
        layout.addWidget(help_box)

        dev_area_title = QLabel(
            "<b>Entwicklerbereich (Hilfebereich): Implementiert vs. Geplant</b><br/>"
            "Dieser Bereich bündelt Entwicklungsstatus getrennt von der normalen Tool-Konfiguration."
        )
        dev_area_title.setWordWrap(True)
        dev_area_title.setAccessibleName("Entwicklerbereich Titel")
        dev_area_title.setAccessibleDescription(
            "Erklärt den getrennten Bereich für Entwicklungs- und Statusinformationen"
        )
        layout.addWidget(dev_area_title)

        dev_area_help = QLabel(
            "<b>Status-Legende:</b> ✅ bedeutet abgeschlossen, 🟡 bedeutet noch offen.<br/>"
            "<b>Layout-Hinweis:</b> Nutzen Sie die Filterbuttons, um offene Punkte schneller zu finden."
        )
        dev_area_help.setWordWrap(True)
        dev_area_help.setAccessibleName("Status Legende und Layout-Hinweis")
        dev_area_help.setAccessibleDescription(
            "Erklärt in einfacher Sprache die Bedeutung der Statussymbole und die Filterbedienung"
        )
        dev_area_help.setStyleSheet(
            "border: 1px solid #6b7280; border-radius: 10px; padding: 10px;"
        )
        layout.addWidget(dev_area_help)

        filter_bar = QHBoxLayout()
        self.btn_status_filter_all = QPushButton("Alle")
        self.btn_status_filter_open = QPushButton("Nur offen")
        self.btn_status_filter_all.setToolTip(
            "Zeigt implementierte und geplante Punkte gemeinsam an"
        )
        self.btn_status_filter_open.setToolTip(
            "Zeigt nur geplante (offene) Punkte für die nächste Umsetzung"
        )
        self.btn_status_filter_all.setMinimumHeight(40)
        self.btn_status_filter_open.setMinimumHeight(40)
        self.btn_status_filter_all.setAccessibleName("Statusfilter alle Einträge")
        self.btn_status_filter_open.setAccessibleName(
            "Statusfilter nur offene Einträge"
        )
        self.btn_status_filter_all.clicked.connect(
            lambda: self._apply_project_status_filter("all")
        )
        self.btn_status_filter_open.clicked.connect(
            lambda: self._apply_project_status_filter("open")
        )
        filter_bar.addWidget(self.btn_status_filter_all)
        filter_bar.addWidget(self.btn_status_filter_open)
        layout.addLayout(filter_bar)

        self.lbl_project_status_summary = QLabel("Status-Hilfe wird geladen...")
        self.lbl_project_status_summary.setWordWrap(True)
        self.lbl_project_status_summary.setAccessibleName(
            "Status-Hilfe Zusammenfassung"
        )
        layout.addWidget(self.lbl_project_status_summary)

        self.list_project_status = QListWidget()
        self.list_project_status.setAccessibleName("Implementiert-vs-Geplant Liste")
        self.list_project_status.setAccessibleDescription(
            "Liste mit Projektstatus für implementierte und offene Punkte"
        )
        self.list_project_status.setMinimumHeight(130)
        layout.addWidget(self.list_project_status)
        self._apply_project_status_filter("all")

        self.developer_widgets = [
            dev_area_title,
            dev_area_help,
            self.btn_status_filter_all,
            self.btn_status_filter_open,
            self.lbl_project_status_summary,
            self.list_project_status,
        ]
        self.combo_experience_mode.currentTextChanged.connect(
            self._apply_experience_mode
        )
        self._apply_experience_mode(self.combo_experience_mode.currentText())

        # Verlauf (History) anzeigen: zeigt die letzten Läufe mit Anzahl Dateien und Megabytes.
        history_title = QLabel("<b>Verlauf (Dateien/MB pro Lauf)</b>")
        history_title.setAccessibleName("Verlauf Titel")
        history_title.setAccessibleDescription(
            "Überschrift des Verlaufbereichs mit Zusammenfassung früherer Aufräumläufe"
        )
        layout.addWidget(history_title)

        history_help = QLabel(
            "In diesem Verlauf sehen Sie, wie viele Dateien und Megabyte bei früheren Läufen bearbeitet wurden."
            " Sie können den Verlauf exportieren oder löschen."
        )
        history_help.setWordWrap(True)
        history_help.setAccessibleName("Verlaufs-Hilfe")
        history_help.setAccessibleDescription(
            "Kurze Erklärung des Verlaufbereichs mit Hinweisen zur Bedienung"
        )
        history_help.setStyleSheet(
            "border: 1px solid #6b7280; border-radius: 10px; padding: 8px;"
        )
        layout.addWidget(history_help)

        self.list_history = QListWidget()
        self.list_history.setAccessibleName("Verlaufsliste")
        self.list_history.setAccessibleDescription(
            "Liste der letzten Läufe mit Anzahl der Dateien und Gesamtspeicherplatz"
        )
        self.list_history.setMinimumHeight(110)
        layout.addWidget(self.list_history)

        hist_btns = QHBoxLayout()
        # Verlaufsschaltflächen einheitlich anlegen
        self.btn_export_history = self._create_standard_button(
            "Verlauf exportieren",
            "Speichert den Verlauf als CSV-Datei",
            self._export_history,
            accessible_name="Verlauf exportieren",
            accessible_description="Exportiert den Verlauf in eine CSV-Datei für die Weiterverwendung",
        )
        self.btn_clear_history = self._create_standard_button(
            "Verlauf löschen",
            "Löscht alle Einträge im Verlauf",
            self._clear_history,
            accessible_name="Verlauf löschen",
            accessible_description="Löscht alle gespeicherten Verlaufsdaten nach Bestätigung",
        )
        for btn in (self.btn_export_history, self.btn_clear_history):
            hist_btns.addWidget(btn)
        layout.addLayout(hist_btns)
        # Verlauf laden
        self._refresh_history_display()

        # Navigation buttons
        btn_next = QPushButton("Weiter →")
        btn_next.setToolTip("Speichert die Auswahl und geht zum nächsten Schritt")
        btn_next.setAccessibleName("Zum nächsten Schritt")
        btn_next.clicked.connect(self._welcome_next)
        layout.addWidget(btn_next)
        self._refresh_dashboard_info()

    def _show_graphics_improvement_help(self) -> None:
        """Zeigt eine laienfreundliche Liste mit visuellen Verbesserungsmöglichkeiten."""

        tips_html = self._build_graphics_improvement_text()
        message = QMessageBox(self)
        message.setWindowTitle("Grafik-Verbesserungen")
        message.setIcon(QMessageBox.Information)
        message.setText(tips_html)
        message.setInformativeText(
            "Nächster Schritt: Einen Punkt auswählen, anwenden und danach im Theme-Wechsel gegenprüfen."
        )
        message.setStandardButtons(QMessageBox.Ok)
        message.setAccessibleName("Dialog Grafik Verbesserungen")
        message.setAccessibleDescription(
            "Dialog mit klaren Empfehlungen für bessere Lesbarkeit, Kontrast und Tastaturfokus"
        )
        message.exec()

    def _refresh_dashboard_info(self) -> None:
        selected_folder = self.root_path or Path(self.settings.download_dir)
        folder_text = escape(
            str(selected_folder) if selected_folder else "Noch kein Ordner festgelegt"
        )
        active_types = (
            ", ".join(self.settings.filters.types)
            if self.settings.filters.types
            else "keine"
        )
        active_types = escape(active_types)
        active_preset = escape(self.settings.presets)
        duplicates_mode = escape(self.settings.duplicates_mode)
        permission_prefix = "✅"
        permission_status = "noch nicht geprüft"
        if self.root_path:
            perm_ok, perm_message, _ = self._check_folder_permissions(
                require_write=True
            )
            permission_prefix = "✅" if perm_ok else "⚠️"
            permission_status = perm_message

        safe_permission_status = escape(permission_status)
        system_text = escape(f"{platform.system()} {platform.release()}")
        persistence_icon = escape(self.persistence_status_icon)
        persistence_text = escape(self.persistence_status_text)
        dashboard_health_cards = self._build_dashboard_health_cards()
        dashboard_role_hint = self._build_dashboard_role_hint()

        neon_mockup = self._build_soft_neon_dashboard_mockup()

        self.lbl_dashboard_info.setText(
            f"{neon_mockup}<br/><br/>"
            "<b>Haupt-Dashboard (Schnellübersicht)</b><br/>"
            "<b>Alles auf einem Bildschirm:</b> Sidebar links, Aktionsraster in der Mitte, Hilfe- und Statuspanel rechts.<br/>"
            f"• System: {system_text}<br/>"
            "• Offline-Betrieb: aktiv (keine Internetverbindung nötig)<br/>"
            f"• Aktueller Zielordner: {folder_text}<br/>"
            f"• Linux-Berechtigungen: {permission_prefix} {safe_permission_status}<br/>"
            f"• Aktives Preset: {active_preset}<br/>"
            f"• Dateitypen-Filter: {active_types}<br/>"
            f"• Duplikat-Prüfung: {duplicates_mode}<br/><br/>"
            f"• Einstellungen dauerhaft: {persistence_icon} {persistence_text}<br/><br/>"
            "<b>Hilfe in einfacher Sprache:</b><br/>"
            "1) Wählen Sie einen Ordner.<br/>"
            "2) Wählen Sie ein gut lesbares Farbschema.<br/>"
            "3) Drücken Sie <b>Weiter</b>, um die Analyse zu starten.<br/>"
            "4) Prüfen Sie im Dashboard, ob der Speicherstatus auf ✅ steht.<br/><br/>"
            "<b>Extra-Hilfe (idiotensicher):</b><br/>"
            "• <b>Bereich 1 – Start:</b> Ordner wählen, dann Theme prüfen.<br/>"
            "• <b>Bereich 2 – Aufräumen:</b> Eine Kachel klicken und Vorschlag bestätigen.<br/>"
            "• <b>Bereich 3 – Hilfe:</b> Bei Fehlern immer zuerst den Hilfe-Button nutzen.<br/><br/>"
            "<b>Dashboard-Systemgesundheit:</b><br/>"
            f"{dashboard_health_cards}<br/>"
            "<b>Schnelle Bedienpfade:</b><br/>"
            f"{dashboard_role_hint}<br/><br/>"
            "<b>Gate-Übersicht:</b><br/>"
            f"{self._build_gate_status_html()}"
        )

        try:
            self._write_debug_gui_snapshot()
        except Exception as exc:
            LOGGER.warning(
                "Debug-HTML Snapshot konnte nicht aktualisiert werden: %s",
                exc,
            )

        # Wenn ein Verlauf angezeigt wird, diesen ebenfalls aktualisieren
        if getattr(self, "list_history", None) is not None:
            self._refresh_history_display()

    def _build_soft_neon_dashboard_mockup(self) -> str:
        """Erstellt eine barrierearme Dashboard-Vorschau mit Sidebar, Raster und Hilfepanel."""

        header_segments = ["Segment A", "Segment B", "Segment C"]
        if len(header_segments) != 3:
            raise ValueError(
                "Mockup-Segmente fehlen. Nächster Schritt: Genau drei Kopf-Segmente setzen."
            )

        icon_col = "".join(
            (
                "<div style='margin:8px 0;color:#9db0d8;'>●</div>"
                if index != 1
                else "<div style='margin:8px 0;padding:6px 10px;border-radius:14px;background:#ff2d5f;color:#ffffff;box-shadow:0 0 8px #ff2d5f;'>◆</div>"
            )
            for index in range(6)
        )
        if not icon_col.strip():
            raise RuntimeError(
                "Mockup-Navigation leer. Nächster Schritt: Linke Symbolleiste erneut aufbauen."
            )

        mockup = (
            "<div style='background:#0a1020;border-radius:30px;padding:16px;border:1px solid #2a3f68;'>"
            "<div style='display:flex;gap:12px;align-items:center;margin-bottom:12px;'>"
            "<div style='flex:1;background:#121f37;border-radius:999px;padding:10px 16px;color:#7f93bf;'>🔎 Dashboard-Suche · Ordner · Presets</div>"
            "<div style='display:flex;gap:10px;'>"
            + "".join(
                "<span style='display:inline-block;width:44px;height:6px;border-radius:999px;background:#61e1ff;'></span>"
                for _ in header_segments
            )
            + "</div></div>"
            "<table width='100%' cellspacing='10'><tr>"
            f"<td width='86' style='vertical-align:top;background:#050b19;border-radius:22px;padding:12px;text-align:center;color:#dbe7ff;'>{icon_col}<div style='margin-top:10px;font-size:11px;'>Sidebar</div></td>"
            "<td style='vertical-align:top;'>"
            "<div style='background:#14233d;border-radius:20px;padding:12px;margin-bottom:10px;color:#f0f4ff;'>"
            "<b>Download-Clean-Zentrale</b><br/><span style='color:#a9b8d8;'>Alles sofort im Blick: Ordnerwahl, Schnellaktionen und Hilfe.</span></div>"
            "<table width='100%' cellspacing='8'>"
            "<tr><td style='background:#1b3362;border:1px solid #61e1ff;border-radius:14px;padding:10px;color:#ffffff;'>📂 Ordner wählen</td>"
            "<td style='background:#1b3362;border:1px solid #7ec9ff;border-radius:14px;padding:10px;color:#ffffff;'>🧹 Große Dateien</td>"
            "<td style='background:#1b3362;border:1px solid #61e1ff;border-radius:14px;padding:10px;color:#ffffff;'>🧩 Duplikate</td></tr>"
            "<tr><td style='background:#1b3362;border:1px solid #7ec9ff;border-radius:14px;padding:10px;color:#ffffff;'>🎵 Medien sortieren</td>"
            "<td style='background:#1b3362;border:1px solid #61e1ff;border-radius:14px;padding:10px;color:#ffffff;'>📊 Analyse starten</td>"
            "<td style='background:#1b3362;border:1px solid #7ec9ff;border-radius:14px;padding:10px;color:#ffffff;'>✅ Plan prüfen</td></tr>"
            "</table>"
            "</td>"
            "<td width='250' style='vertical-align:top;'>"
            "<div style='background:#111d33;border-radius:24px;padding:12px;color:#f0f4ff;margin-bottom:10px;'>"
            "<b>Hilfe-Panel</b><br/>1) Ordner wählen<br/>2) Kachel drücken<br/>3) Vorschau prüfen</div>"
            "<div style='background:#111d33;border-radius:24px;padding:12px;color:#9fb2d8;margin-bottom:10px;'>"
            "Status: Kontrast, Rechte, Speicher und letzter Lauf mit ✅/⚠️.<br/>"
            "Soforthilfe: Bei ⚠️ zuerst 'Hilfe-Center' öffnen, dann 'Reparatur' klicken.</div>"
            "<div style='background:#111d33;border-radius:24px;padding:12px;color:#9fb2d8;'>"
            "Fehlerhilfe: Erneut versuchen · Reparatur · Protokoll.</div>"
            "</td></tr></table>"
            "</div>"
        )
        if not mockup.strip():
            raise RuntimeError(
                "Mockup-Ausgabe leer. Nächster Schritt: Soft-Neon-Layout erneut generieren."
            )
        return mockup

    def _refresh_history_display(self) -> None:
        """
        Füllt die Verlaufsliste mit Daten aus der Verlaufsdatei.
        Jeder Eintrag zeigt Datum, Anzahl der Dateien und Gesamtgröße.
        """
        if self.list_history is None:
            return
        try:
            history_entries = read_history()
        except Exception:
            history_entries = []
        self.list_history.clear()
        for entry in history_entries:
            ts = entry.get("timestamp", "")
            files = entry.get("files", 0)
            size_mb = entry.get("size_mb", 0.0)
            try:
                size_val = float(size_mb)
            except Exception:
                size_val = 0.0
            item_text = f"{ts} – {files} Dateien · {size_val:.2f} MB"
            li = QListWidgetItem(item_text)
            li.setData(Qt.UserRole, entry)
            self.list_history.addItem(li)

    def _export_history(self) -> None:
        """
        Exportiert den Verlauf als CSV-Datei in den Ordner 'exports'.
        Zeigt eine kurze Rückmeldung nach erfolgreichem Export.
        """
        try:
            history_entries = read_history()
        except Exception:
            history_entries = []
        if not history_entries:
            QMessageBox.information(
                self, "Verlauf exportieren", "Keine Einträge im Verlauf vorhanden."
            )
            return
        export_dir = Path(__file__).resolve().parent.parent / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        csv_path = export_dir / "history.csv"
        try:
            with csv_path.open("w", encoding="utf-8") as f:
                f.write("timestamp;files;size_mb\n")
                for entry in history_entries:
                    f.write(
                        f"{entry['timestamp']};{entry['files']};{entry['size_mb']}\n"
                    )
            QMessageBox.information(
                self,
                "Verlauf exportieren",
                f"Der Verlauf wurde erfolgreich exportiert nach:\n{csv_path}",
            )
        except Exception as exc:
            QMessageBox.warning(self, "Export-Fehler", f"Export nicht möglich: {exc}")

    def _clear_history(self) -> None:
        """
        Löscht alle Verlaufsdaten nach Bestätigung.
        """
        reply = QMessageBox.question(
            self,
            "Verlauf löschen",
            "Möchten Sie wirklich alle Einträge im Verlauf löschen?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            clear_history()
            if self.list_history is not None:
                self._refresh_history_display()
            QMessageBox.information(
                self, "Verlauf gelöscht", "Der Verlauf wurde erfolgreich gelöscht."
            )
        except Exception as exc:
            QMessageBox.warning(
                self, "Fehler beim Löschen", f"Löschen nicht möglich: {exc}"
            )

    def _choose_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Ordner auswählen", str(Path.home() / "Downloads")
        )
        if path:
            self.lbl_folder.setText(path)
            self.root_path = Path(path)
            self.settings.download_dir = str(self.root_path)
            self._save_settings_with_feedback("Ordnerauswahl")
            self._refresh_dashboard_info()

    def _open_selected_folder_in_file_manager(self) -> None:
        """Öffnet den gewählten Zielordner direkt aus dem Dashboard mit validierten Next Steps."""

        target_folder = self.root_path or Path(self.settings.download_dir)
        if not target_folder:
            self._show_error_with_mini_help(
                title="Ordner fehlt",
                happened_text="Es ist noch kein Zielordner für das Dashboard gesetzt.",
                next_clicks=[
                    "Erneut versuchen: Erst auf 'Ordner wählen…' klicken.",
                    "Reparatur: Danach erneut 'Ordner im Dateimanager öffnen' nutzen.",
                ],
            )
            return

        expanded_folder = Path(target_folder).expanduser()
        if not expanded_folder.exists() or not expanded_folder.is_dir():
            self._show_error_with_mini_help(
                title="Ordner nicht erreichbar",
                happened_text="Der gewählte Ordner ist nicht vorhanden oder kein Verzeichnis.",
                next_clicks=[
                    "Erneut versuchen: Einen vorhandenen Ordner neu auswählen.",
                    "Protokoll: Bei externer Platte zuerst das Laufwerk einhängen.",
                ],
            )
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(expanded_folder)))

    def _welcome_next(self) -> None:
        # Save theme settings
        selected_theme = self.combo_theme.currentText()
        try:
            self.settings.theme = self._resolve_theme_key(selected_theme)
        except ValueError as exc:
            self._show_error_with_mini_help(
                title="Farbschema prüfen",
                happened_text=str(exc),
                next_clicks=[
                    "Erneut versuchen: Bitte ein Theme aus der Liste auswählen.",
                    "Reparatur: Bei Anzeigeproblemen 'kontrast' verwenden.",
                    "Protokoll: Log-Datei öffnen und Fehlermeldung teilen.",
                ],
            )
            return
        self.settings.large_text = self.cb_large.isChecked()
        if self.root_path:
            self.settings.download_dir = str(self.root_path)
        saved_ok, save_message = self._save_settings_with_feedback("Startseite")
        if not saved_ok:
            self._show_error_with_mini_help(
                title="Einstellungen prüfen",
                happened_text=save_message,
                next_clicks=[
                    "Erneut versuchen: Einstellungen ändern und erneut auf 'Weiter' klicken.",
                    "Reparatur: Im Projektordner 'bash start.sh' ausführen.",
                    "Protokoll: logs/app.log öffnen und Meldung prüfen.",
                ],
            )
        self.apply_theme(self.settings.theme, self.settings.large_text)
        self.statusBar().showMessage(
            "Tipp: Nutzen Sie die große Ecke unten rechts oder die großen Scrollleisten für bessere Skalierung.",
            12000,
        )
        self._refresh_dashboard_info()
        # Ensure folder selected
        if not self.root_path:
            clicked = self._show_error_with_mini_help(
                title="Fehlende Angabe",
                happened_text="Bitte wählen Sie zuerst einen Ordner aus.",
                next_clicks=[
                    "Erneut versuchen: Ordnerauswahl noch einmal öffnen.",
                    "Reparatur: Hilfe bei häufigen Startproblemen anzeigen.",
                    "Protokoll: Ort der Log-Datei anzeigen.",
                ],
                buttons=[
                    ("Erneut versuchen", QMessageBox.AcceptRole),
                    ("Reparatur", QMessageBox.ActionRole),
                    ("Protokoll", QMessageBox.HelpRole),
                ],
            )

            if clicked == "Erneut versuchen":
                self._choose_folder()
            elif clicked == "Reparatur":
                QMessageBox.information(
                    self,
                    "Reparaturhilfe",
                    "Bitte führen Sie im Projektordner den Befehl 'bash start.sh' aus.\n"
                    "Das Programm prüft automatisch wichtige Voraussetzungen und zeigt Rückmeldungen an.",
                )
            elif clicked == "Protokoll":
                log_path = Path(__file__).resolve().parent.parent / "logs" / "app.log"
                QMessageBox.information(
                    self,
                    "Protokollpfad",
                    f"Log-Datei: {log_path}\n"
                    "Diese Datei hilft bei der Fehlersuche und kann an den Support weitergegeben werden.",
                )
            return
        self.stack.setCurrentWidget(self.page_options)

    # ---------------------------
    # Page 2: Options
    def _setup_options_page(self) -> None:
        layout = QVBoxLayout(self.page_options_content)
        layout.setSpacing(14)
        title = QLabel("<h2>Schritt 2/4 – Optionen</h2>")
        layout.addWidget(title)
        intro = QLabel(
            "Wählen Sie hier ein Preset (Voreinstellung) oder setzen Sie einzelne Filter. "
            "Die Bereiche sind bewusst klar getrennt für bessere Orientierung."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        preset_box = QLabel(
            "<b>1) Preset auswählen</b><br/>Schneller Start mit sinnvollen Standardwerten"
        )
        preset_box.setWordWrap(True)
        layout.addWidget(preset_box)
        hl_presets = QHBoxLayout()
        hl_presets.setSpacing(10)
        btn_senior = QPushButton("Preset: Senior")
        btn_std = QPushButton("Preset: Standard")
        btn_power = QPushButton("Preset: Power")
        for btn in (btn_senior, btn_std, btn_power):
            btn.setMinimumHeight(40)
            hl_presets.addWidget(btn)
        layout.addLayout(hl_presets)
        btn_senior.clicked.connect(lambda: self._load_preset("senior"))
        btn_std.clicked.connect(lambda: self._load_preset("standard"))
        btn_power.clicked.connect(lambda: self._load_preset("power"))
        self.current_preset_label = QLabel("Aktuelles Preset: " + self.settings.presets)
        layout.addWidget(self.current_preset_label)

        filters_box = QLabel(
            "<b>2) Dateitypen auswählen</b><br/>Mindestens ein Typ muss aktiv sein"
        )
        filters_box.setWordWrap(True)
        layout.addWidget(filters_box)
        self.cb_images = QCheckBox("Bilder")
        self.cb_videos = QCheckBox("Videos")
        self.cb_archives = QCheckBox("Archive")
        self.cb_other = QCheckBox("Andere")
        layout.addWidget(self.cb_images)
        layout.addWidget(self.cb_videos)
        layout.addWidget(self.cb_archives)
        layout.addWidget(self.cb_other)

        limits_box = QLabel(
            "<b>3) Grenzen setzen</b><br/>Optional: Größe und Alter eingrenzen"
        )
        limits_box.setWordWrap(True)
        layout.addWidget(limits_box)
        hl_size = QHBoxLayout()
        hl_size.addWidget(QLabel("Min. Größe:"))
        self.combo_size = QComboBox()
        self.combo_size.addItems(["any", "10MB", "50MB", "100MB"])
        hl_size.addWidget(self.combo_size)
        layout.addLayout(hl_size)
        hl_age = QHBoxLayout()
        hl_age.addWidget(QLabel("Min. Alter:"))
        self.combo_age = QComboBox()
        self.combo_age.addItems(["any", "30d", "180d", "365d"])
        hl_age.addWidget(self.combo_age)
        layout.addLayout(hl_age)

        duplicates_box = QLabel(
            "<b>4) Duplikat-Prüfung</b><br/>Wählen Sie die Sicherheitstiefe"
        )
        duplicates_box.setWordWrap(True)
        layout.addWidget(duplicates_box)
        hl_dup = QHBoxLayout()
        hl_dup.addWidget(QLabel("Duplikate:"))
        self.combo_dups = QComboBox()
        self.combo_dups.addItems(["none", "quick", "safe"])
        hl_dup.addWidget(self.combo_dups)
        layout.addLayout(hl_dup)

        cleanup_goal_box = QLabel(
            "<b>5) Aufräumziel (Schnellwahl)</b><br/>Farbiges Leitsystem für typische Reinigungen"
        )
        cleanup_goal_box.setWordWrap(True)
        layout.addWidget(cleanup_goal_box)
        hl_cleanup_goal = QHBoxLayout()
        hl_cleanup_goal.addWidget(QLabel("Aufräumziel:"))
        self.combo_cleanup_goal = QComboBox()
        self.combo_cleanup_goal.addItems(
            [
                "Ausgewogen (empfohlen)",
                "Große Dateien",
                "Alte Dateien",
                "Duplikate zuerst",
            ]
        )
        hl_cleanup_goal.addWidget(self.combo_cleanup_goal)
        layout.addLayout(hl_cleanup_goal)

        self.lbl_cleanup_goal_hint = QLabel()
        self.lbl_cleanup_goal_hint.setWordWrap(True)
        self.lbl_cleanup_goal_hint.setAccessibleName("Aufräumziel-Hilfe")
        self.lbl_cleanup_goal_hint.setAccessibleDescription(
            "Erklärung in einfacher Sprache zum aktiven Aufräumziel"
        )
        layout.addWidget(self.lbl_cleanup_goal_hint)
        self.combo_cleanup_goal.currentTextChanged.connect(self._apply_cleanup_goal)
        self._apply_cleanup_goal(self.combo_cleanup_goal.currentText())

        footer_hint = QLabel(
            "Tipp: Starten Sie mit Preset Standard. Danach können Sie bei Bedarf verfeinern."
        )
        footer_hint.setWordWrap(True)
        layout.addWidget(footer_hint)

        self.lbl_workflow_examples = QLabel(
            "<b>Anwendungsbeispiele (Workflow):</b><br/>"
            "• <b>Beispiel 1: Laptop schnell frei machen</b> – Preset Standard, danach in Schritt 3 nur "
            "wichtige Treffer auswählen und in Schritt 4 ausführen.<br/>"
            "• <b>Beispiel 2: Externe Platte prüfen</b> – Preset Power, Duplikate auf safe, Trefferliste "
            "kontrollieren und nur passende Dateien markieren.<br/>"
            "Alle Hauptschritte haben Aktionstasten: Zurück, Weiter, Ausführen, Undo und Fertig."
        )
        self.lbl_workflow_examples.setWordWrap(True)
        self.lbl_workflow_examples.setAccessibleName("Workflow-Beispiele")
        self.lbl_workflow_examples.setAccessibleDescription(
            "Zwei kurze Beispiele in einfacher Sprache, damit der Ablauf klar wird"
        )
        layout.addWidget(self.lbl_workflow_examples)

        # 6) Schnellstart-Buttons – große Kacheln für direkte Aktionen
        quick_label = QLabel(
            "<b>6) Schnellstart-Buttons</b><br/>"
            "Starten Sie eine der folgenden Schnell-Aktionen:"
        )
        quick_label.setWordWrap(True)
        quick_label.setAccessibleName("Schnellstart-Überschrift")
        quick_label.setAccessibleDescription(
            "Kurze Erklärung zu den Schnellstart-Buttons für häufige Aufgaben"
        )
        layout.addWidget(quick_label)

        keyboard_help = self._build_quick_grid_keyboard_help()
        self.lbl_quick_grid_help = QLabel(
            "Die Schnell-Aktionen sind jetzt als Raster (Grid) in zwei Bereiche gruppiert: "
            "<b>Medien</b> und <b>Aufräumen</b>. Das hilft bei schneller Orientierung.<br/>"
            f"{keyboard_help}"
        )
        self.lbl_quick_grid_help.setWordWrap(True)
        self.lbl_quick_grid_help.setAccessibleName("Schnellstart-Raster Hilfe")
        self.lbl_quick_grid_help.setAccessibleDescription(
            "Erklärt in einfacher Sprache die Gruppierung und die Tastatur-Navigation im Schnellstart-Raster"
        )
        layout.addWidget(self.lbl_quick_grid_help)

        quick_grid_host = QWidget()
        quick_grid_host.setObjectName("quick-grid-shell")
        quick_grid_host.setStyleSheet(
            "#quick-grid-shell {"
            "background:#162e5c; border:1px solid #4b6698; border-radius:14px; padding:10px;"
            "}"
        )
        quick_grid_host.setAccessibleName("Schnellstart Raster")
        quick_grid_host.setAccessibleDescription(
            "Grid-Hauptbereich mit gruppierten Schnellstart-Karten"
        )
        quick_grid = QGridLayout(quick_grid_host)
        quick_grid.setHorizontalSpacing(14)
        # Laut Design-Referenz sollten Zeilen- und Spaltenabstände identisch 14px betragen
        quick_grid.setVerticalSpacing(14)

        media_header = self._create_quick_section_header("Medien")
        cleanup_header = self._create_quick_section_header("Aufräumen")

        self.btn_quick1 = self._create_quick_action_tile(
            label=self.ui_texts.get("quick_button_1_label", "Fotos sortieren"),
            tooltip=self.ui_texts.get(
                "quick_button_1_tooltip",
                "Scannt nur nach Bilddateien (JPG, PNG) und erstellt eine Vorschau.",
            ),
            accessible_name="Schnellstart Fotos",
            accessible_description="Startet sofort einen Scan mit dem Preset für Fotos",
            section="Medien",
        )
        self.btn_quick2 = self._create_quick_action_tile(
            label=self.ui_texts.get("quick_button_4_label", "Dokumente sortieren"),
            tooltip=self.ui_texts.get(
                "quick_button_4_tooltip",
                "Scannt nur nach Dokumenten (PDF, DOC) und erstellt eine Vorschau.",
            ),
            accessible_name="Schnellstart Dokumente",
            accessible_description="Startet sofort einen Scan mit dem Preset für Dokumente",
            section="Medien",
        )
        self.btn_quick3 = self._create_quick_action_tile(
            label=self.ui_texts.get("quick_button_5_label", "Musik sortieren"),
            tooltip=self.ui_texts.get(
                "quick_button_5_tooltip",
                "Scannt nur nach Musikdateien (MP3, WAV) und erstellt eine Vorschau.",
            ),
            accessible_name="Schnellstart Musik",
            accessible_description="Startet sofort einen Scan mit dem Preset für Musik",
            section="Medien",
        )
        self.btn_quick4 = self._create_quick_action_tile(
            label=self.ui_texts.get("quick_button_2_label", "Große Dateien prüfen"),
            tooltip=self.ui_texts.get(
                "quick_button_2_tooltip",
                "Scannt nach Dateien größer als 100MB und erstellt eine Vorschau.",
            ),
            accessible_name="Schnellstart Große Dateien",
            accessible_description="Startet sofort einen Scan mit dem Preset für große Dateien",
            section="Aufräumen",
        )
        self.btn_quick5 = self._create_quick_action_tile(
            label=self.ui_texts.get("quick_button_3_label", "Duplikate finden"),
            tooltip=self.ui_texts.get(
                "quick_button_3_tooltip",
                "Scannt nach möglichen Duplikaten und erstellt eine Vorschau.",
            ),
            accessible_name="Schnellstart Duplikate",
            accessible_description="Startet sofort einen Scan mit dem Preset für Duplikate",
            section="Aufräumen",
        )
        self.btn_quick6 = self._create_quick_action_tile(
            label=self.ui_texts.get("quick_button_6_label", "Alles sortieren"),
            tooltip=self.ui_texts.get(
                "quick_button_6_tooltip",
                "Scannt alle Dateitypen und erstellt eine Vorschau.",
            ),
            accessible_name="Schnellstart Alles",
            accessible_description="Startet sofort einen Scan mit dem Preset für alle Dateitypen",
            section="Aufräumen",
        )

        quick_grid.addWidget(media_header, 0, 0, 1, 3)
        quick_grid.addWidget(self.btn_quick1, 1, 0)
        quick_grid.addWidget(self.btn_quick2, 1, 1)
        quick_grid.addWidget(self.btn_quick3, 1, 2)
        quick_grid.addWidget(cleanup_header, 2, 0, 1, 3)
        quick_grid.addWidget(self.btn_quick4, 3, 0)
        quick_grid.addWidget(self.btn_quick5, 3, 1)
        quick_grid.addWidget(self.btn_quick6, 3, 2)

        self.btn_quick1.clicked.connect(lambda: self._quick_scan_preset("quick_photos"))
        self.btn_quick2.clicked.connect(lambda: self._quick_scan_preset("quick_docs"))
        self.btn_quick3.clicked.connect(lambda: self._quick_scan_preset("quick_music"))
        self.btn_quick4.clicked.connect(lambda: self._quick_scan_preset("quick_large"))
        self.btn_quick5.clicked.connect(lambda: self._quick_scan_preset("quick_dups"))
        self.btn_quick6.clicked.connect(lambda: self._quick_scan_preset("quick_all"))
        layout.addWidget(quick_grid_host)

        # Im Einsteiger-/Button‑Only‑Modus blenden wir komplexe Filter aus und heben Schnellstart hervor.
        if self.settings.novice_mode:
            # Verstecke Preset-Auswahl
            preset_box.hide()
            btn_senior.hide()
            btn_std.hide()
            btn_power.hide()
            self.current_preset_label.hide()
            # Verstecke Dateitypen
            filters_box.hide()
            self.cb_images.hide()
            self.cb_videos.hide()
            self.cb_archives.hide()
            self.cb_other.hide()
            # Verstecke Grenz-Einstellungen
            limits_box.hide()
            self.combo_size.hide()
            self.combo_age.hide()
            # Verstecke Duplikat-Prüfung
            duplicates_box.hide()
            self.combo_dups.hide()
            # Verstecke Aufräumziel
            cleanup_goal_box.hide()
            self.combo_cleanup_goal.hide()
            self.lbl_cleanup_goal_hint.hide()
            # Verstecke Workflow-Beispiele und Tipps
            footer_hint.hide()
            self.lbl_workflow_examples.hide()
            # Passe Überschrift der Schnellstart-Buttons an
            quick_label.setText(
                "<b>1) Schnellstart-Buttons</b><br/>Wählen Sie eine einfache Aufräumaktion aus:"
            )

        nav = QHBoxLayout()
        btn_prev = QPushButton("← Zurück")
        btn_prev.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_welcome))
        btn_next = QPushButton("Weiter →")
        btn_next.setMinimumHeight(40)
        btn_next.clicked.connect(self._options_next)
        nav.addWidget(btn_prev)
        nav.addWidget(btn_next)
        layout.addLayout(nav)
        # initialise checkboxes from settings
        self._apply_filters_from_settings()

    def _quick_scan_preset(self, preset_name: str) -> None:
        """
        Führt eine Schnellstart-Aktion aus: lädt ein Preset, speichert die Einstellungen,
        startet die Analyse und zeigt die Ergebnisse an.

        Wenn kein Ordner ausgewählt wurde, wird ein klarer Fehlerdialog mit nächstem Schritt angezeigt.
        """
        # Überprüfen, ob ein Ordner gewählt wurde
        if not self.root_path:
            self._show_error_with_mini_help(
                title="Ordner fehlt",
                happened_text="Bitte wählen Sie zuerst einen Ordner aus.",
                next_clicks=[
                    "OK: Klicken Sie auf 'Ordner wählen…' und wählen Sie Ihren Download-Ordner aus.",
                    "Danach den Schnellstart-Button erneut drücken.",
                ],
            )
            return
        # Lade das Preset (setzt Checkboxen und Filter)
        self._load_preset(preset_name)
        # Speichere Filter und starte Scan wie im Options-Schritt
        self._options_next()

    def _apply_filters_from_settings(self) -> None:
        f = self.settings.filters
        self.cb_images.setChecked("images" in f.types)
        self.cb_videos.setChecked("videos" in f.types)
        self.cb_archives.setChecked("archives" in f.types)
        self.cb_other.setChecked("other" in f.types)
        self.combo_size.setCurrentText(f.size)
        self.combo_age.setCurrentText(f.age)
        self.combo_dups.setCurrentText(self.settings.duplicates_mode)
        self.current_preset_label.setText("Aktuelles Preset: " + self.settings.presets)

    def _load_preset(self, preset_name: str) -> None:
        # Load preset JSON
        p = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "presets"
            / f"{preset_name}.json"
        )
        if p.exists():
            try:
                raw = json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                self._show_error_with_mini_help(
                    title="Fehler",
                    happened_text=f"Preset konnte nicht geladen werden: {e}",
                    next_clicks=[
                        "OK: Meldung schließen und ein anderes Preset probieren.",
                        "Datei im Ordner data/presets prüfen.",
                    ],
                )
                return
            filters = raw.get("filters", {})
            # update UI elements
            types = filters.get("types", [])
            self.cb_images.setChecked("images" in types)
            self.cb_videos.setChecked("videos" in types)
            self.cb_archives.setChecked("archives" in types)
            self.cb_other.setChecked("other" in types)
            self.combo_size.setCurrentText(filters.get("size", "any"))
            self.combo_age.setCurrentText(filters.get("age", "any"))
            self.combo_dups.setCurrentText(raw.get("duplicates_mode", "none"))
            # update settings
            self.settings.presets = preset_name
            self.settings.confirm_threshold = int(raw.get("confirm_threshold", 10))
            self.settings.filters = Filters.from_dict(filters)
            self.settings.duplicates_mode = raw.get("duplicates_mode", "none")
            self._save_settings_with_feedback("Preset laden")
            self.current_preset_label.setText("Aktuelles Preset: " + preset_name)

    def _options_next(self) -> None:
        # store custom filters
        types = []
        if self.cb_images.isChecked():
            types.append("images")
        if self.cb_videos.isChecked():
            types.append("videos")
        if self.cb_archives.isChecked():
            types.append("archives")
        if self.cb_other.isChecked():
            types.append("other")
        if not types:
            self._show_error_with_mini_help(
                title="Keine Dateitypen",
                happened_text="Bitte wählen Sie mindestens einen Dateityp aus.",
                next_clicks=[
                    "Mindestens ein Kästchen bei Bilder, Videos, Archive oder Andere aktivieren.",
                    "Dann auf Weiter klicken.",
                ],
            )
            return
        self.settings.filters = Filters(
            types=types,
            size=self.combo_size.currentText(),
            age=self.combo_age.currentText(),
        )
        self.settings.duplicates_mode = self.combo_dups.currentText()
        self._save_settings_with_feedback("Optionen")
        # proceed to scan
        if not self._start_scan():
            return
        self.stack.setCurrentWidget(self.page_scan)

    # ---------------------------
    # Page 3: Scan & Summary
    def _setup_scan_page(self) -> None:
        layout = QVBoxLayout(self.page_scan_content)
        self.lbl_scan_title = QLabel("<h2>Schritt 3/4 – Analyse</h2>")
        layout.addWidget(self.lbl_scan_title)
        self.lbl_scan_status = QLabel("Noch nicht gestartet.")
        self.lbl_scan_status.setWordWrap(True)
        layout.addWidget(self.lbl_scan_status)

        # Hinweis, wie die Trefferliste genutzt wird
        self.lbl_scan_help = QLabel(
            "<b>Trefferliste:</b> Wählen Sie die gefundenen Dateien aus, die in den Plan übernommen werden sollen. "
            "Ohne Auswahl werden alle Treffer verwendet. Die Liste ist farblich kodiert: blau = Bilder, "
            "lila = Videos, orange = Archive, grau = andere Dateien. Unter der Sortierauswahl finden Sie "
            "Buttons wie 'Nur Bilder', um schnell nur einen Dateityp zu markieren."
        )
        self.lbl_scan_help.setWordWrap(True)
        layout.addWidget(self.lbl_scan_help)
        self.lbl_scan_fixed_help = QLabel(
            "<b>Feste Hilfe:</b> Tastaturweg: Tab/Shift+Tab zum Navigieren, Enter zum Bestätigen. "
            "Kontrast-Hinweis: Bei schlechter Lesbarkeit Theme auf High-Contrast stellen. "
            "Nächste Aktion: Analyse starten und dann Treffer für den Plan markieren."
        )
        self.lbl_scan_fixed_help.setWordWrap(True)
        self.lbl_scan_fixed_help.setAccessibleName("Feste Hilfe Analyse")
        self.lbl_scan_fixed_help.setAccessibleDescription(
            "Kurze barrierearme Hilfe für Tastatur-Navigation, Kontrast und nächste Aktion im Analyseschritt"
        )
        self.lbl_scan_fixed_help.setToolTip(
            "Kurze Hilfe zu Tastaturweg, Kontrast und nächster Aktion"
        )
        layout.addWidget(self.lbl_scan_fixed_help)

        # Sortierfeld für die Trefferliste: Name oder Größe
        sort_layout = QHBoxLayout()
        lbl_sort = QLabel("Sortieren nach:")
        lbl_sort.setAccessibleName("Sortierlabel")
        lbl_sort.setAccessibleDescription(
            "Beschriftung für die Sortierauswahl der Trefferliste"
        )
        self.combo_scan_sort = QComboBox()
        self.combo_scan_sort.addItems(["Name", "Größe"])
        self.combo_scan_sort.setAccessibleName("Sortierauswahl")
        self.combo_scan_sort.setAccessibleDescription(
            "Sortieroptionen für die Trefferliste: alphabetisch oder nach Dateigröße"
        )
        self.combo_scan_sort.setToolTip(
            "Sortiert die Trefferliste entweder nach Dateiname oder nach Größe"
        )
        # Beim Wechsel der Sortieroption die Liste neu aufbauen
        self.combo_scan_sort.currentTextChanged.connect(self._sort_scan_results)
        # Größere Schaltfläche für bessere Bedienbarkeit
        self.combo_scan_sort.setMinimumHeight(34)
        sort_layout.addWidget(lbl_sort)
        sort_layout.addWidget(self.combo_scan_sort, 1)
        layout.addLayout(sort_layout)

        # Schnell-Auswahl für Dateitypen
        type_select_layout = QHBoxLayout()
        # Schaltfläche: Nur Bilder
        btn_only_images = QPushButton("Nur Bilder")
        btn_only_images.setAccessibleName("Nur Bilder wählen")
        btn_only_images.setAccessibleDescription(
            "Markiert nur Bilddateien (JPEG, PNG, etc.) in der Trefferliste."
        )
        btn_only_images.setToolTip(
            "Wählt nur die gefundenen Bilder aus und hebt alle anderen Auswahlmöglichkeiten auf"
        )
        btn_only_images.setMinimumHeight(38)
        btn_only_images.clicked.connect(lambda: self._select_scan_by_type("images"))
        # Schaltfläche: Nur Videos
        btn_only_videos = QPushButton("Nur Videos")
        btn_only_videos.setAccessibleName("Nur Videos wählen")
        btn_only_videos.setAccessibleDescription(
            "Markiert nur Videodateien (z. B. MP4) in der Trefferliste."
        )
        btn_only_videos.setToolTip(
            "Wählt nur die gefundenen Videos aus und hebt alle anderen Auswahlmöglichkeiten auf"
        )
        btn_only_videos.setMinimumHeight(38)
        btn_only_videos.clicked.connect(lambda: self._select_scan_by_type("videos"))
        # Schaltfläche: Nur Archive
        btn_only_archives = QPushButton("Nur Archive")
        btn_only_archives.setAccessibleName("Nur Archive wählen")
        btn_only_archives.setAccessibleDescription(
            "Markiert nur Archivdateien (ZIP, RAR) in der Trefferliste."
        )
        btn_only_archives.setToolTip(
            "Wählt nur die gefundenen Archive aus und hebt alle anderen Auswahlmöglichkeiten auf"
        )
        btn_only_archives.setMinimumHeight(38)
        btn_only_archives.clicked.connect(lambda: self._select_scan_by_type("archives"))
        # Schaltfläche: Nur Andere
        btn_only_other = QPushButton("Nur Andere")
        btn_only_other.setAccessibleName("Nur andere Dateien wählen")
        btn_only_other.setAccessibleDescription(
            "Markiert nur sonstige Dateitypen, die nicht als Bilder, Videos oder Archive erkannt wurden."
        )
        btn_only_other.setToolTip(
            "Wählt nur die sonstigen gefundenen Dateien aus und hebt alle anderen Auswahlmöglichkeiten auf"
        )
        btn_only_other.setMinimumHeight(38)
        btn_only_other.clicked.connect(lambda: self._select_scan_by_type("other"))
        # Schaltfläche: Alle auswählen
        btn_select_all_types = QPushButton("Alle")
        btn_select_all_types.setAccessibleName("Alle Dateien wählen")
        btn_select_all_types.setAccessibleDescription(
            "Markiert alle gefundenen Dateien in der Trefferliste."
        )
        btn_select_all_types.setToolTip(
            "Markiert die gesamte Trefferliste – alle Dateitypen werden berücksichtigt"
        )
        btn_select_all_types.setMinimumHeight(38)
        btn_select_all_types.clicked.connect(lambda: self._select_scan_by_type("all"))

        # Buttons zum Layout hinzufügen
        for btn in (
            btn_only_images,
            btn_only_videos,
            btn_only_archives,
            btn_only_other,
            btn_select_all_types,
        ):
            type_select_layout.addWidget(btn)
        layout.addLayout(type_select_layout)

        self.list_scan_results = QListWidget()
        self.list_scan_results.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_scan_results.setAccessibleName("Gefundene Dateien")
        self.list_scan_results.setAccessibleDescription(
            "Mehrfachauswahl der gefundenen Dateien für den nächsten Planungsschritt"
        )
        self.list_scan_results.setToolTip(
            "Mit Strg oder Umschalt mehrere Dateien markieren."
        )
        layout.addWidget(self.list_scan_results)

        self.lbl_scan_selection_status = QLabel(
            "Ausgewählt: 0 von 0 · Aktion: Bitte zuerst Analyse starten."
        )
        self.lbl_scan_selection_status.setWordWrap(True)
        self.lbl_scan_selection_status.setAccessibleName("Auswahlstatus Trefferliste")
        self.lbl_scan_selection_status.setAccessibleDescription(
            "Zeigt Anzahl markierter Treffer und die nächste sinnvolle Aktion"
        )
        layout.addWidget(self.lbl_scan_selection_status)

        selection_buttons = QHBoxLayout()
        self.btn_select_all_scan = QPushButton("Alle markieren")
        self.btn_select_all_scan.clicked.connect(self.list_scan_results.selectAll)
        self.btn_select_none_scan = QPushButton("Auswahl löschen")
        self.btn_select_none_scan.clicked.connect(self.list_scan_results.clearSelection)
        self.btn_copy_selected_paths = QPushButton("Auswahlpfade kopieren")
        self.btn_copy_selected_paths.setToolTip(
            "Kopiert die vollständigen Dateipfade der markierten Treffer in die Zwischenablage"
        )
        self.btn_copy_selected_paths.clicked.connect(self._copy_selected_scan_paths)
        for button in (
            self.btn_select_all_scan,
            self.btn_select_none_scan,
            self.btn_copy_selected_paths,
        ):
            button.setMinimumHeight(38)
            selection_buttons.addWidget(button)
        layout.addLayout(selection_buttons)
        self.list_scan_results.itemSelectionChanged.connect(
            self._update_scan_selection_status
        )
        self._update_scan_selection_status()

        # Navigation
        nav = QHBoxLayout()
        btn_prev = QPushButton("← Zurück")
        btn_prev.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_options))
        self.btn_next_plan = QPushButton("Weiter →")
        self.btn_next_plan.clicked.connect(self._scan_next)
        nav.addWidget(btn_prev)
        nav.addWidget(self.btn_next_plan)
        layout.addLayout(nav)

    def _start_scan(self) -> bool:
        perm_ok, perm_message, perm_steps = self._check_folder_permissions(
            require_write=False
        )
        if not perm_ok:
            self._show_error_with_mini_help(
                title="Linux-Berechtigungen prüfen",
                happened_text=perm_message,
                next_clicks=perm_steps,
            )
            return False

        self.lbl_scan_status.setText("Scanne Ordner… Bitte warten.")
        QApplication.processEvents()
        # parse thresholds
        size_bytes = _parse_size(self.settings.filters.size)
        age_secs = _parse_age(self.settings.filters.age)
        types = self.settings.filters.types
        assert self.root_path, "root_path sollte gesetzt sein"
        results = scan_directory(self.root_path, types, size_bytes, age_secs)
        dups = detect_duplicates(results, self.settings.duplicates_mode)
        self.scan_results = results
        self.duplicates_map = dups
        total_files = len(results)
        dup_groups = len(dups)
        total_size = sum(r.size for r in results)
        size_mb = total_size / (1024 * 1024)
        self.lbl_scan_status.setText(
            f"{perm_message}<br/>Gefundene Dateien: {total_files}<br/>Duplikat-Gruppen: {dup_groups}<br/>Gesamtgröße: {size_mb:.2f} MB"
        )
        # Ergebnisse speichern und Liste sortiert aufbauen
        self.list_scan_results.clear()
        # sortierte Liste anhand der aktuellen Sortiereinstellung aufbauen
        self._sort_scan_results()
        # Button "Weiter" nur aktivieren, wenn Dateien vorhanden sind
        self.btn_next_plan.setEnabled(total_files > 0)
        # Nach dem Sortieren die Auswahlanzeige aktualisieren
        self._update_scan_selection_status()
        return True

    def _format_scan_hit_row_text(self, hit_path: str, size_mb: float) -> str:
        cleaned_path = hit_path.strip()
        if not cleaned_path:
            raise ValueError(
                "Pfadtext ist leer. Nächster Schritt: Analyse erneut starten und nur gültige Treffer anzeigen."
            )
        if size_mb < 0:
            raise ValueError(
                "Dateigröße ist negativ. Nächster Schritt: Scan erneut starten und Dateisystem prüfen."
            )

        max_visible_chars = 72
        if len(cleaned_path) > max_visible_chars:
            short_path = f"…{cleaned_path[-(max_visible_chars - 1):]}"
        else:
            short_path = cleaned_path
        row_text = f"{short_path} · {size_mb:.2f} MB"
        if "MB" not in row_text:
            raise RuntimeError(
                "Treffertext unvollständig. Nächster Schritt: Anzeigeformat prüfen und erneut analysieren."
            )
        return row_text

    def _sort_scan_results(self) -> None:
        """Sortiert die Scan-Ergebnisse nach Name oder Größe und aktualisiert die Liste.

        Diese Methode liest die aktuelle Auswahl aus dem Sortierfeld (Name/Größe) und
        ordnet die interne Liste `scan_results` entsprechend. Anschließend wird
        die `list_scan_results` neu aufgebaut. Sie wird auch beim Scan-Aufruf
        genutzt, um die anfängliche Sortierung zu übernehmen.

        Die Sortierung erfolgt stabil, d. h. bei gleicher Größe bleibt die
        alphabetische Reihenfolge erhalten. Größere Dateien erscheinen zuerst,
        wenn "Größe" gewählt ist.
        """
        # Wenn noch keine Ergebnisse vorliegen, abbrechen
        if not hasattr(self, "scan_results") or not isinstance(self.scan_results, list):
            return
        # Prüfen, ob das Sortierfeld vorhanden ist (kann im Test fehlen)
        sort_field = getattr(self, "combo_scan_sort", None)
        if sort_field is None:
            return
        criterion = sort_field.currentText().strip().lower()
        # Erstelle sortierte Liste nach gewähltem Kriterium
        if criterion == "größe":
            # Nach Dateigröße (Bytes) absteigend, dann nach Pfad
            sorted_results = sorted(
                self.scan_results,
                key=lambda r: (-r.size, str(r.path).lower()),
            )
        else:
            # Standard: alphabetisch nach Pfad (case-insensitive)
            sorted_results = sorted(
                self.scan_results,
                key=lambda r: str(r.path).lower(),
            )
        # Merke sortierte Liste für spätere Planung
        self.scan_results = sorted_results
        # Liste neu aufbauen
        self.list_scan_results.clear()
        # Farbzuordnung für unterschiedliche Dateitypen
        color_map = {
            "images": QColor("#eaf4fc"),  # hellblau für Bilder
            "videos": QColor("#f5eafc"),  # helllila für Videos
            "archives": QColor("#fff5e6"),  # hellorange für Archive
            "other": QColor("#f0f0f0"),  # hellgrau für sonstige Dateien
        }
        for hit in sorted_results:
            path_str = str(hit.path).strip()
            size_mb = hit.size / (1024 * 1024)
            # Formatierte Zeile: gekürzter Pfad mit Größe
            row = QListWidgetItem(self._format_scan_hit_row_text(path_str, size_mb))
            row.setData(Qt.UserRole, path_str)
            row.setToolTip(path_str)
            # Setze Hintergrundfarbe je nach Datei-Typ
            file_type = getattr(hit, "file_type", "other")
            bg_color = color_map.get(file_type, QColor("#ffffff"))
            row.setBackground(bg_color)
            self.list_scan_results.addItem(row)
        # Nach Sortierung gesamte Liste markieren, um keine unabsichtliche Verwirrung zu erzeugen
        if self.list_scan_results.count() > 0:
            self.list_scan_results.selectAll()
        self._update_scan_selection_status()

    def _copy_selected_scan_paths(self) -> None:
        selected_paths = [
            str(item.data(Qt.UserRole)).strip()
            for item in self.list_scan_results.selectedItems()
            if str(item.data(Qt.UserRole)).strip()
        ]
        if not selected_paths:
            self._show_error_with_mini_help(
                title="Keine Auswahl zum Kopieren",
                happened_text="Bitte markieren Sie mindestens eine Datei in der Trefferliste.",
                next_clicks=[
                    "Erneut versuchen: In Schritt 3 eine oder mehrere Zeilen markieren.",
                    "Reparatur: Bei Bedarf zuerst auf 'Alle markieren' klicken.",
                    "Protokoll: Danach 'Auswahlpfade kopieren' erneut ausführen.",
                ],
            )
            return

        QApplication.clipboard().setText("\n".join(selected_paths))
        copied_count = len(selected_paths)
        self.lbl_scan_selection_status.setText(
            f"Ausgewählt: {copied_count} von {self.list_scan_results.count()} · Aktion: Pfade in Zwischenablage kopiert."
        )

    def _select_scan_by_type(self, file_type: str) -> None:
        """Markiert Treffer in der Scan-Liste nach Dateityp.

        Diese Methode ermöglicht es, schnell nur bestimmte Dateitypen auszuwählen.
        Wird "images", "videos", "archives" oder "other" übergeben, werden nur
        die entsprechenden Treffer markiert; bei "all" wird die gesamte Liste markiert.
        Anschließend wird der Auswahlstatus aktualisiert.
        """
        # Abbrechen, wenn keine Ergebnisse vorhanden sind
        if not hasattr(self, "scan_results") or not self.scan_results:
            return
        # Bei "all" einfach alle markieren
        if file_type == "all":
            self.list_scan_results.selectAll()
            self._update_scan_selection_status()
            return
        # Zunächst Auswahl löschen
        self.list_scan_results.clearSelection()
        # Alle Treffer durchgehen und passende auswählen
        for index in range(self.list_scan_results.count()):
            # Sicherstellen, dass index auch in scan_results existiert
            if index >= len(self.scan_results):
                continue
            hit = self.scan_results[index]
            if getattr(hit, "file_type", "other") == file_type:
                item = self.list_scan_results.item(index)
                if item:
                    item.setSelected(True)
        self._update_scan_selection_status()

    def _update_scan_selection_status(self) -> None:
        total_count = self.list_scan_results.count()
        selected_count = len(self.list_scan_results.selectedItems())
        has_entries = total_count > 0
        has_selection = selected_count > 0

        self.btn_select_all_scan.setEnabled(has_entries)
        self.btn_select_none_scan.setEnabled(has_entries)
        self.btn_copy_selected_paths.setEnabled(has_selection)

        if not has_entries:
            action_hint = "Bitte zuerst Analyse starten."
        elif not has_selection:
            action_hint = (
                "Mindestens eine Datei markieren oder auf 'Alle markieren' klicken."
            )
        else:
            action_hint = (
                "Sie können mit 'Weiter' planen oder die Auswahlpfade kopieren."
            )

        self.lbl_scan_selection_status.setText(
            f"Ausgewählt: {selected_count} von {total_count} · Aktion: {action_hint}"
        )

    def _scan_next(self) -> None:
        perm_ok, perm_message, perm_steps = self._check_folder_permissions(
            require_write=True
        )
        if not perm_ok:
            self._show_error_with_mini_help(
                title="Linux-Berechtigungen prüfen",
                happened_text=perm_message,
                next_clicks=perm_steps,
            )
            return

        # build plan
        # compute trash directory under download_dir
        assert self.root_path, "root_path sollte gesetzt sein"
        trash_dir = self.root_path / ".downloads_organizer_trash"
        trash_dir.mkdir(parents=True, exist_ok=True)
        selected_paths = {
            str(item.data(Qt.UserRole)).strip()
            for item in self.list_scan_results.selectedItems()
            if str(item.data(Qt.UserRole)).strip()
        }
        selected_scan_results = [
            hit for hit in self.scan_results if str(hit.path) in selected_paths
        ]
        if not selected_scan_results:
            self._show_error_with_mini_help(
                title="Keine Dateien markiert",
                happened_text=(
                    "Bitte markieren Sie mindestens eine gefundene Datei für den Plan."
                ),
                next_clicks=[
                    "Erneut versuchen: In Schritt 3 mindestens eine Zeile in der Trefferliste auswählen.",
                    "Reparatur: Optional zuerst auf 'Alle markieren' klicken.",
                ],
            )
            return

        selected_duplicates_map = {
            checksum: [
                candidate
                for candidate in candidates
                if str(candidate.path) in selected_paths
            ]
            for checksum, candidates in self.duplicates_map.items()
        }
        selected_duplicates_map = {
            checksum: candidates
            for checksum, candidates in selected_duplicates_map.items()
            if len(candidates) > 1
        }

        self.plan = build_plan(
            selected_scan_results,
            selected_duplicates_map,
            self.root_path,
            trash_dir,
        )
        if self.plan is None:
            raise RuntimeError(
                "Plan-Erstellung fehlgeschlagen. Nächster Schritt: Einstellungen prüfen und erneut analysieren."
            )
        self.stack.setCurrentWidget(self.page_plan)
        self._refresh_plan_page()

    # ---------------------------
    # Page 4: Plan & Execute
    def _setup_plan_page(self) -> None:
        layout = QVBoxLayout(self.page_plan_content)
        self.lbl_plan_title = QLabel("<h2>Schritt 4/4 – Plan und Ausführung</h2>")
        layout.addWidget(self.lbl_plan_title)
        self.lbl_plan_summary = QLabel("Plan ist noch nicht erstellt.")
        self.lbl_plan_summary.setWordWrap(True)
        layout.addWidget(self.lbl_plan_summary)
        self.lbl_plan_fixed_help = QLabel(
            "<b>Feste Hilfe:</b> Tastaturweg: Tab/Shift+Tab zwischen Liste und Buttons, Enter zum Ausführen. "
            "Kontrast-Hinweis: Für klare Lesbarkeit bei Bedarf High-Contrast-Theme aktivieren. "
            "Nächste Aktion: Plan prüfen und danach mit 'Ausführen' bestätigen."
        )
        self.lbl_plan_fixed_help.setWordWrap(True)
        self.lbl_plan_fixed_help.setAccessibleName("Feste Hilfe Plan")
        self.lbl_plan_fixed_help.setAccessibleDescription(
            "Kurze barrierearme Hilfe für Tastatur-Navigation, Kontrast und nächste Aktion im Planschritt"
        )
        self.lbl_plan_fixed_help.setToolTip(
            "Kurze Hilfe zu Tastaturweg, Kontrast und nächster Aktion"
        )
        layout.addWidget(self.lbl_plan_fixed_help)
        # List widget to show plan items
        self.list_plan = QListWidget()
        # Plan-Liste mit Kontextmenü für Zielordner öffnen
        self.list_plan.setAccessibleName("Planierte Aktionen")
        self.list_plan.setAccessibleDescription(
            "Liste der geplanten Dateiaktionen. Mit Rechtsklick öffnet sich ein Menü, um den Zielordner zu öffnen."
        )
        # Aktiviert das benutzerdefinierte Kontextmenü
        self.list_plan.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_plan.customContextMenuRequested.connect(self._show_plan_context_menu)
        layout.addWidget(self.list_plan)
        # Buttons
        btns = QHBoxLayout()
        btn_prev = QPushButton("← Zurück")
        btn_prev.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_scan))
        self.btn_execute = QPushButton("Ausführen")
        self.btn_execute.clicked.connect(self._execute_plan)
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.clicked.connect(self._undo_last)
        btn_finish = QPushButton("Fertig")
        btn_finish.clicked.connect(self.close)
        btns.addWidget(btn_prev)
        btns.addWidget(self.btn_execute)
        btns.addWidget(self.btn_undo)
        btns.addWidget(btn_finish)
        layout.addLayout(btns)

    def _refresh_plan_page(self) -> None:
        if not self.plan:
            self.lbl_plan_summary.setText("Kein Plan verfügbar.")
            self.list_plan.clear()
            self.btn_execute.setEnabled(False)
            return
        count, total_bytes = self.plan.summary()
        total_mb = total_bytes / (1024 * 1024)
        self.lbl_plan_summary.setText(
            f"Vorgeschlagene Dateien: {count}\nGeschätzter Speicherplatz: {total_mb:.2f} MB"
        )
        self.list_plan.clear()
        for item in self.plan.items:
            # Zeile mit Quelle, Ziel und Begründung anzeigen
            text = f"{item.src}  →  {item.dest} ({item.reason})"
            li = QListWidgetItem(text)
            # Destinationspfad als UserRole speichern, damit Kontextmenü ihn nutzen kann
            li.setData(Qt.UserRole, str(item.dest))
            li.setToolTip(str(item.dest))
            self.list_plan.addItem(li)
        # Ausführen-Knopf nur aktivieren, wenn Aktionen vorhanden sind
        self.btn_execute.setEnabled(count > 0)

    def _execute_plan(self) -> None:
        if not self.plan:
            return

        perm_ok, perm_message, perm_steps = self._check_folder_permissions(
            require_write=True
        )
        if not perm_ok:
            self._show_error_with_mini_help(
                title="Linux-Berechtigungen prüfen",
                happened_text=perm_message,
                next_clicks=perm_steps,
            )
            return

        count = len(self.plan.items)
        # If exceed confirm threshold, ask
        if count > self.settings.confirm_threshold:
            reply = QMessageBox.question(
                self,
                "Bestätigung erforderlich",
                f"Es sollen {count} Dateien verschoben werden. Sind Sie sicher?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
        ok, msg = execute_move_plan(self.plan)
        QMessageBox.information(self, "Ausführen", msg)
        if ok:
            # Nach erfolgreicher Ausführung Verlaufsdaten speichern
            try:
                count_summary, total_bytes_summary = self.plan.summary()
                total_mb_summary = total_bytes_summary / (1024 * 1024)
                append_history(count_summary, total_mb_summary)
            except Exception:
                # Fehler beim Speichern des Verlaufs ignorieren – Verlauf ist optional
                pass

    def _create_quick_action_tile(
        self,
        *,
        label: str,
        tooltip: str,
        accessible_name: str,
        accessible_description: str,
        section: str,
    ) -> QPushButton:
        """Erstellt eine barrierearme Schnellstart-Kachel für das Raster mit validierten Eingaben."""

        clean_label = label.strip()
        clean_tooltip = tooltip.strip()
        clean_name = accessible_name.strip()
        clean_desc = accessible_description.strip()
        clean_section = section.strip()
        if not clean_label:
            raise ValueError(
                "Schnellstart-Label fehlt. Nächster Schritt: Bitte sichtbare Beschriftung setzen."
            )
        if not clean_tooltip:
            raise ValueError(
                "Schnellstart-Hilfe fehlt. Nächster Schritt: Bitte Tooltip in einfacher Sprache ergänzen."
            )
        if clean_section not in {"Medien", "Aufräumen"}:
            raise ValueError(
                "Schnellstart-Bereich ist ungültig. Nächster Schritt: 'Medien' oder 'Aufräumen' verwenden."
            )

        tile = QPushButton(clean_label)
        tile.setToolTip(f"Bereich {clean_section}: {clean_tooltip}")
        tile.setAccessibleName(clean_name)
        tile.setAccessibleDescription(f"{clean_desc}. Enter startet die Aktion direkt.")
        tile.setMinimumHeight(96)
        tile.setProperty("quickSection", clean_section.lower())
        tile.setProperty("quickTile", "true")
        tile.setObjectName(f"quick-tile-{clean_section.lower()}")

        if tile.minimumHeight() < 48:
            raise RuntimeError(
                "Schnellstart-Kachel zu klein. Nächster Schritt: Mindesthöhe auf mindestens 48 setzen."
            )
        if tile.property("quickTile") != "true":
            raise RuntimeError(
                "Schnellstart-Kachel-Stil fehlt. Nächster Schritt: Kachel-Stilmarkierung erneut setzen."
            )
        return tile

    def _create_standard_button(
        self,
        text: str,
        tooltip: str,
        callback,
        *,
        accessible_name: str | None = None,
        accessible_description: str | None = None,
    ) -> QPushButton:
        """
        Erstellt einen einheitlichen Button mit konsistenter Mindestgröße,
        Tooltip, AccessibleName und AccessibleDescription.

        Dies hilft, Barrierefreiheit und Lesbarkeit über die gesamte
        Oberfläche hinweg zu vereinheitlichen. Der Parameter ``callback``
        wird an das ``clicked``-Signal gebunden.
        """
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        if accessible_name:
            btn.setAccessibleName(accessible_name)
        if accessible_description:
            btn.setAccessibleDescription(accessible_description)
        # Einheitliche Mindesthöhe für Tastatur- und Touch‑Bedienung
        btn.setMinimumHeight(40)
        btn.clicked.connect(callback)
        return btn

    def _undo_last(self) -> None:
        ok, msg = undo_last()
        QMessageBox.information(self, "Undo", msg)
        # After undo, update list maybe
        # Nothing else to do

    def _show_plan_context_menu(self, pos) -> None:
        """Zeigt das Kontextmenü für die Plan-Liste und öffnet bei Auswahl den Zielordner.

        Bei Rechtsklick auf einen Eintrag wird ein kleines Menü mit der Option
        "Zielordner öffnen" angezeigt. Wird diese Option gewählt, so wird der
        entsprechende Zielordner im Dateimanager des Systems geöffnet. Enthält
        der Eintrag keinen gültigen Zielpfad, passiert nichts.

        Args:
            pos: Die Position des Rechtsklicks relativ zur Plan-Liste.
        """
        # Finde das Element unter der Klickposition
        item = self.list_plan.itemAt(pos)
        if item is None:
            return
        dest_path = item.data(Qt.UserRole)
        if not dest_path:
            return
        # Erstelle Menü mit einer Aktion
        menu = QMenu(self)
        action_open = menu.addAction("Zielordner öffnen")
        # Menü an der korrekten Bildschirmposition anzeigen
        selected_action = menu.exec_(self.list_plan.mapToGlobal(pos))
        if selected_action == action_open:
            # Öffne den Ordner im System-Dateimanager
            url = QUrl.fromLocalFile(dest_path)
            QDesktopServices.openUrl(url)


def main() -> int:
    """Starte die GUI und lade optionale Plugins.

    Vor dem Erstellen der Qt-Anwendung wird das Plugin-Verzeichnis
    durchsucht. Gefundene Plugins werden initialisiert, dürfen aber
    nicht zu einem Startabbruch führen. Dies ermöglicht eine
    flexible Erweiterung, ohne dass Nutzer die Kernanwendung
    modifizieren müssen.
    """
    # Optional vorhandene Plugins laden
    from pathlib import Path

    from core.plugins import discover_plugins

    plugins_dir = Path(__file__).resolve().parent.parent / "plugins"
    for plugin in discover_plugins(plugins_dir):
        try:
            # Initialisiere Plugin ohne spezifische Einstellungen;
            # zukünftige Plugins können hier Einstellungen entgegennehmen
            plugin.init(None)
        except Exception:
            # Fehler im Plugin dürfen die Anwendung nicht blockieren
            continue

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
