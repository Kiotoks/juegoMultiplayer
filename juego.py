import pygame
import sys
import math
import socket
import threading
import json


HOST = "localhost"  # Dirección del servidor
PORT = 8000  # Puerto del servidor

# Inicializa Pygame
pygame.init()

GRID_SIZE = 40
CHAR_SIZE = GRID_SIZE
GRID_WIDTH = 30
GRID_HEIGHT = 20
RED = (255, 0, 0)

WIDTH, HEIGHT = GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_WIDTH

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survival")

# Configura la posición inicial del personaje
CHAR_X, CHAR_Y = GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE
CHAR_SPEED = GRID_SIZE

# Carga las imágenes de la grilla
worldfile = []
blockSounds = []
worldSprites = []

for i in range(3):
    worldSprites.append(pygame.image.load(f'cell{i}.png'))
    worldSprites[i] = pygame.transform.scale(worldSprites[i], (GRID_SIZE, GRID_SIZE))

for i in range(3):
    blockSounds.append(pygame.mixer.Sound(f'block{i}.wav'))

# Reloj para controlar los FPS
clock = pygame.time.Clock()

# Controla el estado de movimiento
CHAR_SIZE = 35
movimiento = False
CHAR_X, CHAR_Y = WIDTH // 2, HEIGHT // 2
CHAR_SPEED = 3
CHAR_VX = 0
CHAR_VY = 0
online = False
clientes = []
bufferBloques = []
bloqueSeleccionado = 2
timeout = 0

spritepj = pygame.image.load(f'sprite.png')
spritepj = pygame.transform.scale(spritepj, (CHAR_SIZE, CHAR_SIZE))


# Reloj para controlar los FPS
clock = pygame.time.Clock()

def readWorldData():
    worldfile = open("world.txt","r").readlines()
    for i in range(len(worldfile)):
        worldfile[i] = worldfile[i][:-1]
        worldfile[i] = list(worldfile[i])

    newWorldFile = []
    for x in worldfile:
        newLine = []
        for y in x:
            newLine.append(int(y))
        newWorldFile.append(newLine)

    return newWorldFile

def cambiarCoordsAGrid(x,y):
    return  math.trunc(x/GRID_SIZE) , math.trunc(y/GRID_SIZE)

def getBlockInGrid(x,y):
    return int(worldfile[y][x])

def cambiarBloque(x, y , id):
    if worldfile[y][x] != id:
        if id != 0:
            if abs(x*40 - CHAR_X) <= 40 and abs(y*40 - CHAR_Y) <= 40:
                return
        pygame.mixer.Sound.play(blockSounds[id])
        worldfile[y][x] = id
        bufferBloques.append({"x":x, "y":y, "id":id})

def chequearColisionAxis(futuro_x, futuro_y):
    future_grid_corners = [
        cambiarCoordsAGrid(futuro_x, futuro_y),  # esquina superior izquierda
        cambiarCoordsAGrid(futuro_x + CHAR_SIZE, futuro_y),  # esquina superior derecha
        cambiarCoordsAGrid(futuro_x, futuro_y + CHAR_SIZE),  # esquina inferior izquierda
        cambiarCoordsAGrid(futuro_x + CHAR_SIZE, futuro_y + CHAR_SIZE)  # esquina inferior derecha
    ]
    
    for corner in future_grid_corners:
        if getBlockInGrid(*corner) == 2:
            return True
    return False

def manejarComunicacionCliente(cliente):
    
    while True:
        try:
            if bufferBloques:
                cliente.send(json.dumps({"bloque":bufferBloques[0]}).encode('utf-8'))
                bufferBloques.pop(0)
        except:
            # Si hay un error, cierra la conexión con el cliente
            cliente.close()
            for i in range(0, len(clientes)):
                if cliente == clientes[i]:
                    clientes.pop(i)
            break

def atenderClientes(server):
    print("arranca a atender clientes")
    while True:
        try:
            cliente, direccion = server.accept()
            print(f"[CONEXIÓN] Cliente conectado desde {direccion}")

            clientes.append(cliente)

            # Crea un hilo para atender al cliente
            hilo_cliente = threading.Thread(target=manejarComunicacionCliente, args=(cliente,))
            hilo_cliente.start()
        except:
            print("error 1")

def recibirMensajes(server):
    print("tremendo")
    while True:
        try:
            # Recibe mensajes del servidor
            data = server.recv(1024).decode('utf-8')
            json_data = json.loads(data)
            print("Datos recibidos del cliente:", json_data)
            if json_data["bloque"]:
                bloque = json_data["bloque"]
                cambiarBloque(bloque["x"], bloque["y"], bloque["id"])

        except:
            # Si hay un error, cierra la conexión con el servidor
            server.close()
            global conexionEstablecida 
            conexionEstablecida = False
            print("Conexión con el servidor cerrada.")
            return

def abrirServidor():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un socket TCP
        server.bind((HOST, PORT))  # Asocia el socket a la dirección y puerto
        server.listen(5)  # Pone el socket en modo escucha
        print("[SERVIDOR] Servidor iniciado")
        listener = threading.Thread(target=atenderClientes, args=(server,))
        listener.start()
    except:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un socket TCP
        server.connect((HOST, PORT))  # Se conecta al servidor
        listener = threading.Thread(target=recibirMensajes, args=(server,))
        listener.start()
        print("Servidor ya iniciado, modo cliente")
        return

worldfile = readWorldData()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Obtén las teclas presionadas
    keys = pygame.key.get_pressed()
    
    
    if keys[pygame.K_m] and not online:
        abrirServidor()
        online = True

    if keys[pygame.K_w]:
        CHAR_VY = -1
    if keys[pygame.K_s]:
        CHAR_VY = 1
    
    if keys[pygame.K_a]:
        CHAR_VX = -1
    if keys[pygame.K_d]:
        CHAR_VX = 1
    
    if CHAR_VY != 0 and CHAR_VX != 0:
        CHAR_VX = CHAR_VX/1.414 
        CHAR_VY = CHAR_VY/1.414

    # Calcular la posición futura
    futuro_x = CHAR_X + CHAR_VX * CHAR_SPEED
    futuro_y = CHAR_Y + CHAR_VY * CHAR_SPEED
    
    # Convertir las coordenadas futuras a coordenadas de grilla
    if chequearColisionAxis(futuro_x, CHAR_Y):
        CHAR_VX = 0
    if chequearColisionAxis(CHAR_X, futuro_y):
        CHAR_VY = 0
        

    CHAR_X += CHAR_VX * CHAR_SPEED
    CHAR_Y += CHAR_VY * CHAR_SPEED

    CHAR_VX = 0
    CHAR_VY = 0

    if  pygame.mouse.get_pressed() and movimiento:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cell_x , cell_y = cambiarCoordsAGrid(mouse_x, mouse_y)
        if pygame.mouse.get_pressed()[2]:
            cambiarBloque(cell_x, cell_y, bloqueSeleccionado)
        elif pygame.mouse.get_pressed()[0]:
            cambiarBloque(cell_x, cell_y, 0)
        movimiento = False
    
    if timeout != 0:
        timeout -= 1

    if event.type == pygame.MOUSEMOTION:
        movimiento = True

    # Asegúrate de que el personaje no se salga de la ventana
    CHAR_X = max(0, min(CHAR_X, WIDTH - CHAR_SIZE))
    CHAR_Y = max(0, min(CHAR_Y, HEIGHT - CHAR_SIZE))

    # Dibuja el fondo
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            WIN.blit(worldSprites[getBlockInGrid(x,y)], (x * GRID_SIZE, y * GRID_SIZE))

    # Dibuja el personaje
    WIN.blit(spritepj,(CHAR_X, CHAR_Y, CHAR_SIZE, CHAR_SIZE))
    
    # Actualiza la pantalla
    pygame.display.flip()
    
    # Controla los FPS
    clock.tick(60)  # Ajusta los FPS según lo necesites
