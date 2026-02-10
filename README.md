# Downloads Organizer

This project provides a simple desktop application to clean up your `Downloads` folder safely. It is designed to be easy to use for people who are not experienced with computers. The application scans a chosen folder, identifies files that might be old, large or duplicated and moves them into a dedicated trash folder. You can review the plan before any files are moved and undo your last action if necessary.

## Features

- **One–Click Wizard** – A four‑step wizard guides you through selecting a folder, choosing a preset or custom cleaning options, reviewing the plan and executing it.
- **Presets** – Three preset profiles (`Senior`, `Standard` and `Power`) set sensible defaults for thresholds and safety levels. You can also customise file types, age and size limits.
- **Duplicate Detection** – The scanner can detect duplicate files based on file name and size. An optional safe mode uses checksums for more accurate detection.
- **Dry‑Run Plan** – Nothing is moved until you review the plan. The dry‑run shows how many files will be moved and how much space will be freed.
- **Undo** – After executing the plan, you can undo the last clean‑up action and restore files from the trash.
- **Theme Support** – Choose between light, dark, high‑contrast and extra‑large text themes to improve readability.
- **Self‑Check and Logs** – The application runs a self‑check on start and writes detailed logs to help diagnose problems. Quality checks ensure the code compiles before the GUI starts.

## Getting Started

1. Extract the zip archive to a folder of your choice.
2. Open a terminal in that folder and run:

   ```bash
   chmod +x start.sh
   ./start.sh
   ```

   This script creates a Python virtual environment, installs dependencies, runs a simple code quality check and starts the GUI.

3. When the application opens, follow the steps on screen. No command‑line knowledge is required.

## Directory Structure

- **app/** – GUI code and main entry point.
- **core/** – Logic for scanning, planning, executing and undoing file operations.
- **data/** – Default settings and preset profiles saved as JSON.
- **logs/** – Application log files (created automatically).
- **exports/** – Reports and exports created by the application (created automatically).
- **tools/** – Helper scripts for quality checks and repair dialogs.

## Known Limitations

This tool is intentionally simple and focuses on safety. It does not delete files permanently. The duplicate detection in quick mode relies on file name and size and may not detect all duplicates. Advanced filtering options (by extension, modification date, etc.) are limited to what is provided in the wizard.
