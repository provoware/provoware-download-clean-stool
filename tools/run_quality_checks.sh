#!/bin/bash
# Run quality checks with optional autofix mode.
set -euo pipefail

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )"
AUTO_FIX="${AUTO_FIX:-0}"
AUTO_FIX_ON_WARN="${AUTO_FIX_ON_WARN:-auto}"
FAST_MODE="${FAST_MODE:-1}"
AUTO_INSTALL_TOOLS="${AUTO_INSTALL_TOOLS:-1}"
STRICT_SMOKE="${STRICT_SMOKE:-0}"
STATE_FILE="$ROOT_DIR/data/quality_state.json"
WARNINGS=0
TOTAL_STEPS=12

say() {
  printf '%s\n' "$1"
}

announce_quality_step() {
  # Gibt einheitliche, validierte Schrittzeilen für den Qualitätslauf aus.
  # Input: Schrittindex und kurzer Titel. Output: [QUALITY] X/Y Titel.
  local raw_step="${1:-0}"
  local step_title="${2:-Unbenannter Schritt}"
  if ! [[ "$raw_step" =~ ^[0-9]+$ ]] || [ "$raw_step" -lt 1 ] || [ "$raw_step" -gt "$TOTAL_STEPS" ]; then
    say "[QUALITY][WARN] Ungültiger Schrittindex '$raw_step'. Verwende sicheren Fallback 1/$TOTAL_STEPS."
    raw_step=1
  fi
  say "[QUALITY] ${raw_step}/${TOTAL_STEPS} ${step_title}"
}

resolve_quality_python() {
  # Liefert den besten Python-Interpreter für automatische Tool-Installation.
  # Priorität: venv-Python im Projekt, danach System-python3.
  local venv_python="$ROOT_DIR/venv/bin/python"
  if [ -x "$venv_python" ]; then
    printf '%s' "$venv_python"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  printf '%s' ""
  return 1
}

normalize_binary_flag() {
  # Akzeptiert nur 0 oder 1 für Konfigurations-Flags.
  # Bei ungültigem Wert folgt ein sicherer Fallback auf 1 inkl. Hilfehinweis.
  local raw_value="${1:-1}"
  local label="${2:-FLAG}"
  if [ "$raw_value" = "0" ] || [ "$raw_value" = "1" ]; then
    printf '%s' "$raw_value"
    return 0
  fi
  say "[QUALITY][WARN] $label hat einen ungültigen Wert: '$raw_value'. Erlaubt sind nur 0 oder 1."
  say "[QUALITY][HILFE] Nächster Schritt: $label=1 bash tools/run_quality_checks.sh"
  WARNINGS=$((WARNINGS + 1))
  printf '%s' "1"
  return 1
}

resolve_auto_fix_on_warn_flag() {
  # Erlaubt 0/1/auto. "auto" verhindert stilles Umformatieren in Standardläufen.
  # Output: 0 oder 1, immer mit klarer Rückmeldung für den nächsten Schritt.
  local raw_value="${1:-auto}"

  if [ "$raw_value" = "0" ] || [ "$raw_value" = "1" ]; then
    printf '%s' "$raw_value"
    return 0
  fi

  if [ "$raw_value" != "auto" ]; then
    say "[QUALITY][WARN] AUTO_FIX_ON_WARN hat einen ungültigen Wert: '$raw_value'. Erlaubt sind 0, 1 oder auto."
    say "[QUALITY][HILFE] Nächster Schritt: AUTO_FIX_ON_WARN=0 bash tools/run_quality_checks.sh"
    WARNINGS=$((WARNINGS + 1))
  fi

  if [ "$AUTO_FIX" = "1" ]; then
    printf '%s' "1"
    return 0
  fi

  if [ -n "${CI:-}" ]; then
    printf '%s' "0"
    return 0
  fi

  printf '%s' "0"
  return 0
}

print_quality_summary_for_humans() {
  # Zeigt eine kurze, laienfreundliche Abschlusshilfe in klarer Reihenfolge.
  local warnings_count="${1:-0}"
  say "[QUALITY][ÜBERSICHT] ===== Kurzfassung in einfacher Sprache ====="
  say "[QUALITY][ÜBERSICHT] Gefundene Warnungen: $warnings_count"
  if [ "$warnings_count" -eq 0 ]; then
    say "[QUALITY][ÜBERSICHT] Alles grün. Sie können direkt mit dem Tool arbeiten."
    say "[QUALITY][HILFE] Optionaler Kontrolllauf: FAST_MODE=0 bash tools/run_quality_checks.sh"
    return 0
  fi
  say "[QUALITY][ÜBERSICHT] Bitte führen Sie diese Reihenfolge aus:"
  say "[QUALITY][HILFE] 1) Auto-Korrektur starten: AUTO_FIX=1 bash tools/run_quality_checks.sh"
  say "[QUALITY][HILFE] 2) Vollprüfung starten: FAST_MODE=0 bash tools/run_quality_checks.sh"
  say "[QUALITY][HILFE] 3) Danach Startprüfung laufen lassen: bash start.sh"
}

QUALITY_PYTHON="$(resolve_quality_python)"
if [ -z "$QUALITY_PYTHON" ]; then
  say "[QUALITY][WARN] Kein Python-Interpreter verfügbar. Auto-Installation von Tools ist nicht möglich."
  say "[QUALITY][HILFE] Nächster Schritt: python3 installieren und dann erneut starten."
  WARNINGS=$((WARNINGS + 1))
fi

AUTO_FIX="$(normalize_binary_flag "$AUTO_FIX" "AUTO_FIX")"
AUTO_FIX_ON_WARN="$(resolve_auto_fix_on_warn_flag "$AUTO_FIX_ON_WARN")"
if [ "$AUTO_FIX" = "1" ]; then
  say "[QUALITY][INFO] AUTO_FIX=1 aktiv: AUTO_FIX_ON_WARN ist auf 1 gesetzt."
elif [ -n "${CI:-}" ]; then
  say "[QUALITY][INFO] CI-Umgebung erkannt: AUTO_FIX_ON_WARN=0, damit keine stillen Codeänderungen entstehen."
else
  say "[QUALITY][INFO] Standardlauf ohne AUTO_FIX: AUTO_FIX_ON_WARN=0 (nur prüfen, keine stillen Änderungen)."
  say "[QUALITY][HILFE] Optional: AUTO_FIX_ON_WARN=1 bash tools/run_quality_checks.sh für automatische Korrektur bei Warnungen."
fi
FAST_MODE="$(normalize_binary_flag "$FAST_MODE" "FAST_MODE")"
AUTO_INSTALL_TOOLS="$(normalize_binary_flag "$AUTO_INSTALL_TOOLS" "AUTO_INSTALL_TOOLS")"
STRICT_SMOKE="$(normalize_binary_flag "$STRICT_SMOKE" "STRICT_SMOKE")"

check_shared_library_exists() {
  # Prüft eine einzelne Bibliothek robust und liefert 0 (gefunden) oder 1 (fehlt).
  # Input: Bibliotheksname und optionale Fallback-Pfade.
  local lib_name="${1:-}"
  local fallback_a="${2:-}"
  local fallback_b="${3:-}"

  if [ -z "$lib_name" ]; then
    say "[QUALITY][WARN] Interner Check-Fehler: Bibliotheksname fehlt."
    return 1
  fi

  if command -v ldconfig >/dev/null 2>&1 && ldconfig -p 2>/dev/null | grep -q "$lib_name"; then
    return 0
  fi

  if [ -n "$fallback_a" ] && [ -e "$fallback_a" ]; then
    return 0
  fi

  if [ -n "$fallback_b" ] && [ -e "$fallback_b" ]; then
    return 0
  fi

  return 1
}

check_gui_smoke_prerequisites() {
  # Prüft minimale GUI-Voraussetzungen vor dem Smoke-Test.
  # Output: 0 wenn alles bereit ist; sonst 1 + verständlicher Hinweis mit Next Step.
  local missing_items=()

  if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
    missing_items+=("Display/Wayland-Sitzung")
  fi
  if ! check_shared_library_exists "libGL.so.1" "/usr/lib/x86_64-linux-gnu/libGL.so.1" "/lib/x86_64-linux-gnu/libGL.so.1"; then
    missing_items+=("libGL.so.1")
  fi
  if ! check_shared_library_exists "libEGL.so.1" "/usr/lib/x86_64-linux-gnu/libEGL.so.1" "/lib/x86_64-linux-gnu/libEGL.so.1"; then
    missing_items+=("libEGL.so.1")
  fi
  if ! check_shared_library_exists "libxkbcommon.so.0" "/usr/lib/x86_64-linux-gnu/libxkbcommon.so.0" "/lib/x86_64-linux-gnu/libxkbcommon.so.0"; then
    missing_items+=("libxkbcommon.so.0")
  fi

  if [ "${#missing_items[@]}" -eq 0 ]; then
    say "[QUALITY][OK] Smoke-Voraussetzungen vorhanden (Display/Wayland + Basis-Bibliotheken)."
    return 0
  fi

  say "[QUALITY][WARN] Smoke-Voraussetzungen fehlen: ${missing_items[*]}"
  say "[QUALITY][HILFE] Nächster Schritt 1 (Ubuntu/Debian): sudo apt update && sudo apt install -y libgl1 libegl1 libxkbcommon0"
  say "[QUALITY][HILFE] Nächster Schritt 2 (Fedora): sudo dnf install -y mesa-libGL mesa-libEGL libxkbcommon"
  say "[QUALITY][HILFE] Nächster Schritt 3: Danach erneut prüfen: STRICT_SMOKE=1 bash tools/run_quality_checks.sh"
  return 1
}

run_optional() {
  local tool_name="$1"
  local check_cmd="$2"
  local fix_cmd="$3"
  local install_cmd="$QUALITY_PYTHON -m pip install $tool_name"

  if ! command -v "$tool_name" >/dev/null 2>&1; then
    say "[QUALITY][WARN] $tool_name fehlt. Dieser Qualitäts-Check konnte nicht laufen."
    if [ "$AUTO_INSTALL_TOOLS" = "1" ]; then
      say "[QUALITY][FIX] Versuche fehlendes Werkzeug automatisch zu installieren: $tool_name"
      if eval "$install_cmd" >/dev/null 2>&1 && command -v "$tool_name" >/dev/null 2>&1; then
        say "[QUALITY][OK] $tool_name wurde automatisch installiert."
      else
        say "[QUALITY][HILFE] Auto-Installation nicht möglich. Nächster Schritt: $install_cmd"
        WARNINGS=$((WARNINGS + 1))
        return 0
      fi
    else
      say "[QUALITY][HILFE] Nächster Schritt: $install_cmd"
      WARNINGS=$((WARNINGS + 1))
      return 0
    fi
  fi

  local fix_applied=0

  if [ "$AUTO_FIX" = "1" ]; then
    say "[QUALITY][FIX] Starte Auto-Korrektur mit $tool_name …"
    eval "$fix_cmd"
    fix_applied=1
    if ! eval "$check_cmd"; then
      say "[QUALITY][WARN] $tool_name konnte nicht alle Abweichungen automatisch korrigieren."
      say "[QUALITY][HILFE] Nächster Schritt: Log lesen und die verbleibenden Meldungen einzeln beheben."
      WARNINGS=$((WARNINGS + 1))
    else
      say "[QUALITY][OK] $tool_name Auto-Korrektur abgeschlossen."
    fi
  else
    say "[QUALITY][CHECK] Prüfe Code mit $tool_name …"
    if ! eval "$check_cmd"; then
      if [ "$AUTO_FIX_ON_WARN" = "1" ]; then
        say "[QUALITY][FIX] $tool_name meldet Abweichungen. Starte automatische Korrektur (AUTO_FIX_ON_WARN=1)."
        eval "$fix_cmd"
        fix_applied=1
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
    else
      say "[QUALITY][OK] $tool_name Prüfung bestanden."
    fi
  fi

  if [ "$fix_applied" = "1" ]; then
    say "[QUALITY][HILFE] Prüfung der Änderungen: git diff --stat"
    say "[QUALITY][HILFE] Rückgängig machen (falls nötig): git restore <datei>"
  fi
}

validate_version_registry() {
  local registry_file="$ROOT_DIR/data/version_registry.json"
  if [ ! -f "$registry_file" ]; then
    say "[QUALITY][WARN] Versions-Registry fehlt: data/version_registry.json"
    say "[QUALITY][HILFE] Nächster Schritt: Datei anlegen und für jede geänderte Datei eine Versionsnummer eintragen."
    WARNINGS=$((WARNINGS + 1))
    return 0
  fi

  if ! python3 - "$registry_file" <<'PYREG'
import json
import re
import sys
from pathlib import Path

registry_path = Path(sys.argv[1])
pattern = re.compile(r"^\d{4}\.\d{2}\.\d{2}(?:\.\d+)?$")

try:
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
except Exception as exc:  # noqa: BLE001
    print(f"[QUALITY][WARN] Versions-Registry ist kein gültiges JSON: {exc}")
    print("[QUALITY][HILFE] Nächster Schritt: JSON-Syntax in data/version_registry.json korrigieren.")
    raise SystemExit(1)

global_version = payload.get("global_version")
if not isinstance(global_version, str) or not pattern.fullmatch(global_version):
    print("[QUALITY][WARN] global_version fehlt oder hat ein ungültiges Format (erwartet YYYY.MM.DD).")
    print("[QUALITY][HILFE] Nächster Schritt: global_version auf das Iterationsdatum setzen, z. B. 2026.02.12.")
    raise SystemExit(1)

files = payload.get("files")
if not isinstance(files, dict) or not files:
    print("[QUALITY][WARN] 'files' fehlt oder ist leer in data/version_registry.json.")
    print("[QUALITY][HILFE] Nächster Schritt: Für jede geänderte Datei einen Eintrag ergänzen.")
    raise SystemExit(1)

invalid = []
for path, version in files.items():
    if not isinstance(path, str) or not path.strip():
        invalid.append("<leerer-pfad>")
        continue
    if not isinstance(version, str) or not version.strip():
        invalid.append(path)

if invalid:
    print("[QUALITY][WARN] Versionseinträge unvollständig für: " + ", ".join(invalid))
    print("[QUALITY][HILFE] Nächster Schritt: Leere Pfade/Versionen in der Registry korrigieren.")
    raise SystemExit(1)

print("[QUALITY][OK] Versions-Registry geprüft: Format und Pflichtfelder sind gültig.")
PYREG
  then
    WARNINGS=$((WARNINGS + 1))
  fi
}

validate_required_json() {
  local file_path="$1"
  local required_keys_csv="$2"
  local required_types_csv="${3:-}"
  local required_ranges_csv="${4:-}"

  if [ ! -f "$file_path" ]; then
    say "[QUALITY][WARN] JSON-Datei fehlt: $file_path"
    say "[QUALITY][HILFE] Nächster Schritt: Datei wiederherstellen oder aus Git neu auschecken."
    WARNINGS=$((WARNINGS + 1))
    return 0
  fi

  if ! python3 - "$file_path" "$required_keys_csv" "$required_types_csv" "$required_ranges_csv" <<'PY'
import json
import sys
from pathlib import Path

file_path = Path(sys.argv[1])
required_keys = [key for key in sys.argv[2].split(",") if key]
required_types_raw = [entry for entry in sys.argv[3].split(",") if entry]
required_ranges_raw = [entry for entry in sys.argv[4].split(",") if entry]
required_types: dict[str, str] = {}
required_ranges: dict[str, tuple[float | None, float | None]] = {}
for entry in required_types_raw:
    if ":" not in entry:
        continue
    key, expected = entry.split(":", 1)
    required_types[key.strip()] = expected.strip()

for entry in required_ranges_raw:
    parts = [part.strip() for part in entry.split(":", 2)]
    if len(parts) != 3:
        continue
    key, minimum_raw, maximum_raw = parts

    def parse_boundary(raw_value: str) -> float | None:
        if raw_value == "*":
            return None
        try:
            return float(raw_value)
        except ValueError:
            return None

    required_ranges[key] = (parse_boundary(minimum_raw), parse_boundary(maximum_raw))


def is_type_ok(value: object, expected: str) -> bool:
    if expected == "str":
        return isinstance(value, str)
    if expected == "bool":
        return isinstance(value, bool)
    if expected == "dict":
        return isinstance(value, dict)
    if expected == "list":
        return isinstance(value, list)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return value is not None

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

invalid_types = []
for key, expected in required_types.items():
    if key in payload and not is_type_ok(payload[key], expected):
        invalid_types.append(f"{key} (erwartet: {expected})")

if invalid_types:
    print(f"[QUALITY][WARN] Inhalt unvollständig oder Typ passt nicht in {file_path}: {', '.join(invalid_types)}")
    print("[QUALITY][HILFE] Nächster Schritt: Werte in einfacher Form korrigieren (z. B. Text statt leerem Wert oder true/false bei Schaltern) und erneut prüfen.")
    raise SystemExit(1)

range_issues = []
for key, (minimum, maximum) in required_ranges.items():
    if key not in payload:
        continue
    value = payload[key]
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        range_issues.append(f"{key} (keine Zahl)")
        continue
    if minimum is not None and value < minimum:
        range_issues.append(f"{key} (< {minimum:g})")
    if maximum is not None and value > maximum:
        range_issues.append(f"{key} (> {maximum:g})")

if range_issues:
    print(f"[QUALITY][WARN] Zahlenbereich verletzt in {file_path}: {', '.join(range_issues)}")
    print("[QUALITY][HILFE] Nächster Schritt: Beispiel-Korrektur `confirm_threshold`: 20 (erlaubt 1 bis 100), dann Check erneut starten.")
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
      git ls-files app core tools data/design_reference_domotic_assistant.json start.sh requirements.txt | while read -r file; do
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
say "[QUALITY] Auto-Installation fehlender Werkzeuge: AUTO_INSTALL_TOOLS=$AUTO_INSTALL_TOOLS"
announce_quality_step 1 "Syntaxprüfung (compileall)"
python3 -m compileall -q \
  "$ROOT_DIR/app" \
  "$ROOT_DIR/core" \
  "$ROOT_DIR/tools" \
  "$ROOT_DIR/start.sh"

announce_quality_step 2 "Formatprüfung"
run_optional "black" "black --check \"$ROOT_DIR/app\" \"$ROOT_DIR/core\" \"$ROOT_DIR/tools\"" "black \"$ROOT_DIR/app\" \"$ROOT_DIR/core\" \"$ROOT_DIR/tools\""
run_optional "isort" "isort --check-only \"$ROOT_DIR/app\" \"$ROOT_DIR/core\" \"$ROOT_DIR/tools\"" "isort \"$ROOT_DIR/app\" \"$ROOT_DIR/core\" \"$ROOT_DIR/tools\""

announce_quality_step 3 "Lintprüfung"
run_optional "ruff" "ruff check \"$ROOT_DIR/app\" \"$ROOT_DIR/core\" \"$ROOT_DIR/tools\"" "ruff check --fix \"$ROOT_DIR/app\" \"$ROOT_DIR/core\" \"$ROOT_DIR/tools\""

announce_quality_step 4 "Smoke-Test"
if [ -f "$ROOT_DIR/tools/smoke_test.py" ]; then
  smoke_rc=0
  if ! check_gui_smoke_prerequisites; then
    if [ "$STRICT_SMOKE" = "1" ]; then
      WARNINGS=$((WARNINGS + 1))
      say "[QUALITY][WARN] STRICT_SMOKE=1: Fehlende Voraussetzungen gelten als Qualitätswarnung mit hoher Priorität."
    else
      say "[QUALITY][INFO] Smoke-Test wurde in dieser Umgebung übersprungen (kein harter Fehler)."
    fi
  else
    if ! python3 "$ROOT_DIR/tools/smoke_test.py"; then
      smoke_rc=$?
    fi
    if [ "$smoke_rc" -ne 0 ]; then
      say "[QUALITY][WARN] Smoke-Test fehlgeschlagen (Code: $smoke_rc)."
      say "[QUALITY][HILFE] Nächster Schritt: bash start.sh für automatische Reparaturhilfe oder python3 tools/smoke_test.py für Einzeldiagnose."
      WARNINGS=$((WARNINGS + 1))
    else
      say "[QUALITY][OK] Smoke-Test erfolgreich abgeschlossen."
    fi
  fi
else
  say "[QUALITY][INFO] Kein Smoke-Test gefunden."
fi


announce_quality_step 5 "A11y-Theme-Check"
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

announce_quality_step 6 "JSON-Struktur-Check"
validate_required_json "$ROOT_DIR/data/settings.json" "theme,large_text,download_dir,presets,filters,duplicates_mode" "theme:str,large_text:bool,download_dir:str,presets:str,filters:dict,duplicates_mode:str"
validate_required_json "$ROOT_DIR/data/standards_manifest.json" "manifest_version,language_policy,accessibility,quality_gates,validation_policy,structure_policy" "manifest_version:str,language_policy:dict,accessibility:dict,quality_gates:list,validation_policy:dict,structure_policy:dict"
validate_required_json "$ROOT_DIR/data/design_reference_domotic_assistant.json" "reference,visual_language,palette,layout_blueprint,typography,component_targets,accessibility_targets,view_questions_checklist,project_mapping" "reference:dict,visual_language:dict,palette:dict,layout_blueprint:dict,typography:dict,component_targets:dict,accessibility_targets:dict,view_questions_checklist:list,project_mapping:dict"
validate_required_json "$ROOT_DIR/data/presets/standard.json" "name,description,filters,duplicates_mode,confirm_threshold" "name:str,description:str,filters:dict,duplicates_mode:str,confirm_threshold:number" "confirm_threshold:1:100"
validate_required_json "$ROOT_DIR/data/presets/power.json" "name,description,filters,duplicates_mode,confirm_threshold" "name:str,description:str,filters:dict,duplicates_mode:str,confirm_threshold:number" "confirm_threshold:1:100"
validate_required_json "$ROOT_DIR/data/presets/senior.json" "name,description,filters,duplicates_mode,confirm_threshold" "name:str,description:str,filters:dict,duplicates_mode:str,confirm_threshold:number" "confirm_threshold:1:100"


announce_quality_step 7 "Validierungsstandard-Check"
if ! python3 - "$ROOT_DIR/core/validation.py" <<'PY'
import ast
import sys
from pathlib import Path

validation_file = Path(sys.argv[1])
source = validation_file.read_text(encoding="utf-8")
tree = ast.parse(source)
functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
required = {"require_type", "require_non_empty_text", "require_output"}
missing = sorted(required - functions)
if missing:
    print(f"[QUALITY][WARN] Validierungsstandard unvollständig: {', '.join(missing)} fehlt.")
    print("[QUALITY][HILFE] Nächster Schritt: Fehlende Standardfunktion in core/validation.py ergänzen und Check erneut starten.")
    raise SystemExit(1)
print("[QUALITY][OK] Validierungsstandard geprüft: require_type, require_non_empty_text, require_output vorhanden.")
PY
then
  WARNINGS=$((WARNINGS + 1))
fi

announce_quality_step 8 "Versions-Registry-Check"
validate_version_registry



announce_quality_step 9 "Exit-Knoten-Hilfe-Check"
if [ -f "$ROOT_DIR/tools/exit_path_audit.py" ]; then
  if ! python3 "$ROOT_DIR/tools/exit_path_audit.py"; then
    say "[QUALITY][WARN] Exit-Knoten-Check meldet fehlende Lösungshinweise."
    say "[QUALITY][HILFE] Nächster Schritt: Bei den gemeldeten Zeilen jeweils einen kurzen Hinweis mit Nächster Schritt ergänzen."
    WARNINGS=$((WARNINGS + 1))
  fi
else
  say "[QUALITY][WARN] Exit-Knoten-Check fehlt (tools/exit_path_audit.py)."
  say "[QUALITY][HILFE] Nächster Schritt: Datei wiederherstellen oder aus Versionsverwaltung holen."
  WARNINGS=$((WARNINGS + 1))
fi
announce_quality_step 10 "Mini-UX-Gate"
if [ -f "$ROOT_DIR/tools/mini_ux_gate.py" ]; then
  if ! python3 "$ROOT_DIR/tools/mini_ux_gate.py"; then
    say "[QUALITY][WARN] Mini-UX-Gate meldet fehlende Hilfe-/A11y-Hinweise."
    say "[QUALITY][HILFE] Nächster Schritt: Erste gemeldete Stelle mit kurzer Hilfe in einfacher Sprache ergänzen."
    WARNINGS=$((WARNINGS + 1))
  fi
else
  say "[QUALITY][WARN] Mini-UX-Gate fehlt (tools/mini_ux_gate.py)."
  say "[QUALITY][HILFE] Nächster Schritt: Datei wiederherstellen oder aus Versionsverwaltung holen."
  WARNINGS=$((WARNINGS + 1))
fi

announce_quality_step 11 "Design-Referenz-Check"
if [ -f "$ROOT_DIR/tools/design_reference_check.py" ]; then
  if ! python3 "$ROOT_DIR/tools/design_reference_check.py"; then
    say "[QUALITY][WARN] Design-Referenz-Check meldet Lücken bei Layout-, A11y- oder Fragen-Standards."
    say "[QUALITY][HILFE] Nächster Schritt: data/design_reference_domotic_assistant.json anhand der Warnung ergänzen und Check erneut starten."
    WARNINGS=$((WARNINGS + 1))
  fi
else
  say "[QUALITY][WARN] Design-Referenz-Check fehlt (tools/design_reference_check.py)."
  say "[QUALITY][HILFE] Nächster Schritt: Datei wiederherstellen oder aus Versionsverwaltung holen."
  WARNINGS=$((WARNINGS + 1))
fi

announce_quality_step 12 "Release-Lücken-Report"
if [ -f "$ROOT_DIR/tools/release_gap_report.py" ]; then
  if ! python3 "$ROOT_DIR/tools/release_gap_report.py"; then
    say "[QUALITY][WARN] Release-Lücken-Report zeigt noch offene oder widersprüchliche Punkte."
    say "[QUALITY][HILFE] Nächster Schritt: zuerst den ersten Report-Punkt lösen, dann den Check erneut starten."
    WARNINGS=$((WARNINGS + 1))
  fi
else
  say "[QUALITY][WARN] Release-Lücken-Report fehlt (tools/release_gap_report.py)."
  say "[QUALITY][HILFE] Nächster Schritt: Datei wiederherstellen oder aus Versionsverwaltung holen."
  WARNINGS=$((WARNINGS + 1))
fi

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

print_quality_summary_for_humans "$WARNINGS"
