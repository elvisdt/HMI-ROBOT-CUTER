from __future__ import annotations

from typing import Iterable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ..data import ShapeParameter


class PropertiesPanel(QFrame):
    """Parameter editor for the selected shape."""

    parameterChanged = pyqtSignal(str, float)
    parametersCommitted = pyqtSignal(dict)
    deleteRequested = pyqtSignal()
    patternRequested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("propertiesPanel")
        self.setMinimumWidth(220)
        self._title = QLabel("Edit Closed Shape")
        self._title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self._side_selector = QComboBox()
        self._side_selector.addItems(["Inside", "Outside"])
        self._form = QFormLayout()
        self._form.setSpacing(10)
        self._form.setHorizontalSpacing(18)
        self._form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self._form.setContentsMargins(0, 0, 0, 0)
        self._delete_btn = QPushButton("Delete")
        self._delete_btn.setObjectName("deleteBtn")
        self._pattern_btn = QPushButton("Pattern")
        self._pattern_btn.setObjectName("patternBtn")
        self._done_btn = QPushButton("Done")
        self._done_btn.setObjectName("doneBtn")

        self._editors: dict[str, QDoubleSpinBox] = {}
        self._current_values: dict[str, float] = {}

        self._build_layout()
        self._apply_style()
        self.update_parameters(
            [
                ShapeParameter("rotation", "Rotation (°)", 0.0, -180, 180),
                ShapeParameter("scale", "Scale", 1.0, 0.1, 5.0),
                ShapeParameter("x_move", "X Move", 0.0, -500, 500),
                ShapeParameter("y_move", "Y Move", 0.0, -500, 500),
            ]
        )

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(self._title)

        layout.addSpacing(10)
        side_row = QFormLayout()
        side_row.addRow("Side", self._side_selector)
        layout.addLayout(side_row)
        layout.addSpacing(4)
        layout.addLayout(self._form)

        layout.addStretch()
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(10)
        button_row.addWidget(self._delete_btn)
        button_row.addWidget(self._pattern_btn)
        button_row.addStretch()
        button_row.addWidget(self._done_btn)
        layout.addLayout(button_row)

        self._delete_btn.clicked.connect(self.deleteRequested.emit)
        self._pattern_btn.clicked.connect(self.patternRequested.emit)
        self._done_btn.clicked.connect(self._emit_commit)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            #propertiesPanel {
                background-color: #202020;
                color: #f2f2f2;
            }
            #propertiesPanel QDoubleSpinBox,
            #propertiesPanel QComboBox {
                background-color: #2a2a2a;
                border: 1px solid #3e3e3e;
                padding: 4px 6px;
            }
            #propertiesPanel QPushButton {
                border: 1px solid #3e3e3e;
                padding: 8px 14px;
                border-radius: 4px;
                background-color: #2a2a2a;
            }
            #propertiesPanel QPushButton:hover {
                background-color: #3a3a3a;
            }
            #propertiesPanel #deleteBtn {
                border-color: #8b1a1a;
                background-color: #5a1a1a;
            }
            #propertiesPanel #deleteBtn:hover {
                background-color: #7a2020;
            }
            #propertiesPanel #doneBtn {
                border-color: #256c9e;
                background-color: #1f4d7a;
            }
            #propertiesPanel #doneBtn:hover {
                background-color: #296194;
            }
            #propertiesPanel QLabel {
                font-size: 12px;
                color: #dddddd;
            }
            """
        )

    def update_parameters(self, params: Iterable[ShapeParameter]) -> None:
        """Rebuild the editor form using the provided parameter descriptors."""
        # Clear current rows
        while self._form.rowCount():
            self._form.removeRow(0)

        self._editors.clear()
        self._current_values = {param.key: param.value for param in params}

        for param in params:
            editor = QDoubleSpinBox()
            editor.setRange(param.minimum, param.maximum)
            editor.setValue(param.value)
            editor.setDecimals(2)
            editor.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
            editor.setAlignment(Qt.AlignmentFlag.AlignRight)
            self._form.addRow(param.label, editor)

            editor.valueChanged.connect(self._make_value_changed_handler(param.key))
            self._editors[param.key] = editor

    # ------------------------------------------------------------------ Slots
    def _make_value_changed_handler(self, key: str):
        def handler(value: float) -> None:
            self._current_values[key] = value
            self.parameterChanged.emit(key, value)

        return handler

    def _emit_commit(self) -> None:
        self.parametersCommitted.emit(dict(self._current_values))

    def set_parameter_values(self, values: dict[str, float]) -> None:
        """Synchronize the editor widgets with external state."""
        for key, value in values.items():
            editor = self._editors.get(key)
            if editor is None:
                continue
            editor.blockSignals(True)
            editor.setValue(value)
            editor.blockSignals(False)
            self._current_values[key] = value
