from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
import pandas as pd

class CanvasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.simulation_animation = None
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.figure, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.setup_plot()
    
    def setup_plot(self):
        """Configurar el gráfico base"""
        self.ax.set_title("Robot Cortador - Visualización de Trayectorias")
        self.ax.set_xlabel("X [mm]")
        self.ax.set_ylabel("Y [mm]")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
    
    def plot_geometries(self, geometries):
        """Dibujar geometrías en el canvas"""
        self.ax.clear()
        self.setup_plot()
        
        for i, geom in enumerate(geometries):
            x, y = geom.xy
            self.ax.plot(x, y, linewidth=2, label=f"Trayectoria {i+1}")
        
        self.ax.legend()
        self.canvas.draw()
    
    def start_simulation(self, trajectory_df: pd.DataFrame):
        """Iniciar simulación animada"""
        self.ax.clear()
        self.setup_plot()
        
        # Plot todas las trayectorias
        for traj_id in trajectory_df['trajectory_id'].unique():
            traj_data = trajectory_df[
                (trajectory_df['trajectory_id'] == traj_id) & 
                (trajectory_df['point_type'] == 'path')
            ]
            if not traj_data.empty:
                self.ax.plot(traj_data['x'], traj_data['y'], 'b-', alpha=0.3, linewidth=1)
        
        # Punto para animación
        self.sim_point, = self.ax.plot([], [], 'ro', markersize=6, label='Posición Actual')
        self.ax.legend()
        
        # Preparar datos para animación
        path_points = trajectory_df[trajectory_df['point_type'] == 'path']
        self.sim_data = list(zip(path_points['x'], path_points['y']))
        self.current_index = 0
        
        # Iniciar animación
        self.simulation_animation = FuncAnimation(
            self.figure, self._update_simulation,
            frames=len(self.sim_data), interval=50, repeat=False, blit=True
        )
        
        self.canvas.draw()
    
    def _update_simulation(self, frame):
        """Actualizar frame de simulación"""
        if self.current_index < len(self.sim_data):
            x, y = self.sim_data[self.current_index]
            self.sim_point.set_data([x], [y])
            self.current_index += 1
        return [self.sim_point]