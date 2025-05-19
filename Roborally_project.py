import os
import pygame
import sys
import math

# ─── Constants ────────────────────────────────────────────────────────────────
TILE   = 108                     # Size of each tile in pixels
W, H   = 12, 9                   # Width and height of the board in tiles
SCREEN = (TILE * W, TILE * H + 80)  # Window size including UI space
BG     = (40, 40, 50)           # Background color
FPS    = 30                     # Frames per second

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
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.x, self.y = x, y
        self.dir       = 0        # Direction: 0=up, 1=right, 2=down, 3=left
        self.next_flag = 1
        self.alive     = True
        self.color     = color

        self.image = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(topleft=(x * TILE, y * TILE))
        self._draw()

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

    def rotate(self, cw=True):
        # Rotate player clockwise or counterclockwise
        self.dir = (self.dir + (1 if cw else -1)) % 4
        self._draw()

# ─── Tile Image Loader ───────────────────────────────────────────────────────
def load_images(path='tiles'):
    imgs = {}
    for name in TILES:
        fn = os.path.join(path, f"{name}.png")
        imgs[name] = pygame.transform.scale(
            pygame.image.load(fn).convert_alpha(), (TILE, TILE)
        )
    for ov in ['tile-laser-1-overlay', 'tile-laser-1-start-overlay']:
        fn = os.path.join(path, f"{ov}.png")
        if os.path.exists(fn):
            imgs[ov] = pygame.transform.scale(
                pygame.image.load(fn).convert_alpha(), (TILE, TILE)
            )
    return imgs

# ─── Game Board ──────────────────────────────────────────────────────────────
class Board:
    def __init__(self, images):
        global board
        board = self
        self.images = images

        # Define the tile grid (9 rows of 12 columns)
        self.grid = [

            # Row 1 
            ['tile-clear', 'tile-clear', 'tile-conveyor-2-turnright',
             'tile-conveyor-2', 'tile-conveyor-2', 'tile-hammer-wrench',
             'tile-conveyor-2', 'tile-conveyor-2', 'tile-conveyor-2',
             'tile-conveyor-2-turnleft', 'tile-clear', 'tile-clear'],

            # Row 2
             ['tile-clear', 'tile-clear', 'tile-conveyor-2',
             'tile-clear', 'tile-clear', 'tile-clear',
             'tile-clear', 'tile-clear', 'tile-clear',
             'tile-clear', 'tile-conveyor-2', 'tile-clear'],

            # Row 3
            ['tile-clear', 'tile-clear', 'tile-conveyor-2',
             'tile-laser-1', 'tile-conveyor-2', 'tile-clear',
             'tile-clear', 'tile-clear', 'tile-conveyor-2',
             'tile-laser-1', 'tile-conveyor-2', 'tile-clear'],

            # Row 4
            ['tile-clear', 'tile-clear', 'tile-conveyor-2',
             'tile-conveyor-1', 'tile-conveyor-1', 'tile-conveyor-1',
             'tile-conveyor-1', 'tile-conveyor-1', 'tile-conveyor-2',
             'tile-clear', 'tile-clear', 'tile-clear'],

            # Row 5
            ['tile-clear', 'tile-clear', 'tile-conveyor-2',
             'flag1', 'tile-clear', 'tile-clear',
             'tile-clear', 'flag2', 'tile-conveyor-2',
             'tile-clear', 'tile-clear', 'tile-clear'],

            # Row 6
            ['tile-clear', 'tile-clear', 'tile-conveyor-2',
             'tile-conveyor-1', 'tile-conveyor-1', 'tile-conveyor-1',
             'tile-conveyor-1', 'tile-conveyor-1', 'tile-conveyor-2',
             'tile-clear', 'tile-clear', 'tile-clear'],

            # Row 7
            ['tile-clear', 'tile-clear', 'tile-conveyor-2',
             'tile-laser-1', 'tile-conveyor-2', 'tile-clear',
             'tile-clear', 'tile-clear', 'tile-conveyor-2',
             'tile-laser-1', 'tile-conveyor-2', 'tile-clear'],

            # Row 8
            ['tile-clear', 'tile-clear', 'tile-hole',
             'tile-clear', 'tile-clear', 'tile-clear',
             'tile-clear', 'tile-clear', 'tile-clear',
             'tile-hole', 'tile-clear', 'tile-clear'],

            # Row 9
            ['tile-clear', 'tile-clear', 'tile-conveyor-2-turnleft',
              'tile-conveyor-2', 'tile-conveyor-2', 'tile-conveyor-2',
             'tile-wrench', 'tile-conveyor-2', 'tile-conveyor-2',
             'tile-conveyor-2-turnright', 'tile-clear', 'tile-clear']
        ]

    def draw(self, surf):
        # Draw grid tiles
        for y in range(H):
            for x in range(W):
                key = self.grid[y][x]
                tile_key = 'tile-clear' if key.startswith('flag') else key
                surf.blit(self.images[tile_key], (x * TILE, y * TILE))
                ov = key + '-overlay'
                if ov in self.images:
                    surf.blit(self.images[ov], (x * TILE, y * TILE))
                if key.startswith('flag'):
                    hl = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                    hl.fill((255,255,255,160))  # semi-transparent white
                    surf.blit(hl, (x * TILE, y * TILE))

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
                    print(f"{p.name} captured flag {n}")
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

class Card:
    def __init__(self):
        pass
    # have 9 kort og vælge fem 
    # rykke frem 1
    # rykke frem 2
    # rykke frem 3
    # rykke til højre
    # rykke til venstre
    # uturn 
    # rykke tilbage 1

# ─── Game Loop ───────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN)
        pygame.display.set_caption("RoboRally Right Track")
        self.clock  = pygame.time.Clock()
        imgs        = load_images('tiles')
        self.board  = Board(imgs)
        global game; game = self

        self.players = pygame.sprite.Group()
        self.players.add(Player(0, H - 1, (255, 255, 255)))  # Add 1 player

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN:
                    p = next(iter(self.players))
                    if e.key == pygame.K_UP:    p.move(0, -1)
                    elif e.key == pygame.K_DOWN:  p.move(0, 1)
                    elif e.key == pygame.K_LEFT:  p.move(-1, 0)
                    elif e.key == pygame.K_RIGHT: p.move(1, 0)

            self.board.apply(self.players)
            self.screen.fill(BG)
            self.board.draw(self.screen)
            self.players.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()