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