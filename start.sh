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
  OVERALL_STATUS="WARN"
  OVERALL_ICON="⚠️"
  OVERALL_MESSAGE="Es gibt noch Probleme bei Paketen. Bitte die 3 Hilfeschritte unten ausführen."

  echo "[HILFE] Es gibt noch offene Paketprobleme."
  echo "[HILFE] 1) Internet prüfen"
  echo "[HILFE] 2) Erneut starten: bash start.sh"
  echo "[HILFE] 3) Log öffnen: $SETUP_LOG"
else
  OVERALL_STATUS="OK"
  OVERALL_ICON="✅"
  OVERALL_MESSAGE="Alle Paketprüfungen sind erfolgreich abgeschlossen."
fi

echo "[STATUS] $OVERALL_ICON Gesamtstatus Abhängigkeiten: $OVERALL_STATUS"
echo "[STATUS] $OVERALL_MESSAGE"

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
QUALITY_STATUS="OK"
QUALITY_ICON="✅"
QUALITY_HINT="Keine Aktion nötig."
if ! bash tools/run_quality_checks.sh > "$QUALITY_LOG" 2>&1; then
  QUALITY_STATUS="WARN"
  QUALITY_ICON="⚠️"
  QUALITY_HINT="Bitte zuerst die Qualitäts-Hilfe öffnen und dann erneut starten."
  echo "[WARN] Qualitätsprüfung meldet etwas. Tool versucht trotzdem zu starten."
  python3 tools/quality_gate_gui.py || true
fi

QUALITY_WARN_COUNT="$(rg -c "\[QUALITY\]\[WARN\]" "$QUALITY_LOG" 2>/dev/null || echo "0")"
QUALITY_INFO_COUNT="$(rg -c "\[QUALITY\]\[INFO\]" "$QUALITY_LOG" 2>/dev/null || echo "0")"
echo "[STATUS] $QUALITY_ICON Qualitäts-Gate: $QUALITY_STATUS"
echo "[STATUS] Hinweise: WARN=$QUALITY_WARN_COUNT, INFO=$QUALITY_INFO_COUNT"
echo "[HILFE] Nächster Schritt: $QUALITY_HINT"
echo "[HILFE] Log-Datei: $QUALITY_LOG"

# 5) Linux-Systembibliotheken prüfen (vor Smoke-Test)
check_and_repair_linux_lib() {
  local lib_name="$1"
  local apt_package="$2"
  local lib_label="$3"
  local lib_reason="$4"
  local dialog_title="$5"
  local install_now=0

  echo "[CHECK] Prüfe Linux-Systembibliothek: $lib_name"
  if ldconfig -p 2>/dev/null | grep -q "$lib_name"; then
    return 0
  fi

  echo "[WARN] $lib_name fehlt. Starte geführte Reparatur."
  echo "Fehlt: $lib_name" >> "$ERR_LOG"

  local repair_text="Was fehlt?
$lib_label: $lib_name

Warum wichtig?
$lib_reason

Was tun?
Klicken Sie auf 'Jetzt installieren'. Danach das Programm neu starten."

  if command -v zenity >/dev/null 2>&1; then
    if zenity --question \
      --title="$dialog_title" \
      --width=560 \
      --ok-label="Jetzt installieren" \
      --cancel-label="Abbrechen" \
      --text="$repair_text"; then
      install_now=1
    fi
  else
    echo "[HILFE] $repair_text"
    install_now=1
  fi

  if [ "$install_now" -eq 1 ]; then
    if command -v apt-get >/dev/null 2>&1; then
      echo "[SETUP] Installiere Systempaket ($apt_package)"
      if sudo apt-get update >>"$SETUP_LOG" 2>&1 && sudo apt-get install -y "$apt_package" >>"$SETUP_LOG" 2>&1; then
        echo "[OK] $apt_package wurde installiert."
      else
        echo "[WARN] Automatische Installation von $apt_package fehlgeschlagen." >>"$SETUP_LOG"
      fi
    else
      echo "[WARN] apt-get nicht verfügbar. $apt_package konnte nicht automatisch installiert werden." >>"$SETUP_LOG"
    fi
  fi

  if ldconfig -p 2>/dev/null | grep -q "$lib_name"; then
    return 0
  fi

  python3 tools/boot_error_gui.py "Was fehlt?
$lib_label: $lib_name

Warum wichtig?
$lib_reason

Was tun?
1) Falls möglich: sudo apt update && sudo apt install $apt_package
2) Danach neu starten: bash start.sh
3) Hilfe/Details: exports/setup_log.txt" "$dialog_title"
  exit 1
}

check_and_repair_linux_lib "libGL.so.1" "libgl1" "Grafik-Baustein" "Die grafische Oberfläche braucht diesen Baustein zum Anzeigen." "Grafik-Baustein fehlt"
check_and_repair_linux_lib "libEGL.so.1" "libegl1" "EGL-Grafik-Baustein" "Die grafische Oberfläche braucht diesen Baustein für die GPU-Verbindung (Grafikbeschleunigung)." "EGL-Baustein fehlt"
check_and_repair_linux_lib "libxkbcommon.so.0" "libxkbcommon0" "Tastatur-Baustein" "Die grafische Oberfläche braucht diesen Baustein für Tastatur und Eingabe." "Tastatur-Baustein fehlt"

# 6) Smoke-Test mit venv python
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

# 7) GUI starten
echo "[RUN] Starte GUI"
if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
  echo "[WARN] Keine grafische Sitzung erkannt (headless). GUI-Start wird übersprungen."
  python3 tools/boot_error_gui.py "Keine grafische Sitzung erkannt.

Was bedeutet das?
- Diese Umgebung hat aktuell kein Bildschirm-Backend (Display/Wayland).
- Darum kann die Oberfläche nicht geöffnet werden.

Nächste Schritte:
1) Im Desktop-Terminal neu ausführen: bash start.sh
2) Oder Display setzen (Beispiel): export DISPLAY=:0
3) Details im Protokoll lesen: exports/setup_log.txt" "GUI-Start im Headless-Modus"
  exit 0
fi

if ! "$VENV_PY" -m app.main >>"$SETUP_LOG" 2>&1; then
  echo "[ERROR] GUI konnte nicht gestartet werden"
  python3 tools/boot_error_gui.py "Die GUI konnte nicht gestartet werden.

Lösung:
- exports/setup_log.txt öffnen
- start.sh erneut ausführen

Details: exports/setup_log.txt" "GUI-Start"
  exit 1
fi
