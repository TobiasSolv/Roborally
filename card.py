import random

class Card:
    def __init__(self):
        pass

    def execute(self, _board, _player):
        pass

def generateDeck():
    deck = [MoveForward("forward_1", 1), 
            MoveForward("forward_2", 2), 
            MoveForward("forward_3", 3), 
            MoveForward("backward", -1),
            Turn("turn_right", 1), 
            Turn("turn_left", 3), 
            Turn("uturn", 2)
        ] * 12
    random.shuffle(deck)
    return deck

class MoveForward(Card):
    def __init__(self, name, steps):
        self.name = name
        self.steps = steps


    def execute(self, _board, player):
        player.moveForward(self.steps)

    def __str__(self):
        return "MoveForward("+str(self.steps)+")"

class Turn(Card):
    def __init__(self, name, dir):
        self.name = name
        self.dir = dir
    
    def execute(self, _board, player):
        player.rotate(self.dir)

    def __str__(self):
        return "Turn("+str(self.dir)+")"
