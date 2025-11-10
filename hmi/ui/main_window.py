from __future__ import annotations

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ..data import CutProgram, CutShape, ShapeParameter
from .bottom_nav import BottomNav, NavStep
from .canvas import CanvasView
from .properties_panel import PropertiesPanel
from .sidebar import Sidebar, SidebarAction


class MainWindow(QMainWindow):
    """Robot cutter HMI composed from modular UI widgets."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Robot Cutter HMI")
        self.resize(1400, 860)

        self.program = self._build_mock_program()

        self.sidebar = Sidebar(
            [
                SidebarAction("FILES"),
                SidebarAction("ADD"),
                SidebarAction("SAVE"),
                SidebarAction("CLEAR"),
                SidebarAction("P2P"),
            ]
        )
        self.canvas = CanvasView()
        self.properties = PropertiesPanel()
        self.bottom_nav = BottomNav(
            [
                NavStep("Design", "Shapes & Paths"),
                NavStep("Place", "Workspace"),
                NavStep("Materials", "Consumables"),
                NavStep("Run", "Execution"),
            ]
        )
        self._default_state = {"rotation": 0.0, "scale": 1.0, "x_move": 0.0, "y_move": 0.0}

        self._build_menu()
        self._build_ui()
        self._build_status_bar()
        self._load_program(self.program)
        self._connect_signals()

    def _build_menu(self) -> None:
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(QAction("New Program", self))
        file_menu.addAction(QAction("Open...", self))
        file_menu.addAction(QAction("Save", self))
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menu.addMenu("&View")
        view_menu.addAction(QAction("Toggle grid", self))
        view_menu.addAction(QAction("Reset zoom", self))

    def _build_ui(self) -> None:
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        workspace = QFrame()
        workspace_layout = QHBoxLayout(workspace)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)
        workspace_layout.addWidget(self.sidebar)

        canvas_container = QWidget()
        canvas_container.setObjectName("canvasContainer")
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(16, 16, 16, 16)
        canvas_layout.setSpacing(12)
        title = QLabel("Workspace")
        title.setStyleSheet("color: #dddddd; font-size: 18px; font-weight: bold;")
        canvas_layout.addWidget(title)

        info_bar = QFrame()
        info_bar.setObjectName("workspaceInfo")
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(12, 6, 12, 6)
        info_layout.setSpacing(18)
        grid_label = QLabel(f"Grid: {int(self.canvas.scene().grid)} mm")
        origin_label = QLabel("Origin: center (0, 0)")
        hint_label = QLabel("Wheel = zoom · Middle drag = pan")
        for label in (grid_label, origin_label, hint_label):
            label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
            info_layout.addWidget(label)
        info_layout.addStretch()
        canvas_layout.addWidget(info_bar)
        canvas_layout.addWidget(self.canvas, stretch=1)

        workspace_layout.addWidget(canvas_container, stretch=1)
        workspace_layout.addWidget(self.properties)

        central_layout.addWidget(workspace, stretch=1)
        central_layout.addWidget(self.bottom_nav, stretch=0)
        self.setCentralWidget(central)

        canvas_container.setStyleSheet(
            """
            #canvasContainer {
                background-color: #111213;
                border-left: 1px solid #1f1f1f;
            }
            #workspaceInfo {
                background-color: #1b1c1f;
                border: 1px solid #232427;
                border-radius: 6px;
            }
            """
        )

    def _build_status_bar(self) -> None:
        status = QStatusBar()
        status.showMessage("Ready")
        self.setStatusBar(status)

    def _connect_signals(self) -> None:
        self.sidebar.actionTriggered.connect(self._on_sidebar_action)
        self.properties.parameterChanged.connect(self._on_parameter_changed)
        self.properties.parametersCommitted.connect(self._on_parameters_committed)
        self.properties.deleteRequested.connect(self._on_delete_requested)
        self.properties.patternRequested.connect(self._on_pattern_requested)

    def _build_mock_program(self) -> CutProgram:
        part = CutShape(
            name="Base Plate",
            kind="plate",
            parameters=[
                ShapeParameter("rotation", "Rotation (°)", 0),
                ShapeParameter("scale", "Scale", 1),
                ShapeParameter("x_move", "X Move", 0),
                ShapeParameter("y_move", "Y Move", 0),
            ],
        )
        return CutProgram("Sample Plate", [part])

    def _load_program(self, program: CutProgram) -> None:
        if not program.shapes:
            return
        shape = program.shapes[0]
        self.properties.update_parameters(shape.parameters)
        state = {param.key: param.value for param in shape.parameters}
        self.canvas.apply_parameter_set(state)
        self.properties.set_parameter_values(state)

    # ------------------------------------------------------------------ Slots
    def _on_sidebar_action(self, name: str) -> None:
        self.statusBar().showMessage(f"{name.title()} action selected")
        if name == "CLEAR":
            self.properties.set_parameter_values(self._default_state)
            self.canvas.reset_shape()
            self.statusBar().showMessage("Workspace reset to origin")

    def _on_parameter_changed(self, key: str, value: float) -> None:
        self.canvas.apply_parameter_change(key, value)
        display_value = f"{value:.2f}" if key != "scale" else f"{value:.2f}x"
        self.statusBar().showMessage(f"{key.replace('_', ' ').title()} -> {display_value}")

    def _on_parameters_committed(self, values: dict) -> None:
        self.canvas.apply_parameter_set(values)
        self.properties.set_parameter_values(values)
        self.statusBar().showMessage("Parameters committed to workspace")

    def _on_delete_requested(self) -> None:
        self.statusBar().showMessage("Delete requested (placeholder action)")

    def _on_pattern_requested(self) -> None:
        self.statusBar().showMessage("Pattern generator coming soon")
