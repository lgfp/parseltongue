import copy
import hashlib
import logging

from .common import load_file_as_list, Grouping
from .masks import MaskInstance


class Engine:
    def __init__(self, answers_file: str, words_file: str, hard_mode: bool = False):
        self._answers = load_file_as_list(answers_file)
        self._words = load_file_as_list(words_file)
        self._hard_mode = hard_mode

    @property
    def hard_mode(self):
        return self._hard_mode

    def is_answer(self, guess: str) -> bool:
        return guess in self._answers

    def compute_grouping(self, word: str) -> Grouping:
        groups = dict()
        for answer in self._answers:
            resp = MaskInstance.for_answer(answer, word)
            groups.setdefault(resp.mask, [])
            groups[resp.mask].append(answer)
        return groups

    def pruned(self, *mask_instances: MaskInstance):
        pruned = copy.copy(self)
        pruned_answers = self._prune_answers(mask_instances)
        pruned._answers = pruned_answers
        if self._hard_mode:
            pruned._words = [pw for pw in self._words if any(mi.matches(pw) for mi in mask_instances)]
        else:
            pruned._words = self._words
        return pruned

    def _prune_answers(self, mask_instances):
        answers = set()
        solutions_already_found = set()
        for mi in mask_instances:
            this_answers = self.compute_grouping(mi.cause)[mi.mask]
            if len(this_answers) == 1 and mi.cause in this_answers:
                logging.debug("Found a solution")
                solutions_already_found.add(this_answers[0])
                continue
            answers = answers.union(this_answers)
        return answers - solutions_already_found

    def game_id(self) -> str:
        logging.debug("Calculating hash for universe")
        bigstring: str = "\n".join(sorted(self._words)) + "\n".join(sorted(self._answers))
        the_hash = hashlib.md5(bigstring.encode())
        return the_hash.hexdigest()

    @property
    def words(self):
        return set(self._words)

    @property
    def eligible_answers(self):
        return set(self._answers)

    def acceptable_guess(self, guess: str) -> bool:
        return guess in self._words


class MutableEngine(Engine):
    def pruned(self, *mask_instances: MaskInstance):
        self._answers = self._prune_answers(mask_instances)
        if self._hard_mode:
            self._words = [pw for pw in self._words if any(mi.matches(pw) for mi in mask_instances)]
        return self
