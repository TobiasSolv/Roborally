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