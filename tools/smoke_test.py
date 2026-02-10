"""Smoke test for Downloads Organizer.

# ruff: noqa: E402

This script performs a minimal import of the core modules and the GUI to
ensure there are no import‑time errors. It is used during development.
"""

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.selfcheck import run_selfcheck
from core.settings import Settings


def run_core_settings_checks() -> None:
    """Run minimal core validation checks for settings handling."""
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

        loaded = Settings.load(settings_path)
        if loaded.theme != "dark":
            raise AssertionError("Settings.load sollte das Theme korrekt übernehmen.")
        if loaded.confirm_threshold != 7:
            raise AssertionError("Settings.load sollte numerische Schwellen korrekt umwandeln.")
        if loaded.ui_texts.get("error_title") != "Fehlerhinweis":
            raise AssertionError("Settings.load sollte UI-Texte korrekt übernehmen.")

        loaded.save(settings_path)
        saved = json.loads(settings_path.read_text(encoding="utf-8"))
        if saved.get("schema_version", 0) < 2:
            raise AssertionError("Settings.save sollte schema_version >= 2 schreiben.")
        if saved.get("file_revision", 0) < 1:
            raise AssertionError("Settings.save sollte file_revision erhöhen.")

ok, msg = run_selfcheck()
if not ok:
    print("Selfcheck failed:", msg)
    sys.exit(1)

try:
    run_core_settings_checks()
except Exception as e:
    print("Core settings checks failed:", e)
    sys.exit(1)

try:
    # Attempt to import the main window without starting the event loop
    from app.main import MainWindow  # noqa: F401
except Exception as e:
    print("Import failed:", e)
    sys.exit(1)

print("Smoke test passed")
