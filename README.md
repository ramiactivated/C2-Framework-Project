# <p align="center">⚡ G3-FLASH | Advanced C2 Framework ⚡</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.2.0-00ff41?style=for-the-badge&logo=target" />
  <img src="https://img.shields.io/badge/C%2B%2B-Implante-blue?style=for-the-badge&logo=c%2B%2B" />
  <img src="https://img.shields.io/badge/Python-C2%20Server-yellow?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/License-MIT-red?style=for-the-badge" />
</p>

---

## 📖 Descripción
**G3-FLASH** es una plataforma de Comando y Control (C2) de grado de investigación diseñada para demostrar la interacción compleja entre implantes de bajo nivel y servidores de control modernos. El proyecto se enfoca en la **exfiltración binaria**, la **vigilancia en tiempo real** y la **persistencia** en sistemas Windows.

---

## 🛠️ Arquitectura Técnica

### 🛡️ Agente (Implante C++ Native)
* **📸 Vigilancia por GDI+:** Captura de pantalla en tiempo real con sistema de bloqueo de ámbito para evitar colisiones de E/S.
* **⌨️ Keylogger Multihilo:** Basado en `SetWindowsHookEx` para captura asíncrona sin bloquear la comunicación.
* **📂 Motor de Exfiltración:** Transmisión de archivos mediante buffers dinámicos de `std::vector` (PDF, DOCX, EXE, etc).
* **🔄 Persistencia:** Auto-replicación en `%APPDATA%` y persistencia mediante registro (`HKCU\Run`).
* **👤 Identificación:** Recolección automática de metadatos (Hostname/User) en el *handshake* inicial.

### 💻 Panel de Control (Python/Flask)
* **🔗 Sincronización de Sockets:** Lógica avanzada para manejar fragmentación de paquetes TCP.
* **📟 Dashboard Cyberpunk:** UI responsiva con Bootstrap 5 y estética Dark Terminal.
* **🖼️ Visor de Screenshots:** Sistema de *Cache Busting* para visualización inmediata de capturas.

---

## 📂 Estructura del Proyecto
\`\`\`text
.
├── agent/
│   └── main.cpp         # Código fuente del implante (C++)
├── server/
│   ├── web_server.py    # Backend Flask y motor de sockets
│   ├── templates/       # Dashboard HTML (Bootstrap 5)
│   └── downloads/       # Repositorio de exfiltración (Loot)
└── README.md
\`\`\`

---

## 🚀 Guía de Despliegue

### 1. Compilación del Implante (Windows/MinGW)
\`\`\`bash
g++ main.cpp -o agente.exe -lws2_32 -ladvapi32 -lgdiplus -lgdi32 -mwindows -static -pthread
\`\`\`
> **Nota:** El flag \`-mwindows\` asegura que el agente no abra ninguna consola al ejecutarse.

### 2. Inicio del Servidor (Kali Linux)
\`\`\`bash
pip install flask
python3 web_server.py
\`\`\`

---

## 📋 Comandos Disponibles

| Comando | Acción | Descripción |
| :--- | :--- | :--- |
| \`screenshot\` | **Vigilancia** | Toma una captura de pantalla y la muestra en el panel. |
| \`download [ruta]\` | **Exfiltración** | Descarga archivos desde la víctima a la carpeta \`/downloads\`. |
| \`dump\` | **Keylogger** | Recupera todas las pulsaciones de teclas capturadas. |
| \`[Shell CMD]\` | **RCE** | Ejecuta comandos directamente en la CMD de la víctima. |

---

## ⚠️ Propósitos Educativos (Disclaimer)
Este software ha sido desarrollado con el único propósito de **educar** en  ciberseguridad. 
1. **No** debe ser utilizado en sistemas sin autorización explícita.
2. El uso de esta herramienta en redes ajenas es **ilegal**.
3. El desarrollador no se hace responsable del mal uso de este software.

---
<p align="center">
  <b>Desarrollado por ramiactivated | 2026</b>
</p>
