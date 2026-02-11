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
    novice_mode: bool
    allowed_file_types: List[str]
    organizer_target_mode: str
    organizer_target_path: str
    assistant_tips_enabled: bool

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
            novice_mode=bool(merged.get("novice_mode", True)),
            allowed_file_types=Settings._normalize_allowed_file_types(
                merged.get(
                    "allowed_file_types",
                    ["images", "documents", "videos", "audio", "archives", "other"],
                )
            ),
            organizer_target_mode=Settings._normalize_target_mode(
                str(merged.get("organizer_target_mode", "single_folder"))
            ),
            organizer_target_path=Settings._normalize_target_path(
                str(merged.get("organizer_target_path", ""))
            ),
            assistant_tips_enabled=bool(merged.get("assistant_tips_enabled", True)),
        )

    @staticmethod
    def _normalize_allowed_file_types(raw_types: object) -> List[str]:
        """Normalize selected file types with safe defaults for novice users."""

        allowed = {"images", "documents", "videos", "audio", "archives", "other"}
        if not isinstance(raw_types, list):
            raise ValueError(
                "Dateitypen-Auswahl ist ungültig. Nächster Schritt: Bitte Dateitypen per Schalter neu wählen."
            )
        normalized = [
            str(item).strip().lower() for item in raw_types if str(item).strip()
        ]
        filtered = [item for item in normalized if item in allowed]
        if not filtered:
            return ["images", "documents", "videos", "other"]
        return list(dict.fromkeys(filtered))

    @staticmethod
    def _normalize_target_mode(mode: str) -> str:
        """Validate and normalize organizer target mode."""

        supported_modes = {"single_folder", "topic_folders"}
        clean_mode = mode.strip().lower()
        if clean_mode not in supported_modes:
            return "single_folder"
        return clean_mode

    @staticmethod
    def _normalize_target_path(path_value: str) -> str:
        """Normalize target path text and validate stable output."""

        clean_path = path_value.strip()
        if not clean_path:
            return ""
        return str(Path(clean_path).expanduser())

    def beginner_setting_hints(self) -> Dict[str, str]:
        """Provide simple, actionable setting help texts for non-technical users."""

        active_types = ", ".join(self.allowed_file_types)
        hints = {
            "novice_mode": "Einfacher Modus: zeigt nur klare Schalter und blendet Expertenoptionen aus.",
            "allowed_file_types": (
                f"Dateitypen-Schalter aktiv: {active_types}. Tipp: Für mehr Ruhe nur Bilder + Dokumente aktiv lassen."
            ),
            "organizer_target_mode": (
                "Ordnerziel: Ein Sammelordner (single_folder) oder Themenordner (topic_folders)."
            ),
            "organizer_target_path": (
                "Zielpfad: Wählen Sie am besten einen festen Ordner wie ~/Sortiert, damit nichts verloren geht."
            ),
            "assistant_tips_enabled": (
                "Hilfehinweise: Zeigt kurze Next Steps wie 'Erneut versuchen', 'Reparatur', 'Protokoll'."
            ),
        }
        if not hints:
            raise RuntimeError(
                "Einstellungs-Hilfe konnte nicht aufgebaut werden. Nächster Schritt: Einstellungen laden und erneut öffnen."
            )
        return hints

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
