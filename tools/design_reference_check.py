#!/usr/bin/env python3
"""Prüft die Zielvorgaben aus dem Design-Referenzprofil auf Vollständigkeit und A11y-Mindestwerte."""

from __future__ import annotations

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DESIGN_FILE = ROOT_DIR / "data/design_reference_domotic_assistant.json"
THUMBNAIL_FILE = ROOT_DIR / "docs/design_reference_thumbnail.svg"


def _require_type(value: object, expected_type: type, message: str) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(message)


def _require_non_empty_text(value: object, message: str) -> str:
    _require_type(value, str, message)
    text = value.strip()
    if not text:
        raise ValueError(message)
    return text


def _require_output(success: bool, message: str) -> None:
    if not success:
        raise RuntimeError(message)


def _load_payload(path: Path) -> dict:
    _require_type(
        path,
        Path,
        "Designpfad ungültig. Nächster Schritt: Pfad als pathlib.Path übergeben.",
    )
    if not path.exists():
        raise FileNotFoundError(
            "Design-Referenzdatei fehlt. Nächster Schritt: Datei data/design_reference_domotic_assistant.json wiederherstellen."
        )
    content = path.read_text(encoding="utf-8")
    _require_non_empty_text(
        content,
        "Design-Referenz ist leer. Nächster Schritt: JSON-Inhalt aus der letzten Iteration wiederherstellen.",
    )
    payload = json.loads(content)
    _require_type(
        payload,
        dict,
        "Design-Referenz muss ein JSON-Objekt sein. Nächster Schritt: JSON-Struktur prüfen.",
    )
    return payload


def _require_keys(payload: dict, required_keys: list[str]) -> None:
    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise ValueError(
            "Design-Referenz unvollständig: "
            + ", ".join(missing)
            + ". Nächster Schritt: fehlende Bereiche ergänzen und Check erneut starten."
        )


def _validate_a11y_targets(targets: dict) -> None:
    _require_type(
        targets,
        dict,
        "A11y-Bereich fehlt. Nächster Schritt: accessibility_targets als Objekt eintragen.",
    )
    ratio_text = targets.get("contrast_ratio_text_min")
    ratio_ui = targets.get("contrast_ratio_ui_min")
    min_click = targets.get("min_click_target_px")

    if not isinstance(ratio_text, (int, float)) or ratio_text < 4.5:
        raise ValueError(
            "A11y-Kontrast für Text zu niedrig. Nächster Schritt: contrast_ratio_text_min auf mindestens 4.5 setzen."
        )
    if not isinstance(ratio_ui, (int, float)) or ratio_ui < 3.0:
        raise ValueError(
            "A11y-Kontrast für UI zu niedrig. Nächster Schritt: contrast_ratio_ui_min auf mindestens 3.0 setzen."
        )
    if not isinstance(min_click, (int, float)) or min_click < 36:
        raise ValueError(
            "Klickziel zu klein. Nächster Schritt: min_click_target_px auf mindestens 36 setzen."
        )


def _validate_spacing_scale(layout_blueprint: dict) -> None:
    _require_type(
        layout_blueprint,
        dict,
        "Layout-Bereich fehlt. Nächster Schritt: layout_blueprint ergänzen.",
    )
    spacing_scale = layout_blueprint.get("spacing_scale_px")
    _require_type(
        spacing_scale,
        list,
        "spacing_scale_px fehlt. Nächster Schritt: spacing_scale_px mit 4er-Rasterwerten ergänzen.",
    )
    if len(spacing_scale) < 4:
        raise ValueError(
            "Spacing-Skala zu kurz. Nächster Schritt: mindestens vier Abstandswerte eintragen."
        )

    for value in spacing_scale:
        if not isinstance(value, int) or value <= 0 or value % 2 != 0:
            raise ValueError(
                "Spacing-Skala ungültig. Nächster Schritt: nur positive, gerade Pixelwerte verwenden (z. B. 4, 8, 12)."
            )


def _validate_view_questions(questions: list[str]) -> None:
    _require_type(
        questions,
        list,
        "Ansichtsfragen fehlen. Nächster Schritt: view_questions_checklist mit mindestens sechs Fragen ergänzen.",
    )
    cleaned = [
        _require_non_empty_text(
            question,
            "Leere Ansichtsfrage gefunden. Nächster Schritt: Frage mit klarer Sprache ergänzen.",
        )
        for question in questions
    ]
    if len(cleaned) < 6:
        raise ValueError(
            "Zu wenige Ansichtsfragen. Nächster Schritt: mindestens sechs konkrete Prüf-Fragen ergänzen."
        )


def _validate_main_window_preview_mapping(project_mapping: dict) -> None:
    _require_type(
        project_mapping,
        dict,
        "Projekt-Mapping fehlt. Nächster Schritt: project_mapping als Objekt ergänzen.",
    )
    preview_targets = project_mapping.get("main_window_preview_targets")
    _require_type(
        preview_targets,
        dict,
        "Preview-Mapping fehlt. Nächster Schritt: main_window_preview_targets ergänzen.",
    )

    required_keys = [
        "theme_similarity_score_label",
        "target_layout_modes",
        "target_scale_labels",
        "next_step_message_required",
    ]
    missing = [key for key in required_keys if key not in preview_targets]
    if missing:
        raise ValueError(
            "Preview-Mapping unvollständig: "
            + ", ".join(missing)
            + ". Nächster Schritt: Felder in project_mapping.main_window_preview_targets ergänzen."
        )

    score_label = _require_non_empty_text(
        preview_targets.get("theme_similarity_score_label"),
        "Design-Nähe Label fehlt. Nächster Schritt: theme_similarity_score_label als Klartext setzen.",
    )
    if "Design-Nähe" not in score_label:
        raise ValueError(
            "Design-Nähe Label unklar. Nächster Schritt: Label muss 'Design-Nähe' enthalten."
        )

    layout_modes = preview_targets.get("target_layout_modes")
    _require_type(
        layout_modes,
        list,
        "target_layout_modes fehlt. Nächster Schritt: mindestens zwei Layout-Modi als Liste eintragen.",
    )
    if len(layout_modes) < 2:
        raise ValueError(
            "Zu wenige Layout-Modi. Nächster Schritt: mindestens zwei Layout-Modi dokumentieren."
        )
    for mode in layout_modes:
        _require_non_empty_text(
            mode,
            "Leerer Layout-Modus gefunden. Nächster Schritt: nur klare Layout-Bezeichnungen verwenden.",
        )

    scale_labels = preview_targets.get("target_scale_labels")
    _require_type(
        scale_labels,
        list,
        "target_scale_labels fehlt. Nächster Schritt: mindestens zwei Skalierungswerte als Liste eintragen.",
    )
    if len(scale_labels) < 2:
        raise ValueError(
            "Zu wenige Skalierungswerte. Nächster Schritt: mindestens zwei Prozentwerte dokumentieren."
        )

    for label in scale_labels:
        text = _require_non_empty_text(
            label,
            "Leerer Skalierungswert gefunden. Nächster Schritt: Werte wie '115 %' oder '130 %' eintragen.",
        )
        if "%" not in text:
            raise ValueError(
                "Skalierungswert ohne Prozentzeichen gefunden. Nächster Schritt: Prozentangaben in target_scale_labels nutzen."
            )

    if preview_targets.get("next_step_message_required") is not True:
        raise ValueError(
            "Next-Step-Pflicht fehlt. Nächster Schritt: next_step_message_required auf true setzen."
        )


def _validate_thumbnail_reference(path: Path) -> None:
    _require_type(
        path,
        Path,
        "Thumbnail-Pfad ungültig. Nächster Schritt: docs/design_reference_thumbnail.svg als pathlib.Path übergeben.",
    )
    if not path.exists():
        raise FileNotFoundError(
            "Design-Thumbnail fehlt. Nächster Schritt: docs/design_reference_thumbnail.svg wiederherstellen."
        )
    text = path.read_text(encoding="utf-8").strip()
    if not text.startswith("<svg") and "<svg" not in text:
        raise ValueError(
            "Design-Thumbnail ist kein SVG. Nächster Schritt: gültige SVG-Datei in docs/design_reference_thumbnail.svg ablegen."
        )


def main() -> int:
    payload = _load_payload(DESIGN_FILE)
    _require_keys(
        payload,
        [
            "reference",
            "visual_language",
            "palette",
            "layout_blueprint",
            "typography",
            "component_targets",
            "accessibility_targets",
            "view_questions_checklist",
            "project_mapping",
        ],
    )

    _validate_a11y_targets(payload["accessibility_targets"])
    _validate_spacing_scale(payload["layout_blueprint"])
    _validate_view_questions(payload["view_questions_checklist"])
    _validate_main_window_preview_mapping(payload["project_mapping"])
    _validate_thumbnail_reference(THUMBNAIL_FILE)

    _require_output(
        True,
        "Design-Zielvorgaben konnten nicht bestätigt werden. Nächster Schritt: Dateiinhalt prüfen.",
    )
    print(
        "[DESIGN][OK] Design-Zielvorgabe vollständig, a11y-konform und prüfbar dokumentiert."
    )
    print(
        "[DESIGN][HILFE] Nächster Schritt: Änderungen an UI-Abständen/Farben gegen data/design_reference_domotic_assistant.json und docs/design_reference_thumbnail.svg spiegeln."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
