from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import List, Tuple

from .logger import setup_logger
from .planner import ActionPlan, PlanItem
from .validation import ValidationError, require_condition, require_type

LOGGER = setup_logger()

UNDO_FILE = Path(__file__).resolve().parent.parent / "data" / "last_undo.json"


def _validate_plan_item(item: object, index: int) -> PlanItem:
    """Validate one plan item with clear next-step messages."""
    plan_item = require_type(item, PlanItem, f"plan.items[{index}]")
    require_condition(
        plan_item.src.exists(),
        "Ungültiger Output bei 'plan.items': Quelldatei fehlt. "
        "Nächster Schritt: Scan erneut starten und den Plan neu erzeugen.",
    )
    require_condition(
        bool(str(plan_item.reason).strip()),
        "Ungültiger Input bei 'plan.items.reason': Grundtext fehlt. "
        "Nächster Schritt: Plan mit gültigem Begründungstext neu erzeugen.",
    )
    return plan_item


def _read_undo_entries() -> List[Tuple[Path, Path]]:
    """Load and validate undo data with a strict tuple format."""
    raw_data = json.loads(UNDO_FILE.read_text(encoding="utf-8"))
    require_condition(
        isinstance(raw_data, list),
        "Ungültiger Output bei 'last_undo.json': Liste erwartet. "
        "Nächster Schritt: Aktion erneut ausführen, damit eine neue Undo-Datei erstellt wird.",
    )

    entries: List[Tuple[Path, Path]] = []
    for index, pair in enumerate(raw_data):
        require_condition(
            isinstance(pair, list) and len(pair) == 2,
            "Ungültiger Output bei 'last_undo.json': Jeder Eintrag muss aus Quelle und Ziel bestehen. "
            "Nächster Schritt: Undo-Datei löschen und Aktion erneut ausführen.",
        )
        src_str = require_type(pair[0], str, f"last_undo[{index}][0]")
        dest_str = require_type(pair[1], str, f"last_undo[{index}][1]")
        entries.append((Path(src_str), Path(dest_str)))

    return entries


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
    valid_plan = require_type(plan, ActionPlan, "plan")
    if not valid_plan.items:
        return True, "Keine Dateien zum Verschieben"

    moves: List[Tuple[str, str]] = []
    try:
        for index, item in enumerate(valid_plan.items):
            valid_item = _validate_plan_item(item, index)
            src = valid_item.src
            dest = valid_item.dest
            # ensure destination directory exists
            dest.parent.mkdir(parents=True, exist_ok=True)
            # avoid overwriting existing files in trash: append a numeric suffix
            final_dest = dest
            counter = 1
            while final_dest.exists():
                final_dest = dest.with_name(dest.stem + f"_{counter}" + dest.suffix)
                counter += 1
            shutil.move(str(src), str(final_dest))
            require_condition(
                final_dest.exists(),
                "Ungültiger Output bei 'execute_move_plan': Ziel-Datei wurde nach dem Verschieben nicht gefunden. "
                "Nächster Schritt: Speicherort prüfen und Vorgang erneut starten.",
            )
            LOGGER.info("Moved %s → %s (%s)", src, final_dest, valid_item.reason)
            moves.append((str(src), str(final_dest)))
        # save undo metadata
        UNDO_FILE.parent.mkdir(parents=True, exist_ok=True)
        UNDO_FILE.write_text(json.dumps(moves, indent=2), encoding="utf-8")
        require_condition(
            UNDO_FILE.exists(),
            "Ungültiger Output bei 'execute_move_plan': Undo-Datei wurde nicht erstellt. "
            "Nächster Schritt: Schreibrechte im data-Ordner prüfen und erneut versuchen.",
        )
        return True, f"{len(moves)} Dateien wurden verschoben."
    except ValidationError as error:
        LOGGER.error("Validierungsfehler beim Verschieben: %s", error)
        return False, str(error)
    except Exception as e:
        LOGGER.error("Fehler beim Verschieben: %s", e)
        return (
            False,
            "Fehler beim Verschieben. Nächster Schritt: Pfade und Schreibrechte prüfen, dann erneut versuchen. "
            f"Technisches Detail: {e}",
        )


def undo_last() -> Tuple[bool, str]:
    """Undo the last move operation.

    Reads the last undo metadata file and moves files back to their original
    locations. The undo metadata is then removed.
    """
    if not UNDO_FILE.exists():
        return False, "Keine vorherige Aktion zum Rückgängig machen"
    try:
        moves = _read_undo_entries()
    except ValidationError as error:
        LOGGER.error("Validierungsfehler in Undo-Datei: %s", error)
        return False, str(error)
    except Exception as error:
        LOGGER.error("Fehler beim Lesen der Undo-Datei: %s", error)
        return (
            False,
            "Fehler beim Lesen der Undo-Datei. Nächster Schritt: Aktion erneut ausführen, "
            "damit neue Undo-Daten erstellt werden.",
        )

    restored_count = 0
    for src_path, dest_path in moves:
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
    require_condition(
        restored_count >= 0,
        "Ungültiger Output bei 'undo_last': Wiederherstellungszähler ist ungültig. "
        "Nächster Schritt: Protokoll prüfen und Support kontaktieren.",
    )
    return True, f"{restored_count} Dateien wurden wiederhergestellt."
