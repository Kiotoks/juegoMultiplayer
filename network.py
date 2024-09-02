import socket
import threading
import json


HOST = "localhost"  # Dirección del servidor
PORT = 8000  # Puerto del servidor
clientes = []
server = None

def enviar(CHAR_X, CHAR_Y, bufferMensajes):
    for cliente in clientes:
        try:
            mensaje = {"events": []}
            mensaje["events"].append({"pos":{"x":CHAR_X,"y":CHAR_Y}})

            for m in bufferMensajes:
                mensaje["events"].append(m)

            bufferMensajes = []

            cliente.send(json.dumps(mensaje).encode('utf-8'))
            
        except Exception as e:
            print("error enviando")
            print(mensaje)
            print(e)
            # Si hay un error, cierra la conexión con el cliente
            cliente.close()
            for i in range(0, len(clientes)):
                if cliente == clientes[i]:
                    clientes.pop(i)


def recibir():
    for server in clientes:
        buffer = ""
        try:
            # Recibir datos del servidor
            data = server.recv(1024).decode('utf-8')
            buffer += data
            
            # Procesar los datos en el buffer
            while True:
                try:
                    # Intentar cargar un objeto JSON desde el buffer
                    json_data, index = json.JSONDecoder().raw_decode(buffer)
                    buffer = buffer[index:].lstrip()
                    return json_data["events"]
                    
                except json.JSONDecodeError:
                    # Si no se puede decodificar más, salir del bucle interno
                    break
            
        except Exception as e:
            print("error recibiendo:", buffer)
            print(e)
            # Si hay un error, cierra la conexión con el servidor
            server.close()
            for i in range(len(clientes)):
                if server == clientes[i]:
                    clientes.pop(i)

def atenderClientes(server):
    print("arranca a atender clientes")
    while True:
        try:
            cliente, direccion = server.accept()
            print(f"[CONEXIÓN] Cliente conectado desde {direccion}")
            clientes.append(cliente)
        except Exception as e:
            print("error 1", e)

def abrirServidor():
    global server
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un socket TCP
        server.bind((HOST, PORT))  # Asocia el socket a la dirección y puerto
        server.listen(5)  # Pone el socket en modo escucha
        print("[SERVIDOR] Servidor iniciado")
        listener = threading.Thread(target=atenderClientes, args=(server,))
        listener.start()
        return "server"
    except:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un socket TCP
        server.connect((HOST, PORT))
        clientes.append(server)
        print("Servidor ya iniciado, modo cliente")
        return "client"