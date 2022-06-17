# Parseltongue
A set of tools to play and interact with word games (such as wordle)
in Python (hence the name).

In this repo there are the dictionary and answers for NYT Wordle
(under `wordle/`) and [@fserb][1]'s Termo (under `term.ooo/`), so you
can start playing right away.

## Features:
### Main features
* Get guidance to solve the game
* Have parseltongue solve the game for you
* Play games against random word(s)
* Replay games to see how you could do better

### Special cases!
* Supports games that use a number of letters different than 5
  as long as you provide your own dictionary
* Supports multi-word games (such as quordle)

## Pull Requests welcome! 
Send any pull request you want. Specially desirable are different
dictionaries / solutions (lemot? hogwartle?) or different strategies
or solvers.

## TODO
- [ ] Improve cmdline arguments
- [ ] Make "computer" better at solving multi-word games
- [ ] Make the display of the game a plugin 

[1]: https://github.com/fserb
