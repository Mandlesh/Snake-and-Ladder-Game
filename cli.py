"""
Terminal CLI interface for Snake and Ladder Game.
Supports 1-4 players (human and AI bots), ASCII art board and dice,
and colorized game status.
"""

import os
import sys
import time
from typing import List

from game.engine import (
    Board,
    Player,
    PlayerType,
    SnakeLadderGame,
    DEFAULT_SNAKES,
    DEFAULT_LADDERS,
)

# ANSI escape codes for styling
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
DIM = "\033[2m"

PLAYER_COLORS = [RED, BLUE, GREEN, MAGENTA]

DICE_FACES = {
    1: [
        "+-------+",
        "|       |",
        "|   o   |",
        "|       |",
        "+-------+",
    ],
    2: [
        "+-------+",
        "| o     |",
        "|       |",
        "|     o |",
        "+-------+",
    ],
    3: [
        "+-------+",
        "| o     |",
        "|   o   |",
        "|     o |",
        "+-------+",
    ],
    4: [
        "+-------+",
        "| o   o |",
        "|       |",
        "| o   o |",
        "+-------+",
    ],
    5: [
        "+-------+",
        "| o   o |",
        "|   o   |",
        "| o   o |",
        "+-------+",
    ],
    6: [
        "+-------+",
        "| o   o |",
        "| o   o |",
        "| o   o |",
        "+-------+",
    ],
}


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    banner = f"""
{CYAN}{BOLD}======================================================================
               🐍  S N A K E   &   L A D D E R  🪜
======================================================================{RESET}
"""
    print(banner)


def print_board(game: SnakeLadderGame):
    """Prints a clear 10x10 ASCII board with player tokens and snake/ladder tags."""
    board = game.board
    player_positions = {p.position: f"P{p.id}" for p in game.players if p.position > 0}

    print(f"\n{BOLD}┌{'──────┬'*9}──────┐{RESET}")
    for r in range(board.rows):
        row_cells = []
        for c in range(board.cols):
            # Calculate tile number based on row and col
            row_from_bottom = (board.rows - 1) - r
            if row_from_bottom % 2 == 1:
                tile = (row_from_bottom * board.cols) + (board.cols - c)
            else:
                tile = (row_from_bottom * board.cols) + (c + 1)

            # Check if any players are here
            players_here = [f"P{p.id}" for p in game.players if p.position == tile]
            if players_here:
                tag = "/".join(players_here)[:5]
                cell_text = f"{YELLOW}{BOLD}{tag:^6}{RESET}"
            elif tile in board.snakes:
                cell_text = f"{RED}🐍{tile:<2}→{board.snakes[tile]:<2}{RESET}"[:16]
                # Format to 6 visual chars
                cell_text = f"{RED}S:{board.snakes[tile]:<3}{RESET}"
            elif tile in board.ladders:
                cell_text = f"{GREEN}L:{board.ladders[tile]:<3}{RESET}"
            else:
                if tile == 100:
                    cell_text = f"{BOLD}{YELLOW} 100  {RESET}"
                else:
                    cell_text = f"{DIM}{tile:^6}{RESET}"

            row_cells.append(cell_text)

        print("│" + "│".join(row_cells) + "│")
        if r < board.rows - 1:
            print(f"├{'──────┼'*9}──────┤")
    print(f"└{'──────┴'*9}──────┘\n")


def display_dice(roll: int):
    print(f"{YELLOW}")
    for line in DICE_FACES.get(roll, []):
        print("   " + line)
    print(f"{RESET}")


def setup_game() -> SnakeLadderGame:
    print_banner()
    print("Welcome to Snake & Ladder! Let's set up your players.\n")

    while True:
        try:
            num_players_str = input("Enter number of players (2-4) [default: 2]: ").strip()
            if not num_players_str:
                num_players = 2
            else:
                num_players = int(num_players_str)
            if 2 <= num_players <= 4:
                break
            print("Please enter a number between 2 and 4.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    players: List[Player] = []
    default_names = ["Player 1", "Computer Bot", "Player 3", "Player 4"]

    for i in range(num_players):
        default_name = default_names[i]
        name = input(f"Enter name for Player {i+1} [default: {default_name}]: ").strip()
        if not name:
            name = default_name

        p_type = PlayerType.HUMAN
        if i > 0:
            bot_choice = input(f"Is {name} a Computer Bot? (y/N): ").strip().lower()
            if bot_choice in ["y", "yes"]:
                p_type = PlayerType.BOT

        color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
        players.append(Player(id=i + 1, name=name, color=color, player_type=p_type))

    return SnakeLadderGame(players=players)


def run_cli_game():
    game = setup_game()

    while not game.game_over:
        print_banner()
        print_board(game)

        # Player status leaderboard
        print(f"{BOLD}Current Standings:{RESET}")
        for p in game.players:
            turn_indicator = f" {CYAN}◄ Turn{RESET}" if p == game.current_player else ""
            bot_tag = " [BOT]" if p.player_type == PlayerType.BOT else ""
            print(
                f"  {p.color}{BOLD}{p.name}{RESET}{bot_tag} (P{p.id}): "
                f"Tile {p.position}/100{turn_indicator}"
            )
        print("-" * 50)

        current = game.current_player

        if current.player_type == PlayerType.HUMAN:
            input(f"\n👉 {current.color}{BOLD}{current.name}'s turn{RESET}. Press [Enter] to roll dice...")
        else:
            print(f"\n🤖 {current.color}{BOLD}{current.name}{RESET} is rolling...")
            time.sleep(1.0)

        # Execute move
        result = game.play_turn()

        # Display roll
        display_dice(result.dice_roll)
        print(f"{BOLD}{result.message}{RESET}\n")

        if result.is_snake:
            print(f"  {RED}Oh no! Snake bit you at {result.intermediate_pos}, sliding to {result.final_pos}! 🐍{RESET}")
        elif result.is_ladder:
            print(f"  {GREEN}Awesome! Climbed ladder from {result.intermediate_pos} to {result.final_pos}! 🪜{RESET}")
        elif result.overshot:
            print(f"  {YELLOW}Overshot 100! Need exact roll.{RESET}")

        if result.extra_turn and not result.won:
            print(f"  {CYAN}Rolled a 6! Extra turn incoming! 🎲{RESET}")

        time.sleep(1.5)

    # Game Over Summary
    print_banner()
    print_board(game)
    winner = game.winner
    print(f"\n{YELLOW}{BOLD}{'='*50}")
    print(f"   🏆 WINNER: {winner.name} (P{winner.id})! 🏆")
    print(f"{'='*50}{RESET}\n")

    print(f"{BOLD}Final Match Statistics:{RESET}")
    for p in game.players:
        print(f"• {p.name}:")
        print(f"    Final Position: {p.position}/100")
        print(f"    Total Rolls: {p.total_rolls}")
        print(f"    Ladders Climbed: {p.ladders_climbed}")
        print(f"    Snakes Bitten: {p.snakes_bitten}")

    print("\nThanks for playing Snake & Ladder!\n")


if __name__ == "__main__":
    try:
        run_cli_game()
    except KeyboardInterrupt:
        print("\n\nGame exited. Goodbye!")
        sys.exit(0)
