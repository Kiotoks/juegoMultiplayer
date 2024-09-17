import math
import random

GRID_WIDTH = 10 
GRID_HEIGHT = 10 

cantCofres = 0 
cantEnds = 0
ends = []

def getCompatibles(tileSides):
    global tiles
    for tile in tiles:
        if tile["sides"] == tileSides:
            return tile

#levelsRooms y tiles deberian estar guardadas en un propio archivo de json
#se deberia de usar map() y find para hacer el codigo mas eficiente

tiles = []
tiles.append({"img":15,"sides": [0,0,0,0],"name": "BLANK", "end": False, "room":""})
tiles.append({"img":10,"sides": [1,1,0,1],"name": "UP T", "end": False, "room":""})
tiles.append({"img":7,"sides": [1,1,1,0],"name": "RIGHT T", "end": False, "room":""})
tiles.append({"img":8,"sides": [0,1,1,1],"name": "DOWN T", "end": False, "room":""})
tiles.append({"img":9,"sides": [1,0,1,1],"name": "LEFT T", "end": False, "room":""})
tiles.append({"img":13,"sides": [0,0,1,0],"name": "END DOWN", "end": True, "room":""})
tiles.append({"img":14,"sides": [0,0,0,1],"name": "END LEFT", "end": True, "room":""})
tiles.append({"img":11,"sides": [1,0,0,0],"name": "END UP", "end": True, "room":""})
tiles.append({"img":12,"sides": [0,1,0,0],"name": "END RIGHT", "end": True, "room":""})
tiles.append({"img":2,"sides": [0,1,0,1],"name": "H LINE", "end": False, "room":""})
tiles.append({"img":1,"sides": [1,0,1,0],"name": "V LINE", "end": False, "room":""})
tiles.append({"img":3,"sides": [1,1,0,0],"name": "UP L", "end": False, "room":""})
tiles.append({"img":4,"sides": [0,1,1,0],"name": "RIGHT L", "end": False, "room":""})
tiles.append({"img":5,"sides": [0,0,1,1],"name": "DOWN L", "end": False, "room":""})
tiles.append({"img":6,"sides": [1,0,0,1],"name": "LEFT L", "end": False, "room":""})
tiles.append({"img":0,"sides": [1,1,1,1],"name": "START CROSS", "end": False, "room":""})

levelsRooms =[
    {"chest": 2, "tienda": 1, "mina": 2},
    {"chest": 2, "tienda": 1, "mina": 2},
    {"chest": 2, "tienda": 1, "mina": 2},
    {"chest": 2, "tienda": 1, "mina": 2},
    {"chest": 2, "tienda": 1, "mina": 2}
]

grid = []

for i in range(GRID_HEIGHT):
    row = []
    for j in range(GRID_WIDTH):
        row.append(None)
    grid.append(row)

grid[math.trunc(GRID_HEIGHT/2)][math.trunc(GRID_WIDTH/2)] = tiles[0]

LIFE = 10
sidecoords = [[-1,0], [0,1], [1,0], [0,-1]]

def llenarMatriz(width, height):
    grid = []
    for i in range(width):
        row = []
        for j in range(height):
            row.append(None)
        grid.append(row)
    return grid

def fillRooms(grid, ends, level):

    rooms = ["chest", "normal", "tienda"]
    grid[ends[0][0]][ends[0][1]]["room"] = "spawn"
    grid[ends[1][0]][ends[1][1]]["room"] = "boss"
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            cell = grid[i][j]
            
    return grid

def getSides(cell, i, j):
    global grid
    sides = []
    sidecoords = [[-1,0], [0,1], [1,0], [0,-1]]
    for sideIndex in range(len(cell["sides"])):
        nx = j + sidecoords[sideIndex][1]
        ny = i + sidecoords[sideIndex][0]
        nbCell = grid[ny][nx]
        if nbCell != None:
            sides.append(1)
        else:
            sides.append(0)
    return sides

def generarDungeon(life, width, height, level):
    print("cargando")
    global grid, cantEnds, ends
    grid = llenarMatriz(width, height)
    grid[math.trunc(GRID_HEIGHT/2)][math.trunc(GRID_WIDTH/2)] = tiles[0]
    LIFE = life

    while LIFE > 0: 
        placeList= []
        #seleccionar todas las nuevas habitaciones 
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                cell = grid[i][j]
                if cell != None:
                    placeList.append([i,j])
                        
        for cellPos in placeList:
            y, x = cellPos
            cellValue = grid[y][x]
            for sideIndex in range(len(cellValue["sides"])):
                nx = x + sidecoords[sideIndex][1]
                ny = y + sidecoords[sideIndex][0]
                # 25% de chance de poner una habitacion en cada lado de la actual
                r = random.randint(1,4)
                if r == 1: #se puede añadir una condicion para comprobar la vida asi se la vida corresponde a la cantidad de habitaciones
                    try:
                        if grid[ny][nx] == None:
                            grid[ny][nx] = tiles[0]
                            print(LIFE)
                            LIFE -= 1 #descontar vida solo aca
                    except:
                        pass

    # Recorrer matriz y agregar puertas a habitaciones
    primera = None
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            cell = grid[i][j]
            if cell != None:
                #chequear la cantidad de vecinos para desp elegir la cantidad de puertas
                sides = getSides(cell, i, j)
                unicoCompatible = getCompatibles(sides)
                if unicoCompatible["end"] == True:
                    ends.append([i,j])
                    cantEnds += 1
                grid[i][j] = unicoCompatible
                if primera == None:
                    primera = [i,j, cell]
                ultimaHabitacion = [i,j, cell]


    # Añadir un final debajo de la ultima habitacion (abajo a la derecha) si hay un solo final   
    if cantEnds < 2:
        print("no alcanzaban los finales")
        ui, uj  = ultimaHabitacion[0], ultimaHabitacion[1]
        grid[ui+1][uj] = tiles[7]
        #actualizar puertas ultima habitacion
        grid[ui][uj] = unicoCompatible = getCompatibles(getSides(ultimaHabitacion[2], ui, uj))
        ends.append([ui, uj])
        if cantEnds < 1:
            ui, uj  = primera[0], primera[1]
            grid[ui-1][uj] = tiles[5]
            #actualizar puertas ultima habitacion
            grid[ui][uj] = unicoCompatible = getCompatibles(getSides(primera[2], ui, uj))


    
    print(ends)
    grid = fillRooms(grid, ends, level)
    print("terminado")
    return grid, ends[0]
