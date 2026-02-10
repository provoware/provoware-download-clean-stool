#!/usr/bin/env python3
"""Qualitätsprüfung-Dialog (ohne externe Abhängigkeiten).

Wird aufgerufen, wenn tools/run_quality_checks.sh fehlschlägt.
Zeigt eine laienverständliche Meldung und öffnet optional den Report.
"""

from __future__ import annotations
import shutil
import subprocess
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPORT = APP_DIR / "exports" / "quality_report.txt"
EXPORTS = APP_DIR / "exports"
EXPORTS.mkdir(exist_ok=True)

def main() -> int:
    msg = (
        "Die Qualitätsprüfung hat ein Problem gefunden.\n\n"
        f"Report: {REPORT}\n\n"
        "Das Tool kann meistens trotzdem starten, aber wir empfehlen:\n"
        "1) Internet prüfen (für pip)\n"
        "2) Start erneut ausführen\n"
        "3) Report öffnen und ggf. 'Reparatur' nutzen\n"
    )
    if shutil.which("zenity"):
        subprocess.run(["zenity","--warning","--title","Qualitätsprüfung","--width=700","--text",msg], check=False)
        if shutil.which("xdg-open") and REPORT.exists():
            subprocess.run(["xdg-open", str(REPORT)], check=False)
    else:
        print(msg)
        if REPORT.exists():
            print("\n--- quality_report.txt (Auszug) ---")
            try:
                print(REPORT.read_text(encoding="utf-8")[:2000])
            except Exception:
                pass
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
