import os
import pygame
import sys
from card import generateDeck
from constants import *
from player import Player
from board import Board


#færdig
#undgå overflow 
#lav knap virker når man har valgt 5 kort
#gør så man kun kan vælge 5 kort
#ny runde knap der giver 9 nye kort og fjerder de gamle kort
#start spillet med 9 kort
#rydde op

#TODO
#robot spiller
#lave et formål/ en win condition
#delay når man rykker sig
#prøve eksamen

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
            pygame.time.wait(200)
            self.redrawEverythin()
            print('after executing ' + str(card) + ': ' + str(player))
            self.board.apply(self.players)
            pygame.time.wait(200)
            self.redrawEverythin()
            print('after boards moves ' + str(card) + ': ' + str(player))
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
        self.run_img = pygame.image.load("happy_robot_run.png").convert_alpha()
        self.run_img = pygame.transform.scale(self.run_img, (CARD_W, CARD_H))

        self.run_grey_img = pygame.image.load("happy_robot_run_grey.png").convert_alpha()
        self.run_grey_img = pygame.transform.scale(self.run_grey_img, (CARD_W, CARD_H))

        #run program knap
        player0 = next(iter(self.players))
        x = CARD_W * PROGRAM_LIMIT
        y = CARD_AREA_START_Y + CARD_H
        if len(player0.program) == PROGRAM_LIMIT and not player0.executed:
            actualImg = self.run_img
        else:
            actualImg = self.run_grey_img
            
        buttonRect1 = pygame.Rect(x, y, CARD_W, CARD_H)
        surface.blit(actualImg, buttonRect1)

        #new round knap
        self.next_round_img = pygame.image.load("happy_robot_next_round.png").convert_alpha()
        self.next_round_img = pygame.transform.scale(self.next_round_img, (CARD_W, CARD_H))

        self.next_round_grey_img = pygame.image.load("happy_robot_next_round_grey.png").convert_alpha()
        self.next_round_grey_img = pygame.transform.scale(self.next_round_grey_img, (CARD_W, CARD_H))
        x = CARD_W * (PROGRAM_LIMIT + 1)
        y = CARD_AREA_START_Y + CARD_H
        if player0.executed:
            actualImg = self.next_round_img
        else:
            actualImg = self.next_round_grey_img
        
        buttonRect2 = pygame.Rect(x, y, CARD_W, CARD_H)
        surface.blit(actualImg, buttonRect2)

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

    def redrawEverythin(self):
        self.screen.fill(BG)
        self.board.draw(self.screen)
        self.players.draw(self.screen)
        self.drawCards(self.screen)
        self.drawButtons(self.screen)
        pygame.display.flip()
        self.clock.tick(FPS)

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
                        
            self.redrawEverythin()

if __name__ == "__main__":
    Game().run()