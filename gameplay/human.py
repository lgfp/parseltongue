from gameplay.guidance import Guidance
from model.engine import Engine
from model.masks import MaskInstance
from gameplay.player import Player


class HumanPlayer(Player):
    def __init__(self, engine: Engine, guidance: Guidance = Guidance()):
        self.__engine = engine
        self.__guide = guidance

    def provide(self) -> str:
        self.__guide.guide()
        valid = False
        guess: str
        while not valid:
            guess = input("Your guess: ")
            valid = self.__engine.acceptable_guess(guess)
            if not valid and guess != "giveup":
                print("Not a valid guess.")
        return guess

    def accept(self, *mask: MaskInstance):
        self.__engine = self.__engine.pruned(*mask)
