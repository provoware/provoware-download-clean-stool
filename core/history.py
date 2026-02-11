from __future__ import annotations

"""
core.history – verwaltet den Verlauf früherer Aufräumläufe.

Dieses Modul stellt einfache Funktionen bereit, um
Aufräumläufe zu protokollieren (Anzahl Dateien und Größe in MB),
den Verlauf als Liste einzulesen und den Verlauf zu leeren.
Die Daten werden in einer JSON‑Datei im Ordner ``data`` gespeichert.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Datei, in der der Verlauf gespeichert wird
HISTORY_FILE: Path = (
    Path(__file__).resolve().parent.parent / "data" / "history.json"
)


def read_history() -> List[Dict[str, object]]:
    """
    Liest den bisherigen Verlauf ein.

    Returns:
        Liste von Dictionaries mit Schlüsseln ``timestamp``, ``files`` und ``size_mb``.
        Ist keine Datei vorhanden oder ein Fehler aufgetreten, wird eine leere Liste geliefert.
    """
    try:
        if not HISTORY_FILE.exists():
            return []
        with HISTORY_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            # Ggf. sortieren nach Zeitstempel absteigend
            return list(data)
    except Exception:
        return []
    return []


def append_history(num_files: int, size_mb: float) -> None:
    """
    Fügt einen neuen Lauf zum Verlauf hinzu.

    Args:
        num_files: Anzahl der verarbeiteten Dateien.
        size_mb: Verarbeitete Gesamtgröße in Megabyte.
    """
    history = read_history()
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "files": int(num_files),
        "size_mb": round(float(size_mb), 2),
    }
    history.append(entry)
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with HISTORY_FILE.open("w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        # Fehler nicht propagieren – Verlauf ist optional
        pass


def clear_history() -> None:
    """
    Löscht den gesamten Verlauf.
    """
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with HISTORY_FILE.open("w", encoding="utf-8") as f:
            json.dump([], f)
    except Exception:
        pass