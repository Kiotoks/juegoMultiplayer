import pygame
import sys
import math
import socket
import threading
import json
import time


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
SCX = 0
SCY = 0
CHAR_SPEED = 3
CHAR_VX = 0
CHAR_VY = 0
online = False
clientes = []
bufferBloques = []
bloqueSeleccionado = 2
timeout = 0
fps = 70

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

def enviar(cliente):
    delay = 1/(fps)
    while True:
        try:
            mensaje = {"bloque":{}, "pos":{"x":0,"y":0}}

            if bufferBloques:
                mensaje["bloque"] = bufferBloques[0]
                bufferBloques.pop(0)

            mensaje["pos"] = {"x": CHAR_X, "y":CHAR_Y}

            cliente.send(json.dumps(mensaje).encode('utf-8'))
            
        except Exception as e:
            print("error enviando")
            print(e)
            # Si hay un error, cierra la conexión con el cliente
            cliente.close()
            for i in range(0, len(clientes)):
                if cliente == clientes[i]:
                    clientes.pop(i)
            break
        time.sleep(delay)

def recibir(server):
    delay = 1/(fps)
    global SCX
    global SCY
    while True:
        try:
            data = server.recv(1024).decode('utf-8')
            json_data = json.loads(data)
            if json_data["bloque"]:
                bloque = json_data["bloque"]
                cambiarBloque(bloque["x"], bloque["y"], bloque["id"])
            
            pos =json_data["pos"]
            SCX = pos["x"]
            SCY = pos["y"]
        except Exception as e:
            print("error recibiendo")
            print(e)
            # Si hay un error, cierra la conexión con el servidor
            server.close()
            for i in range(0, len(clientes)):
                if server == clientes[i]:
                    clientes.pop(i)
            break
        time.sleep(delay)


def atenderClientes(server):
    print("arranca a atender clientes")
    while True:
        try:
            cliente, direccion = server.accept()
            print(f"[CONEXIÓN] Cliente conectado desde {direccion}")

            clientes.append(cliente)

            # Crea un hilo para atender al cliente
            hilo_enviar = threading.Thread(target=enviar, args=(cliente,))
            hilo_enviar.start()
            hilo_recibir= threading.Thread(target=recibir, args=(cliente,))
            hilo_recibir.start()
        except:
            print("error 1")

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
        listener = threading.Thread(target=recibir, args=(server,))
        sender = threading.Thread(target=enviar, args=(server,))
        fps = 70
        listener.start()
        sender.start()
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
    if SCX and SCY:
        WIN.blit(spritepj,(SCX, SCY, CHAR_SIZE, CHAR_SIZE))
    
    # Actualiza la pantalla
    pygame.display.flip()
    
    # Controla los FPS
    clock.tick(fps)  # Ajusta los FPS según lo necesites
