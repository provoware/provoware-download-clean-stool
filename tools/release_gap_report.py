#!/usr/bin/env python3
"""Prüft in einfacher Form, was für den Release noch fehlt."""

from __future__ import annotations

import argparse
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


@dataclass(frozen=True)
class AppImageCheckResult:
    name: str
    ok: bool
    detail: str
    next_step: str


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


def _collect_appimage_checks() -> list[AppImageCheckResult]:
    appimage_dir = ROOT / "tools" / "appimage"
    appdir_dir = ROOT / "AppDir"
    dist_dir = ROOT / "dist"

    appimagetool_local = appimage_dir / "appimagetool-x86_64.AppImage"
    linuxdeploy_local = appimage_dir / "linuxdeploy-x86_64.AppImage"
    app_run = appdir_dir / "AppRun"

    appimage_outputs = list(dist_dir.glob("*.AppImage")) if dist_dir.exists() else []

    return [
        AppImageCheckResult(
            name="Build-Werkzeug vorhanden",
            ok=(appimagetool_local.exists() or linuxdeploy_local.exists()),
            detail=(
                "Lokales AppImage-Build-Werkzeug gefunden."
                if (appimagetool_local.exists() or linuxdeploy_local.exists())
                else "Kein lokales Build-Werkzeug in tools/appimage gefunden."
            ),
            next_step=(
                "mkdir -p tools/appimage && cd tools/appimage && wget https://github.com/AppImage/AppImageKit/releases/latest/download/appimagetool-x86_64.AppImage && chmod +x appimagetool-x86_64.AppImage"
            ),
        ),
        AppImageCheckResult(
            name="AppDir vorbereitet",
            ok=(appdir_dir.exists() and app_run.exists()),
            detail=(
                "AppDir und AppRun sind vorhanden."
                if (appdir_dir.exists() and app_run.exists())
                else "AppDir oder AppRun fehlt noch für den Build."
            ),
            next_step="mkdir -p AppDir/usr/bin && cp start.sh AppDir/AppRun && chmod +x AppDir/AppRun",
        ),
        AppImageCheckResult(
            name="Build-Artefakt vorhanden",
            ok=bool(appimage_outputs),
            detail=(
                f"{len(appimage_outputs)} AppImage-Datei(en) in dist gefunden."
                if appimage_outputs
                else "Noch keine fertige .AppImage-Datei im Ordner dist gefunden."
            ),
            next_step="mkdir -p dist && tools/appimage/appimagetool-x86_64.AppImage AppDir dist/Provoware-Clean-Tool-x86_64.AppImage",
        ),
    ]


def _run_shell_step(label: str, command: str) -> tuple[bool, str]:
    if not label.strip() or not command.strip():
        return (
            False,
            "Ungültiger Auto-Fix-Schritt. Nächster Schritt: Skript mit gültigen Parametern erneut starten.",
        )
    exit_code = 0
    output = ""
    try:
        import subprocess

        result = subprocess.run(
            ["bash", "-lc", command],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        exit_code = result.returncode
        output = (result.stdout + "\n" + result.stderr).strip()
    except Exception as exc:  # pragma: no cover - robust fallback for runtime envs
        return (
            False,
            f"{label} konnte nicht gestartet werden: {exc}. Nächster Schritt: Python-Umgebung prüfen und den Befehl manuell im Terminal ausführen.",
        )

    if exit_code == 0:
        return True, f"{label} erfolgreich ausgeführt."

    short_output = output.splitlines()[-1] if output else "ohne Detailausgabe"
    return (
        False,
        f"{label} fehlgeschlagen (Exitcode {exit_code}): {short_output}. Nächster Schritt: Befehl einzeln im Terminal ausführen.",
    )


def _auto_fix_appimage_basics() -> list[str]:
    steps = [
        (
            "Build-Werkzeug laden",
            "mkdir -p tools/appimage && cd tools/appimage && wget -q https://github.com/AppImage/AppImageKit/releases/latest/download/appimagetool-x86_64.AppImage && chmod +x appimagetool-x86_64.AppImage",
        ),
        (
            "AppDir-Grundstruktur anlegen",
            "mkdir -p AppDir/usr/bin && cp start.sh AppDir/AppRun && chmod +x AppDir/AppRun",
        ),
    ]
    notes: list[str] = []
    for label, command in steps:
        ok, message = _run_shell_step(label, command)
        prefix = "OK" if ok else "WARN"
        notes.append(f"[{prefix}] {message}")
        if not ok:
            break
    return notes


def _print_appimage_report(checks: list[AppImageCheckResult]) -> int:
    missing = [check for check in checks if not check.ok]
    ready = not missing

    print("[RELEASE][APPIMAGE] Kompaktprüfung")
    for check in checks:
        icon = "OK" if check.ok else "WARN"
        print(f"- [{icon}] {check.name}: {check.detail}")
        if not check.ok:
            print(f"  [HILFE] Nächster Schritt: {check.next_step}")

    print(f"[RELEASE][APPIMAGE] Releasefertig: {'JA' if ready else 'NEIN'}")
    if not ready:
        print(
            "[RELEASE][APPIMAGE] Bitte zuerst die erste WARN-Zeile lösen und erneut prüfen."
        )
        return 1

    print("[RELEASE][APPIMAGE] Alle Mindestpunkte erfüllt.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--appimage-only",
        action="store_true",
        help="Prüft nur die AppImage-Bereitschaft in kompakter Form.",
    )
    parser.add_argument(
        "--auto-fix-appimage",
        action="store_true",
        help="Versucht fehlende AppImage-Basics automatisch zu erstellen und prüft danach erneut.",
    )
    args = parser.parse_args()

    if args.auto_fix_appimage:
        print("[RELEASE][APPIMAGE] Starte Auto-Fix für Basisbausteine …")
        for line in _auto_fix_appimage_basics():
            print(f"[RELEASE][APPIMAGE] {line}")

    if args.appimage_only:
        return _print_appimage_report(_collect_appimage_checks())

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
    else:
        print(f"[RELEASE][WARN] Es fehlen noch {len(gaps)} Release-Punkt(e):")
        for index, gap in enumerate(gaps, start=1):
            print(f"  {index}. {gap}")
        print(
            "[RELEASE][HILFE] Bitte zuerst Punkt 1 lösen und den Report erneut starten."
        )

    appimage_exit = _print_appimage_report(_collect_appimage_checks())
    if gaps:
        return 1
    return appimage_exit


if __name__ == "__main__":
    sys.exit(main())
