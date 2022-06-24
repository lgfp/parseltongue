from random import choice
from typing import Optional

from model import Mask, Engine


class Visitor:
    def visit(self, guess: str, mask: Optional[Mask] = None):
        raise NotImplementedError


class GuessQualityVisitor(Visitor):
    def __init__(self, engine: Engine):
        self.__engine = engine

    def visit(self, guess, mask=None):
        grouping = self.__engine.compute_grouping(guess)
        grouping_values = grouping.values()
        n_groups = len(grouping_values)
        remaining = sum(len(group) for group in grouping_values)
        print("Your guess divides the space in %d groups among %d remaining answers" % (n_groups, remaining))
        if mask:
            print("Based on %s, this means there are %d remaining answers, such as %s"
                  % (mask, len(grouping[mask]), choice(grouping[mask])))
