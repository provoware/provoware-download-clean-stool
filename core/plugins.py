"""
Basismodul für das Plugin‑System des Provoware Clean Tool.

Dieses Modul definiert ein einfaches Plugin‑Interface und eine dynamische
Ladefunktion. Plugins können im Verzeichnis `plugins/` platziert werden
und müssen eine Klasse `Plugin` bereitstellen, die von
`PluginInterface` erbt. Die Ladefunktion sucht in diesem Verzeichnis
nach Python‑Dateien und instanziiert gefundene Plugins.

Plugins ermöglichen es, Scanner‑, Export‑ oder Analysefunktionen
hinzuzufügen, ohne die Kernlogik zu verändern. Jede Plugin‑Klasse
muss mindestens das Attribut `name` definieren und kann die Methode
`init(settings)` überschreiben, um sich beim Start zu initialisieren.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import List, Optional, Type


class PluginInterface:
    """Basisklasse für Plugins.

    Plugins sollten dieses Interface implementieren. Jedes Plugin
    repräsentiert eine eigenständige Erweiterung (z. B. einen neuen
    Dateiscanner oder einen Exporter) und wird zur Laufzeit geladen.
    """

    name: str = "UnnamedPlugin"

    def init(self, settings: object) -> Optional[object]:
        """Initialisiert das Plugin mit den aktuellen Einstellungen.

        Diese Methode kann überschrieben werden, um dem Kern neue
        Aktionen oder Datenstrukturen zurückzugeben. Sie sollte ein
        Objekt (z. B. eine Liste neuer Aktionen) oder `None` liefern.
        """
        return None


def discover_plugins(directory: Path) -> List[PluginInterface]:
    """Durchsucht das angegebene Verzeichnis nach Plugins.

    Ein Plugin ist eine Python‑Datei, die eine Klasse `Plugin`
    exportiert, die von `PluginInterface` erbt. Gefundene Plugins
    werden instanziiert und in einer Liste zurückgegeben. Fehler beim
    Laden einzelner Module führen nicht zum Abbruch, sondern werden
    ignoriert, damit ein defektes Plugin den Start nicht verhindert.

    Args:
        directory: Das Verzeichnis, in dem nach Plugins gesucht wird.

    Returns:
        Eine Liste instanziierter Plugins.
    """

    plugins: List[PluginInterface] = []
    if not directory.exists() or not directory.is_dir():
        return plugins

    for file in directory.iterdir():
        if file.suffix == ".py" and not file.name.startswith("__"):
            module_name = file.stem
            try:
                # Module relativ zum Plugins-Paket importieren.
                module = importlib.import_module(f"plugins.{module_name}")
                plugin_class: Optional[Type[PluginInterface]] = getattr(module, "Plugin", None)
                if plugin_class and issubclass(plugin_class, PluginInterface):
                    plugin_instance = plugin_class()  # type: ignore[call-arg]
                    plugins.append(plugin_instance)
            except Exception:
                # Beim Laden eines Plugins keine Unterbrechung; Fehler können
                # später im Log dokumentiert werden.
                continue

    return plugins