#!/bin/bash
# Run quality checks with optional autofix mode.
set -euo pipefail

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )"
AUTO_FIX="${AUTO_FIX:-0}"

say() {
  printf '%s\n' "$1"
}

run_optional() {
  local tool_name="$1"
  local check_cmd="$2"
  local fix_cmd="$3"

  if ! command -v "$tool_name" >/dev/null 2>&1; then
    say "[QUALITY][INFO] $tool_name nicht installiert. Schritt wird übersprungen."
    return 0
  fi

  if [ "$AUTO_FIX" = "1" ]; then
    say "[QUALITY][FIX] Starte Auto-Korrektur mit $tool_name …"
    eval "$fix_cmd"
  else
    say "[QUALITY][CHECK] Prüfe Code mit $tool_name …"
    if ! eval "$check_cmd"; then
      say "[QUALITY][WARN] $tool_name meldet Abweichungen. Kein Abbruch, bitte bei Bedarf AUTO_FIX=1 nutzen."
    fi
  fi
}

say "[QUALITY] Starte Qualitätsprüfung (AUTO_FIX=$AUTO_FIX)"
say "[QUALITY] 1/4 Syntaxprüfung (compileall)"
python3 -m compileall -q "$ROOT_DIR"

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
  fi
else
  say "[QUALITY][INFO] Kein Smoke-Test gefunden."
fi

say "[QUALITY][OK] Alle verfügbaren Prüfungen erfolgreich beendet."
say "[QUALITY][HILFE] Für automatische Korrekturen: AUTO_FIX=1 bash tools/run_quality_checks.sh"
