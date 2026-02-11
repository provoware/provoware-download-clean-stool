#!/bin/bash
# Run quality checks with optional autofix mode.
set -euo pipefail

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )"
AUTO_FIX="${AUTO_FIX:-0}"
AUTO_FIX_ON_WARN="${AUTO_FIX_ON_WARN:-1}"
FAST_MODE="${FAST_MODE:-1}"
STATE_FILE="$ROOT_DIR/data/quality_state.json"
WARNINGS=0

say() {
  printf '%s\n' "$1"
}

run_optional() {
  local tool_name="$1"
  local check_cmd="$2"
  local fix_cmd="$3"
  local install_cmd="python3 -m pip install $tool_name"

  if ! command -v "$tool_name" >/dev/null 2>&1; then
    say "[QUALITY][WARN] $tool_name fehlt. Dieser Qualitäts-Check konnte nicht laufen."
    say "[QUALITY][HILFE] Nächster Schritt: $install_cmd"
    WARNINGS=$((WARNINGS + 1))
    return 0
  fi

  if [ "$AUTO_FIX" = "1" ]; then
    say "[QUALITY][FIX] Starte Auto-Korrektur mit $tool_name …"
    eval "$fix_cmd"
    if ! eval "$check_cmd"; then
      say "[QUALITY][WARN] $tool_name konnte nicht alle Abweichungen automatisch korrigieren."
      say "[QUALITY][HILFE] Nächster Schritt: Log lesen und die verbleibenden Meldungen einzeln beheben."
      WARNINGS=$((WARNINGS + 1))
    fi
  else
    say "[QUALITY][CHECK] Prüfe Code mit $tool_name …"
    if ! eval "$check_cmd"; then
      if [ "$AUTO_FIX_ON_WARN" = "1" ]; then
        say "[QUALITY][FIX] $tool_name meldet Abweichungen. Starte automatische Korrektur (AUTO_FIX_ON_WARN=1)."
        eval "$fix_cmd"
        if eval "$check_cmd"; then
          say "[QUALITY][OK] $tool_name hat die Abweichungen automatisch behoben."
        else
          say "[QUALITY][WARN] $tool_name meldet weiterhin Abweichungen nach Auto-Korrektur."
          say "[QUALITY][HILFE] Nächster Schritt: AUTO_FIX=1 wiederholen und verbleibende Meldungen manuell prüfen."
          WARNINGS=$((WARNINGS + 1))
        fi
      else
        say "[QUALITY][WARN] $tool_name meldet Abweichungen. Kein Abbruch, bitte bei Bedarf AUTO_FIX=1 nutzen."
        WARNINGS=$((WARNINGS + 1))
      fi
    fi
  fi
}

validate_required_json() {
  local file_path="$1"
  local required_keys_csv="$2"

  if [ ! -f "$file_path" ]; then
    say "[QUALITY][WARN] JSON-Datei fehlt: $file_path"
    say "[QUALITY][HILFE] Nächster Schritt: Datei wiederherstellen oder aus Git neu auschecken."
    WARNINGS=$((WARNINGS + 1))
    return 0
  fi

  if ! python3 - "$file_path" "$required_keys_csv" <<'PY'
import json
import sys
from pathlib import Path

file_path = Path(sys.argv[1])
required_keys = [key for key in sys.argv[2].split(",") if key]

try:
    payload = json.loads(file_path.read_text(encoding="utf-8"))
except Exception as exc:  # noqa: BLE001
    print(f"[QUALITY][WARN] JSON ungültig in {file_path}: {exc}")
    print("[QUALITY][HILFE] Nächster Schritt: JSON mit korrekten Klammern/Kommas speichern und den Check erneut starten.")
    raise SystemExit(1)

missing = [key for key in required_keys if key not in payload]
if missing:
    print(f"[QUALITY][WARN] Pflichtfelder fehlen in {file_path}: {', '.join(missing)}")
    print("[QUALITY][HILFE] Nächster Schritt: Fehlende Felder ergänzen und danach erneut prüfen.")
    raise SystemExit(1)

print(f"[QUALITY][OK] JSON-Struktur geprüft: {file_path}")
PY
  then
    WARNINGS=$((WARNINGS + 1))
  fi
}

calculate_signature() {
  (
    cd "$ROOT_DIR"
    if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      git ls-files app core tools start.sh requirements.txt | while read -r file; do
        [ -f "$file" ] && sha256sum "$file"
      done | sha256sum | cut -d' ' -f1
    else
      echo "no-git-signature"
    fi
  )
}

read_cached_signature() {
  python3 - "$STATE_FILE" <<'PY'
import json
import sys
from pathlib import Path

state = Path(sys.argv[1])
if not state.exists():
    print("", end="")
    raise SystemExit(0)

try:
    data = json.loads(state.read_text(encoding="utf-8"))
except Exception:
    print("", end="")
    raise SystemExit(0)

if data.get("status") == "ok":
    print(data.get("signature", ""), end="")
PY
}

write_state() {
  local status="$1"
  local signature="$2"
  mkdir -p "$(dirname "$STATE_FILE")"
  python3 - "$STATE_FILE" "$status" "$signature" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

state_file = Path(sys.argv[1])
status = sys.argv[2]
signature = sys.argv[3]
state_file.write_text(
    json.dumps(
        {
            "status": status,
            "signature": signature,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "hint": "FAST_MODE=0 erzwingt alle Checks."
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
PY
}

CURRENT_SIGNATURE="$(calculate_signature)"
CACHED_SIGNATURE="$(read_cached_signature)"

if [ "$FAST_MODE" = "1" ] && [ "$AUTO_FIX" = "0" ] && [ -n "$CACHED_SIGNATURE" ] && [ "$CURRENT_SIGNATURE" = "$CACHED_SIGNATURE" ]; then
  say "[QUALITY][FAST] Keine relevanten Dateiänderungen seit dem letzten erfolgreichen Lauf erkannt."
  say "[QUALITY][FAST] Checks werden übersprungen, damit du nicht unnötig dieselben Tests wiederholst."
  say "[QUALITY][HILFE] Für kompletten Lauf: FAST_MODE=0 bash tools/run_quality_checks.sh"
  exit 0
fi

say "[QUALITY] Starte Qualitätsprüfung (AUTO_FIX=$AUTO_FIX)"
say "[QUALITY] Automatische Korrektur bei Warnungen: AUTO_FIX_ON_WARN=$AUTO_FIX_ON_WARN"
say "[QUALITY] 1/4 Syntaxprüfung (compileall)"
python3 -m compileall -q \
  "$ROOT_DIR/app" \
  "$ROOT_DIR/core" \
  "$ROOT_DIR/tools" \
  "$ROOT_DIR/start.sh"

say "[QUALITY] 2/4 Formatprüfung"
run_optional "black" "black --check \"$ROOT_DIR/app\" \"$ROOT_DIR/core\" \"$ROOT_DIR/tools\"" "black \"$ROOT_DIR/app\" \"$ROOT_DIR/core\" \"$ROOT_DIR/tools\""
run_optional "isort" "isort --check-only \"$ROOT_DIR/app\" \"$ROOT_DIR/core\" \"$ROOT_DIR/tools\"" "isort \"$ROOT_DIR/app\" \"$ROOT_DIR/core\" \"$ROOT_DIR/tools\""

say "[QUALITY] 3/4 Lintprüfung"
run_optional "ruff" "ruff check \"$ROOT_DIR/app\" \"$ROOT_DIR/core\" \"$ROOT_DIR/tools\"" "ruff check --fix \"$ROOT_DIR/app\" \"$ROOT_DIR/core\" \"$ROOT_DIR/tools\""

say "[QUALITY] 4/5 Smoke-Test"
if [ -f "$ROOT_DIR/tools/smoke_test.py" ]; then
  if ! python3 "$ROOT_DIR/tools/smoke_test.py"; then
    say "[QUALITY][WARN] Smoke-Test fehlgeschlagen (oft fehlende Linux-GUI-Bibliotheken im Headless-System)."
    say "[QUALITY][HILFE] Nächster Schritt: bash start.sh für automatische Reparaturhilfe."
    WARNINGS=$((WARNINGS + 1))
  fi
else
  say "[QUALITY][INFO] Kein Smoke-Test gefunden."
fi


say "[QUALITY] 5/5 A11y-Theme-Check"
if [ -f "$ROOT_DIR/tools/a11y_theme_check.py" ]; then
  if ! python3 "$ROOT_DIR/tools/a11y_theme_check.py"; then
    say "[QUALITY][WARN] A11y-Theme-Check meldet Probleme bei Kontrast oder Fokusregeln."
    say "[QUALITY][HILFE] Nächster Schritt: app/main.py Theme-Farben und :focus-Regeln prüfen, danach Quality-Check erneut starten."
    WARNINGS=$((WARNINGS + 1))
  fi
else
  say "[QUALITY][WARN] A11y-Theme-Check fehlt (tools/a11y_theme_check.py)."
  say "[QUALITY][HILFE] Nächster Schritt: Datei wiederherstellen oder aus Versionsverwaltung holen."
  WARNINGS=$((WARNINGS + 1))
fi

say "[QUALITY] 6/6 JSON-Struktur-Check"
validate_required_json "$ROOT_DIR/data/settings.json" "theme,large_text,download_dir,presets,filters,duplicates_mode"
validate_required_json "$ROOT_DIR/data/standards_manifest.json" "manifest_version,language_policy,accessibility,quality_gates,validation_policy,structure_policy"
validate_required_json "$ROOT_DIR/data/presets/standard.json" "name,description,filters,duplicates_mode,confirm_threshold"
validate_required_json "$ROOT_DIR/data/presets/power.json" "name,description,filters,duplicates_mode,confirm_threshold"
validate_required_json "$ROOT_DIR/data/presets/senior.json" "name,description,filters,duplicates_mode,confirm_threshold"

if [ "$WARNINGS" -eq 0 ]; then
  write_state "ok" "$CURRENT_SIGNATURE"
else
  write_state "warning" "$CURRENT_SIGNATURE"
fi

if [ "$WARNINGS" -eq 0 ]; then
  say "[QUALITY][OK] Alle verfügbaren Prüfungen erfolgreich beendet."
else
  say "[QUALITY][WARN] Qualitätslauf beendet mit $WARNINGS Warnung(en)."
  say "[QUALITY][HILFE] Nächster Schritt: AUTO_FIX=1 bash tools/run_quality_checks.sh und verbleibende Warnungen einzeln beheben."
fi
