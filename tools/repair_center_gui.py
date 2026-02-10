#!/usr/bin/env python3
"""Show a repair centre dialog for startup problems.

This dialog provides buttons to attempt common repairs, such as
installing dependencies or restarting the application. It is invoked
when the startup scripts detect an unrecoverable error.
"""

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QMessageBox,
)


def main() -> int:
    app = QApplication([])
    win = QWidget()
    win.setWindowTitle("Reparaturzentrum")
    layout = QVBoxLayout(win)
    message = QLabel(
        "Es sind Probleme beim Start des Programms aufgetreten. "
        "Sie können versuchen, die Abhängigkeiten zu installieren oder das Programm neu zu starten."
    )
    message.setWordWrap(True)
    layout.addWidget(message)

    btn_deps = QPushButton("Abhängigkeiten installieren")
    btn_restart = QPushButton("Erneut starten")
    btn_close = QPushButton("Schließen")
    layout.addWidget(btn_deps)
    layout.addWidget(btn_restart)
    layout.addWidget(btn_close)

    project_root = Path(__file__).resolve().parent.parent
    venv_path = project_root / "venv"

    def install_deps():
        # Attempt to install requirements using pip
        python_exe = venv_path / "bin" / "python3"
        if not python_exe.exists():
            python_exe = venv_path / "bin" / "python"
        reqs = project_root / "requirements.txt"
        if python_exe.exists() and reqs.exists():
            subprocess.run([str(python_exe), "-m", "pip", "install", "-r", str(reqs)])
            QMessageBox.information(win, "Fertig", "Abhängigkeiten wurden installiert.")
        else:
            QMessageBox.warning(win, "Fehler", "Python oder requirements.txt wurde nicht gefunden.")

    def restart():
        # Relaunch start.sh in a new subprocess
        start_script = project_root / "start.sh"
        if start_script.exists():
            subprocess.Popen(["bash", str(start_script)])
        win.close()

    btn_deps.clicked.connect(install_deps)
    btn_restart.clicked.connect(restart)
    btn_close.clicked.connect(win.close)
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
