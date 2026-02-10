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


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    selfcheck_module = importlib.import_module("core.selfcheck")
    settings_module = importlib.import_module("core.settings")

    run_selfcheck = getattr(selfcheck_module, "run_selfcheck", None)
    settings_cls = getattr(settings_module, "Settings", None)
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
        # Attempt to import the main window without starting the event loop
        importlib.import_module("app.main")
    except Exception as e:
        print("Import failed:", e)
        return 1

    print("Smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
