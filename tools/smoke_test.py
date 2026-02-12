"""Smoke test für das Provoware Clean Tool 2026.

Dieses Skript führt minimale Importe der Kernmodule und der GUI aus, um
sicherzustellen, dass zur Entwicklungszeit keine Importfehler auftreten.
"""

import importlib
import json
import os
import sys
import tempfile
from pathlib import Path


def run_core_settings_checks(settings_cls: type) -> None:
    """Run minimal core validation checks for settings handling."""
    if settings_cls is None:
        raise AssertionError("Settings-Klasse fehlt. Bitte Smoke-Test-Import prüfen.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        settings_path = Path(tmp_dir) / "settings.json"
        settings_path.write_text(
            json.dumps(
                {
                    "theme": "dark",
                    "confirm_threshold": "7",
                    "filters": {"types": ["pdf"], "size": "any", "age": "30d"},
                    "ui_texts": {"error_title": "Fehlerhinweis"},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        loaded = settings_cls.load(settings_path)
        if loaded.theme != "dark":
            raise AssertionError("Settings.load sollte das Theme korrekt übernehmen.")
        if loaded.confirm_threshold != 7:
            raise AssertionError(
                "Settings.load sollte numerische Schwellen korrekt umwandeln."
            )
        if loaded.ui_texts.get("error_title") != "Fehlerhinweis":
            raise AssertionError("Settings.load sollte UI-Texte korrekt übernehmen.")

        loaded.save(settings_path)
        saved = json.loads(settings_path.read_text(encoding="utf-8"))
        if saved.get("schema_version", 0) < 2:
            raise AssertionError("Settings.save sollte schema_version >= 2 schreiben.")
        if saved.get("file_revision", 0) < 1:
            raise AssertionError("Settings.save sollte file_revision erhöhen.")


def run_core_planner_checks(planner_module: object, scan_result_cls: type) -> None:
    """Run minimal core validation checks for planning logic."""
    if planner_module is None or scan_result_cls is None:
        raise AssertionError(
            "Planner-Modul oder ScanResult fehlt. Bitte Smoke-Test-Import prüfen."
        )

    build_plan = getattr(planner_module, "build_plan", None)
    action_plan_cls = getattr(planner_module, "ActionPlan", None)
    if build_plan is None or action_plan_cls is None:
        raise AssertionError(
            "build_plan oder ActionPlan fehlt. Bitte Planner-Implementierung prüfen."
        )

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir) / "downloads"
        trash_dir = Path(tmp_dir) / "trash"
        root.mkdir(parents=True, exist_ok=True)

        keep_file = root / "a.txt"
        move_file = root / "copy" / "a.txt"
        move_file.parent.mkdir(parents=True, exist_ok=True)
        keep_file.write_text("ABC", encoding="utf-8")
        move_file.write_text("ABC", encoding="utf-8")

        keep_result = scan_result_cls(
            path=keep_file,
            size=keep_file.stat().st_size,
            mtime=2000.0,
            file_type="other",
        )
        move_result = scan_result_cls(
            path=move_file,
            size=move_file.stat().st_size,
            mtime=1000.0,
            file_type="other",
        )

        plan = build_plan(
            files=[keep_result, move_result],
            duplicate_groups={0: [keep_result, move_result]},
            root=root,
            trash_dir=trash_dir,
        )

        if not isinstance(plan, action_plan_cls):
            raise AssertionError("build_plan sollte ein ActionPlan-Objekt zurückgeben.")
        if len(plan.items) != 2:
            raise AssertionError(
                "build_plan sollte beide Dateien in den Plan aufnehmen."
            )

        moved_item = next((item for item in plan.items if item.src == move_file), None)
        if moved_item is None:
            raise AssertionError("Plan sollte die ältere Duplikat-Datei enthalten.")
        if moved_item.reason != "duplicate":
            raise AssertionError(
                "Duplikat-Datei sollte den Grund 'duplicate' erhalten."
            )
        if moved_item.dest != trash_dir / "copy" / "a.txt":
            raise AssertionError(
                "Zielpfad sollte relativ zum Scan-Root berechnet werden."
            )

        count, total_bytes = plan.summary()
        expected_bytes = keep_file.stat().st_size + move_file.stat().st_size
        if count != 2:
            raise AssertionError(
                "ActionPlan.summary sollte die Dateianzahl korrekt melden."
            )
        if total_bytes != expected_bytes:
            raise AssertionError(
                "ActionPlan.summary sollte die Gesamtgröße korrekt melden."
            )


def run_core_scanner_checks(scanner_module: object) -> None:
    """Run minimal core validation checks for scanner logic."""
    if scanner_module is None:
        raise AssertionError("Scanner-Modul fehlt. Bitte Smoke-Test-Import prüfen.")

    scan_directory = getattr(scanner_module, "scan_directory", None)
    detect_duplicates = getattr(scanner_module, "detect_duplicates", None)
    parse_size = getattr(scanner_module, "_parse_size", None)
    parse_age = getattr(scanner_module, "_parse_age", None)
    if (
        scan_directory is None
        or detect_duplicates is None
        or parse_size is None
        or parse_age is None
    ):
        raise AssertionError(
            "scan_directory, detect_duplicates oder Parser fehlen im Scanner-Modul."
        )

    if parse_size("2kb") != 2048:
        raise AssertionError("_parse_size sollte KB-Werte korrekt umwandeln.")
    if parse_size("kaputt") != 0:
        raise AssertionError("_parse_size sollte bei ungültigen Werten 0 liefern.")
    if int(parse_age("2h")) != 7200:
        raise AssertionError("_parse_age sollte Stunden korrekt in Sekunden umwandeln.")
    if parse_age("kaputt") != 0.0:
        raise AssertionError("_parse_age sollte bei ungültigen Werten 0.0 liefern.")

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir) / "downloads"
        root.mkdir(parents=True, exist_ok=True)

        duplicate_a = root / "a" / "same.txt"
        duplicate_b = root / "b" / "same.txt"
        other_file = root / "photo.png"

        duplicate_a.parent.mkdir(parents=True, exist_ok=True)
        duplicate_b.parent.mkdir(parents=True, exist_ok=True)

        duplicate_a.write_text("DUPLICATE", encoding="utf-8")
        duplicate_b.write_text("DUPLICATE", encoding="utf-8")
        other_file.write_text("IMG", encoding="utf-8")

        scan_results = scan_directory(
            root=root,
            types=["other"],
            size_threshold=0,
            age_threshold=0.0,
        )
        if len(scan_results) != 2:
            raise AssertionError(
                "scan_directory sollte bei Typfilter 'other' nur Textdateien liefern."
            )

        duplicate_groups = detect_duplicates(scan_results, mode="safe")
        if len(duplicate_groups) != 1:
            raise AssertionError(
                "detect_duplicates im Modus 'safe' sollte genau eine Duplikatgruppe finden."
            )

        duplicate_count = len(next(iter(duplicate_groups.values())))
        if duplicate_count != 2:
            raise AssertionError(
                "Duplikatgruppe im Modus 'safe' sollte beide gleichen Dateien enthalten."
            )

        if detect_duplicates(scan_results, mode="ungültig") != {}:
            raise AssertionError(
                "detect_duplicates sollte bei ungültigem Modus ein leeres Ergebnis liefern."
            )


def run_core_validation_checks(validation_module: object) -> None:
    """Prüft zentrale Input-/Output-Validierung mit klaren Next Steps."""
    if validation_module is None:
        raise AssertionError("Validation-Modul fehlt. Bitte Import prüfen.")

    require_non_empty_text = getattr(validation_module, "require_non_empty_text", None)
    require_output = getattr(validation_module, "require_output", None)
    validation_error_cls = getattr(validation_module, "ValidationError", None)
    if (
        require_non_empty_text is None
        or require_output is None
        or validation_error_cls is None
    ):
        raise AssertionError(
            "Validation-Standards fehlen: require_non_empty_text, require_output oder ValidationError."
        )

    if require_non_empty_text("  ok  ", "feld") != "ok":
        raise AssertionError(
            "require_non_empty_text sollte Text trimmen und zurückgeben."
        )

    try:
        require_non_empty_text("   ", "feld")
        raise AssertionError("Leerer Text muss eine ValidationError auslösen.")
    except validation_error_cls as exc:
        if "Nächster Schritt" not in str(exc):
            raise AssertionError(
                "ValidationError sollte einen einfachen Next Step enthalten."
            )

    if require_output({"ok": True}, "result") != {"ok": True}:
        raise AssertionError(
            "require_output sollte vorhandene Ergebnisse unverändert zurückgeben."
        )

    try:
        require_output(None, "result")
        raise AssertionError("Fehlender Output muss eine ValidationError auslösen.")
    except validation_error_cls as exc:
        if "Nächster Schritt" not in str(exc):
            raise AssertionError(
                "Output-Fehler sollte einen einfachen Next Step enthalten."
            )


def run_gui_status_filter_checks(main_module: object) -> None:
    """Prüft den Hilfebereich 'Implementiert vs. Geplant' inkl. Filter ohne GUI-Crash."""
    if main_module is None:
        raise AssertionError("GUI-Modul fehlt. Bitte app.main-Import prüfen.")

    main_window_cls = getattr(main_module, "MainWindow", None)
    if main_window_cls is None:
        raise AssertionError("MainWindow fehlt im GUI-Modul app.main.")

    window = main_window_cls.__new__(main_window_cls)
    entries = main_window_cls._get_project_status_entries(window)
    if not entries:
        raise AssertionError(
            "Projektstatus-Liste darf nicht leer sein. Mindestens ein Punkt ist nötig."
        )

    states = {entry["state"] for entry in entries}
    if "done" not in states or "open" not in states:
        raise AssertionError(
            "Projektstatus-Liste sollte mindestens einen 'done' und einen 'open' Eintrag haben."
        )

    all_texts = [
        main_window_cls._format_project_status_entry(entry) for entry in entries
    ]
    if not all_texts or not all(
        "Implementiert" in text or "Geplant" in text for text in all_texts
    ):
        raise AssertionError("Filter 'Alle' sollte verständliche Status-Texte liefern.")

    open_texts = [
        main_window_cls._format_project_status_entry(entry)
        for entry in entries
        if entry["state"] == "open"
    ]
    if not open_texts:
        raise AssertionError(
            "Filter 'Nur offen' sollte mindestens einen geplanten Punkt anzeigen."
        )
    if not all(text.startswith("🟡 Geplant:") for text in open_texts):
        raise AssertionError(
            "Filter 'Nur offen' sollte nur geplante Statuspunkte enthalten."
        )


def run_gui_debug_snapshot_checks(main_module: object) -> None:
    """Prüft den HTML-Debug-Snapshot der GUI ohne Eventloop."""
    if main_module is None:
        raise AssertionError("GUI-Modul fehlt. Bitte app.main-Import prüfen.")

    main_window_cls = getattr(main_module, "MainWindow", None)
    if main_window_cls is None:
        raise AssertionError("MainWindow fehlt im GUI-Modul app.main.")

    window = main_window_cls.__new__(main_window_cls)
    window.THEME_A11Y_HINTS = dict(main_window_cls.THEME_A11Y_HINTS)
    window.PROJECT_STATUS_ITEMS = list(main_window_cls.PROJECT_STATUS_ITEMS)

    context = {
        "timestamp": "2026-02-12 12:00:00",
        "mode": "Laien-Modus (empfohlen)",
        "theme": "kontrast",
        "folder": "/tmp/downloads",
        "dashboard_html": "<b>Dashboard bereit</b>",
        "gate_html": "• ✅ G1",
    }
    html = main_window_cls._build_debug_gui_snapshot_html(window, context)
    if "Optischer Debug-Stand der GUI" not in html:
        raise AssertionError("Debug-HTML sollte eine klare Überschrift enthalten.")
    if "A11y-Theme-Hinweise" not in html:
        raise AssertionError("Debug-HTML sollte A11y-Hinweise enthalten.")
    if "Implementiert" not in html or "Geplant" not in html:
        raise AssertionError(
            "Debug-HTML sollte den Projektstatus mit Implementiert/Geplant enthalten."
        )


def should_run_gui_checks() -> tuple[bool, str]:
    """Entscheidet robust, ob GUI-nahe Smoke-Checks laufen können."""
    if os.environ.get("SMOKE_SKIP_GUI", "0") == "1":
        return (
            False,
            "SMOKE_SKIP_GUI=1 gesetzt. Nächster Schritt: Ohne SMOKE_SKIP_GUI im Desktop-Terminal erneut ausführen.",
        )
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        return (
            False,
            "keine Display/Wayland-Sitzung erkannt. Nächster Schritt: Im Desktop-Terminal mit aktivem Display erneut ausführen.",
        )
    return True, "GUI-Voraussetzungen erkannt"


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    selfcheck_module = importlib.import_module("core.selfcheck")
    planner_module = importlib.import_module("core.planner")
    scanner_module = importlib.import_module("core.scanner")
    settings_module = importlib.import_module("core.settings")
    validation_module = importlib.import_module("core.validation")

    run_selfcheck = getattr(selfcheck_module, "run_selfcheck", None)
    settings_cls = getattr(settings_module, "Settings", None)
    scan_result_cls = getattr(scanner_module, "ScanResult", None)
    if run_selfcheck is None or settings_cls is None:
        print(
            "Import fehlgeschlagen: core.selfcheck.run_selfcheck oder core.settings.Settings fehlt."
        )
        return 1

    ok, msg = run_selfcheck()
    if not ok:
        print("Selfcheck failed:", msg)
        return 1

    try:
        run_core_settings_checks(settings_cls)
    except Exception as e:
        print("Core settings checks failed:", e)
        return 1

    try:
        run_core_planner_checks(planner_module, scan_result_cls)
    except Exception as e:
        print("Core planner checks failed:", e)
        return 1

    try:
        run_core_scanner_checks(scanner_module)
    except Exception as e:
        print("Core scanner checks failed:", e)
        return 1

    try:
        run_core_validation_checks(validation_module)
    except Exception as e:
        print("Core validation checks failed:", e)
        return 1

    run_gui, gui_reason = should_run_gui_checks()
    if not run_gui:
        print(f"Smoke test passed (GUI-Checks übersprungen: {gui_reason})")
        print(
            "Nächster Schritt: Für vollständigen GUI-Smoke im Desktop-Terminal erneut ausführen."
        )
        return 0

    try:
        # Attempt to import the main window without starting the event loop
        main_module = importlib.import_module("app.main")
    except Exception as e:
        print("Import failed:", e)
        return 1

    try:
        run_gui_status_filter_checks(main_module)
    except Exception as e:
        print("GUI status filter checks failed:", e)
        return 1

    try:
        run_gui_debug_snapshot_checks(main_module)
    except Exception as e:
        print("GUI debug snapshot checks failed:", e)
        return 1

    print("Smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
