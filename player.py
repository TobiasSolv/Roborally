from helpers import clamp
import pygame
from constants import *
import math

# ─── Player ──────────────────────────────────────────────────────────────────
class IllegalDirection(Exception):
    pass

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.x, self.y = x, y
        self.dir       = 0        # Direction: 0=up, 1=right, 2=down, 3=left
        self.next_flag = 1
        self.alive     = True
        self.color     = color
        self.hand      = []
        self.program   = []
        self.executed  = False

        self.image = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(topleft=(x * TILE, y * TILE))
        self._draw()

    def __str__(self):
        return "Player("+str(self.x)+ ", " +str(self.y)+ ", " +str(self.dir)+ ")"
    

    def _draw(self):
        # Draw triangle pointing in direction of player
        self.image.fill((0,0,0,0))
        cx, cy, r = TILE // 2, TILE // 2, TILE // 2 - 8
        pts = []
        for deg in (-90, 30, 150):
            ang = math.radians(deg + 90 * self.dir)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        pygame.draw.polygon(self.image, self.color, pts)

    def move(self, dx, dy, ddir):
        #boarded flytter spilleren
        # Try to move player by (dx, dy)
        #dx diff x, dy diff y
        #nx new x, ny new y
        oldDir = self.dir
        self.x = clamp(self.x + dx, 0, W - 1)
        self.y = clamp(self.y + dy, 0, H - 1)
        #t = board.grid[ny][nx]
        self.rect.topleft = (self.x * TILE, self.y * TILE)
        self.dir = (self.dir + ddir) % 4
        self._draw()
            
        print("oldDir: ", oldDir, "self.dir: ", self.dir)

    def moveForward(self, steps):
        #rykker player med kort
        if self.dir == 0: # Direction: 0=up, 1=right, 2=down, 3=left
            self.move(0, -steps, 0)
        elif self.dir == 1:
            self.move(steps, 0, 0)
        elif self.dir == 2:
            self.move(0, steps, 0)
        elif self.dir == 3:
            self.move(-steps, 0, 0)
        else: 
            raise IllegalDirection()
        self.rect.topleft = (self.x * TILE, self.y * TILE)
        
    def rotate(self, steps):
        # Rotate player clockwise or counterclockwise
        self.dir = (self.dir + steps) % 4
        self._draw()