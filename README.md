# MikroTik Dashboard Pro

> Panel de administración para routers MikroTik vía API RouterOS, construido con PyQt6.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![PyQt6](https://img.shields.io/badge/UI-PyQt6-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Características

- **Gestión de conexión** — conéctate a cualquier router MikroTik mediante la API RouterOS.
- **Gestión de usuarios** — consulta, crea y administra usuarios del sistema.
- **Gestión de interfaces** — visualiza y controla las interfaces de red del router.
- **Monitoreo en tiempo real** — gráficos de tráfico actualizados en vivo por interfaz.
- **Operaciones no bloqueantes** — todas las llamadas de red corren en hilos separados para mantener la UI fluida.

---

## 🗂 Estructura del proyecto

```
mikrotik_dashboard/
│
├── main.py                    # Punto de entrada de la aplicación
│
├── core/                      # Lógica de negocio (sin dependencias de UI)
│   ├── api_service.py         # Todas las llamadas a la API RouterOS
│   └── worker.py              # Hilo genérico para operaciones de red
│
├── ui/                        # Capa de presentación (PyQt6)
│   ├── styles.py              # Estilos QSS globales
│   ├── main_window.py         # Ventana principal + orquestación de señales
│   └── tabs/
│       ├── tab_conexion.py    # Pestaña de conexión y listas generales
│       ├── tab_usuarios.py    # Pestaña de gestión de usuarios
│       ├── tab_interfaces.py  # Pestaña de gestión de interfaces
│       └── tab_monitoreo.py   # Pestaña de gráficos de tráfico
│
└── utils/
    └── validators.py          # Validaciones reutilizables (IP, usuario…)
```

---

## 🚀 Instalación

### Requisitos

- Python 3.9 o superior
- Router MikroTik con la API habilitada (puerto 8728 por defecto)

### Dependencias

```bash
pip install PyQt6 pyqtgraph librouteros
```

### Ejecución

```bash
python main.py
```

---

## 🔌 Configurar la API en MikroTik

Asegúrate de que la API RouterOS esté habilitada en tu router:

```
/ip service enable api
```

Por defecto escucha en el puerto **8728**. Se recomienda crear un usuario dedicado con permisos limitados para mayor seguridad.

---

## 🏗 Principios de diseño

La arquitectura sigue una separación estricta de responsabilidades:

| Módulo | Responsabilidad |
|---|---|
| `core/api_service.py` | Única clase que se comunica con RouterOS. Sin imports de Qt. |
| `core/worker.py` | Ejecuta cualquier función en un hilo separado para no bloquear la UI. |
| `ui/tabs/tab_*.py` | Construyen widgets y exponen señales/atributos. Sin lógica de negocio. |
| `ui/main_window.py` | Conecta señales de UI con llamadas al servicio. Archivo "glue" central. |
| `utils/validators.py` | Funciones puras de validación, sin dependencias externas. |

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor abre un *issue* antes de enviar un *pull request* con cambios importantes.

1. Haz un fork del repositorio.
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Realiza tus cambios y haz commit: `git commit -m 'feat: descripción del cambio'`
4. Envía tu rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request.

---

## 📄 Licencia

```
MIT License

Copyright (c) 2025 MikroTik Dashboard Pro Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
