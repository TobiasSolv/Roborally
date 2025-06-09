import os
import pygame
import sys
import math
from card import generateDeck
#import board
#import player
from helpers import clamp

#færdig
#undgå overflow 
#lav knap virker når man har valgt 5 kort
#gør så man kun kan vælge 5 kort
#ny runde knap der giver 9 nye kort og fjerder de gamle kort
#start spillet med 9 kort

#TODO
#rydde op
#robot spiller

# ─── Constants ────────────────────────────────────────────────────────────────
TILE   = 90                     # Size of each tile in pixels
W, H   = 18, 8                  # Width and height of the board in tiles
BG     = (40, 40, 50)           # Background color
FPS    = 30                     # Frames per second
CARD_W = 1.5 * TILE
CARD_H = 2 * TILE
CARD_AREA_START_X = 0
CARD_AREA_START_Y = TILE * H
CARD_AREA_W = TILE * W
CARD_AREA_H = CARD_H * 2
SCREEN = (TILE * W, TILE * H + CARD_AREA_H)  # Window size including UI space
PROGRAM_LIMIT = 5

# ─── Tile Types and Tile Effects ─────────────────────────────────────────────
TILES = [
    'tile-clear',
    'tile-conveyor-1-threeway-1', 'tile-conveyor-1-threeway-2',
    'tile-hole',
    'tile-laser-1', 'tile-laser-1-start',
    'tile-wall-1', 'tile-wall-2',
    'tile-wrench', 'tile-hammer-wrench',
    'tile-conveyorRight-1',
    'tile-conveyorDown-1',
    'tile-conveyorUp-1',
    'tile-conveyorLeft-1',
    "tile-conveyor-1-turnLeftFromDown",
    "tile-conveyor-1-turnLeftFromLeft",
    "tile-conveyor-1-turnLeftFromRight",
    "tile-conveyor-1-turnLeftFromUp",
    "tile-conveyor-1-turnRightFromDown",
    "tile-conveyor-1-turnRightFromLeft",
    "tile-conveyor-1-turnRightFromRight",
    "tile-conveyor-1-turnRightFromUp",
]

CARDS = [
    "forward_1",
    "forward_2",
    "forward_3",
    "backward",
    "turn_right",
    "turn_left",
    "uturn",
]

LEFT = -1
RIGHT = 1
# Mapping from tile type to effect
EFFECT = {
    # Conveyors: move right
    #'tile-conveyor-2':              (2, 0), 
    #'tile-conveyor-2-turnleft':     (2, 0),
    #'tile-conveyor-2-turnright':    (2, 0),
    #'tile-conveyor-2-threeway-1':   (2, 0),
    #'tile-conveyor-2-threeway-2':   (2, 0),
    #'tile-conveyor-1':              (1, 0),
    #'tile-conveyor-1-turnleft':     (1, 0),
    #'tile-conveyor-1-turnright':    (1, 0),
    #'tile-conveyor-1-threeway-1':   (1, 0),
    #'tile-conveyor-1-threeway-2':   (1, 0),
    "tile-conveyor-1-turnLeftFromDown": (-1, 0, LEFT),
    "tile-conveyor-1-turnLeftFromLeft": (0, -1, LEFT),
    "tile-conveyor-1-turnLeftFromRight": (0, 1, LEFT),
    "tile-conveyor-1-turnLeftFromUp": (1, 0, LEFT),
    "tile-conveyor-1-turnRightFromDown": (1, 0, RIGHT),
    "tile-conveyor-1-turnRightFromLeft": (0, 1, RIGHT),
    "tile-conveyor-1-turnRightFromRight": (0, -1, RIGHT),
    "tile-conveyor-1-turnRightFromUp": (-1, 0, RIGHT),
    'tile-conveyorRight-1': (1, 0, 0),  # right
    'tile-conveyorLeft-1':  (-1, 0, 0), # left 
    'tile-conveyorUp-1':    (0, -1, 0), # up
    'tile-conveyorDown-1':  (0, 1, 0),  # down
    # Holes destroy players
    'tile-hole':                    'destroy',
    # Lasers fire horizontal beams
    'tile-laser-1':                 'laser_h',
    'tile-laser-1-start':           'laser_h'
}

# ─── Globals ─────────────────────────────────────────────────────────────────
board = None  # Global reference to the game board
game  = None  # Global reference to the game instance

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

# ─── Tile Image Loader ───────────────────────────────────────────────────────
def load_images(tiles_path='tiles', cards_path='cards'):
    imgs = {}
    for name in TILES:
        fn = os.path.join(tiles_path, f"{name}.png")
        img = pygame.image.load(fn).convert_alpha()
        imgs[name] = pygame.transform.scale(img, (TILE, TILE))
    for name in CARDS:
        fn = os.path.join(cards_path, f"{name}.png")
        img = pygame.image.load(fn).convert_alpha()
        imgs[name] = pygame.transform.scale(img, (CARD_W, CARD_H))
    for ov in ['tile-laser-1-overlay', 'tile-laser-1-start-overlay']:
        fn = os.path.join(tiles_path, f"{ov}.png")
        img = pygame.image.load(fn).convert_alpha()
        imgs[ov] = pygame.transform.scale(img, (TILE, TILE))
    return imgs

# ─── Game Board ──────────────────────────────────────────────────────────────
class Board:
    def __init__(self, images):
        global board
        board = self
        self.images = images

        self.grid = [
    # Row 1 - Top border with walls and entry points
    ['tile-clear', 'tile-clear', 'tile-clear', 'tile-laser-1-start', 'tile-clear', 'tile-clear', 'tile-clear', 'tile-clear', 'tile-clear', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-laser-1-start', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1'],
    
    # Row 2 - Starting area with conveyor system leading to first challenge
    ['tile-clear', 'tile-clear', 'tile-clear', 'tile-laser-1', 'tile-conveyorRight-1', 'tile-conveyorRight-1', 'tile-conveyorRight-1', 'tile-clear', 'tile-wrench', 'tile-clear', 'tile-clear', 'tile-conveyorRight-1', 'tile-conveyorRight-1', 'tile-laser-1', 'tile-clear', 'tile-clear', 'flag1', 'tile-wall-1'],
    
    # Row 3 - Complex conveyor maze with obstacles
    ['tile-clear', 'tile-clear', 'tile-wall-2', 'tile-clear', 'tile-clear', 'tile-hole', 'tile-conveyorLeft-1', 'tile-clear', 'tile-clear', 'tile-clear', 'tile-conveyorUp-1', 'tile-hole', 'tile-clear', 'tile-clear', 'tile-wall-2', 'tile-clear', 'tile-clear', 'tile-wall-1'],
    
    # Row 4 - Central hub with multiple paths
    ['tile-conveyor-1-turnRightFromDown', 'tile-conveyor-1-turnRightFromLeft', 'tile-clear', 'tile-conveyorLeft-1', 'tile-conveyorLeft-1', 'tile-clear', 'tile-clear', 'tile-conveyorLeft-1', 'tile-conveyorLeft-1', 'tile-conveyorLeft-1', 'tile-clear', 'tile-clear', 'tile-conveyorRight-1', 'tile-conveyorRight-1', 'tile-clear', 'flag2', 'tile-clear', 'tile-wall-1'],
    
    # Row 5 - Laser gauntlet with strategic positioning
    ['tile-conveyor-1-turnRightFromRight', 'tile-conveyor-1-turnRightFromUp', 'tile-laser-1-start', 'tile-clear', 'tile-clear', 'tile-wall-2', 'tile-clear', 'tile-clear', 'tile-wall-2', 'tile-wall-2', 'tile-clear', 'tile-clear', 'tile-clear', 'tile-clear', 'tile-clear', 'tile-laser-1-start', 'tile-clear', 'tile-wall-1'],
    
    # Row 6 - Return path with turning conveyors
    ['tile-conveyor-1-turnLeftFromRight', 'tile-conveyor-1-turnLeftFromDown', 'tile-laser-1', 'tile-conveyorRight-1', 'tile-clear', 'tile-clear', 'tile-conveyorRight-1', 'tile-conveyorRight-1', 'tile-clear', 'tile-clear', 'tile-conveyorLeft-1', 'tile-conveyorLeft-1', 'tile-clear', 'tile-clear', 'tile-clear', 'tile-laser-1', 'flag3', 'tile-wall-1'],
    
    # Row 7 - Final approach with hazards and repair stations
    ['tile-conveyor-1-turnLeftFromUp', 'tile-conveyor-1-turnLeftFromLeft', 'tile-clear', 'tile-clear', 'tile-clear', 'tile-hole', 'tile-clear', 'tile-clear', 'tile-conveyorDown-1', 'tile-clear', 'tile-conveyorRight-1', 'tile-hole', 'tile-conveyorLeft-1', 'tile-clear', 'tile-clear', 'tile-hammer-wrench', 'tile-clear', 'tile-wall-1'],
    
    # Row 8 - Bottom border with finishing area
    ['tile-clear', 'tile-clear', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1', 'tile-wall-1']
]
    def draw(self, surface):
        # Draw grid tiles
        for y in range(H):
            for x in range(W):
                key = self.grid[y][x]
                tile_key = 'tile-clear' if key.startswith('flag') else key
                surface.blit(self.images[tile_key], (x * TILE, y * TILE))
                ov = key + '-overlay'
                if ov in self.images:
                    surface.blit(self.images[ov], (x * TILE, y * TILE))
                if key.startswith('flag'):
                    hl = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                    hl.fill((255,255,255,160))  # semi-transparent white
                    surface.blit(hl, (x * TILE, y * TILE))

    def apply(self, players):
        # Apply tile effects (conveyors, holes, lasers, flags)
        for p in players:
            if not p.alive: continue
            x = self.grid[p.y][p.x]
            e = EFFECT.get(x)
            print("apply: ", x, e)
            if isinstance(e, tuple): p.move(*e)

        for p in players:
            if not p.alive: continue
            if EFFECT.get(self.grid[p.y][p.x]) == 'destroy':
                p.alive = False

        for p in players:
            if not p.alive: continue
            if EFFECT.get(self.grid[p.y][p.x]) == 'laser_h':
                self._fire(p.x, p.y)

        for p in players:
            if not p.alive: continue
            t = self.grid[p.y][p.x]
            if t.startswith('flag'):
                n = int(t.replace('flag',''))
                if n == p.next_flag:
                    print(f"{p} captured flag {n}")
                    p.next_flag += 1

    def _fire(self, x, y):
        # Fire laser horizontally from (x, y)
        for dx in (1, -1):
            cx = x + dx
            while 0 <= cx < W:
                if self.grid[y][cx].startswith('tile-wall'): break
                for p in game.players:
                    if p.alive and (p.x, p.y) == (cx, y):
                        p.alive = False
                        print(f"{p.name} zapped!")
                cx += dx

# ─── Game Loop ───────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN)
        pygame.display.set_caption("RoboRally Right Track")
        self.clock  = pygame.time.Clock()
        self.images = load_images('tiles')
        self.board  = Board(self.images)
        global game; game = self
        self.deck = []

        self.players = pygame.sprite.Group()
        self.players.add(Player(0, H - 1, (255, 255, 255)))  # Add 1 player

    def executeCards(self, cards):
        for card in cards: 
            player = next(iter(self.players))
            print('before executing ' + str(card) + ': ' + str(player))
            card.execute(self.board, player)
            print('after executing ' + str(card) + ': ' + str(player))
        for player in self.players:
            player.executed = True 

    def drawCards(self, surface):
        player0 = next(iter(self.players))
        #tegner hånden
        for i, card in enumerate(player0.hand): 
            x = CARD_W * i
            y = CARD_AREA_START_Y
            surface.blit(self.images[card.name], (x, y))
        #tegner programmet 
        for i, card in enumerate(player0.program): 
            x = CARD_W * i
            y = CARD_AREA_START_Y + CARD_H
            surface.blit(self.images[card.name], (x, y))

    def drawButtons(self, surface):
        #run program knap
        player0 = next(iter(self.players))
        enableColor = (0, 0, 80)
        disableColor = (127, 127, 127)
        x = CARD_W * PROGRAM_LIMIT
        y = CARD_AREA_START_Y + CARD_H
        if len(player0.program) == PROGRAM_LIMIT and not player0.executed:
            actualColor = enableColor
        else:
            actualColor = disableColor
        pygame.draw.rect(surface, actualColor, pygame.Rect(x + 25, y + 50, CARD_W - 50, CARD_H - 100))
        #new round knap
        x = CARD_W * (PROGRAM_LIMIT + 1)
        y = CARD_AREA_START_Y + CARD_H
        if player0.executed:
            actualColor = enableColor
        else:
            actualColor = disableColor
        pygame.draw.rect(surface, actualColor, pygame.Rect(x + 25, y + 50, CARD_W - 50, CARD_H - 100))

    def isCardClicked(self, pos):
        x, y = pos
        if y < CARD_AREA_START_Y:
            return ("board", None)
        elif y < CARD_AREA_START_Y + CARD_H:
            return ("hand", int(x/CARD_W))
        elif y < CARD_AREA_START_Y + 2 * CARD_H:
            return ("program", int(x / CARD_W))
        else: 
            return ("outside", None)
        
    def createNewRound(self):
        self.deck = generateDeck()
        for player in self.players:
            player.executed = False
            player.hand = []
            player.program = []
        for _ in range(9):
            for player in self.players:
                card = self.deck.pop()
                player.hand.append(card)

  
    def run(self):
        player0 = next(iter(self.players))
        self.createNewRound()
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN: 
                        self.createNewRound()
                    elif e.key == pygame.K_k: 
                        self.executeCards(player0.program)
                        self.board.apply(self.players)
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    clickArea, clickIndex = self.isCardClicked(e.pos)
                    print(e.pos, clickArea, clickIndex)
                    if clickArea == "hand" and clickIndex < len(player0.hand) and len(player0.program) < PROGRAM_LIMIT:
                        card = player0.hand.pop(clickIndex)
                        player0.program.append(card)
                    elif clickArea == "program" and clickIndex < len(player0.program):
                        card = player0.program.pop(clickIndex)
                        player0.hand.append(card)
                    elif clickArea == "program" and clickIndex == PROGRAM_LIMIT and len(player0.program) == PROGRAM_LIMIT and not player0.executed:
                        self.executeCards(player0.program)
                        self.board.apply(self.players)
                    elif clickArea == "program" and clickIndex == PROGRAM_LIMIT + 1 and player0.executed:
                        self.createNewRound()
                        



                         
                                                                    
            
            self.screen.fill(BG)
            self.board.draw(self.screen)
            self.players.draw(self.screen)
            self.drawCards(self.screen)
            self.drawButtons(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()