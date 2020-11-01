# the-game-solver
Simulator for the card game "The Game"

Description
=====
This repo contains a simulator for the game state of "The Game" by Pandasaurus games.

You can implement a strategy for playing the game by simply writing a function with the signature `(GameState) -> PlayerTurn` (see `src/strategies.py` for examples).

The rules for the game can be found [here](https://www.dropbox.com/s/cs2ht2msdkzvtty/The-Game_Rules_2020-Rebrand_Working.pdf?dl=0)

Requirements
=====
- `pipenv`

Setup
=====
- `pipenv install`

Run
=====
- `pipenv run main`

Additional Commands
=====
- `pipenv run test`
- `pipenv run mypy`
- `pipenv run flake8`