# HMI para robot cortador

Proyecto inicial para experimentar con una interfaz HMI escrita en PyQt6 orientada a controlar y simular un robot de corte de metal.

## Requisitos

- Python 3.10+ (probado con 3.13)
- [PyQt6](https://pypi.org/project/PyQt6/)

## Instalación rápida

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install PyQt6
```

## Ejecutar la interfaz

```powershell
.venv\Scripts\activate
python main.py
```

## Qué incluye

- Arquitectura modular en el paquete `hmi/` separando ventana principal, barra lateral, lienzo y paneles.
- Barra lateral con acciones principales (Files, Add, Save, Clear, P2P).
- Lienzo CAD preliminar (`QGraphicsView`) con cuadrícula, ejes y geometría de ejemplo manipulable en tiempo real.
- Panel de propiedades editable que actualiza rotación, escala y desplazamientos directamente sobre el lienzo.
- Barra inferior con flujo de trabajo por etapas (Design → Place → Materials → Run).

## Próximos pasos sugeridos

- Conectar los botones de control con lógica real (PLC, ROS, sockets, etc.).
- Persistir programas de corte a disco (G-Code, JSON o base de datos).
- Integrar un simulador 2D/3D más completo (ej. PyQtGraph, OpenGL, ROS RViz).
- Añadir panel de alarmas con registros históricos y filtros.
- Implementar autenticación/roles para restringir accesos críticos.
