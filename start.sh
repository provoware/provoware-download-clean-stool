#!/bin/bash
set -euo pipefail

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

mkdir -p logs exports
SETUP_LOG="exports/setup_log.txt"
ERR_LOG="exports/last_start_error.txt"
QUALITY_LOG="exports/quality_report.txt"
TOOL_WORKDIR_SLUG="provoware-clean-tool-2026"

normalize_enable_auto_format_flag() {
  # Validiert das Format-Flag (0/1) und liefert bei Fehlern einen sicheren Fallback.
  local raw_value="${1:-1}"
  if [ "$raw_value" = "0" ] || [ "$raw_value" = "1" ]; then
    printf '%s' "$raw_value"
    return 0
  fi
  echo "[WARN] ENABLE_AUTO_FORMAT hat einen ungültigen Wert '$raw_value'. Erlaubt sind nur 0 oder 1." | tee -a "$SETUP_LOG"
  echo "[HILFE] Nächster Schritt: ENABLE_AUTO_FORMAT=1 bash start.sh für Auto-Format oder ENABLE_AUTO_FORMAT=0 bash start.sh zum Überspringen." | tee -a "$SETUP_LOG"
  printf '%s' "1"
  return 1
}

run_preflight_health_checks() {
  # Prüft notwendige Start-Dateien vor dem Setup und liefert klare Next Steps.
  # Output: 0 wenn alle Pflichtdateien vorhanden sind, sonst 1.
  local required_paths=(
    "tools/run_quality_checks.sh"
    "tools/a11y_theme_check.py"
    "tools/boot_error_gui.py"
    "requirements.txt"
    "tools/smoke_test.py"
    "data/version_registry.json"
  )
  local missing_paths=()
  local path

  for path in "${required_paths[@]}"; do
    if [ ! -f "$path" ]; then
      missing_paths+=("$path")
    fi
  done

  if ! ensure_optional_info_files; then
    echo "[WARN] Vorprüfung: Optionale Info-Dateien konnten nicht automatisch vorbereitet werden." | tee -a "$SETUP_LOG"
    echo "[HILFE] Nächster Schritt: Schreibrechte im Projektordner prüfen und danach bash start.sh erneut ausführen." | tee -a "$SETUP_LOG"
    return 1
  fi

  if ! ensure_required_cli_tools; then
    echo "[WARN] Vorprüfung: Benötigte Befehle konnten nicht vollständig vorbereitet werden." | tee -a "$SETUP_LOG"
    echo "[HILFE] Nächster Schritt: Hinweise im Log befolgen und danach erneut starten: bash start.sh" | tee -a "$SETUP_LOG"
    return 1
  fi

  if [ "${#missing_paths[@]}" -eq 0 ]; then
    echo "[CHECK] Vorprüfung: Alle Pflichtdateien sind vorhanden." | tee -a "$SETUP_LOG"
    return 0
  fi

  echo "[WARN] Vorprüfung fehlgeschlagen: Pflichtdateien fehlen." | tee -a "$SETUP_LOG"
  for path in "${missing_paths[@]}"; do
    echo "[WARN] - fehlt: $path" | tee -a "$SETUP_LOG"
  done
  echo "[HILFE] Nächster Schritt 1: Fehlende Dateien aus dem Repository wiederherstellen (git restore <datei>)." | tee -a "$SETUP_LOG"
  echo "[HILFE] Nächster Schritt 2: Danach erneut starten: bash start.sh" | tee -a "$SETUP_LOG"
  return 1
}

detect_linux_pkg_manager() {
  # Ermittelt den verfügbaren Linux-Paketmanager für automatische Reparatur.
  # Output: apt-get|dnf|pacman oder leer, wenn keiner erkannt wurde.
  if command -v apt-get >/dev/null 2>&1; then
    printf '%s' "apt-get"
    return 0
  fi
  if command -v dnf >/dev/null 2>&1; then
    printf '%s' "dnf"
    return 0
  fi
  if command -v pacman >/dev/null 2>&1; then
    printf '%s' "pacman"
    return 0
  fi
  printf '%s' ""
  return 1
}

try_install_cli_tool() {
  # Installiert ein fehlendes CLI-Werkzeug automatisch, wenn ein unterstützter Paketmanager verfügbar ist.
  # Input: tool_name. Output: 0 bei Erfolg, sonst 1 mit Next Steps.
  local tool_name="${1:-}"
  local pkg_manager
  local package_name=""

  if [ -z "$tool_name" ]; then
    echo "[WARN] CLI-Reparatur ohne Tool-Namen aufgerufen." | tee -a "$SETUP_LOG"
    return 1
  fi

  case "$tool_name" in
    rg)
      package_name="ripgrep"
      ;;
    *)
      echo "[WARN] Für CLI-Tool '$tool_name' ist keine Auto-Reparatur hinterlegt." | tee -a "$SETUP_LOG"
      return 1
      ;;
  esac

  pkg_manager="$(detect_linux_pkg_manager || true)"
  if [ -z "$pkg_manager" ]; then
    echo "[WARN] Kein unterstützter Paketmanager gefunden. '$tool_name' konnte nicht automatisch installiert werden." | tee -a "$SETUP_LOG"
    echo "[HILFE] Nächster Schritt: '$tool_name' manuell installieren und danach bash start.sh erneut ausführen." | tee -a "$SETUP_LOG"
    return 1
  fi

  echo "[SETUP] Auto-Reparatur: installiere '$tool_name' über $pkg_manager." | tee -a "$SETUP_LOG"
  case "$pkg_manager" in
    apt-get)
      run_with_sudo "apt-get update" apt-get update >>"$SETUP_LOG" 2>&1 || return 1
      run_with_sudo "apt-get install $package_name" apt-get install -y "$package_name" >>"$SETUP_LOG" 2>&1 || return 1
      ;;
    dnf)
      run_with_sudo "dnf install $package_name" dnf install -y "$package_name" >>"$SETUP_LOG" 2>&1 || return 1
      ;;
    pacman)
      run_with_sudo "pacman install $package_name" pacman -Sy --noconfirm "$package_name" >>"$SETUP_LOG" 2>&1 || return 1
      ;;
    *)
      return 1
      ;;
  esac

  if command -v "$tool_name" >/dev/null 2>&1; then
    echo "[OK] CLI-Tool erfolgreich vorbereitet: $tool_name" | tee -a "$SETUP_LOG"
    return 0
  fi

  echo "[WARN] '$tool_name' wurde installiert, ist aber noch nicht im PATH verfügbar." | tee -a "$SETUP_LOG"
  echo "[HILFE] Nächster Schritt: Terminal neu öffnen und erneut starten: bash start.sh" | tee -a "$SETUP_LOG"
  return 1
}

ensure_required_cli_tools() {
  # Prüft wichtige Befehle für den Start und repariert fehlende Tools soweit möglich automatisch.
  # Output: 0 wenn alle Befehle bereit sind, sonst 1.
  local required_tools=("bash" "python3" "rg")
  local tool_name
  local missing_count=0

  for tool_name in "${required_tools[@]}"; do
    if command -v "$tool_name" >/dev/null 2>&1; then
      echo "[CHECK] Befehl verfügbar: $tool_name" | tee -a "$SETUP_LOG"
      continue
    fi

    echo "[WARN] Benötigter Befehl fehlt: $tool_name" | tee -a "$SETUP_LOG"
    if try_install_cli_tool "$tool_name"; then
      continue
    fi

    missing_count=$((missing_count + 1))
    echo "[HILFE] Nächster Schritt: Tool '$tool_name' installieren und danach erneut starten." | tee -a "$SETUP_LOG"
  done

  if [ "$missing_count" -eq 0 ]; then
    echo "[CHECK] CLI-Vorprüfung vollständig: alle Befehle sind bereit." | tee -a "$SETUP_LOG"
    return 0
  fi

  return 1
}

ensure_optional_info_files() {
  # Repariert fehlende Info-Dateien automatisch mit minimalem Standardinhalt.
  # Output: 0 wenn alle Ziel-Dateien vorhanden sind, sonst 1.
  local info_files=("README.md" "CHANGELOG.md" "todo.txt")
  local file_path
  local created_count=0

  for file_path in "${info_files[@]}"; do
    if [ -f "$file_path" ]; then
      continue
    fi

    case "$file_path" in
      "README.md")
        printf '%s\n\n%s\n' "# Projektübersicht" "Diese Datei wurde automatisch wiederhergestellt. Nächster Schritt: Inhalte aus Git ergänzen (git restore README.md)." > "$file_path"
        ;;
      "CHANGELOG.md")
        printf '%s\n\n- Was: Datei automatisch wiederhergestellt.\n- Warum: Startablauf benötigt vollständige Basis-Doku.\n- Wirkung: Startroutine kann ohne Abbruch weiterlaufen.\n' "# CHANGELOG" > "$file_path"
        ;;
      "todo.txt")
        printf '%s\n%s\n' "DONE: Automatische Wiederherstellung von todo.txt durchgeführt ($(date +%Y-%m-%d))." "NEXT: Inhalte aus Versionsverwaltung prüfen und ergänzen ($(date +%Y-%m-%d))." > "$file_path"
        ;;
    esac

    if [ -f "$file_path" ]; then
      created_count=$((created_count + 1))
      echo "[CHECK] Info-Datei automatisch wiederhergestellt: $file_path" | tee -a "$SETUP_LOG"
      echo "[HILFE] Nächster Schritt: git diff $file_path prüfen und bei Bedarf git restore $file_path verwenden." | tee -a "$SETUP_LOG"
    else
      echo "[WARN] Info-Datei konnte nicht erstellt werden: $file_path" | tee -a "$SETUP_LOG"
      return 1
    fi
  done

  echo "[CHECK] Optionale Info-Dateien geprüft. Neu erstellt: $created_count" | tee -a "$SETUP_LOG"
  return 0
}

run_auto_format_step() {
  # Führt bei Bedarf einen klaren Auto-Format-Lauf über das Quality-Skript aus.
  # Input: ENABLE_AUTO_FORMAT (0/1). Output: 0 bei Erfolg oder bewusstem Skip, sonst 1.
  local enable_auto_format="${1:-1}"

  if [ "$enable_auto_format" = "0" ]; then
    echo "[FORMAT] Auto-Format ist deaktiviert (ENABLE_AUTO_FORMAT=0)." | tee -a "$SETUP_LOG"
    return 0
  fi

  echo "[FORMAT] Starte automatisches Formatieren und Kurzprüfung (AUTO_FIX=1, FAST_MODE=1)." | tee -a "$SETUP_LOG"
  if AUTO_FIX=1 FAST_MODE=1 AUTO_INSTALL_TOOLS=1 bash tools/run_quality_checks.sh >> "$QUALITY_LOG" 2>&1; then
    echo "[OK] Auto-Formatierung abgeschlossen." | tee -a "$SETUP_LOG"
    return 0
  fi

  echo "[WARN] Auto-Formatierung meldet Warnungen. Der normale Qualitätslauf folgt trotzdem." | tee -a "$SETUP_LOG"
  echo "[HILFE] Nächster Schritt: quality_report prüfen und die erste Warnung beheben." | tee -a "$SETUP_LOG"
  return 1
}


run_gate_compileall() {
  # Führt GATE 1 (Syntax) als eigenen Startschritt mit klarer Hilfe aus.
  # Output: 0 bei Erfolg, 1 bei Fehlern mit nächsten Schritten.
  echo "[GATE][G1] Starte Syntaxprüfung: python -m compileall -q ." | tee -a "$SETUP_LOG"
  if "$VENV_PY" -m compileall -q . >>"$SETUP_LOG" 2>&1; then
    echo "[GATE][G1] ✅ Syntaxprüfung bestanden." | tee -a "$SETUP_LOG"
    return 0
  fi

  echo "[GATE][G1] ⚠️ Syntaxprüfung fehlgeschlagen." | tee -a "$SETUP_LOG"
  echo "[HILFE] Nächster Schritt 1: Protokoll öffnen: cat exports/setup_log.txt" | tee -a "$SETUP_LOG"
  echo "[HILFE] Nächster Schritt 2: Fehler beheben und erneut prüfen: python -m compileall -q ." | tee -a "$SETUP_LOG"
  echo "[HILFE] Nächster Schritt 3: Danach erneut starten: bash start.sh" | tee -a "$SETUP_LOG"
  return 1
}

run_mini_ux_gate() {
  # Führt das Mini-UX-Gate (G5) direkt in der Startroutine aus.
  # Output: 0 bei bestandenem Gate, 1 bei Warnungen oder technischen Fehlern.
  if [ ! -f "tools/mini_ux_gate.py" ]; then
    echo "[WARN] Mini-UX-Gate nicht gefunden: tools/mini_ux_gate.py" | tee -a "$SETUP_LOG"
    echo "[HILFE] Nächster Schritt: Datei wiederherstellen (git restore tools/mini_ux_gate.py) und erneut starten." | tee -a "$SETUP_LOG"
    return 1
  fi

  if "$VENV_PY" tools/mini_ux_gate.py >> "$QUALITY_LOG" 2>&1; then
    echo "[STATUS] ✅ Mini-UX-Gate: OK" | tee -a "$SETUP_LOG"
    return 0
  fi

  echo "[WARN] Mini-UX-Gate meldet offene Hinweise." | tee -a "$SETUP_LOG"
  echo "[HILFE] Nächster Schritt: $VENV_PY tools/mini_ux_gate.py ausführen und zuerst die erste Warnung beheben." | tee -a "$SETUP_LOG"
  return 1
}

determine_default_workdir() {
  # Ermittelt den Linux-Standardarbeitsordner im Nutzerpfad.
  # Output: voller Pfad oder leer bei ungültiger HOME-Umgebung.
  local home_dir="${HOME:-}"
  if [ -z "$home_dir" ] || [ ! -d "$home_dir" ]; then
    printf '%s' ""
    return 1
  fi
  printf '%s' "$home_dir/.local/share/$TOOL_WORKDIR_SLUG"
}

ensure_tool_workdir() {
  # Prüft den Arbeitsordner bei Start und legt ihn bei Bedarf mit sicheren Linux-Rechten an.
  # Output: Pfad wird in TOOL_WORKDIR gesetzt, Return 0 bei Erfolg.
  local default_workdir
  default_workdir="$(determine_default_workdir)"
  if [ -z "$default_workdir" ]; then
    echo "[WARN] HOME-Pfad ist ungültig. Standard-Arbeitsordner konnte nicht ermittelt werden." | tee -a "$SETUP_LOG"
    echo "[HILFE] Nächster Schritt: Mit normalem Benutzerkonto anmelden und danach erneut starten: bash start.sh" | tee -a "$SETUP_LOG"
    return 1
  fi

  if [ ! -e "$default_workdir" ]; then
    echo "[CHECK] Arbeitsordner fehlt. Lege Standardordner an: $default_workdir" | tee -a "$SETUP_LOG"
    if ! mkdir -p "$default_workdir"; then
      echo "[WARN] Arbeitsordner konnte nicht angelegt werden (Linux-Rechte fehlen)." | tee -a "$SETUP_LOG"
      echo "[HILFE] Nächster Schritt: Rechte prüfen (z. B. chmod u+rwx '$HOME/.local/share') und erneut starten." | tee -a "$SETUP_LOG"
      return 1
    fi
  fi

  if [ ! -d "$default_workdir" ] || [ ! -r "$default_workdir" ] || [ ! -w "$default_workdir" ] || [ ! -x "$default_workdir" ]; then
    echo "[WARN] Arbeitsordner ist vorhanden, aber Linux-Rechte sind unvollständig: $default_workdir" | tee -a "$SETUP_LOG"
    echo "[HILFE] Nächster Schritt: Im Terminal ausführen: chmod u+rwx '$default_workdir'" | tee -a "$SETUP_LOG"
    return 1
  fi

  chmod u+rwx "$default_workdir" 2>/dev/null || true
  TOOL_WORKDIR="$default_workdir"
  export TOOL_WORKDIR
  echo "[OK] Arbeitsordner geprüft: $TOOL_WORKDIR" | tee -a "$SETUP_LOG"
  return 0
}

sync_settings_workdir() {
  # Schreibt den geprüften Arbeitsordner als Download-Ordner in data/settings.json.
  # Input: TOOL_WORKDIR muss gesetzt sein. Output: 0 bei erfolgreicher Synchronisierung.
  if [ -z "${TOOL_WORKDIR:-}" ]; then
    echo "[WARN] TOOL_WORKDIR fehlt. Einstellungen konnten nicht synchronisiert werden." | tee -a "$SETUP_LOG"
    return 1
  fi

  "$PROJECT_DIR/venv/bin/python" - <<'PY' >>"$SETUP_LOG" 2>&1
from __future__ import annotations

import json
import os
from pathlib import Path

settings_path = Path("data/settings.json")
workdir = os.environ.get("TOOL_WORKDIR", "").strip()
if not workdir:
    raise SystemExit(1)

if settings_path.exists():
    data = json.loads(settings_path.read_text(encoding="utf-8"))
else:
    data = {}

configured = str(data.get("download_dir", "")).strip()
if configured != workdir:
    data["download_dir"] = workdir
    settings_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
PY
}

normalize_binary_runtime_flag() {
  # Akzeptiert nur 0 oder 1 für Laufzeit-Flags und zeigt bei Fehlern klare Next Steps.
  local raw_value="${1:-0}"
  local label="${2:-FLAG}"
  if [ "$raw_value" = "0" ] || [ "$raw_value" = "1" ]; then
    printf '%s' "$raw_value"
    return 0
  fi
  echo "[WARN] $label hat einen ungültigen Wert '$raw_value'. Erlaubt sind nur 0 oder 1." | tee -a "$SETUP_LOG"
  echo "[HILFE] Nächster Schritt: $label=1 bash start.sh (Debug aktiv) oder $label=0 bash start.sh (Debug aus)." | tee -a "$SETUP_LOG"
  printf '%s' "0"
  return 1
}

log_debug() {
  # Gibt zusätzliche Debug-Infos aus, wenn DEBUG_LOG_MODE=1 gesetzt ist.
  local message="${1:-}"
  if [ "${DEBUG_LOG_MODE:-0}" = "1" ] && [ -n "$message" ]; then
    echo "[DEBUG] $message" | tee -a "$SETUP_LOG"
  fi
}

normalize_status_value() {
  # Validiert Statuswerte für die Abschluss-Zusammenfassung.
  # Erlaubte Werte: OK, WARN, läuft, erfolgreich, nicht möglich, nicht nötig.
  local raw_value="${1:-}"
  case "$raw_value" in
    OK|WARN|läuft|erfolgreich|"nicht möglich"|"nicht nötig")
      printf '%s' "$raw_value"
      ;;
    *)
      printf '%s' "WARN"
      ;;
  esac
}

validate_non_negative_int() {
  # Prüft, ob ein Wert eine nicht-negative Ganzzahl ist.
  # Input: beliebiger Text. Output: Zahl oder 0 als sicherer Fallback.
  local raw_value="${1:-0}"
  if [[ "$raw_value" =~ ^[0-9]+$ ]]; then
    printf '%s' "$raw_value"
    return 0
  fi
  printf '%s' "0"
  return 1
}


print_module_repair_status_block() {
  # Zeigt je fehlendem Python-Modul den Reparaturstatus in einfacher Sprache.
  # Input: kommaseparierte Modulliste. Output: Statusblock mit klaren Next Steps.
  local missing_csv="${1:-}"
  local normalized_csv
  normalized_csv="$(printf '%s' "$missing_csv" | tr -d '[:space:]')"

  if [ -z "$normalized_csv" ]; then
    echo "[SETUP] Modul-Reparatur: Keine fehlenden Module erkannt." | tee -a "$SETUP_LOG"
    echo "[SETUP] Modul-Reparatur kompakt (Priorität):" | tee -a "$SETUP_LOG"
    echo "[SETUP] - keine Einträge (nicht nötig)" | tee -a "$SETUP_LOG"
    return 0
  fi

  echo "[SETUP] ===== Modul-Reparaturstatus ====="
  IFS=',' read -r -a raw_modules <<< "$normalized_csv"
  local repaired_count=0
  local failed_count=0
  local module_name
  local module_priority
  local compact_report="[SETUP] Modul-Reparatur kompakt (Priorität):"

  for module_name in "${raw_modules[@]}"; do
    [ -z "$module_name" ] && continue
    case "$module_name" in
      PySide6*|Pillow*|PIL*|numpy*|pandas*)
        module_priority="kritisch"
        ;;
      *)
        module_priority="mittel"
        ;;
    esac

    if "$VENV_PY" -c "import importlib; importlib.import_module('$module_name')" >>"$SETUP_LOG" 2>&1; then
      echo "[SETUP] Import jetzt OK: $module_name (Priorität: $module_priority)"
      compact_report+="\n[SETUP] - $module_name => OK ($module_priority)"
      repaired_count=$((repaired_count + 1))
    else
      echo "[SETUP] Import weiterhin FEHLER: $module_name (Priorität: $module_priority)"
      compact_report+="\n[SETUP] - $module_name => FEHLER ($module_priority)"
      failed_count=$((failed_count + 1))
    fi
  done

  echo "[SETUP] Ergebnis: OK=$repaired_count | FEHLER=$failed_count"
  printf '%b\n' "$compact_report" | tee -a "$SETUP_LOG"
  if [ "$failed_count" -gt 0 ]; then
    echo "[HILFE] Nächster Schritt 1: Modulwarnungen im Log lesen: cat exports/setup_log.txt"
    echo "[HILFE] Nächster Schritt 2: Ein Modul nach dem anderen reparieren (nicht alles gleichzeitig)."
    return 1
  fi
  return 0
}

print_quality_quickfix_block() {
  # Zeigt einen kompakten Qualitätsblock mit klaren Auto-Fix-Befehlen.
  # Input: Warnzahl, Infozahl, Logpfad. Output: laienfreundliche Next Steps.
  local warn_count="${1:-0}"
  local info_count="${2:-0}"
  local quality_log_path="${3:-exports/quality_report.txt}"
  local validated_warn_count
  local validated_info_count
  validated_warn_count="$(validate_non_negative_int "$warn_count")"
  validated_info_count="$(validate_non_negative_int "$info_count")"

  echo "[QUALITÄT] ===== Kompaktblock ====="
  echo "[QUALITÄT] Warnungen: $validated_warn_count | Hinweise: $validated_info_count"
  echo "[QUALITÄT] Protokoll: $quality_log_path"
  if [ "$validated_warn_count" -gt 0 ]; then
    echo "[QUALITÄT] Nächster Schritt (Auto-Fix): AUTO_FIX=1 bash tools/run_quality_checks.sh"
    echo "[QUALITÄT] Danach neu prüfen: bash tools/run_quality_checks.sh"
    echo "[QUALITÄT] Danach Start wiederholen: bash start.sh"
  else
    echo "[QUALITÄT] Keine Warnungen erkannt. Für Kontrolle optional: bash tools/run_quality_checks.sh"
  fi
}

print_start_summary_for_humans() {
  # Zeigt eine laienfreundliche Abschluss-Übersicht mit klaren Next Steps.
  local dep_status_input="${1:-WARN}"
  local quality_status_input="${2:-WARN}"
  local autorepair_status_input="${3:-nicht möglich}"
  local web_status_input="${4:-WARN}"
  local appimage_status_input="${5:-WARN}"
  local quality_warn_count="${6:-0}"
  local quality_info_count="${7:-0}"
  local quality_log_path="${8:-exports/quality_report.txt}"

  local dep_status
  local quality_status
  local autorepair_status
  dep_status="$(normalize_status_value "$dep_status_input")"
  quality_status="$(normalize_status_value "$quality_status_input")"
  autorepair_status="$(normalize_status_value "$autorepair_status_input")"

  case "$web_status_input" in
    OK|WARN) ;;
    *) web_status_input="WARN" ;;
  esac
  case "$appimage_status_input" in
    OK|WARN) ;;
    *) appimage_status_input="WARN" ;;
  esac

  echo "[ÜBERSICHT] ===== Startprüfung in einfacher Sprache ====="
  echo "[ÜBERSICHT] Abhängigkeiten: $dep_status"
  echo "[ÜBERSICHT] Qualitätsprüfung: $quality_status"
  echo "[ÜBERSICHT] Auto-Reparatur: $autorepair_status"
  echo "[ÜBERSICHT] Optional Web-Frontend: $web_status_input"
  echo "[ÜBERSICHT] Optional AppImage: $appimage_status_input"

  if [ "$dep_status" = "OK" ] && [ "$quality_status" = "OK" ]; then
    echo "[HILFE] Alles Wichtige ist grün. Sie können normal weiterarbeiten."
  else
    echo "[HILFE] Es gibt mindestens eine Warnung. Bitte diese 3 Schritte nacheinander ausführen:"
    echo "[HILFE] 1) Protokoll öffnen: cat exports/setup_log.txt"
    echo "[HILFE] 2) Qualität prüfen: bash tools/run_quality_checks.sh"
    echo "[HILFE] 3) Start erneut ausführen: bash start.sh"
  fi

  print_quality_quickfix_block "$quality_warn_count" "$quality_info_count" "$quality_log_path"
}

run_with_sudo() {
  # Führt einen Befehl mit sudo aus, wenn möglich.
  # Gibt bei Fehlern klare Next Steps in einfacher Sprache aus.
  local context_label="$1"
  shift

  if ! command -v sudo >/dev/null 2>&1; then
    echo "[WARN] sudo fehlt. $context_label konnte nicht automatisch ausgeführt werden." | tee -a "$SETUP_LOG"
    echo "[HILFE] Nächster Schritt: sudo installieren und danach erneut starten: bash start.sh" | tee -a "$SETUP_LOG"
    return 1
  fi

  if sudo -n true >/dev/null 2>&1; then
    sudo "$@"
    return $?
  fi

  echo "[WARN] sudo benötigt ein Passwort oder ist nicht freigegeben. $context_label konnte nicht automatisch ausgeführt werden." | tee -a "$SETUP_LOG"
  echo "[HILFE] Nächster Schritt: Terminal öffnen und den Befehl manuell ausführen. Danach erneut starten: bash start.sh" | tee -a "$SETUP_LOG"
  return 1
}

detect_system_pkg_manager() {
  # Gibt den Paketmanager zurück, der auf dem System verfügbar ist.
  if command -v apt-get >/dev/null 2>&1; then
    printf '%s' "apt-get"
    return 0
  fi
  if command -v dnf >/dev/null 2>&1; then
    printf '%s' "dnf"
    return 0
  fi
  if command -v pacman >/dev/null 2>&1; then
    printf '%s' "pacman"
    return 0
  fi
  printf '%s' ""
}

try_install_python_venv() {
  # Versucht python3-venv (oder Distribution-Äquivalent) automatisch zu installieren.
  # Input: kein Argument. Output: 0 bei Erfolg, 1 bei nicht möglich.
  local pkg_manager
  pkg_manager="$(detect_system_pkg_manager)"
  if [ -z "$pkg_manager" ]; then
    echo "[WARN] Kein unterstützter Paketmanager gefunden (apt-get/dnf/pacman)." | tee -a "$SETUP_LOG"
    echo "[HILFE] Nächster Schritt: python3-venv manuell installieren und dann bash start.sh erneut ausführen." | tee -a "$SETUP_LOG"
    return 1
  fi

  case "$pkg_manager" in
    apt-get)
      run_with_sudo "apt-get update" apt-get update >>"$SETUP_LOG" 2>&1 || return 1
      run_with_sudo "apt-get install python3-venv" apt-get install -y python3-venv >>"$SETUP_LOG" 2>&1 || return 1
      ;;
    dnf)
      run_with_sudo "dnf install python3-virtualenv" dnf install -y python3-virtualenv >>"$SETUP_LOG" 2>&1 || return 1
      ;;
    pacman)
      run_with_sudo "pacman install python-virtualenv" pacman -Sy --noconfirm python-virtualenv >>"$SETUP_LOG" 2>&1 || return 1
      ;;
    *)
      echo "[WARN] Paketmanager $pkg_manager wird für Auto-Reparatur nicht unterstützt." | tee -a "$SETUP_LOG"
      return 1
      ;;
  esac

  return 0
}


requirement_to_import_name() {
  # Leitet aus einem requirements-Eintrag einen wahrscheinlichen Importnamen ab.
  # Beispiel: PySide6>=6.5 -> PySide6
  local requirement_text="${1:-}"
  local normalized
  normalized="$(printf '%s' "$requirement_text" | sed -E 's/[[:space:]]*\[.*\]//g' | sed -E 's/[<>=!~].*$//' | tr -d '[:space:]')"
  case "$normalized" in
    Pillow)
      printf '%s' "PIL"
      return 0
      ;;
    pyyaml|PyYAML)
      printf '%s' "yaml"
      return 0
      ;;
    *)
      printf '%s' "$normalized"
      return 0
      ;;
  esac
}

collect_missing_python_modules() {
  # Prüft alle requirement-Einträge per Import-Test und gibt fehlende Module zeilenweise aus.
  local req_file="${1:-requirements.txt}"
  local venv_python="${2:-python3}"

  if [ ! -f "$req_file" ]; then
    return 0
  fi

  "$venv_python" - "$req_file" <<'PYCODE'
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

req_path = Path(sys.argv[1])
module_aliases = {"Pillow": "PIL", "PyYAML": "yaml"}
missing: list[str] = []
for raw in req_path.read_text(encoding="utf-8").splitlines():
    cleaned = re.sub(r"#.*$", "", raw).strip()
    if not cleaned or cleaned.startswith("-"):
        continue
    package = re.split(r"[<>=!~]", cleaned, maxsplit=1)[0].strip()
    package = re.sub(r"\[.*\]", "", package)
    module_name = module_aliases.get(package, package)
    if not module_name:
        continue
    try:
        importlib.import_module(module_name)
    except Exception:
        missing.append(cleaned)

if missing:
    print("\n".join(missing))
PYCODE
}

print_accessibility_next_steps() {
  # Zeigt kurze, feste Hilfe zu Tastatur und Kontrast an.
  # Hilft beim barrierearmen Einstieg direkt nach der Startprüfung.
  echo "[A11Y] Kurze Hilfe (barrierearm):"
  echo "[A11Y] 1) Tastatur: Mit Tab navigieren, Shift+Tab zurück, Enter zum Ausführen."
  echo "[A11Y] 2) Lesbarkeit: Bei zu wenig Kontrast Theme wechseln (Dark/Light/High-Contrast)."
  echo "[A11Y] 3) Schnelltest: python3 tools/a11y_theme_check.py"
  echo "[A11Y] 4) Klarer Ablauf: Scan starten → Vorschau prüfen → Aufräumen ausführen."
  echo "[A11Y] 5) Bei Unsicherheit: DEBUG_LOG_MODE=1 bash start.sh für detaillierte Hilfe starten."
}

extract_quality_count() {
  # Liest die Anzahl eines Quality-Patterns robust aus dem Qualitätsprotokoll.
  # Input: Pattern und Logpfad. Output: nicht-negative Ganzzahl.
  local pattern="${1:-}"
  local quality_log_path="${2:-exports/quality_report.txt}"
  local raw_count="0"

  if [ -z "$pattern" ] || [ ! -f "$quality_log_path" ]; then
    printf '%s' "0"
    return 0
  fi

  raw_count="$(rg -c "$pattern" "$quality_log_path" 2>/dev/null | head -n 1 || echo "0")"
  validate_non_negative_int "$raw_count"
}


run_a11y_theme_gate() {
  # Prüft Theme-Kontraste automatisch und liefert klare Hilfe bei Warnungen.
  # Output: 0 bei erfolgreicher Prüfung ohne Warnstatus, sonst 1.
  local a11y_log_path="${1:-exports/quality_report.txt}"

  if [ ! -f "tools/a11y_theme_check.py" ]; then
    echo "[WARN] A11y-Theme-Check fehlt (tools/a11y_theme_check.py)." | tee -a "$SETUP_LOG"
    echo "[HILFE] Nächster Schritt: Datei wiederherstellen und danach bash start.sh erneut ausführen." | tee -a "$SETUP_LOG"
    return 1
  fi

  if [ -z "${VENV_PY:-}" ] || [ ! -x "${VENV_PY:-}" ]; then
    echo "[WARN] VENV-Python ist nicht verfügbar. A11y-Theme-Check kann nicht sicher gestartet werden." | tee -a "$SETUP_LOG"
    echo "[HILFE] Nächster Schritt: Prüfen Sie die virtuelle Umgebung (venv/) und starten Sie danach bash start.sh erneut." | tee -a "$SETUP_LOG"
    return 1
  fi

  if "$VENV_PY" tools/a11y_theme_check.py >> "$a11y_log_path" 2>&1; then
    echo "[OK] A11y-Theme-Check ist grün." | tee -a "$SETUP_LOG"
    return 0
  fi

  echo "[WARN] A11y-Theme-Check meldet Kontrast- oder Theme-Warnungen." | tee -a "$SETUP_LOG"
  echo "[HILFE] Nächster Schritt: python3 tools/a11y_theme_check.py ausführen und erste Warnung im Theme korrigieren." | tee -a "$SETUP_LOG"
  return 1
}
run_quality_with_autofix() {
  # Führt den Qualitätslauf robust aus: Erst Prüfung, bei Warnungen ein Auto-Fix, danach Kontrolllauf.
  # Output: 0 wenn Abschluss ohne Warn-Exitcode möglich, 1 bei weiterhin rotem Ergebnis.
  local quality_log_path="${1:-exports/quality_report.txt}"

  if bash tools/run_quality_checks.sh > "$quality_log_path" 2>&1; then
    echo "[OK] Qualitätsprüfung ohne Warn-Exitcode abgeschlossen."
    return 0
  fi

  echo "[WARN] Qualitätsprüfung meldet Warnungen. Starte genau einen Auto-Fix-Lauf." | tee -a "$SETUP_LOG"
  if AUTO_FIX=1 bash tools/run_quality_checks.sh >> "$quality_log_path" 2>&1; then
    echo "[OK] Auto-Fix-Lauf abgeschlossen. Starte Kontrolllauf." | tee -a "$SETUP_LOG"
  else
    echo "[WARN] Auto-Fix-Lauf konnte nicht alles reparieren. Kontrolllauf folgt trotzdem." | tee -a "$SETUP_LOG"
  fi

  if bash tools/run_quality_checks.sh >> "$quality_log_path" 2>&1; then
    echo "[OK] Kontrolllauf nach Auto-Fix ist grün." | tee -a "$SETUP_LOG"
    return 0
  fi

  echo "[WARN] Qualitätswarnungen bleiben nach Auto-Fix bestehen." | tee -a "$SETUP_LOG"
  echo "[HILFE] Nächster Schritt: quality_report lesen, erste Warnung beheben, dann bash start.sh erneut starten." | tee -a "$SETUP_LOG"
  return 1
}

DEBUG_LOG_MODE="$(normalize_binary_runtime_flag "${DEBUG_LOG_MODE:-0}" "DEBUG_LOG_MODE")"
export DEBUG_LOG_MODE
ENABLE_AUTO_FORMAT="$(normalize_enable_auto_format_flag "${ENABLE_AUTO_FORMAT:-1}")"
export ENABLE_AUTO_FORMAT

echo "[START] Provoware Clean Tool 2026 – Auto-Setup"
log_debug "Debug-Modus aktiv. Zusätzliche Details werden in $SETUP_LOG protokolliert."
echo "=== START $(date -Is) ===" >> "$SETUP_LOG"

if ! run_preflight_health_checks; then
  python3 tools/boot_error_gui.py "Pflichtdateien für den Start fehlen.

Lösung:
- Fehlende Dateien aus dem Repository wiederherstellen.
- Danach erneut starten: bash start.sh

Details: exports/setup_log.txt" "Vorprüfung fehlgeschlagen"
  exit 1
fi

if ! ensure_tool_workdir; then
  python3 tools/boot_error_gui.py "Der Standard-Arbeitsordner konnte nicht korrekt vorbereitet werden.

Lösung:
- Prüfe Linux-Rechte im Nutzerpfad (~/.local/share).
- Falls nötig: chmod u+rwx ~/.local/share
- Danach erneut starten: bash start.sh

Details: exports/setup_log.txt" "Arbeitsordner-Problem"
  exit 1
fi

# 1) venv sicher erstellen
if [ ! -d "venv" ]; then
  echo "[SETUP] Erstelle virtuelle Umgebung (venv/)"
  if ! python3 -m venv venv >>"$SETUP_LOG" 2>&1; then
    echo "[WARN] Konnte keine virtuelle Umgebung erstellen. Starte Auto-Reparatur für python3-venv." | tee -a "$SETUP_LOG"
    if try_install_python_venv && python3 -m venv venv >>"$SETUP_LOG" 2>&1; then
      echo "[OK] Auto-Reparatur erfolgreich: virtuelle Umgebung wurde erstellt." | tee -a "$SETUP_LOG"
    else
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
fi

VENV_PY="$PROJECT_DIR/venv/bin/python"
VENV_PIP="$PROJECT_DIR/venv/bin/pip"

if sync_settings_workdir; then
  echo "[OK] Einstellungen auf Arbeitsordner synchronisiert: $TOOL_WORKDIR" | tee -a "$SETUP_LOG"
else
  echo "[WARN] Einstellungen konnten nicht synchronisiert werden. Nächster Schritt: start.sh erneut starten." | tee -a "$SETUP_LOG"
fi

echo "[SETUP] Aktualisiere pip (wenn möglich)"
"$VENV_PIP" install --upgrade pip >>"$SETUP_LOG" 2>&1 || true

# 2) Abhängigkeiten robust installieren + Konflikte automatisch prüfen
echo "[SETUP] Installiere Abhängigkeiten (vollautomatisch, mit Status und Konfliktprüfung)"
log_debug "Verwendeter Python-Interpreter: $VENV_PY"
OFFLINE_WHEELS_DIR="$PROJECT_DIR/offline_wheels"
REQ_SANITIZED="$PROJECT_DIR/exports/requirements.sanitized.txt"
> "$REQ_SANITIZED"
INSTALL_ERRORS=0
INSTALL_OK=0
INSTALL_SKIPPED=0
INSTALL_SOURCE_OFFLINE=0
INSTALL_SOURCE_ONLINE=0
INSTALL_CONFLICTS=0
AUTOREPAIR_STATUS="nicht nötig"
AUTOREPAIR_ICON="ℹ️"
AUTOREPAIR_MESSAGE="Es war keine automatische Reparatur nötig."

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

MISSING_MODULES_RAW="$(collect_missing_python_modules "requirements.txt" "$VENV_PY" || true)"
if [ -n "$MISSING_MODULES_RAW" ]; then
  AUTOREPAIR_STATUS="läuft"
  AUTOREPAIR_ICON="🔧"
  AUTOREPAIR_MESSAGE="Automatische Reparatur für fehlende Module wurde gestartet."
  echo "[WARN] Fehlende Python-Module erkannt. Starte automatische Reparatur." | tee -a "$SETUP_LOG"
  while IFS= read -r missing_req || [ -n "$missing_req" ]; do
    [ -z "$missing_req" ] && continue
    import_name="$(requirement_to_import_name "$missing_req")"
    echo "[SETUP] Auto-Reparatur fehlendes Modul: $missing_req (Import: $import_name)" | tee -a "$SETUP_LOG"
    if "$VENV_PIP" install --upgrade --no-cache-dir "$missing_req" >>"$SETUP_LOG" 2>&1; then
      if "$VENV_PY" -c "import importlib; importlib.import_module('$import_name')" >>"$SETUP_LOG" 2>&1; then
        echo "[OK] Modul-Reparatur erfolgreich: $missing_req" | tee -a "$SETUP_LOG"
      else
        echo "[WARN] Modul installiert, Import weiter fehlgeschlagen: $missing_req" | tee -a "$SETUP_LOG"
        INSTALL_ERRORS=$((INSTALL_ERRORS + 1))
      fi
    else
      echo "[WARN] Modul-Reparatur fehlgeschlagen: $missing_req" | tee -a "$SETUP_LOG"
      INSTALL_ERRORS=$((INSTALL_ERRORS + 1))
    fi
  done <<< "$MISSING_MODULES_RAW"
  if print_module_repair_status_block "$MISSING_MODULES_RAW"; then
    echo "[OK] Modul-Reparaturblock: alle fehlenden Module sind jetzt importierbar." | tee -a "$SETUP_LOG"
  else
    echo "[WARN] Modul-Reparaturblock zeigt noch offene Imports. Siehe Hilfeschritte oben." | tee -a "$SETUP_LOG"
    INSTALL_ERRORS=$((INSTALL_ERRORS + 1))
  fi
fi

if ! "$VENV_PIP" check >>"$SETUP_LOG" 2>&1; then
  INSTALL_CONFLICTS=1
  AUTOREPAIR_STATUS="läuft"
  AUTOREPAIR_ICON="🔧"
  AUTOREPAIR_MESSAGE="Automatische Reparatur wurde gestartet."
  echo "[WARN] Versionskonflikt erkannt. Starte automatische Reparatur (Upgrade nach requirements)."
  if [ -s "$REQ_SANITIZED" ]; then
    if [ -d "$OFFLINE_WHEELS_DIR" ]; then
      "$VENV_PIP" install --upgrade --no-index --find-links "$OFFLINE_WHEELS_DIR" -r "$REQ_SANITIZED" >>"$SETUP_LOG" 2>&1 || true
    fi
    "$VENV_PIP" install --upgrade --upgrade-strategy eager --no-cache-dir -r "$REQ_SANITIZED" >>"$SETUP_LOG" 2>&1 || true
  fi
  if "$VENV_PIP" check >>"$SETUP_LOG" 2>&1; then
    INSTALL_CONFLICTS=0
    AUTOREPAIR_STATUS="erfolgreich"
    AUTOREPAIR_ICON="✅"
    AUTOREPAIR_MESSAGE="Automatische Reparatur erfolgreich abgeschlossen."
    echo "[OK] Konflikte wurden automatisch behoben."
  else
    AUTOREPAIR_STATUS="nicht möglich"
    AUTOREPAIR_ICON="⚠️"
    AUTOREPAIR_MESSAGE="Automatische Reparatur war nicht möglich. Bitte die Hilfe-Schritte unten ausführen."
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
echo "[SETUP] - Auto-Reparatur-Status: $AUTOREPAIR_STATUS"
echo "[STATUS] $AUTOREPAIR_ICON $AUTOREPAIR_MESSAGE"

if [ "$AUTOREPAIR_STATUS" = "läuft" ]; then
  if [ "$INSTALL_ERRORS" -eq 0 ] && [ "$INSTALL_CONFLICTS" -eq 0 ]; then
    AUTOREPAIR_STATUS="erfolgreich"
    AUTOREPAIR_ICON="✅"
    AUTOREPAIR_MESSAGE="Automatische Reparatur für fehlende Module/Konflikte erfolgreich abgeschlossen."
  else
    AUTOREPAIR_STATUS="nicht möglich"
    AUTOREPAIR_ICON="⚠️"
    AUTOREPAIR_MESSAGE="Automatische Reparatur war nicht möglich. Bitte die Hilfeschritte ausführen."
  fi
fi

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

# 3) Optionalen Ausbau prüfen (Web-Frontend + AppImage)
normalize_optional_status() {
  # Validiert den Status optionaler Checks und liefert nur OK oder WARN.
  local raw_value="${1:-WARN}"
  if [ "$raw_value" = "OK" ] || [ "$raw_value" = "WARN" ]; then
    printf '%s' "$raw_value"
    return 0
  fi
  printf '%s' "WARN"
  return 1
}

check_optional_toolchain() {
  local feature_name="$1"
  local check_cmd="$2"
  local install_hint="$3"
  local success_hint="$4"

  if [ -z "$feature_name" ] || [ -z "$check_cmd" ] || [ -z "$install_hint" ] || [ -z "$success_hint" ]; then
    echo "[WARN] Optional-Check wurde übersprungen: unvollständige Eingaben." | tee -a "$SETUP_LOG"
    echo "[HILFE] Nächster Schritt: start.sh unverändert nutzen oder den Optional-Check mit allen Parametern aufrufen." | tee -a "$SETUP_LOG"
    return 1
  fi

  if [[ "$install_hint" != *" "* ]]; then
    echo "[WARN] Optional-Check '$feature_name' hat keinen klaren Befehl als Install-Hinweis." | tee -a "$SETUP_LOG"
    echo "[HILFE] Nächster Schritt: Install-Hinweis mit vollständigem Befehl ergänzen (z. B. python3 -m pip install ...)." | tee -a "$SETUP_LOG"
    return 1
  fi

  echo "[CHECK][OPTIONAL] Prüfe Ausbaupfad: $feature_name"
  log_debug "Optional-Check-Befehl für '$feature_name': $check_cmd"
  if bash -lc "$check_cmd" >/dev/null 2>&1; then
    echo "[OK][OPTIONAL] $feature_name ist bereit."
    echo "[HILFE][OPTIONAL] $success_hint"
    return 0
  fi

  echo "[WARN][OPTIONAL] $feature_name ist noch nicht eingerichtet."
  echo "[HILFE][OPTIONAL] Nächster Schritt: $install_hint"
  echo "[HILFE][OPTIONAL] Danach zur Kontrolle erneut starten: bash start.sh"
  return 1
}

print_optional_quickfix_block() {
  # Zeigt bei optionalen Warnungen eine einheitliche Hilfe mit klarer Reihenfolge.
  local web_status_input="${1:-WARN}"
  local appimage_status_input="${2:-WARN}"
  local web_status
  local appimage_status
  web_status="$(normalize_optional_status "$web_status_input")"
  appimage_status="$(normalize_optional_status "$appimage_status_input")"

  echo "[OPTIONAL] ===== Kurzbericht Optional-Checks ====="
  echo "[OPTIONAL] Web-Frontend: $web_status | AppImage: $appimage_status"

  if [ "$web_status" = "WARN" ] || [ "$appimage_status" = "WARN" ]; then
    echo "[OPTIONAL] Nächster Schritt 1: Protokoll prüfen: cat exports/setup_log.txt"
    echo "[OPTIONAL] Nächster Schritt 2: Optionales Ziel auswählen und nur diesen Bereich installieren."
    echo "[OPTIONAL] Nächster Schritt 3: Erneut prüfen mit: bash start.sh"
  else
    echo "[OPTIONAL] Beide optionalen Ausbaupfade sind bereit."
  fi
}

WEB_OPTIONAL_STATUS="WARN"
APPIMAGE_OPTIONAL_STATUS="WARN"

if check_optional_toolchain \
  "Web-Frontend (Flask/FastAPI + Build-Werkzeuge)" \
  "command -v python3 >/dev/null && python3 -m pip --version >/dev/null" \
  "python3 -m pip install flask fastapi uvicorn" \
  "Sie können als nächsten Mini-Schritt eine API in app/web_api.py anlegen und danach mit uvicorn lokal starten."; then
  WEB_OPTIONAL_STATUS="OK"
fi

if check_optional_toolchain \
  "AppImage-Build (linuxdeploy + appimagetool)" \
  "test -x tools/appimage/appimagetool-x86_64.AppImage || test -x tools/appimage/linuxdeploy-x86_64.AppImage || command -v appimagetool >/dev/null || command -v linuxdeploy >/dev/null" \
  "python3 tools/release_gap_report.py --auto-fix-appimage && python3 tools/release_gap_report.py --appimage-only" \
  "Auto-Fix verfügbar: python3 tools/release_gap_report.py --auto-fix-appimage. Danach zeigt --appimage-only den klaren JA/NEIN-Status."; then
  APPIMAGE_OPTIONAL_STATUS="OK"
fi

WEB_OPTIONAL_STATUS="$(normalize_optional_status "$WEB_OPTIONAL_STATUS")"
APPIMAGE_OPTIONAL_STATUS="$(normalize_optional_status "$APPIMAGE_OPTIONAL_STATUS")"

echo "[STATUS][OPTIONAL] Web-Frontend-Bereitschaft: $WEB_OPTIONAL_STATUS"
echo "[STATUS][OPTIONAL] AppImage-Bereitschaft: $APPIMAGE_OPTIONAL_STATUS"
print_optional_quickfix_block "$WEB_OPTIONAL_STATUS" "$APPIMAGE_OPTIONAL_STATUS"

# 4) Kritische Imports prüfen (ohne Crash)
echo "[CHECK] Prüfe kritische Module"
check_missing_python_modules() {
  "$VENV_PY" - <<'PY'
import importlib

required_modules = ("PySide6", "PIL")
missing_modules = []

for module_name in required_modules:
    try:
        importlib.import_module(module_name)
    except Exception:
        missing_modules.append(module_name)

print(",".join(missing_modules))
PY
}

MISSING="$(check_missing_python_modules)"
if [ -n "$MISSING" ]; then
  echo "[CHECK] Fehlende Module erkannt: $MISSING"
  echo "[SETUP] Versuche automatische Reparatur über apt (Ubuntu/Kubuntu)"
  APT_PACKAGES=()
  [[ ",$MISSING," == *",PySide6,"* ]] && APT_PACKAGES+=("python3-pyside6")
  [[ ",$MISSING," == *",PIL,"* ]] && APT_PACKAGES+=("python3-pil")

  if command -v apt-get >/dev/null 2>&1 && [ "${#APT_PACKAGES[@]}" -gt 0 ]; then
    echo "[SETUP] Installiere Systempakete: ${APT_PACKAGES[*]}"
    if run_with_sudo "apt-get update" apt-get update >>"$SETUP_LOG" 2>&1 && run_with_sudo "apt-get install ${APT_PACKAGES[*]}" apt-get install -y "${APT_PACKAGES[@]}" >>"$SETUP_LOG" 2>&1; then
      MISSING="$(check_missing_python_modules)"
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

# 5) Qualitätsprüfung (ohne den Nutzer zu verwirren)
echo "[CHECK] Führe Qualitätsprüfung aus"
QUALITY_STATUS="OK"
QUALITY_ICON="✅"
QUALITY_HINT="Keine Aktion nötig."
if ! run_gate_compileall; then
  QUALITY_STATUS="WARN"
  QUALITY_ICON="⚠️"
  QUALITY_HINT="Syntaxprüfung fehlgeschlagen: zuerst compileall-Fehler beheben und danach erneut starten."
fi
run_auto_format_step "$ENABLE_AUTO_FORMAT" || true
if ! run_a11y_theme_gate "$QUALITY_LOG"; then
  QUALITY_STATUS="WARN"
  QUALITY_ICON="⚠️"
  QUALITY_HINT="Bitte zuerst den A11y-Theme-Check prüfen und die erste Warnung beheben."
fi
if ! run_quality_with_autofix "$QUALITY_LOG"; then
  log_debug "Qualitätsprüfung meldet Warnung. Öffne Details in $QUALITY_LOG."
  QUALITY_STATUS="WARN"
  QUALITY_ICON="⚠️"
  QUALITY_HINT="Bitte zuerst die erste Warnung beheben, dann Qualitätslauf erneut starten und danach erneut starten."
  echo "[WARN] Qualitätsprüfung meldet etwas. Tool versucht trotzdem zu starten."
  python3 tools/quality_gate_gui.py || true
fi

if ! run_mini_ux_gate; then
  QUALITY_STATUS="WARN"
  QUALITY_ICON="⚠️"
  QUALITY_HINT="Mini-UX-Gate meldet Hinweise: zuerst die erste Warnung im UX-Check beheben und danach erneut starten."
fi

QUALITY_WARN_COUNT="$(extract_quality_count "\[QUALITY\]\[WARN\]" "$QUALITY_LOG")"
QUALITY_INFO_COUNT="$(extract_quality_count "\[QUALITY\]\[INFO\]" "$QUALITY_LOG")"
if [ "$QUALITY_WARN_COUNT" -gt 0 ]; then
  QUALITY_HINT="Warnungen gefunden: Öffnen Sie den Qualitätsbericht und beheben Sie zuerst die erste Warnung. Danach erneut starten."
elif [ "$QUALITY_INFO_COUNT" -gt 0 ]; then
  QUALITY_HINT="Nur Hinweise gefunden: Sie können starten. Für bessere Stabilität Hinweise später nacheinander umsetzen."
else
  QUALITY_HINT="Keine Aktion nötig."
fi
echo "[STATUS] $QUALITY_ICON Qualitäts-Gate: $QUALITY_STATUS"
echo "[STATUS] Hinweise: WARN=$QUALITY_WARN_COUNT, INFO=$QUALITY_INFO_COUNT"
echo "[HILFE] Nächster Schritt: $QUALITY_HINT"
echo "[HILFE] Log-Datei: $QUALITY_LOG"

if [ -f "tools/release_gap_report.py" ]; then
  if ! python3 tools/release_gap_report.py >>"$QUALITY_LOG" 2>&1; then
    echo "[WARN] Release-Report meldet noch offene oder widersprüchliche Punkte."
    echo "[HILFE] Nächster Schritt: python3 tools/release_gap_report.py"
  else
    echo "[STATUS] ✅ Release-Report: OK"
  fi

  if python3 tools/release_gap_report.py --appimage-only >>"$QUALITY_LOG" 2>&1; then
    echo "[STATUS] ✅ AppImage-Releasecheck: JA (Mindestpunkte erfüllt)"
  else
    echo "[WARN] AppImage-Releasecheck: NEIN"
    echo "[HILFE] Nächster Schritt: python3 tools/release_gap_report.py --appimage-only"
  fi
fi

# 6) Linux-Systembibliotheken prüfen (vor Smoke-Test)
check_and_repair_linux_lib() {
  local lib_name="$1"
  local apt_package="$2"
  local lib_label="$3"
  local lib_reason="$4"
  local dialog_title="$5"
  local install_now=0

  lib_is_available() {
    ldconfig -p 2>/dev/null | grep -q "$lib_name" && return 0
    [ -e "/usr/lib/$lib_name" ] && return 0
    [ -e "/usr/lib/x86_64-linux-gnu/$lib_name" ] && return 0
    [ -e "/lib/x86_64-linux-gnu/$lib_name" ] && return 0
    return 1
  }

  echo "[CHECK] Prüfe Linux-Systembibliothek: $lib_name"
  if lib_is_available; then
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
      if run_with_sudo "apt-get update" apt-get update >>"$SETUP_LOG" 2>&1 && run_with_sudo "apt-get install $apt_package" apt-get install -y "$apt_package" >>"$SETUP_LOG" 2>&1; then
        echo "[OK] $apt_package wurde installiert."
        run_with_sudo "ldconfig" ldconfig >>"$SETUP_LOG" 2>&1 || true
      else
        echo "[WARN] Automatische Installation von $apt_package fehlgeschlagen." >>"$SETUP_LOG"
      fi
    else
      echo "[WARN] apt-get nicht verfügbar. $apt_package konnte nicht automatisch installiert werden." >>"$SETUP_LOG"
    fi
  fi

  if lib_is_available; then
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

# 7) Smoke-Test mit venv python
echo "[CHECK] Starte Smoke-Test"
if [ ! -f "tools/smoke_test.py" ]; then
  echo "[ERROR] Smoke-Test-Datei fehlt: tools/smoke_test.py" | tee -a "$SETUP_LOG"
  python3 tools/boot_error_gui.py "Smoke-Test-Datei fehlt.

Lösung:
- Datei wiederherstellen: git restore tools/smoke_test.py
- Danach erneut starten: bash start.sh

Details: exports/setup_log.txt" "Smoke-Test-Datei fehlt"
  exit 1
fi

if ! "$VENV_PY" tools/smoke_test.py >>"$SETUP_LOG" 2>&1; then
  echo "[ERROR] Smoke-Test fehlgeschlagen"
  python3 tools/boot_error_gui.py "Smoke-Test fehlgeschlagen.

Lösung:
- start.sh erneut ausführen
- Wenn es wieder passiert: exports/setup_log.txt öffnen

Details: exports/setup_log.txt" "Smoke-Test"
  exit 1
fi

print_start_summary_for_humans "$OVERALL_STATUS" "$QUALITY_STATUS" "$AUTOREPAIR_STATUS" "$WEB_OPTIONAL_STATUS" "$APPIMAGE_OPTIONAL_STATUS" "$QUALITY_WARN_COUNT" "$QUALITY_INFO_COUNT" "$QUALITY_LOG"
print_accessibility_next_steps
if [ "$DEBUG_LOG_MODE" = "1" ]; then
  echo "[HILFE] Debug ist aktiv. Bei Problemen zuerst öffnen: cat exports/setup_log.txt"
fi

# 8) GUI starten
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
