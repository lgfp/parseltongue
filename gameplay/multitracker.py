import itertools
import logging
import sys
from copy import copy
from typing import Iterable

import ai
from model import MaskInstance, Engine
from .computer import Computer
from .guidance import Guidance


class Multitracker(Guidance):
    __computers: Iterable[Computer]

    def __init__(self, engine: Engine, n: int, skip_first=None):
        # we need to copy the engine
        self.__computers = [Computer(copy(engine), engine.hard_mode) for _ in range(n)]
        self.__skip_first = skip_first
        self.__first = True

    def update(self, *mi: MaskInstance):
        # MaskInstances MUST be ordered
        for m,c in zip(mi, self.__computers):
            c.update(m)

    def guide(self):
        if self.__skip_first and self.__first:
            self.__first = False
            return
        if self.__first:
            evaluate = [next(self.__computers.__iter__())]
        else:
            evaluate = self.__computers
        self.__first = False
        avgs = dict()
        remaining_answers = []
        for computer in evaluate:
            chunked_answers = list(answers for choice in computer.solution_space.values() for answers in choice.values())
            answers = set(ans for answers in chunked_answers for ans in answers)
            remaining_answers.append(answers)
            print("Remaining answers: ", list(answers)[:10])
            for k,v in computer.solution_space.items():
                n = len(v)
                p = sum(len(vv) for vv in v.values())
                avgs.setdefault(k, (0, 0, 0))
                avgs[k] = (avgs[k][0] + n, avgs[k][1] + p, avgs[k][2] + 1)
        remaining_answers.sort(key=len)
        certainties=filter(lambda ra:len(ra) == 1, remaining_answers)
        best_choices = [e for sublist in remaining_answers for e in sublist]
        solution_probability = {e:100/len(sublist) for sublist in remaining_answers for e in sublist}
        avg_dict = {k: v[1] / v[0] for k, v in avgs.items()}
        lowest_avg = sorted(avg_dict.items(),
                            key=lambda p:(-avgs[p[0]][2], p[1], best_choices.index(p[0]) if p[0] in best_choices else sys.maxsize))

        best_of_best = {k:avg_dict[k] for sublist in certainties for k in sublist}
        most_cutting = lowest_avg[:10]

        most_cutting_answers = [x for x in itertools.islice(((w,a) for w,a in lowest_avg if w in best_choices), 5)]
        logging.debug("Most cutting answers:")
        logging.debug(most_cutting_answers)
        best_answers = [(k, avg_dict[k]) for k in best_choices]
        elem_shown_best_answers = 25 - (len(best_of_best) + len(most_cutting) + len(most_cutting_answers))
        def char(word):
            if word in best_of_best: return 'x '
            elif word in [k for k,v in best_answers[:elem_shown_best_answers]]: return '* '
            elif self.is_answer(word): return '+ '
            else: return '  '
        for word, avg in list(dict.fromkeys(list(best_of_best.items()) + most_cutting + most_cutting_answers + best_answers))[:25]:
            guess = ai.Guess(computer.solution_space[word],)
            print("%s%s: has an average division of %.2f (%.2f%% guess)" %
                      (char(word), word, avg, solution_probability.get(word, 0)))

    def is_answer(self, word: str):
        return any(computer.is_answer(word) for computer in self.__computers)

    def commit(self, *masks: MaskInstance):
        def remaining_computers():
            for mi,computer in zip(masks, self.__computers):
                if not self.is_only_answer(computer, mi):
                    computer.update(mi)
                    yield computer
        self.__computers = list(remaining_computers())

    def is_only_answer(self, computer, mi):
        return computer.is_answer(mi.cause) and len(computer.solution_space[mi.cause]) == 1