##########################
### Author: Sam Banks  ###
### Mentor: Ping-Ya Chao #
##########################

# CITATION: Character spritesheet from https://opengameart.org/content/rpg-character
# CITATION: Tileset from https://askariot.itch.io/game-tileset?download

import math, time
import level_generator

# CITATION: Tkinter graphics wrapper from CMU 15-112 https://www.cs.cmu.edu/~112/index.html
from cmu_112_graphics import *

# Parent class of Person and Projectile classes.
class Entity(object):
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.r = r
        self.speedScale = 0

    # Moves entity in direction specified by dx and dy, scaled by timeScale and 
    # the speed of the entity (speedScale).
    def move(self, timeScale):
        mag = (self.dx**2 + self.dy**2)**.5
        if mag != 0: a = 1/mag
        else: a = 1
        self.x += a*self.dx*self.speedScale*timeScale
        self.y += a*self.dy*self.speedScale*timeScale

    # Checks if entity collides with square at given location.
    def checkObstacleCollision(self, squareX, squareY, squareR):
        xLeft = squareX - (self.x + self.r)
        xRight = (self.x - self.r) - (2 * squareR + squareX)
        yTop = squareY - (self.y + self.r)
        yBottom = (self.y - self.r) - (2 * squareR + squareY)
        
        minDistance = min(abs(xLeft), abs(xRight), abs(yTop), abs(yBottom))

        if abs(xLeft) == minDistance:
            return xLeft < 0
        elif abs(xRight) == minDistance:
            return xRight < 0
        elif abs(yTop) == minDistance:
            return yTop < 0
        elif abs(yBottom) == minDistance:
            return yBottom < 0

    # Collision detection for circular entity and square obstacle.
    # squareX and squareY should be center of square.
    def collidesWithObstacle(self, squareX, squareY, squareR):
        r = ((squareX-self.x)**2 + (squareY-self.y)**2)**.5
        if r < squareR: return True
        elif r > self.r + squareR*(2)**.5: return False

        if abs(squareX - self.x) > abs(squareY - self.y):
            a = math.cos(math.acos(abs(squareX-self.x)/r))
        else:
            a = math.cos(math.acos(abs(squareY-self.y)/r))
        d = squareR/a
        return r < d + self.r

# Parent class of Enemy and Player
class Person(Entity):
    def __init__(self, x, y, r, weapon):
        super().__init__(x, y, r)
        self.weapon = weapon

# Class to represent the player.
class Player(Person):
    def __init__(self, x, y, weapon):
        super().__init__(x, y, 20, weapon)
        self.startX = x
        self.startY = y
        self.speedScale = 10

    # Moves player, and updates paths for enemies.
    # FIX: only check for new paths when player changes cells.
    def move(self, timeScale, app):
        super().move(timeScale)
        if self.dx != 0 or self.dy != 0:
            app.calculateEnemyPaths()

# Class to represent enemies.
class Enemy(Person):
    def __init__(self, x, y, weapon):
        super().__init__(x, y, 20, weapon)
        self.triggered = False
        self.speedScale = 10*.75
        self.foundPlayer = False
        self.seesPlayer = False

    # Move function for Enemy class.
    # Moves entity in direction specified by dx and dy, scaled by timeScale and 
    # the speed of the entity (speedScale).
    # Assumes enemy will only be moving horizontally or vertically.
    def move(self, timeScale, app):
        if self.foundPlayer: return
        if self.triggered:
            self.followPath()
        mag = (self.dx**2 + self.dy**2)**.5
        if mag != 0: a = 1/mag
        else: a = 1
        dx = a*self.dx*self.speedScale*timeScale
        dy = a*self.dy*self.speedScale*timeScale

        if len(self.path) < 2: 
            self.x += dx
            self.y += dy
            return

        # Ensure enemy doesn't move beyond center of next square on path
        targetX, targetY = app.getCoords(self.path[1][0], self.path[1][1])
        if (dx != 0 and (self.x <= targetX <= self.x + dx or 
            self.x >= targetX >= self.x +dx)):
            self.x = targetX
            self.path.pop(0)
            self.followPath()
        elif (dy != 0 and (self.y <= targetY <= self.y + dy or 
            self.y >= targetY >= self.y + dy)):
            self.y = targetY
            self.path.pop(0)
            self.followPath()
        else:
            self.x += dx
            self.y += dy
    
    # Find path to player.
    def findPlayer(self, app):
        row, col = app.getCell(self.x, self.y)
        playerRow, playerCol = app.getCell(app.player.x, app.player.y)
        if (row, col) == (playerRow, playerCol):
            return
        result = app.findPath((row, col), (playerRow, playerCol))
        self.path = result[2]
        return result

    # Sets the enemy's dx and dy to follow path.
    def followPath(self):
        if len(self.path) < 2:
            self.foundPlayer = True
            self.dx, self.dy = 0, 0
        else:
            self.dx = self.path[1][1] - self.path[0][1]
            self.dy = self.path[1][0] - self.path[0][0]

    # Function to check whether enemy has a line of sight to player.
    # ex and ey represent enemy coords, px and py represent player coords.
    # (x1, y1) and (x2, y2) are opposite corners of the given cell.
    def canSeePlayer(self, app):
        for row, col in app.obstaclesTest:
            squareX, squareY = app.getCoords(row, col)
            x1, y1 = squareX - app.cellSize/2, squareY - app.cellSize/2
            x2, y2 = squareX + app.cellSize/2, squareY + app.cellSize/2
            ex, ey = self.x, self.y
            px, py = app.player.x, app.player.y
            dx, dy = px - ex, py - ey

            if dx == 0:
                if (x1 < px < x2) and ((py < (y1+y2)/2 < ey) or (py > (y1+y2)/2) > ey):
                    return False
            elif dy == 0:
                if (y1 < py < y2) and ((px < (x1+x2)/2 < ex) or (px > (x1+x2)/2) > ex):
                    return False
            
            # CHECK THIS CONDITIONAL
            elif ((y1 < ey + (x1-ex)*(dy/dx) < y2) or 
                (y1 < ey + (x2-ex)*(dy/dx) < y2) or 
                (x1 < ex + (y1-ey)*(dx/dy) < x2) or 
                (x1 < ex + (y1-ey)*(dx/dy) < x2)) and (
                (py < (y1+y2)/2 < ey) or (py > (y1+y2)/2 > ey) or 
                (px < (x1+x2)/2 < ex) or (px > (x1+x2)/2) > ex):
                print(row, col)
                # print((y1 < ey + (x1-ex)*(dy/dx) < y2),(y1 < ey + (x2-ex)*(dy/dx) < y2),
                #         (x1 < ex + (y1-ey)*(dx/dy) < x2), (x1 < ex + (y1-ey)*(dx/dy) < x2))
                # print(y1, ey + (x1-ex)*(dy/dx), y2)
                # print(y1, ey + (x2-ex)*(dy/dx), y2)
                # print(x1, ex + (y1-ey)*(dx/dy), x2)
                # print(x1, ex + (y1-ey)*(dx/dy), x2)
                return False
        return True

    # Function called to shoot weapon at player.
    def fireAtPlayer(self, app):
        if self.weapon.fire(app):
            dx = app.player.x - self.x
            dy = app.player.y - self.y
            bullet = Projectile(self.x, self.y, dx, dy, 10, True)
            app.projectiles.append(bullet)

# Class to represent projectiles.
class Projectile(Entity):
    def __init__(self, x, y, dx, dy, r, harmful):
        super().__init__(x, y, r)
        self.dx = dx
        self.dy = dy
        self.harmful = harmful
        self.speedScale = 30

# Parent class of all weapons.
class Weapon(object):
    def __init__(self, name, reloadTime, ammo):
        self.name = name
        self.reloadTime = reloadTime
        self.ammo = ammo
        self.lastFired = -reloadTime

    # Fires weapon and returns True if successful and False otherwise.
    def fire(self, app):
        if app.timeCounter >= self.lastFired + self.reloadTime and self.ammo > 0:
            self.ammo -= 1
            self.lastFired = app.timeCounter
            return True
        else:
            return False

# Subclass of Weapon to represent pistol.
class Pistol(Weapon):
    def __init__(self):
        super().__init__("Pistol", 10, 6)

# Subclass of Weapon to represent machine gun.
class MachineGun(Weapon):
    def __init__(self):
        super().__init__("Machine Gun", 3, 50)

# Main class for game.
class MyApp(App):
    def appStarted(self):
        self.player = Player(self.width/2, self.height/2, MachineGun())
        self.timerDelay = 50
        # self.setupBoard()
        self.board = level_generator.makeLevel()
        # self.cellSize = self.player.r*2
        self.cellSize = 50

        self.isSlow = True
        self.maxTimeScale = 1
        self.minTimeScale = .1
        self.timeScale = self.minTimeScale
        self.timeScaleStep = .1
        self.timeCounter = 0

        self.obstacles = set([])
        
        self.initializeSprites()
        self.enemies = []

        # Find spawn, initialize obstacles
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == "p":
                    self.player.x, self.player.y = self.getCoords(row, col)
                elif self.board[row][col] == "o":
                    self.obstacles.add((row, col))
                elif self.board[row][col][0] == "e":
                    x, y = self.getCoords(row, col)
                    self.enemies.append(Enemy(x, y, MachineGun()))

        self.obstaclesTest = sorted(list(self.obstacles))[:]

        # TEST CODE FOR ENEMY PATHING
        for enemy in self.enemies:
            enemy.triggered = True
            print(enemy.findPlayer(self)[2])

        self.projectiles = []

        self.testStuff()

    # Called for each frame of the game; moves entities, checks collisions.
    def timerFired(self):
        self.timeCounter += self.timeScale

        self.player.move(self.timeScale, self)
        self.moveProjectiles(self.timeScale)
        self.moveEnemies()
        self.doEnemyAttacks()

        for (row, col) in self.obstacles:
            if self.player.collidesWithObstacle((col+.5)*self.cellSize,
                                                (row+.5)*self.cellSize,
                                                self.cellSize/2):
                dx, dy = self.player.dx, self.player.dy
                self.player.dx *= -1
                self.player.dy *= -1
                self.player.move(self.timeScale, self)
                self.player.dx, self.player.dy = dx, dy
    
            for projectile in self.projectiles:
                if projectile.collidesWithObstacle((col+.5)*self.cellSize,
                                                    (row+.5)*self.cellSize,
                                                    self.cellSize/2):
                    self.projectiles.remove(projectile)

        # Scale speed linearly.
        if self.player.dx == 0 and self.player.dy == 0:
            self.isSlow = True
        else:
            self.isSlow = False

        if self.isSlow:
            self.timeScale = max(self.minTimeScale,self.timeScale-self.timeScaleStep)
        else:
            self.timeScale = min(self.maxTimeScale,self.timeScale+self.timeScaleStep)


    # Resolves keypresses for player movement, pause menu, etc.    
    def keyPressed(self, event):
        if event.key == "w":
            self.player.dy += -1
        elif event.key == "s":
            self.player.dy += 1
        elif event.key == "a":
            self.player.dx += -1
        elif event.key == "d":
            self.player.dx += 1
        elif event.key == "r":
            MyApp(400, 400)

    # Works with keyPressed for movement.
    def keyReleased(self, event):
        if event.key == "w":
            self.player.dy += 1
        elif event.key == "s":
            self.player.dy += -1
        elif event.key == "a":
            self.player.dx += 1
        elif event.key == "d":
            self.player.dx += -1

    # MAKE OBJECT-ORIENTED
    # Function for weapon behavior when player clicks.
    def mousePressed(self, event):
        clickX = event.x + self.player.x - self.width/2
        clickY = event.y + self.player.y - self.height/2

        # Check if player clicked directly on themself.
        if clickX == self.player.x and clickY == self.player.y: return

        # Attempt to fire weapon, skip rest of function if unsuccessful.
        if not self.player.weapon.fire(self): return

        r = 1
        dx = (clickX-self.player.x) / r
        dy = (clickY-self.player.y) / r
        bullet = Projectile(self.player.x, self.player.y, dx, dy, 10, False)
        self.projectiles.append(bullet)
    
    # Main drawing function to draw map, player, enemies and projectiles.
    def redrawAll(self, canvas):
        x = self.width/2
        y = self.height/2
        r = self.player.r
        self.drawBoard(canvas)
        self.drawEnemies(canvas)
        canvas.create_image(x, y, image=self.playerSprite.cachedPhotoImage)
        self.drawProjectiles(canvas)

    # Test function to create board.
    def setupBoard(self):
        board = [[" "]*10 for i in range(10)]
        board[2][3] = "p"
        board[4][3] = "e"
        board[1][1] = "o"
        board[2][2] = "o"
        board[3][3] = "o"
        board[3][4] = "o"
        board[3][5] = "o"
        for row in range(len(board)):
            for col in range(len(board[0])):
                if row==0 or col==0 or row==len(board)-1 or col==len(board[0])-1:
                    board[row][col] = "o"
        self.board = board

    # Function to draw obstancles from board.
    def drawBoard(self, canvas):
        canvas.create_rectangle(0,0,self.width,self.height,fill="grey")
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                x = col * self.cellSize - (self.player.x - self.width/2)
                y = row * self.cellSize - (self.player.y - self.height/2)
                if self.board[row][col] == "o":
                    canvas.create_image(x+self.cellSize/2,y+self.cellSize/2,
                                        image=self.wall.cachedPhotoImage)
                    
    # Move every projectile in game.
    def moveProjectiles(self, timeScale):
        for projectile in self.projectiles:
            projectile.move(timeScale)

    # Draw projectiles.
    def drawProjectiles(self, canvas):
        for p in self.projectiles:
            if p.harmful: color = "red"
            else: color = "blue"
            x = p.x - (self.player.x - self.width/2)
            y = p.y - (self.player.y - self.height/2)
            canvas.create_oval(x-p.r, y-p.r, x+p.r, y+p.r, fill=color)

    # Sets up sprites for main character, enemy and background tiles.
    # CITATION: Referenced 15-112 website for caching technique: 
    # https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html#imageMethods
    def initializeSprites(self):
        # playerImg = self.loadImage("img/player.png")
        # playerSprites = [[0]*3 for i in range(4)]
        # size = playerImg.size[0] / 3
        # for i in range(len(playerSprites)):
        #     for j in range(len(playerSprites[0])):
        #         sprite = playerImg.crop((j*size, i*size, (j+1)*size, (i+1)*size))
        #         # sprite = playerImg.crop((0, 0, 100 , 100)
        #         sprite = self.scaleImage(sprite, self.cellSize/size)
        #         sprite.cachedPhotoImage = ImageTk.PhotoImage(sprite)
        #         playerSprites[i][j] = sprite
        # self.playerSprites = playerSprites

        playerSprite = self.loadImage("img/player_single.gif")
        playerSprite = self.scaleImage(playerSprite, self.player.r*2/playerSprite.size[0])
        playerSprite.cachedPhotoImage = ImageTk.PhotoImage(playerSprite)
        self.playerSprite = playerSprite

        # Using player radius
        enemySprite = self.loadImage("img/enemy_single.gif")
        enemySprite = self.scaleImage(enemySprite, self.player.r*2/enemySprite.size[0])
        enemySprite.cachedPhotoImage = ImageTk.PhotoImage(enemySprite)
        self.enemySprite = enemySprite

        floor = self.loadImage("img/floor.png")
        floor = self.scaleImage(floor, self.cellSize/floor.size[0])
        floor.cachedPhotoImage = ImageTk.PhotoImage(floor)
        self.floor = floor

        wall = self.loadImage("img/wall.png")
        wall = self.scaleImage(wall, self.cellSize/wall.size[0])
        wall.cachedPhotoImage = ImageTk.PhotoImage(wall)
        self.wall = wall

    # Draws enemies to screen.
    def drawEnemies(self, canvas):
        for enemy in self.enemies:
            x, y, r = enemy.x, enemy.y, enemy.r
            x += self.width/2 - self.player.x
            y += self.height/2 - self.player.y
            # canvas.create_oval(x-r, y-r, x+r, y+r, fill="red")
            canvas.create_image(x, y, image=self.enemySprite.cachedPhotoImage)

    # Wrapper function for dijkstras pathfinding algorithm. Takes a start tuple
    # and end tuple (row, col).
    # CITATION: I referenced algorithm explanation at 
    # https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
    def findPath(self, start, end):
        board = self.board
        distances = [[-1] * len(board[0]) for i in range(len(board))]
        distances[start[0]][start[1]] = 0
        paths = [[0] * len(board[0]) for i in range(len(board))]

        unvisited = set([])
        for i in range(len(distances)):
            for j in range(len(distances[0])):
                if board[i][j] != "o":
                    unvisited.add((i, j))
        current = start
        
        while True:
            result = self.doStep(distances, paths, unvisited, end)
            if result or result == False: break
        if not result: return False
        return result, distances, self.getPath(paths, start, end), paths

    # Helper funtion for pathfinding algorithm.
    # Determines current cell, then visits cell.
    def doStep(self, distances, paths, unvisited, end):
        board = self.board

        # Determine current cell.
        shortest = None
        shortestDistance = -1
        for row, col in unvisited:
            if distances[row][col] != -1:
                if shortest == None or distances[row][col] < shortestDistance:
                    shortest = (row, col)
                    shortestDistance = distances[row][col]
        current = shortest
        if current == None: return False

        self.visitCell(distances, paths, unvisited, current)
        if end not in unvisited: return True
        elif len(unvisited) == 0: return False

    # Helper function for pathfinding algorithm.
    # Marks all neighbors of a given cell with distances from the start.
    def visitCell(self, distances, paths, unvisited, current):
        board = self.board
        # Check up, down, left right
        row, col = current
        for drow in (-1, 0, 1):
            for dcol in (-1, 0, 1):
                newRow, newCol = row + drow, col + dcol
                if (abs(drow) + abs(dcol) == 1 and 0 <= newRow < len(board) and
                    0 <= newCol < len(board[0])):
                    if ((distances[newRow][newCol] == -1 or 
                        distances[newRow][newCol] > distances[row][col] + 1) and
                        board[newRow][newCol] != "#"):

                        distances[newRow][newCol] = distances[row][col] + 1
                        paths[newRow][newCol] = (-drow, -dcol)
                        
        unvisited.remove(current)

    # CHECK FOR DIAGONAL ISSUE
    # ALSO CHECK FOR ISSUE WHERE START AND END ARE ADJACENT/SAME.
    # Helper function for pathfinding algorithm.
    # Creates path from end to start using results of pathfinding algorithm.
    def getPath(self, paths, start, end):
        path = [end]
        row, col = end
        while True:
            drow = paths[row][col][0]
            dcol = paths[row][col][1]
            row += drow
            col += dcol
            path = [(row, col)] + path
            if start == (row, col): 
                return path

    # Returns (x, y) for a given row and col (center of cell).
    def getCoords(self, row, col):
        return ((col+.5)*self.cellSize, (row+.5)*self.cellSize)

    # Returns (row, col) for a given x and y.
    def getCell(self, x, y):
        return (int(y//self.cellSize), int(x//self.cellSize))

    # Moves every enemy.
    def moveEnemies(self):
        for enemy in self.enemies:
            
            seesPlayer = enemy.canSeePlayer(self)
            print(seesPlayer)
            if enemy.triggered and not seesPlayer:
                enemy.move(self.timeScale, self)
                enemy.seesPlayer = seesPlayer
            elif enemy.triggered and seesPlayer:
                enemy.seesPlayer = seesPlayer

    # Calculates path to player for every enemy.
    def calculateEnemyPaths(self):
        for enemy in self.enemies:
            enemy.foundPlayer = False
            enemy.findPlayer(self)

    # Miscellaneous testing function.
    def testStuff(self):
        assert(self.getCoords(1, 2) == (125.0, 75.0))
        print("passed")

    # Enemies who can see player fire their weapons.
    def doEnemyAttacks(self):
        for enemy in self.enemies:
            if enemy.triggered and enemy.seesPlayer:
                enemy.fireAtPlayer(self)

MyApp(400, 400)