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