from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

from .scanner import ScanResult
from .validation import (require_condition, require_existing_dir,
                         require_sequence_of_type, require_type)


@dataclass
class PlanItem:
    """Represents a single file move action."""

    src: Path
    dest: Path
    reason: str


@dataclass
class ActionPlan:
    """Contains the list of file moves and summary information."""

    items: List[PlanItem] = field(default_factory=list)

    def summary(self) -> Tuple[int, int]:
        """Return a tuple (count, total_bytes) for the plan."""
        count = len(self.items)
        total_bytes = sum(
            item.src.stat().st_size for item in self.items if item.src.exists()
        )
        return count, total_bytes


def build_plan(
    files: List[ScanResult],
    duplicate_groups: Dict[int, List[ScanResult]],
    root: Path,
    trash_dir: Path,
) -> ActionPlan:
    """Create an action plan based on scan results and duplicate groups.

    Parameters
    ----------
    files: List[ScanResult]
        Files that meet the filter criteria and are candidates for moving.
    duplicate_groups: Dict[int, List[ScanResult]]
        Groups of duplicates returned by `detect_duplicates()`.
    root: Path
        The root directory of the scan. Used to compute relative paths.
    trash_dir: Path
        Directory where files will be moved.

    Returns
    -------
    ActionPlan
        A plan containing all file moves and reasons (duplicate or filtered).
    """
    validated_files = require_sequence_of_type(files, ScanResult, "files")
    validated_root = require_existing_dir(root, "root")
    validated_trash_dir = require_type(trash_dir, Path, "trash_dir")
    for group_id, group_files in duplicate_groups.items():
        require_type(group_id, int, "duplicate_groups.group_id")
        require_sequence_of_type(
            group_files, ScanResult, f"duplicate_groups[{group_id}]"
        )

    plan = ActionPlan()
    duplicates_set = set()
    for group in duplicate_groups.values():
        if not group:
            continue
        keep = max(group, key=lambda x: x.mtime)
        for file_entry in group:
            if file_entry is not keep:
                duplicates_set.add(file_entry.path)

    for file_entry in validated_files:
        reason = "duplicate" if file_entry.path in duplicates_set else "filtered"
        src = file_entry.path
        try:
            rel = src.relative_to(validated_root)
        except ValueError:
            rel = Path(src.name)
        dest = validated_trash_dir / rel
        plan.items.append(PlanItem(src=src, dest=dest, reason=reason))

    require_condition(
        len(plan.items) == len(validated_files),
        (
            "Interner Planungsfehler: Anzahl geplanter Aktionen passt nicht zu den Eingabedateien. "
            "Nächster Schritt: Protokoll prüfen und Planung erneut starten."
        ),
    )
    return plan
