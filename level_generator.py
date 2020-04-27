##########################
### Author: Sam Banks  ###
### Mentor: Ping-Ya Chao #
##########################

from random import randrange, random, choice
import copy

class LevelSpec(object):
    def __init__(self):
        self.obstacle = "o"
        self.space = " "
        self.player = "p"
        self.enemy = "e"

def print2dList(L):
    for row in L: print(row)

# Top layer level-generator function.
def makeLevel(difficulty):
    return setup(spec, difficulty)

# Basic level setup.
# Take dictionary of level specifications.
# Difficulty model: D = k*N/A, for Difficulty, Number of enemies, Area, k constant
# Enemy weapons are chosen by D.
def setup(spec, difficulty):
    rows = randrange(spec["rowMin"], spec["rowMax"])
    cols = randrange(spec["colMin"], spec["colMax"])
    board = [[spec["space"]]*cols for i in range(rows)]

    # d = 1+(difficulty-1)/10
    # FIX: This calculation of number of enemies.
    enemyMultiplier = difficulty*rows*cols/80
    numEnemies = int(enemyMultiplier)
    print(numEnemies)

    # Create bounding walls.
    board[0] = [spec["obstacle"]]*cols
    board[-1] = [spec["obstacle"]]*cols
    for row in range(len(board)):
        board[row][0] = spec["obstacle"]
        board[row][-1] = spec["obstacle"]

    boardCopy = copy.deepcopy(board)

    # Checks that the terrain is acceptable.
    finishedMap = False
    while not finishedMap:
        board = copy.deepcopy(boardCopy)
        generateTerrain(spec, board)
        print("trying map")
        if isConnected(spec, board):
            openCells = []
            for row in range(len(board)):
                for col in range(len(board[0])):
                    if board[row][col] == spec["space"]:
                        openCells.append((row, col))
            if len(openCells) >= spec["minOpenCells"]:
                finishedMap = True

    print("finished map")

    # Places the player in an empty cell.
    placedPlayer = False
    while not placedPlayer:
        prow, pcol = choice(openCells)
        if board[prow][pcol] == spec["space"]:
            board[prow][pcol] = spec["player"]
            placedPlayer = True
            openCells.remove((prow, pcol))

    # Place each enemy with an enemy.
    for i in range(numEnemies):
        placedEnemy = False
        while not placedEnemy:
            erow, ecol = choice(openCells)
            if board[erow][ecol] == spec["space"]:
                weaponRoll = random()
                if weaponRoll < spec["machineGunProb"]:
                    weapon = "machineGun"
                elif weaponRoll < spec["shotgunProb"]:
                    weapon = "shotgun"
                else:
                    weapon = "pistol"

                board[erow][ecol] = spec["enemy"]+","+weapon
                placedEnemy = True
                openCells.remove((erow, ecol))

    # Place weapons on map.
    numWeapons = int(numEnemies/2)
    for i in range(numWeapons):
        wrow, wcol = choice(openCells)
        weaponRoll = random()
        if weaponRoll < spec["machineGunProb"]:
            weapon = "machineGun"
        elif weaponRoll < spec["shotgunProb"]:
            weapon = "shotgun"
        else:
            weapon = "pistol"
        board[wrow][wcol] = "w,"+weapon
        openCells.remove((wrow, wcol))
        
    return board
    print2dList(board)

# Generates obstacles for level.
def generateTerrain(spec, board):
    for row in range(1, len(board)-1):
        for col in range(1, len(board[0])-1):
            prob = random()

            for drow in [-1, 0, 1]:
                for dcol in [-1, 0, 1]:
                    if board[row+drow][col+dcol] == spec["obstacle"]:
                        if abs(drow) + abs(dcol) == 1:
                            if prob < spec["adjacentProb"]:
                                board[row][col] = spec["obstacle"]
                        elif abs(drow) + abs(dcol) == 2:
                            if prob < spec["diagProb"]:
                                board[row][col] = spec["obstacle"]
            if prob < spec["stdProb"]:
                board[row][col] = spec["obstacle"]

# Checks that all open space in level is connected.
def isConnected(spec, board):

    # Find all open cells.
    openCells = set([])
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] == spec["space"]:
                openCells.add((row, col))

    if len(openCells) < 1: return False

    openCellsCopy = openCells.copy()
    
    visited = set([])
    toCheck = set([openCellsCopy.pop()])

    while len(toCheck) > 0:
        row, col = toCheck.pop()
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                if (abs(drow) + abs(dcol) == 1 and  0 <= row+drow < len(board) 
                    and 0 <= col+dcol < len(board[0])):
                    if (board[row+drow][col+dcol] == spec["space"] and 
                        (row+drow, col+dcol) not in visited):
                        toCheck.add((row+drow, col+dcol))
        visited.add((row, col))

    return visited == openCells

spec = {"rowMin":10, "rowMax":30, "colMin":10, "colMax":30, "obstacle":"o",
            "space":" ", "stdProb":.1, "diagProb":.1, "adjacentProb":.3,
            "player":"p", "enemy":"e", "minOpenCells":10, "machineGunProb":.2,
            "shotgunProb":.4, "weaponSpawnProb":.05}

# print2dList(makeLevel(1))