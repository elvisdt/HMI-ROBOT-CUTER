from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QButtonGroup, QFrame, QToolButton, QVBoxLayout, 
                            QSizePolicy, QLabel, QProgressBar)

from PyQt6.QtCore import QSize


@dataclass
class SidebarAction:
    text: str
    icon: QIcon | None = None
    enabled: bool = True

class Sidebar(QFrame):
    """Vertical action bar for robot cutter HMI."""
    
    # Señales para las acciones del robot
    actionTriggered = pyqtSignal(str)
    loadDxfRequested = pyqtSignal()
    generatePathRequested = pyqtSignal()
    simulateRequested = pyqtSignal()
    exportRequested = pyqtSignal()

    def __init__(self, actions: Iterable[SidebarAction]) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(140)
        
        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QToolButton] = {}
        
        # Header
        header = QLabel("ROBOT CORTADOR")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; color: #5aa4db;")
        self._layout.addWidget(header)
        
        self._build_buttons(actions)
        
        # Progress bar para simulación
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self._layout.addWidget(self.progress_bar)
        
        self._layout.addStretch()
        self._apply_style()

    def _build_buttons(self, actions: Iterable[SidebarAction]) -> None:
        for index, action in enumerate(actions):
            button = QToolButton()
            button.setText(action.text)
            button.setCheckable(True)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            button.setMinimumSize(120, 80)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setEnabled(action.enabled)
            
            if action.icon is not None:
                button.setIcon(action.icon)
                button.setIconSize(QSize(32, 32))
            
            self._layout.addWidget(button)
            self._group.addButton(button)
            self._buttons[action.text] = button
            button.toggled.connect(self._make_toggle_handler(action.text))
            
            if index == 0:
                button.setChecked(True)

    def _apply_style(self) -> None:
        self.setStyleSheet("""
            #sidebar {
                background-color: #1a1a1a;
                color: #f0f0f0;
                border-right: 1px solid #333;
            }
            #sidebar QToolButton {
                border: 2px solid #245983;
                padding: 8px 4px;
                font-size: 11px;
                background-color: transparent;
                border-radius: 6px;
                margin: 4px 6px;
                font-weight: 500;
                color: #d8dce2;
            }
            #sidebar QToolButton:checked {
                background-color: #2f6ba5;
                border-color: #5aa4db;
                color: white;
            }
            #sidebar QToolButton:hover:!checked {
                background-color: rgba(47,107,165,0.3);
            }
            #sidebar QToolButton:disabled {
                border-color: #555;
                color: #777;
            }
        """)

    def _make_toggle_handler(self, name: str):
        def handler(checked: bool) -> None:
            if checked:
                self.actionTriggered.emit(name)
                # Emitir señales específicas
                if name == "Cargar DXF":
                    self.loadDxfRequested.emit()
                elif name == "Generar Trayectoria":
                    self.generatePathRequested.emit()
                elif name == "Simular Corte":
                    self.simulateRequested.emit()
                elif name == "Exportar":
                    self.exportRequested.emit()
        return handler

    def trigger_action(self, name: str) -> None:
        """Programmatically activate a sidebar button."""
        button = self._buttons.get(name)
        if button is not None and button.isEnabled():
            button.setChecked(True)

    def set_action_enabled(self, name: str, enabled: bool) -> None:
        """Habilitar/deshabilitar acción específica."""
        button = self._buttons.get(name)
        if button:
            button.setEnabled(enabled)

    def show_progress(self, visible: bool) -> None:
        """Mostrar/ocultar barra de progreso."""
        self.progress_bar.setVisible(visible)

    def set_progress(self, value: int) -> None:
        """Establecer valor de progreso."""
        self.progress_bar.setValue(value)