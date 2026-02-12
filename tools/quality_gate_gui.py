#!/usr/bin/env python3
"""Qualitätsprüfung-Dialog (ohne externe Abhängigkeiten).

Wird aufgerufen, wenn tools/run_quality_checks.sh fehlschlägt.
Zeigt einen einheitlichen Kurzbericht wie in start.sh mit klaren Next Steps.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
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


def _validate_debug_log_mode(raw_value: str) -> tuple[str, str]:
    """Validiert DEBUG_LOG_MODE robust auf 0/1 mit laienfreundlicher Hilfe."""

    value = str(raw_value).strip()
    if value in {"0", "1"}:
        return value, ""
    return (
        "0",
        "[HILFE] DEBUG_LOG_MODE war ungültig. Verwenden Sie DEBUG_LOG_MODE=1 für mehr Details oder 0 für Standard.",
    )


def _run_action_command(action_key: str) -> str:
    """Führt sichere Folgeaktionen aus und liefert einen klaren Ergebnistext zurück."""

    commands = {
        "auto_fix": ["bash", "tools/run_quality_checks.sh"],
        "quality": ["bash", "tools/run_quality_checks.sh"],
        "restart": ["bash", "start.sh"],
    }
    env = os.environ.copy()
    if action_key == "auto_fix":
        env["AUTO_FIX"] = "1"

    cmd = commands.get(action_key)
    if cmd is None:
        return "[WARN] Unbekannte Aktion. Bitte führen Sie den Befehl manuell aus."

    result = subprocess.run(
        cmd,
        cwd=APP_DIR,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return (
            f"[OK] Aktion erfolgreich: {' '.join(cmd)}\n"
            "[HILFE] Nächster Schritt: Prüfen Sie den Report und wiederholen Sie den Start nur bei Bedarf."
        )
    return (
        f"[WARN] Aktion fehlgeschlagen (Exitcode {result.returncode}): {' '.join(cmd)}\n"
        "[HILFE] Öffnen Sie exports/quality_report.txt und nutzen Sie danach den angezeigten Reparaturbefehl."
    )


def main() -> int:
    debug_mode, debug_hint = _validate_debug_log_mode(os.getenv("DEBUG_LOG_MODE", "0"))
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
        "Tastatur-Hilfe: Mit Tab wechseln, Enter bestätigen, Esc schließen.\n"
        f"Debug-Modus: {debug_mode} (1 = ausführlich, 0 = Standard)\n"
        f"{quickfix_block}\n"
    )
    if debug_hint:
        msg = f"{msg}\n{debug_hint}\n"

    selected_action = ""
    if shutil.which("zenity"):
        action_prompt = (
            "Was möchten Sie jetzt tun?\n"
            "- auto_fix: automatische Reparatur starten\n"
            "- quality: Qualitätslauf erneut starten\n"
            "- restart: Startskript ausführen\n"
            "- report: nur Report öffnen"
        )
        action_result = subprocess.run(
            [
                "zenity",
                "--entry",
                "--title",
                "Qualitätsprüfung",
                "--width=780",
                "--entry-text",
                "report",
                "--text",
                f"{msg}\n{action_prompt}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        selected_action = action_result.stdout.strip().lower()
        if selected_action not in {"", "report", "auto_fix", "quality", "restart"}:
            selected_action = "report"

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
        if sys.stdin.isatty():
            print(
                "\nAktion wählen [report/auto_fix/quality/restart], Enter für 'report':"
            )
            selected_action = input().strip().lower() or "report"
        else:
            selected_action = "report"

    if selected_action in {"auto_fix", "quality", "restart"}:
        print(_run_action_command(selected_action))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
