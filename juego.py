import pygame
import sys

# Inicializa Pygame
pygame.init()

# Configura las dimensiones de la ventana

# Configura la grilla
GRID_SIZE = 40
CHAR_SIZE = GRID_SIZE
GRID_WIDTH = 30
GRID_HEIGHT = 20
RED = (255, 0, 0)

WIDTH, HEIGHT = GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_WIDTH

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Movimiento en Grilla con Fondo")

# Configura la posición inicial del personaje
CHAR_X, CHAR_Y = GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE
CHAR_SPEED = GRID_SIZE

# Carga las imágenes de la grilla
background_images = []

worldfile = open("world.txt","r").readlines()
for i in range(len(worldfile)):
    worldfile[i] = worldfile[i][:-1]

worldSprites = []

for i in range(3):
    worldSprites.append(pygame.image.load(f'cell{i}.png'))
    worldSprites[i] = pygame.transform.scale(worldSprites[i], (GRID_SIZE, GRID_SIZE))

spritepj = pygame.image.load(f'sprite.png')
spritepj = pygame.transform.scale(spritepj, (GRID_SIZE, GRID_SIZE))

# Reloj para controlar los FPS
clock = pygame.time.Clock()

# Controla el estado de movimiento
CHAR_SIZE = 40
movimiento = False
CHAR_X, CHAR_Y = WIDTH // 2, HEIGHT // 2
CHAR_SPEED = 3

# Reloj para controlar los FPS
clock = pygame.time.Clock()

def cambiarCoordsAGrid(x,y):
    return x/GRID_SIZE , y/GRID_SIZE

def getBlockInGrid(x,y):
    return int(worldfile[y][x])

def cambiarBloque(x, y , id):
    worldfile[y][x] = id

# Bucle principal del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Obtén las teclas presionadas
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_w]:
        CHAR_Y -= CHAR_SPEED
    if keys[pygame.K_s]:
        CHAR_Y += CHAR_SPEED
    if keys[pygame.K_a]:
        CHAR_X -= CHAR_SPEED
    if keys[pygame.K_d]:
        CHAR_X += CHAR_SPEED
   
    if event.type == pygame.MOUSEBUTTONDOWN and movimiento:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cell_x , cell_y = cambiarCoordsAGrid(mouse_x, mouse_y)
        cambiarBloque(cell_x, cell_y, 2)
        movimiento = False

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
