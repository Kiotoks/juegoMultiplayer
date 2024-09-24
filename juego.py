import pygame
import sys
import math
import threading
import os
import json
import time
import generacionProcedural as gp
import classes
import network as nt

# Inicializa Pygame
pygame.init()

GRID_SIZE = 40
GRID_WIDTH = 30
GRID_HEIGHT = 15

WIDTH = GRID_WIDTH * GRID_SIZE
HEIGHT = GRID_HEIGHT * GRID_SIZE

classes.setDim(HEIGHT, WIDTH)
 
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survival")

# Carga las imágenes de la grilla
worldfile = []
blockSounds = []
worldSprites = []
enemSprites = []
tileSprites = []
bufferMensajes = []
MAP_SIZE = 10

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

for i in range(16):
    tileSprites.append(pygame.image.load(f'{cwd}/files/maptiles/tile{i}.png'))
    tileSprites[i] = pygame.transform.scale(tileSprites[i], (MAP_SIZE, MAP_SIZE))

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

DNG_X = 0
DNG_Y = 0

cantEnemigos = 0

online = False
isHost = False
isOnDng = False

movimiento = False

dmgCooldown = 0
primaryCooldown = 0
timeout = 0
uiCooldown = 0 

bloqueSeleccionado = 2

bufferBloques = []
proyectiles = []
entities = []
nivel = 0
ronda = 0

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
    with open(cwd+"/files/data/world.json", 'r') as archivo:
        datos = json.load(archivo)
    return datos[name]

#crear funcion de cargar habitacion que se base por las cordenadas de la dungeon
#solucionar el tema de tener un solo 

def cambiarBloque(x, y , id, out):
    if worldfile[y][x] != id:
        if id != 0:
            if abs(x*40 - CHAR_X) <= 40 and abs(y*40 - CHAR_Y) <= 40:
                return
        #pygame.mixer.Sound.play(blockSounds[id])
        worldfile[y][x] = id
        if not out :
            bufferMensajes.append({"bloque":{"x":x, "y":y, "id":id}})


def colocarPuertas(sides):
    def ponerMuro(x, y):
        worldfile[y][x] = 0
    print(sides)
    bloque = 0
    if sides[3] == 1:
        print("puerta izquierda")
        ponerMuro(0, math.trunc(GRID_HEIGHT/2))
        ponerMuro(0, math.trunc(GRID_HEIGHT/2)+1)
    if sides[0]  == 1:
        print("puerta arriba")
        ponerMuro(math.trunc(GRID_WIDTH/2), 0)
        ponerMuro(math.trunc(GRID_WIDTH/2)+1, 0)
    if sides[1]  == 1:
        print("puerta derecha")
        ponerMuro(GRID_WIDTH-1, math.trunc(GRID_HEIGHT/2))
        ponerMuro(GRID_WIDTH-1, math.trunc(GRID_HEIGHT/2)+1)
    if sides[2]  == 1:
        print("puerta abajo")
        ponerMuro(math.trunc(GRID_WIDTH/2), GRID_HEIGHT-1)
        ponerMuro(math.trunc(GRID_WIDTH/2)+1, GRID_HEIGHT-1)


def crearBorde(sides):
    global worldfile
    bloqueBorde = 2
    print("ly", len(worldfile))
    print("lxdw",(worldfile[0]))
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if x  ==  0 or y == 0:
                worldfile[y][x] =  bloqueBorde
            if x  ==  GRID_WIDTH-1 or y == GRID_HEIGHT-1:
                worldfile[y][x] =  bloqueBorde
    colocarPuertas(sides)
    
def cargarEnemigos(enemArray, ronda):
    global entities, cantEnemigos
    for e in enemArray[ronda]:
        if e["name"] == "slime":
            cantEnemigos += 1
            entities.append(Slime(e["x"], e["y"], cantEnemigos))

def cargarHabitacion(dy, dx):
    global worldfile, background, cwd, dungeon, ronda
    print(f"habitacion cargada y: {dy}, x: {dx}")
    bufferMensajes.append({"room":{"x":x, "y":y}})
    room = dungeon[dy][dx]
    nombre = room["room"]
    with open(cwd+"/files/data/rooms.json", 'r') as archivo:
        datos = json.load(archivo)
    #añadir spawn de enemigos
    background =  datos[nombre]["background"]
    worldfile = datos[nombre]["foreground"]
    crearBorde(room["sides"])
    ronda = 0
    cargarEnemigos(datos[nombre]["enemiesRounds"], ronda)

def entrarDungeon(lvl):
    global dungeon, CHAR_X, CHAR_Y, DNG_X, DNG_Y, isOnDng
    CHAR_X, CHAR_Y = WIDTH/2, HEIGHT/2
    levels = [(10, 10, 10)] #reemplazar en el futuro por un json
    lvldim = levels[lvl-1]
    bufferMensajes.append({"dungeon":{"d":"sas"}})
    isOnDng = True
    while True:
        try:
            dungeon, spawn = gp.generarDungeon(lvldim[0],lvldim[1], lvldim[2], lvl)
            print("spawn que llego:", spawn)
        except:
            print("fallo generacion")
        finally:
            break
    
    DNG_Y, DNG_X = spawn[0], spawn[1]
    
    cargarHabitacion(DNG_Y,DNG_X) 

    pass

def cambiarCoordsAGrid(x,y):
    return  math.trunc(x/GRID_SIZE) , math.trunc(y/GRID_SIZE)

def getBlockInGrid(x,y):
    x = min(x, GRID_WIDTH-1)
    y = min(y, GRID_HEIGHT-1)
    return int(worldfile[y][x])

def getBlockInBack(x,y):
    x = min(x, GRID_WIDTH-1)
    y = min(y, GRID_HEIGHT-1)
    return int(background[y][x])


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
                    encontrado = True
            if not encontrado:
                entities.append(Slime(e["x"], e["y"], e["id"]))
    
    elif "hit" in msg:
        hit = msg["hit"]
        for en in entities:
            if en.type == "enemy" and en.id == hit["enemy"]:
                en.applyDmg(hit["dmg"])
        
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

def killAll():
    global entities
    entities = []

def restart():
    global worldfile, background, isOnDng, dungeon, DNG_X, DNG_Y
    dungeon = None
    DNG_X = 0
    DNG_Y = 0
    isOnDng = False
    worldfile = readWorldData("foreground")
    background = readWorldData("background")
    killAll()

def die():
    global CHAR_X, CHAR_Y, HEIGHT, WIDTH, VIDA, isOnDng
    CHAR_X = WIDTH/2
    CHAR_Y = HEIGHT/2
    VIDA = 10
    if isOnDng:
        restart()



def applyDmg():
    global VIDA, dmgCooldown
    if VIDA > 0:
        VIDA -= 1
    if not VIDA:
        die()
    dmgCooldown = 30

def renderMap():
    global dungeon, isOnDng

    transparent_color = (255, 0, 0, 128)  # Black with 50% transparency

    # Create a Surface with SRCALPHA to allow transparency
    rect_surface = pygame.Surface((MAP_SIZE, MAP_SIZE), pygame.SRCALPHA)
    rect_surface.fill(transparent_color)

    if isOnDng:
        for y in range(10):
            for x in range(10):
                cellvalue = dungeon[y][x]
                if cellvalue:
                    WIN.blit(tileSprites[cellvalue["img"]], (x * MAP_SIZE, y * MAP_SIZE))
                if x == DNG_X and y == DNG_Y:
                    WIN.blit(rect_surface, (x * MAP_SIZE, y * MAP_SIZE))

def renderUI():
    global font, WIN, VIDA, bloqueSeleccionado
    #renderizar vida
    color = (255,255,255)
    text = font.render(f"Life: {VIDA}", True, color)
    WIN.blit(text, (10, 10))
    #renderizar bloque seleccionado
    pygame.draw.rect(WIN, (255,255,255), pygame.Rect(17, HEIGHT - 23 - GRID_SIZE, GRID_SIZE+ 6, GRID_SIZE + 6))
    WIN.blit(worldSprites[bloqueSeleccionado], (20, HEIGHT - 20 - GRID_SIZE))
    renderMap()

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
            
worldfile = readWorldData("foreground")
background = readWorldData("background")

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
    elif bloqueParado == 6 and not dmgCooldown:
        nivel += 1
        entrarDungeon(nivel)
        dmgCooldown = 30

    CHAR_X += CHAR_VX * CHAR_SPEED
    CHAR_Y += CHAR_VY * CHAR_SPEED

    CHAR_VX = 0
    CHAR_VY = 0

    if  pygame.mouse.get_pressed() and movimiento and VIDA:

        mouse_x, mouse_y = pygame.mouse.get_pos()
        cell_x , cell_y = cambiarCoordsAGrid(mouse_x, mouse_y)

        if pygame.mouse.get_pressed()[2] and not primaryCooldown:

            px, py = getNormDir(gx, gy, mouse_x, mouse_y)
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
    if isOnDng:
        if CHAR_X < 40:
            DNG_X -= 1
            cargarHabitacion(DNG_Y, DNG_X)
            CHAR_X = WIDTH - 80
        elif CHAR_X > WIDTH - 40:
            DNG_X += 1
            cargarHabitacion(DNG_Y, DNG_X)
            CHAR_X = 50
        if CHAR_Y < 40:
            DNG_Y -= 1
            cargarHabitacion(DNG_Y, DNG_X)
            CHAR_Y = HEIGHT - 80
        elif CHAR_Y > HEIGHT - 40:
            DNG_Y += 1
            cargarHabitacion(DNG_Y, DNG_X)
            CHAR_Y = 50

    WIN.fill((0,0,0))

    # Dibuja el fondo
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            block = getBlockInGrid(x, y)
            if block == 0:
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
