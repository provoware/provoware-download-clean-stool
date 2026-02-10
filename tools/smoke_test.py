"""Smoke test for Downloads Organizer.

This script performs a minimal import of the core modules and the GUI to
ensure there are no import‑time errors. It is used during development.
"""

import importlib
import json
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


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    selfcheck_module = importlib.import_module("core.selfcheck")
    planner_module = importlib.import_module("core.planner")
    scanner_module = importlib.import_module("core.scanner")
    settings_module = importlib.import_module("core.settings")

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
        # Attempt to import the main window without starting the event loop
        importlib.import_module("app.main")
    except Exception as e:
        print("Import failed:", e)
        return 1

    print("Smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
