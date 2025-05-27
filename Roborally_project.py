import os
import pygame
import sys
import math
import card

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

# ─── Tile Types and Tile Effects ─────────────────────────────────────────────
TILES = [
    'tile-clear',
    'tile-conveyor-1','tile-conveyor-1-threeway-1','tile-conveyor-1-threeway-2',
    'tile-conveyor-1-turnleft','tile-conveyor-1-turnright',
    'tile-conveyor-2','tile-conveyor-2-threeway-1','tile-conveyor-2-threeway-2',
    'tile-conveyor-2-turnleft','tile-conveyor-2-turnright',
    'tile-hole',
    'tile-laser-1','tile-laser-1-start',
    'tile-wall-1','tile-wall-2',
    'tile-wrench','tile-hammer-wrench'
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

# Mapping from tile type to effect
EFFECT = {
    # Conveyors: move right
    'tile-conveyor-2':              (2, 0),
    'tile-conveyor-2-turnleft':     (2, 0),
    'tile-conveyor-2-turnright':    (2, 0),
    'tile-conveyor-2-threeway-1':   (2, 0),
    'tile-conveyor-2-threeway-2':   (2, 0),
    'tile-conveyor-1':              (1, 0),
    'tile-conveyor-1-turnleft':     (1, 0),
    'tile-conveyor-1-turnright':    (1, 0),
    'tile-conveyor-1-threeway-1':   (1, 0),
    'tile-conveyor-1-threeway-2':   (1, 0),
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

    def move(self, dx, dy):
        # Try to move player by (dx, dy)
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < W and 0 <= ny < H:
            t = board.grid[ny][nx]
            if not t.startswith('tile-wall'):
                self.x, self.y = nx, ny
                self.rect.topleft = (nx * TILE, ny * TILE)

    def moveForward(self, steps):
        if self.dir == 0: # Direction: 0=up, 1=right, 2=down, 3=left
            self.y -= steps
        elif self.dir == 1:
            self.x += steps
        elif self.dir == 2:
            self.y += steps
        elif self.dir == 3:
            self.x -= steps
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
            ['tile-clear'] * W
        ] * H
        # Define the tile grid (9 rows of 12 columns)
        # self.grid = [

        #     # Row 1 
        #     ['tile-clear', 'tile-clear', 'tile-conveyor-2-turnright',
        #      'tile-conveyor-2', 'tile-conveyor-2', 'tile-hammer-wrench',
        #      'tile-conveyor-2', 'tile-conveyor-2', 'tile-conveyor-2',
        #      'tile-conveyor-2-turnleft', 'tile-clear', 'tile-clear'],

        #     # Row 2
        #      ['tile-clear', 'tile-clear', 'tile-conveyor-2',
        #      'tile-clear', 'tile-clear', 'tile-clear',
        #      'tile-clear', 'tile-clear', 'tile-clear',
        #      'tile-clear', 'tile-conveyor-2', 'tile-clear'],

        #     # Row 3
        #     ['tile-clear', 'tile-clear', 'tile-conveyor-2',
        #      'tile-laser-1', 'tile-conveyor-2', 'tile-clear',
        #      'tile-clear', 'tile-clear', 'tile-conveyor-2',
        #      'tile-laser-1', 'tile-conveyor-2', 'tile-clear'],

        #     # Row 4
        #     ['tile-clear', 'tile-clear', 'tile-conveyor-2',
        #      'tile-conveyor-1', 'tile-conveyor-1', 'tile-conveyor-1',
        #      'tile-conveyor-1', 'tile-conveyor-1', 'tile-conveyor-2',
        #      'tile-clear', 'tile-clear', 'tile-clear'],

        #     # Row 5
        #     ['tile-clear', 'tile-clear', 'tile-conveyor-2',
        #      'flag1', 'tile-clear', 'tile-clear',
        #      'tile-clear', 'flag2', 'tile-conveyor-2',
        #      'tile-clear', 'tile-clear', 'tile-clear'],

        #     # Row 6
        #     ['tile-clear', 'tile-clear', 'tile-conveyor-2',
        #      'tile-conveyor-1', 'tile-conveyor-1', 'tile-conveyor-1',
        #      'tile-conveyor-1', 'tile-conveyor-1', 'tile-conveyor-2',
        #      'tile-clear', 'tile-clear', 'tile-clear'],

        #     # Row 7
        #     ['tile-clear', 'tile-clear', 'tile-conveyor-2',
        #      'tile-laser-1', 'tile-conveyor-2', 'tile-clear',
        #      'tile-clear', 'tile-clear', 'tile-conveyor-2',
        #      'tile-laser-1', 'tile-conveyor-2', 'tile-clear'],

        #     # Row 8
        #     ['tile-clear', 'tile-clear', 'tile-hole',
        #      'tile-clear', 'tile-clear', 'tile-clear',
        #      'tile-clear', 'tile-clear', 'tile-clear',
        #      'tile-hole', 'tile-clear', 'tile-clear'],

        #     # Row 9
        #     ['tile-clear', 'tile-clear', 'tile-conveyor-2-turnleft',
        #       'tile-conveyor-2', 'tile-conveyor-2', 'tile-conveyor-2',
        #      'tile-wrench', 'tile-conveyor-2', 'tile-conveyor-2',
        #      'tile-conveyor-2-turnright', 'tile-clear', 'tile-clear']
        # ]

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
            e = EFFECT.get(self.grid[p.y][p.x])
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
        self.images        = load_images('tiles')
        self.board  = Board(self.images)
        global game; game = self
        self.deck = card.generateDeck()

        self.players = pygame.sprite.Group()
        self.players.add(Player(0, H - 1, (255, 255, 255)))  # Add 1 player

    def executeCards(self, cards):
        for card in cards: 
            """
            #print('before executing ' + str(card) + ': ' + str(self.players[0]))
            #card.execute(self.board, self.players[0])
            #print('after executing ' + str(card) + ': ' + str(self.players[0]))
            player = next(iter(self.players))
            """
            player = next(iter(self.players))
            print('before executing ' + str(card) + ': ' + str(player))
            card.execute(self.board, player)
            print('after executing ' + str(card) + ': ' + str(player))

    def drawCards(self, surface):
        player0 = next(iter(self.players))
        for i, card in enumerate(player0.hand): 
            x = CARD_W * i
            y = CARD_AREA_START_Y
            surface.blit(self.images[card.name], (x, y))
        for i, card in enumerate(player0.program): 
            x = CARD_W * i
            y = CARD_AREA_START_Y + CARD_H
            surface.blit(self.images[card.name], (x, y))

    def isCardClicked(self, pos):
        x, y = pos
        if y < CARD_AREA_START_Y:
            return False
        elif y > CARD_AREA_START_Y + CARD_H:
            return False
        return int(x / CARD_W)

  
    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN: 
                        for _ in range(9):
                            for player in self.players:
                                card = self.deck.pop()
                                player.hand.append(card)
                    elif e.key == pygame.K_k: 
                        player0 = next(iter(self.players))
                        self.executeCards(player0.program)

                elif e.type == pygame.MOUSEBUTTONDOWN:
                    x = self.isCardClicked(e.pos)
                    print(e.pos, x)
                    if str(x).isnumeric():
                        player0 = next(iter(self.players))
                        card = player0.hand.pop(x)
                        player0.program.append(card)
                        
                        
                        
                    
            self.board.apply(self.players)
            self.screen.fill(BG)
            self.board.draw(self.screen)
            self.players.draw(self.screen)
            self.drawCards(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()