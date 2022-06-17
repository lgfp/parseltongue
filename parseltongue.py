import logging
from random import choice, sample
from typing import Iterable, List, Optional

from gameplay import Guidance, RemainingAnswerGuidance, CompleteGuidance
from gameplay import guidance, SpaceSearch, HumanPlayer
# TODO: do not depend on computer
from gameplay.computer import Computer
from model import Engine, MutableEngine, MaskInstance, Mask
from strategies import Heuristic


class Visitor:
    def visit(self, guess: str, mask: Optional[Mask] = None):
        raise NotImplementedError


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


class GuessQualityVisitor(Visitor):
    def __init__(self, engine: Engine):
        self.__engine = engine

    def visit(self, guess, mask=None):
        grouping = self.__engine.compute_grouping(guess)
        grouping_values = grouping.values()
        n_groups = len(grouping_values)
        remaining = sum(len(group) for group in grouping_values)
        print("Your guess divides the space in %d groups among %d remaining answers" % (n_groups, remaining))
        if mask:
            print("Based on %s, this means there are %d remaining answers, such as %s"
                  % (mask, len(grouping[mask]), choice(grouping[mask])))


from argparse import ArgumentParser, BooleanOptionalAction

def stats(engine: Engine):
    print("Overall information regarding starting words")
    computer = Computer(engine)
    print("Calculating solution space, this can take a while...")
    sol_space = computer.solution_space
    answers = engine.eligible_answers
    guidance.stats(answers, sol_space)

    exit(0)

def main():
    logging.root.setLevel(logging.INFO)
    argp = ArgumentParser(allow_abbrev=True)
    # For all modes
    argp.add_argument("--hard", action=BooleanOptionalAction, help="Hard Mode rules")
    argp.add_argument("--solutions", type=str, help="file containing the eligible answers", required=True)
    argp.add_argument("--dictionary", type=str, help="file containing the word dictionary", required=True)

    argp.add_argument("mode", choices=["play", "solve", "stats"], help="you PLAY the game or I SOLVE it")
    # For play
    argp.add_argument("--guidance", choices=["no", "remaining", "computer"], default="no",
                      help="How much guidance you want to play the game. " +
                      "no means no guidance, remaining shows remaining answers, " +
                      "computer shows best answers at each step")
    # It would be really nice to create an evaluator that plugs into wordle / termo / quordle / letreco of the day
    argp.add_argument("--evaluator", choices=["answers", "input"],
                      help="How guesses will be evaluated. A known answer, or from the input")
    argp.add_argument("--answers", type=str, nargs='+',
                      help="The answer(s) to this game. Required when evaluator is 'answers'")
    argp.add_argument("--random-answers", action=BooleanOptionalAction, default=False, help="In play mode, generate answers of play")
    argp.add_argument("--quantity", type=int, default=1, help="Number of words in the game.")
    argp.add_argument("--guide-first", action=BooleanOptionalAction, help="Give guidance for first guess")
    argp.add_argument("--first-words", type=str, nargs='+', help="When running the solver, choose its first words")

    arguments = argp.parse_args()

    engine = MutableEngine(arguments.solutions, arguments.dictionary, hard_mode=arguments.hard)
    computer = Computer(engine)

    if arguments.mode == "stats":
        stats(engine)

    if arguments.guidance == "remaining":
        guide = RemainingAnswerGuidance(engine)
    elif arguments.guidance == "computer":
        guide = CompleteGuidance(engine, computer, not arguments.guide_first)
    else:
        guide = Guidance()

    if arguments.mode == "solve":
        # TODO: Allow strategy to be chosen
        solver = SpaceSearch(computer, strategy=Heuristic())
    else:
        solver = HumanPlayer(engine, guide)

    answers = []
    if arguments.evaluator == "answers":
        if arguments.random_answers:
            n = arguments.quantity
            answers = sample(list(engine.eligible_answers), n)
        else:
            answers = arguments.answers
            n = len(arguments.answers)
        evaluator = KnownAnswerEvaluator(*answers)
    else:
        evaluator = InputEvaluator(arguments.quantity)
        n = arguments.quantity

    remaining = n
    for op in range(5 + remaining):
        guess = solver.provide()
        if guess == "giveup":
            break
        masks = evaluator.evaluate(guess)
        [print("", mask) for mask in masks]
        solver.accept(*masks)
        if any(m.mask.solved for m in masks):
            remaining = remaining - 1
            print("Solved %s in %d tries%s" % (guess.upper(), op + 1, (" %d remaining" % remaining) if remaining > 0 else ""))
            evaluator.answer_found(guess)
            if remaining == 0: break
    else:
        for answer in answers: print("Answer was %s" % answer.upper())

if __name__ == '__main__':
    main()
