import math
import random

# Inicializa Pygame

# Configura las dimensiones de la ventana
GRID_WIDTH = 10  # Ancho del mundo en celdas
GRID_HEIGHT = 10  # Alto del mundo en celdas

def getCompatibles(tileSides):
    global tiles
    for tile in tiles:
        if tile["sides"] == tileSides:
            return tile

def showGrid():
    cont = 0
    for i in range(GRID_HEIGHT):
        row = []
        for j in range(GRID_WIDTH):
            sas = grid[i][j] != None
            if sas:
                cont += 1
            row.append(sas)
        print(row)
    print(cont)

tiles = []
tiles.append({"img":15,"sides": [0,0,0,0],"name": "BLANK", "end": False})
tiles.append({"img":10,"sides": [1,1,0,1],"name": "UP T", "end": False})
tiles.append({"img":7,"sides": [1,1,1,0],"name": "RIGHT T", "end": False})
tiles.append({"img":8,"sides": [0,1,1,1],"name": "DOWN T", "end": False})
tiles.append({"img":9,"sides": [1,0,1,1],"name": "LEFT T", "end": False})
tiles.append({"img":13,"sides": [0,0,1,0],"name": "END DOWN", "end": True})
tiles.append({"img":14,"sides": [0,0,0,1],"name": "END LEFT", "end": True})
tiles.append({"img":11,"sides": [1,0,0,0],"name": "END UP", "end": True})
tiles.append({"img":12,"sides": [0,1,0,0],"name": "END RIGHT", "end": True})
tiles.append({"img":2,"sides": [0,1,0,1],"name": "H LINE", "end": False})
tiles.append({"img":1,"sides": [1,0,1,0],"name": "V LINE", "end": False})
tiles.append({"img":3,"sides": [1,1,0,0],"name": "UP L", "end": False})
tiles.append({"img":4,"sides": [0,1,1,0],"name": "RIGHT L", "end": False})
tiles.append({"img":5,"sides": [0,0,1,1],"name": "DOWN L", "end": False})
tiles.append({"img":6,"sides": [1,0,0,1],"name": "LEFT L", "end": False})
tiles.append({"img":0,"sides": [1,1,1,1],"name": "START CROSS", "end": False})

grid = []

for i in range(GRID_HEIGHT):
    row = []
    for j in range(GRID_WIDTH):
        row.append(None)
    grid.append(row)

grid[math.trunc(GRID_HEIGHT/2)][math.trunc(GRID_WIDTH/2)] = tiles[0]

LIFE = 10
END_PLACED = False
sidecoords = [[-1,0], [0,1], [1,0], [0,-1]]

def llenarMatriz(width, height):
    grid = []
    for i in range(width):
        row = []
        for j in range(height):
            row.append(None)
        grid.append(row)


def generarDungeon(life, width, height):

    llenarMatriz(width, height)
    LIFE = life

    while LIFE > 0: # cambiar for por un while donde la vida se descuente como en el codigo original
        placeList= []
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                cell = grid[i][j]
                if cell != None:
                    placeList.append([i,j])
                    print(j, i)
                    grid[i][j]["end"] = True
                        
        for cellPos in placeList:
            y, x = cellPos
            cellValue = grid[y][x]
            for sideIndex in range(len(cellValue["sides"])):
                nx = x + sidecoords[sideIndex][1]
                ny = y + sidecoords[sideIndex][0]
                r = random.randint(1,4)
                if r == 1:
                    if grid[ny][nx] == None:
                        grid[ny][nx] = tiles[0]
                        LIFE -= 1 #descontar vida solo aca
    

    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            cell = grid[i][j]
            if cell != None:
                sides = []
                for sideIndex in range(len(cell["sides"])):
                    nx = j + sidecoords[sideIndex][1]
                    ny = i + sidecoords[sideIndex][0]
                    nbCell = grid[ny][nx]
                    if nbCell != None:
                        sides.append(1)
                    else:
                        sides.append(0)
                grid[i][j] = getCompatibles(sides)
    
    return grid
