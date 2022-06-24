from functools import cached_property
from typing import Iterable, Union, Sized

from . import Grouping
from .guess import Guess


class MultiGuess(Guess):
    def __init__(self, *guess: Guess):
        super().__init__(guess[0]._guess, guess[0]._eligible_solutions)
        self.__guesses: Iterable[Guess] = guess
        self.__remaining = sum(1 for _ in guess)

    @property
    def is_the_solution(self) -> bool:
        return self.is_a_solution

    @cached_property
    def current_solving_percentage(self) -> float:
        csp = max(guess.current_solving_percentage for guess in self.__guesses)
        if (csp > 99): print([(g._guess,csp) for g in self.__guesses])
        return csp

    @cached_property
    def is_a_solution(self) -> bool:
        return any(guess.is_the_solution for guess in self.__guesses)

    @cached_property
    def is_useless(self) -> bool:
        return all(guess.is_useless for guess in self.__guesses)

    @cached_property
    def largest_split(self) -> int:
        return min(guess.largest_split for guess in self.__guesses)

    @cached_property
    def mean_split_size(self) -> float:
        return sum(len(guess._eligible_solutions) for guess in self.__guesses) / self.n_splits

    @cached_property
    def n_splits(self) -> int:
        return sum(guess.n_splits for guess in self.__guesses)

    @cached_property
    def split_sizes(self):
        return sorted(size for guess in self.__guesses for size in guess.split_sizes)

    @cached_property
    def next_solving_percentage(self) -> float:
        return min(guess.next_solving_percentage for guess in self.__guesses)

    @cached_property
    def _eligible_solutions(self) -> Union[Iterable[str], Sized]:
        return set(eligible for guess in self.__guesses for eligible in guess._eligible_solutions)
