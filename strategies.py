import logging
from typing import Tuple, Iterable

from model import Space, Grouping

class Strategy:
    def choose(self, space: Space) -> str:
        logging.debug("Choosing in space among %d words available" % len(space))
        chunked_answers = list(answers for choice in space.values() for answers in choice.values())
        answers = set(ans for answers in chunked_answers for ans in answers)

        sol = max(space.items(), key=lambda it: self._score(it[1], it[0] in answers))
        return sol[0]

    def _score(self, grouping: Grouping, is_answer:bool = False) -> Tuple[int, bool, int]:
        score = len(grouping), is_answer, -Strategy.wcs(grouping)
        return score

    @staticmethod
    def wcs(grouping: Grouping) -> int:
        return max(len(pruned) for pruned in grouping.values())


class Greedy(Strategy):
    """
    Tries to get the most chance to hit soon
    """

    def choose(self, space: Space) -> str:
        logging.debug("Choosing in space among %d words available" % len(space))
        chunked_answers = list(answers for choice in space.values() for answers in choice.values())
        answers = set(ans for answers in chunked_answers for ans in answers)

        top10 = sorted(space.items(), key=lambda it: self._score(it[1], it[0] in answers), reverse=True)[:10]
        return (list(filter(lambda t: t[0] in answers, top10)) + top10)[0][0]

    def _score(self, grouping: Grouping, is_answer:bool = False):
        hit_it_big = sum(1 for v in grouping.values() if len(v) == 1)
        n_splits = len(grouping)
        worst_case = max(len(v) for v in grouping.values())
        return hit_it_big, n_splits, is_answer, -worst_case


class Heuristic(Strategy):
    def __init__(self, threshold_for_guessing=5):
        self.threshold_for_guessing = threshold_for_guessing

    def choose(self, space: Space):
        chunked_answers = list(answers for choice in space.values() for answers in choice.values())
        self.answers = set(ans for answers in chunked_answers for ans in answers)

        logging.debug("Choosing in space among %d words and %d answers available" % (len(space), len(self.answers)))
        best = sorted(space.items(), key=lambda sp: self.__comparer(sp), reverse=True)

        def gen_best(best: Iterable[Tuple[str, Grouping]], limit: int):
            counter = 0
            last = None
            for e in best:
                if counter >= limit: return
                cur = list(e[1].values())
                if cur != last or e[0] in self.answers:
                    yield e
                    counter += 1
                last = cur

        displayed = list(gen_best(best, self.threshold_for_guessing))
        first_solution = next(filter(lambda p: p[0] in self.answers, best))
        if first_solution not in displayed[:5] and len(displayed[0][1]) > self.threshold_for_guessing:
            return displayed[0][0]
        else:
            return first_solution[0]

    def __comparer(self, g: Tuple[str, Grouping]):
        return len(g[1]), -max(len(v) for v in g[1].values()), g[0] in self.answers

