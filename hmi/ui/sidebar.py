from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QButtonGroup, QFrame, QToolButton, QVBoxLayout, QSizePolicy


@dataclass
class SidebarAction:
    text: str
    icon: QIcon | None = None


class Sidebar(QFrame):
    """Vertical action bar with large buttons."""

    actionTriggered = pyqtSignal(str)

    def __init__(self, actions: Iterable[SidebarAction]) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(120)
        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QToolButton] = {}
        self._build_buttons(actions)
        self._apply_style()

    def _build_buttons(self, actions: Iterable[SidebarAction]) -> None:
        for index, action in enumerate(actions):
            button = QToolButton()
            button.setText(action.text)
            button.setCheckable(True)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            button.setMinimumSize(100, 90)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            if action.icon is not None:
                button.setIcon(action.icon)
            self._layout.addWidget(button)
            self._group.addButton(button)
            self._buttons[action.text] = button
            button.toggled.connect(self._make_toggle_handler(action.text))
            if index == 0:
                button.setChecked(True)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            #sidebar {
                background-color: #151515;
                color: #f0f0f0;
            }
            #sidebar QToolButton {
                border: 2px solid #245983;
                padding: 12px 4px;
                font-size: 12px;
                background-color: transparent;
                border-radius: 8px;
                margin: 6px 8px;
                font-weight: 600;
                color: #d8dce2;
            }
            #sidebar QToolButton:checked {
                background-color: #2f6ba5;
                border-color: #5aa4db;
                color: white;
            }
            #sidebar QToolButton:hover {
                background-color: rgba(47,107,165,0.25);
            }
            #sidebar QToolButton::menu-indicator {
                image: none;
            }
            """
        )

    def _make_toggle_handler(self, name: str):
        def handler(checked: bool) -> None:
            if checked:
                self.actionTriggered.emit(name)

        return handler

    def trigger_action(self, name: str) -> None:
        """Programmatically activate a sidebar button."""
        button = self._buttons.get(name)
        if button is not None:
            button.setChecked(True)
