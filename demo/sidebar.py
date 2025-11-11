from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (QButtonGroup, QFrame, QToolButton, QVBoxLayout, 
                            QSizePolicy, QLabel, QProgressBar, QGroupBox,
                            QDoubleSpinBox, QCheckBox, QComboBox, QScrollArea)

from PyQt6.QtWidgets import QWidget


@dataclass
class SidebarAction:
    text: str
    icon: QIcon | None = None
    enabled: bool = True

class Sidebar(QFrame):
    """Vertical action bar combining simple design with full workspace sections."""
    
    # Señales principales (tu diseño simple)
    actionTriggered = pyqtSignal(str)
    loadDxfRequested = pyqtSignal()
    generatePathRequested = pyqtSignal()
    simulateRequested = pyqtSignal()
    exportRequested = pyqtSignal()
    configRequested = pyqtSignal()
    
    # Señales de edición (workspace completo)
    scaleChanged = pyqtSignal(float)
    moveXChanged = pyqtSignal(float)
    moveYChanged = pyqtSignal(float)
    relationChanged = pyqtSignal(float)
    saveRequested = pyqtSignal()
    clearRequested = pyqtSignal()
    p2pRequested = pyqtSignal()
    runRequested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(300)
        
        # Scroll area para contenido largo
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.content_widget = QWidget()
        self._layout = QVBoxLayout(self.content_widget)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.setSpacing(12)
        self._layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll_area.setWidget(self.content_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area)
        
        self._build_header_section()
        self._build_main_actions_section()  # Tu diseño simple
        self._build_workspace_section()     # Sección workspace completa
        self._build_edit_section()          # Sección edición
        self._build_help_section()          # Sección ayuda/navegación
        
        self._apply_style()

    def _build_header_section(self):
        """Header with robot title"""
        header = QLabel("ROBOT CORTADOR")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            padding: 15px; 
            color: #5aa4db;
            background-color: #2a2a2a;
            border-radius: 8px;
            margin: 5px;
        """)
        header.setMinimumHeight(50)
        self._layout.addWidget(header)

    def _build_main_actions_section(self):
        """Tu diseño simple - acciones principales"""
        group = QGroupBox("ACCIONES PRINCIPALES")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Botones principales (tu diseño)
        main_actions = [
            ("Cargar DXF", "📁", self.loadDxfRequested),
            ("Generar Trayectoria", "🔄", self.generatePathRequested),
            ("Simular Corte", "🎬", self.simulateRequested),
            ("Exportar", "📤", self.exportRequested),
            ("Configuración", "⚙️", self.configRequested)
        ]
        
        self.main_buttons = {}
        
        for text, icon, signal in main_actions:
            btn = self._create_main_button(text, icon)
            btn.clicked.connect(signal.emit)
            layout.addWidget(btn)
            self.main_buttons[text] = btn
        
        self._layout.addWidget(group)

    def _build_workspace_section(self):
        """Workspace section - collapsed by default"""
        self.workspace_group = QGroupBox("WORKSPACE ▸")
        self.workspace_group.setCheckable(True)
        self.workspace_group.setChecked(False)  # Colapsado por defecto
        self.workspace_group.toggled.connect(self._on_workspace_toggled)
        
        layout = QVBoxLayout(self.workspace_group)
        
        # Files info
        files_label = QLabel("ARCHIVOS")
        files_label.setStyleSheet("font-weight: bold; color: #5aa4db; font-size: 12px;")
        layout.addWidget(files_label)
        
        self.files_info = QLabel("No hay archivos cargados")
        self.files_info.setStyleSheet("font-size: 11px; color: #cccccc;")
        layout.addWidget(self.files_info)
        
        # Dimensions
        dims_label = QLabel("Material: 25 mm\nOrigen: centro (0, 0)")
        dims_label.setStyleSheet("font-size: 11px; color: #cccccc;")
        layout.addWidget(dims_label)
        
        # Navigation info
        nav_label = QLabel("Rueda = zoom | Click medio = pan")
        nav_label.setStyleSheet("font-size: 10px; color: #888888; font-style: italic;")
        layout.addWidget(nav_label)
        
        # Quick actions
        quick_layout = QVBoxLayout()
        quick_layout.setSpacing(4)
        
        self.save_btn = self._create_small_button("GUARDAR", "💾")
        self.save_btn.clicked.connect(self.saveRequested.emit)
        quick_layout.addWidget(self.save_btn)
        
        self.clear_btn = self._create_small_button("LIMPIAR", "🗑️")
        self.clear_btn.clicked.connect(self.clearRequested.emit)
        quick_layout.addWidget(self.clear_btn)
        
        self.p2p_btn = self._create_small_button("PUNTO A PUNTO", "↔️")
        self.p2p_btn.clicked.connect(self.p2pRequested.emit)
        quick_layout.addWidget(self.p2p_btn)
        
        layout.addLayout(quick_layout)
        self._layout.addWidget(self.workspace_group)

    def _build_edit_section(self):
        """Edit section - collapsed by default"""
        self.edit_group = QGroupBox("EDITAR FORMA ▸")
        self.edit_group.setCheckable(True)
        self.edit_group.setChecked(False)
        
        layout = QVBoxLayout(self.edit_group)
        
        # Side/Inside selection
        side_layout = QVBoxLayout()
        side_label = QLabel("Lado de Corte")
        side_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        side_layout.addWidget(side_label)
        
        self.side_combo = QComboBox()
        self.side_combo.addItems(["Exterior", "Interior"])
        self.side_combo.setStyleSheet("font-size: 11px;")
        side_layout.addWidget(self.side_combo)
        layout.addLayout(side_layout)
        
        # Rotation
        rotation_layout = QVBoxLayout()
        rotation_label = QLabel("Rotación (°)")
        rotation_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        rotation_layout.addWidget(rotation_label)
        
        self.rotation_spin = QDoubleSpinBox()
        self.rotation_spin.setRange(-360, 360)
        self.rotation_spin.setValue(0.0)
        self.rotation_spin.setDecimals(2)
        self.rotation_spin.setSingleStep(5.0)
        self.rotation_spin.valueChanged.connect(self.relationChanged.emit)
        self.rotation_spin.setStyleSheet("font-size: 11px;")
        rotation_layout.addWidget(self.rotation_spin)
        layout.addLayout(rotation_layout)
        
        # Scale
        scale_layout = QVBoxLayout()
        scale_label = QLabel("Escala")
        scale_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        scale_layout.addWidget(scale_label)
        
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.1, 10.0)
        self.scale_spin.setValue(1.0)
        self.scale_spin.setSingleStep(0.1)
        self.scale_spin.setDecimals(2)
        self.scale_spin.valueChanged.connect(self.scaleChanged.emit)
        self.scale_spin.setStyleSheet("font-size: 11px;")
        scale_layout.addWidget(self.scale_spin)
        layout.addLayout(scale_layout)
        
        # Move controls
        move_layout = QVBoxLayout()
        move_label = QLabel("Desplazamiento (mm)")
        move_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        move_layout.addWidget(move_label)
        
        # X Move
        x_layout = QVBoxLayout()
        x_label = QLabel("X:")
        self.x_move_spin = QDoubleSpinBox()
        self.x_move_spin.setRange(-1000, 1000)
        self.x_move_spin.setValue(0.0)
        self.x_move_spin.setDecimals(2)
        self.x_move_spin.setSingleStep(1.0)
        self.x_move_spin.valueChanged.connect(self.moveXChanged.emit)
        self.x_move_spin.setStyleSheet("font-size: 11px;")
        x_layout.addWidget(x_label)
        x_layout.addWidget(self.x_move_spin)
        
        # Y Move
        y_layout = QVBoxLayout()
        y_label = QLabel("Y:")
        self.y_move_spin = QDoubleSpinBox()
        self.y_move_spin.setRange(-1000, 1000)
        self.y_move_spin.setValue(0.0)
        self.y_move_spin.setDecimals(2)
        self.y_move_spin.setSingleStep(1.0)
        self.y_move_spin.valueChanged.connect(self.moveYChanged.emit)
        self.y_move_spin.setStyleSheet("font-size: 11px;")
        y_layout.addWidget(y_label)
        y_layout.addWidget(self.y_move_spin)
        
        # Horizontal layout for X/Y
        xy_main_layout = QVBoxLayout()
        xy_main_layout.addLayout(x_layout)
        xy_main_layout.addLayout(y_layout)
        move_layout.addLayout(xy_main_layout)
        layout.addLayout(move_layout)
        
        self._layout.addWidget(self.edit_group)

    def _build_help_section(self):
        """Help section - collapsed by default"""
        self.help_group = QGroupBox("HERRAMIENTAS ▸")
        self.help_group.setCheckable(True)
        self.help_group.setChecked(False)
        
        layout = QVBoxLayout(self.help_group)
        
        help_actions = [
            ("Diseño", "🎨"),
            ("Patrones", "🔁"), 
            ("Colocar", "📍"),
            ("Workspace", "📐"),
            ("Materiales", "📦"),
            ("Comandos", "⌨️"),
            ("Ejecutar", "🚀")
        ]
        
        for text, icon in help_actions:
            btn = self._create_help_button(text, icon)
            if text == "Ejecutar":
                btn.clicked.connect(self.runRequested.emit)
            layout.addWidget(btn)
        
        self._layout.addWidget(self.help_group)

    def _create_main_button(self, text: str, icon: str) -> QToolButton:
        """Create main action button"""
        button = QToolButton()
        button.setText(text)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        button.setMinimumSize(200, 50)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.setStyleSheet(f"""
            QToolButton {{
                background-color: #2a2a2a;
                border: 2px solid #245983;
                border-radius: 8px;
                padding: 12px 15px;
                color: #d8dce2;
                font-weight: bold;
                font-size: 13px;
                margin: 3px;
            }}
            QToolButton:hover {{
                background-color: rgba(47,107,165,0.3);
                border-color: #5aa4db;
            }}
            QToolButton:pressed {{
                background-color: #2f6ba5;
                color: white;
            }}
        """)
        return button

    def _create_small_button(self, text: str, icon: str) -> QToolButton:
        """Create small action button"""
        button = QToolButton()
        button.setText(text)
        button.setMinimumSize(120, 30)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.setStyleSheet("""
            QToolButton {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 8px;
                color: #cccccc;
                font-size: 10px;
            }
            QToolButton:hover {
                background-color: #3a3a3a;
                border-color: #5aa4db;
            }
        """)
        return button

    def _create_help_button(self, text: str, icon: str) -> QToolButton:
        """Create help section button"""
        button = QToolButton()
        button.setText(text)
        button.setMinimumSize(120, 28)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.setStyleSheet("""
            QToolButton {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 8px;
                text-align: left;
                color: #cccccc;
                font-size: 10px;
            }
            QToolButton:hover {
                background-color: #3a3a3a;
            }
        """)
        return button

    def _on_workspace_toggled(self, checked: bool):
        """Update group title when toggled"""
        self.workspace_group.setTitle("WORKSPACE ▸" if not checked else "WORKSPACE ▾")

    def _apply_style(self) -> None:
        self.setStyleSheet("""
            #sidebar {
                background-color: #1e1e1e;
                color: #ffffff;
                border-right: 1px solid #333;
            }
            QGroupBox {
                color: #5aa4db;
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 5px;
                padding-top: 10px;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #5aa4db;
            }
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QDoubleSpinBox, QComboBox {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 4px;
                color: white;
                min-height: 25px;
            }
            QDoubleSpinBox:focus, QComboBox:focus {
                border-color: #5aa4db;
            }
        """)

    # Métodos públicos para controlar el estado
    def set_main_action_enabled(self, action: str, enabled: bool):
        """Habilitar/deshabilitar acción principal"""
        if action in self.main_buttons:
            self.main_buttons[action].setEnabled(enabled)

    def update_files_info(self, info: str):
        """Actualizar información de archivos"""
        self.files_info.setText(info)

    def get_edit_parameters(self) -> dict:
        """Obtener parámetros de edición actuales"""
        return {
            'side': self.side_combo.currentText(),
            'rotation': self.rotation_spin.value(),
            'scale': self.scale_spin.value(),
            'move_x': self.x_move_spin.value(),
            'move_y': self.y_move_spin.value()
        }