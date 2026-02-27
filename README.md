# MikroTik Dashboard Pro

Panel de administración para routers MikroTik vía API RouterOS.

## Estructura del proyecto

```
mikrotik_dashboard/
│
├── main.py                        # Punto de entrada
│
├── core/                          # Lógica de negocio (sin UI)
│   ├── api_service.py             # Todas las llamadas a la API RouterOS
│   └── worker.py                  # Hilo genérico para operaciones de red
│
├── ui/                            # Capa de presentación
│   ├── styles.py                  # Estilos QSS globales
│   ├── main_window.py             # Ventana principal + orquestación
│   └── tabs/                      # Una clase por pestaña
│       ├── tab_conexion.py        # Pestaña de conexión y listas generales
│       ├── tab_usuarios.py        # Pestaña de gestión de usuarios
│       ├── tab_interfaces.py      # Pestaña de gestión de interfaces
│       └── tab_monitoreo.py       # Pestaña de gráficos de tráfico
│
└── utils/
    └── validators.py              # Validaciones reutilizables (IP, usuario…)
```

## Instalación de dependencias

```bash
pip install PyQt6 pyqtgraph librouteros
```

## Ejecución

```bash
python main.py
```

## Principios de diseño

| Capa | Responsabilidad |
|---|---|
| `core/api_service.py` | Única clase que habla con RouterOS. Sin imports de Qt. |
| `core/worker.py` | Ejecuta cualquier función en un hilo separado para no bloquear la UI. |
| `ui/tabs/tab_*.py` | Solo construyen widgets y exponen señales/atributos. Sin lógica de negocio. |
| `ui/main_window.py` | Conecta señales de UI con llamadas al servicio. Único archivo "glue". |
| `utils/validators.py` | Funciones puras de validación, sin dependencias externas. |
