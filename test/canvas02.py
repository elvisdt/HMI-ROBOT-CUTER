from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np

class ModernNavigationToolbar(NavigationToolbar):
    """Toolbar personalizada con estilo moderno"""
    
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.setStyleSheet("""
            QToolBar {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 6px;
                spacing: 3px;
                padding: 5px;
                margin: 5px;
            }
            QToolButton {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
                min-width: 30px;
                min-height: 30px;
            }
            QToolButton:hover {
                background-color: #4d4d4d;
                border-color: #5aa4db;
            }
            QToolButton:pressed {
                background-color: #5aa4db;
            }
        """)

class CanvasWidget(QWidget):
    # Señales para comunicación
    simulationStarted = pyqtSignal()
    simulationFinished = pyqtSignal()
    simulationProgress = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.simulation_animation = None
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self._update_simulation)
        self.current_sim_index = 0
        self.sim_data = []
        self.is_simulating = False
        
        self.setup_ui()
        self.setup_modern_plot_style()
        
    def setup_ui(self):
        """Configurar la interfaz del canvas centrada"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Header centrado
        self.setup_centered_header(main_layout)
        
        # Área de visualización principal centrada
        self.setup_centered_canvas(main_layout)
        
        # Barra de estado centrada
        self.setup_status_bar(main_layout)
        
    def setup_centered_header(self, layout):
        """Header centrado con información"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Título principal centrado
        title_label = QLabel("VISUALIZACIÓN DE TRAYECTORIAS")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #5aa4db;
                font-weight: bold;
                font-size: 16px;
                padding: 5px;
            }
        """)
        
        # Subtítulo
        subtitle_label = QLabel("Trayectorias de Corte - Robot")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 12px;
                padding: 2px;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
    
    def setup_centered_canvas(self, layout):
        """Área del canvas centrada y bien distribuida"""
        # Contenedor principal para el canvas
        canvas_container = QFrame()
        canvas_container.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 8px;
            }
        """)
        
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(10, 10, 10, 10)
        canvas_layout.setSpacing(8)
        
        # Barra de herramientas centrada
        self.setup_toolbar(canvas_layout)
        
        # Canvas centrado
        self.setup_main_canvas(canvas_layout)
        
        # Controles de simulación centrados
        self.setup_simulation_controls(canvas_layout)
        
        layout.addWidget(canvas_container, 1)  # Factor de estiramiento 1
    
    def setup_toolbar(self, layout):
        """Toolbar centrada"""
        toolbar_container = QFrame()
        toolbar_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        
        toolbar_layout = QHBoxLayout(toolbar_container)
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Toolbar personalizada
        self.figure, self.ax = plt.subplots(figsize=(10, 8), facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = ModernNavigationToolbar(self.canvas, self)
        
        toolbar_layout.addWidget(self.toolbar)
        layout.addWidget(toolbar_container)
    
    def setup_main_canvas(self, layout):
        """Canvas principal centrado"""
        canvas_frame = QFrame()
        canvas_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 0px;
            }
        """)
        
        canvas_frame_layout = QVBoxLayout(canvas_frame)
        canvas_frame_layout.setContentsMargins(0, 0, 0, 0)
        canvas_frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Canvas centrado dentro del frame
        canvas_inner_layout = QHBoxLayout()
        canvas_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        canvas_inner_layout.addWidget(self.canvas)
        
        canvas_frame_layout.addLayout(canvas_inner_layout)
        layout.addWidget(canvas_frame, 1)  # Factor de estiramiento 1
    
    def setup_simulation_controls(self, layout):
        """Controles de simulación centrados"""
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.setSpacing(15)
        
        # Información de estado
        info_label = QLabel("Estado de Simulación:")
        info_label.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        
        self.sim_btn = QPushButton("▶ Iniciar Simulación")
        self.sim_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #34495e;
                color: #7f8c8d;
            }
        """)
        self.sim_btn.clicked.connect(self.toggle_simulation)
        self.sim_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("⏹ Detener")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #34495e;
                color: #7f8c8d;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_simulation)
        self.stop_btn.setEnabled(False)
        
        controls_layout.addWidget(info_label)
        controls_layout.addWidget(self.sim_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addStretch()
        
        layout.addWidget(controls_frame)
    
    def setup_status_bar(self, layout):
        """Barra de estado centrada"""
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QLabel {
                color: #bdc3c7;
                font-size: 11px;
            }
        """)
        
        status_layout = QHBoxLayout(status_frame)
        
        # Estado actual
        self.status_label = QLabel("🟢 Listo - Cargue un archivo DXF para comenzar")
        self.status_label.setStyleSheet("font-weight: bold;")
        
        # Progreso
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #5aa4db; font-weight: bold;")
        
        # Información de coordenadas
        self.coords_label = QLabel("X: -- | Y: --")
        self.coords_label.setStyleSheet("color: #f39c12; font-family: monospace;")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.coords_label)
        status_layout.addWidget(self.progress_label)
        
        layout.addWidget(status_frame)
    
    def setup_modern_plot_style(self):
        """Configurar estilo moderno para matplotlib"""
        plt.style.use('dark_background')
        
        # Configuración personalizada más moderna
        self.figure.set_facecolor('#1e1e1e')
        self.ax.set_facecolor('#2d2d2d')
        
        # Estilo de grid y ejes moderno
        self.ax.grid(True, alpha=0.2, color='#5aa4db', linestyle='-', linewidth=0.5)
        self.ax.tick_params(colors='#bdc3c7', labelsize=9)
        self.ax.spines['bottom'].set_color('#5aa4db')
        self.ax.spines['left'].set_color('#5aa4db')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
    
    def setup_plot(self):
        """Configurar el gráfico base con estilo moderno y centrado"""
        self.ax.clear()
        self.ax.set_facecolor('#2d2d2d')
        
        # Títulos y etiquetas con estilo moderno - CENTRADOS
        self.ax.set_title("Sistema de Coordenadas de Corte", 
                         color='#5aa4db', fontsize=14, fontweight='bold', pad=20)
        self.ax.set_xlabel("Coordenada X [mm]", color='#bdc3c7', fontsize=11, labelpad=10)
        self.ax.set_ylabel("Coordenada Y [mm]", color='#bdc3c7', fontsize=11, labelpad=10)
        
        # Grid moderno
        self.ax.grid(True, alpha=0.2, color='#5aa4db', linestyle='-', linewidth=0.5)
        self.ax.set_aspect('equal')
        
        # Ejes con estilo
        self.ax.tick_params(colors='#bdc3c7', labelsize=9)
        self.ax.spines['bottom'].set_color('#5aa4db')
        self.ax.spines['left'].set_color('#5aa4db')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        # Líneas de referencia en el origen - MÁS VISIBLES
        self.ax.axhline(y=0, color='#e74c3c', linestyle='--', alpha=0.6, linewidth=1.2)
        self.ax.axvline(x=0, color='#e74c3c', linestyle='--', alpha=0.6, linewidth=1.2)
        
        # Texto de origen mejorado
        self.ax.text(0.02, 0.98, 'ORIGEN (0,0)', transform=self.ax.transAxes, 
                    color='#e74c3c', fontsize=10, fontweight='bold', alpha=0.8,
                    verticalalignment='top', 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#1e1e1e', 
                            edgecolor='#e74c3c', alpha=0.9))
        
        # Asegurar que el gráfico esté centrado
        self.ax.set_xlim(-100, 100)
        self.ax.set_ylim(-100, 100)
    
    def plot_geometries(self, geometries):
        """Dibujar geometrías en el canvas con estilo moderno"""
        if not geometries:
            return
            
        self.setup_plot()
        
        # Paleta de colores moderna
        colors = ['#5aa4db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6', '#1abc9c']
        
        for i, geom in enumerate(geometries):
            x, y = geom.xy
            color = colors[i % len(colors)]
            
            # Línea principal
            line = self.ax.plot(x, y, linewidth=2.5, color=color, 
                               label=f"Trayectoria {i+1}", alpha=0.9,
                               marker='o', markersize=4, markevery=8)[0]
            
            # Puntos de inicio/fin destacados
            self.ax.plot(x[0], y[0], 'o', markersize=10, color=color, 
                        markeredgecolor='white', markeredgewidth=2,
                        label=f'_Inicio {i+1}' if i == 0 else "")
            self.ax.plot(x[-1], y[-1], 's', markersize=10, color=color,
                        markeredgecolor='white', markeredgewidth=2,
                        label=f'_Fin {i+1}' if i == 0 else "")
        
        # Leyenda moderna y centrada
        legend = self.ax.legend(loc='upper right', framealpha=0.95, 
                               facecolor='#2d2d2d', edgecolor='#5aa4db',
                               fontsize=10, labelcolor='#bdc3c7',
                               bbox_to_anchor=(0.98, 0.98))
        legend.get_frame().set_linewidth(1.5)
        
        # Ajustar límites con margen para mejor visualización
        all_x = []
        all_y = []
        for geom in geometries:
            x, y = geom.xy
            all_x.extend(x)
            all_y.extend(y)
        
        if all_x and all_y:
            x_margin = (max(all_x) - min(all_x)) * 0.15
            y_margin = (max(all_y) - min(all_y)) * 0.15
            self.ax.set_xlim(min(all_x) - x_margin, max(all_x) + x_margin)
            self.ax.set_ylim(min(all_y) - y_margin, max(all_y) + y_margin)
        
        self.canvas.draw()
        self.status_label.setText(f"✅ {len(geometries)} trayectorias cargadas y centradas")
        self.sim_btn.setEnabled(True)
        
        # Actualizar información de coordenadas
        if all_x and all_y:
            self.coords_label.setText(f"X: [{min(all_x):.1f} : {max(all_x):.1f}] | Y: [{min(all_y):.1f} : {max(all_y):.1f}]")
    
    def start_simulation(self, trajectory_df: pd.DataFrame):
        """Iniciar simulación animada con estilo moderno"""
        if trajectory_df is None or trajectory_df.empty:
            return
            
        self.setup_plot()
        
        # Preparar datos para simulación
        path_points = trajectory_df[trajectory_df['point_type'] == 'path']
        self.sim_data = list(zip(path_points['x'], path_points['y']))
        
        if not self.sim_data:
            return
            
        # Dibujar todas las trayectorias de fondo
        colors = plt.cm.viridis(np.linspace(0, 1, len(trajectory_df['trajectory_id'].unique())))
        
        for i, traj_id in enumerate(trajectory_df['trajectory_id'].unique()):
            traj_data = trajectory_df[
                (trajectory_df['trajectory_id'] == traj_id) & 
                (trajectory_df['point_type'] == 'path')
            ]
            if not traj_data.empty:
                self.ax.plot(traj_data['x'], traj_data['y'], 
                           color=colors[i], alpha=0.4, linewidth=2.5, 
                           label=f"_Trayectoria {traj_id+1}")
        
        # Elementos de simulación
        self.sim_point, = self.ax.plot([], [], 'o', 
                                     markersize=14, color='#e74c3c',
                                     markeredgecolor='white', 
                                     markeredgewidth=2.5,
                                     label='Cabeza de Corte')
        
        # Rastro de la simulación
        self.sim_trail, = self.ax.plot([], [], '-', 
                                     color='#f39c12', alpha=0.7, linewidth=2.0)
        
        # Leyenda centrada
        legend = self.ax.legend(loc='upper right', framealpha=0.95)
        legend.get_frame().set_facecolor('#2d2d2d')
        
        # Iniciar simulación
        self.current_sim_index = 0
        self.trail_x, self.trail_y = [], []
        self.is_simulating = True
        
        self.sim_btn.setText("⏸ Pausar")
        self.sim_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("🎬 Simulación en progreso...")
        
        # Usar QTimer para mejor control
        self.simulation_timer.start(25)  # 25ms entre frames para mayor suavidad
        
        self.simulationStarted.emit()
    
    def _update_simulation(self):
        """Actualizar frame de simulación"""
        if self.current_sim_index < len(self.sim_data):
            x, y = self.sim_data[self.current_sim_index]
            
            # Actualizar punto de simulación
            self.sim_point.set_data([x], [y])
            
            # Actualizar rastro
            self.trail_x.append(x)
            self.trail_y.append(y)
            self.sim_trail.set_data(self.trail_x, self.trail_y)
            
            # Actualizar coordenadas en tiempo real
            self.coords_label.setText(f"X: {x:.1f} | Y: {y:.1f}")
            
            # Actualizar progreso
            progress = int((self.current_sim_index + 1) / len(self.sim_data) * 100)
            self.progress_label.setText(f"Progreso: {progress}%")
            self.simulationProgress.emit(progress)
            
            self.current_sim_index += 1
            self.canvas.draw()
        else:
            self.stop_simulation()
    
    def toggle_simulation(self):
        """Alternar entre play/pause"""
        if self.is_simulating:
            self.pause_simulation()
        else:
            if hasattr(self, 'trajectory_df'):
                self.start_simulation(self.trajectory_df)
    
    def pause_simulation(self):
        """Pausar simulación"""
        if self.is_simulating:
            self.simulation_timer.stop()
            self.is_simulating = False
            self.sim_btn.setText("▶ Continuar")
            self.status_label.setText("⏸ Simulación pausada")
    
    def stop_simulation(self):
        """Detener simulación completamente"""
        self.simulation_timer.stop()
        self.is_simulating = False
        self.current_sim_index = 0
        self.trail_x, self.trail_y = [], []
        
        self.sim_btn.setText("▶ Iniciar Simulación")
        self.sim_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_label.setText("")
        self.status_label.setText("✅ Simulación completada")
        self.coords_label.setText("Simulación finalizada")
        
        self.simulationFinished.emit()
    
    def clear(self):
        """Limpiar el canvas"""
        self.setup_plot()
        self.canvas.draw()
        self.status_label.setText("🟢 Canvas limpiado - Listo para nueva carga")
        self.sim_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.progress_label.setText("")
        self.coords_label.setText("X: -- | Y: --")
        
        # Limpiar datos de simulación
        if hasattr(self, 'trajectory_df'):
            del self.trajectory_df
    
    def set_trajectory_data(self, trajectory_df: pd.DataFrame):
        """Establecer datos de trayectoria para simulación"""
        self.trajectory_df = trajectory_df
        if trajectory_df is not None and not trajectory_df.empty:
            self.sim_btn.setEnabled(True)
    
    def update_status(self, message: str):
        """Actualizar mensaje de estado"""
        self.status_label.setText(message)