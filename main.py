import numpy as np
import argparse
from tabulate import tabulate
import matplotlib.pyplot as plt
from pathlib import Path

STARTING_CASH = 3
MAX_ROLLS = 3
OUTPUT_DIR = Path(__file__).parent.joinpath('output')


def game_active(game_state: np.ndarray) -> bool:
    return sum((1 if x > 0 else 0 for x in game_state)) > 1


def game_loop(players: int) -> int:
    inventory = np.asarray([STARTING_CASH, ]*players)

    while True:
        for player_index, money in enumerate(inventory):
            rolls = np.random.randint(1, 6, min([MAX_ROLLS, money]))

            for roll in rolls:
                if roll == 1:                       # Left/down an index. 0 wraps to end.
                    inventory[player_index] -= 1
                    inventory[player_index-1] += 1
                elif roll == 2:                     # Center, remove 1.
                    inventory[player_index] -= 1
                elif roll == 3:                     # Right/up an index. end wraps to 0.
                    inventory[player_index] -= 1
                    inventory[(player_index + 1) % players] += 1

            if not game_active(inventory):
                for victor_index, value in enumerate(inventory):
                    if value > 0:
                        return victor_index

                raise GameError


def simulation(players: int, trials: int | float) -> (np.ndarray, np.ndarray):

    player_ids = np.arange(players)
    player_victories = np.zeros(shape=player_ids.shape)

    for trial in range(int(trials)):
        winner = game_loop(players)
        player_victories[winner] += 1

    player_victory_ratios = player_victories / int(trials)
    return player_ids, player_victory_ratios


def print_results(player_ids: np.ndarray, player_victory_ratios: np.ndarray) -> str:
    table = [list(x) for x in (player_ids, player_victory_ratios)]
    formatted_table = tabulate(table)
    print(formatted_table)
    return formatted_table


def graph_results(player_ids: np.ndarray, player_victory_ratios: np.ndarray):
    fig, ax = plt.subplots()
    ax.plot(player_ids, player_victory_ratios)
    fig.show()
    return fig


def main(sys_args):
    trials = int(sys_args.trials)
    x, y = simulation(sys_args.players, trials)
    outfile_stem = f'p-{sys_args.players}-t-{trials}'

    if sys_args.print:
        text = print_results(x, y)

        if sys_args.save:
            outfile = OUTPUT_DIR.joinpath(outfile_stem + '.txt')
            with open(outfile, 'w') as f:
                f.write(text)

    if sys_args.graph:
        fig = graph_results(x, y)

        if sys_args.save:
            outfile = OUTPUT_DIR.joinpath(outfile_stem + '.png')
            fig.savefig(outfile)


class GameError(Exception):
    pass


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('players', type=int, help="The number of players.")
    parser.add_argument('trials', type=int, help="The number of simulations to run")
    parser.add_argument('--print', action='store_true', help='Add this flag to print the results')
    parser.add_argument('--graph', action='store_true', help='Add this flag to graph the results')
    parser.add_argument('--save', action='store_true', help='Add this flag to save any output you generate')
    args = parser.parse_args()

    main(args)
