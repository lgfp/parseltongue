import itertools
from copy import copy
from functools import partial
from typing import Dict, Iterable

from ai.sorting import Sorters
from gameplay import Guidance
from model import MaskInstance, Engine
from model.guess import Guess
from model.multi_guess import MultiGuess
from heapq import nsmallest


class Multitracker2(Guidance):
    def __init__(self, engine: Engine, n: int, skip_first=True):
        self.__engines = [copy(engine) for _ in range(n)]
        # we need to copy the engine
        self.__skip_first = skip_first
        self.__first = True

    def guide(self):
        if self.__skip_first and self.__first:
            self.__first = False
            return
        self.__first = False

        cutoff = 10
        guesses : Dict[str, Iterable[Guess]] = dict()
        print("Compiling all guesses... ", end='')
        for engine in self.__engines:
            for word in engine.words:
                guesses.setdefault(word, [])
                guesses[word] += [Guess(word, engine.eligible_answers)]
        print("done!")
        print("Compiling multi-guesses... ", end='')
        multiguesses = [MultiGuess(*guesses) for k,guesses in guesses.items()]
        print("done!")
        tips = {
            "Most chance to solve": lambda g: 100-g.current_solving_percentage,
            "Most splits": partial(Sorters.most_splits, eligibles_first=False),
            "Best worst case": partial(Sorters.worst_case_scenario, eligibles_first=False),
            "Solutions with most splits": partial(Sorters.most_splits, eligibles_first=True)
        }
        for name, tip in tips.items():
            print("\n%d %s ... " % (cutoff, name))
            best_guesses = nsmallest(cutoff, multiguesses, key=tip)
#            best_guesses = sorted(multiguesses, key=tip)[:5]
            for guess in best_guesses: print(guess)

    def commit(self, *mi: MaskInstance):
        print(mi)
        print("Pruning %d engines... " % len(self.__engines), end='')
        self.__engines = list(filter(lambda engine: len(engine.eligible_answers) > 0,
                                [engine.pruned(m) for m,engine in zip(mi,self.__engines)]))
        print("Done! (%d engines remaining)" % len(self.__engines))