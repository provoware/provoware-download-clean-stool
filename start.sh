#!/bin/bash
set -euo pipefail

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

mkdir -p logs exports
SETUP_LOG="exports/setup_log.txt"
ERR_LOG="exports/last_start_error.txt"
QUALITY_LOG="exports/quality_report.txt"

echo "[START] Downloads Organizer – Auto-Setup"
echo "=== START $(date -Is) ===" >> "$SETUP_LOG"

# 1) venv sicher erstellen
if [ ! -d "venv" ]; then
  echo "[SETUP] Erstelle virtuelle Umgebung (venv/)"
  if ! python3 -m venv venv >>"$SETUP_LOG" 2>&1; then
    echo "[ERROR] Konnte keine virtuelle Umgebung erstellen."
    python3 tools/boot_error_gui.py "Konnte keine virtuelle Umgebung erstellen.

Lösung:
- Prüfe, ob python3-venv installiert ist:
  sudo apt install python3-venv
- Danach start.sh erneut ausführen.

Details: exports/setup_log.txt" "Venv-Problem"
    exit 1
  fi
fi

VENV_PY="$PROJECT_DIR/venv/bin/python"
VENV_PIP="$PROJECT_DIR/venv/bin/pip"

echo "[SETUP] Aktualisiere pip (wenn möglich)"
"$VENV_PIP" install --upgrade pip >>"$SETUP_LOG" 2>&1 || true

# 2) Abhängigkeiten einzeln installieren + klare Status-Ausgabe
echo "[SETUP] Installiere Abhängigkeiten (vollautomatisch, mit Status)"
OFFLINE_WHEELS_DIR="$PROJECT_DIR/offline_wheels"
INSTALL_ERRORS=0
if [ -f requirements.txt ]; then
  while read -r pkg; do
    if [[ -z "$pkg" || "$pkg" =~ ^# ]]; then
      continue
    fi

    if [ -d "$OFFLINE_WHEELS_DIR" ]; then
      echo "[SETUP] Offline-Install für $pkg aus offline_wheels/ …"
      if "$VENV_PIP" install --no-index --find-links "$OFFLINE_WHEELS_DIR" "$pkg" >>"$SETUP_LOG" 2>&1; then
        continue
      fi
      echo "[WARN] Offline-Install fehlgeschlagen, versuche Online-Install: $pkg"
    else
      echo "[SETUP] Online-Install für $pkg …"
    fi

    if ! "$VENV_PIP" install --no-cache-dir "$pkg" >>"$SETUP_LOG" 2>&1; then
      echo "[WARN] Installation fehlgeschlagen: $pkg"
      echo "Install-Fehler: $pkg" >> "$ERR_LOG"
      INSTALL_ERRORS=$((INSTALL_ERRORS + 1))
    fi
  done < requirements.txt
fi

if [ "$INSTALL_ERRORS" -gt 0 ]; then
  echo "[WARN] $INSTALL_ERRORS Paket(e) konnten nicht installiert werden. Details: $ERR_LOG"
fi

# 3) Kritische Imports prüfen (ohne Crash)
echo "[CHECK] Prüfe kritische Module"
MISSING="$("$VENV_PY" - <<'PY'
import importlib
missing=[]
for mod in ("PySide6","PIL"):
    try:
        importlib.import_module(mod)
    except Exception:
        missing.append(mod)
print(",".join(missing))
PY
)"
if [ -n "$MISSING" ]; then
  MSG="Ein wichtiges Modul fehlt: $MISSING

Das Tool kann ohne diese Module nicht starten.

Automatische Schritte:
- Pip-Installation wurde versucht.

Wahrscheinliche Ursache:
- Keine Internetverbindung (pip kann nichts laden)
- Paketquelle blockiert

Schnelle Lösungen (Ubuntu/Kubuntu):
1) Internet aktivieren und start.sh erneut ausführen
2) Alternativ Systempakete installieren:
   sudo apt update
   sudo apt install python3-pyside6 python3-pil

Details: exports/setup_log.txt"
  python3 tools/boot_error_gui.py "$MSG" "Abhängigkeiten fehlen"
  exit 1
fi

# 4) Qualitätsprüfung (ohne den Nutzer zu verwirren)
echo "[CHECK] Führe Qualitätsprüfung aus"
if ! bash tools/run_quality_checks.sh > "$QUALITY_LOG" 2>&1; then
  echo "[WARN] Qualitätsprüfung meldet etwas. Tool versucht trotzdem zu starten."
  python3 tools/quality_gate_gui.py || true
fi

# 5) Smoke-Test mit venv python
echo "[CHECK] Starte Smoke-Test"
if ! "$VENV_PY" tools/smoke_test.py >>"$SETUP_LOG" 2>&1; then
  echo "[ERROR] Smoke-Test fehlgeschlagen"
  python3 tools/boot_error_gui.py "Smoke-Test fehlgeschlagen.

Lösung:
- start.sh erneut ausführen
- Wenn es wieder passiert: exports/setup_log.txt öffnen

Details: exports/setup_log.txt" "Smoke-Test"
  exit 1
fi

# 6) GUI starten
echo "[RUN] Starte GUI"
if ! "$VENV_PY" -m app.main >>"$SETUP_LOG" 2>&1; then
  echo "[ERROR] GUI konnte nicht gestartet werden"
  python3 tools/boot_error_gui.py "Die GUI konnte nicht gestartet werden.

Lösung:
- exports/setup_log.txt öffnen
- start.sh erneut ausführen

Details: exports/setup_log.txt" "GUI-Start"
  exit 1
fi
