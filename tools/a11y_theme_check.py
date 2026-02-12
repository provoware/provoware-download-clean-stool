"""Automatischer A11y-Theme-Check für Kontrast und Fokus-Hinweise.

Prüft die in ``app.main.MainWindow.STYLES`` definierten Themes auf:
- Mindestkontrast zwischen Vordergrund und Hintergrund (WCAG-ähnlich)
- Fokus-Selektor (sichtbarer Tastaturfokus)

Ausgaben sind bewusst in einfacher Sprache mit klaren Next Steps gehalten.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

HEX_COLOR_PATTERN = re.compile(r"#[0-9a-fA-F]{6}")


@dataclass(frozen=True)
class ThemeCheckResult:
    """Ergebnis je Theme."""

    name: str
    contrast_ratio: float
    selection_ratio: float
    disabled_ratio: float
    has_focus_rule: bool


class ThemeCheckError(ValueError):
    """Fehler für verständliche Prüfmeldungen."""


def _validate_hex_color(color: str) -> str:
    """Validiert eine Hex-Farbe und gibt sie normalisiert zurück."""
    if not isinstance(color, str):
        raise ThemeCheckError("Farbwert ist ungültig: Es wurde kein Text übergeben.")
    value = color.strip()
    if not HEX_COLOR_PATTERN.fullmatch(value):
        raise ThemeCheckError(
            f"Farbwert '{color}' ist ungültig. Erwartet wird #RRGGBB."
        )
    return value.lower()


def _hex_to_rgb(color: str) -> tuple[float, float, float]:
    """Konvertiert #RRGGBB nach RGB-Werten im Bereich 0..1."""
    normalized = _validate_hex_color(color)
    return tuple(int(normalized[idx : idx + 2], 16) / 255 for idx in (1, 3, 5))


def _relative_luminance(color: str) -> float:
    """Berechnet die relative Leuchtdichte gemäß WCAG-Formel."""

    def _channel(value: float) -> float:
        if value <= 0.03928:
            return value / 12.92
        return ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = _hex_to_rgb(color)
    luminance = (
        0.2126 * _channel(red) + 0.7152 * _channel(green) + 0.0722 * _channel(blue)
    )
    if luminance < 0 or luminance > 1:
        raise ThemeCheckError(
            "Leuchtdichte liegt außerhalb des gültigen Bereichs 0..1."
        )
    return luminance


def _contrast_ratio(foreground: str, background: str) -> float:
    """Berechnet das Kontrastverhältnis zweier Farben."""
    lum_foreground = _relative_luminance(foreground)
    lum_background = _relative_luminance(background)
    bright, dark = sorted((lum_foreground, lum_background), reverse=True)
    ratio = (bright + 0.05) / (dark + 0.05)
    if ratio < 1.0:
        raise ThemeCheckError(
            "Kontrastberechnung lieferte einen ungültigen Wert < 1.0."
        )
    return ratio


def _extract_property(stylesheet: str, selector: str, prop: str) -> str:
    """Extrahiert einen CSS-ähnlichen Property-Wert aus einem Selektorblock."""
    if not isinstance(stylesheet, str) or not stylesheet.strip():
        raise ThemeCheckError("Theme-Stylesheet ist leer oder ungültig.")

    block_pattern = re.compile(rf"{re.escape(selector)}\s*\{{(.*?)\}}", re.DOTALL)
    block_match = block_pattern.search(stylesheet)
    if block_match is None:
        raise ThemeCheckError(
            f"Selektor '{selector}' wurde nicht gefunden. Bitte Theme-Styles prüfen."
        )

    prop_pattern = re.compile(rf"(?<![\w-]){re.escape(prop)}\s*:\s*([^;]+)")
    prop_match = prop_pattern.search(block_match.group(1))
    if prop_match is None:
        raise ThemeCheckError(f"Eigenschaft '{prop}' fehlt im Selektor '{selector}'.")

    value = prop_match.group(1).strip()
    _validate_hex_color(value)
    return value


def _extract_first_available_property(
    stylesheet: str, selectors: tuple[str, ...], prop: str
) -> str:
    """Liest die erste verfügbare Eigenschaft aus einer Selektorliste."""
    for selector in selectors:
        try:
            return _extract_property(stylesheet, selector, prop)
        except ThemeCheckError:
            continue
    raise ThemeCheckError(
        f"Eigenschaft '{prop}' wurde in keinem erwarteten Selektor gefunden: {', '.join(selectors)}"
    )


def _extract_optional_property(
    stylesheet: str, selectors: tuple[str, ...], prop: str, fallback: str
) -> str:
    """Liest eine Eigenschaft oder nutzt einen validierten Fallback."""
    try:
        return _extract_first_available_property(stylesheet, selectors, prop)
    except ThemeCheckError:
        return _validate_hex_color(fallback)


def run_theme_checks(
    styles: dict[str, str], minimum_ratio: float = 4.5
) -> list[ThemeCheckResult]:
    """Prüft Themes auf Kontrast, Fokusregeln und Zustandsfarben."""
    if not isinstance(styles, dict) or not styles:
        raise ThemeCheckError("Es wurden keine Themes zum Prüfen übergeben.")
    if minimum_ratio < 1.0:
        raise ThemeCheckError("Mindest-Kontrast muss mindestens 1.0 sein.")

    results: list[ThemeCheckResult] = []
    for theme_name, stylesheet in styles.items():
        foreground = _extract_property(stylesheet, "QWidget", "color")
        background = _extract_property(stylesheet, "QWidget", "background-color")
        selection_bg = _extract_optional_property(
            stylesheet,
            ("QListWidget::item:selected",),
            "background-color",
            fallback=background,
        )
        selection_fg = _extract_optional_property(
            stylesheet,
            ("QListWidget::item:selected",),
            "color",
            fallback=foreground,
        )
        disabled_bg = _extract_optional_property(
            stylesheet,
            ("QPushButton:disabled",),
            "background-color",
            fallback=background,
        )
        disabled_fg = _extract_optional_property(
            stylesheet,
            ("QPushButton:disabled",),
            "color",
            fallback=foreground,
        )

        ratio = _contrast_ratio(foreground, background)
        selection_ratio = _contrast_ratio(selection_fg, selection_bg)
        disabled_ratio = _contrast_ratio(disabled_fg, disabled_bg)
        has_focus = ":focus" in stylesheet
        if not has_focus:
            raise ThemeCheckError(
                f"Theme '{theme_name}' hat keine :focus-Regel. Tastaturfokus wäre unsichtbar."
            )
        if ratio < minimum_ratio:
            raise ThemeCheckError(
                f"Theme '{theme_name}' hat zu wenig Standard-Kontrast ({ratio:.2f}:1). "
                f"Benötigt sind mindestens {minimum_ratio:.1f}:1."
            )
        if selection_ratio < minimum_ratio:
            raise ThemeCheckError(
                f"Theme '{theme_name}' hat zu wenig Kontrast bei Auswahlfeldern ({selection_ratio:.2f}:1). "
                f"Bitte Auswahlfarben klarer trennen (mindestens {minimum_ratio:.1f}:1)."
            )
        if disabled_ratio < 3.0:
            raise ThemeCheckError(
                f"Theme '{theme_name}' hat zu wenig Kontrast bei deaktivierten Buttons ({disabled_ratio:.2f}:1). "
                "Bitte Lesbarkeit für den deaktivierten Zustand erhöhen (mindestens 3.0:1)."
            )
        results.append(
            ThemeCheckResult(
                name=theme_name,
                contrast_ratio=ratio,
                selection_ratio=selection_ratio,
                disabled_ratio=disabled_ratio,
                has_focus_rule=has_focus,
            )
        )

    if not results:
        raise ThemeCheckError("Theme-Prüfung lieferte kein Ergebnis.")
    return results


def _load_styles() -> dict[str, str]:
    """Lädt die Theme-Styles robust aus app/main.py ohne GUI-Import."""
    app_main_path = Path(__file__).resolve().parents[1] / "app" / "main.py"
    if not app_main_path.exists():
        raise ThemeCheckError("Datei app/main.py fehlt. Theme-Check kann nicht laufen.")

    try:
        tree = ast.parse(app_main_path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        raise ThemeCheckError(f"app/main.py enthält Syntaxfehler: {exc}") from exc

    styles_node: ast.Dict | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "STYLES":
                    if isinstance(node.value, ast.Dict):
                        styles_node = node.value
                        break
            if styles_node is not None:
                break

    if styles_node is None:
        raise ThemeCheckError("STYLES-Definition wurde in app/main.py nicht gefunden.")

    parsed_styles: dict[str, str] = {}
    for key_node, value_node in zip(styles_node.keys, styles_node.values):
        if not isinstance(key_node, ast.Constant) or not isinstance(
            key_node.value, str
        ):
            raise ThemeCheckError("Theme-Name in STYLES ist ungültig (kein Text).")
        if not isinstance(value_node, ast.Constant) or not isinstance(
            value_node.value, str
        ):
            raise ThemeCheckError(
                f"Theme '{key_node.value}' hat kein statisches Stylesheet als Text."
            )
        parsed_styles[key_node.value] = value_node.value

    if not parsed_styles:
        raise ThemeCheckError("STYLES ist leer. Keine Themes verfügbar.")
    return parsed_styles


def main() -> int:
    try:
        results = run_theme_checks(_load_styles())
    except ThemeCheckError as exc:
        print(f"[A11Y][WARN] {exc}")
        print(
            "[A11Y][HILFE] Nächster Schritt: Theme-Farben/Fokus-Regeln in app/main.py prüfen."
        )
        return 1
    except Exception as exc:  # pragma: no cover - defensive fallback for startup checks
        print(f"[A11Y][WARN] Unerwarteter Fehler im A11y-Check: {exc}")
        print(
            "[A11Y][HILFE] Nächster Schritt: python tools/a11y_theme_check.py erneut starten und Log prüfen."
        )
        return 1

    for result in results:
        print(
            "[A11Y][OK] "
            f"Theme '{result.name}': Standard-Kontrast {result.contrast_ratio:.2f}:1, "
            f"Auswahl-Kontrast {result.selection_ratio:.2f}:1, "
            f"Disabled-Kontrast {result.disabled_ratio:.2f}:1, "
            f"Fokusregel vorhanden={result.has_focus_rule}"
        )
    print("[A11Y][OK] Automatischer Theme-A11y-Check erfolgreich.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
