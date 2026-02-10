from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple


def run_selfcheck() -> Tuple[bool, str]:
    """Perform a basic self‑check before starting the GUI.

    The check ensures that the Python version is recent enough and that
    required directories (logs/ and exports/) can be created. Additional
    checks can be added as needed.

    Returns
    -------
    Tuple[bool, str]
        A tuple `(ok, message)` where `ok` indicates success and
        `message` contains details in case of failure.
    """
    # Require at least Python 3.8
    if sys.version_info < (3, 8):
        return False, "Python 3.8 oder höher ist erforderlich"
    root = Path(__file__).resolve().parent.parent
    logs_dir = root / "logs"
    exports_dir = root / "exports"
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        exports_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"Fehler beim Erstellen der Verzeichnisse: {e}"
    return True, "Selfcheck erfolgreich"
