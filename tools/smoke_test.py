"""Smoke test for Downloads Organizer.

This script performs a minimal import of the core modules and the GUI to
ensure there are no import‑time errors. It is used during development.
"""

import sys

from core.selfcheck import run_selfcheck

ok, msg = run_selfcheck()
if not ok:
    print("Selfcheck failed:", msg)
    sys.exit(1)

try:
    # Attempt to import the main window without starting the event loop
    from app.main import MainWindow  # noqa: F401
except Exception as e:
    print("Import failed:", e)
    sys.exit(1)

print("Smoke test passed")
