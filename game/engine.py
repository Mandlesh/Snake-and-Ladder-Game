"""
Core game engine for Snake and Ladder.
Handles player states, dice rolling, movement mechanics, snake/ladder interactions,
and win conditions.
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class PlayerType(Enum):
    HUMAN = "Human"
    BOT = "Bot"


@dataclass
class Player:
    id: int
    name: str
    color: str
    player_type: PlayerType = PlayerType.HUMAN
    position: int = 0
    total_rolls: int = 0
    snakes_bitten: int = 0
    ladders_climbed: int = 0

    def reset(self) -> None:
        self.position = 0
        self.total_rolls = 0
        self.snakes_bitten = 0
        self.ladders_climbed = 0


# Classic Snake & Ladder configuration
DEFAULT_SNAKES: Dict[int, int] = {
    16: 6,
    47: 26,
    49: 11,
    56: 53,
    62: 19,
    64: 60,
    87: 24,
    93: 73,
    95: 75,
    98: 78,
}

DEFAULT_LADDERS: Dict[int, int] = {
    4: 14,
    9: 31,
    20: 38,
    28: 84,
    40: 59,
    51: 67,
    63: 81,
    71: 91,
}


@dataclass
class Board:
    size: int = 100
    rows: int = 10
    cols: int = 10
    snakes: Dict[int, int] = field(default_factory=lambda: dict(DEFAULT_SNAKES))
    ladders: Dict[int, int] = field(default_factory=lambda: dict(DEFAULT_LADDERS))

    def __post_init__(self):
        # Validate that snakes only go down and ladders only go up
        for head, tail in self.snakes.items():
            if head <= tail:
                raise ValueError(f"Snake head ({head}) must be higher than tail ({tail})")
            if head > self.size or tail < 1:
                raise ValueError(f"Snake {head}->{tail} out of board range 1-{self.size}")

        for bottom, top in self.ladders.items():
            if bottom >= top:
                raise ValueError(f"Ladder bottom ({bottom}) must be lower than top ({top})")
            if top > self.size or bottom < 1:
                raise ValueError(f"Ladder {bottom}->{top} out of board range 1-{self.size}")

    def tile_to_coords(self, tile: int) -> Tuple[int, int]:
        """
        Converts tile number (1-100) to grid coordinates (row, col)
        where (0,0) is top-left, and row 9 is bottom row.
        Tile 1 starts at bottom-left (row 9, col 0) and zig-zags upwards.
        """
        if tile < 1 or tile > self.size:
            return -1, -1

        index = tile - 1
        row_from_bottom = index // self.cols
        row = (self.rows - 1) - row_from_bottom
        col_in_row = index % self.cols

        # Boustrophedon (alternating left-to-right, right-to-left)
        if row_from_bottom % 2 == 1:
            col = (self.cols - 1) - col_in_row
        else:
            col = col_in_row

        return row, col


class Dice:
    """Represents standard n-sided dice."""
    def __init__(self, sides: int = 6):
        self.sides = sides

    def roll(self) -> int:
        return random.randint(1, self.sides)


@dataclass
class MoveResult:
    player: Player
    dice_roll: int
    initial_pos: int
    step_positions: List[int]
    intermediate_pos: int
    final_pos: int
    is_snake: bool = False
    snake_tail: Optional[int] = None
    is_ladder: bool = False
    ladder_top: Optional[int] = None
    overshot: bool = False
    won: bool = False
    extra_turn: bool = False
    turn_skipped: bool = False
    message: str = ""


class SnakeLadderGame:
    """Manages the full state and logic for a Snake and Ladder game."""

    def __init__(
        self,
        players: Optional[List[Player]] = None,
        board: Optional[Board] = None,
        exact_win: bool = True,
        max_consecutive_sixes: int = 3,
    ):
        self.board = board if board is not None else Board()
        self.dice = Dice()
        self.exact_win = exact_win
        self.max_consecutive_sixes = max_consecutive_sixes

        if players:
            self.players = players
        else:
            self.players = [
                Player(id=1, name="Player 1", color="#E53935", player_type=PlayerType.HUMAN),
                Player(id=2, name="Player 2", color="#1E88E5", player_type=PlayerType.BOT),
            ]

        self.current_player_idx: int = 0
        self.consecutive_sixes: int = 0
        self.game_over: bool = False
        self.winner: Optional[Player] = None
        self.history: List[MoveResult] = []

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_idx]

    def reset(self) -> None:
        """Resets the game to start a fresh match."""
        for p in self.players:
            p.reset()
        self.current_player_idx = 0
        self.consecutive_sixes = 0
        self.game_over = False
        self.winner = None
        self.history.clear()

    def advance_turn(self) -> None:
        """Move to the next player's turn."""
        self.consecutive_sixes = 0
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

    def roll_dice(self) -> int:
        """Rolls the dice."""
        return self.dice.roll()

    def play_turn(self, fixed_roll: Optional[int] = None) -> MoveResult:
        """
        Executes a turn for current player.
        Optional fixed_roll allows predictable rolls for unit testing.
        """
        if self.game_over:
            raise RuntimeError("Cannot play turn: game is already over.")

        player = self.current_player
        roll = fixed_roll if fixed_roll is not None else self.roll_dice()
        player.total_rolls += 1

        initial_pos = player.position

        # Check consecutive sixes
        if roll == 6:
            self.consecutive_sixes += 1
        else:
            self.consecutive_sixes = 0

        # If rolled 3 consecutive sixes, turn is cancelled as penalty
        if self.consecutive_sixes >= self.max_consecutive_sixes:
            message = (
                f"{player.name} rolled three consecutive 6s! "
                f"Turn cancelled and passed to next player."
            )
            result = MoveResult(
                player=player,
                dice_roll=roll,
                initial_pos=initial_pos,
                step_positions=[],
                intermediate_pos=initial_pos,
                final_pos=initial_pos,
                turn_skipped=True,
                extra_turn=False,
                message=message,
            )
            self.history.append(result)
            self.advance_turn()
            return result

        target_pos = initial_pos + roll
        step_positions: List[int] = []

        # Check overshooting top square
        if self.exact_win and target_pos > self.board.size:
            message = (
                f"{player.name} rolled a {roll}, but needs exact roll to reach {self.board.size}. "
                f"Cannot move from {initial_pos}."
            )
            result = MoveResult(
                player=player,
                dice_roll=roll,
                initial_pos=initial_pos,
                step_positions=[],
                intermediate_pos=initial_pos,
                final_pos=initial_pos,
                overshot=True,
                extra_turn=(roll == 6),
                message=message,
            )
            self.history.append(result)
            if roll != 6:
                self.advance_turn()
            return result

        # Normal forward movement
        start_step = max(1, initial_pos + 1)
        step_positions = list(range(start_step, target_pos + 1))
        intermediate_pos = target_pos
        final_pos = intermediate_pos

        is_snake = False
        snake_tail = None
        is_ladder = False
        ladder_top = None

        if intermediate_pos in self.board.snakes:
            is_snake = True
            snake_tail = self.board.snakes[intermediate_pos]
            final_pos = snake_tail
            player.snakes_bitten += 1
        elif intermediate_pos in self.board.ladders:
            is_ladder = True
            ladder_top = self.board.ladders[intermediate_pos]
            final_pos = ladder_top
            player.ladders_climbed += 1

        player.position = final_pos

        # Check win condition
        won = final_pos == self.board.size
        if won:
            self.game_over = True
            self.winner = player

        # Message formulation
        if won:
            message = f"🎉 {player.name} rolled a {roll} and reached tile {final_pos}! {player.name} WINS! 🎉"
        elif is_ladder:
            message = (
                f"{player.name} rolled a {roll}, landed on {intermediate_pos} "
                f"and climbed a LADDER to {final_pos}! 🪜"
            )
        elif is_snake:
            message = (
                f"{player.name} rolled a {roll}, landed on {intermediate_pos} "
                f"and got swallowed by a SNAKE down to {final_pos}! 🐍"
            )
        else:
            message = f"{player.name} rolled a {roll} and moved to {final_pos}."

        extra_turn = (roll == 6 and not won)
        if extra_turn:
            message += f" Rolled a 6! {player.name} gets an EXTRA ROLL!"

        result = MoveResult(
            player=player,
            dice_roll=roll,
            initial_pos=initial_pos,
            step_positions=step_positions,
            intermediate_pos=intermediate_pos,
            final_pos=final_pos,
            is_snake=is_snake,
            snake_tail=snake_tail,
            is_ladder=is_ladder,
            ladder_top=ladder_top,
            won=won,
            extra_turn=extra_turn,
            message=message,
        )

        self.history.append(result)

        if not extra_turn and not won:
            self.advance_turn()

        return result
