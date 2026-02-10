from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict


DEFAULTS_PATH = Path(__file__).resolve().parent.parent / "data" / "settings.json"


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
        # load defaults
        if DEFAULTS_PATH != settings_path and DEFAULTS_PATH.exists():
            try:
                defaults = json.loads(DEFAULTS_PATH.read_text(encoding="utf-8"))
            except Exception:
                defaults = {}
        else:
            defaults = data
        # merge
        merged = {**defaults, **data}
        filters = Filters.from_dict(merged.get("filters", {}))
        return Settings(
            theme=str(merged.get("theme", "light")),
            large_text=bool(merged.get("large_text", False)),
            download_dir=str(merged.get("download_dir", "")),
            presets=str(merged.get("presets", "standard")),
            filters=filters,
            duplicates_mode=str(merged.get("duplicates_mode", "none")),
            confirm_threshold=int(merged.get("confirm_threshold", 10)),
        )

    def save(self, path: Path | None = None) -> None:
        """Save settings to disk."""
        settings_path = path or DEFAULTS_PATH
        data = asdict(self)
        # nested dataclass manually convert
        data["filters"] = self.filters.to_dict()
        try:
            settings_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass
