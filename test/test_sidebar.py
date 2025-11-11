import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from app.ui.parts.sidebar import Sidebar, SidebarAction

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Sidebar")
        self.setGeometry(100, 100, 800, 600)
        
        # Crear acciones de prueba
        actions = [
            SidebarAction("Archivo", QIcon("📁")),  # Puedes usar emojis como iconos simples
            SidebarAction("Editar", QIcon("✏️")),
            SidebarAction("Ver", QIcon("👁️")),
            SidebarAction("Herramientas", QIcon("🔧")),
            SidebarAction("Ayuda", QIcon("❓")),
        ]
        
        # Crear sidebar
        self.sidebar = Sidebar(actions)
        self.sidebar.actionTriggered.connect(self.on_action_triggered)
        
        # Área de contenido
        self.content_label = QLabel("Selecciona una acción del sidebar")
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_label.setStyleSheet("font-size: 16px; margin: 20px;")
        
        # Layout principal
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.content_label)
        
        # Configurar ventana
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(central_widget)
        
        self.setCentralWidget(main_widget)
        
        # Agregar sidebar como widget flotante
        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.addWidget(self.sidebar)
        self.setMenuWidget(sidebar_container)
    
    def on_action_triggered(self, action_name: str):
        self.content_label.setText(f"Acción seleccionada: {action_name}")
        print(f"Sidebar action: {action_name}")

def test_sidebar():
    """Función de prueba básica"""
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    # Test programático después de mostrar la ventana
    def test_programmatic_trigger():
        window.sidebar.trigger_action("Herramientas")
    
    # Ejecutar test después de que la ventana esté visible
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(1000, test_programmatic_trigger)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_sidebar()