import pygame
import sys

# Inicializa Pygame
pygame.init()

# Configura las dimensiones de la ventana

GRID_SIZE = 40
CHAR_SIZE = GRID_SIZE
GRID_WIDTH = 200  # Ancho del mundo en celdas
GRID_HEIGHT = 160  # Alto del mundo en celdas

WIDTH, HEIGHT = GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_WIDTH

print(WIDTH + " " +HEIGHT)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Movimiento en Grilla con Cámara")

# Configura la grilla


# Tamaño total del mundo
WORLD_WIDTH = GRID_WIDTH * GRID_SIZE
WORLD_HEIGHT = GRID_HEIGHT * GRID_SIZE

# Configura la posición inicial del personaje
CHAR_X, CHAR_Y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
CHAR_SPEED = GRID_SIZE

# Carga las imágenes de la grilla
image = pygame.image.load(f'cell.png')
image = pygame.transform.scale(image, (GRID_SIZE, GRID_SIZE))

# Reloj para controlar los FPS
clock = pygame.time.Clock()

# Variables para el movimiento
move_x, move_y = 0, 0

# Bucle principal del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                move_x, move_y = 0, -CHAR_SPEED
            elif event.key == pygame.K_s:
                move_x, move_y = 0, CHAR_SPEED
            elif event.key == pygame.K_a:
                move_x, move_y = -CHAR_SPEED, 0
            elif event.key == pygame.K_d:
                move_x, move_y = CHAR_SPEED, 0
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                move_x, move_y = 0, 0

    # Actualiza la posición del personaje
    CHAR_X += move_x
    CHAR_Y += move_y

    # Asegúrate de que el personaje se mantenga dentro del mundo
    CHAR_X = max(0, min(CHAR_X, WORLD_WIDTH - CHAR_SIZE))
    CHAR_Y = max(0, min(CHAR_Y, WORLD_HEIGHT - CHAR_SIZE))
    
    # Para que se mueva de celda en celda
    CHAR_X = (CHAR_X // GRID_SIZE) * GRID_SIZE
    CHAR_Y = (CHAR_Y // GRID_SIZE) * GRID_SIZE

    # Calcular el área visible de la cámara
    camera_x = CHAR_X - WIDTH // 2
    camera_y = CHAR_Y - HEIGHT // 2

    # Asegúrate de que la cámara no se salga de los límites del mundo
    camera_x = max(0, min(camera_x, WORLD_WIDTH - WIDTH))
    camera_y = max(0, min(camera_y, WORLD_HEIGHT - HEIGHT))

    # Limpia la pantalla
    WIN.fill((255, 255, 255))  # Relleno inicial, se sobrescribirá

    # Dibuja el fondo
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            WIN.blit(image, (x * GRID_SIZE, y * GRID_SIZE))

    # Dibuja el personaje
    pygame.draw.rect(WIN, (255, 0, 0), (WIDTH // 2 - CHAR_SIZE // 2, HEIGHT // 2 - CHAR_SIZE // 2, CHAR_SIZE, CHAR_SIZE))
    
    # Actualiza la pantalla
    pygame.display.flip()
    
    # Controla los FPS
    clock.tick(60)  # Ajusta los FPS según lo necesites