import logging

from model import Engine, MaskInstance, Space
from .data import fetch_cache, save_cache

class Computer:
    __mem_cache = None

    def __init__(self, engine: Engine, hard_mode=False):
        self.__engine = engine
        self.__hard_mode = hard_mode

    @property
    def solution_space(self) -> Space:
        if self.__mem_cache:
            return self.__mem_cache
        return self.__load_groups()

    def __load_groups(self) -> Space:
        game_id = self.__engine.game_id()
        cached = fetch_cache(game_id)
        if cached:
            self.__mem_cache = cached
            return cached
        else:
            computed = self.__compute_groups()
            self.__mem_cache = computed
            save_cache(game_id, computed)
            return computed

    def bust(self):
        self.__mem_cache = None

    def __compute_groups(self) -> Space:
        computed: Space = dict()
        words = self.__engine.words
        logging.debug("Calculating all groups for %d words" % len(words))
        n_words = len(words)
        for i, word in enumerate(words):
            groups = self.__engine.compute_grouping(word)
            # This means that this does not help us
            #if (len(groups) == 1) and not self.__engine.is_answer(word):
            #    continue
            computed[word] = groups
            if logging.root.level <= logging.DEBUG:
                print("Progress: %.02f%%" % (100 * i / n_words), end='\r')
        return computed

    def is_answer(self, word: str) -> bool:
        return self.__engine.is_answer(word)

    def update(self, *mi: MaskInstance):
        self.__engine = self.__engine.pruned(*mi)
        self.__mem_cache = None
