# Developer Manual

This document provides a high‑level overview of the internals of the Downloads Organizer application. Developers looking to extend or maintain the tool should read this document first.

## Application Flow

The entry point for the application is `app/main.py`. When run as a script via `python -m app.main`, it performs a simple self‑check (see `core/selfcheck.py`) and then instantiates a `MainWindow`. The GUI is built using PySide6 and uses a wizard‑style workflow implemented with a `QStackedWidget`.

### Wizard Pages

1. **Welcome & Folder Selection** – The user chooses the folder to scan (defaulting to the Downloads folder) and selects a theme. Pressing “Weiter” moves to the next page.
2. **Options** – Users choose a preset (Senior, Standard or Power) or customise filters. Filters control which file types are considered and set size and age thresholds. The duplicate detection mode (none, quick or safe) is also configured here. “Zurück” returns to the previous page and “Weiter” starts the scan.
3. **Scan & Plan** – The application scans the chosen folder using `core.scanner.scan_directory`. Duplicate detection is performed by `core.scanner.detect_duplicates`. A summary is displayed. The user can click “Plan anzeigen” to see details. “Weiter” builds an `ActionPlan` using `core.planner.build_plan`.
4. **Execute & Undo** – The final page shows the number of files that will be moved and the total size freed. Clicking “Ausführen” calls `core.executor.execute_move_plan` to move files to the trash directory. “Undo” calls `core.executor.undo_last` to restore files from the last action. “Fertig” closes the application.

## Core Modules

- **`core/settings.py`** – Defines a `Settings` dataclass and helper functions to load and save settings from JSON.
- **`core/scanner.py`** – Contains the logic for scanning directories, applying filters and detecting duplicates. The `scan_directory()` function yields dictionaries describing candidate files. The `detect_duplicates()` function groups files by (name, size) for quick mode or by checksum for safe mode.
- **`core/planner.py`** – Defines the `ActionPlan` and `PlanItem` classes. The `build_plan()` function uses scan results and duplicate groups to decide which files should be moved.
- **`core/executor.py`** – Implements `execute_move_plan()` to move files to the trash and `undo_last()` to restore files from the trash. A trash directory is created in the user’s Downloads folder under `.downloads_organizer_trash`.
- **`core/logger.py`** – Provides a simple logging setup that writes to `logs/app.log` and to the console.
- **`core/selfcheck.py`** – Performs a basic self‑check at startup, ensuring that required directories can be created and that the Python version is sufficient.

## Tools

The `tools/` folder contains helper scripts used by the start script and for diagnostics:

- **`run_quality_checks.sh`** – Runs a basic code compilation check on the `app` and `core` modules. It ensures that Python files compile without syntax errors. This script is invoked automatically by `start.sh` before the GUI is launched. If it fails, the application will not start.
- **`smoke_test.py`** – Performs a minimal smoke test by importing the GUI and core modules. It can be run during development to verify that the application starts without errors.
- **`boot_error_gui.py`**, **`quality_gate_gui.py`**, **`repair_center_gui.py`** – These simple PySide6 dialogs present user‑friendly information when errors occur during startup or quality checks. They allow the user to attempt repairs or view logs without needing to use the terminal.

## Running Locally

The `start.sh` script is the recommended way to run the application. It sets up a virtual environment in the project directory, installs dependencies from `requirements.txt`, runs a quality check and then starts the GUI. If something goes wrong, a friendly error dialog will appear with options to repair or view logs.

For development, you can bypass `start.sh` and simply run:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

## Contributing

Contributions are welcome! Please open issues or pull requests to suggest improvements or report bugs. When adding new features, remember to include them in the README and CHANGELOG and consider how they fit into the overall user experience for non‑technical users.
