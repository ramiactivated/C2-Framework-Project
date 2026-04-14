⚡ G3-FLASH | Advanced Command & Control Framework
G3-FLASH es una plataforma de Comando y Control (C2) de grado de investigación diseñada para demostrar la interacción compleja entre implantes de bajo nivel y servidores de control modernos. El proyecto se enfoca en la exfiltración binaria, la vigilancia en tiempo real y la persistencia en sistemas Windows.

🛠️ Arquitectura Técnica
El sistema se divide en dos componentes críticos que se comunican mediante un protocolo TCP personalizado, diseñado para manejar flujos de datos mixtos (texto y binario).

1. El Implante (C++ Native)
Desarrollado para ser ligero y eficiente, interactuando directamente con las APIs de Windows:

Vigilancia por GDI+: Captura de pantalla en tiempo real. Utiliza un sistema de bloqueo de ámbito para garantizar la liberación de handles de archivos y evitar colisiones de E/S.

Keylogger Multihilo: Basado en SetWindowsHookEx (WH_KEYBOARD_LL) para capturar pulsaciones de forma asíncrona sin bloquear el hilo principal de comunicación.

Motor de Exfiltración Binaria: Capacidad de lectura y transmisión de archivos mediante buffers dinámicos de std::vector, permitiendo el robo de datos de cualquier formato (PDF, DOCX, EXE).

Persistencia Silenciosa: Implementa técnicas de replicación en %APPDATA% y modificación del registro de Windows (HKCU\Run) para asegurar el inicio automático tras el reinicio del sistema.

Identificación Dinámica: Recolección automática de metadatos del sistema (Hostname/Username) en el handshake inicial.

2. Panel de Control (Python/Flask)
Un centro de mando táctico que prioriza la visualización de datos y la gestión de múltiples activos:

Protocolo de Sincronización de Sockets: Lógica avanzada para manejar la fragmentación de paquetes TCP, permitiendo recibir archivos grandes sin desincronizar el flujo de comandos.

Dashboard Cyberpunk: UI responsiva con Bootstrap 5 y FontAwesome, optimizada para la legibilidad en entornos de operaciones de seguridad.

Gestor de Visores: Implementación de un visor de capturas de pantalla con técnicas de Cache Busting (parámetros de tiempo dinámicos) para visualización inmediata.

Multithreading: Capacidad de manejar conexiones concurrentes mediante hilos dedicados para cada agente conectado.

📂 Estructura del Proyecto
.
├── agent/
│   ├── main.cpp         # Código fuente del implante (C++)
│   └── icons/           # Recursos visuales opcionales
├── server/
│   ├── web_server.py    # Backend Flask y motor de sockets
│   ├── templates/       # Dashboard HTML (Bootstrap 5)
│   └── downloads/       # Repositorio de exfiltración (Loot)
└── README.md


🚀 Guía de Despliegue
Compilación del Implante (Windows)
Se requiere MinGW-w64 para una compilación estática que no dependa de DLLs externas:
Bash
g++ main.cpp -o agente.exe -lws2_32 -ladvapi32 -lgdiplus -lgdi32 -mwindows -static -pthread

Parametrización:

-lws2_32: Librería de red (Winsock).

-lgdiplus: Librería de gráficos para screenshots.

-mwindows: Ejecución oculta (sin consola).

-static: Incluye todas las dependencias en el binario.

Inicio del Servidor (Kali Linux)
Instalar dependencias: pip install flask

Ejecutar:
python3 web_server.py



📋 Comandos Disponibles en el Panel
Comando,Acción,Descripción
screenshot,Vigilancia,Toma una captura de pantalla y la muestra en el modal.
download [ruta],Exfiltración,Descarga un archivo desde la víctima a la carpeta /downloads.
dump,Keylogger,Recupera todas las pulsaciones de teclas capturadas hasta el momento.
[cualquier otro],RCE,Ejecuta comandos directamente en la CMD de la víctima.

🛡️ Propósitos Educativos (Disclaimer)
 el único propósito es educar a estudiantes y profesionales de la ciberseguridad sobre el funcionamiento de las amenazas persistentes.

No debe ser utilizado en sistemas sin autorización explícita.

El uso de esta herramienta en redes ajenas es ilegal y bajo la responsabilidad del usuario final.

Se recomienda su uso en entornos controlados (Laboratorios de Virtualización).
