from typing import Tuple

from model.guess import Guess


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
        percentile = guess.split_sizes[index]
        return Sorters.prioritize(guess, (percentile,), eligibles_first)
