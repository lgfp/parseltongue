from gameplay.computer import Computer
from gameplay.player import Player
from model import MaskInstance
from strategies import Strategy

class SpaceSearch(Player):
    def __init__(self, computer: Computer, strategy: Strategy, *first_words: str):
        self.__computer = computer
        self.__strategy = strategy
        self.__first_word = list(reversed(first_words))
        self.log = []

    def provide(self) -> str:
        if self.__first_word:
            choice = self.__first_word.pop()
        else:
            choice = self.__strategy.choose(self.__computer.solution_space)
        print(" > %s" % choice)
        return choice

    def accept(self, *mask: MaskInstance):
        self.__computer.update(*mask)
