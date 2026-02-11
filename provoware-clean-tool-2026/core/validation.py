from __future__ import annotations

from pathlib import Path
from typing import Sequence, Type, TypeVar

T = TypeVar("T")


class ValidationError(ValueError):
    """Klare Validierungsfehler in einfacher Sprache mit Next Step."""


def require_type(value: object, expected_type: Type[T], field_name: str) -> T:
    """Validate that a value has the expected type.

    Raises
    ------
    ValidationError
        If the value is not of the expected type.
    """
    if not isinstance(value, expected_type):
        expected_name = expected_type.__name__
        actual_name = type(value).__name__
        raise ValidationError(
            f"Ungültiger Input bei '{field_name}': erwartet {expected_name}, erhalten {actual_name}. "
            "Nächster Schritt: Eingabewert prüfen und erneut versuchen."
        )
    return value


def require_sequence_of_type(
    values: object, item_type: Type[T], field_name: str
) -> Sequence[T]:
    """Validate a sequence and all contained item types."""
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise ValidationError(
            f"Ungültiger Input bei '{field_name}': erwartet Liste/Sequenz. "
            "Nächster Schritt: Eine Liste übergeben und erneut versuchen."
        )
    for index, item in enumerate(values):
        if not isinstance(item, item_type):
            raise ValidationError(
                f"Ungültiger Input bei '{field_name}[{index}]': erwartet {item_type.__name__}, "
                f"erhalten {type(item).__name__}. Nächster Schritt: Listeneinträge korrigieren und erneut versuchen."
            )
    return values


def require_existing_dir(path: object, field_name: str) -> Path:
    """Validate that a path points to an existing directory."""
    path_obj = require_type(path, Path, field_name)
    if not path_obj.exists() or not path_obj.is_dir():
        raise ValidationError(
            f"Ungültiger Input bei '{field_name}': Verzeichnis '{path_obj}' wurde nicht gefunden. "
            "Nächster Schritt: Pfad prüfen oder Verzeichnis erstellen."
        )
    return path_obj


def require_non_negative_number(value: object, field_name: str) -> float:
    """Validate that value is int/float and non-negative."""
    if not isinstance(value, (int, float)):
        raise ValidationError(
            f"Ungültiger Input bei '{field_name}': Zahl erwartet. "
            "Nächster Schritt: Numerischen Wert eintragen und erneut versuchen."
        )
    if value < 0:
        raise ValidationError(
            f"Ungültiger Input bei '{field_name}': Wert darf nicht negativ sein. "
            "Nächster Schritt: Wert auf 0 oder höher setzen."
        )
    return float(value)


def require_condition(condition: bool, message: str) -> None:
    """Validate an output/runtime condition and raise a clear error."""
    if not condition:
        raise ValidationError(message)
