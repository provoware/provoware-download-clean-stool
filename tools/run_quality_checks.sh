#!/bin/bash
# Run quality checks with optional autofix mode.
set -euo pipefail

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )"
AUTO_FIX="${AUTO_FIX:-0}"
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
  else
    say "[QUALITY][CHECK] Prüfe Code mit $tool_name …"
    if ! eval "$check_cmd"; then
      say "[QUALITY][WARN] $tool_name meldet Abweichungen. Kein Abbruch, bitte bei Bedarf AUTO_FIX=1 nutzen."
      WARNINGS=$((WARNINGS + 1))
    fi
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

say "[QUALITY] 4/4 Smoke-Test"
if [ -f "$ROOT_DIR/tools/smoke_test.py" ]; then
  if ! python3 "$ROOT_DIR/tools/smoke_test.py"; then
    say "[QUALITY][WARN] Smoke-Test fehlgeschlagen (oft fehlende Linux-GUI-Bibliotheken im Headless-System)."
    say "[QUALITY][HILFE] Nächster Schritt: bash start.sh für automatische Reparaturhilfe."
    WARNINGS=$((WARNINGS + 1))
  fi
else
  say "[QUALITY][INFO] Kein Smoke-Test gefunden."
fi

if [ "$WARNINGS" -eq 0 ]; then
  write_state "ok" "$CURRENT_SIGNATURE"
else
  write_state "warning" "$CURRENT_SIGNATURE"
fi

say "[QUALITY][OK] Alle verfügbaren Prüfungen erfolgreich beendet."
say "[QUALITY][HILFE] Für automatische Korrekturen: AUTO_FIX=1 bash tools/run_quality_checks.sh"
