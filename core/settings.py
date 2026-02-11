from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

DEFAULTS_PATH = Path(__file__).resolve().parent.parent / "data" / "settings.json"
SCHEMA_VERSION = 2


def _default_ui_texts() -> Dict[str, str]:
    """Central fallback catalog for user-facing texts (German)."""
    return {
        "app_title": "Downloads Organizer",
        "error_title": "Fehler",
        "warn_missing_folder_title": "Fehlende Angabe",
        "warn_missing_folder_body": "Bitte wählen Sie einen Ordner aus.",
        "action_retry": "Erneut versuchen",
        "action_repair": "Reparatur",
        "action_log": "Protokoll",
    }


@dataclass
class Filters:
    """Represents filter options for the scanner."""

    types: List[str]
    size: str
    age: str

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "Filters":
        return Filters(
            types=list(data.get("types", [])),
            size=str(data.get("size", "any")),
            age=str(data.get("age", "any")),
        )

    def to_dict(self) -> Dict[str, object]:
        return {"types": self.types, "size": self.size, "age": self.age}


@dataclass
class Settings:
    """User‑modifiable settings.

    Settings are stored in JSON format in `data/settings.json`. When
    loaded, missing values are filled with defaults from that file.
    """

    theme: str
    large_text: bool
    download_dir: str
    presets: str
    filters: Filters
    duplicates_mode: str
    confirm_threshold: int
    schema_version: int
    file_revision: int
    ui_texts: Dict[str, str]

    @staticmethod
    def load(path: Path | None = None) -> "Settings":
        """Load settings from disk or fall back to defaults.

        Parameters
        ----------
        path: Path, optional
            The path to the settings JSON file. If not provided, the default
            settings file in the `data` directory will be used.
        """

        settings_path = path or DEFAULTS_PATH
        if settings_path.exists():
            try:
                data = json.loads(settings_path.read_text(encoding="utf-8"))
            except Exception:
                data = {}
        else:
            data = {}

        if DEFAULTS_PATH != settings_path and DEFAULTS_PATH.exists():
            try:
                defaults = json.loads(DEFAULTS_PATH.read_text(encoding="utf-8"))
            except Exception:
                defaults = {}
        else:
            defaults = data

        merged = {**defaults, **data}
        filters = Filters.from_dict(merged.get("filters", {}))
        ui_texts = _default_ui_texts()
        raw_ui_texts = merged.get("ui_texts", {})
        if isinstance(raw_ui_texts, dict):
            ui_texts.update({str(k): str(v) for k, v in raw_ui_texts.items()})

        return Settings(
            theme=str(merged.get("theme", "light")),
            large_text=bool(merged.get("large_text", False)),
            download_dir=str(merged.get("download_dir", "")),
            presets=str(merged.get("presets", "standard")),
            filters=filters,
            duplicates_mode=str(merged.get("duplicates_mode", "none")),
            confirm_threshold=int(merged.get("confirm_threshold", 10)),
            schema_version=max(int(merged.get("schema_version", 1)), SCHEMA_VERSION),
            file_revision=max(int(merged.get("file_revision", 0)), 0),
            ui_texts=ui_texts,
        )

    def save(self, path: Path | None = None) -> None:
        """Save settings to disk with deterministic version metadata."""

        settings_path = path or DEFAULTS_PATH
        self.schema_version = SCHEMA_VERSION
        self.file_revision = max(self.file_revision, 0) + 1

        data = asdict(self)
        data["filters"] = self.filters.to_dict()
        data["ui_texts"] = {str(k): str(v) for k, v in self.ui_texts.items()}

        try:
            settings_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
        except Exception:
            pass
