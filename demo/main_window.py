from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QStatusBar, QMessageBox, QFileDialog, QMenuBar, QAction)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
import pandas as pd

from .sidebar import Sidebar
from .canvas import CanvasWidget
from app.core.dxf_processor import DXFProcessor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dxf_processor = DXFProcessor()
        self.trajectory_df = None
        self.current_file = None
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        self.setWindowTitle("ROBOT CORTADOR - HMI")
        self.setGeometry(100, 100, 1600, 900)
        
        # Crear widgets principales
        self.sidebar = Sidebar()
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
        self.status_bar.showMessage("Ready - Cargar archivo DXF para comenzar")
        
        self.setup_menu()
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Archivo")
        load_action = QAction("Cargar DXF", self)
        load_action.triggered.connect(self.load_dxf)
        file_menu.addAction(load_action)
        
    def setup_connections(self):
        """Conectar todas las señales del sidebar"""
        # Señales principales (tu diseño)
        self.sidebar.loadDxfRequested.connect(self.load_dxf)
        self.sidebar.generatePathRequested.connect(self.generate_trajectory)
        self.sidebar.simulateRequested.connect(self.simulate_cutting)
        self.sidebar.exportRequested.connect(self.export_trajectory)
        self.sidebar.configRequested.connect(self.show_config)
        
        # Señales del workspace
        self.sidebar.saveRequested.connect(self.save_workspace)
        self.sidebar.clearRequested.connect(self.clear_workspace)
        self.sidebar.p2pRequested.connect(self.point_to_point_mode)
        self.sidebar.runRequested.connect(self.run_execution)
        
        # Señales de edición
        self.sidebar.scaleChanged.connect(self.apply_scale)
        self.sidebar.moveXChanged.connect(self.apply_move_x)
        self.sidebar.moveYChanged.connect(self.apply_move_y)
        self.sidebar.relationChanged.connect(self.apply_rotation)
        
    def load_dxf(self):
        """Cargar archivo DXF"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo DXF", "", "DXF Files (*.dxf)")
        
        if file_path:
            self.current_file = file_path
            self.status_bar.showMessage(f"Procesando DXF: {file_path}")
            
            try:
                success = self.dxf_processor.process_file(file_path)
                
                if success:
                    # Convertir a DataFrame
                    self.trajectory_df = self.geometries_to_dataframe()
                    
                    # Actualizar UI
                    self.canvas.plot_geometries(self.dxf_processor.merged_geoms)
                    
                    # Actualizar sidebar
                    file_name = file_path.split('/')[-1]
                    self.sidebar.update_files_info(f"📁 {file_name}")
                    
                    # Habilitar acciones
                    self.sidebar.set_main_action_enabled("Generar Trayectoria", True)
                    self.sidebar.set_main_action_enabled("Simular Corte", True)
                    self.sidebar.set_main_action_enabled("Exportar", True)
                    
                    # Mostrar estadísticas
                    stats = self.dxf_processor.get_statistics()
                    self.status_bar.showMessage(
                        f"✅ DXF cargado: {stats['final_trajectories']} trayectorias, "
                        f"{len(self.trajectory_df)} puntos"
                    )
                    
                else:
                    self.status_bar.showMessage("❌ Error procesando DXF")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el DXF:\n{str(e)}")
                self.status_bar.showMessage("❌ Error cargando DXF")
    
    def generate_trajectory(self):
        """Generar trayectoria a partir del DXF"""
        if self.trajectory_df is not None:
            self.status_bar.showMessage("🔄 Generando trayectoria optimizada...")
            
            # Aquí iría la lógica de optimización de trayectoria
            QTimer.singleShot(1000, lambda: self.status_bar.showMessage("✅ Trayectoria generada"))
    
    def simulate_cutting(self):
        """Simular proceso de corte"""
        if self.trajectory_df is not None:
            self.status_bar.showMessage("🎬 Iniciando simulación de corte...")
            self.canvas.start_simulation(self.trajectory_df)
    
    def export_trajectory(self):
        """Exportar trayectoria"""
        if self.trajectory_df is not None:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Exportar Trayectoria", "trayectoria_robot.txt", "Text Files (*.txt)")
            
            if file_path:
                try:
                    # Exportar lógica
                    self.status_bar.showMessage(f"✅ Trayectoria exportada: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error exportando:\n{str(e)}")
    
    def show_config(self):
        """Mostrar configuración"""
        QMessageBox.information(self, "Configuración", "Panel de configuración del robot")
    
    # Métodos del workspace
    def save_workspace(self):
        self.status_bar.showMessage("💾 Workspace guardado")
    
    def clear_workspace(self):
        reply = QMessageBox.question(
            self, "Limpiar Workspace", 
            "¿Estás seguro de limpiar el workspace?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.trajectory_df = None
            self.current_file = None
            self.canvas.clear()
            self.sidebar.update_files_info("No hay archivos cargados")
            self.sidebar.set_main_action_enabled("Generar Trayectoria", False)
            self.sidebar.set_main_action_enabled("Simular Corte", False)
            self.sidebar.set_main_action_enabled("Exportar", False)
            self.status_bar.showMessage("Workspace limpiado")
    
    def point_to_point_mode(self):
        self.status_bar.showMessage("🔗 Modo Punto a Punto activado")
    
    def run_execution(self):
        self.status_bar.showMessage("🚀 Ejecutando en robot...")
    
    # Métodos de edición
    def apply_scale(self, scale: float):
        if self.trajectory_df is not None:
            self.status_bar.showMessage(f"🔍 Escala aplicada: {scale}x")
    
    def apply_move_x(self, move_x: float):
        if self.trajectory_df is not None:
            self.status_bar.showMessage(f"↔️ Movimiento X: {move_x} mm")
    
    def apply_move_y(self, move_y: float):
        if self.trajectory_df is not None:
            self.status_bar.showMessage(f"↕️ Movimiento Y: {move_y} mm")
    
    def apply_rotation(self, angle: float):
        if self.trajectory_df is not None:
            self.status_bar.showMessage(f"🔄 Rotación: {angle}°")
    
    def geometries_to_dataframe(self) -> pd.DataFrame:
        """Convertir geometrías a DataFrame"""
        points = []
        
        for i, geom in enumerate(self.dxf_processor.merged_geoms):
            x, y = geom.xy
            for xi, yi in zip(x, y):
                points.append({
                    'x': xi, 'y': yi, 
                    'trajectory_id': i, 'point_type': 'path'
                })
            points.append({
                'x': None, 'y': None,
                'trajectory_id': i, 'point_type': 'separator'
            })
            
        return pd.DataFrame(points)