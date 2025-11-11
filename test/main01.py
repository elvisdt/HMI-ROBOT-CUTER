import sys
from PyQt6.QtWidgets import QApplication
from .main_window01 import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Configurar estilo de la aplicación
    app.setStyle('Fusion')
    
    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()