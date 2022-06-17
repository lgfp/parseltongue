from typing import Iterable, Tuple

from .computer import Computer
from model import Engine, Grouping


class Guidance:
    def guide(self):
        pass


class RemainingAnswerGuidance:
    def __init__(self, engine: Engine):
        self.__engine = engine

    def guide(self):
        eligible_answers = self.__engine.eligible_answers
        sample = list(eligible_answers)[:5] + (['...'] if len(eligible_answers) > 5 else [])
        print("Remaining answers: %s" % sample)


class CompleteGuidance(Guidance):
    def __init__(self, engine: Engine, computer: Computer, skip_first: bool = True):
        self.__engine = engine
        self.__computer = computer
        self.__skip_first = skip_first
        self.__first = True

    def guide(self):
        if not (self.__skip_first and self.__first):
            stats(self.__engine.eligible_answers, self.__computer.solution_space, cutoff=5)
        self.__first = False
        self.__computer.bust()


def stats(answers, sol_space, cutoff: int = 10):
    if len(answers) == 1:
        print("\nThere's only one eligible answer to the game:\n* %s" % next(answers.__iter__()))
        return

    print("Words with a star to their left are one of %d eligible answers to the game" % len(answers))
    print("\nTop 10 words with most splits (meaning they will divide most your solution)")

    def gen_best(best: Iterable[Tuple[str, Grouping]], limit: int):
        counter = 0
        last = None
        for e in best:
            if counter >= limit: return
            cur = list(e[1].values())
            if cur != last or e[0] in answers:
                yield e
                counter += 1
            last = cur

    def sort_by_slices(grouping: Grouping, is_answer: bool):
        n_splits = len(grouping)
        worst_case = max(len(v) for v in grouping.values())
        return n_splits, -worst_case, is_answer

    base_sorting = sorted(sol_space.items(), key=lambda s: sort_by_slices(s[1], s[0] in answers), reverse=True)
    most_splits = gen_best(base_sorting, cutoff)
    for word, grouping in most_splits:
        n_splits, worst_case, is_answer = sort_by_slices(grouping, word in answers)
        print("%s%s: divides space in %d splits with largest split sized %d" %
              ("* " if is_answer else "  ", word, n_splits, -worst_case))
    print("\nTop %d words with most chance of finding a solution on spot:" % cutoff)

    def sort_by_allin(grouping: Grouping, is_answer: bool):
        hit_it_big = sum(1 for v in grouping.values() if len(v) == 1)
        n_splits = len(grouping)
        worst_case = max(len(v) for v in grouping.values())
        return hit_it_big, n_splits, is_answer, -worst_case

    most_all_in = gen_best(sorted(sol_space.items(),
                         key=lambda s: sort_by_allin(s[1], s[0] in answers),
                         reverse=True), cutoff)
    for word, grouping in most_all_in:
        hit_it_big, n_splits, is_answer, worst_case = sort_by_allin(grouping, word in answers)
        print(
            "%s%s: may determine among %d answers on spot, and divides space in %d splits with largest split sized %d" %
            ("* " if is_answer else "  ", word, hit_it_big, n_splits, -worst_case))
    print("\nTop %d words with best worst case scenarios (meaning they guarantee it won't be that bad)" % cutoff)

    def sort_by_wcs(grouping: Grouping, is_answer: bool):
        n_splits = len(grouping)
        worst_case = max(len(v) for v in grouping.values())
        return worst_case, -n_splits, not is_answer

    best_of_worst = gen_best(sorted(sol_space.items(),
                           key=lambda s: sort_by_wcs(s[1], s[0] in answers)), cutoff)
    for word, grouping in best_of_worst:
        n_splits, worst_case, is_answer = sort_by_slices(grouping, word in answers)
        print("%s%s: has worst case scenario sized %d and divides space in %d splits " %
              ("* " if is_answer else "  ", word, -worst_case, n_splits))

    print("\nTop %d solutions that divide the solution space the most" % cutoff)
    best_solutions = list(filter(lambda b: b[0] in answers, base_sorting))[:cutoff]
    for word, grouping in best_solutions:
        n_splits, worst_case, is_answer = sort_by_slices(grouping, word in answers)
        print("* %s: has worst case scenario sized %d and divides space in %d splits " %
              (word, -worst_case, n_splits))
