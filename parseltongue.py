#!/usr/bin/env python3

import logging
from random import sample

from evaluators import KnownAnswerEvaluator, InputEvaluator
from gameplay import Guidance, RemainingAnswerGuidance, CompleteGuidance, multitracker, multitracker2
from gameplay import guidance, SpaceSearch, HumanPlayer
# TODO: do not depend on computer
from gameplay.computer import Computer
from model import Engine, MutableEngine
from strategies import Heuristic

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
    argp.add_argument("--debug", action=BooleanOptionalAction, default=False)

    arguments = argp.parse_args()
    if arguments.debug:
        logging.root.setLevel(logging.DEBUG)

    if arguments.answers or arguments.random_answers:
        arguments.evaluator = "answers"

    engine = MutableEngine(arguments.solutions, arguments.dictionary, hard_mode=arguments.hard)
    computer = Computer(engine)

    if arguments.mode == "stats":
        stats(engine)

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

    if arguments.guidance == "remaining":
        guide = RemainingAnswerGuidance(engine)
    elif arguments.guidance == "computer":
        #if n > 1:
        immutable_engine = Engine(answers_file=arguments.solutions, words_file=arguments.dictionary, hard_mode=arguments.hard)
        guide = multitracker2.Multitracker2(immutable_engine, n, not arguments.guide_first)
        #else:
        #    guide = CompleteGuidance(engine, computer, not arguments.guide_first)
    else:
        guide = Guidance()

    if arguments.mode == "solve":
        # TODO: Allow strategy to be chosen
        solver = SpaceSearch(computer, Heuristic(), *arguments.first_words)
    else:
        solver = HumanPlayer(engine, guide)

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
