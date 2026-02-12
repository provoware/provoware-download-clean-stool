#!/usr/bin/env python3
"""Prüft in einfacher Form, was für den Release noch fehlt."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class StatusSnapshot:
    source: str
    progress: int | None
    open_points: int | None


def _read_text(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Datei fehlt: {file_path}. Nächster Schritt: Datei wiederherstellen und erneut prüfen."
        )
    return file_path.read_text(encoding="utf-8")


def _extract_int(pattern: str, text: str) -> int | None:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def _snapshot_for(file_path: Path) -> StatusSnapshot:
    text = _read_text(file_path)
    progress_patterns = (
        r"Fortschritt[^\n]*?\*\*(\d+)%\*\*",
        r"Entwicklungsfortschritt[^\n]*?\*\*(\d+)%\*\*",
        r"Fortschritt[^\n]*?(\d+)%",
    )
    progress = None
    for pattern in progress_patterns:
        progress = _extract_int(pattern, text)
        if progress is not None:
            break

    open_patterns = (
        r"Offene Punkte[^\n]*?\*\*(\d+)\*\*",
        r"Offen[^\n]*?\*\*(\d+)\*\*",
        r"Offen[^\n]*?(\d+)",
    )
    open_points = None
    for pattern in open_patterns:
        open_points = _extract_int(pattern, text)
        if open_points is not None:
            break

    return StatusSnapshot(
        source=file_path.as_posix(), progress=progress, open_points=open_points
    )


def _format_snapshot(snapshot: StatusSnapshot) -> str:
    progress = "unbekannt" if snapshot.progress is None else f"{snapshot.progress}%"
    open_points = (
        "unbekannt" if snapshot.open_points is None else str(snapshot.open_points)
    )
    return f"- {snapshot.source}: Fortschritt={progress}, Offen={open_points}"


def _build_release_gaps(snapshots: list[StatusSnapshot]) -> list[str]:
    gaps: list[str] = []
    values_with_source = [
        (snapshot.source, snapshot.progress, snapshot.open_points)
        for snapshot in snapshots
    ]

    progress_values = {
        progress for _, progress, _ in values_with_source if progress is not None
    }
    if len(progress_values) > 1:
        gaps.append(
            "Fortschritt ist nicht konsistent. Nächster Schritt: Prozentzahl in README, RELEASE_CHECKLIST und Entwicklerdoku angleichen."
        )

    open_values = {
        open_points
        for _, _, open_points in values_with_source
        if open_points is not None
    }
    if len(open_values) > 1:
        gaps.append(
            "Offene Punkte sind nicht konsistent. Nächster Schritt: überall den gleichen Restumfang eintragen."
        )

    for source, progress, open_points in values_with_source:
        if progress is not None and progress < 100:
            gaps.append(
                f"{source} meldet noch keinen Vollstatus ({progress}%). Nächster Schritt: fehlende Punkte priorisieren und abhaken."
            )
        if open_points is not None and open_points > 0:
            gaps.append(
                f"{source} meldet noch {open_points} offene Punkte. Nächster Schritt: zuerst diese Punkte schließen."
            )

    return gaps


def main() -> int:
    tracked_files = [
        ROOT / "README.md",
        ROOT / "RELEASE_CHECKLIST.md",
        ROOT / "docs/developer_manual.md",
    ]

    try:
        snapshots = [_snapshot_for(file_path) for file_path in tracked_files]
    except FileNotFoundError as exc:
        print(f"[RELEASE][WARN] {exc}")
        return 1

    print("[RELEASE] Statusvergleich über zentrale Dateien")
    for snapshot in snapshots:
        print(_format_snapshot(snapshot))

    gaps = _build_release_gaps(snapshots)
    if not gaps:
        print("[RELEASE][OK] Für den dokumentierten Scope fehlt kein Pflichtpunkt.")
        print(
            "[RELEASE][HILFE] Optional: UI-Live-Screenshot ergänzen und bei jeder UI-Änderung erneuern."
        )
        return 0

    print(f"[RELEASE][WARN] Es fehlen noch {len(gaps)} Release-Punkt(e):")
    for index, gap in enumerate(gaps, start=1):
        print(f"  {index}. {gap}")

    print("[RELEASE][HILFE] Bitte zuerst Punkt 1 lösen und den Report erneut starten.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
