from __future__ import annotations

import sys
import json
import platform
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QComboBox,
    QCheckBox,
    QMessageBox,
)

from core.settings import Settings, Filters
from core.logger import setup_logger
from core.selfcheck import run_selfcheck
from core.scanner import scan_directory, detect_duplicates, _parse_size, _parse_age
from core.planner import build_plan, ActionPlan
from core.executor import execute_move_plan, undo_last


LOGGER = setup_logger()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        ok, msg = run_selfcheck()
        if not ok:
            QMessageBox.critical(self, "Fehler", msg)
            raise SystemExit(msg)
        self.settings = Settings.load()
        self.root_path: Path | None = None
        self.plan: ActionPlan | None = None
        self.scan_results = []
        self.duplicates_map = {}
        self.setWindowTitle("Downloads Organizer")
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
        self._create_pages()
        self.apply_theme(self.settings.theme, self.settings.large_text)

    # Theme stylesheets
    STYLES = {
        "light": "",
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
        "senior": "QWidget { background-color: #ffffff; color: #000000; font-size: 18pt; } QPushButton { background-color: #e0e0e0; color: #000000; padding: 10px; font-size: 16pt; } QPushButton:hover { background-color: #c0c0c0; }",
    }

    def apply_theme(self, theme: str, large_text: bool) -> None:
        style = self.STYLES.get(theme, "")
        if large_text and theme != "senior":
            # Increase base font size
            style += " QWidget { font-size: 14pt; }"
        self.setStyleSheet(style)

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
        title = QLabel("<h2>Schritt 1/4 – Ordner und Anzeige</h2>")
        title.setAccessibleName("Schrittanzeige")
        title.setAccessibleDescription("Überschrift für den ersten Schritt des Assistenten")
        layout.addWidget(title)
        intro = QLabel(
            "<b>Einfach starten:</b> Wählen Sie zuerst Ihren Download-Ordner. "
            "Danach können Sie ein gut lesbares Farbschema auswählen."
        )
        intro.setWordWrap(True)
        intro.setAccessibleName("Einstiegshilfe")
        intro.setAccessibleDescription("Kurze Hilfe in einfacher Sprache für den Start")
        layout.addWidget(intro)
        self.lbl_dashboard_info = QLabel()
        self.lbl_dashboard_info.setWordWrap(True)
        self.lbl_dashboard_info.setTextFormat(Qt.RichText)
        self.lbl_dashboard_info.setAccessibleName("Schnellübersicht")
        self.lbl_dashboard_info.setAccessibleDescription("Zeigt aktuelle Einstellungen und Hilfehinweise")
        layout.addWidget(self.lbl_dashboard_info)
        # Folder selection
        hl_folder = QHBoxLayout()
        self.lbl_folder = QLabel("Kein Ordner ausgewählt")
        self.lbl_folder.setWordWrap(True)
        self.lbl_folder.setAccessibleName("Ausgewählter Ordner")
        btn_choose = QPushButton("Ordner wählen…")
        btn_choose.setToolTip("Öffnet den Dialog zur Ordnerauswahl")
        btn_choose.setAccessibleName("Ordner auswählen")
        btn_choose.setAccessibleDescription("Öffnet die Auswahl für den Download-Ordner")
        hl_folder.addWidget(self.lbl_folder)
        hl_folder.addWidget(btn_choose)
        layout.addLayout(hl_folder)
        btn_choose.clicked.connect(self._choose_folder)
        # Theme selection
        hl_theme = QHBoxLayout()
        lbl_theme = QLabel("Farbschema:")
        hl_theme.addWidget(lbl_theme)
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["hell", "dunkel", "kontrast", "senior"])
        self.combo_theme.setToolTip("Wählen Sie ein Farbschema mit guter Lesbarkeit")
        self.combo_theme.setAccessibleName("Farbschema")
        theme_display = {"light": "hell", "dark": "dunkel"}.get(self.settings.theme, self.settings.theme)
        self.combo_theme.setCurrentText(theme_display)
        lbl_theme.setBuddy(self.combo_theme)
        hl_theme.addWidget(self.combo_theme)
        self.cb_large = QCheckBox("Großer Text")
        self.cb_large.setChecked(self.settings.large_text)
        self.cb_large.setToolTip("Vergrößert Text für bessere Lesbarkeit")
        self.cb_large.setAccessibleName("Großer Text aktivieren")
        hl_theme.addWidget(self.cb_large)
        layout.addLayout(hl_theme)
        help_box = QLabel(
            "<b>Hilfe:</b><br/>"
            "• Tastatur: Mit <b>Tab</b> wechseln Sie zwischen Feldern.<br/>"
            "• Bei Unsicherheit starten Sie mit dem Schema <b>kontrast</b>.<br/>"
            "• Sie können Einstellungen später jederzeit ändern."
        )
        help_box.setWordWrap(True)
        help_box.setAccessibleName("Hilfebereich")
        help_box.setAccessibleDescription("Tipps für Bedienung und Lesbarkeit")
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
        folder_text = str(selected_folder) if selected_folder else "Noch kein Ordner festgelegt"
        active_types = ", ".join(self.settings.filters.types) if self.settings.filters.types else "keine"
        self.lbl_dashboard_info.setText(
            "<b>Haupt-Dashboard (Schnellübersicht)</b><br/>"
            f"• System: {platform.system()} {platform.release()}<br/>"
            f"• Aktueller Zielordner: {folder_text}<br/>"
            f"• Aktives Preset: {self.settings.presets}<br/>"
            f"• Dateitypen-Filter: {active_types}<br/>"
            f"• Duplikat-Prüfung: {self.settings.duplicates_mode}<br/><br/>"
            "<b>Hilfe in einfacher Sprache:</b><br/>"
            "1) Wählen Sie einen Ordner.<br/>"
            "2) Wählen Sie ein gut lesbares Farbschema.<br/>"
            "3) Drücken Sie <b>Weiter</b>, um die Analyse zu starten."
        )

    def _choose_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Ordner auswählen", str(Path.home() / "Downloads"))
        if path:
            self.lbl_folder.setText(path)
            self.root_path = Path(path)
            self._refresh_dashboard_info()

    def _welcome_next(self) -> None:
        # Save theme settings
        selected_theme = self.combo_theme.currentText()
        self.settings.theme = {"hell": "light", "dunkel": "dark"}.get(selected_theme, selected_theme)
        self.settings.large_text = self.cb_large.isChecked()
        self.apply_theme(self.settings.theme, self.settings.large_text)
        self._refresh_dashboard_info()
        # Ensure folder selected
        if not self.root_path:
            message = QMessageBox(self)
            message.setWindowTitle("Fehlende Angabe")
            message.setIcon(QMessageBox.Warning)
            message.setText("Bitte wählen Sie zuerst einen Ordner aus.")
            message.setInformativeText(
                "Nächster Schritt in einfacher Sprache:\n"
                "• Erneut versuchen: Ordnerauswahl noch einmal öffnen.\n"
                "• Reparatur: Hilfe bei häufigen Startproblemen anzeigen.\n"
                "• Protokoll: Ort der Log-Datei anzeigen."
            )
            message.setAccessibleName("Fehlende Ordnerauswahl")
            message.setAccessibleDescription("Dialog mit klaren nächsten Schritten für fehlende Ordnerauswahl")
            retry_btn = message.addButton("Erneut versuchen", QMessageBox.AcceptRole)
            repair_btn = message.addButton("Reparatur", QMessageBox.ActionRole)
            log_btn = message.addButton("Protokoll", QMessageBox.HelpRole)
            message.exec()

            clicked = message.clickedButton()
            if clicked == retry_btn:
                self._choose_folder()
            elif clicked == repair_btn:
                QMessageBox.information(
                    self,
                    "Reparaturhilfe",
                    "Bitte führen Sie im Projektordner den Befehl 'bash start.sh' aus.\n"
                    "Das Programm prüft automatisch wichtige Voraussetzungen und zeigt Rückmeldungen an.",
                )
            elif clicked == log_btn:
                log_path = Path(__file__).resolve().parent.parent / "logs" / "app.log"
                QMessageBox.information(
                    self,
                    "Protokollpfad",
                    f"Log-Datei: {log_path}\n"
                    "Diese Datei hilft bei der Fehlersuche und kann an den Support weitergegeben werden.",
                )
            return
        self.settings.download_dir = str(self.root_path)
        self.settings.save()
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

        preset_box = QLabel("<b>1) Preset auswählen</b><br/>Schneller Start mit sinnvollen Standardwerten")
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

        filters_box = QLabel("<b>2) Dateitypen auswählen</b><br/>Mindestens ein Typ muss aktiv sein")
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

        limits_box = QLabel("<b>3) Grenzen setzen</b><br/>Optional: Größe und Alter eingrenzen")
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

        duplicates_box = QLabel("<b>4) Duplikat-Prüfung</b><br/>Wählen Sie die Sicherheitstiefe")
        duplicates_box.setWordWrap(True)
        layout.addWidget(duplicates_box)
        hl_dup = QHBoxLayout()
        hl_dup.addWidget(QLabel("Duplikate:"))
        self.combo_dups = QComboBox()
        self.combo_dups.addItems(["none", "quick", "safe"])
        hl_dup.addWidget(self.combo_dups)
        layout.addLayout(hl_dup)

        footer_hint = QLabel("Tipp: Starten Sie mit Preset Standard. Danach können Sie bei Bedarf verfeinern.")
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
        p = Path(__file__).resolve().parent.parent / "data" / "presets" / f"{preset_name}.json"
        if p.exists():
            try:
                raw = json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Preset konnte nicht geladen werden: {e}")
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
            self.settings.save()
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
            QMessageBox.warning(self, "Keine Dateitypen", "Bitte wählen Sie mindestens einen Dateityp aus.")
            return
        self.settings.filters = Filters(types=types, size=self.combo_size.currentText(), age=self.combo_age.currentText())
        self.settings.duplicates_mode = self.combo_dups.currentText()
        self.settings.save()
        # proceed to scan
        self._start_scan()
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

    def _start_scan(self) -> None:
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
            f"Gefundene Dateien: {total_files}<br/>Duplikat-Gruppen: {dup_groups}<br/>Gesamtgröße: {size_mb:.2f} MB"
        )
        # disable next if nothing to move
        self.btn_next_plan.setEnabled(total_files > 0)

    def _scan_next(self) -> None:
        # build plan
        # compute trash directory under download_dir
        assert self.root_path, "root_path sollte gesetzt sein"
        trash_dir = self.root_path / ".downloads_organizer_trash"
        trash_dir.mkdir(parents=True, exist_ok=True)
        self.plan = build_plan(self.scan_results, self.duplicates_map, self.root_path, trash_dir)
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
