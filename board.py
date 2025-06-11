from constants import *
import pygame


LEFT = -1
RIGHT = 1
# Mapping from tile type to effect
EFFECT = {
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

# ─── Game Board ──────────────────────────────────────────────────────────────
class Board:
    def __init__(self, images):
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
                self._fire(p.x, p.y, players)

        for p in players:
            if not p.alive: continue
            t = self.grid[p.y][p.x]
            if t.startswith('flag'):
                n = int(t.replace('flag',''))
                if n == p.next_flag:
                    print(f"{p} captured flag {n}")
                    p.next_flag += 1

    def _fire(self, x, y, players):
        # Fire laser horizontally from (x, y)
        for dx in (1, -1):
            cx = x + dx
            while 0 <= cx < W:
                if self.grid[y][cx].startswith('tile-wall'): break
                for i, p in enumerate(players):
                    if p.alive and (p.x, p.y) == (cx, y):
                        p.alive = False
                        print(f"player {i} zapped!")
                cx += dx