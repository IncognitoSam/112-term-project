#########################
### Author: Sam Banks ###
#########################

import math

# Tkinter graphics wrapper from CMU 15-112: https://www.cs.cmu.edu/~112/index.html
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

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.speedScale = 0

    # Moves entity in direction specified by dx and dy, scaled by timeScale and 
    # the speed of the entity (speedScale).
    def move(self, timeScale):
        mag = (self.dx**2 + self.dy**2)**.5
        if mag != 0: a = 1/mag
        else: a = 1
        self.x += a*self.dx*self.speedScale*timeScale
        self.y += a*self.dy*self.speedScale*timeScale

# Parent class of Enemy and Player
class Person(Entity):
    def __init__(self, x, y, weapon):
        super().__init__(x, y)
        self.r = 25
        self.weapon = weapon

# Class to represent the player.
class Player(Person):
    def __init__(self, x, y, weapon):
        super().__init__(x, y, weapon)
        self.startX = x
        self.startY = y
        self.speedScale = 10

# Class to represent enemies.
class Enemy(Person):
    def __init__(self, x, y, weapon):
        super().__init__(x, y, weapon)
        self.triggered = False

# Class to represent projectiles.
class Projectile(Entity):
    def __init__(self, x, y, dx, dy, r, harmful):
        super().__init__(x, y)
        self.dx = dx
        self.dy = dy
        self.r = r
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
        self.timeScale = .1
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == "s":
                    self.player.x = (col+.5)*self.cellSize
                    self.player.y = (row+.5)*self.cellSize
        self.projectiles = []

    # Called for each frame of the game; moves entities, checks collisions.
    def timerFired(self):
        self.player.move(self.timeScale)
        self.moveProjectiles(self.timeScale)

        if self.player.dx == 0 and self.player.dy == 0 and not self.isSlow:
            self.isSlow = True
            self.timeScale = .1
        elif (self.player.dx != 0 or self.player.dy != 0) and self.isSlow:
            self.isSlow = False
            self.timeScale = 1

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
        # r = ((event.x-self.player.x)**2 + (event.y-self.player.y)**2)**.5
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
        canvas.create_oval(x-r, y-r, x+r, y+r, fill="blue")
        self.drawBoard(canvas)
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
        self.board = board

    # Function to draw obstancles from board.
    def drawBoard(self, canvas):
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == "o":
                    x = col * self.cellSize - (self.player.x - self.width/2)
                    y = row * self.cellSize - (self.player.y - self.height/2)
                    canvas.create_rectangle(x, y, x+self.cellSize, y+self.cellSize,
                                            fill="black", outline="white")
    
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

MyApp(400, 400)