from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPen, QFont
from PyQt6.QtWidgets import QFrame, QGraphicsItemGroup, QGraphicsScene, QGraphicsView


class CanvasScene(QGraphicsScene):
    """Scene that renders a machining bed grid and sample geometry."""

    def __init__(self, width: float = 900, height: float = 620, grid: float = 25.0) -> None:
        half_w = width / 2
        half_h = height / 2
        super().__init__(-half_w, -half_h, width, height)
        self.grid = grid
        self.major_step = 5
        self.major_grid = self.grid * self.major_step
        self.setBackgroundBrush(QColor("#090909"))
        self.shape_group: QGraphicsItemGroup | None = None
        self._shape_origin = QPointF()
        self._add_sample_geometry()

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:  # noqa: N802
        """Draw grid lines for the canvas."""
        super().drawBackground(painter, rect)

        painter.save()
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(20, 20, 20))
        gradient.setColorAt(0.5, QColor(12, 12, 12))
        gradient.setColorAt(1.0, QColor(6, 6, 6))
        painter.fillRect(rect, gradient)
        painter.restore()

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        minor_pen = QPen(QColor(45, 45, 45))
        minor_pen.setWidth(1)
        major_pen = QPen(QColor(70, 70, 70))
        major_pen.setWidth(2)

        v_start = int(math.floor(rect.left() / self.grid))
        v_end = int(math.ceil(rect.right() / self.grid))
        for i in range(v_start, v_end + 1):
            x = i * self.grid
            painter.setPen(major_pen if i % self.major_step == 0 else minor_pen)
            painter.drawLine(x, rect.top(), x, rect.bottom())

        h_start = int(math.floor(rect.top() / self.grid))
        h_end = int(math.ceil(rect.bottom() / self.grid))
        for j in range(h_start, h_end + 1):
            y = j * self.grid
            painter.setPen(major_pen if j % self.major_step == 0 else minor_pen)
            painter.drawLine(rect.left(), y, rect.right(), y)
        painter.restore()

        painter.save()
        axis_pen = QPen(QColor("#17a589"))
        axis_pen.setWidth(2)
        painter.setPen(axis_pen)
        painter.drawLine(rect.left(), 0, rect.right(), 0)  # X axis
        axis_pen.setColor(QColor("#c0392b"))
        painter.setPen(axis_pen)
        painter.drawLine(0, rect.top(), 0, rect.bottom())  # Y axis
        painter.setBrush(QColor("#f4d03f"))
        painter.drawEllipse(QPointF(0, 0), 4, 4)
        painter.restore()

        painter.save()
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QColor("#8c9399"))

        for i in range(v_start, v_end + 1):
            if i == 0 or i % self.major_step != 0:
                continue
            x = i * self.grid
            painter.drawText(
                QRectF(x - 30, -18, 60, 16),
                Qt.AlignmentFlag.AlignCenter,
                f"{int(x)}",
            )

        for j in range(h_start, h_end + 1):
            if j == 0 or j % self.major_step != 0:
                continue
            y = j * self.grid
            painter.drawText(
                QRectF(-54, y - 8, 48, 16),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                f"{int(-y)}",
            )

        painter.drawText(
            QRectF(rect.right() - 70, rect.top() + 8, 60, 16),
            Qt.AlignmentFlag.AlignRight,
            "units: mm",
        )
        painter.restore()

    def _add_sample_geometry(self) -> None:
        """Populate scene with sample shape placeholders."""
        plate_pen = QPen(QColor("#3c7dd9"))
        plate_pen.setWidth(2)
        items = []
        plate = self.addRect(-150, -150, 300, 300, plate_pen, QColor(255, 215, 0, 40))
        items.append(plate)

        hole_pen = QPen(QColor("#f1c40f"))
        hole_pen.setWidth(2)
        for offset in [(-110, -110), (70, -110), (-110, 70), (70, 70)]:
            items.append(self.addEllipse(offset[0], offset[1], 40, 40, hole_pen))

        items.append(self.addEllipse(-80, -80, 160, 160, hole_pen))

        path_pen = QPen(QColor("#3498db"))
        path_pen.setWidth(3)
        cut_path = self.addPath(self._build_cut_path(), path_pen)
        cut_path.setZValue(1)
        items.append(cut_path)

        self.shape_group = self.createItemGroup(items)
        self._shape_origin = QPointF(0, 0)
        self.shape_group.setTransformOriginPoint(self._shape_origin)
        self.shape_group.setZValue(5)

    def _build_cut_path(self):
        from PyQt6.QtGui import QPainterPath

        path = QPainterPath(QPointF(-130, -130))
        path.lineTo(130, -130)
        path.lineTo(130, 130)
        path.lineTo(-130, 130)
        path.closeSubpath()
        return path

    # ------------------------------------------------------------------ API
    def update_shape_transform(
        self, *, rotation: float, scale: float, x_move: float, y_move: float
    ) -> None:
        if self.shape_group is None:
            return
        # Clamp scale softly to avoid collapsing geometry
        safe_scale = max(0.05, scale)
        self.shape_group.setRotation(rotation)
        self.shape_group.setScale(safe_scale)
        # Invert Y to follow CAD convention (positive up)
        self.shape_group.setPos(x_move, -y_move)

    def reset_shape_transform(self) -> None:
        if self.shape_group is None:
            return
        self.shape_group.setRotation(0)
        self.shape_group.setScale(1)
        self.shape_group.setPos(0, 0)


class CanvasView(QGraphicsView):
    """Graphics view configured for CAD-like interaction."""

    def __init__(self) -> None:
        super().__init__(CanvasScene())
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(
            """
            QGraphicsView {
                border: 1px solid #262626;
                border-radius: 12px;
                background-color: transparent;
            }
            """
        )
        self.setBackgroundBrush(Qt.GlobalColor.transparent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.centerOn(0, 0)
        self._shape_state = {"rotation": 0.0, "scale": 1.0, "x_move": 0.0, "y_move": 0.0}

    def wheelEvent(self, event):  # noqa: N802
        """Implement zoom using the mouse wheel."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)

    # ------------------------------------------------------------------ API
    def apply_parameter_change(self, key: str, value: float) -> None:
        if key not in self._shape_state:
            return
        self._shape_state[key] = value
        self._apply_state()

    def apply_parameter_set(self, state: dict) -> None:
        for key, value in state.items():
            if key in self._shape_state:
                self._shape_state[key] = value
        self._apply_state()

    def reset_shape(self) -> None:
        self._shape_state = {"rotation": 0.0, "scale": 1.0, "x_move": 0.0, "y_move": 0.0}
        self.scene().reset_shape_transform()

    def _apply_state(self) -> None:
        scene: CanvasScene = self.scene()
        scene.update_shape_transform(**self._shape_state)
