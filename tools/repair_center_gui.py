#!/usr/bin/env python3
"""Show a repair centre dialog for startup problems.

This dialog provides buttons to attempt common repairs, such as
installing dependencies or restarting the application. It is invoked
when the startup scripts detect an unrecoverable error.
"""

import importlib.util
import subprocess
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    venv_path = project_root / "venv"

    def install_deps_with_feedback() -> bool:
        python_exe = venv_path / "bin" / "python3"
        if not python_exe.exists():
            python_exe = venv_path / "bin" / "python"
        reqs = project_root / "requirements.txt"
        if not (python_exe.exists() and reqs.exists()):
            return False
        completed = subprocess.run(
            [str(python_exe), "-m", "pip", "install", "-r", str(reqs)],
            check=False,
        )
        return completed.returncode == 0

    if importlib.util.find_spec("PySide6") is None:
        install_deps_with_feedback()

    if importlib.util.find_spec("PySide6") is None:
        message = (
            "PySide6 fehlt weiterhin.\n\n"
            "Nächster Schritt:\n"
            "1) Reparatur erneut starten\n"
            "2) Wenn es weiter fehlschlägt: Protokoll öffnen und Fehler melden"
        )
        zenity = subprocess.run(
            ["which", "zenity"],
            check=False,
            capture_output=True,
            text=True,
        )
        if zenity.returncode == 0:
            subprocess.run(
                [
                    "zenity",
                    "--error",
                    "--width=520",
                    "--title=Reparaturzentrum",
                    f"--text={message}",
                ],
                check=False,
            )
        else:
            print(message)
        return 1

    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QMessageBox,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    app = QApplication([])
    win = QWidget()
    win.setWindowTitle("Reparaturzentrum")
    layout = QVBoxLayout(win)
    message = QLabel(
        "Es sind Probleme beim Start des Programms aufgetreten. "
        "Sie können versuchen, die Abhängigkeiten zu installieren, das Programm neu zu starten "
        "oder das Protokoll zu öffnen."
    )
    message.setWordWrap(True)
    layout.addWidget(message)

    btn_deps = QPushButton("Abhängigkeiten installieren")
    btn_restart = QPushButton("Erneut starten")
    btn_log = QPushButton("Protokoll öffnen")
    btn_close = QPushButton("Schließen")
    layout.addWidget(btn_deps)
    layout.addWidget(btn_restart)
    layout.addWidget(btn_log)
    layout.addWidget(btn_close)

    def install_deps():
        if install_deps_with_feedback():
            QMessageBox.information(win, "Fertig", "Abhängigkeiten wurden installiert.")
        else:
            QMessageBox.warning(win, "Fehler", "Python oder requirements.txt wurde nicht gefunden.")

    def restart():
        start_script = project_root / "start.sh"
        if start_script.exists():
            subprocess.Popen(["bash", str(start_script)])
        win.close()

    def open_log():
        log_path = project_root / "logs" / "start.log"
        if log_path.exists():
            subprocess.Popen(["xdg-open", str(log_path)])
        else:
            QMessageBox.information(
                win,
                "Hinweis",
                "Kein Protokoll gefunden. Bitte starten Sie das Tool einmal über start.sh.",
            )

    btn_deps.clicked.connect(install_deps)
    btn_restart.clicked.connect(restart)
    btn_log.clicked.connect(open_log)
    btn_close.clicked.connect(win.close)
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
