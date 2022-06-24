from typing import Iterable, Sized, Union, Tuple, Optional

from model import Grouping

class Guess:
    def __init__(self, guess: str, grouping: Grouping,):
        self.__guess = guess
        self.__grouping = grouping

        self.__split_sizes = None
        self.__eligibles = None

    @property
    def is_the_solution(self) -> bool:
        if self.n_splits != 1:
            return False
        return list(self.__eligible_solutions()) == [self.__guess]

    @property
    def is_useless(self) -> bool:
        return self.n_splits == 1 and not self.is_the_solution

    @property
    def largest_split(self) -> int:
        return max(len(grouping) for grouping in self.__grouping.values())

    def __eligible_solutions(self) -> Union[Iterable[str], Sized]:
        if (self.__eligibles):
            return self.__eligibles
        self.__eligibles = set(word for grouping in self.__grouping.values() for word in grouping)
        return self.__eligibles

    @property
    def mean_split_size(self) -> float:
        return len(self.__eligible_solutions()) / self.n_splits

    @property
    def n_splits(self) -> int:
        return len(self.__grouping)

    @property
    def median_split_size(self) -> float:
        split_sizes = self.split_sizes()
        n = len(split_sizes)
        if n % 2 == 0:
            return (split_sizes[n//2-1] + split_sizes[n//2])/2
        return split_sizes[n//2]

    def split_sizes(self):
        if self.__split_sizes:
            return self.__split_sizes
        self.__split_sizes = sorted(len(gi) for gi in self.__grouping.values())
        return self.__split_sizes

    @property
    def next_solving_percentage(self) -> float:
        return 100 * self.n_splits / len(self.__eligible_solutions())

    @property
    def split_stdev(self) -> float:
        variance = sum(pow(si-self.mean_split_size, 2) for si in self.split_sizes())/self.n_splits
        return pow(variance, 1/2)

    @property
    def is_eligible(self) -> bool:
        return self.__guess in self.__eligible_solutions()


    def __str__(self):
        return "%s%s: %d splits (mean: %.2f, median: %.1f, stdev: %.2f, max: %d) win prob: %.2f%% -> %.2f%% " % (
            "+ " if self.is_the_solution else "* " if self.is_eligible else "  ",
            self.__guess,
            self.n_splits,
            self.mean_split_size,
            self.median_split_size,
            self.split_stdev,
            self.split_sizes()[-1],
            100/len(self.__eligible_solutions()) if self.__guess in self.__eligible_solutions() else 0,
            self.next_solving_percentage
        )

    def equiv(self, other):
        if other is None: return False
        if self.is_eligible or other.is_eligible: return False
        return list(self.__grouping.values()) == list(other.__grouping.values())


class Sorters:
    @staticmethod
    def always_first(guess: Guess) -> Tuple:
        return not guess.is_the_solution, guess.is_useless

    @staticmethod
    def ordinary(guess: Guess) -> Tuple:
        return (guess.mean_split_size, guess.median_split_size, guess.largest_split,
                not guess.is_eligible)

    @staticmethod
    def prioritize(guess: Guess, priority: Tuple, eligibles_first=False) -> Tuple:
        if eligibles_first:
            priority = (not guess.is_eligible,) + priority
        return Sorters.always_first(guess) + priority + Sorters.ordinary(guess)

    @staticmethod
    def worst_case_scenario(guess: Guess, eligibles_first=False) -> Tuple:
        return Sorters.prioritize(guess, (guess.largest_split,), eligibles_first)

    @staticmethod
    def most_splits(guess: Guess, eligibles_first=False):
        return Sorters.prioritize(guess, (), eligibles_first)

    @staticmethod
    def percentile(guess: Guess, percentile: int, eligibles_first=False):
        index = min(guess.n_splits * percentile // 100, guess.n_splits-1)
        percentile = guess.split_sizes()[index]
        return Sorters.prioritize(guess, (percentile,), eligibles_first)


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