from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .validation import (require_condition, require_existing_dir,
                         require_non_negative_number, require_sequence_of_type,
                         require_type)

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}
VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm"}
ARCHIVE_EXTS = {".zip", ".tar", ".gz", ".bz2", ".7z", ".rar"}


def _classify_file(path: Path) -> str:
    """Return a type label based on the file extension."""
    ext = path.suffix.lower()
    if ext in IMAGE_EXTS:
        return "images"
    if ext in VIDEO_EXTS:
        return "videos"
    if ext in ARCHIVE_EXTS:
        return "archives"
    return "other"


def _parse_size(threshold: str) -> int:
    """Convert a human‑readable size threshold into bytes.

    Supported units: KB, MB, GB. 'any' returns 0.
    """
    if not threshold or threshold == "any":
        return 0
    try:
        threshold = threshold.strip().lower()
        if threshold.endswith("kb"):
            return int(float(threshold[:-2]) * 1024)
        if threshold.endswith("mb"):
            return int(float(threshold[:-2]) * 1024 * 1024)
        if threshold.endswith("gb"):
            return int(float(threshold[:-2]) * 1024 * 1024 * 1024)
        # assume bytes
        return int(threshold)
    except Exception:
        return 0


def _parse_age(age: str) -> float:
    """Convert an age threshold (e.g. '180d') into seconds.

    Supported suffixes: d (days), h (hours), m (minutes). 'any' returns 0.
    """
    if not age or age == "any":
        return 0.0
    try:
        age = age.strip().lower()
        if age.endswith("d"):
            return float(age[:-1]) * 24 * 3600
        if age.endswith("h"):
            return float(age[:-1]) * 3600
        if age.endswith("m"):
            return float(age[:-1]) * 60
        # assume seconds
        return float(age)
    except Exception:
        return 0.0


@dataclass
class ScanResult:
    path: Path
    size: int
    mtime: float
    file_type: str
    duplicate_group: Optional[int] = None


def scan_directory(
    root: Path,
    types: List[str],
    size_threshold: int,
    age_threshold: float,
) -> List[ScanResult]:
    """Scan a directory and return files matching the filter criteria.

    Parameters
    ----------
    root: Path
        The directory to scan recursively.
    types: List[str]
        File type labels to include (images, videos, archives, other).
    size_threshold: int
        Files smaller than this size (in bytes) are ignored. Zero means no threshold.
    age_threshold: float
        Files younger than this age (in seconds) are ignored. Zero means no threshold.

    Returns
    -------
    List[ScanResult]
        A list of files matching the criteria.
    """
    validated_root = require_existing_dir(root, "root")
    validated_types = set(require_sequence_of_type(types, str, "types"))
    validated_size_threshold = int(
        require_non_negative_number(size_threshold, "size_threshold")
    )
    validated_age_threshold = require_non_negative_number(
        age_threshold, "age_threshold"
    )
    results: List[ScanResult] = []
    now = time.time()
    for dirpath, _dirnames, filenames in os.walk(validated_root):
        for name in filenames:
            path = Path(dirpath) / name
            try:
                stat = path.stat()
            except Exception:
                continue
            file_type = _classify_file(path)
            if file_type not in validated_types:
                continue
            if validated_size_threshold and stat.st_size < validated_size_threshold:
                continue
            if validated_age_threshold:
                age = now - stat.st_mtime
                if age < validated_age_threshold:
                    continue
            results.append(
                ScanResult(
                    path=path,
                    size=stat.st_size,
                    mtime=stat.st_mtime,
                    file_type=file_type,
                )
            )
    require_condition(
        all(item.file_type in validated_types for item in results),
        (
            "Interner Scanner-Fehler: Ergebnis enthält einen Dateityp außerhalb des Filters. "
            "Nächster Schritt: Protokoll prüfen und Scan erneut starten."
        ),
    )
    return results


def detect_duplicates(
    files: List[ScanResult],
    mode: str = "none",
) -> Dict[int, List[ScanResult]]:
    """Group duplicate files.

    Parameters
    ----------
    files: List[ScanResult]
        A list of scan results from `scan_directory()`.
    mode: str
        Duplicate detection mode: 'none' to skip, 'quick' to group by (name, size) and 'safe' to also compare sha256 hashes.

    Returns
    -------
    Dict[int, List[ScanResult]]
        A dictionary mapping group identifiers to lists of duplicates. Each group contains two or more items.
    """
    validated_files = require_sequence_of_type(files, ScanResult, "files")
    validated_mode = require_type(mode, str, "mode").strip().lower()
    if validated_mode not in {"none", "quick", "safe"}:
        return {}
    groups: Dict[str, List[ScanResult]] = {}
    if validated_mode == "none":
        return {}
    for f in validated_files:
        key = (f.path.name, f.size)
        groups.setdefault(str(key), []).append(f)
    # For safe mode, refine by comparing hashes
    if validated_mode == "safe":
        refined: Dict[str, List[ScanResult]] = {}
        for group_files in groups.values():
            if len(group_files) < 2:
                continue
            # compute hashes
            hashes: Dict[str, List[ScanResult]] = {}
            for f in group_files:
                h = _file_hash(f.path)
                hashes.setdefault(h, []).append(f)
            for files_with_same_hash in hashes.values():
                if len(files_with_same_hash) > 1:
                    refined[str(id(files_with_same_hash))] = files_with_same_hash
        # assign refined to groups; if none, return {}
        out: Dict[int, List[ScanResult]] = {}
        group_id = 0
        for g in refined.values():
            out[group_id] = g
            group_id += 1
        require_condition(
            all(len(group) > 1 for group in out.values()),
            (
                "Interner Duplikat-Fehler: Eine Duplikatgruppe ist zu klein. "
                "Nächster Schritt: Protokoll prüfen und Duplikatmodus auf 'quick' testen."
            ),
        )
        return out
    else:
        out: Dict[int, List[ScanResult]] = {}
        group_id = 0
        for g in groups.values():
            if len(g) > 1:
                out[group_id] = g
                group_id += 1
        require_condition(
            all(len(group) > 1 for group in out.values()),
            (
                "Interner Duplikat-Fehler: Ergebnis enthält eine Gruppe mit weniger als 2 Dateien. "
                "Nächster Schritt: Protokoll prüfen und Duplikaterkennung erneut ausführen."
            ),
        )
        return out


def _file_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute SHA256 hash of a file.

    Parameters
    ----------
    path: Path
        File path to hash.
    chunk_size: int, optional
        Read chunk size in bytes. Defaults to 1 MB.

    Returns
    -------
    str
        A hex digest of the file.
    """
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                h.update(data)
    except Exception:
        return ""
    return h.hexdigest()
