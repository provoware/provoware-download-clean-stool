from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import List, Tuple

from .planner import ActionPlan, PlanItem
from .logger import setup_logger

LOGGER = setup_logger()

UNDO_FILE = Path(__file__).resolve().parent.parent / "data" / "last_undo.json"


def execute_move_plan(plan: ActionPlan) -> Tuple[bool, str]:
    """Execute the plan: move files to the trash directory.

    Parameters
    ----------
    plan: ActionPlan
        The action plan to execute.

    Returns
    -------
    Tuple[bool, str]
        (True, message) on success; (False, error message) on failure.
    """
    if not plan.items:
        return True, "Keine Dateien zum Verschieben"
    moves: List[Tuple[str, str]] = []
    try:
        for item in plan.items:
            src = item.src
            dest = item.dest
            # ensure destination directory exists
            dest.parent.mkdir(parents=True, exist_ok=True)
            # avoid overwriting existing files in trash: append a numeric suffix
            final_dest = dest
            counter = 1
            while final_dest.exists():
                final_dest = dest.with_name(dest.stem + f"_{counter}" + dest.suffix)
                counter += 1
            shutil.move(str(src), str(final_dest))
            LOGGER.info("Moved %s → %s (%s)", src, final_dest, item.reason)
            moves.append((str(src), str(final_dest)))
        # save undo metadata
        UNDO_FILE.write_text(json.dumps(moves, indent=2), encoding="utf-8")
        return True, f"{len(moves)} Dateien wurden verschoben."
    except Exception as e:
        LOGGER.error("Fehler beim Verschieben: %s", e)
        return False, f"Fehler beim Verschieben: {e}"


def undo_last() -> Tuple[bool, str]:
    """Undo the last move operation.

    Reads the last undo metadata file and moves files back to their original
    locations. The undo metadata is then removed.
    """
    if not UNDO_FILE.exists():
        return False, "Keine vorherige Aktion zum Rückgängig machen"
    try:
        moves = json.loads(UNDO_FILE.read_text(encoding="utf-8"))
    except Exception:
        return False, "Fehler beim Lesen der Undo‑Datei"
    restored_count = 0
    for src, dest in moves:
        src_path = Path(src)
        dest_path = Path(dest)
        if dest_path.exists():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            # ensure source parent exists
            src_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dest_path), str(src_path))
            LOGGER.info("Restored %s ← %s", src_path, dest_path)
            restored_count += 1
    try:
        UNDO_FILE.unlink()
    except Exception:
        pass
    return True, f"{restored_count} Dateien wurden wiederhergestellt."
