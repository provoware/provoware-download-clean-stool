from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [
    ROOT / "start.sh",
    ROOT / "tools" / "run_quality_checks.sh",
    ROOT / "tools" / "release_gap_report.py",
    ROOT / "tools" / "a11y_theme_check.py",
    ROOT / "tools" / "smoke_test.py",
    ROOT / "core" / "selfcheck.py",
]
HELP_PATTERN = re.compile(
    r"Nächster Schritt|HILFE|erneut|Reparatur|prüfen", re.IGNORECASE
)


@dataclass
class Finding:
    file_path: Path
    line_no: int
    line_text: str
    reason: str


def _validate_text(value: str, label: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError(
            f"{label} fehlt. Nächster Schritt: Übergabe prüfen und Audit erneut starten."
        )
    return text


def _has_help_nearby(lines: list[str], index: int, window: int = 4) -> bool:
    if window < 1:
        raise ValueError(
            "Audit-Fenster muss >= 1 sein. Nächster Schritt: Standardwert 4 verwenden."
        )
    start = max(0, index - window)
    end = min(len(lines), index + window + 1)
    area = "\n".join(lines[start:end])
    return HELP_PATTERN.search(area) is not None


def _find_exit_markers(lines: list[str], file_suffix: str) -> list[tuple[int, str]]:
    if file_suffix == ".sh":
        pattern = re.compile(r"\bexit\s+1\b")
    else:
        pattern = re.compile(r"raise\s+SystemExit\(1\)|return\s+False\s*,")
    markers: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        if pattern.search(line):
            markers.append((idx, line.rstrip()))
    return markers


def run_audit() -> int:
    findings: list[Finding] = []
    checked_nodes = 0

    for file_path in TARGETS:
        if not file_path.exists():
            findings.append(
                Finding(
                    file_path=file_path,
                    line_no=0,
                    line_text="",
                    reason="Datei fehlt im Audit-Ziel.",
                )
            )
            continue

        content = file_path.read_text(encoding="utf-8")
        _validate_text(content, f"Dateiinhalt {file_path.name}")
        lines = content.splitlines()
        markers = _find_exit_markers(lines, file_path.suffix)

        for idx, line_text in markers:
            checked_nodes += 1
            if not _has_help_nearby(lines, idx):
                findings.append(
                    Finding(
                        file_path=file_path,
                        line_no=idx + 1,
                        line_text=_validate_text(line_text, "Exit-Zeile"),
                        reason="Kein klarer Lösungs-Hinweis in unmittelbarer Nähe gefunden.",
                    )
                )

    if findings:
        print("[EXIT-AUDIT][WARN] Exit-Knoten ohne klare Lösung gefunden:")
        for finding in findings:
            location = f"{finding.file_path.relative_to(ROOT)}:{finding.line_no}"
            print(f"  - {location}: {finding.reason}")
            if finding.line_text:
                print(f"    Auslöser: {finding.line_text}")
        print(
            "[EXIT-AUDIT][HILFE] Nächster Schritt: In der gemeldeten Datei direkt vor dem Exit einen kurzen Lösungssatz ergänzen."
        )
        return 1

    print(
        f"[EXIT-AUDIT][OK] Geprüfte Exit-Knoten: {checked_nodes}. Jeder Knoten bietet einen Lösungs-Hinweis."
    )
    print(
        "[EXIT-AUDIT][HILFE] Optional: Nach neuen Fehlerpfaden erneut prüfen mit `python3 tools/exit_path_audit.py`."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run_audit())
