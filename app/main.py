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
        "dark": "QWidget { background-color: #2b2b2b; color: #ffffff; } QPushButton { background-color: #3c3f41; color: #ffffff; padding: 6px; } QPushButton:hover { background-color: #505357; }",
        "kontrast": "QWidget { background-color: #000000; color: #ffff00; } QPushButton { background-color: #000000; color: #ffff00; border: 2px solid #ffff00; padding: 6px; } QPushButton:hover { background-color: #222222; }",
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
        layout.addWidget(title)
        # Folder selection
        hl_folder = QHBoxLayout()
        self.lbl_folder = QLabel("Kein Ordner ausgewählt")
        btn_choose = QPushButton("Ordner wählen…")
        hl_folder.addWidget(self.lbl_folder)
        hl_folder.addWidget(btn_choose)
        layout.addLayout(hl_folder)
        btn_choose.clicked.connect(self._choose_folder)
        # Theme selection
        hl_theme = QHBoxLayout()
        hl_theme.addWidget(QLabel("Farbschema:"))
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["hell", "dunkel", "kontrast", "senior"])
        theme_display = {"light": "hell", "dark": "dunkel"}.get(self.settings.theme, self.settings.theme)
        self.combo_theme.setCurrentText(theme_display)
        hl_theme.addWidget(self.combo_theme)
        self.cb_large = QCheckBox("Großer Text")
        self.cb_large.setChecked(self.settings.large_text)
        hl_theme.addWidget(self.cb_large)
        layout.addLayout(hl_theme)
        # Navigation buttons
        btn_next = QPushButton("Weiter →")
        btn_next.clicked.connect(self._welcome_next)
        layout.addWidget(btn_next)

    def _choose_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Ordner auswählen", str(Path.home() / "Downloads"))
        if path:
            self.lbl_folder.setText(path)
            self.root_path = Path(path)

    def _welcome_next(self) -> None:
        # Save theme settings
        selected_theme = self.combo_theme.currentText()
        self.settings.theme = {"hell": "light", "dunkel": "dark"}.get(selected_theme, selected_theme)
        self.settings.large_text = self.cb_large.isChecked()
        self.apply_theme(self.settings.theme, self.settings.large_text)
        # Ensure folder selected
        if not self.root_path:
            QMessageBox.warning(self, "Fehlende Angabe", "Bitte wählen Sie einen Ordner aus.")
            return
        self.settings.download_dir = str(self.root_path)
        self.settings.save()
        self.stack.setCurrentWidget(self.page_options)

    # ---------------------------
    # Page 2: Options
    def _setup_options_page(self) -> None:
        layout = QVBoxLayout(self.page_options)
        title = QLabel("<h2>Schritt 2/4 – Optionen</h2>")
        layout.addWidget(title)
        # Presets buttons
        hl_presets = QHBoxLayout()
        btn_senior = QPushButton("Preset: Senior")
        btn_std = QPushButton("Preset: Standard")
        btn_power = QPushButton("Preset: Power")
        hl_presets.addWidget(btn_senior)
        hl_presets.addWidget(btn_std)
        hl_presets.addWidget(btn_power)
        layout.addLayout(hl_presets)
        btn_senior.clicked.connect(lambda: self._load_preset("senior"))
        btn_std.clicked.connect(lambda: self._load_preset("standard"))
        btn_power.clicked.connect(lambda: self._load_preset("power"))
        self.current_preset_label = QLabel("Aktuelles Preset: " + self.settings.presets)
        layout.addWidget(self.current_preset_label)
        # File type filters
        layout.addWidget(QLabel("Dateitypen einbeziehen:"))
        self.cb_images = QCheckBox("Bilder")
        self.cb_videos = QCheckBox("Videos")
        self.cb_archives = QCheckBox("Archive")
        self.cb_other = QCheckBox("Andere")
        layout.addWidget(self.cb_images)
        layout.addWidget(self.cb_videos)
        layout.addWidget(self.cb_archives)
        layout.addWidget(self.cb_other)
        # Size threshold
        hl_size = QHBoxLayout()
        hl_size.addWidget(QLabel("Min. Größe:"))
        self.combo_size = QComboBox()
        self.combo_size.addItems(["any", "10MB", "50MB", "100MB"])
        hl_size.addWidget(self.combo_size)
        layout.addLayout(hl_size)
        # Age threshold
        hl_age = QHBoxLayout()
        hl_age.addWidget(QLabel("Min. Alter:"))
        self.combo_age = QComboBox()
        self.combo_age.addItems(["any", "30d", "180d", "365d"])
        hl_age.addWidget(self.combo_age)
        layout.addLayout(hl_age)
        # Duplicates mode
        hl_dup = QHBoxLayout()
        hl_dup.addWidget(QLabel("Duplikate:"))
        self.combo_dups = QComboBox()
        self.combo_dups.addItems(["none", "quick", "safe"])
        hl_dup.addWidget(self.combo_dups)
        layout.addLayout(hl_dup)
        # Navigation buttons
        nav = QHBoxLayout()
        btn_prev = QPushButton("← Zurück")
        btn_prev.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_welcome))
        btn_next = QPushButton("Weiter →")
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
