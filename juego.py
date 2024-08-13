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
GRID_WIDTH = 30
GRID_HEIGHT = 20

WIDTH, HEIGHT = GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_WIDTH

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survival")

# Carga las imágenes de la grilla
worldfile = []
blockSounds = []
worldSprites = []
enemSprites = []

for i in range(3):
    worldSprites.append(pygame.image.load(f'cell{i}.png'))
    worldSprites[i] = pygame.transform.scale(worldSprites[i], (GRID_SIZE, GRID_SIZE))

for i in range(3):
    blockSounds.append(pygame.mixer.Sound(f'block{i}.wav'))

for i in range(1):
    enemSprites.append(pygame.image.load(f'enem{i}.png'))
    enemSprites[i] = pygame.transform.scale(enemSprites[i], (GRID_SIZE, GRID_SIZE))

# Reloj para controlar los FPS
clock = pygame.time.Clock()

# Controla el estado de movimiento
CHAR_SIZE = 35
CHAR_X, CHAR_Y = WIDTH // 2, HEIGHT // 2
SCX = 0
SCY = 0
CHAR_SPEED = 3
CHAR_VX = 0
CHAR_VY = 0
VIDA = 10

online = False
movimiento = False

dmgCooldown = 0
primaryCooldown = 0
timeout = 0

bloqueSeleccionado = 2

clientes = []
bufferBloques = []
proyectiles = []
enemies = []

font = pygame.font.Font('freesansbold.ttf', 32)
fps = 70

spritepj = pygame.image.load(f'sprite.png')
spritepj = pygame.transform.scale(spritepj, (CHAR_SIZE, CHAR_SIZE))


# Reloj para controlar los FPS
clock = pygame.time.Clock()


class Projectile:
    def __init__(self, x, y, vx, vy, v, size, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.v = v

    def update(self):
        self.x += self.vx * self.v
        self.y += self.vy * self.v

    def checkCol(self, enemies):
        if self.x > WIDTH or self.x < 0:
            return True
        if self.y > HEIGHT or self.y < 0:
            return True
        if getBlockInGrid(*cambiarCoordsAGrid(self.x, self.y)):
            return True
        for e in enemies:
            ex , ey = e.coords()
            if abs( ex - self.x) <= e.size and abs(ey - self.y) <= e.size:
                e.applyDmg()
                return True
            

    def draw(self, screen):
        self.update()
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)


class Enemy:
    def __init__(self, x, y, v, size, type, color, enemSprites, vida):
        self.x = x
        self.y = y
        self.size = size
        self.type = type
        self.color = color
        self.vida = vida
        self.v = v
        self.sprite = enemSprites[type]
        self.cooldown = 0
    
    def applyDmg(self):
        if self.vida > 0 and not self.cooldown:
            self.vida -= 1
            self.cooldown = 5
        print(self.vida)
        

    def coords(self):
        return self.x + self.size/2, self.y + self.size/2

    def draw(self, screen):
        screen.blit(self.sprite,(self.x, self.y, self.size, self.size))
        if self.cooldown > 0:
            self.cooldown -= 1


def readWorldData(name):
    worldfile = open(name,"r").readlines()
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
def getBlockInBack(x,y):
    return int(background[y][x])

def cambiarBloque(x, y , id, out):
    if worldfile[y][x] != id:
        if id != 0:
            if abs(x*40 - CHAR_X) <= 40 and abs(y*40 - CHAR_Y) <= 40:
                return
        pygame.mixer.Sound.play(blockSounds[id])
        worldfile[y][x] = id
        if not out :
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
            mensaje = {"pos":{"x":0,"y":0}}

            if bufferBloques:
                mensaje["bloque"] = bufferBloques[0]
                bufferBloques.pop(0)

            mensaje["pos"] = {"x": CHAR_X, "y":CHAR_Y}

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
            break
        time.sleep(delay)

def recibir(server):
    delay = 1 / fps
    global SCX
    global SCY
    buffer = ""
    
    while True:
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
                    
                    # Procesar el objeto JSON
                    if "bloque" in json_data:
                        bloque = json_data["bloque"]
                        cambiarBloque(bloque["x"], bloque["y"], bloque["id"], True)
                    
                    if "pos" in json_data:
                        pos = json_data["pos"]
                        SCX = pos["x"]
                        SCY = pos["y"]
                
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
    bufferBloques = []
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un socket TCP
        server.bind((HOST, PORT))  # Asocia el socket a la dirección y puerto
        server.settimeout(60)
        server.listen(5)  # Pone el socket en modo escucha
        print("[SERVIDOR] Servidor iniciado")
        listener = threading.Thread(target=atenderClientes, args=(server,))
        listener.start()
    except:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un socket TCP
        server.connect((HOST, PORT))
        server.settimeout(60)  # Se conecta al servidor
        listener = threading.Thread(target=recibir, args=(server,))
        sender = threading.Thread(target=enviar, args=(server,))
        fps = 70
        listener.start()
        sender.start()
        print("Servidor ya iniciado, modo cliente")
        return

def getNormDir(x1, y1, x2, y2):
    # Step 1: Calculate the direction vector
    dx = x2 - x1
    dy = y2 - y1

    magnitude = math.sqrt(dx**2 + dy**2)

    # Step 3: Normalize the direction vector
    if magnitude != 0:
        dx /= magnitude
        dy /= magnitude

    return dx, dy


def die():
    global CHAR_X, CHAR_Y, HEIGHT, WIDTH, VIDA
    CHAR_X = WIDTH/2
    CHAR_Y = HEIGHT/2
    VIDA = 10

def applyDmg():
    global VIDA
    if VIDA > 0:
        VIDA -= 1
        print(VIDA)
    if not VIDA:
        die()

def renderUI():
    global font, WIN, VIDA
    color = (255,255,255)
    text = font.render(f"Life: {VIDA}", True, color)
    WIN.blit(text, (10, 10)) 

worldfile = readWorldData("world.txt")
background = readWorldData("back.txt")

enemies.append(Enemy(100, 100, 3, 40, 0, (255,255,255), enemSprites, 10))

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

    if VIDA:
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
    gx = CHAR_X+CHAR_SIZE/2
    gy = CHAR_Y+ CHAR_SIZE/2
    if getBlockInGrid(*cambiarCoordsAGrid(gx, gy)) == 1 and not dmgCooldown:
        applyDmg()
        dmgCooldown = 30

    CHAR_X += CHAR_VX * CHAR_SPEED
    CHAR_Y += CHAR_VY * CHAR_SPEED

    CHAR_VX = 0
    CHAR_VY = 0

    if  pygame.mouse.get_pressed() and movimiento and VIDA:

        mouse_x, mouse_y = pygame.mouse.get_pos()
        cell_x , cell_y = cambiarCoordsAGrid(mouse_x, mouse_y)

        if pygame.mouse.get_pressed()[2] and not primaryCooldown:

            px, py = getNormDir(CHAR_X, CHAR_Y, mouse_x, mouse_y)
            p = Projectile(gx, gy, px, py, 5, 10, (255,255,255))
            proyectiles.append(p)
            primaryCooldown = 45
            #cambiarBloque(cell_x, cell_y, bloqueSeleccionado, False)

        elif pygame.mouse.get_pressed()[0]:

            cambiarBloque(cell_x, cell_y, 0, False)

        movimiento = False
    
    if timeout != 0:
        timeout -= 1
    if dmgCooldown:
        dmgCooldown -= 1
    if primaryCooldown:
        primaryCooldown -= 1

    if event.type == pygame.MOUSEMOTION:
        movimiento = True

    # Asegúrate de que el personaje no se salga de la ventana
    CHAR_X = max(0, min(CHAR_X, WIDTH - CHAR_SIZE))
    CHAR_Y = max(0, min(CHAR_Y, HEIGHT - CHAR_SIZE))

    # Dibuja el fondo
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            block = getBlockInGrid(x,y)
            if getBlockInGrid(x,y) == 0:
                WIN.blit(worldSprites[getBlockInBack(x, y)], (x * GRID_SIZE, y * GRID_SIZE))
            else:
                WIN.blit(worldSprites[block], (x * GRID_SIZE, y * GRID_SIZE))

    for p in proyectiles:
        p.draw(WIN)
        if p.checkCol(enemies):
            proyectiles.remove(p)
    
    for e in enemies:
        ex , ey = e.coords()
        if abs( ex - gx) <= e.size and abs(ey - gy) <= e.size:
            if not dmgCooldown:
                applyDmg()
                dmgCooldown = 30
        if e.vida < 1:
            enemies.remove(e)
        e.draw(WIN)

    # Dibuja el personaje
    WIN.blit(spritepj,(CHAR_X, CHAR_Y, CHAR_SIZE, CHAR_SIZE))

    if SCX and SCY:
        WIN.blit(spritepj,(SCX, SCY, CHAR_SIZE, CHAR_SIZE))
    
    renderUI()

    # Actualiza la pantalla
    pygame.display.flip()
    
    # Controla los FPS
    clock.tick(fps)  # Ajusta los FPS según lo necesites
