from __future__ import annotations

import json
import os
import platform
import sys
from html import escape
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QBoxLayout, QCheckBox, QComboBox,
                               QFileDialog, QHBoxLayout, QLabel, QListWidget,
                               QListWidgetItem, QMainWindow, QMessageBox,
                               QPushButton, QStackedWidget, QVBoxLayout,
                               QWidget)

from core.executor import execute_move_plan, undo_last
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
        "kontrast": "Maximaler Kontrast mit sehr klaren Fokusrahmen für Sehunterstützung.",
        "blau": "Ruhiges blaues Schema mit klaren Konturen und guter Erkennbarkeit.",
        "senior": "Extra große Schrift und starke Umrandungen für ruhiges Lesen.",
    }

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
        self.setWindowTitle("Downloads Organizer")
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
        self._create_pages()
        self.apply_theme(self.settings.theme, self.settings.large_text)

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
        self.combo_size.setCurrentText(size_value)
        self.combo_age.setCurrentText(age_value)
        self.combo_dups.setCurrentText(dup_mode)
        output_text = f"<b>Aktives Aufräumziel:</b> {help_text}"
        if not output_text.strip():
            raise RuntimeError(
                "Aufräumhilfe fehlt. Nächster Schritt: Bitte Auswahl erneut setzen."
            )
        self.lbl_cleanup_goal_hint.setText(output_text)

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
        "kontrast": "kontrast",
        "blau": "blau",
        "senior": "senior",
    }
    THEME_KEY_TO_DISPLAY = {
        "light": "hell",
        "dark": "dunkel",
        "kontrast": "kontrast",
        "blau": "blau",
        "senior": "senior",
    }
    PREVIEW_SCALE_LABELS = {
        "100 %": 1.0,
        "115 %": 1.15,
        "130 %": 1.3,
        "150 %": 1.5,
    }
    PREVIEW_POSITION_MODES = {
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
        style = self.STYLES[resolved_theme]
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
        self.combo_theme.setCurrentText(theme_display)
        self.cb_large.setChecked(large_text)
        self.combo_preview_scale.setCurrentText(scale_text)
        self.combo_preview_position.setCurrentText(position_text)
        self._sync_theme_preview()

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
        scale_factor = self._resolve_preview_scale_factor(selected_scale)
        self._apply_preview_scale(scale_factor)

        selected_position = self.combo_preview_position.currentText().strip()
        position_mode = self._resolve_preview_position_mode(selected_position)
        self._apply_preview_layout(position_mode)

        preview_title = self.THEME_KEY_TO_DISPLAY.get(resolved_theme, "kontrast")
        position_title = selected_position.lower()
        a11y_hint = self._build_theme_a11y_hint(resolved_theme, large_text_enabled)
        preview_text = (
            "<b>Live-Vorschau aktiv</b><br/>"
            f"Theme: <b>{preview_title}</b> · Großer Text: "
            f"<b>{'an' if large_text_enabled else 'aus'}</b><br/>"
            f"Bereichsskalierung: <b>{selected_scale}</b> · Position: <b>{position_title}</b><br/>"
            f"A11y-Hinweis (Zugänglichkeit): {a11y_hint}<br/>"
            "Beispiel unten zeigt Button, Liste und Kontrast in Echtzeit."
        )
        if not preview_text.strip():
            raise RuntimeError(
                "Vorschauausgabe fehlt. Nächster Schritt: Bitte Theme-Auswahl erneut öffnen."
            )
        self.lbl_theme_preview_info.setText(preview_text)

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

    def _create_pages(self) -> None:
        self.page_welcome = QWidget()
        self._setup_welcome_page()
        self.stack.addWidget(self.page_welcome)

        self.page_options = QWidget()
        self._setup_options_page()
        self.stack.addWidget(self.page_options)

        self.page_scan = QWidget()
        self._setup_scan_page()
        self.stack.addWidget(self.page_scan)

        self.page_plan = QWidget()
        self._setup_plan_page()
        self.stack.addWidget(self.page_plan)

    # ---------------------------
    # Page 1: Welcome & Folder/Theme
    def _setup_welcome_page(self) -> None:
        layout = QVBoxLayout(self.page_welcome)
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

        preview_shell = QHBoxLayout()
        preview_shell.setSpacing(12)

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
            ]
        )
        self.list_category_nav.setCurrentRow(0)
        preview_shell.addWidget(self.list_category_nav)

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
                "border: 1px solid #6b7280; border-radius: 10px; padding: 10px;"
            )
            card.setAccessibleName("Aktionskarte Vorschau")
            card.setAccessibleDescription(
                "Vorschau einer zentralen Aktionskarte in der neuen Hauptansicht"
            )
            self.preview_action_cards.append(card)
            cards_wrap.addWidget(card)

        preview_shell.addLayout(cards_wrap, stretch=1)
        layout.addLayout(preview_shell)

        self.lbl_dashboard_info = QLabel()
        self.lbl_dashboard_info.setWordWrap(True)
        self.lbl_dashboard_info.setTextFormat(Qt.RichText)
        self.lbl_dashboard_info.setAccessibleName("Schnellübersicht")
        self.lbl_dashboard_info.setAccessibleDescription(
            "Zeigt aktuelle Einstellungen und Hilfehinweise"
        )
        self.lbl_dashboard_info.setStyleSheet(
            "border: 1px solid #6b7280; border-radius: 10px; padding: 10px;"
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
        # Theme selection
        hl_theme = QHBoxLayout()
        lbl_theme = QLabel("Farbschema:")
        hl_theme.addWidget(lbl_theme)
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["hell", "dunkel", "kontrast", "blau", "senior"])
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

        hl_preview_controls = QHBoxLayout()
        lbl_preview_scale = QLabel("Bereichsskalierung:")
        self.combo_preview_scale = QComboBox()
        self.combo_preview_scale.addItems(list(self.PREVIEW_SCALE_LABELS.keys()))
        self.combo_preview_scale.setCurrentText("115 %")
        self.combo_preview_scale.setToolTip(
            "Steuert die Größe der Vorschau-Fläche für bessere Lesbarkeit"
        )
        self.combo_preview_scale.setAccessibleName("Bereichsskalierung Vorschau")
        self.combo_preview_scale.setMinimumWidth(140)
        lbl_preview_scale.setBuddy(self.combo_preview_scale)
        hl_preview_controls.addWidget(lbl_preview_scale)
        hl_preview_controls.addWidget(self.combo_preview_scale)

        lbl_preview_position = QLabel("Vorschau-Position:")
        self.combo_preview_position = QComboBox()
        self.combo_preview_position.addItems(list(self.PREVIEW_POSITION_MODES.keys()))
        self.combo_preview_position.setCurrentText("Aktion links · Liste rechts")
        self.combo_preview_position.setToolTip(
            "Legt fest, ob Aktion und Liste links, rechts oder untereinander liegen"
        )
        self.combo_preview_position.setAccessibleName("Vorschau-Position wählen")
        self.combo_preview_position.setMinimumWidth(220)
        lbl_preview_position.setBuddy(self.combo_preview_position)
        hl_preview_controls.addWidget(lbl_preview_position)
        hl_preview_controls.addWidget(self.combo_preview_position)
        layout.addLayout(hl_preview_controls)

        self.lbl_theme_preview_info = QLabel()
        self.lbl_theme_preview_info.setWordWrap(True)
        self.lbl_theme_preview_info.setAccessibleName("Theme Live-Vorschau Hinweis")
        self.lbl_theme_preview_info.setAccessibleDescription(
            "Zeigt den aktiven Vorschau-Status für Theme und großen Text"
        )
        layout.addWidget(self.lbl_theme_preview_info)

        self.preview_row = QBoxLayout(QBoxLayout.LeftToRight)
        self.preview_action_button = QPushButton("Beispiel: Primäraktion")
        self.preview_action_button.setEnabled(False)
        self.preview_action_button.setToolTip(
            "Nur Vorschau: So sieht ein Aktionsbutton im gewählten Theme aus"
        )
        self.preview_row.addWidget(self.preview_action_button)
        self.preview_list = QListWidget()
        self.preview_list.setAccessibleName("Theme Vorschau-Liste")
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
            "• Schnellwahl: Mit <b>Alt+O</b> öffnen Sie direkt die Ordnerauswahl.<br/>"
            "• Schnellhilfe Lesbarkeit: <b>Alt+K</b> maximiert Kontrast, <b>Alt+L</b> lädt die ausgewogene Ansicht.<br/>"
            "• Bei Unsicherheit starten Sie mit dem Schema <b>kontrast</b>.<br/>"
            "• Für ruhige, helle Farben wählen Sie <b>blau</b>.<br/>"
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
        # Navigation buttons
        btn_next = QPushButton("Weiter →")
        btn_next.setToolTip("Speichert die Auswahl und geht zum nächsten Schritt")
        btn_next.setAccessibleName("Zum nächsten Schritt")
        btn_next.clicked.connect(self._welcome_next)
        layout.addWidget(btn_next)
        self._refresh_dashboard_info()

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

        self.lbl_dashboard_info.setText(
            "<b>Haupt-Dashboard (Schnellübersicht)</b><br/>"
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
            "4) Prüfen Sie im Dashboard, ob der Speicherstatus auf ✅ steht."
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
        layout = QVBoxLayout(self.page_options)
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
        layout = QVBoxLayout(self.page_scan)
        self.lbl_scan_title = QLabel("<h2>Schritt 3/4 – Analyse</h2>")
        layout.addWidget(self.lbl_scan_title)
        self.lbl_scan_status = QLabel("Noch nicht gestartet.")
        self.lbl_scan_status.setWordWrap(True)
        layout.addWidget(self.lbl_scan_status)
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
        # disable next if nothing to move
        self.btn_next_plan.setEnabled(total_files > 0)
        return True

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
        self.plan = build_plan(
            self.scan_results, self.duplicates_map, self.root_path, trash_dir
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
        layout = QVBoxLayout(self.page_plan)
        self.lbl_plan_title = QLabel("<h2>Schritt 4/4 – Plan und Ausführung</h2>")
        layout.addWidget(self.lbl_plan_title)
        self.lbl_plan_summary = QLabel("Plan ist noch nicht erstellt.")
        self.lbl_plan_summary.setWordWrap(True)
        layout.addWidget(self.lbl_plan_summary)
        # List widget to show plan items
        self.list_plan = QListWidget()
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
            li = QListWidgetItem(f"{item.src}  →  {item.dest} ({item.reason})")
            self.list_plan.addItem(li)
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
            self._refresh_plan_page()

    def _undo_last(self) -> None:
        ok, msg = undo_last()
        QMessageBox.information(self, "Undo", msg)
        # After undo, update list maybe
        # Nothing else to do


def main() -> int:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
