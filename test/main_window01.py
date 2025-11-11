from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QStatusBar, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from .sidebar01 import Sidebar, SidebarAction
from .canvas01 import CanvasWidget
from app.core.dxf_processor import DXFProcessor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dxf_processor = DXFProcessor()
        self.trajectory_df = None
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        self.setWindowTitle("HMI - Robot Cortador")
        self.setGeometry(100, 100, 1400, 900)
        
        # Crear acciones del sidebar
        actions = [
            SidebarAction("Cargar DXF", QIcon("📁")),
            SidebarAction("Generar Trayectoria", QIcon("🔄"), enabled=False),
            SidebarAction("Simular Corte", QIcon("🎬"), enabled=False),
            SidebarAction("Exportar", QIcon("📤"), enabled=False),
            SidebarAction("Configuración", QIcon("⚙️")),
        ]
        
        # Crear widgets principales
        self.sidebar = Sidebar(actions)
        self.canvas = CanvasWidget()
        
        # Layout principal
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.canvas, 1)
        
        self.setCentralWidget(central_widget)
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo para cargar archivo DXF")
        
        # Menú
        self.setup_menu()
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("Archivo")
        
        load_action = QAction("Cargar DXF", self)
        load_action.triggered.connect(self.load_dxf)
        file_menu.addAction(load_action)
        
        export_action = QAction("Exportar Trayectoria", self)
        export_action.triggered.connect(self.export_trajectory)
        file_menu.addAction(export_action)
        
    def setup_connections(self):
        """Conectar señales del sidebar"""
        self.sidebar.loadDxfRequested.connect(self.load_dxf)
        self.sidebar.generatePathRequested.connect(self.generate_trajectory)
        self.sidebar.simulateRequested.connect(self.simulate_cutting)
        self.sidebar.exportRequested.connect(self.export_trajectory)
        
    def load_dxf(self):
        """Cargar y procesar archivo DXF"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo DXF", "", "DXF Files (*.dxf)")
        
        if file_path:
            self.status_bar.showMessage(f"Procesando {file_path}...")
            self.sidebar.show_progress(True)
            
            # Procesar en background (simulado con QTimer)
            QTimer.singleShot(100, lambda: self.process_dxf_file(file_path))
            
    def process_dxf_file(self, file_path: str):
        """Procesar el archivo DXF"""
        try:
            success = self.dxf_processor.process_file(file_path)
            
            if success:
                # Convertir a DataFrame
                self.trajectory_df = self.geometries_to_dataframe()
                
                # Actualizar UI
                self.canvas.plot_geometries(self.dxf_processor.merged_geoms)
                self.sidebar.set_action_enabled("Generar Trayectoria", True)
                self.status_bar.showMessage(f"✅ DXF cargado: {len(self.dxf_processor.merged_geoms)} trayectorias")
                
                # Mostrar estadísticas
                stats = self.dxf_processor.get_statistics()
                self.show_stats_message(stats)
            else:
                self.status_bar.showMessage("❌ Error procesando DXF")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo procesar el DXF:\n{str(e)}")
            self.status_bar.showMessage("❌ Error cargando DXF")
        finally:
            self.sidebar.show_progress(False)
            
    def geometries_to_dataframe(self) -> pd.DataFrame:
        """Convertir geometrías a DataFrame de puntos"""
        points = []
        
        for i, geom in enumerate(self.dxf_processor.merged_geoms):
            x, y = geom.xy
            for xi, yi in zip(x, y):
                points.append({
                    'x': xi,
                    'y': yi, 
                    'trajectory_id': i,
                    'point_type': 'path'
                })
            # Añadir separador entre trayectorias
            points.append({
                'x': None,
                'y': None,
                'trajectory_id': i,
                'point_type': 'separator'
            })
            
        df = pd.DataFrame(points)
        print(f"📊 DataFrame creado: {len(df)} puntos, {len(self.dxf_processor.merged_geoms)} trayectorias")
        return df
    
    def generate_trajectory(self):
        """Generar trayectoria para el robot"""
        if self.trajectory_df is not None:
            self.status_bar.showMessage("🔄 Generando trayectoria optimizada...")
            self.sidebar.set_action_enabled("Simular Corte", True)
            
            # Aquí iría la lógica de optimización de trayectoria
            QTimer.singleShot(500, lambda: self.status_bar.showMessage("✅ Trayectoria generada"))
            
    def simulate_cutting(self):
        """Simular proceso de corte"""
        if self.trajectory_df is not None:
            self.status_bar.showMessage("🎬 Iniciando simulación de corte...")
            self.sidebar.set_action_enabled("Exportar", True)
            self.canvas.start_simulation(self.trajectory_df)
            
    def export_trajectory(self):
        """Exportar trayectoria a archivo"""
        if self.trajectory_df is not None:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar trayectoria", "trayectoria_robot.txt", "Text Files (*.txt)")
            
            if file_path:
                try:
                    # Filtrar solo puntos de trayectoria (no separadores)
                    path_points = self.trajectory_df[self.trajectory_df['point_type'] == 'path']
                    
                    with open(file_path, 'w') as f:
                        f.write("X,Y,Trajectory\n")
                        for _, point in path_points.iterrows():
                            f.write(f"{point['x']:.6f},{point['y']:.6f},{int(point['trajectory_id'])}\n")
                    
                    self.status_bar.showMessage(f"✅ Trayectoria exportada: {file_path}")
                    QMessageBox.information(self, "Éxito", f"Trayectoria exportada:\n{file_path}")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo exportar:\n{str(e)}")
    
    def show_stats_message(self, stats: dict):
        """Mostrar estadísticas del procesamiento"""
        message = (f"📊 Estadísticas DXF:\n"
                  f"• Trayectorias: {stats['final_trajectories']}\n"
                  f"• Tolerancia: {stats['tolerance_used']} mm\n"
                  f"• Puntos en DataFrame: {len(self.trajectory_df) if self.trajectory_df is not None else 0}")
        
        QMessageBox.information(self, "Procesamiento Completado", message)