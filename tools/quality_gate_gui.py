#!/usr/bin/env python3
"""Qualitätsprüfung-Dialog (ohne externe Abhängigkeiten).

Wird aufgerufen, wenn tools/run_quality_checks.sh fehlschlägt.
Zeigt einen einheitlichen Kurzbericht wie in start.sh mit klaren Next Steps.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPORT = APP_DIR / "exports" / "quality_report.txt"
EXPORTS = APP_DIR / "exports"
EXPORTS.mkdir(exist_ok=True)


def _validate_non_negative_int(raw_value: str) -> int:
    """Liefert eine nicht-negative Zahl oder 0 als sicheren Fallback."""

    text = str(raw_value).strip()
    return int(text) if text.isdigit() else 0


def _extract_count(report_text: str, pattern: str) -> int:
    """Liest Warn-/Hinweiswerte aus dem Report robust aus."""

    match = re.search(pattern, report_text)
    if not match:
        return 0
    return _validate_non_negative_int(match.group(1))


def _build_quality_quickfix_block(warn_count: int, info_count: int) -> str:
    """Erzeugt einen laienfreundlichen Kompaktblock mit Auto-Fix-Schritten."""

    validated_warn_count = _validate_non_negative_int(str(warn_count))
    validated_info_count = _validate_non_negative_int(str(info_count))
    lines = [
        "[QUALITÄT] ===== Kompaktblock =====",
        f"[QUALITÄT] Warnungen: {validated_warn_count} | Hinweise: {validated_info_count}",
        f"[QUALITÄT] Protokoll: {REPORT}",
    ]
    if validated_warn_count > 0:
        lines.extend(
            [
                "[QUALITÄT] Nächster Schritt (Auto-Fix): AUTO_FIX=1 bash tools/run_quality_checks.sh",
                "[QUALITÄT] Danach neu prüfen: bash tools/run_quality_checks.sh",
                "[QUALITÄT] Danach Start wiederholen: bash start.sh",
            ]
        )
    else:
        lines.append(
            "[QUALITÄT] Keine Warnungen erkannt. Für Kontrolle optional: bash tools/run_quality_checks.sh"
        )
    return "\n".join(lines)


def _load_report_excerpt(path: Path, *, max_length: int = 2000) -> str:
    """Lädt einen sicheren Report-Auszug für Terminal-Ausgabe."""

    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")[:max_length]
    except OSError:
        return ""


def main() -> int:
    report_text = _load_report_excerpt(REPORT, max_length=20_000)
    warn_count = _extract_count(report_text, r"WARN(?:UNGEN)?:\s*([0-9]+)")
    info_count = _extract_count(report_text, r"INFO(?:S|HINWEISE)?:\s*([0-9]+)")
    quickfix_block = _build_quality_quickfix_block(warn_count, info_count)

    msg = (
        "Die Qualitätsprüfung hat ein Problem gefunden.\n\n"
        f"Report: {REPORT}\n\n"
        "Bitte diese 3 Schritte ausführen:\n"
        "1) Protokoll öffnen\n"
        "2) Auto-Fix oder Qualitätslauf starten\n"
        "3) Start erneut ausführen\n\n"
        f"{quickfix_block}\n"
    )
    if shutil.which("zenity"):
        subprocess.run(
            [
                "zenity",
                "--warning",
                "--title",
                "Qualitätsprüfung",
                "--width=780",
                "--text",
                msg,
            ],
            check=False,
        )
        if shutil.which("xdg-open") and REPORT.exists():
            subprocess.run(["xdg-open", str(REPORT)], check=False)
    else:
        print(msg)
        excerpt = _load_report_excerpt(REPORT)
        if excerpt:
            print("\n--- quality_report.txt (Auszug) ---")
            print(excerpt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
