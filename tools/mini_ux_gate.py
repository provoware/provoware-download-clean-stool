#!/usr/bin/env python3
"""Mini-UX-Gate für einfache Sprache, Next Steps und Basis-A11y-Hinweise.

Prüft zentrale Dateien auf:
- deutsche Hilfehinweise im betroffenen Bereich,
- klare Next-Step-Formulierung,
- Hinweise auf Kontrast/Fokus für Barrierefreiheit.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = {
    "start_hilfe": {
        "file": ROOT / "start.sh",
        "must_contain": ["[HILFE]", "Nächster Schritt", "Kontrast"],
        "hint": "Ergänzen Sie in start.sh kurze [HILFE]-Zeilen mit 'Nächster Schritt' und Kontrast-Hinweis.",
    },
    "quality_dialog_hilfe": {
        "file": ROOT / "tools" / "quality_gate_gui.py",
        "must_contain": ["Tastatur-Hilfe", "Nächster Schritt", "Auto-Fix"],
        "hint": "Ergänzen Sie im Qualitätsdialog eine Tastatur-Hilfe und konkrete Auto-Fix-Schritte.",
    },
    "gui_focus": {
        "file": ROOT / "app" / "main.py",
        "must_contain": [":focus", "Kontrast", "Nächster Schritt"],
        "hint": "Ergänzen Sie in app/main.py Fokus-/Kontrast-Hinweise und einen klaren nächsten Schritt.",
    },
}


def validate_check_config(check_name: str, cfg: dict[str, object]) -> tuple[bool, str]:
    """Validiert die Check-Konfiguration und liefert klare Fehlhinweise.

    Input:
        check_name: Name des Checks.
        cfg: Konfigurations-Dictionary.
    Output:
        (ok, message) mit laienfreundlicher Hilfe bei Fehlern.
    """
    file_path = cfg.get("file")
    must_contain = cfg.get("must_contain")
    hint = cfg.get("hint")

    if not isinstance(file_path, Path):
        return (
            False,
            f"[MINI-UX][WARN] {check_name}: Konfiguration ungültig (file ist kein Pfad).",
        )
    if (
        not isinstance(must_contain, list)
        or not must_contain
        or any(
            not isinstance(token, str) or not token.strip() for token in must_contain
        )
    ):
        return (
            False,
            f"[MINI-UX][WARN] {check_name}: Konfiguration ungültig (must_contain braucht mindestens ein Text-Token).",
        )
    if not isinstance(hint, str) or not hint.strip():
        return (
            False,
            f"[MINI-UX][WARN] {check_name}: Konfiguration ungültig (hint fehlt).",
        )
    return True, ""


def run() -> int:
    warnings = 0
    print("[MINI-UX] Starte Mini-UX-Gate (2-Minuten-Check, statisch).")

    for check_name, cfg in CHECKS.items():
        ok_cfg, cfg_message = validate_check_config(check_name, cfg)
        if not ok_cfg:
            print(cfg_message)
            print(
                "[MINI-UX][HILFE] Nächster Schritt: Konfiguration im selben Check-Block korrigieren und Gate erneut starten."
            )
            warnings += 1
            continue

        file_path = cfg["file"]
        if not file_path.exists():
            print(f"[MINI-UX][WARN] Datei fehlt: {file_path.relative_to(ROOT)}")
            print(f"[MINI-UX][HILFE] Nächster Schritt: {cfg['hint']}")
            warnings += 1
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(
                f"[MINI-UX][WARN] Datei kann nicht gelesen werden: {file_path.relative_to(ROOT)} ({exc})"
            )
            print(
                "[MINI-UX][HILFE] Nächster Schritt: Datei-Rechte prüfen und den Check erneut starten."
            )
            warnings += 1
            continue

        missing = [token for token in cfg["must_contain"] if token not in content]
        if missing:
            print(
                f"[MINI-UX][WARN] {check_name}: fehlende Hinweise in {file_path.relative_to(ROOT)} -> {', '.join(missing)}"
            )
            print(f"[MINI-UX][HILFE] Nächster Schritt: {cfg['hint']}")
            print("[MINI-UX][HILFE] Danach erneut prüfen: python tools/mini_ux_gate.py")
            warnings += 1
        else:
            print(
                f"[MINI-UX][OK] {check_name}: Basis-Hinweise vorhanden ({file_path.relative_to(ROOT)})."
            )

    if warnings:
        print(f"[MINI-UX][WARN] Mini-UX-Gate beendet mit {warnings} Warnung(en).")
        print(
            "[MINI-UX][HILFE] Nächster Schritt: Erst die erste Warnung beheben, dann Check erneut starten."
        )
        return 1

    print("[MINI-UX][OK] Mini-UX-Gate bestanden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
