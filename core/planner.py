from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .scanner import ScanResult


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
        total_bytes = sum(item.src.stat().st_size for item in self.items if item.src.exists())
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
    plan = ActionPlan()
    # Mark duplicates
    duplicates_set = set()
    for group in duplicate_groups.values():
        # choose one file to keep: the most recently modified
        if not group:
            continue
        keep = max(group, key=lambda x: x.mtime)
        for f in group:
            if f is not keep:
                duplicates_set.add(f.path)
    for f in files:
        reason = ""
        if f.path in duplicates_set:
            reason = "duplicate"
        else:
            reason = "filtered"
        src = f.path
        # compute relative path to root
        try:
            rel = src.relative_to(root)
        except ValueError:
            rel = src.name
        dest = trash_dir / rel
        plan.items.append(PlanItem(src=src, dest=dest, reason=reason))
    return plan
