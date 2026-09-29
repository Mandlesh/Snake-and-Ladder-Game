"""
Unit tests for the Snake and Ladder game engine.
"""

import pytest
from game.engine import (
    Board,
    Player,
    PlayerType,
    SnakeLadderGame,
    DEFAULT_SNAKES,
    DEFAULT_LADDERS,
)


def test_board_coordinate_mapping():
    board = Board()
    # Tile 1 is at bottom-left: row 9, col 0
    assert board.tile_to_coords(1) == (9, 0)
    # Tile 10 is at bottom-right: row 9, col 9
    assert board.tile_to_coords(10) == (9, 9)
    # Tile 11 is row 8, col 9 (reversed / zig-zag)
    assert board.tile_to_coords(11) == (8, 9)
    # Tile 20 is row 8, col 0
    assert board.tile_to_coords(20) == (8, 0)
    # Tile 21 is row 7, col 0
    assert board.tile_to_coords(21) == (7, 0)
    # Tile 100 is top-left: row 0, col 0
    assert board.tile_to_coords(100) == (0, 0)


def test_normal_movement():
    p1 = Player(id=1, name="Alice", color="red")
    p2 = Player(id=2, name="Bob", color="blue")
    game = SnakeLadderGame(players=[p1, p2])

    # Alice rolls 3 -> moves from 0 to 3
    res = game.play_turn(fixed_roll=3)
    assert res.player == p1
    assert res.initial_pos == 0
    assert res.final_pos == 3
    assert p1.position == 3
    # Turn advances to Bob
    assert game.current_player == p2


def test_ladder_climb():
    p1 = Player(id=1, name="Alice", color="red")
    p2 = Player(id=2, name="Bob", color="blue")
    game = SnakeLadderGame(players=[p1, p2])

    # Ladder at 4 -> 14
    res = game.play_turn(fixed_roll=4)
    assert res.is_ladder is True
    assert res.intermediate_pos == 4
    assert res.final_pos == 14
    assert p1.position == 14
    assert p1.ladders_climbed == 1


def test_snake_bite():
    p1 = Player(id=1, name="Alice", color="red")
    p2 = Player(id=2, name="Bob", color="blue")
    game = SnakeLadderGame(players=[p1, p2])

    p1.position = 10
    # Snake at 16 -> 6. Roll 6 moves from 10 to 16, then down to 6!
    # Because roll is 6, Alice also gets an extra turn.
    res = game.play_turn(fixed_roll=6)
    assert res.is_snake is True
    assert res.intermediate_pos == 16
    assert res.final_pos == 6
    assert p1.position == 6
    assert p1.snakes_bitten == 1
    assert res.extra_turn is True
    assert game.current_player == p1


def test_extra_turn_on_six():
    p1 = Player(id=1, name="Alice", color="red")
    p2 = Player(id=2, name="Bob", color="blue")
    game = SnakeLadderGame(players=[p1, p2])

    res = game.play_turn(fixed_roll=6)
    assert res.extra_turn is True
    assert game.current_player == p1

    # Second roll: 2 -> moves to 8, normal turn so turns over to Bob
    res2 = game.play_turn(fixed_roll=2)
    assert res2.extra_turn is False
    assert p1.position == 8
    assert game.current_player == p2


def test_consecutive_three_sixes_penalty():
    p1 = Player(id=1, name="Alice", color="red")
    p2 = Player(id=2, name="Bob", color="blue")
    game = SnakeLadderGame(players=[p1, p2])

    # 1st six
    res1 = game.play_turn(fixed_roll=6)
    assert res1.extra_turn is True
    assert p1.position == 6

    # 2nd six (6+6=12)
    res2 = game.play_turn(fixed_roll=6)
    assert res2.extra_turn is True
    assert p1.position == 12

    # 3rd six -> turn cancelled!
    res3 = game.play_turn(fixed_roll=6)
    assert res3.turn_skipped is True
    # Alice stays at 12
    assert p1.position == 12
    # Turn passes to Bob
    assert game.current_player == p2


def test_exact_win_rule():
    p1 = Player(id=1, name="Alice", color="red")
    game = SnakeLadderGame(players=[p1], exact_win=True)

    p1.position = 98
    # Rolls 4 -> 98 + 4 = 102 > 100, cannot move!
    res = game.play_turn(fixed_roll=4)
    assert res.overshot is True
    assert p1.position == 98
    assert not game.game_over

    # Rolls 2 -> 98 + 2 = 100, WINS!
    res2 = game.play_turn(fixed_roll=2)
    assert res2.won is True
    assert p1.position == 100
    assert game.game_over is True
    assert game.winner == p1


def test_reset():
    p1 = Player(id=1, name="Alice", color="red")
    game = SnakeLadderGame(players=[p1])
    game.play_turn(fixed_roll=4)
    assert p1.position == 14
    game.reset()
    assert p1.position == 0
    assert game.current_player_idx == 0
    assert game.game_over is False
    assert len(game.history) == 0
