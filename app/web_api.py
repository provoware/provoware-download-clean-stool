"""Web API skeleton for Provoware Clean Tool 2026.

Dieses Modul stellt einen minimalen FastAPI‑Server bereit. Es definiert zwei
Endpunkte, die in künftigen Iterationen ausgebaut werden können:

* ``/status`` – gibt eine einfache Statusmeldung zurück, ob der Dienst läuft.
* ``/dry_run`` – simuliert einen Aufräumlauf (derzeit nur Plausibilitätsprüfung
  des Pfades). In späteren Versionen sollen hier die Scan‑ und Plan‑Funktionen
  aus dem Kernmodul verwendet werden.

Die API ist bewusst laienfreundlich gestaltet: Fehlermeldungen sind klar
formuliert und geben nächste Schritte vor. Für den produktiven Einsatz
empfiehlt sich, diese Schnittstelle hinter einem Authentifizierungsfilter zu
platzieren.

Zum Starten des Servers kann beispielsweise ``uvicorn app.web_api:app --reload``
verwendet werden.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from fastapi import FastAPI

app = FastAPI(title="Provoware Clean Tool 2026 API")


@app.get("/status", summary="Status abrufen")
def get_status() -> Dict[str, str]:
    """Gibt den aktuellen Systemstatus zurück.

    Returns
    -------
    Dict[str, str]
        Ein Wörterbuch mit einem Statusfeld und einer laienfreundlichen
        Nachricht. Der Status ist "bereit", sobald der Dienst läuft.
    """
    return {"status": "bereit", "message": "Der Dienst läuft und wartet auf Anfragen."}


@app.get("/dry_run", summary="Trockenlauf durchführen")
def dry_run(path: str | None = None) -> Dict[str, str]:
    """Simuliert einen Aufräumlauf und gibt eine Vorschau zurück.

    Parameter
    ---------
    path: str, optional
        Pfad zum zu scannenden Ordner. Ist kein Pfad angegeben oder existiert
        der Pfad nicht, liefert die Funktion eine klare Fehlermeldung mit
        nächstem Schritt.

    Returns
    -------
    Dict[str, str]
        Ein Wörterbuch mit Status und Nachricht. Im Erfolgsfall wird ein
        Platzhaltertext für den noch nicht implementierten Trockenlauf
        zurückgegeben.
    """
    if not path:
        return {
            "status": "fehler",
            "message": "Pfad darf nicht leer sein. Bitte geben Sie einen gültigen Ordner an.",
        }
    p = Path(path)
    if not p.exists():
        return {
            "status": "fehler",
            "message": f"Pfad {path} existiert nicht. Bitte prüfen Sie die Eingabe.",
        }
    # Platzhalter: In späteren Versionen wird hier der Scanner/Planner genutzt
    return {
        "status": "ok",
        "message": f"Trockenlauf für {path} ist noch nicht implementiert, folgt in späteren Versionen.",
    }
