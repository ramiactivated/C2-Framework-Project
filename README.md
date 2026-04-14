# ⚡ G3-FLASH | Advanced C2 Framework (PoC)

Este proyecto es una implementación avanzada de un sistema de **Comando y Control (C2)** diseñado para fines educativos y de investigación en ciberseguridad. Demuestra la comunicación persistente y la exfiltración de datos entre implantes desarrollados en **C++** y un panel de control táctico basado en **Python/Flask**.

## 🚀 Funcionalidades de Élite

### 🛡️ Agente (Implante C++)
- **Reconocimiento Automático:** Identificación inmediata del Hostname y Username de la víctima mediante la API de Windows.
- **Vigilancia Visual:** Captura de pantalla en tiempo real usando GDI+ y transmisión binaria sincronizada.
- **Gestión de Archivos:** Módulo de exfiltración binaria para descargar cualquier archivo del sistema víctima.
- **Keylogger Silencioso:** Registro de pulsaciones a bajo nivel mediante Hooks de Windows (`WH_KEYBOARD_LL`).
- **Persistencia Avanzada:** Auto-copia en `%APPDATA%` y persistencia mediante registro (`HKCU\Run`).
- **Stealth Mode:** Compilación en modo ventana oculta y ejecución multihilo para evitar bloqueos del sistema.

### 💻 Panel de Control (Servidor Python)
- **Interfaz:** Dashboard dinámico desarrollado con Bootstrap 5, FontAwesome y estética Dark Terminal.
- **Gestión de Sockets Robusta:** Protocolo de comunicación personalizado para manejar fragmentación de paquetes y sincronización de buffers.
- **Visor de Screenshots:** Galería integrada con sistema de "Cache Busting" para visualización en tiempo real.
- **Seguridad:** Acceso protegido mediante decoradores de sesión y gestión multicliente mediante threading.

## 🛠️ Stack Tecnológico
- **Lenguajes:** C++17 (Agente), Python 3.x (Servidor), JS/HTML5 (Frontend).
- **Networking:** WinSock2, TCP Sockets (Binary/Text).
- **Gráficos:** Windows GDI+ (Graphics Device Interface).
- **OS:** Kali Linux (C2 Server), Windows 10 (Target).

## 📥 Instalación y Uso

### Compilación del Agente (MinGW en Windows)
```bash
g++ main.cpp -o agente.exe -lws2_32 -ladvapi32 -lgdiplus -lgdi32 -mwindows -static -pthread
