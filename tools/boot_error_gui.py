#!/usr/bin/env python3
"""Laienfreundlicher Start-Fehlerdialog (ohne PySide6-Abhängigkeit).

WICHTIG: Dieses Skript darf KEINE externen Python-Module importieren.
Damit kann es auch dann eine verständliche Meldung anzeigen, wenn PySide6/Pillow
noch nicht installiert sind (z.B. offline, pip-Fehler, falscher Python-Interpreter).

Strategie:
1) Wenn `zenity` vorhanden ist: grafischer Dialog + Buttons.
2) Sonst: klare Terminal-Ausgabe (große Überschrift, nächste Schritte).
3) Immer: Fehlertext in exports/last_start_error.txt schreiben.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
EXPORTS = APP_DIR / "exports"
LOGS = APP_DIR / "logs"
EXPORTS.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)

OUT_FILE = EXPORTS / "last_start_error.txt"


def _write_report(title: str, details: str) -> None:
    OUT_FILE.write_text(f"{title}\n\n{details}\n", encoding="utf-8")


def _zenity_available() -> bool:
    return shutil.which("zenity") is not None


def _show_zenity(title: str, details: str) -> int:
    msg = (
        details.strip()
        + "\n\nNächster Schritt:\n"
        + "• Erneut versuchen\n"
        + "• Reparatur öffnen\n"
        + "• Protokoll öffnen"
    )
    cmd = [
        "zenity",
        "--question",
        "--title",
        title,
        "--width=720",
        "--text",
        msg[:4000],
        "--ok-label=Erneut versuchen",
        "--cancel-label=Schließen",
        "--extra-button=Reparatur",
        "--extra-button=Protokoll",
    ]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    choice = (result.stdout or "").strip()

    if choice == "Reparatur":
        subprocess.run(
            [sys.executable, str(APP_DIR / "tools" / "repair_center_gui.py")],
            check=False,
        )
        return 0
    if choice == "Protokoll":
        if shutil.which("xdg-open"):
            subprocess.run(["xdg-open", str(OUT_FILE)], check=False)
        return 0
    if result.returncode == 0:
        return 10
    return 0


def _show_terminal(title: str, details: str) -> int:
    print("\n" + "=" * 72)
    print(f"[FEHLER] {title}")
    print("=" * 72)
    print(details.strip())
    print("\n[INFO] Diagnose-Datei:", OUT_FILE)
    print("[INFO] Diagnose-Ordner:", EXPORTS)
    print("=" * 72)
    try:
        input("Drücke ENTER zum Beenden...")
    except EOFError:
        pass
    return 0


def main() -> int:
    title = "Startproblem"
    details = ""
    if len(sys.argv) >= 2:
        details = sys.argv[1]
    if len(sys.argv) >= 3:
        title = sys.argv[2]
    if not details:
        details = "Unbekannter Fehler. Bitte exports/last_start_error.txt prüfen."

    _write_report(title, details)

    if _zenity_available():
        return _show_zenity(title, details)
    return _show_terminal(title, details)


if __name__ == "__main__":
    raise SystemExit(main())
