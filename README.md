# <p align="center">⚡ G3-FLASH | Advanced C2 Framework ⚡</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.2.0-00ff41?style=for-the-badge&logo=target" />
  <img src="https://img.shields.io/badge/C%2B%2B-Implante-blue?style=for-the-badge&logo=c%2B%2B" />
  <img src="https://img.shields.io/badge/Python-C2%20Server-yellow?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/License-MIT-red?style=for-the-badge" />
</p>

---

## 📸 Visual Proof (Demo)

### 🖥️ Main Dashboard
<p align="center">
  <img src="assets/dashboard.png" width="85%" style="border-radius: 10px;" />
  <br><em>Interfaz principal con gestión de agentes en tiempo real.</em>
</p>

### 👁️ Live Surveillance (Screenshot Module)
<p align="center">
  <img src="assets/screen_view.png" width="85%" style="border-radius: 10px;" />
  <br><em>Visor de capturas de pantalla integrando bypass de caché del navegador.</em>
</p>

### ⌨️ Keylogger Data Exfiltration
<p align="center">
  <img src="assets/dump_view.png" width="85%" style="border-radius: 10px;" />
  <br><em>Resultado del comando 'dump' mostrando la recuperación de pulsaciones.</em>
</p>

---

## 📖 Descripción
**G3-FLASH** es una plataforma de Comando y Control (C2) de grado de investigación diseñada para demostrar la interacción compleja entre implantes de bajo nivel y servidores de control modernos.

---

## 🛠️ Arquitectura Técnica

### 🛡️ Agente (Implante C++ Native)
* **📸 Vigilancia por GDI+:** Captura de pantalla en tiempo real con sistema de bloqueo de ámbito.
* **⌨️ Keylogger Multihilo:** Basado en `SetWindowsHookEx` para captura asíncrona.
* **📂 Motor de Exfiltración:** Transmisión de archivos mediante buffers dinámicos de `std::vector`.

### 💻 Panel de Control (Python/Flask)
* **🔗 Sincronización de Sockets:** Lógica avanzada para manejar fragmentación de paquetes TCP.
* **📟 Dashboard Cyberpunk:** UI responsiva con Bootstrap 5 y estética Dark Terminal.

---

## 🚀 Guía de Despliegue

### 1. Compilación del Implante (Windows/MinGW)
\`\`\`bash
g++ main.cpp -o agente.exe -lws2_32 -ladvapi32 -lgdiplus -lgdi32 -mwindows -static -pthread
\`\`\`

### 2. Inicio del Servidor (Kali Linux)
\`\`\`bash
pip install flask
python3 web_server.py
\`\`\`

---

## ⚠️ Propósitos Educativos (Disclaimer)
Este software ha sido desarrollado con el único propósito de **educar** en ciberseguridad. El uso de esta herramienta en redes ajenas es **ilegal**.

---
<p align="center">
  <b>Desarrollado por ramiactivated | 2026</b>
</p>
