import pygame
import sys
import math
import threading
import os
import time
import generacionProcedural as gp
import classes
import network as nt

# Inicializa Pygame
pygame.init()

GRID_SIZE = 40
GRID_WIDTH = 30
GRID_HEIGHT = 20

WIDTH, HEIGHT = GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_WIDTH
classes.setDim(HEIGHT, WIDTH)
 
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survival")

# Carga las imágenes de la grilla
worldfile = []
blockSounds = []
worldSprites = []
enemSprites = []
bufferMensajes = []

cwd = os.getcwd()

for i in range(7):
    worldSprites.append(pygame.image.load(f'{cwd}/files/sprites/cell{i}.png'))
    worldSprites[i] = pygame.transform.scale(worldSprites[i], (GRID_SIZE, GRID_SIZE))

"""for i in range(3):
    blockSounds.append(pygame.mixer.Sound(f'{cwd}/files/sounds/block{i}.wav'))
"""
for i in range(1):
    enemSprites.append(pygame.image.load(f'{cwd}/files/sprites/enem{i}.png'))
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

cantEnemigos = 0

online = False
isHost = False

movimiento = False

dmgCooldown = 0
primaryCooldown = 0
timeout = 0
uiCooldown = 0 

bloqueSeleccionado = 2

bufferBloques = []
proyectiles = []
entities = []

font = pygame.font.Font('freesansbold.ttf', 32)
fps = 70

spritepj = pygame.image.load(f'{cwd}/files/sprites/sprite.png')
spritepj = pygame.transform.scale(spritepj, (CHAR_SIZE, CHAR_SIZE))
piuSprite = pygame.image.load(f'{cwd}/files/sprites/projectile.png')


# Reloj para controlar los FPS
clock = pygame.time.Clock()

class Slime(classes.Enemy):
    def __init__(self, x, y, id):
        super().__init__(x, y, 3, 40, enemSprites[0], 5, "slime", id)

class Fireball(classes.Projectile):
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y, 5, 20, piuSprite, vx, vy, 2)

def readWorldData(name):
    global cwd
    worldfile = open(cwd+"/files/saves/"+name+".txt","r").readlines()
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


def entrarDungeon():
    pass

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
        #pygame.mixer.Sound.play(blockSounds[id])
        worldfile[y][x] = id
        if not out :
            bufferMensajes.append({"bloque":{"x":x, "y":y, "id":id}})

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

def enviar():
    delay = 1/(fps)
    global bufferMensajes
    while True:
        nt.enviar(CHAR_X, CHAR_Y, bufferMensajes)
        bufferMensajes = []
        time.sleep(delay)

def handleMsg(msg):
# Procesar el objeto JSON
    global SCX, SCY
    print(msg)
    if "bloque" in msg:
        bloque = msg["bloque"]
        cambiarBloque(bloque["x"], bloque["y"], bloque["id"], True)
    
    elif "pos" in msg:
        pos = msg["pos"]
        SCX = pos["x"]
        SCY = pos["y"]

    elif "projectile" in msg:
        p = msg["projectile"]
        entities.append(Fireball(p["x"], p["y"], p["vx"], p["vy"]))
    
    elif "enemy" in msg:
        e = msg["enemy"]
        encontrado = False
        if not isHost:
            for en in entities:
                if en.type == "enemy" and en.id == e["id"]:
                    en.x = e["x"]
                    en.y = e["y"]
                    print("encontrado")
                    encontrado = True
            if not encontrado:
                entities.append(Slime(e["x"], e["y"], e["id"]))

def recibir():
    delay = 1 / fps
    while True:
        time.sleep(delay)
        mensajes = nt.recibir()
        if mensajes != None:
            for m in mensajes:
                handleMsg(m)
    pass

def abrirServidor():
    role = nt.abrirServidor()
    if role == "server":
        isHost = True
    
    hilo_enviar = threading.Thread(target=enviar)
    hilo_enviar.start()
    hilo_recibir= threading.Thread(target=recibir)
    hilo_recibir.start()

def die():
    global CHAR_X, CHAR_Y, HEIGHT, WIDTH, VIDA
    CHAR_X = WIDTH/2
    CHAR_Y = HEIGHT/2
    VIDA = 10

def applyDmg():
    global VIDA, dmgCooldown
    if VIDA > 0:
        VIDA -= 1
        print(VIDA)
    if not VIDA:
        die()
    dmgCooldown = 30

def renderUI():
    global font, WIN, VIDA, bloqueSeleccionado
    #renderizar vida
    color = (255,255,255)
    text = font.render(f"Life: {VIDA}", True, color)
    WIN.blit(text, (10, 10))
    #renderizar bloque seleccionado
    pygame.draw.rect(WIN, (255,255,255), pygame.Rect(17, HEIGHT - 23 - GRID_SIZE, GRID_SIZE+ 6, GRID_SIZE + 6))
    WIN.blit(worldSprites[bloqueSeleccionado], (20, HEIGHT - 20 - GRID_SIZE))

def crearHabitacion(): #solo debug
    with open(f"{cwd}/files/saves/room.txt", "w") as file:
        for row in worldfile:
            strRow = ""
            for number in row:
                strRow += str(number)

            file.write(strRow + "\n")

def disparar(pro, x, y, vx, vy):
    global cantEnemigos
    match pro:
        case "fireball":
            p = Fireball(x, y, vx, vy)
            bufferMensajes.append({"projectile":{"x": x, "y": y, "vx": vx, "vy": vy}})
            entities.append(p)
        case "slime":
            s = Slime(300, 300, cantEnemigos)
            bufferMensajes.append({"enemy":{"x": 300, "y": 300, "id": cantEnemigos}})
            entities.append(s)
            cantEnemigos += 1
            
worldfile = readWorldData("world")
background = readWorldData("back")
#disparar("slime",500, 500, 0,0)
guardado = False
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
    if keys[pygame.K_g] and not guardado:
        crearHabitacion()
        guardado = True
    if keys[pygame.K_o]:
        worldfile = readWorldData("room")
    
    if not uiCooldown:
        if keys[pygame.K_q]:
            if bloqueSeleccionado > 0:
                bloqueSeleccionado -= 1
            uiCooldown = 10
        if keys[pygame.K_e]:
            if bloqueSeleccionado < len(worldSprites) - 1:
                bloqueSeleccionado += 1
            uiCooldown = 10
    

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

    bloqueParado = getBlockInGrid(*cambiarCoordsAGrid(gx, gy))
    if bloqueParado == 1 and not dmgCooldown:
        applyDmg()
    
    if bloqueParado == 6:
        entrarDungeon()
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
            if isHost:
                disparar("slime", gx, gy, px, py)
            else:
                disparar("fireball", gx, gy, px, py)
            primaryCooldown = 45



        elif pygame.mouse.get_pressed()[0]:

            cambiarBloque(cell_x, cell_y, bloqueSeleccionado, False)

        movimiento = False
    
    if timeout != 0:
        timeout -= 1
    if dmgCooldown:
        dmgCooldown -= 1
    if primaryCooldown:
        primaryCooldown -= 1
    if uiCooldown > 0:
        uiCooldown -= 1

    if event.type == pygame.MOUSEMOTION:
        movimiento = True

    # Asegúrate de que el personaje no se salga de la ventana
    CHAR_X = max(0, min(CHAR_X, WIDTH - CHAR_SIZE))
    CHAR_Y = max(0, min(CHAR_Y, HEIGHT - CHAR_SIZE))

    WIN.fill((0,0,0))

    # Dibuja el fondo
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            block = getBlockInGrid(x,y)
            if getBlockInGrid(x,y) == 0:
                WIN.blit(worldSprites[getBlockInBack(x, y)], (x * GRID_SIZE, y * GRID_SIZE))
            else:
                WIN.blit(worldSprites[getBlockInBack(x, y)], (x * GRID_SIZE, y * GRID_SIZE))
                WIN.blit(worldSprites[block], (x * GRID_SIZE, y * GRID_SIZE))


    for e in entities:
        if e.type == "projectile":
            col = e.checkCol(entities, getBlockInGrid(*cambiarCoordsAGrid(e.x, e.y)))
            if col:
                entities.remove(e)
        elif e.type == "enemy":
            ex , ey = e.coords()
            if e.vida < 1:
                entities.remove(e)
            else:
                if abs(ex - gx) <= e.size and abs(ey - gy) <= e.size:
                    if not dmgCooldown:
                        applyDmg()
                        dmgCooldown = 30
        
        msg = e.draw(WIN, isHost)
        if msg != None:
            bufferMensajes.append(msg)
        

    # Dibuja el personaje
    WIN.blit(spritepj,(CHAR_X, CHAR_Y, CHAR_SIZE, CHAR_SIZE))

    if SCX and SCY:
        WIN.blit(spritepj,(SCX, SCY, CHAR_SIZE, CHAR_SIZE))
    
    renderUI()

    # Actualiza la pantalla
    pygame.display.flip()
    
    # Controla los FPS
    clock.tick(fps)  # Ajusta los FPS según lo necesites
