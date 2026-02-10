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

# 2) Abhängigkeiten robust installieren + Konflikte automatisch prüfen
echo "[SETUP] Installiere Abhängigkeiten (vollautomatisch, mit Status und Konfliktprüfung)"
OFFLINE_WHEELS_DIR="$PROJECT_DIR/offline_wheels"
REQ_SANITIZED="$PROJECT_DIR/exports/requirements.sanitized.txt"
> "$REQ_SANITIZED"
INSTALL_ERRORS=0
INSTALL_OK=0
INSTALL_SKIPPED=0
INSTALL_SOURCE_OFFLINE=0
INSTALL_SOURCE_ONLINE=0
INSTALL_CONFLICTS=0

if [ -f requirements.txt ]; then
  while IFS= read -r raw_pkg || [ -n "$raw_pkg" ]; do
    pkg="$(printf '%s' "$raw_pkg" | sed -e 's/#.*//' -e 's/\r$//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    if [[ -z "$pkg" || "$pkg" == -* ]]; then
      INSTALL_SKIPPED=$((INSTALL_SKIPPED + 1))
      continue
    fi
    printf '%s\n' "$pkg" >> "$REQ_SANITIZED"

    if [ -d "$OFFLINE_WHEELS_DIR" ]; then
      echo "[SETUP] Offline-Install für $pkg aus offline_wheels/ …"
      if "$VENV_PIP" install --no-index --find-links "$OFFLINE_WHEELS_DIR" "$pkg" >>"$SETUP_LOG" 2>&1; then
        echo "[OK] Installiert: $pkg (offline)"
        INSTALL_OK=$((INSTALL_OK + 1))
        INSTALL_SOURCE_OFFLINE=$((INSTALL_SOURCE_OFFLINE + 1))
        continue
      fi
      echo "[WARN] Offline-Install fehlgeschlagen, versuche Online-Install: $pkg"
    else
      echo "[SETUP] Online-Install für $pkg …"
    fi

    if "$VENV_PIP" install --no-cache-dir "$pkg" >>"$SETUP_LOG" 2>&1; then
      echo "[OK] Installiert: $pkg"
      INSTALL_OK=$((INSTALL_OK + 1))
      INSTALL_SOURCE_ONLINE=$((INSTALL_SOURCE_ONLINE + 1))
    else
      echo "[WARN] Installation fehlgeschlagen: $pkg"
      echo "Install-Fehler: $pkg" >> "$ERR_LOG"
      INSTALL_ERRORS=$((INSTALL_ERRORS + 1))
    fi
  done < requirements.txt
fi

if ! "$VENV_PIP" check >>"$SETUP_LOG" 2>&1; then
  INSTALL_CONFLICTS=1
  echo "[WARN] Versionskonflikt erkannt. Starte automatische Reparatur (Upgrade nach requirements)."
  if [ -s "$REQ_SANITIZED" ]; then
    if [ -d "$OFFLINE_WHEELS_DIR" ]; then
      "$VENV_PIP" install --upgrade --no-index --find-links "$OFFLINE_WHEELS_DIR" -r "$REQ_SANITIZED" >>"$SETUP_LOG" 2>&1 || true
    fi
    "$VENV_PIP" install --upgrade --upgrade-strategy eager --no-cache-dir -r "$REQ_SANITIZED" >>"$SETUP_LOG" 2>&1 || true
  fi
  if "$VENV_PIP" check >>"$SETUP_LOG" 2>&1; then
    INSTALL_CONFLICTS=0
    echo "[OK] Konflikte wurden automatisch behoben."
  else
    echo "[WARN] Konflikte bestehen weiter. Bitte Log prüfen: $SETUP_LOG"
  fi
fi

echo "[SETUP] Zusammenfassung Abhängigkeitsprüfung:"
echo "[SETUP] - Erfolgreich installiert: $INSTALL_OK"
echo "[SETUP] - Übersprungen (leer/Kommentar/Option): $INSTALL_SKIPPED"
echo "[SETUP] - Fehler: $INSTALL_ERRORS"
echo "[SETUP] - Quelle offline_wheels: $INSTALL_SOURCE_OFFLINE"
echo "[SETUP] - Quelle online/pip: $INSTALL_SOURCE_ONLINE"
echo "[SETUP] - Offene Versionskonflikte: $INSTALL_CONFLICTS"

if [ "$INSTALL_ERRORS" -gt 0 ] || [ "$INSTALL_CONFLICTS" -gt 0 ]; then
  echo "[HILFE] Es gibt noch offene Paketprobleme."
  echo "[HILFE] 1) Internet prüfen"
  echo "[HILFE] 2) Erneut starten: bash start.sh"
  echo "[HILFE] 3) Log öffnen: $SETUP_LOG"
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
  echo "[CHECK] Fehlende Module erkannt: $MISSING"
  echo "[SETUP] Versuche automatische Reparatur über apt (Ubuntu/Kubuntu)"
  APT_PACKAGES=()
  [[ ",$MISSING," == *",PySide6,"* ]] && APT_PACKAGES+=("python3-pyside6")
  [[ ",$MISSING," == *",PIL,"* ]] && APT_PACKAGES+=("python3-pil")

  if command -v apt-get >/dev/null 2>&1 && [ "${#APT_PACKAGES[@]}" -gt 0 ]; then
    echo "[SETUP] Installiere Systempakete: ${APT_PACKAGES[*]}"
    if sudo apt-get update >>"$SETUP_LOG" 2>&1 && sudo apt-get install -y "${APT_PACKAGES[@]}" >>"$SETUP_LOG" 2>&1; then
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
    else
      echo "[WARN] apt-Autoreparatur fehlgeschlagen" >>"$SETUP_LOG"
    fi
  fi

  if [ -n "$MISSING" ]; then
    MSG="Wichtige Bausteine fehlen noch: $MISSING

Das Programm braucht diese Bausteine zum Start.

Was schon automatisch versucht wurde:
- Installation mit pip
- Installation mit apt (Ubuntu/Kubuntu), wenn möglich

Bitte jetzt so vorgehen:
1) Internet prüfen
2) Dann erneut starten: bash start.sh
3) Wenn es weiter fehlschlägt, diese Befehle ausführen:
   sudo apt update
   sudo apt install python3-pyside6 python3-pil

Hilfe-Datei: exports/setup_log.txt"
    python3 tools/boot_error_gui.py "$MSG" "Abhängigkeiten fehlen"
    exit 1
  fi
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
