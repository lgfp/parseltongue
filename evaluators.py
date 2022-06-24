from typing import List, Iterable

from model import MaskInstance, Mask
from visitors import Visitor


class Evaluator:
    visitor: List[Visitor] = None

    def evaluate(self, guess) -> Iterable[MaskInstance]:
        raise NotImplementedError

    def answer_found(self, guess):
        raise NotImplementedError

    def add_visitor(self, visitor: Visitor):
        if self.visitor is None: self.visitor = []
        self.visitor.append(visitor)

    @property
    def _visitors(self):
        return self.visitor if self.visitor else []


class KnownAnswerEvaluator(Evaluator):
    def __init__(self, *answer: str):
        self.__answers = list(answer)

    def evaluate(self, guess):
        masks = [MaskInstance.for_answer(answer, guess) for answer in self.__answers]
        for visitor in self._visitors:
            for mask in masks:
                visitor.visit(guess, mask.mask)
        return masks

    def answer_found(self, guess):
        self.__answers.remove(guess)


class InputEvaluator(Evaluator):
    def __init__(self, n_masks: int = 1):
        self.__n_masks = n_masks

    def evaluate(self, guess) -> Iterable[MaskInstance]:
        def single_mask():
            result_raw = input("Result (0 for gray, 1 for yellow, 2 for green, no spaces): ")
            mask = Mask([int(i) for i in list(result_raw)])
            return MaskInstance(mask, guess)

        masks = [single_mask() for _ in range(self.__n_masks)]
        for visitor in self._visitors:
            for mask in masks:
                visitor.visit(guess, mask.mask)
        return masks

    def answer_found(self, guess):
        self.__n_masks = self.__n_masks - 1
