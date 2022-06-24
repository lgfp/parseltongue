import logging
from functools import cached_property
from typing import Iterable, Sized, Union, Optional

from model import Mask, Grouping, MaskInstance


class Guess:
    def __init__(self, guess: str, answers: Iterable[str]):
        self._guess = guess
        self.__eligibles = answers
        self.__split_sizes = None

    @cached_property
    def is_the_solution(self) -> bool:
        if self.n_splits != 1:
            return False
        return list(self._eligible_solutions) == [self._guess]

    @cached_property
    def is_useless(self) -> bool:
        return self.n_splits == 1 and not self.is_the_solution

    @cached_property
    def largest_split(self) -> int:
        return max(len(grouping) for grouping in self._answer_groupings.values())

    @cached_property
    def _answer_groupings(self) -> Grouping:
        logging.debug("Calculate grouping for %s" % self._guess)
        grouping: Grouping = dict()
        for answer in self.__eligibles:
            mask = Mask.for_answer(answer, self._guess)
            grouping.setdefault(mask, [])
            grouping[mask].append(answer)
        return grouping

    @cached_property
    def _eligible_solutions(self) -> Union[Iterable[str], Sized]:
        if (self.__eligibles):
            return self.__eligibles
        self.__eligibles = set(word for grouping in self._answer_groupings.values() for word in grouping)
        return self.__eligibles

    @cached_property
    def mean_split_size(self) -> float:
        return len(self._eligible_solutions) / self.n_splits

    @cached_property
    def n_splits(self) -> int:
        return len(self._answer_groupings)

    @cached_property
    def median_split_size(self) -> float:
        split_sizes = self.split_sizes
        n = len(split_sizes)
        if n % 2 == 0:
            return (split_sizes[n//2-1] + split_sizes[n//2])/2
        return split_sizes[n//2]

    @cached_property
    def split_sizes(self):
        if self.__split_sizes:
            return self.__split_sizes
        self.__split_sizes = sorted(len(gi) for gi in self._answer_groupings.values())
        return self.__split_sizes

    @cached_property
    def next_solving_percentage(self) -> float:
        return 100 * self.n_splits / len(self._eligible_solutions)

    @cached_property
    def split_stdev(self) -> float:
        variance = sum(pow(si-self.mean_split_size, 2) for si in self.split_sizes)/self.n_splits
        return pow(variance, 1/2)

    @cached_property
    def is_eligible(self) -> bool:
        return self._guess in self._eligible_solutions

    @cached_property
    def current_solving_percentage(self) -> float:
        return 100 / len(self._eligible_solutions) if self._guess in self._eligible_solutions else 0

    def __str__(self):
        return "%s%s: %d splits (mean: %.2f, median: %.1f, stdev: %.2f, max: %d) win prob: %.2f%% -> %.2f%% " % (
            "x " if self.is_the_solution else "* " if self.is_eligible else "  ",
            self._guess,
            self.n_splits,
            self.mean_split_size,
            self.median_split_size,
            self.split_stdev,
            self.split_sizes[-1],
            self.current_solving_percentage,
            self.next_solving_percentage
        )

    def equiv(self, other):
        if other is None: return False
        if self.is_eligible or other.is_eligible: return False
        return list(self._answer_groupings.values()) == list(other.__grouping.values())


def coalesce(l: Iterable[Guess], await_eligible: bool = False, count: Optional[int] = None):
    last: Optional[Guess] = None
    for guess in l:
        if guess.is_eligible: await_eligible = False
        proceed = count > 0 or guess.is_eligible
        if not guess.equiv(last) and not guess.is_useless and proceed:
            yield guess
            if count is not None: count -= 1
            if count <= 0 and not await_eligible: return
        last = guess