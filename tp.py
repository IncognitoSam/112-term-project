#########################
### Author: Sam Banks ###
#########################

# CITATION: Character spritesheet from https://opengameart.org/content/rpg-character
# CITATION: Tileset from https://askariot.itch.io/game-tileset?download

import math, time

# CITATION: Tkinter graphics wrapper from CMU 15-112 https://www.cs.cmu.edu/~112/index.html
from cmu_112_graphics import *

# Class to contain gamestate information.
# Might be unnecessary with App class.
class Gamestate(object):
    def __init__(self, player, enemies):
        self.player = player
        self.enemies = enemies
        self.projectiles = []

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
        super().__init__(x, y, 25, weapon)
        self.startX = x
        self.startY = y
        self.speedScale = 10

# Class to represent enemies.
class Enemy(Person):
    def __init__(self, x, y, weapon):
        super().__init__(x, y, 25, weapon)
        self.triggered = False

# Class to represent projectiles.
class Projectile(Entity):
    def __init__(self, x, y, dx, dy, r, harmful):
        super().__init__(x, y, r)
        self.dx = dx
        self.dy = dy
        self.harmful = harmful
        self.speedScale = 30

# Main class for game.
class MyApp(App):
    def appStarted(self):
        self.player = Player(self.width/2, self.height/2, "gun")
        self.timerDelay = 50
        self.setupBoard()
        self.cellSize = self.player.r*2

        self.isSlow = True
        self.maxTimeScale = 1
        self.minTimeScale = .1
        self.timeScale = self.minTimeScale
        self.timeScaleStep = .1

        self.obstacles = set([])
        self.initializeSprites()

        # Find spawn, initialize obstacles
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == "s":
                    self.player.x = (col+.5)*self.cellSize
                    self.player.y = (row+.5)*self.cellSize
                elif self.board[row][col] == "o":
                    self.obstacles.add((row, col))

        self.projectiles = []

    # Called for each frame of the game; moves entities, checks collisions.
    def timerFired(self):
        self.player.move(self.timeScale)
        self.moveProjectiles(self.timeScale)

        for (row, col) in self.obstacles:
            if self.player.collidesWithObstacle((col+.5)*self.cellSize,
                                                (row+.5)*self.cellSize,
                                                self.cellSize/2):
                # print("collision:", row, col, time.time())
                dx, dy = self.player.dx, self.player.dy
                self.player.dx *= -1
                self.player.dy *= -1
                self.player.move(self.timeScale)
                self.player.dx, self.player.dy = dx, dy
    
            for projectile in self.projectiles:
                if projectile.collidesWithObstacle((col+.5)*self.cellSize,
                                                    (row+.5)*self.cellSize,
                                                    self.cellSize/2):
                    self.projectiles.remove(projectile)
                  

        # if self.player.dx == 0 and self.player.dy == 0 and not self.isSlow:
        #     self.isSlow = True
        #     self.timeScale = .1
        # elif (self.player.dx != 0 or self.player.dy != 0) and self.isSlow:
        #     self.isSlow = False
        #     self.timeScale = 1

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
    def mousePressed(self, event):
        clickX = event.x + self.player.x - self.width/2
        clickY = event.y + self.player.y - self.height/2
        if clickX == self.player.x and clickY == self.player.y: return
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
        canvas.create_oval(x-r, y-r, x+r, y+r, fill="blue")
        self.drawProjectiles(canvas)

    # Test function to create board.
    def setupBoard(self):
        board = [[""]*10 for i in range(10)]
        board[2][3] = "s"
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
                    # canvas.create_rectangle(x, y, x+self.cellSize, y+self.cellSize,
                                            # fill="black", outline="white")
                    canvas.create_image(x+self.cellSize/2,y+self.cellSize/2,
                                        image=self.wall.cachedPhotoImage)
                # else:
                    # canvas.create_image(x+self.cellSize/2,y+self.cellSize/2,
                    #                     image=self.floor.cachedPhotoImage)
                    
               
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

        floor = self.loadImage("img/floor.png")
        floor = self.scaleImage(floor, self.cellSize/floor.size[0])
        floor.cachedPhotoImage = ImageTk.PhotoImage(floor)
        self.floor = floor

        wall = self.loadImage("img/wall.png")
        wall = self.scaleImage(wall, self.cellSize/wall.size[0])
        wall.cachedPhotoImage = ImageTk.PhotoImage(wall)
        self.wall = wall

MyApp(400, 400)