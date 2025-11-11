from __future__ import annotations

import sys
from typing import Sequence

from PyQt6.QtWidgets import QApplication

from .ui.main_window import MainWindow


def create_app(args: Sequence[str] | None = None) -> QApplication:
    """Return a configured QApplication instance."""
    argv = list(args) if args is not None else sys.argv
    app = QApplication(argv)
    app.setOrganizationName("RobotCut")
    app.setApplicationName("Robot Cutter HMI")
    return app


def run() -> None:
    """Entry point that creates the QApplication and shows the main window."""
    app = create_app()
    window = MainWindow()
    window.show()
    app.exec()
