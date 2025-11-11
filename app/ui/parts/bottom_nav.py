from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QWidget


@dataclass
class NavStep:
    title: str
    subtitle: str | None = None


class StepWidget(QFrame):
    """Small widget representing a single workflow step."""

    def __init__(self, step: NavStep) -> None:
        super().__init__()
        self.setObjectName("stepWidget")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        title = QLabel(step.title)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        if step.subtitle:
            subtitle = QLabel(step.subtitle)
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle.setStyleSheet("font-size: 10px; color: #bbbbbb;")
            layout.addWidget(subtitle)

        self.setStyleSheet(
            """
            #stepWidget {
                background-color: #1f1f1f;
                color: #f5f5f5;
                border-radius: 6px;
                border: 1px solid #2a2a2a;
            }
            #stepWidget:hover {
                background-color: #2c2c2c;
            }
            """
        )


class BottomNav(QFrame):
    """Workflow navigation bar similar to the reference UI."""

    def __init__(self, steps: Iterable[NavStep]) -> None:
        super().__init__()
        self.setObjectName("bottomNav")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        for step in steps:
            layout.addWidget(StepWidget(step))
        layout.addStretch()
        self._apply_style()

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            #bottomNav {
                background-color: #111111;
                border-top: 1px solid #303030;
            }
            """
        )
